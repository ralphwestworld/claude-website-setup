---
name: competitor-teardown
description: Reverse-engineer and structurally break down a competitor job-application product (JobCopilot, Simplify, LazyApply, Sonara, AIHawk, Jobright, etc.). Use when researching how a competitor works, fingerprinting their tech stack, reconstructing their pipeline, mapping their feature set, or building a feature-comparison base before designing our own product.
---

# Competitor Teardown

Systematically reverse-engineer a competitor so we can match or beat their feature set. Output a structured teardown, not a vibe summary.

## When to use
- "How does <competitor> work under the hood?"
- "Build a feature comparison of the AI auto-apply tools."
- "What's <competitor>'s tech stack / pricing / apply mechanism?"

## Method (run in order)

### 1. Surface inventory (no login required)
- Fetch the marketing site, pricing page, Chrome/Firefox extension listing, and 2–3 third-party reviews (Trustpilot, review blogs).
- Pull the extension's listed permissions and supported sites — these reveal exactly which ATS/job boards they integrate and whether they use content scripts (autofill) vs. server-side apply.
- Record: pricing tiers, application volume caps, claimed sources count, supported ATS list, free vs paid features.

### 2. Pipeline reconstruction
Map everything onto the canonical 6 stages and note HOW each is done:
`Profile → Discover → Match/Rank → Tailor → Apply → Track`
- **Apply mechanism** is the key differentiator. Classify as: (a) ATS-native API POST, (b) browser-extension autofill (user clicks submit), (c) server-side headless browser auto-submit, (d) human-in-the-loop reviewers.
- **Discovery cadence** (e.g. "every 4 hours"), source count, and whether they scrape boards vs. partner DB.
- **Human-in-loop posture**: full-auto vs review-mode default.

### 3. Tech fingerprinting (passive only)
- Extension: read the public listing + (if the user provides it) the unpacked extension's manifest.json for `host_permissions` and content-script match patterns.
- Web app: note framework hints (Next.js/Vercel headers, Cloudflare headers, API subdomains) from public responses only.
- Do NOT attempt auth bypass, credential access, or scraping behind logins.

### 4. Gap & differentiation analysis
- What do reviews complain about? (billing friction, spam applies, scam-job exposure, poor matching are the recurring ones.)
- Where is the white space we can win? (better matching rubric, transparency/audit log, review-mode UX, ATS-native reliability, compliance.)

## Output format
Produce a markdown teardown with: **Overview · Pipeline table (6 stages × how) · Apply-mechanism classification · Pricing/volume table · Strengths · Weaknesses (from reviews) · What we'd copy · What we'd do better.**
For multi-competitor work, emit a single comparison matrix (rows = competitors, cols = features) — see `docs/competitor-matrix.md`.

## Guardrails
- Public data only. No login bypass, no scraping behind auth, no credential probing.
- Cite every source URL.
</content>
