"""
Speed-ZeroBaran — HTML report generator (optional)
Renders a self-contained HTML audit report for archiving or for the
Vercel dashboard. Uses Jinja2 when available, falls back to a plain
string template otherwise.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import settings
from src.models.schemas import FullAuditResult
from src.utils import log, slugify


HTML_TEMPLATE = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Speed-ZeroBaran — تقرير أداء {url}</title>
  <style>
    :root {{
      --bg:#0b1020; --card:#151c30; --fg:#e6ecff; --muted:#9aa6c7;
      --accent:#3ddc97; --warn:#ffb86c; --danger:#ff6b6b;
    }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0; padding:24px; font-family:'Segoe UI',Tahoma,sans-serif;
      background:var(--bg); color:var(--fg); line-height:1.6;
    }}
    h1 {{ font-size:1.6rem; margin:0 0 4px; }}
    h2 {{ font-size:1.15rem; margin:28px 0 10px; color:var(--accent); }}
    .card {{
      background:var(--card); border:1px solid #232b48; border-radius:14px;
      padding:18px 20px; margin-bottom:16px;
    }}
    .grid {{ display:grid; gap:12px; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); }}
    .stat {{ background:#0e1428; border-radius:10px; padding:14px; text-align:center; }}
    .stat .label {{ font-size:.75rem; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; }}
    .stat .value {{ font-size:1.4rem; font-weight:700; margin-top:4px; }}
    .stat.good .value {{ color:var(--accent); }}
    .stat.warn .value {{ color:var(--warn); }}
    .stat.bad .value  {{ color:var(--danger); }}
    code, pre {{
      font-family:'Cascadia Code',Consolas,monospace; font-size:.9rem;
      background:#0a0f1f; padding:12px; border-radius:8px; overflow:auto;
      display:block; direction:ltr; text-align:left;
    }}
    .fix {{ border-left:3px solid var(--accent); padding-left:12px; margin-bottom:18px; }}
    .fix h3 {{ margin:0 0 4px; font-size:1rem; }}
    .meta {{ color:var(--muted); font-size:.85rem; margin-top:4px; }}
    a {{ color:var(--accent); }}
    .footer {{ margin-top:32px; padding-top:16px; border-top:1px solid #232b48;
              color:var(--muted); font-size:.85rem; text-align:center; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>⚡ Speed-ZeroBaran — تقرير أداء الموقع</h1>
    <div class="meta">🌐 {url} • 📱 {strategy} • 🕐 {ts}</div>
  </div>

  <div class="card">
    <h2>📊 الدرجات</h2>
    <div class="grid">
      <div class="stat {perf_class}"><div class="label">الأداء</div><div class="value">{perf}/100</div></div>
      <div class="stat"><div class="label">إمكانية الوصول</div><div class="value">{a11y}/100</div></div>
      <div class="stat"><div class="label">الممارسات</div><div class="value">{bp}/100</div></div>
      <div class="stat"><div class="label">SEO</div><div class="value">{seo}/100</div></div>
    </div>
  </div>

  <div class="card">
    <h2>🔬 مؤشرات الأداء الحيوية (Core Web Vitals)</h2>
    <div class="grid">
      <div class="stat"><div class="label">LCP</div><div class="value">{lcp}s</div></div>
      <div class="stat"><div class="label">INP</div><div class="value">{inp}ms</div></div>
      <div class="stat"><div class="label">CLS</div><div class="value">{cls}</div></div>
      <div class="stat"><div class="label">FCP</div><div class="value">{fcp}s</div></div>
      <div class="stat"><div class="label">TTFB</div><div class="value">{ttfb}s</div></div>
    </div>
  </div>

  <div class="card">
    <h2>🛠️ تشخيص الذكاء الاصطناعي</h2>
    <p>{summary}</p>
    <h2>📌 الأسباب الرئيسية</h2>
    <ul>{root_causes}</ul>
  </div>

  <div class="card">
    <h2>💻 الإصلاحات المقترحة</h2>
    {code_fixes}
  </div>

  <div class="footer">
    Speed-ZeroBaran v{version} — by <strong>{author}</strong> ✉️ {email} • 📱 {whatsapp}
  </div>
</body>
</html>
"""


def render_html(result: FullAuditResult) -> str:
    r = result.report
    o = result.optimization

    def _class_for(score: int) -> str:
        if score >= 90: return "good"
        if score >= 50: return "warn"
        return "bad"

    root_causes_html = "".join(f"<li>{c}</li>" for c in o.root_causes[:6])
    fixes_html_parts = []
    for fix in o.code_fixes[:5]:
        fixes_html_parts.append(
            f"<div class='fix'><h3>{fix.get('title','')}</h3>"
            f"<div class='meta'>{fix.get('explanation','')}</div>"
            f"<pre><code>{fix.get('code','')}</code></pre></div>"
        )
    fixes_html = "".join(fixes_html_parts) or "<p>(لا توجد إصلاحات مقترحة)</p>"

    return HTML_TEMPLATE.format(
        url=r.url,
        strategy=r.strategy,
        ts=r.audit_timestamp,
        perf=r.performance_score,
        perf_class=_class_for(r.performance_score),
        a11y=r.accessibility_score,
        bp=r.best_practices_score,
        seo=r.seo_score,
        lcp=f"{r.vitals.lcp:.2f}" if r.vitals.lcp else "—",
        inp=f"{r.vitals.inp*1000:.0f}" if r.vitals.inp else "—",
        cls=f"{r.vitals.cls:.3f}" if r.vitals.cls else "—",
        fcp=f"{r.vitals.fcp:.2f}" if r.vitals.fcp else "—",
        ttfb=f"{r.vitals.ttfb:.2f}" if r.vitals.ttfb else "—",
        summary=o.summary,
        root_causes=root_causes_html,
        code_fixes=fixes_html,
        version=settings.project_version,
        author=settings.author_name,
        email=settings.author_email,
        whatsapp=settings.author_whatsapp,
    )


def save_html(result: FullAuditResult, out_dir: str = "reports") -> Path:
    """Persist the HTML report under reports/<site>_<timestamp>.html"""
    out_path = Path(out_dir)
    out_path.mkdir(exist_ok=True)
    fname = (
        out_path
        / f"{slugify(result.report.site_name or result.report.url)}_"
          f"{slugify(result.report.audit_timestamp)}.html"
    )
    html = render_html(result)
    fname.write_text(html, encoding="utf-8")
    log.info(f"📄 HTML report saved to {fname}")
    return fname


__all__ = ["render_html", "save_html"]
