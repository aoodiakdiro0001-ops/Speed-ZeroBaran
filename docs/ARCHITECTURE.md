# 🏗️ Speed-ZeroBaran — Architecture Deep Dive

> This document explains the engineering decisions behind the 4-layer design.
> For a high-level overview see [README.md](../README.md).

## Design Principles

1. **100% free-tier** — every external service must have a usable free quota.
2. **Layered separation** — each layer can be swapped without breaking the others
   (e.g. Gemini → Groq, Supabase → Notion API, Telegram → Discord).
3. **Graceful degradation** — if one service is down or unconfigured, the
   pipeline still produces a (partial) result.
4. **Stateless runners** — GitHub Actions runners are ephemeral; all state
   lives in Supabase, not on disk.
5. **Bilingual** — code is in English, user-facing messages are in Arabic
   (the author's primary audience).

---

## Layer 1 — Performance Ingestion (`src/core/performance.py`)

**Tech:** Google PageSpeed Insights API + Lighthouse CLI (fallback)

The `PerformanceAuditor.audit(url, strategy)` method:

1. Calls `https://www.googleapis.com/pagespeedonline/v5/runPagesSpeed` with
   `url`, `strategy` (`mobile|desktop`), `category` (performance, accessibility,
   best-practices, seo) and the free `key`.
2. On HTTP 429 (quota) or network failure, falls back to running the
   `lighthouse` CLI locally inside the GitHub Actions runner — this gives us
   an extra 25k+ audits per day without touching the API quota.
3. Parses the response JSON (Lighthouse + loadingExperience) into a strongly
   typed `AuditReport` dataclass.

### Core Web Vitals extraction

```python
vitals = CoreWebVitals(
    lcp = audits["largest-contentful-paint"]["numericValue"] / 1000,
    inp = audits["interaction-to-next-paint"]["numericValue"],  # INP (2024+)
    cls = audits["cumulative-layout-shift"]["numericValue"],
    fcp = audits["first-contentful-paint"]["numericValue"] / 1000,
    ttfb = audits["server-response-time"]["numericValue"] / 1000,
    ...
)
```

> Note: Google replaced FID with INP in March 2024. We probe `interaction-to-next-paint`
> first, then fall back to `experimental-interaction` for older reports.

---

## Layer 2 — AI Optimization Core (`src/core/ai_optimizer.py`)

**Tech:** Google Gemini API (primary) + Groq API (fallback)

Both providers are called behind a single `AIOptimizer.analyze(report)` method.
The `__init__` auto-detects which provider is configured and silently falls
back if the chosen one's key is missing.

### Prompt design

We use a **system instruction** that pins the LLM to a strict JSON schema:

```json
{
  "summary": "string",
  "root_causes": ["string", ...],
  "priority": "high|medium|low",
  "code_fixes": [
    {
      "title": "string",
      "language": "html|css|js|python|nginx|json|bash",
      "code": "string",
      "explanation": "string"
    }
  ]
}
```

This guarantees the response parses cleanly into our `AIOptimization` dataclass,
no matter which provider generated it.

### Resilience

- Gemini supports `response_mime_type: "application/json"` natively → forces valid JSON.
- Groq supports `response_format: {"type": "json_object"}` → same effect.
- If parsing fails anyway, we extract the first `{...}` block as a last resort,
  and if even that fails, we save the raw text as the `summary` so the user
  still sees something useful.

---

## Layer 3 — Persistence (`src/core/database.py`)

**Tech:** Supabase (PostgreSQL) — accessed via the auto-generated REST API.

We deliberately avoid pulling in the heavy `supabase-py` SDK and instead use
plain `requests` against `/rest/v1/<table>`. This keeps the dependency tree
tiny and means the same code works for any PostgREST-style backend.

### Schema (see `scripts/setup_db.sql`)

- **`speed_audit_logs`** — append-only audit rows (one per site per run).
- **`v_latest_audit_per_url`** — view returning the most recent audit per URL.
  The Vercel dashboard reads from this view.
- **RLS** is enabled; the service role has full access, anonymous users get
  read-only on the table (so the public dashboard works).

### Indexes

```sql
CREATE INDEX idx_audit_url_time   ON speed_audit_logs (url, audit_timestamp DESC);
CREATE INDEX idx_audit_needs_alert ON speed_audit_logs (needs_alert) WHERE needs_alert = TRUE;
```

---

## Layer 4 — Delivery & Control (`src/core/notifier.py` + `dashboard/`)

### Telegram

The `TelegramNotifier.send(result)` method renders the audit as a markdown
message using the `FullAuditResult.to_telegram_message()` template, then:

1. Splits messages > 4096 chars at line boundaries (Telegram's hard cap).
2. Tries `parse_mode=Markdown` first.
3. On parse error (rare edge cases with backticks), retries as plain text.
4. If Telegram itself is unreachable, writes the report to `reports/<ts>.txt`
   so nothing is ever lost.

### Vercel Dashboard

A single self-contained `index.html` (no build step, no framework). The user
pastes their Supabase URL + anon key once; both are stored in `localStorage`
and never leave the browser except to talk directly to Supabase.

The dashboard reads the `v_latest_audit_per_url` view and renders one card per
site with the perf score, all Core Web Vitals, the AI summary, and the
timestamp of the last audit. An optional 60-second auto-refresh is built in.

---

## Data flow diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  GitHub Actions Runner                      │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ performance │───▶│ ai_optimizer│───▶│  database   │     │
│  │   .audit()  │    │  .analyze() │    │   .save()   │     │
│  └─────────────┘    └─────────────┘    └──────┬──────┘     │
│         │                  │                  │            │
│         ▼                  ▼                  ▼            │
│   PageSpeed API     Gemini / Groq         Supabase         │
│   (or Lighthouse    (free tier)           (free tier)      │
│    CLI fallback)                                          │
│                                                            │
│  ┌─────────────┐                                           │
│  │  notifier   │◀──── FullAuditResult                     │
│  │   .send()   │                                           │
│  └─────────────┘                                           │
│         │                                                  │
└─────────┼──────────────────────────────────────────────────┘
          ▼
      Telegram ────► User phone
      Vercel  ────► Public dashboard (reads from Supabase)
```

---

## Why these choices?

| Decision | Rationale |
|----------|-----------|
| **PageSpeed API over pure Lighthouse CLI** | API is faster (no browser launch) and doesn't need a headless Chrome in CI. We keep Lighthouse as a fallback for quota-exhaustion days. |
| **Gemini + Groq, not OpenAI** | Both have genuinely free tiers; OpenAI does not. Gemini's JSON mode is the most reliable for structured output. |
| **Supabase over Notion/Airtable** | Real SQL means we can build the `v_latest_audit_per_url` view and trend queries; not just a flat sheet. |
| **Telegram over email** | Instant push, free, no SMTP config, no spam folder, supports markdown + 4096-char messages. |
| **GitHub Actions over self-hosted cron** | Free 2000 minutes/month for private repos, unlimited for public. No server to maintain. |
| **Dataclasses over Pydantic models** | Lighter dependency, sufficient for our needs. Pydantic is in requirements only as an optional convenience. |
| **Plain `requests` over Supabase SDK** | One less heavy dependency; the PostgREST API is simple enough. |

---

## Extending the system

### Add a new AI provider
1. Implement `def _call_<provider>(self, prompt: str) -> str` in `ai_optimizer.py`.
2. Add a branch in `_call_llm()` dispatch.
3. Add the API-key env var to `Settings`.

### Add a new notification channel (Discord, Slack, Email)
1. Implement a `send(result: FullAuditResult) -> bool` method following
   the `TelegramNotifier` pattern.
2. Wire it up in `scripts/run_audit.py` next to the existing notifier call.

### Add a new audit source (WebPageTest, Pingdom)
1. Add a method to `PerformanceAuditor` returning the same raw Lighthouse-shape JSON.
2. The `_parse_to_report` method will handle the rest unchanged.

---

*Speed-ZeroBaran — by Baran Avisat <Baranavisat@gmail.com> — MIT License*
