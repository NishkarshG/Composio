# Approval Path

Guides for the slowest part of an agent integration: registering your own OAuth app with a provider and
getting it approved. Built for the Composio APM take-home.

- **Live page:** published as a Claude artifact (title "Approval Path"). It is private until the owner
  shares it from the page's Share menu.
- **Source:** this folder. One static HTML page plus JSON data. No server, no secrets.

## The problem, as I understood it

Composio supplies the OAuth app for **124** toolkits. For another **219** the developer has to register
their own app with the provider and give Composio the client ID and secret in a custom auth config
(redirect URI `https://backend.composio.dev/api/v3/toolkits/auth/callback`). Counts are from the
[managed OAuth apps directory](https://docs.composio.dev/toolkits/managed-auth), read 2026-10-20.

A developer in that second group needs four answers: how hard is this, how long will it take including
waiting, what could block me, and what can an agent do versus what do I have to do myself.

## Scope and why

- **Focus on the 219, not the 124.** Managed apps need no guide. The bring-your-own list is where
  launches stall.
- **Six apps chosen for different gates, not for popularity.** Spotify (user cap plus a business-size
  threshold), Xero (paid connection tiers), Shopify (review plus per-shop URLs), Meta Ads (business
  verification plus per-permission review), X (pay-per-use billing), Workday (customer admins register the
  client, no developer-owned app). Each exposes a different reason an OAuth app is "not ready".
- **Difficulty measures the gate, not the form.** Every app here gives credentials in under an hour.
  The score reflects what stands between those credentials and real users.
- **A common schema for every guide** (`data/SCHEMA.md`): stages with an owner (you, agent, provider),
  what works before approval, steps, gotchas, blockers with escalation paths, what an agent can and
  cannot do, and an evidence list. A guide that cannot say who acts and what is unverified is not
  finished.
- **Evidence is part of the product.** Each claim is `verified` (read on the cited page that session),
  `inferred` (community or third-party source) or `unverified`.

## How it works

1. **Library guides** (`data/guides/*.json`). One research agent per app, run in parallel, each with the
   brief in `research/agent-brief.md`. Agents could only read the web and could not log in or submit
   anything.
2. **Lead check.** I re-read the claims most likely to be wrong against the live pages (log below).
3. **Page** (`src/template.html`, built by `build.py` into `dist/index.html`). Overview ladder, one view
   per guide, copy-as-Markdown, and lookup against the embedded Composio directory.
4. **Live generation** for any app not in the library. Two Claude calls on the viewer's own account:
   - *Draft.* The model gets two page tools, `checkComposioDirectory` and `getReferenceGuide`, and writes
     a guide in the schema above.
   - *Review.* A second call acts as a sceptical reviewer, softens or removes claims likely to be stale,
     and adds what the draft missed.
   - The page then **forces every model-written evidence item to `inferred` or `unverified`**, drops any
     non-https URL, and adds one `verified` item of its own: whether Composio has a managed app, matched
     from the embedded directory.

## What I checked (2026-10-20)

Sixteen to twenty claims per guide were researched by agents: 96 verified, 19 inferred, 7 unverified
across 122 evidence items. I then re-read these myself:

| Claim | Result |
|---|---|
| Spotify dev mode allows 5 users; owner needs Premium | Confirmed on the quota-modes page |
| Spotify Extended Quota needs an organization and at least 250k MAU; review up to 6 weeks | Confirmed on the same page. The 250k figure is absent from Spotify's April 2025 announcement, so a guide based on that post alone would miss it |
| Xero free tier caps an app at 5 connections; Core is 50 connections for AUD 35/month with a card; effective 2 March 2026 | Confirmed on the Xero pricing page |
| X API is pay-per-use, not fixed tiers | Confirmed on docs.x.com. No effective date on the page, so "current as of when?" stays open |
| Shopify blocks new legacy custom apps from 1 Jan 2026 | Matches a Shopify staff announcement on community.shopify.dev. Not found on an official docs page |

Nothing I re-checked was contradicted. Nothing was corrected by the re-check either, so I can't claim the
agents' work is error-free, only that the highest-risk numbers held.

## Not verified

- **No provider app was actually registered.** That needs accounts, passwords, 2FA, payment details and
  legal acceptance, which an agent must not supply. Guides say where a human takes over. "Tested" here
  means read against official pages, not exercised end to end.
- **Review timelines are mostly community reports** (Meta, Shopify). Providers rarely publish them.
- **Composio specifics are unconfirmed.** Whether Composio's custom auth config accepts Meta's Facebook
  Login for Business configuration, Shopify's per-shop URLs, or Workday's per-tenant hosts is not in
  Composio's public docs. Guides flag it.
- **Many provider consoles are login-gated or script-rendered.** Workday guidance comes from vendor docs
  (Nango, Okta, Workato, CData), not Workday's own pages. Xero app-creation steps are from a third-party
  walkthrough.
- **Directory count.** The bring-your-own list as rendered shows 218 names against a headline of 219,
  so `data/directory.json` may be missing one toolkit.

## Limits of live generation

- **The page's Claude cannot browse.** A published page can call Claude but cannot fetch web pages (its
  network is blocked). Generated guides come from the model's memory plus a review pass, and the page
  labels them "AI draft, unverified". A server with web search would do better; see Next steps.
- **It was tested against a stand-in, not the real model.** In a headless browser I replaced Claude with
  a scripted reply and confirmed the tools are called, the review pass runs, evidence is downgraded, a
  `javascript:` link is dropped and injected HTML does not execute. I did not run it against the real
  `sample` call, so output quality and timing are unmeasured.
- **Generated guides are not saved.** They live in the page until it is closed. Copy as Markdown to keep
  one.
- **It spends the viewer's Claude usage**, and the first call asks them to allow it.

## Run it

```bash
python3 build.py           # writes dist/index.html from src/ and data/
open dist/index.html       # library, overview and search work offline except fonts
cd tests && npm i && node smoke.mjs   # headless check with a mocked Claude
```

Live generation works only inside Claude, where the page runs with the `sample` capability. To add a
guide, run the brief in `research/agent-brief.md`, drop the JSON into `data/guides/`, and rebuild.

## Next steps

1. **Server-side agent with web search** for generation, writing to a store so guides get a shareable
   URL and a "last checked" date.
2. **Re-verify on a schedule.** Prices and caps changed in the last year (Spotify, Xero, X); a guide
   should expire.
3. **Reach 100 apps** by clustering the 219 by gating model and researching one app per cluster, then
   templating the rest.
4. **Test the Composio side** (custom auth config with each provider's redirect URI rules) with a real
   account.

No credentials are stored anywhere in this folder.
