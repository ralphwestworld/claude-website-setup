---
name: resume-intelligence
description: Parse a resume into a structured profile and score/rank jobs against it using semantic matching plus an LLM rubric. Use when building the profile-extraction stage, the match/rank stage, or the "should I apply?" gate.
---

# Resume Intelligence

Two jobs: (1) resume → canonical profile JSON, (2) job ↔ profile match score + apply/skip decision.

## 1. Resume → profile
- Extract text: PyMuPDF / pdfplumber (PDF), `unstructured` (DOCX/HTML).
- First pass structure: pyresparser (name, skills, experience) OR regex/spaCy.
- **Authoritative pass: Claude API with structured output** (Instructor/Pydantic) → normalize into the JSON Resume-style schema. LLM beats pyresparser on messy resumes; use the `claude-api` skill and cache the resume as a stable prefix.

## 2. Match & rank
- **Semantic**: sentence-transformers (SBERT) embeddings of resume sections vs. JD; cosine similarity. Store vectors in pgvector / Chroma. (On Cloudflare: **Vectorize** + **Workers AI** `bge` embeddings — runs natively.)
- **Keyword/skills gap**: rapidfuzz + TF-IDF for explainable overlap and missing keywords.
- **LLM re-rank (the gate)**: Claude scores each job against a rubric — must-have skills present, seniority fit, location/remote, salary, red flags (scam signals). Output `{score 0-100, reasons[], apply: bool, missing[]}`. This is the differentiator that prevents spam-applying.

## Output
```
{ job_id, semantic_score, keyword_score, llm_score, decision: apply|review|skip,
  reasons[], missing_keywords[] }
```

## Default posture
- `decision=apply` only above a high threshold AND when human-in-loop review is satisfied.
- Surface `reasons` + `missing_keywords` in the review UI so the user can edit before submit.

## Guardrails
- Never fabricate qualifications the candidate doesn't have when tailoring downstream — flag gaps, don't invent.
</content>
