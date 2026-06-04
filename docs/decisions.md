# Architecture Decisions (locked)

Binding choices for the job-search & auto-apply product. Update via PR if revisited.

| # | Decision | Choice | Date |
|---|----------|--------|------|
| 1 | Hosting | **Cloudflare, end-to-end** | 2026-06-04 |
| 2 | Stack | **TypeScript-native** — Hono on Workers (not Python/FastAPI) | 2026-06-04 |
| 3 | Job sources | ATS public APIs (Greenhouse/Lever/Ashby) first; Indeed MCP; career-page crawl for the long tail | 2026-06-04 |
| 4 | Apply default | **Auto-submit Path A (ATS API) high-confidence matches; review-mode for everything else** | 2026-06-04 |
| 5 | Compliance | No CAPTCHA/verification bypass or bot-detection evasion. Human handoff for login/verification on the user's own accounts | 2026-06-04 |
| 6 | Truthfulness | Tailoring = emphasis from real profile data; never fabricate qualifications | 2026-06-04 |

## Locked Cloudflare stack (Option A)
- **Web/API:** Hono on Workers · **UI:** Pages/Assets (resume upload + review dashboard)
- **Scheduler:** Cron Triggers → **Workflows** (durable) · **Queue:** Queues
- **Data:** D1 (relational) · KV (sessions/cache) · R2 (resumes, PDFs, screenshots)
- **AI:** Workers AI (`bge` embeddings + LLM) and/or Claude API via `fetch()` · **Vector:** Vectorize
- **Browser (Path B):** Browser Rendering (Playwright GA, Stagehand) with human handoff

See `docs/cloudflare-architecture.md` for the stage-by-stage mapping and `docs/competitor-matrix.md` for the feature base.

## Open (to discuss next)
- MVP feature scope (pick from the backlog in `docs/competitor-matrix.md`)
- Auto-submit confidence threshold + per-profile controls
- Whether to ship a browser extension (Path B) in addition to the web app
</content>
