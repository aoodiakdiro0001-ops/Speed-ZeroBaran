# 🔑 Speed-ZeroBaran — API Keys Guide

Every key below is **100% free**. None of them require a credit card.

---

## 1. Google PageSpeed Insights API Key

**Free quota:** 25,000 calls/day — more than enough for hourly audits on
dozens of sites.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or pick an existing one)
3. **APIs & Services → Library → search "PageSpeed Insights API" → Enable**
4. **APIs & Services → Credentials → Create credentials → API key**
5. Copy the key → put it in `PAGESPEED_API_KEY`

---

## 2. Google Gemini API Key

**Free quota:** 15 requests/minute, 1,500 requests/day for `gemini-1.5-flash`.

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with any Google account
3. Click **Create API key**
4. Choose an existing Google Cloud project (or create a new one)
5. Copy the key → put it in `GEMINI_API_KEY`
6. (Optional) Pick a model: `gemini-1.5-flash` (fast, default) or
   `gemini-1.5-pro` (smarter, lower quota)

---

## 3. Groq API Key (fallback AI)

**Free quota:** Generous — typically 30 req/min, 14,400 req/day.

1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign in with Google or GitHub
3. Click **Create API Key**
4. Copy → put it in `GROQ_API_KEY`
5. (Optional) Pick a model: `llama3-70b-8192` (default),
   `mixtral-8x7b-32768`, or `gemma2-9b-it`

Set `AI_PROVIDER=groq` in `.env` to use Groq as the primary; otherwise
Gemini is used and Groq is the automatic fallback when Gemini fails.

---

## 4. Supabase URL + Key

**Free tier:** 500 MB database, 50,000 monthly active users, unlimited API.

1. Go to [Supabase](https://supabase.com/dashboard)
2. Click **New project** — give it any name
3. Set a strong database password (save it somewhere safe — you won't need
   it for our script, but you'll need it for direct DB access)
4. Choose a region close to your users
5. Wait ~2 minutes for provisioning
6. Go to **Project Settings → API**
7. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **service_role secret key** → `SUPABASE_KEY` (this has write access;
     for a public dashboard use the **anon public** key instead)

Then run the SQL schema:
1. Go to **SQL Editor → New query**
2. Paste `scripts/setup_db.sql`
3. **Run**

---

## 5. Telegram Bot Token + Chat ID

**Free quota:** Unlimited messages, no rate cap for normal use.

### Create the bot
1. Open Telegram, search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a name (e.g. "Speed-ZeroBaran")
4. Choose a username ending in `bot` (e.g. `speed_zerobaran_bot`)
5. BotFather replies with an HTTP API token → copy it → `TELEGRAM_BOT_TOKEN`

### Get your chat ID
1. Search for [@userinfobot](https://t.me/userinfobot) (or [@getmyid_bot](https://t.me/getmyid_bot))
2. Send `/start`
3. It replies with your numeric chat ID → copy → `TELEGRAM_CHAT_ID`

### For a group chat (optional)
1. Create a Telegram group
2. Add your bot to the group
3. Send any message in the group
4. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser
5. Find `"chat":{"id":-1001234567890,...}` — the negative number is your
   group chat ID → put it in `TELEGRAM_CHAT_ID`

### Test the bot
```bash
curl -s "https://api.telegram.org/bot<TOKEN>/sendMessage" \
     -d "chat_id=<CHAT_ID>" \
     -d "text=Speed-ZeroBaran test ✅"
```
You should receive the message on your phone.

---

## 6. (Optional) Vercel for the dashboard

**Free tier:** 100 GB bandwidth, unlimited static deployments.

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. `cd dashboard && npx vercel --prod`
3. Follow the prompts — accept the defaults

The dashboard asks for the Supabase URL + **anon** key in-browser.

---

## Environment variables summary

| Variable | Required | Free quota |
|----------|----------|------------|
| `PAGESPEED_API_KEY` | ✅ | 25k/day |
| `GEMINI_API_KEY` | ⚠️ one of two | 1,500/day |
| `GROQ_API_KEY` | ⚠️ one of two | 14k/day |
| `SUPABASE_URL` | ✅ | 500 MB DB |
| `SUPABASE_KEY` | ✅ | unlimited API |
| `TELEGRAM_BOT_TOKEN` | ✅ | unlimited |
| `TELEGRAM_CHAT_ID` | ✅ | — |
| `TARGET_SITES` | ✅ | — |
| `SPEED_ALERT_THRESHOLD` | optional (default 2.5s) | — |
| `SCORE_ALERT_THRESHOLD` | optional (default 70) | — |
| `AUDIT_STRATEGY` | optional (default mobile) | — |
| `AI_PROVIDER` | optional (default gemini) | — |

---

*Speed-ZeroBaran — by Baran Avisat <Baranavisat@gmail.com> — MIT License*
