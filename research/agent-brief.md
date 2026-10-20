# Research brief used for each library guide

One agent per app, run in parallel. Replace the bracketed parts. The agent writes one JSON file that
follows `data/SCHEMA.md`. It may only use WebSearch and WebFetch, may not log in or submit anything,
and must mark every claim `verified`, `inferred` or `unverified`.

---
You are researching how a developer gets a provider OAuth app ready and approved for **[APP]**
([API name] / Composio toolkit slug [SLUG]). Context: a developer building an AI agent wants their users
to connect [APP] accounts; Composio has NO managed OAuth app for [APP], so the developer must register
their own OAuth app and give Composio the client ID and secret via a custom auth config (redirect URI
https://backend.composio.dev/api/v3/toolkits/auth/callback).

Read data/SCHEMA.md first. Produce ONE file: data/guides/[slug].json following that schema exactly.

Research official docs first, community sources second. Cover: app creation and required fields, redirect
URI rules, app modes (development vs production), user or connection caps before approval, the review or
certification process and its timeline, scopes and which need review, fees and plan requirements, token
lifetimes and refresh behaviour, rate limits, and policy changes in the last 12 months (today is [DATE]).
Confirm numbers and dates on the page itself, not from search snippets. Every factual claim needs an
`evidence` entry. Do not create accounts, log in or submit anything. Do not fabricate URLs.

Aim for 8 to 14 tool calls. Reply with under 120 words: difficulty score, biggest blocker, and the top
two things you could not verify.
---

## Choosing the next apps

`data/directory.json` lists the toolkits that need a bring-your-own OAuth app. Pick by (a) how many
developers ask for it, and (b) how different its gating is from guides already in the library
(self-serve, paid-plan limit, per-permission review, tenant admin, partner programme).
