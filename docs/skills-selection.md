# Skills Selection — what we use to build this

Audit of every skill available in this session, with the relevant ones selected for the job-search & auto-apply project. "Ready" = loaded in-session and committed to the repo.

## Project skills (authored, in `.claude/skills/`) — all in use
| Skill | Pipeline stage |
|---|---|
| `competitor-teardown` | Reverse-engineer competitors, build comparison bases |
| `ats-research` | Identify ATS + map public read/apply APIs (build adapters) |
| `job-discovery` | Scan + normalize jobs from ATS APIs / Indeed / crawl |
| `resume-intelligence` | Resume → profile JSON; semantic + LLM matching/scoring |
| `application-tailoring` | Tailored resume + cover letter + screening answers |
| `apply-runner` | Submit via ATS API (Path A) / browser (Path B) + handoff |

## Built-in harness skills — SELECTED
| Skill | Use in this project | Tier |
|---|---|---|
| `claude-api` | LLM layer (scoring, tailoring, cover letters) with prompt caching | Core |
| `deep-research` | Competitor / ATS / market research with citations | Core |
| `session-start-hook` | Ensure tests/lint/build run in web sessions (after scaffold) | Core / foundation |
| `init` | Generate project `CLAUDE.md` from architecture + decisions | Core / foundation |
| `verify` | Run the app, confirm a change works | Dev loop |
| `run` | Launch/screenshot the Worker to see features live | Dev loop |
| `code-review` | Review diffs for bugs pre-merge | Quality |
| `security-review` | PII (resumes) + credentials + auto-submit → security pass | Quality (important) |
| `simplify` | Cleanup pass on changed code | Optional |
| `review` | Review a PR when opened | Situational |

## Excluded (not relevant)
`keybindings-help`, `update-config`, `fewer-permission-prompts`, `loop` — editor/harness conveniences, no product bearing.

## Readiness checklist
- [x] Project skills authored + committed + loaded in-session
- [x] Relevant harness skills identified
- [ ] `init` → create project `CLAUDE.md` (do at scaffold time)
- [ ] `session-start-hook` → wire tests/lint/build for web sessions (do at scaffold time)
- [ ] Decide MVP feature scope (`docs/competitor-matrix.md`) — next discussion
</content>
