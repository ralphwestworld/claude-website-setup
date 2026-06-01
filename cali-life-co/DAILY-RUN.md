# Daily Run Prompt

This is the prompt your **scheduled web session** runs every morning. Because
`CLAUDE.md` is auto-loaded and carries all the detail, this prompt stays short
and focused on enforcing discipline. Paste this as the scheduled session's
prompt (see `SETUP.md`).

---

```
Run the full Daily Operations Routine for Cali Life Co. exactly as defined in
CLAUDE.md — Phases 0 through 8, in order.

Hard requirements:
- Evidence or it didn't happen: back every completed step with the actual tool
  output. Do not write "I will" — only report what you actually did, with proof.
- Any check you cannot run (API down, auth expired, tool error) is a FAILED
  check and goes in 🚨 NEEDS ATTENTION. Never skip silently.
- Customer email: create DRAFTS only. Never send anything.
- Stay within the autonomy boundaries in CLAUDE.md. Queue anything risky under
  "Awaiting your approval" instead of doing it.
- Finish by writing reports/<today's date>.md and committing + pushing it,
  plus updating STATE.md and BACKLOG.md. The committed report is the proof the
  run happened.

Marketing each day: work the full Marketing & Revenue Engine (email, SMS, SEO,
Google Ads, lifecycle/nurture). Draft every campaign, text, ad, and SEO asset —
never send or spend — and log each one in ACTION-QUEUE.md with a DUE DATE.

Before you end, run the Phase 8 self-check and fix anything that fails it.
Then give me a short summary in this shape:
- 🚨 Top alert (if any)
- What happened yesterday (sales + what marketing did/earned)
- Yesterday's revenue vs the 7-day average + where sales came from
- 📋 Action Queue: what needs me TODAY (incl. drafts to send), and what's due in
  the next 1–3 days
- The single most important decision for me today
```

---

## Manual / ad-hoc runs

You can also paste the block above into any Claude Code session in the Cali Life
Co. repo to run the routine on demand. To run just one part, ask for it by
phase name, e.g. *"Run only Phase 1 (health audit) and Phase 2 (sales audit)
from CLAUDE.md, with evidence."*
