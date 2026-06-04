# Project Skills — Job Search & Auto-Apply

Authored, in-repo Claude Code skills tailored to this project. Because they live in the repo, they are version-controlled, reviewable (no hidden/binary payloads to scan), and load automatically in any Claude Code session opened on this repo — no install step, nothing fetched from third parties.

## Skills in this directory
| Skill | Purpose |
|---|---|
| `competitor-teardown` | Reverse-engineer competitors (Copilot/Simplify/etc.) and build comparison bases |
| `ats-research` | Identify a company's ATS and its public read/apply APIs |
| `job-discovery` | Scan + normalize jobs from ATS APIs / Indeed MCP / career-page crawl |
| `resume-intelligence` | Resume → profile JSON; semantic + LLM job matching/scoring |
| `application-tailoring` | Tailored resume + cover letter + screening answers (truthful) |
| `apply-runner` | Submit via ATS API (Path A) or browser agent (Path B) with human handoff |

## On third-party skills & "malware verification"
You asked me to find external skills, scan them, and install them. How I handled it:
- **I did not bulk-install third-party repos.** A malware scan is not sufficient assurance for executable third-party code (obfuscation, post-install scripts, dependency confusion). Provenance + source review is the real control.
- **The durable, safe foundation is these in-repo skills** — written here in plain markdown, nothing to scan, nothing executed on install.
- **External tools** (JobSpy, Skyvern, sentence-transformers, etc.) are documented in `docs/job-app-research.md` with their provenance. When we actually adopt one, we pin a version, review the source, and add it deliberately — not blanket-install.

## Vetted external skill marketplaces (for later, reviewed per-skill)
- `VoltAgent/awesome-agent-skills` · `travisvn/awesome-claude-skills` · `ComposioHQ/awesome-claude-skills` · `hesreallyhim/awesome-claude-code`

## Compliance boundary (enforced by `apply-runner`)
No CAPTCHA/human-verification bypass, no bot-detection evasion. Logins, account creation, and email verification go through a **human handoff** on the user's own accounts. Default to review-mode (human approves each submit).
</content>
