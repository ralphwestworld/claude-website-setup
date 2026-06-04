# External Skills Manifest — vetted candidates to adopt

Skills sourced from public marketplaces (`VoltAgent/awesome-agent-skills`, `travisvn/awesome-claude-skills`) that are relevant to a **Cloudflare + TypeScript** job-search & auto-apply app. Rated by **provenance/trust** — a malware scan is not sufficient assurance for executable third-party code, so we adopt by trust tier and pin versions when we vendor them into the repo.

> Note: only ~8 skills are actually installed today (our 6 + `session-start-hook` + built-ins). These below are **candidates**, not yet installed. We vendor the Tier-1 set into `.claude/skills/` at scaffold time after a source review.

## Tier 1 — official vendor skills (high trust → adopt)
| Skill | Source | Maps to |
|---|---|---|
| `cloudflare/cloudflare` | Cloudflare | Whole-platform guidance |
| `cloudflare/wrangler` | Cloudflare | Deploy/manage Workers, KV, R2, D1, Vectorize, Queues, Workflows |
| `cloudflare/workers-best-practices` | Cloudflare | Production-quality Workers code |
| `cloudflare/agents-sdk` | Cloudflare | Stateful agents + scheduling → scan engine, apply orchestration |
| `playwright` | OpenAI | Browser automation (Path B forms/scraping) + UI tests |
| `pdf` | Anthropic | Resume/PDF text + table extraction (Stage 1) |
| `webapp-testing` | Anthropic | Playwright UI verification (with `verify`/`run`) |
| Trail of Bits security (`insecure-defaults`, CodeQL/Semgrep) | Trail of Bits | PII + credentials + auto-submit security review |
| `stripe` | Stripe | Subscription billing (fast-follow) |
| `shadcn/ui` | shadcn | Upload UI + review dashboard components |

## Tier 2 — community (useful → review before adopting)
| Skill | Source | Maps to |
|---|---|---|
| `firecrawl/firecrawl-build-scrape` | Firecrawl | Career-page crawl (Path B discovery long tail) |
| `browserbase/browser`, `browserbase/fetch` | Browserbase | Alt browser path (CF supports Stagehand/Browserbase) |
| `playwright-skill` | lackeyjb (community) | General browser automation |
| `mcp-builder` | Anthropic | If we expose our own integrations later |
| `web-artifacts-builder` | Anthropic | Quick React/Tailwind artifacts |

## Excluded as irrelevant
Azure-specific TS skills, iOS simulator, scientific-data skills, fuzzing/pentest skills (not our use case).

## Adoption rule
1. Pick from Tier 1 first.
2. Before vendoring any skill: read its `SKILL.md` + any scripts, confirm source repo/author, pin a commit/version, then copy into `.claude/skills/`.
3. Never blanket-install. Never run a skill that ships obfuscated or binary payloads.
</content>
