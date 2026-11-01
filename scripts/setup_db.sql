-- ============================================================
-- Speed-ZeroBaran — Supabase / PostgreSQL schema
-- Run this once in the Supabase SQL editor (Dashboard > SQL).
-- Author: Baran Avisat <Baranavisat@gmail.com>
-- License: MIT
-- ============================================================

-- Drop if you need a clean reset (careful — this deletes history!)
-- DROP TABLE IF EXISTS speed_audit_logs CASCADE;

CREATE TABLE IF NOT EXISTS speed_audit_logs (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    url                 TEXT NOT NULL,
    site_name           TEXT,
    strategy            TEXT,
    performance_score   INT,
    accessibility_score INT,
    best_practices_score INT,
    seo_score           INT,
    lcp                 REAL,    -- Largest Contentful Paint (sec)
    inp                 REAL,    -- Interaction to Next Paint (sec)
    cls                 REAL,    -- Cumulative Layout Shift
    fcp                 REAL,    -- First Contentful Paint (sec)
    ttfb                REAL,    -- Time to First Byte (sec)
    tbt                 REAL,    -- Total Blocking Time (ms)
    speed_index         REAL,
    total_loading_time  REAL,
    needs_alert         BOOLEAN DEFAULT FALSE,
    opportunities       JSONB,
    diagnostics         JSONB,
    ai_summary          TEXT,
    ai_root_causes      JSONB,
    ai_code_fixes       JSONB,
    ai_priority         TEXT,
    audit_timestamp     TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast history lookups
CREATE INDEX IF NOT EXISTS idx_audit_url_time
    ON speed_audit_logs (url, audit_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_audit_needs_alert
    ON speed_audit_logs (needs_alert)
    WHERE needs_alert = TRUE;

-- Enable Row Level Security (RLS)
ALTER TABLE speed_audit_logs ENABLE ROW LEVEL SECURITY;

-- Allow the service role (used by our script) full access
CREATE POLICY "service_role_all" ON speed_audit_logs
    FOR ALL USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Allow anonymous read for the public dashboard (optional)
CREATE POLICY "anon_read_only" ON speed_audit_logs
    FOR SELECT USING (true);

-- Helpful view: latest audit per URL
CREATE OR REPLACE VIEW v_latest_audit_per_url AS
SELECT DISTINCT ON (url) *
FROM speed_audit_logs
ORDER BY url, audit_timestamp DESC;

COMMENT ON TABLE speed_audit_logs IS
    'Speed-ZeroBaran — historical performance audit logs. '
    'Author: Baran Avisat <Baranavisat@gmail.com>';
