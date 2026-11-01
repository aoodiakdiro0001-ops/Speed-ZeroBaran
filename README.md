# ⚡ Speed-ZeroBaran

> **المنظومة الذاتية لمراقبة، تحليل، وتسريع أداء المواقع والتطبيقات**
> A 100% free, self-hosted, AI-powered web-performance monitoring system.

[![GitHub Actions](https://img.shields.io/badge/Runs%20on-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](.github/workflows/speed_audit.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-3ddc97.svg)](LICENSE)
[![100% Free](https://img.shields.io/badge/Tech%20Stack-100%25%20Free-3ddc97)]()

---

## 🇦🇪 ما هو Speed-ZeroBaran؟

**Speed-ZeroBaran** هو نظام ذكي متكامل ومستقل لاختبار سرعة المواقع، تتبع
مؤشرات الأداء الحيوية (Core Web Vitals)، واكتشاف الاختناقات البرمجية التي
تبطئ تحميل صفحاتك.

يقوم النظام بـ:
- 🔍 فحص موقعك دورياً من خوادم GitHub Actions المجانية كل بضع ساعات.
- 📊 قياس مؤشرات السرعة الرسمية: **LCP, INP, CLS, FCP, TTFB**.
- 🧠 استخدام الذكاء الاصطناعي (Gemini / Groq) لتحليل الأسباب الفعلية للبطء.
- 💻 توليد **كود حل جاهز للنسخ** (ضغط صور، تأجيل سكريبتات، تحسين كاش، …).
- 💾 حفظ السجلات التاريخية في **Supabase** لرسم منحنى التحسن.
- 📲 إرسال تقرير فوري على **Telegram** إذا انخفض الأداء عن الحد المقبول.

**كل ذلك دون دفع دولار واحد لأي منصة مراقبة مدفوعة.**

---

## 🇬🇧 What is Speed-ZeroBaran?

A fully autonomous, AI-augmented web-performance monitoring stack built entirely
on free-tier services. It periodically audits your sites, persists the results
to a database, asks an LLM to explain what is slow and write ready-to-paste
fixes, and pushes an alert to your phone — all for $0/month.

---

## 🛠️ The Free Tech Stack

| Layer | Free Service | Role |
|------|--------------|------|
| ⏰ **Scheduling Engine** | [GitHub Actions](https://github.com/features/actions) | Free runner that fires the audit every few hours |
| 🔎 **Performance Core** | [PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/get-started) + [Lighthouse CLI](https://github.com/GoogleChrome/lighthouse) | Measures LCP/INP/CLS and pulls all opportunities |
| 🧠 **AI Optimization Brain** | [Google Gemini API](https://aistudio.google.com/) & [Groq API](https://console.groq.com/) | Reads audit JSON, diagnoses bottlenecks, writes code fixes |
| 💾 **Persistence Layer** | [Supabase](https://supabase.com/) (PostgreSQL free tier) | Stores historical audit logs for trend analysis |
| 📲 **Delivery & UI** | [Telegram Bot API](https://core.telegram.org/bots/api) + [Vercel](https://vercel.com/) | Instant alerts on phone + public dashboard |

---

## 📐 Software Architecture

```
        ┌──────────────────────────────────┐
        │   Your website / web app target  │
        └──────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │ Layer 1 — Performance Ingestion  │
        │  GitHub Actions + PageSpeed API  │
        │  + Lighthouse CLI fallback       │
        └──────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │ Layer 2 — AI Optimization Core   │
        │  Google Gemini  or  Groq (free)  │
        │  → root causes + code fixes      │
        └──────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │ Layer 3 — Persistence Layer      │
        │  Supabase (PostgreSQL)           │
        │  → historical audit logs         │
        └──────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │ Layer 4 — Delivery & Control     │
        │  Telegram Bot (instant alert)    │
        │  + Vercel dashboard (HTML)       │
        └──────────────────────────────────┘
```

---

## 🚀 Quick Start (5 minutes)

### 1. Clone & bootstrap
```bash
git clone <your-fork-url>.git
cd Speed-ZeroBaran
bash scripts/install.sh
```

### 2. Get your free API keys
| Service | Where to get it | Free quota |
|---------|-----------------|-----------|
| PageSpeed Insights API | [Google Cloud Console](https://developers.google.com/speed/docs/insights/v5/get-started) | 25k calls/day |
| Google Gemini | [AI Studio](https://aistudio.google.com/app/apikey) | 15 req/min, 1500/day |
| Groq (fallback) | [console.groq.com](https://console.groq.com/keys) | Generous free tier |
| Supabase | [supabase.com](https://supabase.com/) | 500MB DB, 50k MAU |
| Telegram Bot | Talk to [@BotFather](https://t.me/BotFather) | Unlimited |

### 3. Configure `.env`
```bash
cp .env.example .env
# Edit .env with your favorite editor
```

### 4. Create the database table
Open Supabase → SQL Editor → paste `scripts/setup_db.sql` → Run.

### 5. Test locally
```bash
python scripts/run_audit.py --url https://example.com --html
```
Open `reports/*.html` to see the full report. You should also receive a
Telegram message if the site breaches your thresholds.

### 6. Push to GitHub
1. Create a new repo and push this folder to it.
2. In **Settings → Secrets and variables → Actions**, add the same keys
   you put in `.env`:
   - `TARGET_SITES`, `PAGESPEED_API_KEY`
   - `GEMINI_API_KEY` (or `GROQ_API_KEY`)
   - `SUPABASE_URL`, `SUPABASE_KEY`
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
3. GitHub Actions will fire automatically every 6 hours. You can also
   trigger it manually via **Actions → Speed-ZeroBaran Audit → Run workflow**.

### 7. (Optional) Deploy the Vercel dashboard
```bash
cd dashboard
npx vercel --prod
```
Open the deployed URL, paste your Supabase URL + anon key, and you have a
live performance dashboard.

---

## 📂 Project Structure

```
Speed-ZeroBaran/
├── .github/workflows/
│   ├── speed_audit.yml          ← Every-6-hours audit job
│   └── lighthouse_audit.yml     ← Weekly deep Lighthouse run
├── config/
│   ├── settings.py              ← Single source of truth (env vars)
│   └── sites.yaml               ← Extra sites config (optional)
├── src/
│   ├── core/
│   │   ├── performance.py       ← Layer 1: PageSpeed + Lighthouse
│   │   ├── ai_optimizer.py      ← Layer 2: Gemini / Groq
│   │   ├── database.py          ← Layer 3: Supabase
│   │   ├── notifier.py          ← Layer 4: Telegram
│   │   └── report.py            ← HTML report renderer
│   ├── models/
│   │   └── schemas.py           ← Typed dataclasses shared across layers
│   └── utils/
│       ├── logger.py            ← Rich console logging
│       └── helpers.py           ← Misc utilities
├── scripts/
│   ├── run_audit.py             ← Main CLI orchestrator
│   ├── setup_db.sql             ← Supabase schema
│   └── install.sh               ← One-shot bootstrap
├── dashboard/
│   ├── index.html               ← Vercel dashboard (vanilla JS)
│   ├── vercel.json
│   └── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   └── API_KEYS.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── CHANGELOG.md
└── README.md
```

---

## ⚙️ How It Works (End-to-End Workflow)

1. **الحدث (Trigger):** في الأوقات المجدولة، يستيقظ GitHub Actions ويبدأ
   بفحص روابط مواقعك.
2. **الفحص والقياس (Audit):** يستدعي النظام PageSpeed API لقياس درجات
   الأداء ومؤشرات Core Web Vitals واكتشاف كل عنصر يسبب بطء التصفح.
3. **التحليل والاقتراح (AI Analyze):** يأخذ الذكاء الاصطناعي (Gemini أو
   Groq) التقرير التقني، يحدد الملفات الثقيلة أو النصوص المعطلة للعرض،
   ويكتب كود الحل (ضغط صور، تأجيل تحميل السكريبتات، تحسين التخزين المؤقت، …).
4. **النتيجة الفورية (Delivery):** يأتيك تقرير أداء مذهل عبر Telegram مع
   حلول فورية تجعل موقعك يطير كالبرق، ودون دفع سنت واحد لأي أداة مراقبة
   مدفوعة. كل البيانات تُحفظ أيضاً في Supabase لمتابعة التحسن عبر الزمن.

مثال على رسالة Telegram:

> ⚡ تقرير أداء الموقع: انخفضت سرعة التحميل إلى 2.1 ثانية.
> 🛠️ سبب البطء الرئيسي: صورة رئيسية غير مضغوطة بحجم 3.4 ميجابايت في الصفحة الرئيسية.
> 💻 الإصلاح المقترح: (الكود أو التوجيه الجاهز للتنفيذ فوراً).

---

## 🔧 CLI Usage

```bash
# Audit all configured sites
python scripts/run_audit.py

# Audit a single URL
python scripts/run_audit.py --url https://example.com

# Choose strategy
python scripts/run_audit.py --strategy desktop

# Dry run (audit only, skip AI + Telegram)
python scripts/run_audit.py --dry-run

# Also save HTML reports under reports/
python scripts/run_audit.py --html
```

---

## 📊 Sample Telegram Alert

```
⚡ Speed-ZeroBaran — تقرير أداء الموقع
🌐 الموقع: https://example.com
📊 درجة الأداء: 58/100
📱 الاستراتيجية: mobile

🔬 مؤشرات الأداء الحيوية (Core Web Vitals):
   • LCP: 4.20s
   • INP: 312ms
   • CLS: 0.180
   • FCP: 2.10s
   • TTFB: 0.95s

🛠️ تشخيص الذكاء الاصطناعي:
الموقع يعاني من بطء في التحميل بسبب صورة هيرو ضخمة غير مضغوطة،
إضافة إلى ثلاثة سكريبتات تعرقل العرض الأولي للصفحة.

📌 الأسباب الرئيسية للبطء:
   • صورة hero.png بحجم 3.4MB (تحتاج ضغط WebP)
   • 3 ملفات JS تعرقل العرض (render-blocking)
   • لا يوجد preload للموارد الحرجة

💻 الإصلاحات المقترحة (جاهزة للنسخ):
   ضغط الصورة إلى WebP
   <picture>
     <source srcset="/img/hero.webp" type="image/webp">
     <img src="/img/hero.png" alt="Hero" loading="lazy" width="1200">
   </picture>

   تأجيل تحميل السكريبتات
   <script src="/js/analytics.js" defer></script>
   <script src="/js/chat.js"   defer></script>

——————————————————————————————
👤 Speed-ZeroBaran — by Baran Avisat
✉️ Baranavisat@gmail.com  •  📱 +90 531 326 3722
```

---

## 👤 Author & Support

| Field | Value |
|-------|-------|
| **Author** | **Baran Avisat** |
| **Email** | Baranavisat@gmail.com |
| **WhatsApp** | +90 531 326 3722 (00905313263722) |
| **License** | MIT — see [LICENSE](LICENSE) |
| **Project** | #23 in the software-innovation registry |

For support, questions, or custom deployments, contact the author directly
via WhatsApp or email. All rights reserved to the author.

---

## 📜 License

```
MIT License — Copyright (c) 2026 Baran Avisat <Baranavisat@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
```

See [LICENSE](LICENSE) for the full text.

---

## 🙏 Acknowledgements

Built on the shoulders of giants — all of whom provide incredible free tiers:

- **Google** — PageSpeed Insights API, Gemini API, Lighthouse
- **GitHub** — Actions (free for public repos + 2000 min/month private)
- **Supabase** — PostgreSQL-as-a-service with REST API
- **Groq** — Free, blazing-fast LLM inference
- **Telegram** — Free Bot API with no message cap
- **Vercel** — Free static-site hosting

---

**⚡ Speed-ZeroBaran** — _اجعل موقعك يطير كالبرق، دون دفع سنت._

---

## 🧾 بيانات المالك وحقوق الملكية (Owner & Copyright)

| الحقل | القيمة |
|---|---|
| **المؤلف / Owner** | **Baran Avisat** |
| **البريد / Email** | [baranavisat@gmail.com](mailto:baranavisat@gmail.com) |
| **واتساب / WhatsApp** | +90 531 326 37 22 |
| **الحساب البنكي / IBAN** | `TR10 0001 0090 1008 4013 0050 01` |
| **GitHub** | [github.com/aoodiakdiro0001-ops](https://github.com/aoodiakdiro0001-ops) |
| **المتجر / Store** | [baranavi.gumroad.com](https://baranavi.gumroad.com/) |
| **الترخيص / License** | MIT License (with attribution) |

**© 2026 Baran Avisat — جميع الحقوق محفوظة / All Rights Reserved.**
