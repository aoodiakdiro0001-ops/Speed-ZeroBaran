# 📦 Speed-ZeroBaran — Installation Guide

## Prerequisites

- **Python 3.11+** — [python.org](https://python.org)
- **Node.js 18+** (optional, for Lighthouse CLI fallback) — [nodejs.org](https://nodejs.org)
- **A GitHub account** (free) — for the scheduled Actions runner
- **A Supabase account** (free) — [supabase.com](https://supabase.com)
- **A Google account** (free) — for PageSpeed API + Gemini API
- **A Telegram account** (free) — for instant alerts

---

## Step 1 — Get the code

```bash
git clone <your-fork>.git
cd Speed-ZeroBaran
```

## Step 2 — Bootstrap the environment

```bash
bash scripts/install.sh
```

This script:
- Creates a Python virtualenv in `.venv/`
- Installs all `requirements.txt`
- Installs Lighthouse CLI globally (if npm is available)
- Copies `.env.example` → `.env` if `.env` doesn't exist
- Runs a smoke test to verify imports work

## Step 3 — Get your free API keys

See [docs/API_KEYS.md](API_KEYS.md) for step-by-step instructions on every key.

## Step 4 — Configure `.env`

Open `.env` and fill in every key you obtained in step 3.

```bash
nano .env
```

At minimum you need:
- `PAGESPEED_API_KEY`
- `GEMINI_API_KEY` **or** `GROQ_API_KEY`
- `SUPABASE_URL`, `SUPABASE_KEY`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `TARGET_SITES` (comma-separated list of URLs to monitor)

## Step 5 — Set up the database

1. Log in to [Supabase](https://supabase.com/dashboard)
2. Create a new project (free tier)
3. Wait ~2 minutes for it to provision
4. Go to **SQL Editor → New query**
5. Paste the contents of `scripts/setup_db.sql`
6. Click **Run** — you should see "Success. No rows returned."
7. The table `speed_audit_logs` and view `v_latest_audit_per_url` are now ready.

## Step 6 — Test locally

```bash
# Activate the venv
source .venv/bin/activate

# Run a single audit
python scripts/run_audit.py --url https://example.com --html
```

You should see:
- Console output with the audit results
- An HTML report in `reports/`
- A Telegram message (if the site breaches thresholds)
- A new row in your Supabase table (check Table Editor)

## Step 7 — Push to GitHub and configure secrets

1. Create a new GitHub repo (private is fine; free Actions minutes apply)
2. Push the code:
   ```bash
   git init
   git add .
   git commit -m "feat: Speed-ZeroBaran v1.0.0 by Baran Avisat"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
3. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**
4. Add every key from your `.env` as a secret with the **same name**:
   - `TARGET_SITES`
   - `PAGESPEED_API_KEY`
   - `GEMINI_API_KEY` (and `GEMINI_MODEL` if changed)
   - `GROQ_API_KEY` (and `GROQ_MODEL`)
   - `SUPABASE_URL`, `SUPABASE_KEY`
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
   - `AI_PROVIDER`
   - `SPEED_ALERT_THRESHOLD`, `SCORE_ALERT_THRESHOLD`

## Step 8 — Trigger the first run

1. In GitHub, go to **Actions → Speed-ZeroBaran Audit**
2. Click **Run workflow** → choose `main` branch → **Run workflow**
3. Watch the live log — it should complete in 1–3 minutes per site.
4. Check your Telegram — you should get the first report!

## Step 9 — (Optional) Deploy the Vercel dashboard

```bash
cd dashboard
npx vercel --prod
```

Open the deployed URL → paste your Supabase URL + **anon key** (not the
service key!) → click **تحميل**. You should see one card per monitored site
with its latest score.

---

## Troubleshooting

### "Quota exceeded for PageSpeed API (429)"
The free tier allows 25,000 calls/day. If you exceed this:
- Reduce the audit frequency in `.github/workflows/speed_audit.yml` (change cron)
- Or rely on the Lighthouse CLI fallback (install it with `npm i -g lighthouse`)

### "Telegram markdown failed"
Some AI-generated code snippets contain characters that confuse Telegram's
markdown parser. The notifier automatically retries as plain text — your
message will still arrive.

### "Supabase insert failed: 401"
You're using the anon key in `SUPABASE_KEY` but RLS is blocking writes.
Either:
- Use the **service_role key** for `SUPABASE_KEY`, or
- Adjust the RLS policy in `setup_db.sql` (less secure)

### "No module named 'google.generativeai'"
Re-run `bash scripts/install.sh` or manually `pip install -r requirements.txt`
inside your virtualenv.

### GitHub Actions workflow not triggering
- Public repos: scheduled workflows run on the GitHub-default UTC cron.
- Private repos: scheduled workflows may be disabled after 60 days of repo
  inactivity. Make a commit to re-activate.

---

## Need help?

📧 **Baranavisat@gmail.com**  •  📱 **+90 531 326 3722** (WhatsApp)

*Speed-ZeroBaran — by Baran Avisat — MIT License*
