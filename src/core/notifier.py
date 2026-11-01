"""
Speed-ZeroBaran — Layer 4: Delivery & Control
=============================================
Sends the final report to the user via Telegram Bot API.
Includes a graceful degradation path: if Telegram is unreachable,
the report is still written to disk so the GitHub Actions log
remains the source of truth.

Author : Baran Avisat <Baranavisat@gmail.com>
License: MIT
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import requests

from config import settings
from src.models.schemas import FullAuditResult
from src.utils import log, utc_now_iso, slugify


TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


class TelegramNotifier:
    """Send the markdown audit report to a Telegram chat."""

    def __init__(self) -> None:
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id

    @property
    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    # ---------- Public ----------
    def send(self, result: FullAuditResult) -> bool:
        """Send one FullAuditResult as a Telegram message."""
        message = result.to_telegram_message()
        # Telegram messages cap at 4096 chars — split if needed
        if len(message) <= 4096:
            return self._send_chunk(message)
        # Split into chunks of ~4000 chars at line boundaries
        chunks = self._split(message, 4000)
        ok = True
        for chunk in chunks:
            ok = self._send_chunk(chunk) and ok
        return ok

    # ---------- Internals ----------
    def _send_chunk(self, text: str) -> bool:
        if not self.is_configured:
            log.warning(
                "Telegram not configured — writing report to disk only."
            )
            self._save_to_disk(text)
            return False
        try:
            url = TELEGRAM_API.format(token=self.token, method="sendMessage")
            resp = requests.post(url, json={
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }, timeout=30)
            if resp.status_code == 200:
                log.info("📤 Telegram report delivered successfully.")
                return True
            # Fallback: parse_mode might choke on weird chars → retry as plain
            log.warning(
                f"Telegram markdown failed ({resp.status_code}) — retrying plain."
            )
            resp = requests.post(url, json={
                "chat_id": self.chat_id,
                "text": text,
                "disable_web_page_preview": True,
            }, timeout=30)
            if resp.status_code == 200:
                log.info("📤 Telegram report delivered (plain text).")
                return True
            log.error(f"Telegram send failed: {resp.text}")
            self._save_to_disk(text)
            return False
        except Exception as exc:
            log.error(f"Telegram exception: {exc}")
            self._save_to_disk(text)
            return False

    @staticmethod
    def _split(text: str, limit: int) -> list[str]:
        chunks, current = [], ""
        for line in text.split("\n"):
            if len(current) + len(line) + 1 > limit:
                chunks.append(current)
                current = ""
            current += line + "\n"
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _save_to_disk(text: str) -> Path:
        """Last-resort fallback: write the report to reports/."""
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        fname = (
            reports_dir
            / f"report_{slugify(utc_now_iso())}.txt"
        )
        fname.write_text(text, encoding="utf-8")
        log.info(f"📝 Report saved to {fname}")
        return fname


# Singleton
notifier = TelegramNotifier()

__all__ = ["TelegramNotifier", "notifier"]
