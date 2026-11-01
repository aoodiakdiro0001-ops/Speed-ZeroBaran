#!/usr/bin/env python3
"""
Speed-ZeroBaran — Main Orchestrator
====================================
Run a full audit cycle:
  1. For each target site:
       a. PerformanceAuditor.audit(url)         -> AuditReport
       b. AIOptimizer.analyze(report)           -> AIOptimization
       c. AuditRepository.save(FullAuditResult) -> persisted row
       d. TelegramNotifier.send(FullAuditResult)-> user alert
  2. Print a final summary to console (visible in GitHub Actions logs).

Usage:
    python scripts/run_audit.py                 # all sites from .env / sites.yaml
    python scripts/run_audit.py --url URL       # single URL
    python scripts/run_audit.py --dry-run       # skip AI + notifications
    python scripts/run_audit.py --html          # also save HTML reports

Author : Baran Avisat <Baranavisat@gmail.com>
License: MIT  —  100% Free Tech Stack
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

# Make project root importable when run from anywhere
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import click

from config import settings
from src.core import auditor, optimizer, repository, notifier
from src.core.report import save_html
from src.models.schemas import FullAuditResult
from src.utils import log


def collect_sites() -> List[dict]:
    """Merge sites from .env (TARGET_SITES) and config/sites.yaml."""
    sites = []
    # 1. From YAML (richer config)
    for s in settings.load_sites_from_yaml():
        sites.append({
            "name": s.get("name", s["url"]),
            "url": s["url"],
            "strategy": s.get("strategy", settings.audit_strategy),
        })
    # 2. From .env (simple comma list) — avoid duplicates
    existing_urls = {s["url"] for s in sites}
    for url in settings.target_sites:
        if url not in existing_urls:
            sites.append({
                "name": url,
                "url": url,
                "strategy": settings.audit_strategy,
            })
    if not sites:
        log.error(
            "No sites configured. Set TARGET_SITES in .env or edit config/sites.yaml"
        )
    return sites


def run_one(site: dict, dry_run: bool = False, html: bool = False) -> FullAuditResult:
    """Run a full audit + AI analysis on a single site."""
    url = site["url"]
    strategy = site.get("strategy", settings.audit_strategy)
    name = site.get("name", url)

    # Layer 1 — Performance
    report = auditor.audit(url, strategy=strategy, site_name=name)

    # Layer 2 — AI
    if dry_run:
        optimization = type(optimizer).analyze.__defaults__  # placeholder
        from src.models.schemas import AIOptimization
        optimization = AIOptimization(summary="[dry-run] AI skipped.")
    else:
        optimization = optimizer.analyze(report)

    result = FullAuditResult(report=report, optimization=optimization)

    # Layer 3 — Persistence
    if not dry_run:
        repository.save(result)

    # Layer 4 — Delivery (only if alert threshold breached OR dry-run off)
    if not dry_run and report.needs_alert:
        log.warning(f"🚨 Alert threshold breached for {url} — sending Telegram alert")
        notifier.send(result)
    elif not dry_run:
        log.info(f"✅ {url} is within thresholds — no alert sent.")
        # Still send a daily summary? Commented to keep spam low.
        # notifier.send(result)

    if html:
        save_html(result)

    return result


@click.command()
@click.option("--url", default=None, help="Audit a single URL (overrides sites.yaml).")
@click.option("--strategy", default=None,
              type=click.Choice(["mobile", "desktop"]),
              help="mobile | desktop")
@click.option("--dry-run", is_flag=True,
              help="Skip AI + notifications (audit only).")
@click.option("--html", is_flag=True,
              help="Also save an HTML report per site under reports/.")
def main(url: str | None, strategy: str | None,
         dry_run: bool, html: bool) -> None:
    log.info("=" * 60)
    log.info(f"⚡ Speed-ZeroBaran v{settings.project_version} starting…")
    log.info(f"👤 Author: {settings.author_name} <{settings.author_email}>")
    log.info("=" * 60)

    missing = settings.validate()
    if missing and not dry_run:
        log.warning(
            f"Missing configuration keys: {', '.join(missing)}. "
            "Audit may degrade gracefully."
        )

    if url:
        sites = [{
            "name": url, "url": url,
            "strategy": strategy or settings.audit_strategy,
        }]
    else:
        sites = collect_sites()
        if strategy:  # override all
            for s in sites:
                s["strategy"] = strategy

    results: List[FullAuditResult] = []
    for site in sites:
        try:
            res = run_one(site, dry_run=dry_run, html=html)
            results.append(res)
        except Exception as exc:
            log.exception(f"❌ Audit failed for {site['url']}: {exc}")

    # ---------- Final summary ----------
    log.info("=" * 60)
    log.info("🏁 Audit cycle summary")
    for r in results:
        rep = r.report
        flag = "🚨" if rep.needs_alert else "✅"
        log.info(
            f"{flag} {rep.url}  perf={rep.performance_score}/100  "
            f"LCP={rep.vitals.lcp}  INP={rep.vitals.inp}  CLS={rep.vitals.cls}"
        )
    log.info("=" * 60)
    log.info("Done. Speed-ZeroBaran — by Baran Avisat.")


if __name__ == "__main__":
    main()
