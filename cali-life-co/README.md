# Cali Life Co. — Autonomous Store Operations

A drop-in system that turns a Claude Code session into a daily operations
manager for a Shopify store. It runs a fixed morning routine, audits the store,
drafts customer replies (never sends them), finds growth opportunities, and
leaves you a dated report — so problems surface the same morning instead of a
week later.

## How it solves the two big problems
- **"It says it'll do things but doesn't."** Every step must be backed by real
  tool output; "I will…" is banned. A Phase 8 self-check strips any unproven
  claim before the run ends.
- **"It breaks and I find out a week later."** A daily health + sales audit
  with loud 🚨 alerts, and a committed dated report every run. A check that
  can't run counts as a failure, never a silent skip. Sales drops past your
  threshold (or zero-sales days) trigger an immediate alert.

## Files
| File | Purpose |
|---|---|
| `CLAUDE.md` | Permanent memory + the full daily routine (auto-loads every session) |
| `DAILY-RUN.md` | The short prompt your scheduled morning session runs |
| `SETUP.md` | Connect Shopify + Gmail, set network access, schedule the run |
| `REPORT-TEMPLATE.md` | Shape of each daily report |
| `STATE.md` | Live KPIs, open issues, pending approvals |
| `BACKLOG.md` | Running task list |
| `reports/` | One dated report per run — the permanent paper trail |

## Quick start
1. Copy this folder's contents into the **root** of the Cali Life Co. repo
   (so `CLAUDE.md` is at the repo root).
2. Fill in the CONFIG block at the top of `CLAUDE.md`.
3. Follow `SETUP.md` to connect Shopify + Gmail and schedule the daily session
   with the prompt from `DAILY-RUN.md`.
4. Do one supervised first run, confirm the report is accurate and drafts (not
   sends) were created, then let the schedule take over.

Customer email is **draft-only by design** — review and send yourself.
Risky actions (prices, sending email, spend, publishing, code) are gated behind
explicit approval. Tune that via `AUTONOMY_LEVEL` in `CLAUDE.md`.
