---
name: job-discovery
description: Discover and normalize job postings from ATS public APIs (Greenhouse/Lever/Ashby), the Indeed MCP, and career-page crawling into a single canonical Job schema. Use when building the scan/discovery stage, aggregating jobs from multiple sources, or scheduling periodic scans.
---

# Job Discovery

The "scan every N hours" engine. Pull jobs from many sources → dedupe → normalize → store.

## Sources (priority order = cleanest first)
1. **ATS public APIs** (via `ats-research`) — Greenhouse, Lever, Ashby. ToS-clean, structured, includes the application form schema. Primary source.
2. **Indeed MCP** (connected) — `search_jobs`, `get_job_details`, `get_company_data`. Sanctioned Indeed access.
3. **JobSpy** (`pip install python-jobspy`) — multi-board (LinkedIn/Indeed/Glassdoor/Google/ZipRecruiter) → DataFrame. Use cautiously: LinkedIn rate-limits/bans; prefer for research, not high-volume production.
4. **Career-page crawl** — Crawl4AI / ScrapeGraphAI / Firecrawl for companies with no API. LLM-extract into the Job schema.
5. **RSS/sitemaps** — feedparser on career feeds; cheapest signal.

## Canonical Job schema (normalize everything to this)
```
{ id, source, ats, company, title, location, remote, department,
  description, url, apply_url, comp_min, comp_max, posted_at,
  questions[]  // application form schema if known (Path A)
}
```

## Workflow
1. For each configured company/source, fetch new postings.
2. Dedupe by (source, external_id) and fuzzy (company+title+location) via rapidfuzz.
3. Normalize → upsert into the `jobs` table; mark `is_new`.
4. Hand new jobs to `resume-intelligence` for scoring.

## Scheduling
- Local/server: APScheduler or Arq+Redis on a cron (e.g. every 4h, matching JobCopilot's cadence).
- **On Cloudflare: use Cron Triggers → Workflows/Queues** (see `docs/cloudflare-architecture.md`). Discovery via `fetch()` to ATS APIs runs natively on Workers; JobSpy/Playwright do NOT run on Workers — offload to Browser Rendering or an external worker.

## Guardrails
- Respect rate limits (429 backoff), robots.txt for crawling, and ToS. Prefer official APIs over scraping.
</content>
