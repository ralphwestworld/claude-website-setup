# Project Handoff — AI Job Search & Auto-Apply

Paste this into a new (local) Claude Code session to continue seamlessly. Everything below is already committed to the repo on branch `claude/magical-feynman-zROus`.

---

## Your role & first step
You are continuing development of an **AI job-search & auto-apply web app**. Before doing anything, **read these committed docs in `docs/` and the skills in `.claude/skills/`** — they are the source of truth:
- `docs/job-app-research.md` — how competitors work + 45-tool toolkit
- `docs/competitor-matrix.md` — 10 tools × ~20 features (our comparison base + feature backlog)
- `docs/cloudflare-architecture.md` — how Cloudflare runs everything, stage-by-stage
- `docs/decisions.md` — **locked architecture decisions** (read first)
- `docs/skills-selection.md` — which skills are relevant
- `docs/external-skills.md` — vetted external skills to vendor

## What we're building
A browser-based product (like JobCopilot / Simplify / LazyApply) that: ingests the user's resume → discovers jobs → matches/scores them → tailors resume + cover letter + screening answers → applies on the user's behalf → tracks everything. Hosted entirely on Cloudflare.

## Locked decisions (do not relitigate without flagging)
| # | Decision | Choice |
|---|----------|--------|
| 1 | Hosting | Cloudflare, end-to-end |
| 2 | Stack | **TypeScript-native** — Hono on Workers (NOT Python/FastAPI) |
| 3 | Job sources | ATS public APIs (Greenhouse/Lever/Ashby) first; Indeed; career-page crawl for the long tail |
| 4 | Apply default | **Auto-submit Path A (official ATS API) high-confidence matches; review-mode for everything else** |
| 5 | Compliance | **No CAPTCHA / human-verification bypass, no bot-detection evasion.** Login/verification = human handoff on the user's own accounts |
| 6 | Truthfulness | Tailoring = emphasis from real profile data; never fabricate qualifications |

## Cloudflare stack (Option A, locked)
Hono on Workers · Pages/Assets (UI) · Cron Triggers → Workflows (scan engine) · Queues · D1 (data) · KV (sessions) · R2 (files/PDFs/screenshots) · Workers AI (embeddings + LLM) · Vectorize (matching) · Browser Rendering (Playwright GA + Stagehand, for Path B) · optionally Claude API via fetch().

## Pipeline (6 stages) and the skills that own them
`Profile → Discover → Match/Rank → Tailor → Apply → Track`
In-repo project skills (`.claude/skills/`): `resume-intelligence` (profile + match), `job-discovery` (discover), `application-tailoring` (tailor), `apply-runner` (apply, w/ handoff), `ats-research` (add sources), `competitor-teardown` (research).

## Skills note (important — this is why we moved local)
- **Project skills** live in the repo (`.claude/skills/`) and load in every session everywhere.
- **The ~100 skills installed on the LOCAL machine's `~/.claude/skills/`** are personal to that machine — they were NOT visible in the cloud session. Now that we're local, they're available.
- **To make any local global skill persist for cloud too:** copy it into `<repo>/.claude/skills/`, commit, push.
- Vetted external skills relevant here (from `docs/external-skills.md`): Cloudflare (`cloudflare`, `wrangler`, `workers-best-practices`, `agents-sdk`), `playwright` (OpenAI), `pdf` (Anthropic), `webapp-testing` (Anthropic), Trail of Bits security, `stripe`, `shadcn/ui`; Tier-2: Firecrawl, Browserbase.

## Current status
- ✅ Foundation complete: research, competitor base, architecture, decisions, 6 project skills.
- ⏳ NOT started: any application code; `init` (CLAUDE.md); `session-start-hook` wiring.

## Next step (where to resume)
**Decide the MVP feature scope**, then scaffold. Recommended v1 (all Path A, clean + auto-submittable):
1. Resume upload → structured profile
2. Discovery from Greenhouse/Lever/Ashby for target companies
3. Match + score (embeddings + LLM rubric, with reasons)
4. Tailor (resume + cover letter + screening answers)
5. Review dashboard + auto-submit toggle for high-confidence
6. ATS-native submit + tracker with audit log

Fast-follow: browser-agent Path B (Workday/Taleo), scam filtering, email follow-up, interview prep, browser extension, recruiter contacts, multi-profile, Stripe billing.

After scope is set: run `init` (CLAUDE.md), wire `session-start-hook`, then scaffold the Hono Worker.
</content>
