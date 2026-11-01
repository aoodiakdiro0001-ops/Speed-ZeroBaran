"""
Speed-ZeroBaran — Layer 2: AI Optimization Core
================================================
Reads the technical audit report, identifies the real bottlenecks
(heavy images, render-blocking JS, unoptimized CSS…), and writes
ready-to-paste code fixes (HTML/CSS/JS/server-config).

Two interchangeable free-tier providers are supported:
  • Google Gemini  (gemini-1.5-flash / gemini-1.5-pro)
  • Groq           (llama3-70b-8192, mixtral, etc.)

Author : Baran Avisat <Baranavisat@gmail.com>
License: MIT
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from config import settings
from src.models.schemas import AIOptimization, AuditReport
from src.utils import log, truncate, safe_json


# ---------- Prompt template ----------
SYSTEM_PROMPT = """You are *Speed-ZeroBaran*, an elite web-performance engineer.
You receive a JSON audit report from Google PageSpeed / Lighthouse for a website.
Your job:
  1. Identify the *top root causes* of slowness (heavy images, render-blocking JS, layout shifts…).
  2. Produce a short, plain-language diagnosis (max 3 sentences).
  3. Write *ready-to-paste code fixes* for the 2-3 most impactful issues.
     Each fix must include a title, programming language, the code, and a one-line explanation.
  4. Assign a priority: high / medium / low based on severity.

Respond ONLY with valid JSON matching this schema:
{
  "summary": "string",
  "root_causes": ["string", ...],
  "priority": "high|medium|low",
  "code_fixes": [
    {
      "title": "string",
      "language": "html|css|js|python|nginx|json|bash",
      "code": "string",
      "explanation": "string"
    }
  ]
}
Do not include any markdown fences, comments, or text outside the JSON object.
"""


USER_PROMPT_TEMPLATE = """Website audited: {url}
Strategy: {strategy}
Performance score: {perf}/100
LCP: {lcp}s | INP: {inp}ms | CLS: {cls} | FCP: {fcp}s | TTFB: {ttfb}s

Top opportunities (render-blocking, heavy assets, unused JS/CSS…):
{opportunities}

Top diagnostics:
{diagnostics}

Produce the JSON analysis now.
"""


class AIOptimizer:
    """Wraps Gemini or Groq behind a single `analyze(report)` method."""

    def __init__(self, provider: Optional[str] = None) -> None:
        self.provider = (provider or settings.ai_provider).lower()
        if self.provider == "gemini" and not settings.gemini_api_key:
            if settings.groq_api_key:
                log.warning(
                    "Gemini key missing — falling back to Groq provider."
                )
                self.provider = "groq"
        if self.provider == "groq" and not settings.groq_api_key:
            if settings.gemini_api_key:
                log.warning(
                    "Groq key missing — falling back to Gemini provider."
                )
                self.provider = "gemini"

    # ---------- Public API ----------
    def analyze(self, report: AuditReport) -> AIOptimization:
        """Send the report to the LLM and parse the structured answer."""
        prompt = self._build_prompt(report)
        raw = self._call_llm(prompt)
        return self._parse_response(raw)

    # ---------- Prompt building ----------
    def _build_prompt(self, r: AuditReport) -> str:
        def _fmt(items: List[Dict[str, Any]], limit: int = 8) -> str:
            if not items:
                return "(none)"
            lines = []
            for it in items[:limit]:
                line = f"- {it.get('title','?')} "
                if it.get("display_value"):
                    line += f"({it['display_value']}) "
                if it.get("wasted_ms"):
                    line += f"— saves ~{it['wasted_ms']}ms"
                lines.append(line)
            return "\n".join(lines)

        return USER_PROMPT_TEMPLATE.format(
            url=r.url,
            strategy=r.strategy,
            perf=r.performance_score,
            lcp=r.vitals.lcp or "N/A",
            inp=(r.vitals.inp * 1000) if r.vitals.inp else "N/A",
            cls=r.vitals.cls or "N/A",
            fcp=r.vitals.fcp or "N/A",
            ttfb=r.vitals.ttfb or "N/A",
            opportunities=_fmt(r.opportunities),
            diagnostics=_fmt(r.diagnostics),
        )

    # ---------- LLM dispatch ----------
    def _call_llm(self, prompt: str) -> str:
        if self.provider == "gemini":
            return self._call_gemini(prompt)
        return self._call_groq(prompt)

    def _call_gemini(self, prompt: str) -> str:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(
                settings.gemini_model,
                system_instruction=SYSTEM_PROMPT,
            )
            log.info(f"🧠 Calling Gemini ({settings.gemini_model})…")
            resp = model.generate_content(
                truncate(prompt, 28000),
                generation_config={
                    "temperature": 0.4,
                    "top_p": 0.9,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json",
                },
            )
            return resp.text or ""
        except Exception as exc:
            log.error(f"Gemini call failed: {exc}")
            return self._call_groq(prompt)  # graceful fallback

    def _call_groq(self, prompt: str) -> str:
        try:
            from groq import Groq
            client = Groq(api_key=settings.groq_api_key)
            log.info(f"🧠 Calling Groq ({settings.groq_model})…")
            resp = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": truncate(prompt, 7000)},
                ],
                temperature=0.4,
                max_tokens=2048,
                response_format={"type": "json_object"},
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            log.error(f"Groq call failed: {exc}")
            return ""

    # ---------- Response parsing ----------
    def _parse_response(self, raw: str) -> AIOptimization:
        if not raw:
            return AIOptimization(
                summary="تعذّر الوصول إلى محرك الذكاء الاصطناعي. "
                        "يُرجى التحقق من مفاتيح API.",
                priority="low",
            )
        # Strip accidental markdown fences
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to extract the first {...} block
            try:
                start = text.find("{")
                end = text.rfind("}") + 1
                data = json.loads(text[start:end])
            except Exception:
                log.error("AI returned non-JSON response — saving raw text")
                return AIOptimization(
                    summary=truncate(text, 600),
                    priority="medium",
                )

        return AIOptimization(
            summary=data.get("summary", ""),
            root_causes=data.get("root_causes", []),
            code_fixes=data.get("code_fixes", []),
            priority=data.get("priority", "medium"),
        )


# Singleton
optimizer = AIOptimizer()

__all__ = ["AIOptimizer", "optimizer"]
