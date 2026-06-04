# AI Job Search & Auto-Apply App — Research & Toolkit

Research brief before we build. Two parts:
1. **How the commercial AI auto-apply tools actually work** (JobCopilot, Simplify, LazyApply, Sonara, Massive, AIHawk).
2. **A 45-item toolkit** of reusable "skills" — open-source tools, APIs, and Claude Code skills — mapped to each stage of the pipeline so we assemble rather than reinvent.

Target stack (decided): **Python + FastAPI**, sourcing primarily from **ATS boards (Greenhouse, Lever, Ashby) and company career pages**.

---

## Part 1 — How the platforms work

All of these tools, despite different marketing, run the **same 6-stage pipeline**. Understanding it tells us exactly what to build.

```
[1 Profile]  → [2 Discover]  → [3 Match/Rank]  → [4 Tailor]  → [5 Apply]  → [6 Track/Review]
 resume→JSON    scan boards     score vs resume   resume+CL     fill+submit   dashboard+notify
                every N hours    + filters         per job       on your behalf  human-in-loop
```

### The players and their approach

| Tool | Discovery | Apply mechanism | Volume | Human-in-loop |
|------|-----------|-----------------|--------|---------------|
| **JobCopilot** | Scans 500k+ career pages & ATS listings **every 4 hours** | Fills forms on **official company career pages** like a human, submits | up to ~1,500/mo | "Review mode" (recommended) vs full auto |
| **Simplify Copilot** | Browser extension on LinkedIn/Indeed + 100+ portals | **Autofill** — maps your profile fields onto Workday, Greenhouse, iCIMS, Taleo, Lever, SmartRecruiters; you click submit | unlimited | Always (you submit) |
| **LazyApply** | Chrome extension, LinkedIn/Indeed/ZipRecruiter | "Job GPT" fills forms, answers screening Qs; **per-application user click** | up to 150/day | Per-app click |
| **Sonara** | Daily scan of partner DB + scraped listings | Rewrites resume per JD, submits on your behalf | 84–420/mo by tier | Light |
| **Massive** | Scans boards | Fills, then **humans review every application** | ~50/week | Human reviewers |
| **AIHawk** (OSS) | LinkedIn search by criteria | Selenium drives LinkedIn **Easy Apply**, LLM generates cover letters + answers screening Qs, generates tailored resume per job | high | none (educational) |

### Key lessons from reviews (what to copy / avoid)
- **Review mode wins.** Across JobCopilot/LazyApply reviews, users who used review mode + edited AI answers got interviews; full unsupervised auto-apply on broad filters produced the worst outcomes (spam, scam-job exposure). → **Build human-in-loop as the default, not an afterthought.**
- **Two apply strategies exist:**
  - **(a) ATS-native API submission** — for Greenhouse/Lever/Ashby, post directly to their documented application endpoints. Reliable, no browser. *(Greenhouse explicitly supports a multipart application POST; Lever supports a candidate-create endpoint, rate-limited.)*
  - **(b) Vision/LLM browser autofill** — for Workday/Taleo/iCIMS and arbitrary career pages with no API. This is where Simplify (field-mapping) and Skyvern (vision) play. **The 80/20: most startup jobs are Greenhouse/Lever/Ashby → API path covers a huge fraction cheaply; reserve the expensive browser-agent path for the rest.**
- **The moat is the field-mapping/answer engine**, not the scraper. Mapping "First Name / Given Name / Forename" → one value, and answering free-text screening questions from a profile, is the hard reusable part.

### Compliance reality (must design around this)
- **LinkedIn & Indeed ToS prohibit automation/scraping**; AIHawk-style bots risk account bans and are "educational only." Indeed's own API/MCP is the sanctioned path there.
- **ATS public job-board APIs (Greenhouse/Lever/Ashby) are explicitly public and safe to read.** Application-submit endpoints are intended for custom careers pages but are usable — mind rate limits (handle HTTP 429).
- **CAPTCHA / bot-detection**: official APIs avoid it; browser autofill will hit it. Plan for human handoff rather than CAPTCHA-solving services (ToS + ethics).
- Default posture: **human approves every submit**, store an audit trail, rate-limit per domain.

---

## Part 2 — The Toolkit (45 building blocks)

Organized by pipeline stage. ✅ = already connected/loaded in this session.

### Stage 1 — Profile (resume → structured data)
1. **pyresparser** — resume (PDF/DOCX) → JSON (name, skills, experience). spaCy+NLTK under the hood. `pip install pyresparser`.
2. **PyMuPDF / pdfplumber** — robust PDF text+layout extraction.
3. **unstructured** (`unstructured.io`) — parse PDF/DOCX/HTML into clean elements for LLM ingestion.
4. **spaCy + NLTK** — NER for entities the regex/LLM passes miss.
5. **JSON Resume schema** (`jsonresume.org`) — canonical profile format; many renderers/importers exist.
6. **Claude API structured extraction** ✅ — LLM pass to normalize messy resumes into our schema (more reliable than pyresparser alone). Use the loaded **claude-api** skill.

### Stage 2 — Discovery (find jobs)
7. **JobSpy** (`speedyapply/JobSpy`) — scrapes LinkedIn/Indeed/Glassdoor/Google/ZipRecruiter → pandas DataFrame. MIT, ~3.4k★. Best general-purpose scraper.
8. **Greenhouse Job Board API** — `GET boards-api.greenhouse.io/v1/boards/{token}/jobs` (+ `/jobs/{id}?questions=true`). Public, no auth.
9. **Lever Postings API** — `GET api.lever.co/v0/postings/{company}?mode=json`. Public, no auth, supports team/location filters.
10. **Ashby Public Posting API** — `GET api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true`. Public.
11. **Workable / SmartRecruiters / Recruitee public endpoints** — similar JSON board APIs to add as adapters.
12. **JobFunnel** — OSS job aggregator/dedupe across boards to CSV.
13. **Indeed MCP** ✅ — `search_jobs`, `get_job_details`, `get_company_data`, `get_resume`. Sanctioned Indeed access in this session.
14. **Firecrawl** — LLM-ready scraping/crawling of arbitrary company career pages (no API).
15. **Crawl4AI** — OSS async crawler tuned for LLM extraction; good free alternative to Firecrawl.
16. **ScrapeGraphAI** — define extraction as a graph + LLM; turns unknown career pages into structured jobs.
17. **feedparser + sitemaps/RSS** — many career pages expose feeds; cheapest discovery path.

### Stage 3 — Anti-bot / fetching infrastructure
18. **Playwright (Python)** — headless browser for JS-heavy boards and the autofill path.
19. **playwright-stealth / undetected-chromedriver** — reduce bot detection (use cautiously, respect ToS).
20. **Residential proxy rotation** — needed only if scaling LinkedIn/Indeed scraping (they rate-limit hard). Budget item, not day-1.

### Stage 4 — Match & rank (resume ↔ JD)
21. **Resume-Matcher** (`srbhr/Resume-Matcher`) — semantic JD↔resume scoring + keyword gap analysis. Good reference impl.
22. **sentence-transformers (SBERT)** — embeddings for semantic similarity; beats keyword matching by ~30%.
23. **pgvector / Chroma / FAISS** — vector store; pgvector keeps it in the same Postgres as the app.
24. **rapidfuzz** — fast fuzzy string matching for titles/skills/locations.
25. **scikit-learn TF-IDF** — cheap keyword baseline + explainability for the match score.
26. **Claude API scoring pass** ✅ — final LLM re-rank with a rubric (seniority, must-haves, salary, location) → the "should I apply?" gate. This is what Sonara/ApplyIQ added in 2025.

### Stage 5 — Tailor (per-job resume + cover letter + answers)
27. **Claude API + prompt caching** ✅ — generate cover letters, tailor resume bullets, answer screening questions. Cache the resume/profile as a stable prefix for cost. (claude-api skill enforces caching.)
28. **Instructor + Pydantic** — force structured, schema-valid LLM outputs (answers keyed to form fields).
29. **RenderCV** — YAML/JSON → polished PDF resume (LaTeX-quality) per job.
30. **Jinja2 + WeasyPrint** — HTML resume/cover-letter templates → PDF, full styling control.
31. **JSON Resume themes** — swap themes to regenerate tailored PDFs from the canonical profile.

### Stage 6 — Apply (the hard part — two paths)
**Path A: ATS-native submission (preferred, cheap, reliable)**
32. **ATS adapter pattern** — per-ATS module that POSTs to the documented application endpoint (Greenhouse multipart application POST; Lever candidate-create). Handle 429s, required-field validation client-side.
33. **httpx (async)** — submit applications + multipart resume upload to ATS endpoints.

**Path B: Browser autofill (for Workday/Taleo/iCIMS/unknown pages)**
34. **Skyvern** (`Skyvern-AI/skyvern`, ~21k★, YC) — vision+LLM form filling, **native Workday integration**, adapts to unseen forms. Best for the "weird ATS" long tail.
35. **browser-use** — Python LLM browser agent; largest community; good default if we want one framework in-process.
36. **Stagehand** (`browserbase/stagehand`) — TS agent with `act/extract/observe` + self-healing caching; near-zero cost on repeated known forms. Run as a sidecar if we stay Python.
37. **Playwright codegen + recorded flows** — for high-volume known ATS, record a deterministic script once (no per-submit LLM cost); fall back to agent only when it breaks.
38. **Field-mapping engine (build our own, à la Simplify)** — synonym dictionary mapping {profile field → many possible labels}; the reusable core asset.

### Stage 7 — Orchestration / backend (FastAPI app)
39. **FastAPI + Uvicorn** — the API and review-mode endpoints.
40. **APScheduler / Arq / Celery + Redis** — the "scan every 4 hours" engine (JobCopilot's cadence).
41. **SQLModel/SQLAlchemy + Postgres (+ pgvector)** — jobs, applications, profiles, audit log, embeddings in one DB.
42. **Pydantic Settings + Docker** — config + sandboxed Playwright apply-workers.

### Stage 8 — Track, review & notify (human-in-loop)
43. **Streamlit** (or Next.js) — review-mode dashboard: approve/edit answers before submit.
44. **Gmail MCP** ✅ — watch for application confirmations/recruiter replies, draft outreach.
45. **Google Calendar MCP** ✅ + **Notion MCP** ✅ — auto-schedule interviews; Notion/DB as the application tracker.

---

## Claude Code skills to use & author

**Already available this session:** `claude-api` (LLM layer w/ caching), `deep-research`, `session-start-hook` (repo CI setup), `verify`/`run` (test the app), `code-review`.

**Curated marketplaces to pull more from:**
- `VoltAgent/awesome-agent-skills` (1000+ skills, incl. official Anthropic/Stripe/Netlify)
- `travisvn/awesome-claude-skills`, `ComposioHQ/awesome-claude-skills`, `hesreallyhim/awesome-claude-code`

**Custom skills worth authoring for this project** (each becomes a reusable `.claude/skills/*`):
- `ats-adapter` — scaffold a new board adapter (discover + submit) from an ATS name.
- `resume-tailor` — profile + JD → tailored resume PDF + cover letter.
- `job-matcher` — embed + rubric-score a job against the profile.
- `apply-runner` — drive Path A/B apply with audit logging + human-approval gate.
- `career-page-scraper` — point at a company URL, emit structured jobs (Crawl4AI/ScrapeGraphAI).

---

## Recommended architecture (the 80/20)

```
                 ┌─────────────── FastAPI ───────────────┐
 Scheduler ─►    │  /scan  /match  /tailor  /review  /apply │  ◄─ Streamlit review UI (human approves)
 (every 4h)      └────────────────────────────────────────┘
        │              │            │           │
   Discovery       Matching      Tailoring     Apply
   ├ ATS APIs   ─► SBERT +    ─► Claude API ─► Path A: ATS POST (httpx)   ← covers most Greenhouse/Lever/Ashby
   ├ JobSpy        pgvector      (cached)      Path B: Skyvern/browser-use ← Workday/Taleo/unknown
   └ Crawl4AI      + Claude                    + field-mapping engine
                   re-rank
                          Postgres (jobs, profile, applications, embeddings, audit log)
```

**Why this wins:** Path A (ATS APIs) is free, reliable, and ToS-clean and likely covers the majority of relevant startup/tech jobs. The expensive vision-browser path is reserved for the long tail. Human-in-loop is default. We reuse JobSpy + Skyvern + sentence-transformers + Claude API instead of building any of them from scratch.

## Top risks to decide on before building
1. **Compliance** — confirm we stay on official APIs + Indeed MCP and avoid LinkedIn/Indeed scraping bots (ban + ToS risk).
2. **Auto-submit vs review-only** — strongly recommend review-only default given the review-mode evidence.
3. **Browser-agent cost** — Skyvern/LLM-per-form is the main running cost; cap it to the no-API long tail.

---

## Sources
- [JobCopilot](https://jobcopilot.com/) · [Workshift review](https://workshiftguide.com/jobcopilot-review-2026/) · [Jobsolv review](https://jobsolv.com/blog/jobcopilot-review-2025-legit-ai-tool-or-red-flag)
- [Simplify Copilot](https://simplify.jobs/copilot) · [Chrome listing](https://chromewebstore.google.com/detail/simplify-copilot-autofill/pbanhockgagggenencehbnadejlgchfc)
- [LazyApply](https://lazyapply.com/) · [Sonara](https://www.sonara.ai/) · [AI job bots 2026](https://blog.fastapply.co/ai-job-application-bots-which-actually-submit-2026)
- [AIHawk (Jobs_Applier_AI_Agent)](https://github.com/feder-cr/Jobs_Applier_AI_Agent_AIHawk)
- [JobSpy](https://github.com/speedyapply/JobSpy) · [python-jobspy](https://pypi.org/project/python-jobspy/)
- [Skyvern](https://github.com/Skyvern-AI/skyvern) · [Skyvern: reads the web](https://www.skyvern.com/blog/how-skyvern-reads-and-understands-the-web/) · [Stagehand](https://github.com/browserbase/stagehand) · [browser-use framework wars](https://dev.to/stevengonsalvez/browser-tools-for-ai-agents-part-2-the-framework-wars-browser-use-stagehand-skyvern-4gn)
- [pyresparser](https://github.com/OmkarPathak/pyresparser) · [Resume-Matcher](https://dev.to/srbhr/creating-a-game-changer-in-job-search-an-open-source-ats-resume-matcher-31g9)
- [Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html) · [Lever Postings API](https://github.com/lever/postings-api) · [Ashby Posting API](https://developers.ashbyhq.com/docs/public-job-posting-api)
- [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) · [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
</content>
</invoke>
