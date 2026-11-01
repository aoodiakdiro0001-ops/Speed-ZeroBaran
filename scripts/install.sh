#!/usr/bin/env bash
# ============================================================
# Speed-ZeroBaran — Local environment bootstrap
# Installs Python deps + Lighthouse CLI + verifies the setup.
# Author: Baran Avisat <Baranavisat@gmail.com>
# License: MIT
# ============================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "============================================================"
echo "⚡ Speed-ZeroBaran — Bootstrap"
echo "👤 Baran Avisat <Baranavisat@gmail.com>"
echo "============================================================"

# --- Python virtualenv ---
if [[ ! -d .venv ]]; then
    echo "🐍 Creating Python virtualenv…"
    python3 -m venv .venv
fi
source .venv/bin/activate

echo "📦 Installing Python dependencies…"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# --- Lighthouse CLI (optional fallback) ---
if ! command -v lighthouse &> /dev/null; then
    echo "🌐 Installing Lighthouse CLI (fallback for API quota)…"
    npm install -g lighthouse || echo "⚠️ npm not available — Lighthouse fallback disabled"
fi

# --- Verify .env ---
if [[ ! -f .env ]]; then
    echo "📝 Copying .env.example -> .env"
    cp .env.example .env
    echo "⚠️  Edit .env and fill in your free-tier API keys before running."
fi

# --- Quick smoke test ---
echo "🧪 Running smoke test…"
python -c "
import sys
sys.path.insert(0, '.')
from config import settings
print(f'Project: {settings.project_name} v{settings.project_version}')
print(f'Author : {settings.author_name} <{settings.author_email}>')
print('OK')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your free-tier API keys"
echo "  2. Run scripts/setup_db.sql in your Supabase SQL editor"
echo "  3. Test locally:  python scripts/run_audit.py --url https://example.com"
echo "  4. Push to GitHub — Actions will pick up the schedule automatically"
echo ""
echo "GitHub Actions secrets to set (Settings → Secrets → Actions):"
echo "  PAGESPEED_API_KEY, GEMINI_API_KEY (or GROQ_API_KEY),"
echo "  SUPABASE_URL, SUPABASE_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID"
