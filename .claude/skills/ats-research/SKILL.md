---
name: ats-research
description: Identify which Applicant Tracking System (ATS) a company career page uses and map its public job-board API and application-form structure. Use when adding support for a new job source, building an ATS adapter, or determining whether a company is reachable via official API (Path A) or needs the browser agent (Path B).
---

# ATS Research

Given a company name or career-page URL, determine the ATS and how to read jobs + submit applications through official channels.

## Detection cheat-sheet
Look at the careers URL / page source for these fingerprints:
- **Greenhouse**: `boards.greenhouse.io/<token>` or `job-boards.greenhouse.io`; embed script `boards-api.greenhouse.io`.
- **Lever**: `jobs.lever.co/<company>`.
- **Ashby**: `jobs.ashbyhq.com/<org>`.
- **Workday**: `myworkdayjobs.com` (no public read API — Path B browser agent).
- **Greenhouse/Lever/Ashby = Path A (API).** Workday/Taleo/iCIMS/SmartRecruiters/Avature = mostly Path B.

## Public read APIs (no auth)
- **Greenhouse**: `GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true` and `.../jobs/{id}?questions=true` (questions = the application form schema).
- **Lever**: `GET https://api.lever.co/v0/postings/{company}?mode=json` (filters: team, location, commitment, level).
- **Ashby**: `GET https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true`.
- **Workable**: `GET https://apply.workable.com/api/v1/widget/accounts/{account}?details=true` (varies).

## Application submission (Path A)
- **Greenhouse**: multipart `POST https://boards-api.greenhouse.io/v1/boards/{token}/jobs/{id}` with Basic Auth (API key as username). NOTE: server does NOT validate required fields — validate client-side. Build the form from the job's `questions` array.
- **Lever**: candidate-create endpoint accepts JSON or multipart; **rate-limited — handle HTTP 429** with backoff.
- Always: dedupe by job id, store the raw `questions` schema, keep an audit record of what was submitted.

## Workflow
1. Resolve the career URL → fingerprint the ATS.
2. If Path A: derive the board token/org, hit the read API, normalize into our `Job` schema, capture the `questions` form schema.
3. If Path B: hand off to the `apply-runner` browser path (with human handoff for login/CAPTCHA).
4. Emit an adapter stub conforming to the project's `ATSAdapter` interface.

## Guardrails
- Use only documented public endpoints. Respect rate limits and robots where applicable.
- No login bypass. Path B logins/verifications go through human handoff, never automated CAPTCHA solving.
</content>
