# Setup — connect integrations & schedule the daily run

One-time setup. After this, the store runs its morning routine on its own and
leaves you a report (and email drafts) to review.

## 1. Put these files in the Cali Life Co. repo

Copy the whole `cali-life-co/` folder contents into the root of the Cali Life
Co. repository so `CLAUDE.md` sits at the repo root (that's what makes it
auto-load every session). Commit them.

```
CLAUDE.md
DAILY-RUN.md
SETUP.md
REPORT-TEMPLATE.md
ACTION-QUEUE.md
STATE.md
BACKLOG.md
reports/
```

Then fill in the **CONFIG block** at the top of `CLAUDE.md` (store domain,
support inbox, alert thresholds, goals, autonomy level).

## 2. Connect Shopify (read/write Admin API)

The routine needs to read orders, revenue, products, inventory, and traffic,
and (within autonomy limits) make changes. Two options:

- **Shopify MCP server** — add a Shopify MCP to the environment so Claude has
  direct tools for orders/products/etc. Configure it with an Admin API access
  token from a custom app in your Shopify admin
  (Settings → Apps and sales channels → Develop apps → create app → Admin API
  access token). Grant read scopes for orders, products, inventory, analytics;
  add write scopes only for what you want autonomous (start read-only if unsure).
- **Or REST/GraphQL via stored token** — store the Admin API token as an
  environment secret and let Claude call the Admin API with `curl`. CLAUDE.md's
  health and sales phases work either way.

> Start **read-mostly**. Give write access only once you trust the reports.
> The Autonomy Boundaries in CLAUDE.md gate risky actions regardless.

## 3. Connect Gmail (drafts only)

The inbox phase reads customer mail and **creates drafts** — it never sends.
Add a Gmail MCP / Google Workspace integration to the environment and authorize
the support inbox account. Required capability: read messages + **create
drafts**. You do **not** need (and should not grant) send permission — keeping
send off is a hard backstop behind the "drafts only" rule.

## 3b. Connect marketing tools (for the Revenue Engine)

The marketing phase works best with live data. Connect what you have; each is
optional — a missing one is noted as a gap and the routine still drafts assets.

- **Email/SMS (Klaviyo recommended, or Shopify Email / Postscript / Attentive):**
  add the platform's MCP or store an API key as an environment secret so Claude
  can read flow/campaign performance and create **drafts**. Do **not** grant
  send permission — drafts/approval only is the backstop behind "never send."
- **Google Ads (+ Meta if you run paid social):** connect read access to spend,
  ROAS, and conversion metrics (Google Ads API / a reporting MCP, or export).
  Keep budget/spend changes manual — the routine only *proposes* ad changes.
- **SEO data (Google Search Console + GA4):** connect read access for indexing,
  rankings, and organic traffic. Without it, Claude falls back to on-page/site
  checks and notes the data gap.

Compliance note for SMS: only opted-in numbers, honor quiet hours in your
TIMEZONE, and include opt-out language. The routine drafts with this built in,
but you are the one who reviews and sends.

## 4. Set environment network access

Scheduled runs must reach Shopify, Gmail, your storefront, and analytics. In
the Claude Code web environment settings, choose a network policy that allows
those outbound hosts. See:
https://code.claude.com/docs/en/claude-code-on-the-web

## 5. Schedule the daily session

In Claude Code on the web, create a **scheduled session** against the Cali Life
Co. environment that runs every morning (set it ~30–60 min after your store's
midnight in `SUPPORT_HOURS_TZ` so a full prior day of data exists). Use the
prompt in `DAILY-RUN.md` as the session prompt.

Docs for environments, triggers, and scheduled sessions:
https://code.claude.com/docs/en/claude-code-on-the-web

If you'd rather not schedule, you can instead keep a session open and use the
`/loop` skill to re-run `DAILY-RUN.md` on an interval — but scheduled sessions
are the more reliable "runs itself every morning" option.

## 6. First run — supervised

Run it once yourself and read the report end to end. Confirm:
- The health table reflects reality (break something on purpose — e.g. an
  obviously-wrong domain — and confirm it shows up as 🚨, not a silent pass).
- Sales numbers match your Shopify dashboard.
- Email drafts were created and **nothing was sent**.
- A `reports/<date>.md` was committed.

Once you trust it, let the schedule take over and just review the morning
report + drafts.

## 7. Optional: alerting to your phone

Have the scheduled session message you (or the web/mobile app notification)
with the 5-line summary so a 🚨 reaches you the same morning — not a week later.
