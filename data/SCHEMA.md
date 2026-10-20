# Guide JSON schema (one file per app: data/guides/<slug>.json)

{
  "slug": "spotify",
  "name": "Spotify",
  "composioSlug": "SPOTIFY",
  "website": "https://...",
  "summary": "One sentence: what getting an OAuth app ready looks like for this provider.",
  "difficulty": 1-5,                       // 1 = minutes, self-serve; 5 = gated, weeks/months, human review
  "difficultyWhy": "One or two sentences justifying the score.",
  "time": {
    "setup": "e.g. ~10 min",               // creating the app + getting credentials
    "approval": "e.g. none | 1-3 business days | 2-6 weeks (reported)",
    "total": "e.g. same day | 3-4 weeks"
  },
  "gatingModel": "self-serve | self-serve-with-limits | review-required | partner-or-tenant-gated",
  "devModeLimits": "What works BEFORE approval (user caps, test users only, scopes, etc.). null if none.",
  "stages": [ { "name": "Create app", "duration": "10 min", "owner": "you|agent|provider" } ],
  "steps": [
    { "n": 1, "title": "...", "detail": "Concrete instructions, field names, exact values.",
      "owner": "you|agent", "url": "official doc/console URL or null" }
  ],
  "requirements": ["account type, verification, fees, business docs, etc."],
  "gotchas": ["nuance that could bite: redirect URI rules, scope review, token expiry, regional limits"],
  "blockers": [ { "blocker": "e.g. App review rejected", "symptom": "...", "whatToDo": "...", "escalation": "support URL/email/forum or null" } ],
  "agentCanDo": ["what an agent can do for the developer"],
  "youMustDo": ["what a human must do (login, 2FA, CAPTCHA, identity/business verification, payment, legal acceptance)"],
  "composio": {
    "redirectUri": "https://backend.composio.dev/api/v3/toolkits/auth/callback",
    "note": "Anything provider-specific about using this redirect URI or scopes with Composio custom auth config."
  },
  "evidence": [
    { "claim": "specific factual claim made above",
      "status": "verified | inferred | unverified",   // verified = you read it on the cited page THIS session
      "source": "URL you actually fetched, or null",
      "note": "optional, e.g. 'docs say X but forum reports Y'" }
  ],
  "uncertainties": ["things you could not confirm, stated plainly"],
  "lastChecked": "2026-10-20"
}

Rules:
- Only mark `verified` if you fetched that page this session and it supports the claim. Never invent URLs.
- Prefer official docs. Community reports (forums, Reddit) may be used for approval timing but mark status `inferred` and say so.
- If docs are behind a login or JS wall and you cannot read them, say so under uncertainties.
- Redirect URI for Composio custom auth configs: https://backend.composio.dev/api/v3/toolkits/auth/callback (from Composio docs).
- No credentials, no account creation, no form submission on provider sites.
