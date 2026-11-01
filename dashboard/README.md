# Speed-ZeroBaran — Vercel Dashboard

A single-page dashboard that reads from Supabase (the `v_latest_audit_per_url` view)
and shows the latest performance scores + Core Web Vitals for every monitored site.

## Deploy to Vercel (free)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import this `dashboard/` folder (or the whole repo and set the root to `dashboard/`)
3. Click **Deploy** — no environment variables needed (the dashboard asks for
   Supabase URL + anon key in-browser and stores them in `localStorage`).

## Run locally

Just open `index.html` in a browser, or:

```bash
npx serve .
```

## Privacy

The Supabase key you enter is the **anon key** (read-only) and stays in your
browser's `localStorage`. It is never sent anywhere except directly to your
own Supabase project.

---

*Speed-ZeroBaran — by Baran Avisat <Baranavisat@gmail.com>*
