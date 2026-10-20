#!/usr/bin/env python3
"""Build the single-file submission PDF for the Composio form (one file, max 10 MB).

Usage: python3 build_submission.py <repo_url> [live_url] [out.pdf]
Evidence counts and guide figures are read from data/, so the PDF cannot drift from the guides.
Without a repo URL it renders a highlighted placeholder and the file is a DRAFT.
"""
import json
import pathlib
import sys
from collections import Counter

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

root = pathlib.Path(__file__).parent
repo = (sys.argv[1] if len(sys.argv) > 1 else "").strip() or None
live = (sys.argv[2] if len(sys.argv) > 2 else "").strip() or "https://claude.ai/artifact/GkqBuv8J1bJgiJUDWzqNVQ"
out = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else root / "dist" / "Nishkarsh-Gupta-Composio-APM-submission.pdf"

guides = [json.loads(p.read_text()) for p in sorted((root / "data" / "guides").glob("*.json"))]
directory = json.loads((root / "data" / "directory.json").read_text())
ev = Counter(e["status"] for g in guides for e in g["evidence"])
ev_total = sum(ev.values())

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-M", FD + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV", boldItalic="DV-B")

INK, MUTED, ACC, LINE = colors.HexColor("#131c26"), colors.HexColor("#536270"), colors.HexColor("#0a5f7a"), colors.HexColor("#d3dae1")
base = ParagraphStyle("b", fontName="DV", fontSize=8.9, leading=12.4, textColor=INK, alignment=TA_LEFT, spaceAfter=4)
small = ParagraphStyle("s", parent=base, fontSize=8, leading=11, textColor=MUTED)
h1 = ParagraphStyle("h1", parent=base, fontName="DV-B", fontSize=21, leading=25, spaceAfter=3)
h2 = ParagraphStyle("h2", parent=base, fontName="DV-B", fontSize=11.5, leading=15, spaceBefore=7, spaceAfter=2, textColor=ACC, keepWithNext=1)
cell = ParagraphStyle("c", parent=base, fontSize=8.3, leading=11, spaceAfter=0)
cellb = ParagraphStyle("cb", parent=cell, fontName="DV-B")
bul = ParagraphStyle("bul", parent=base, leftIndent=11, bulletIndent=0, spaceAfter=2.5)


def a(url, label=None):
    return f'<link href="{url}" color="#0a5f7a"><u>{label or url}</u></link>'


def bullets(items):
    return [Paragraph(t, bul, bulletText="•") for t in items]


def short(s, n=64):
    s = s.split(" (")[0].split("; ")[0].split(" | ")[0]
    if len(s) <= n:
        return s
    cut = s[: n - 1].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


# Short ladder text where the guide's own wording cannot be cut safely (kept consistent with the guide).
LADDER_OVERRIDE = {"workday": {"setup": "~15-30 min per tenant", "approval": "Per customer; no central approval", "total": "Days to weeks per customer (inferred)"}}


def nice_name(name):
    return name.replace(" API v2", "").replace(" (Facebook Marketing API)", "")


repo_line = a(repo) if repo else '<font color="#ad2f1d"><b>[REPO LINK MISSING: DRAFT, DO NOT SEND]</b></font>'

story = [
    Paragraph("Approval Path", h1),
    Paragraph("Composio APM (Toolkits) take-home: guides for setting up and getting an OAuth app approved", base),
    Paragraph("Nishkarsh Gupta · nishkarshgupta381@gmail.com · 20 October 2026", small),
    Spacer(1, 6),
]
links = Table(
    [
        [Paragraph("Working experience", cellb), Paragraph(a(live) + "<br/>Open it inside Claude (claude.ai) for live generation.", cell)],
        [Paragraph("Source repository", cellb), Paragraph(repo_line, cell)],
        [Paragraph("README", cellb), Paragraph("In the repository root: setup, key decisions, limitations.", cell)],
    ],
    colWidths=[38 * mm, 136 * mm],
)
links.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.8, ACC), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
story += [links]

story += [Paragraph("The problem I chose to solve", h2)]
story += [Paragraph(
    f"Composio supplies the OAuth app for <b>{directory['managedCount']}</b> toolkits. For another <b>{directory['byoCount']}</b> the developer must register their own app with the provider, "
    f"wait for any review, then give Composio the client ID and secret in a custom auth config ({a('https://docs.composio.dev/toolkits/managed-auth', 'managed OAuth apps directory')}, read {directory['capturedOn']}). "
    "I focused on those 219, because managed apps need no guide and the bring-your-own list is where launches stall. A developer there needs four answers: how hard it is, how long it takes including waiting, what could block them, and what an agent can do versus what they must do themselves.", base)]

story += [Paragraph("What I built", h2)]
story += bullets([
    f"<b>A library of {len(guides)} researched guides</b> chosen for different gates, not popularity: Spotify, Xero, Shopify, Meta Ads, X and Workday. Every guide uses one schema: path stages with an owner (you, agent, provider), what works before approval, steps, gotchas, blockers with escalation, what an agent can and cannot do, and an evidence list.",
    "<b>A difficulty ladder</b> that scores the gate between credentials and real users, not the registration form. Every app here issues credentials in under an hour.",
    "<b>Live generation for any other app.</b> Claude drafts a guide with two tools (a lookup of Composio's directory and a reference guide from the library), a second pass reviews the draft for stale or doubtful claims, and the page then forces all model-written evidence to “inferred” or “unverified”, drops unsafe links, and adds one verified fact of its own: whether Composio has a managed app.",
])

story += [Paragraph("What the research showed", h2)]
story += bullets([
    "<b>The form is quick, the gate is not.</b> Spotify's Extended Quota needs an organization with at least 250k monthly active users and takes up to six weeks; Meta needs Business Verification plus per-permission App Review; Shopify's public listing needs App Store review.",
    "<b>Some gates are money or people.</b> Xero caps a free app at 5 connections and the next tier is a paid plan with a card. Workday has no developer-owned app: each customer's admin registers a client in their own tenant.",
    "<b>The answer is often hidden.</b> Several provider consoles are login-gated or script-rendered and review times are rarely published, so each claim carries a status instead of a confident number.",
])

rows = [[Paragraph(t, cellb) for t in ("App", "Difficulty", "Gating", "Setup", "Approval", "Total")]]
labels = {1: "Easy", 2: "Light", 3: "Moderate", 4: "Hard", 5: "Gated"}
gating = {"self-serve": "Self-serve", "self-serve-with-limits": "Self-serve, limits", "review-required": "Review required", "partner-or-tenant-gated": "Tenant gated"}
for g in sorted(guides, key=lambda x: x["difficulty"]):
    t = {k: LADDER_OVERRIDE.get(g["slug"], {}).get(k) or short(g["time"][k], 64) for k in ("setup", "approval", "total")}
    rows.append([Paragraph(nice_name(g["name"]), cell), Paragraph(f"{g['difficulty']}/5 {labels[g['difficulty']]}", cell), Paragraph(gating.get(g["gatingModel"], g["gatingModel"]), cell),
                 Paragraph(t["setup"], cell), Paragraph(t["approval"], cell), Paragraph(t["total"], cell)])
lad = Table(rows, colWidths=[24 * mm, 22 * mm, 24 * mm, 28 * mm, 40 * mm, 36 * mm], repeatRows=1)
lad.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 0.8, ACC), ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6), ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
story += [Spacer(1, 3), Paragraph("Difficulty ladder (from the guides)", ParagraphStyle("lh", parent=base, fontName="DV-B", spaceAfter=3)), lad]

story += [Paragraph("How I checked the guidance", h2)]
story += [Paragraph(
    f"One research agent per app read official provider docs first and community sources second, and could not log in or submit anything. Across the {len(guides)} guides that gave "
    f"<b>{ev_total}</b> evidence items: <b>{ev['verified']}</b> verified (read on the cited page), <b>{ev['inferred']}</b> inferred (community or third party), <b>{ev['unverified']}</b> unverified. "
    "I then re-read the claims most likely to be wrong against the live pages:", base)]
chk = [[Paragraph(t, cellb) for t in ("Claim", "Result")],
       [Paragraph("Spotify development mode allows 5 users; owner needs Premium", cell), Paragraph("Confirmed on the quota-modes page", cell)],
       [Paragraph("Spotify Extended Quota: organization, at least 250k MAU, review up to 6 weeks", cell), Paragraph("Confirmed. The 250k figure is missing from Spotify's April 2025 announcement, so a guide built on that post alone would miss it", cell)],
       [Paragraph("Xero free tier is 5 connections; Core is 50 for AUD 35 a month with a card (from 2 March 2026)", cell), Paragraph("Confirmed on the Xero pricing page", cell)],
       [Paragraph("X API is pay-per-use, not fixed tiers", cell), Paragraph("Confirmed on docs.x.com; the page shows no effective date", cell)],
       [Paragraph("Shopify blocks new legacy custom apps from 1 January 2026", cell), Paragraph("Matches a Shopify staff forum announcement; not found on an official docs page", cell)]]
ct = Table(chk, colWidths=[84 * mm, 90 * mm], repeatRows=1)
ct.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 0.8, ACC), ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5), ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
story += [KeepTogether([ct]), Spacer(1, 3), Paragraph("Nothing I re-checked was contradicted, and nothing needed correcting. That shows the highest-risk numbers held, not that the guides are error-free.", small)]

story += [Paragraph("What I could not verify, and the limits", h2)]
story += bullets([
    "<b>No provider app was registered.</b> That needs accounts, 2FA, payment and legal acceptance. “Tested” means read against official pages, not exercised end to end. Guides mark where a human takes over.",
    "<b>Live generation cannot browse.</b> A published page can call Claude but cannot fetch web pages, so generated guides come from the model's memory plus a review pass and are labelled “AI draft, unverified”. I tested the flow in a headless browser against a scripted stand-in for Claude (tool calls, review pass, evidence downgrade, link and HTML safety), not against the real model, so quality and timing are unmeasured.",
    "<b>Review timelines</b> for Meta and Shopify are community reports; providers rarely publish them.",
    "<b>Composio-side behaviour is untested:</b> for example whether a custom auth config accepts Shopify's per-shop URLs, Workday's per-tenant hosts, or Meta's Facebook Login for Business configuration. Guides flag each.",
    "<b>Workday</b> steps come from vendor docs (Nango, Okta, Workato, CData) because Workday's own documentation is login-gated.",
    "Generated guides are not saved; the library has " + str(len(guides)) + " apps, not 100.",
])

story += [Paragraph("What I would do next", h2)]
story += bullets([
    "Run generation server-side with web search and store guides under a shareable URL with a “last checked” date.",
    "Expire guides on a schedule: Spotify, Xero and X all changed terms in the last year.",
    "Reach 100 apps by grouping the 219 by gating model, researching one app per group, and templating the rest.",
    "Test the Composio side with a real account against each provider's redirect-URI rules.",
])


def footer(c, d):
    c.saveState()
    c.setFont("DV", 7.5)
    c.setFillColor(MUTED)
    c.drawString(18 * mm, 10 * mm, "Approval Path · Nishkarsh Gupta" + ("" if repo else " · DRAFT, repo link missing"))
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {d.page}")
    c.restoreState()


out.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm, bottomMargin=16 * mm, title="Approval Path: Composio APM take-home", author="Nishkarsh Gupta")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB){'' if repo else ' [DRAFT: no repo URL]'}")
