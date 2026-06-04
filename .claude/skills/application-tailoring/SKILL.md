---
name: application-tailoring
description: Generate a tailored resume, cover letter, and screening-question answers for a specific job from the candidate's profile. Use when building the tailoring stage or generating per-application materials.
---

# Application Tailoring

Profile + JD → application materials, schema-valid and truthful.

## Outputs
1. **Tailored resume** — reorder/rephrase bullets to surface JD-relevant experience. Render via RenderCV or Jinja2+WeasyPrint → PDF. Keep one canonical profile; tailoring is presentation, never fabrication.
2. **Cover letter** — Claude API, grounded in profile + JD + company facts. Cache profile as stable prefix.
3. **Screening answers** — map the ATS `questions[]` schema to answers. Use Instructor/Pydantic so outputs are valid for each field type (boolean, select, free-text, file). For unknown/unanswerable questions → flag for human, never guess sensitive items (work authorization, salary expectations) without an explicit profile value.

## Field-mapping engine (reusable core asset)
Maintain a synonym dictionary mapping {profile field → many label variants}, e.g.
`first_name → ["First Name","Given Name","Forename","fname"]`.
This is the Simplify-style autofill brain; it serves both Path A (API field keys) and Path B (browser labels).

## Truthfulness rules (hard)
- Never invent employment, degrees, certifications, dates, or authorization status.
- Tailoring = emphasis and wording from REAL profile data only.
- Salary / sponsorship / demographic questions: use the profile's stored value or flag for human; never auto-fabricate.

## Workflow
1. Pull profile + job (with `questions[]`).
2. Generate resume + cover letter + mapped answers.
3. Produce a review bundle for the human-in-loop gate before any submit.
</content>
