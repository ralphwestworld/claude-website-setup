# Cloudflare Architecture — Can Cloudflare run this entirely?

**Short answer: yes, end-to-end — but it forces a stack decision.** Cloudflare Workers run **JavaScript/TypeScript natively**. Python on Workers is beta and Pyodide-limited — our ML/scraping libs (sentence-transformers, spaCy, pyresparser, JobSpy, Playwright) **do not run on Python Workers**. So "Cloudflare runs it entirely" means one of two stacks:

## Option A — Cloudflare-native TypeScript (most native, recommended)
Replace FastAPI with **Hono** (Workers-native web framework). Everything maps to a first-party Cloudflare primitive:

| Pipeline stage | Cloudflare primitive |
|---|---|
| API / web app | **Workers + Hono** (+ Pages/Assets for the upload UI) |
| Scan scheduler (every 4h) | **Cron Triggers → Workflows** (durable, multi-step, retries) |
| Job queue / fan-out | **Queues** |
| Discovery (ATS API calls) | Worker `fetch()` to Greenhouse/Lever/Ashby — native |
| Resume/file storage | **R2** (resumes, generated PDFs, screenshots) |
| Relational data | **D1** (jobs, applications, profiles, audit log) |
| Key/value + sessions | **KV** |
| Embeddings | **Workers AI** (`@cf/baai/bge-*`) — native, no external model host |
| Vector search / matching | **Vectorize** |
| LLM tailoring / scoring | **Workers AI** (Llama etc.) or call **Claude API** via `fetch()` |
| Browser agent (Path B) | **Browser Rendering** — Playwright **GA** (synced to v1.55), **Stagehand** supported (beta), 120 concurrent browsers (paid) |
| Long-running apply runs | **Workflows** (survives restarts) + Browser Rendering |

**Pros:** fully serverless, scales to zero, one bill, lowest ops. Browser Rendering is purpose-built for exactly the Path B agent. **Cons:** rewrite the planned Python in TS; some Python-only libs (pyresparser) replaced by LLM extraction (which we preferred anyway).

## Option B — Workers + Cloudflare Containers (keep Python)
Keep **FastAPI + the Python ML/scraping stack** in **Cloudflare Containers** (run alongside Workers, on Cloudflare). Workers handle edge/API/orchestration; Containers run Python jobs (JobSpy, sentence-transformers, Playwright).

**Pros:** keep the Python ecosystem and the earlier plan; reuse JobSpy/pyresparser as-is. **Cons:** Containers are heavier/pricier than Workers, don't scale to zero the same way, more moving parts. Still "entirely on Cloudflare."

## What this means for the earlier decision
You earlier picked **Python + FastAPI**. Cloudflare-native (Option A) means **TypeScript + Hono** instead. Option B preserves Python but adds Containers. Both run entirely on Cloudflare. **This is the one architectural fork to settle before we scaffold.**

## Reference flow (Option A)
```
Pages (upload UI) ─► Worker/Hono API ─► D1 + R2
        ▲                                  │
        │            Cron Trigger ─► Workflow ─► Queue
   Review UI                          │           │
   (approve)                     Discovery     per-job:
                                 (fetch ATS)   Workers AI embed ─► Vectorize match
                                                ─► Workers AI/Claude tailor
                                                ─► [human gate]
                                                ─► Path A: fetch() ATS POST
                                                   Path B: Browser Rendering + handoff
```
Login / email-verification / CAPTCHA in Path B → **pause Workflow, notify user, resume on completion** (no evasion).

## Sources
- [Cloudflare Workers](https://www.cloudflare.com/products/workers/) · [Browser Rendering](https://www.cloudflare.com/products/browser-rendering/) · [Playwright on Browser Rendering](https://developers.cloudflare.com/browser-rendering/platform/playwright/)
- [Playwright GA + Stagehand + higher limits (2025-09)](https://developers.cloudflare.com/changelog/post/2025-09-25-br-playwright-ga-stagehand-limits/)
</content>
