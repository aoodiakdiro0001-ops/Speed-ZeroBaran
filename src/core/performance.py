"""
Speed-ZeroBaran — Layer 1: Performance Ingestion
=================================================
Hits Google PageSpeed Insights API (100% free) to measure
Core Web Vitals (LCP, INP, CLS) and pull all opportunities
and diagnostics. Falls back to local Lighthouse CLI when
network/api quota is exhausted.

Author : Baran Avisat <Baranavisat@gmail.com>
License: MIT
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from config import settings
from src.models.schemas import AuditReport, CoreWebVitals
from src.utils import log, timed, short_hash


PAGESPEED_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagesSpeed"


class PerformanceAuditor:
    """Calls PageSpeed API / Lighthouse CLI and returns a structured report."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or settings.pagespeed_api_key

    # ---------- Public API ----------
    @timed
    def audit(self, url: str, strategy: str = "mobile",
              site_name: str = "") -> AuditReport:
        """
        Run a full audit on `url`.
        Tries PageSpeed API first; on failure falls back to Lighthouse CLI.
        """
        log.info(f"🔎 Auditing [bold]{url}[/bold] ({strategy})")
        raw: Optional[Dict[str, Any]] = None
        if self.api_key:
            raw = self._call_pagespeed_api(url, strategy)
        if raw is None:
            log.warning("PageSpeed API unavailable — falling back to Lighthouse CLI")
            raw = self._call_lighthouse_cli(url, strategy)

        return self._parse_to_report(raw, url, strategy, site_name)

    # ---------- PageSpeed API ----------
    def _call_pagespeed_api(self, url: str, strategy: str) -> Optional[Dict]:
        params = {
            "url": url,
            "strategy": strategy,
            "key": self.api_key,
            "category": ["performance", "accessibility",
                         "best-practices", "seo"],
        }
        try:
            resp = requests.get(PAGESPEED_ENDPOINT, params=params, timeout=120)
            if resp.status_code == 429:
                log.error("Quota exceeded for PageSpeed API (429).")
                return None
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            log.error(f"PageSpeed API call failed: {exc}")
            return None

    # ---------- Lighthouse CLI fallback ----------
    def _call_lighthouse_cli(self, url: str, strategy: str) -> Optional[Dict]:
        """Run `lighthouse` locally — useful when API quota is exhausted."""
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".json", delete=False, mode="w"
            ) as tmp:
                out_path = tmp.name

            form_factor = "mobile" if strategy == "mobile" else "desktop"
            cmd = [
                "lighthouse", url,
                "--only-categories=performance,accessibility,best-practices,seo",
                f"--form-factor={form_factor}",
                "--quiet",
                "--chrome-flags=--headless --no-sandbox --disable-gpu",
                f"--output=json",
                f"--output-path={out_path}",
            ]
            log.info(f"Running Lighthouse CLI: {' '.join(cmd[:3])}...")
            subprocess.run(cmd, check=True, timeout=300, capture_output=True)
            with open(out_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            log.error(
                "Lighthouse CLI not installed. "
                "Install with: npm install -g lighthouse"
            )
            return None
        except Exception as exc:
            log.error(f"Lighthouse CLI failed: {exc}")
            return None

    # ---------- Parsing ----------
    def _parse_to_report(self, raw: Dict, url: str, strategy: str,
                         site_name: str) -> AuditReport:
        """Convert raw PageSpeed/Lighthouse JSON into our AuditReport."""
        if not raw:
            # Build a minimal empty report so the pipeline doesn't crash
            return AuditReport(
                url=url, site_name=site_name, strategy=strategy,
                needs_alert=True,
            )

        # The two JSON shapes are nearly identical — Lighthouse is the source.
        lighthouse = raw.get("lighthouseResult", raw)
        categories = lighthouse.get("categories", {})
        audits = lighthouse.get("audits", {})

        def _score(cat_key: str) -> int:
            cat = categories.get(cat_key, {})
            s = cat.get("score")
            return int((s or 0) * 100) if s is not None else 0

        # Core Web Vitals — try both new (INP) and legacy (FID) keys.
        def _audit_ms(name: str) -> Optional[float]:
            a = audits.get(name)
            if not a:
                return None
            num = a.get("numericValue")
            return float(num) / 1000.0 if name in {
                "largest-contentful-paint",
                "first-contentful-paint",
                "speed-index",
                "server-response-time",
                "experimental-interaction",
            } else float(num) if num is not None else None

        vitals = CoreWebVitals(
            lcp=_audit_ms("largest-contentful-paint"),
            inp=_audit_ms("interaction-to-next-paint")
                or _audit_ms("experimental-interaction"),
            cls=_audit_ms("cumulative-layout-shift"),
            fcp=_audit_ms("first-contentful-paint"),
            ttfb=_audit_ms("server-response-time"),
            tbt=_audit_ms("total-blocking-time"),
            si=_audit_ms("speed-index"),
        )

        # Loading time = LCP if present, else Speed Index
        total_loading = vitals.lcp or vitals.si or 0.0

        # Opportunities (render-blocking, image savings, unused JS, …)
        opportunities: List[Dict[str, Any]] = []
        for op_key in [
            "render-blocking-resources",
            "uses-responsive-images",
            "uses-optimized-images",
            "modern-image-formats",
            "uses-text-compression",
            "unused-javascript",
            "unused-css-rules",
            "unused-javascript",
            "preconnect",
            "efficient-animated-content",
            "duplicated-javascript",
            "legacy-javascript",
        ]:
            a = audits.get(op_key)
            if not a:
                continue
            if a.get("score") is not None and a.get("score") < 1:
                opportunities.append({
                    "id": op_key,
                    "title": a.get("title", op_key),
                    "description": a.get("description", "")[:300],
                    "score": a.get("score"),
                    "numeric_value": a.get("numericValue"),
                    "display_value": a.get("displayValue", ""),
                    "wasted_ms": (a.get("details", {})
                                    .get("overallSavingsMs", 0)),
                    "wasted_bytes": (a.get("details", {})
                                      .get("overallSavingsBytes", 0)),
                })

        # Diagnostics (other quality signals)
        diagnostics: List[Dict[str, Any]] = []
        for d_key in [
            "total-blocking-time",
            "max-potential-fid",
            "bootup-time",
            "mainthread-work-breakdown",
            "dom-size",
            "critical-request-chains",
            "long-tasks",
            "non-composited-animations",
            "network-requests",
        ]:
            a = audits.get(d_key)
            if a and a.get("score") is not None and a.get("score") < 1:
                diagnostics.append({
                    "id": d_key,
                    "title": a.get("title", d_key),
                    "description": a.get("description", "")[:300],
                    "score": a.get("score"),
                    "numeric_value": a.get("numericValue"),
                    "display_value": a.get("displayValue", ""),
                })

        # Decide whether the site breaches our thresholds
        perf = _score("performance")
        needs_alert = (
            total_loading > settings.speed_alert_threshold
            or perf < settings.score_alert_threshold
        )

        report = AuditReport(
            url=url,
            site_name=site_name or short_hash(url),
            strategy=strategy,
            performance_score=perf,
            accessibility_score=_score("accessibility"),
            best_practices_score=_score("best-practices"),
            seo_score=_score("seo"),
            vitals=vitals,
            total_loading_time=total_loading,
            opportunities=opportunities,
            diagnostics=diagnostics,
            needs_alert=needs_alert,
        )
        log.info(
            f"✅ Audit done — perf={perf}/100, "
            f"LCP={vitals.lcp}, INP={vitals.inp}, CLS={vitals.cls}"
        )
        return report


# Convenience module-level instance
auditor = PerformanceAuditor()

__all__ = ["PerformanceAuditor", "auditor"]
