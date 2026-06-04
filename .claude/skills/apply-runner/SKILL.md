---
name: apply-runner
description: Submit a job application via official ATS API (Path A) or a browser agent (Path B), with a human-in-the-loop handoff for any login, email verification, or CAPTCHA. Use when building the apply/submit stage. This skill enforces the project's compliance boundary.
---

# Apply Runner

Execute an application after the human-in-loop gate approves. Two paths; always auditable.

## Path A — ATS-native API (preferred)
- Greenhouse: multipart POST to `boards-api.greenhouse.io/v1/boards/{token}/jobs/{id}` (Basic Auth w/ API key). Validate required fields client-side first (server won't).
- Lever: candidate-create endpoint; **handle 429** with exponential backoff.
- Upload resume/cover letter as multipart; record the exact payload in the audit log.
- No browser, no login, no CAPTCHA. Covers most Greenhouse/Lever/Ashby jobs.

## Path B — Browser agent (long tail: Workday/Taleo/iCIMS/unknown)
- Drive with Playwright + an LLM agent (browser-use in-process, or Skyvern for vision on weird forms; on Cloudflare use **Browser Rendering** / Browserbase).
- Use the field-mapping engine from `application-tailoring` to fill fields.
- **STOP-and-handoff triggers (mandatory):** any login wall, account creation, email verification step, or CAPTCHA / "human verification" challenge → **pause the run, notify the user, and let the USER complete that step** (e.g. via the review UI or a forwarded link), then resume. The agent fills forms; the human clears human-verification.

## Compliance boundary (do not cross)
- **No automated CAPTCHA solving, no bot-detection evasion, no stealth fingerprint spoofing to defeat anti-bot systems.** These are out of scope by project policy and ToS.
- Account creation / email verification happen on the USER's own accounts, with the user completing verification — never silently/automatedly bypassed.
- Default to **review-mode**: human approves each submission. Full-auto only for Path A on high-confidence matches if the user explicitly opts in.

## Audit (every attempt)
Log `{job_id, path, fields_submitted (redacted), files, result, screenshots, timestamp}` for transparency and dispute resolution.

## Guardrails
- Rate-limit per domain. Respect ToS. If a site clearly prohibits automation, prefer Path A or skip.
</content>
