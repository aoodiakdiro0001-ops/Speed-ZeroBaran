# Changelog — Speed-ZeroBaran

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-11-01 — Initial Public Release

### Added
- 🎯 **Layer 1 — Performance Ingestion**: Google PageSpeed Insights API
  integration with automatic Lighthouse CLI fallback for quota-exhaustion days.
  Extracts LCP, INP (replacing legacy FID), CLS, FCP, TTFB, TBT, Speed Index.
- 🧠 **Layer 2 — AI Optimization Core**: dual-provider support for Google
  Gemini API and Groq API with automatic failover. Strict JSON-schema prompt
  guarantees structured code-fix output.
- 💾 **Layer 3 — Persistence Layer**: Supabase (PostgreSQL) integration with
  append-only audit log table, RLS policies, and `v_latest_audit_per_url`
  view for the dashboard.
- 📲 **Layer 4 — Delivery & Control**: Telegram Bot API integration with
  automatic message splitting, markdown-to-plain fallback, and disk-cache
  last-resort write. Plus a self-contained Vercel HTML dashboard with
  auto-refresh and localStorage-based config.
- ⏰ **GitHub Actions workflows**: scheduled audit every 6 hours + weekly
  deep Lighthouse run on both mobile and desktop strategies.
- 📜 Complete documentation: README (bilingual Arabic/English),
  ARCHITECTURE.md, INSTALLATION.md, API_KEYS.md.
- 🗃️ Supabase SQL schema with indexes, RLS policies, and view.
- 🛠️ `install.sh` bootstrap script for one-command local setup.
- 🐍 CLI orchestrator (`scripts/run_audit.py`) with `--url`, `--strategy`,
  `--dry-run`, and `--html` flags.

### Author
**Baran Avisat** <Baranavisat@gmail.com> • WhatsApp: +90 531 326 3722

### License
MIT — see [LICENSE](LICENSE).

---

## Future roadmap (unreleased)

- [ ] Slack & Discord notifiers
- [ ] Weekly trend email digest
- [ ] Auto-open GitHub issues for regressions
- [ ] Multi-region audit (run from EU, US, Asia runners)
- [ ] LLM-powered auto-fix PRs (let the AI open a pull request with the fix)

*Project #23 in the software-innovation registry of Baran Avisat.*
