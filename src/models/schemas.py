"""
Speed-ZeroBaran — Data models / schemas
=======================================
Typed structures shared across all 4 architectural layers
so performance data flows cleanly:
    Ingestion  ->  AI Core  ->  Persistence  ->  Delivery
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class CoreWebVitals:
    """The three official Google Core Web Vitals (2024+)."""
    lcp: Optional[float] = None       # Largest Contentful Paint (sec)
    inp: Optional[float] = None       # Interaction to Next Paint (sec) — replaced FID
    cls: Optional[float] = None       # Cumulative Layout Shift (unitless)
    fcp: Optional[float] = None       # First Contentful Paint (sec)
    ttfb: Optional[float] = None      # Time to First Byte (sec)
    tbt: Optional[float] = None       # Total Blocking Time (ms)
    si: Optional[float] = None        # Speed Index (sec)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuditReport:
    """Result of a single PageSpeed / Lighthouse run on one URL."""
    url: str
    site_name: str = ""
    strategy: str = "mobile"          # mobile | desktop
    performance_score: int = 0        # 0..100
    accessibility_score: int = 0
    best_practices_score: int = 0
    seo_score: int = 0
    vitals: CoreWebVitals = field(default_factory=CoreWebVitals)
    total_loading_time: float = 0.0   # seconds
    opportunities: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    audit_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Derived flag — true if the site breached our thresholds
    needs_alert: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class AIOptimization:
    """Output of the AI Optimization Core."""
    summary: str = ""                              # plain-text diagnosis
    root_causes: List[str] = field(default_factory=list)
    code_fixes: List[Dict[str, str]] = field(
        default_factory=list
    )  # [{ "title": ..., "language": ..., "code": ..., "explanation": ... }]
    priority: str = "medium"                        # high | medium | low

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FullAuditResult:
    """Combined result of an audit + AI analysis (one site, one run)."""
    report: AuditReport
    optimization: AIOptimization

    def to_telegram_message(self) -> str:
        """Renders a clean markdown report for the Telegram channel."""
        r = self.report
        o = self.optimization
        lines = []
        lines.append("⚡ *Speed-ZeroBaran — تقرير أداء الموقع*")
        lines.append(f"🌐 *الموقع:* `{r.url}`")
        lines.append(f"📊 *درجة الأداء:* {r.performance_score}/100")
        lines.append(f"📱 *الاستراتيجية:* {r.strategy}")
        lines.append("")
        lines.append("🔬 *مؤشرات الأداء الحيوية (Core Web Vitals):*")
        if r.vitals.lcp is not None:
            lines.append(f"   • LCP: `{r.vitals.lcp:.2f}s`")
        if r.vitals.inp is not None:
            lines.append(f"   • INP: `{r.vitals.inp:.0f}ms`")
        if r.vitals.cls is not None:
            lines.append(f"   • CLS: `{r.vitals.cls:.3f}`")
        if r.vitals.fcp is not None:
            lines.append(f"   • FCP: `{r.vitals.fcp:.2f}s`")
        if r.vitals.ttfb is not None:
            lines.append(f"   • TTFB: `{r.vitals.ttfb:.2f}s`")
        lines.append("")
        lines.append("🛠️ *تشخيص الذكاء الاصطناعي:*")
        lines.append(f"_{o.summary}_")
        if o.root_causes:
            lines.append("")
            lines.append("📌 *الأسباب الرئيسية للبطء:*")
            for cause in o.root_causes[:5]:
                lines.append(f"   • {cause}")
        if o.code_fixes:
            lines.append("")
            lines.append("💻 *الإصلاحات المقترحة (جاهزة للنسخ):*")
            for fix in o.code_fixes[:3]:
                lines.append(f"   *{fix.get('title', '')}*")
                if fix.get("explanation"):
                    lines.append(f"   {fix['explanation']}")
                if fix.get("code"):
                    lines.append(f"   ```{fix.get('language','')}")
                    lines.append(fix["code"])
                    lines.append("   ```")
        lines.append("")
        lines.append("—"*30)
        lines.append("👤 *Speed-ZeroBaran* — by Baran Avisat")
        lines.append("✉️ Baranavisat@gmail.com  •  📱 +90 531 326 3722")
        return "\n".join(lines)


__all__ = [
    "CoreWebVitals",
    "AuditReport",
    "AIOptimization",
    "FullAuditResult",
]
