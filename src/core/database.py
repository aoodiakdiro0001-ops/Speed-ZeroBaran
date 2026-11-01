"""
Speed-ZeroBaran — Layer 3: Persistence Layer
=============================================
Stores every audit run in Supabase (PostgreSQL free tier) so we
can plot historical performance trends and detect regressions.

The SQL schema lives in scripts/setup_db.sql — run it once in the
Supabase SQL editor to create the `speed_audit_logs` table.

Author : Baran Avisat <Baranavisat@gmail.com>
License: MIT
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from config import settings
from src.models.schemas import AuditReport, FullAuditResult
from src.utils import log, safe_json


class AuditRepository:
    """Thin wrapper around the Supabase REST API (no heavy SDK needed)."""

    def __init__(self) -> None:
        self.url = settings.supabase_url.rstrip("/")
        self.key = settings.supabase_key
        self.table = settings.supabase_table

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.key)

    # ---------- Insert ----------
    def save(self, result: FullAuditResult) -> Optional[Dict[str, Any]]:
        """Insert one audit run (report + AI optimization)."""
        if not self.is_configured:
            log.warning("Supabase not configured — skipping persistence.")
            return None

        import requests

        r = result.report
        o = result.optimization
        payload = {
            "url": r.url,
            "site_name": r.site_name,
            "strategy": r.strategy,
            "performance_score": r.performance_score,
            "accessibility_score": r.accessibility_score,
            "best_practices_score": r.best_practices_score,
            "seo_score": r.seo_score,
            "lcp": r.vitals.lcp,
            "inp": r.vitals.inp,
            "cls": r.vitals.cls,
            "fcp": r.vitals.fcp,
            "ttfb": r.vitals.ttfb,
            "tbt": r.vitals.tbt,
            "speed_index": r.vitals.si,
            "total_loading_time": r.total_loading_time,
            "needs_alert": r.needs_alert,
            "opportunities": safe_json(r.opportunities),
            "diagnostics": safe_json(r.diagnostics),
            "ai_summary": o.summary,
            "ai_root_causes": safe_json(o.root_causes),
            "ai_code_fixes": safe_json(o.code_fixes),
            "ai_priority": o.priority,
            "audit_timestamp": r.audit_timestamp,
        }
        try:
            resp = requests.post(
                f"{self.url}/rest/v1/{self.table}",
                json=payload,
                headers={
                    "apikey": self.key,
                    "Authorization": f"Bearer {self.key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                timeout=30,
            )
            resp.raise_for_status()
            log.info(f"💾 Saved audit row for {r.url}")
            return resp.json()
        except Exception as exc:
            log.error(f"Supabase insert failed: {exc}")
            return None

    # ---------- Query history ----------
    def history(self, url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most-recent N audit rows for `url`, oldest first."""
        if not self.is_configured:
            return []
        import requests
        try:
            resp = requests.get(
                f"{self.url}/rest/v1/{self.table}",
                params={
                    "url": f"eq.{url}",
                    "order": "audit_timestamp.desc",
                    "limit": str(limit),
                },
                headers={
                    "apikey": self.key,
                    "Authorization": f"Bearer {self.key}",
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            data.reverse()  # oldest first for plotting
            return data
        except Exception as exc:
            log.error(f"Supabase history query failed: {exc}")
            return []

    # ---------- Stats ----------
    def latest_score(self, url: str) -> Optional[Dict[str, Any]]:
        """Convenience: latest perf score + timestamp for a URL."""
        rows = self.history(url, limit=1)
        return rows[-1] if rows else None


# Singleton
repository = AuditRepository()

__all__ = ["AuditRepository", "repository"]
