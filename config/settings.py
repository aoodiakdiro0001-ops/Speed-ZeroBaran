"""
Speed-ZeroBaran — Central configuration loader
================================================
Loads environment variables and YAML configs once,
exposes them to all layers (Performance / AI / DB / Delivery).

Author : Baran Avisat <Baranavisat@gmail.com>
License: MIT  —  100% Free Tech Stack
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml
from dotenv import load_dotenv

# --- Load .env (local) or rely on GitHub Actions secrets ---
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass
class Settings:
    """Single source of truth for all runtime configuration."""

    # --- Target sites ---
    target_sites: List[str] = field(
        default_factory=lambda: [
            s.strip()
            for s in os.getenv("TARGET_SITES", "").split(",")
            if s.strip()
        ]
    )

    # --- PageSpeed API ---
    pagespeed_api_key: str = os.getenv("PAGESPEED_API_KEY", "")

    # --- AI providers ---
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    ai_provider: str = os.getenv("AI_PROVIDER", "gemini").lower()

    # --- Supabase ---
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_table: str = os.getenv("SUPABASE_TABLE", "speed_audit_logs")

    # --- Telegram ---
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # --- Audit thresholds ---
    speed_alert_threshold: float = float(
        os.getenv("SPEED_ALERT_THRESHOLD", "2.5")
    )
    score_alert_threshold: int = int(
        os.getenv("SCORE_ALERT_THRESHOLD", "70")
    )
    audit_strategy: str = os.getenv("AUDIT_STRATEGY", "mobile")
    cron_schedule: str = os.getenv("CRON_SCHEDULE", "0 */6 * * *")

    # --- Author / ownership ---
    author_name: str = "Baran Avisat"
    author_email: str = "Baranavisat@gmail.com"
    author_whatsapp: str = "00905313263722"
    project_name: str = "Speed-ZeroBaran"
    project_version: str = "1.0.0"

    def load_sites_from_yaml(self) -> list[dict]:
        """Load extra site config from config/sites.yaml (optional)."""
        yaml_path = ROOT_DIR / "config" / "sites.yaml"
        if not yaml_path.exists():
            return []
        with open(yaml_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return data.get("sites", [])

    def validate(self) -> list[str]:
        """Returns a list of missing-key warnings (empty = OK)."""
        missing = []
        if not self.pagespeed_api_key:
            missing.append("PAGESPEED_API_KEY")
        if not (self.gemini_api_key or self.groq_api_key):
            missing.append("GEMINI_API_KEY / GROQ_API_KEY")
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        return missing


# Singleton used everywhere
settings = Settings()
