#!/usr/bin/env python3
"""Build the rebate fraud business deck on a copy of the Databricks corporate template.

Usage: python3 deck/build_gslides.py <presentation_id>

The presentation must be a fresh Drive copy of "*TEMPLATE Databricks Corporate Slide 2025".
Every new slide is inserted directly after a template slide on the same master, then moved
into place; the original template sample slides are deleted at the end. All text lives in its
own shape, every text box is sized for its text, and unused placeholders are deleted.
Numbers come only from evidence/HEADLINES.md.
"""

import json
import subprocess
import sys
import urllib.request

AUTH = "/Users/matt.cutini/.vibe/marketplace/plugins/fe-google-tools/skills/google-auth/resources/google_auth.py"
QUOTA = "gcp-dev-field-eng-aiapiquota"
EMU = 914400
FONT = "DM Sans"

# Template theme colours (Databricks Theme: Light master colour scheme).
NAVY = (0.043, 0.125, 0.149)      # DARK1
CORAL = (1.0, 0.373, 0.275)       # DARK2
RED = (1.0, 0.212, 0.129)         # HYPERLINK / accent bar red
TEAL = (0.106, 0.318, 0.384)      # ACCENT1
MUTED = (0.380, 0.529, 0.580)     # ACCENT5
OAT = (0.933, 0.929, 0.914)       # LIGHT2
OFFWHITE = (0.976, 0.969, 0.957)  # LIGHT1
WHITE = (1.0, 1.0, 1.0)

LIGHT_MASTER = "g324ba092b07_3_0"
LAYOUT = {
    "title": "g32c3cd6d0e3_1_108",      # 3 Title Slide B - Light 4 (dark navy cover)
    "basic": "g324ba092b07_3_45",       # 7 Content A - Basic
    "two_col": "g324ba092b07_3_50",     # 9 Content B - 2 Column
    "power": "g32fee89b7b9_0_21",       # Content E - Power Statement 1 (dark)
}
ANCHOR_SLIDE = "g32c3cd6d0e3_1_129"     # template sample slide on the light master


def token():
    return subprocess.check_output(["python3", AUTH, "token"], text=True).strip()


TOKEN = token()


def api(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("x-goog-user-project", QUOTA)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:2000]}")


def batch(pid, reqs):
    if reqs:
        return api("POST", f"https://slides.googleapis.com/v1/presentations/{pid}:batchUpdate", {"requests": reqs})


def get(pid):
    return api("GET", f"https://slides.googleapis.com/v1/presentations/{pid}")


def rgb(c):
    return {"rgbColor": {"red": c[0], "green": c[1], "blue": c[2]}}


def emu(v):
    return int(round(v * EMU))


# ---------- request builders ----------

class Slide:
    def __init__(self, sid):
        self.sid = sid
        self.reqs = []
        self.n = 0

    def _id(self):
        self.n += 1
        return f"{self.sid}_e{self.n}"

    def rect(self, x, y, w, h, fill, shape="RECTANGLE"):
        oid = self._id()
        self.reqs += [
            {"createShape": {"objectId": oid, "shapeType": shape, "elementProperties": {
                "pageObjectId": self.sid,
                "size": {"width": {"magnitude": emu(w), "unit": "EMU"}, "height": {"magnitude": emu(h), "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": emu(x), "translateY": emu(y), "unit": "EMU"}}}},
            {"updateShapeProperties": {"objectId": oid, "shapeProperties": {
                "shapeBackgroundFill": {"solidFill": {"color": rgb(fill)}},
                "outline": {"propertyState": "NOT_RENDERED"}}, "fields": "shapeBackgroundFill,outline"}},
        ]
        return oid

    def text(self, x, y, w, h, runs, fill=None, align="START", valign="TOP", shape="TEXT_BOX",
             spacing=None, bullets=False):
        """runs: list of paragraphs; each paragraph is a list of (text, size, color, bold)."""
        oid = self._id()
        self.reqs.append({"createShape": {"objectId": oid, "shapeType": shape, "elementProperties": {
            "pageObjectId": self.sid,
            "size": {"width": {"magnitude": emu(w), "unit": "EMU"}, "height": {"magnitude": emu(h), "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": emu(x), "translateY": emu(y), "unit": "EMU"}}}})
        props = {"contentAlignment": valign}
        fields = ["contentAlignment"]
        if fill is not None:
            props["shapeBackgroundFill"] = {"solidFill": {"color": rgb(fill)}}
            fields.append("shapeBackgroundFill")
        props["outline"] = {"propertyState": "NOT_RENDERED"}
        fields.append("outline")
        self.reqs.append({"updateShapeProperties": {"objectId": oid, "shapeProperties": props, "fields": ",".join(fields)}})
        full = "\n".join("".join(t for t, *_ in para) for para in runs)
        self.reqs.append({"insertText": {"objectId": oid, "insertionIndex": 0, "text": full}})
        first = runs[0][0]
        self.reqs.append({"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"}, "style": {
            "fontFamily": FONT, "fontSize": {"magnitude": first[1], "unit": "PT"},
            "foregroundColor": {"opaqueColor": rgb(first[2])}, "bold": first[3]},
            "fields": "fontFamily,fontSize,foregroundColor,bold"}})
        idx = 0
        for pi, para in enumerate(runs):
            for t, size, color, bold in para:
                if t:
                    self.reqs.append({"updateTextStyle": {"objectId": oid, "textRange": {
                        "type": "FIXED_RANGE", "startIndex": idx, "endIndex": idx + len(t)}, "style": {
                        "fontFamily": FONT, "fontSize": {"magnitude": size, "unit": "PT"},
                        "foregroundColor": {"opaqueColor": rgb(color)}, "bold": bold},
                        "fields": "fontFamily,fontSize,foregroundColor,bold"}})
                idx += len(t)
            idx += 1  # newline
        pstyle = {"alignment": align, "lineSpacing": 100,
                  "spaceAbove": {"magnitude": 0, "unit": "PT"},
                  "spaceBelow": {"magnitude": spacing or 0, "unit": "PT"}}
        self.reqs.append({"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"},
                                                   "style": pstyle, "fields": "alignment,lineSpacing,spaceAbove,spaceBelow"}})
        if bullets:
            self.reqs.append({"createParagraphBullets": {"objectId": oid, "textRange": {"type": "ALL"},
                                                         "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        return oid


def P(*runs):
    return list(runs)


def R(t, size=18, color=NAVY, bold=False):
    return (t, size, color, bold)


# ---------- deck content ----------

TITLE_PT = 28
FOOT_PT = 15

SLIDES = []


def slide(layout, title, notes, build, **kw):
    SLIDES.append(dict(layout=layout, title=title, notes=notes, build=build, **kw))


# 1 Title
def b1(s):
    """The cover uses only the layout's own placeholders."""


slide("title", "Turn suspected rebate leakage into documented, recoverable action",
      "[YOUR WORDS] Open with the change, not the technology. This prototype connects fragmented rebate "
      "evidence to the actions needed to investigate suspected fraud, keep a complete paper trail and, in a "
      "pilot, validate recovery. Everything you will see is synthetic and vendor-neutral.",
      b1,
      subtitle="For the Director of Rebate Operations\nand the SVP of Contracting, Rebates",
      footer="Synthetic, vendor-neutral prototype  |  November 2026")


# 2 Answer up front
def b2(s):
    y, h = 1.95, 1.75
    cards = [
        (0.82, 4.10, "$9,823,195.85", 36, "simulated suspected overpayment exposure"),
        (5.04, 2.42, "110,000", 40, "released synthetic claims"),
        (7.66, 2.42, "11", 40, "released periods"),
        (10.28, 2.20, "21,845", 40, "live gold feature groups"),
    ]
    for x, w, big, size, label in cards:
        s.rect(x, y, w, 0.06, RED)
        s.text(x, y + 0.06, w, h - 0.06,
               [P(R(big, size, NAVY, True)), P(R(label, 16, TEAL))],
               fill=OAT, valign="MIDDLE", spacing=4)
    s.text(0.82, 4.00, 11.66, 1.55,
           [P(R("The ask", 20, CORAL, True)),
            P(R("Sponsor a bounded pilot that measures verified fraud, achievable recovery and operating "
                "effort on your data, under your controls.", 22, WHITE))],
           fill=NAVY, valign="MIDDLE", spacing=6)
    s.text(0.82, 5.85, 11.66, 0.75,
           [P(R("Measured on the live synthetic prototype, 2026-11-19. Suspected exposure is not verified "
                "fraud, prevented loss or recovered cash.", FOOT_PT, MUTED))])


slide("basic", "$9,823,195.85 of suspected exposure is now visible. Pilot the path to verified recovery.",
      "[YOUR WORDS] Lead with the answer. The prototype processed 110,000 released synthetic claims across 11 "
      "released periods and surfaced $9,823,195.85 in simulated suspected overpayment exposure across 21,845 "
      "live gold feature groups. The decision we are asking for is not a production commitment. It is "
      "approval to validate the economics and the operating model in a bounded pilot.",
      b2)


# 3 Problem
def b3(s):
    s.text(0.82, 2.20, 4.10, 3.90,
           [P(R("110,000", 54, WHITE, True)),
            P(R("released synthetic claims that need identity, channel and purchase reconciliation", 18, OFFWHITE))],
           fill=NAVY, valign="MIDDLE", spacing=10)
    items = [
        ("Aliases hide one business. ", "Changing names and identifiers make one pharmacy look like several."),
        ("Two channels, one activity. ", "Medical and pharmacy claims describe the same units differently."),
        ("Claims outrun purchases. ", "Claimed units must be matched to sales and wholesaler distribution."),
        ("Why now. ", "Growth, gross-to-net pressure and pharmacy closures shrink the window to act."),
    ]
    s.text(5.30, 2.20, 7.18, 3.90,
           [P(R(a, 18, NAVY, True), R(b, 18, NAVY)) for a, b in items],
           valign="MIDDLE", spacing=16, bullets=True)


slide("basic", "Manual reconciliation can't keep pace with 110,000 claims, and the gap grows with the business",
      "[YOUR WORDS] Explain why now. This is not simple duplicate detection. Analysts have to resolve identities, "
      "reconcile two claim channels, prove product movement against sales and distribution, and document every "
      "interaction before the evidence goes stale or the pharmacy closes. Growth makes that gap bigger.",
      b3)


# 4 Today vs tomorrow
def b4(s):
    rows = [
        ("Analysts compare names, addresses and phone numbers by hand.",
         "Identity resolution links aliases to one pharmacy, with match evidence."),
        ("Medical and pharmacy claims are reviewed separately.",
         "Both channels are reconciled around the same entity and activity."),
        ("Claim, sales and distribution evidence is rebuilt for every case.",
         "Each prioritised case opens with its evidence already connected."),
        ("Outreach, responses and escalations live in different places.",
         "One operational record keeps the full action and evidence trail."),
    ]
    xl, xr, w = 0.82, 6.80, 5.68
    s.text(xl, 1.90, w, 0.55, [P(R("Today", 22, MUTED, True))], valign="MIDDLE")
    s.text(xr, 1.90, w, 0.55, [P(R("Tomorrow", 22, CORAL, True))], valign="MIDDLE")
    s.rect(xl, 2.48, w, 0.05, MUTED)
    s.rect(xr, 2.48, w, 0.05, CORAL)
    y = 2.68
    for a, b in rows:
        s.text(xl, y, w, 0.86, [P(R(a, 17, NAVY))], fill=OAT, valign="MIDDLE")
        s.text(xr, y, w, 0.86, [P(R(b, 17, NAVY, True))], fill=OAT, valign="MIDDLE")
        y += 0.98


slide("basic", "One governed case record replaces fragmented matching and follow-up",
      "[YOUR WORDS] Contrast the two operating models row by row. Today, skilled analysts spend their time "
      "assembling and reassembling evidence. Tomorrow, the evidence arrives as a governed case, and the "
      "investigator keeps authority over verification, outreach, recovery and escalation.",
      b4)


# 5 Flow
def b5(s):
    steps = [
        ("Source evidence", "Sales, wholesaler distribution, rebate claims and pharmacy reference files", OAT, NAVY),
        ("Governed identity", "Reconciled pharmacies, channels and quantities with quality controls", OAT, NAVY),
        ("Explainable priority", "Named score drivers rank cases; AI drafts the explanation", OAT, NAVY),
        ("A person decides", "Investigate, contact, verify, recover or escalate", CORAL, WHITE),
    ]
    w, gap, x, y, h = 2.56, 0.47, 0.82, 1.95, 2.55
    for i, (head, body, fill, fg) in enumerate(steps):
        s.text(x, y, w, h, [P(R(head, 20, fg, True)), P(R(body, 16, fg))], fill=fill, valign="MIDDLE", spacing=8)
        if i < 3:
            s.rect(x + w + 0.09, y + h / 2 - 0.16, 0.29, 0.32, RED, shape="RIGHT_ARROW")
        x += w + gap
    s.text(0.82, 4.85, 11.66, 1.45,
           [P(R("Every action updates one durable paper trail", 20, WHITE, True)),
            P(R("Case status, outreach, responses, decisions, recovery and escalation stay linked to the evidence.",
                17, OFFWHITE))],
           fill=NAVY, valign="MIDDLE", spacing=6)


slide("basic", "Every source flows into a short list of cases, and a person makes every decision",
      "[YOUR WORDS] Walk left to right. Each stage consumes the previous stage's output. The system organises "
      "and explains the evidence, but it never labels fraud, withholds payment, demands recovery or starts "
      "legal action on its own. Those decisions stay with authorised people.",
      b5)


# 6 Demo set-up
def b6(s):
    stops = [
        ("1", "Operations Overview", "Exposure, workload and persona views from the governed table"),
        ("2", "Priority Case Queue", "Cases ranked by named, explainable score drivers"),
        ("3", "Case Workspace", "Evidence, outreach, status and immutable case history"),
        ("4", "Ask Genie", "Leadership questions answered from the same governed source"),
    ]
    w, gap, x, y, h = 2.75, 0.22, 0.82, 1.95, 2.85
    for n, head, body in stops:
        s.rect(x, y, w, 0.06, RED)
        s.text(x, y + 0.06, w, h - 0.06,
               [P(R(n, 32, CORAL, True)), P(R(head, 20, NAVY, True)), P(R(body, 16, NAVY))],
               fill=OAT, valign="TOP", spacing=8)
        x += w + gap
    s.text(0.82, 5.10, 11.66, 1.30,
           [P(R("What to watch for", 20, CORAL, True)),
            P(R("The same evidence follows one case from detection to documented action, and suspected exposure "
                "is never presented as verified fraud.", 18, WHITE))],
           fill=NAVY, valign="MIDDLE", spacing=6)


slide("basic", "Watch suspected leakage become documented action",
      "[YOUR WORDS] Set expectations before the demo. There are four stops. Ask the audience to watch how one "
      "case moves from the overview to the queue, into the workspace where outreach and decisions are recorded, "
      "and then how leadership questions are answered from the same governed data.",
      b6)


# 7 Persona KPIs
def b7(s):
    cols = [
        ("Director of Rebate Operations", [
            ("Verified-fraud conversion", "Which suspected cases are confirmed as fraud"),
            ("Investigation aging", "Where cases stall, await a response or need escalation"),
            ("Evidence completeness", "Whether every decision has a defensible paper trail"),
        ]),
        ("SVP of Contracting, Rebates", [
            ("Recovered overpayments", "Dollars actually recovered from verified cases"),
            ("Remaining exposure", "The governed pool still awaiting investigation"),
            ("Leakage trend", "Where exposure persists as the business grows"),
        ]),
    ]
    x, w = 0.82, 5.68
    for head, kpis in cols:
        s.text(x, 1.90, w, 0.60, [P(R(head, 22, WHITE, True))], fill=NAVY, valign="MIDDLE")
        y = 2.62
        for k, d in kpis:
            s.rect(x, y, 0.07, 0.95, RED)
            s.text(x + 0.07, y, w - 0.07, 0.95, [P(R(k, 19, NAVY, True)), P(R(d, 16, NAVY))],
                   fill=OAT, valign="MIDDLE", spacing=2)
            y += 1.07
        x += w + 0.30
    s.text(0.82, 5.95, 11.66, 0.70,
           [P(R("Prototype boundary: ", FOOT_PT, CORAL, True),
              R("the demo measures suspected exposure; verified fraud and recovery become pilot outcomes.",
                FOOT_PT, MUTED))], valign="MIDDLE")


slide("basic", "Operations gets case control; leadership gets exposure control",
      "[YOUR WORDS] Each leader sees their own KPIs. The Director needs conversion, aging and complete evidence "
      "to report progress each month. The SVP needs recovered dollars, remaining exposure and trend for the "
      "quarterly committee. The prototype does not invent outcomes it has not observed; the pilot sets those "
      "baselines.",
      b7)


# 8 Value case
def b8(s):
    y, h = 1.95, 1.75
    boxes = [
        (0.82, 3.30, [P(R("$9,823,195.85", 28, WHITE, True)), P(R("measured suspected exposure", 16, OFFWHITE))], NAVY),
        (4.67, 2.25, [P(R("Verified-fraud rate", 19, NAVY, True)), P(R("measured in the pilot", 16, TEAL))], OAT),
        (7.47, 2.25, [P(R("Recovery rate", 19, NAVY, True)), P(R("measured in the pilot", 16, TEAL))], OAT),
        (10.27, 2.21, [P(R("Recovery value", 19, WHITE, True)), P(R("calculated, not assumed", 16, WHITE))], CORAL),
    ]
    ops = [(4.12, "×"), (6.92, "×"), (9.72, "=")]
    for x, w, runs, fill in boxes:
        s.text(x, y, w, h, runs, fill=fill, valign="MIDDLE", align="CENTER", spacing=4)
    for x, op in ops:
        s.text(x, y + 0.45, 0.55, 0.85, [P(R(op, 36, RED, True))], align="CENTER", valign="MIDDLE")
    notes = [
        ("Base: ", "21,845 live gold feature groups of simulated data at measurement time."),
        ("Verified-fraud rate: ", "from human-adjudicated pilot cases, not from model scores."),
        ("Recovery rate: ", "reflects contract terms, evidence quality and collection results."),
        ("Excluded: ", "analyst time saved and avoided future loss, until baselines are validated."),
    ]
    s.text(0.82, 4.05, 11.66, 2.15, [P(R(a, 17, NAVY, True), R(b, 17, NAVY)) for a, b in notes],
           valign="TOP", spacing=10, bullets=True)
    s.text(0.82, 6.20, 11.66, 0.55,
           [P(R("Every assumption is shown. No recovery figure is claimed before the pilot measures it.",
                FOOT_PT, MUTED))], valign="MIDDLE")


slide("basic", "$9,823,195.85 is an investigation pool, not a recovery forecast",
      "[YOUR WORDS] Be explicit about the economic boundary. $9,823,195.85 is the measured pool of simulated "
      "suspected exposure, not a savings promise. Both rates are unknown today; the pilot turns them into "
      "observed rates, and only then do we calculate a recovery value. Labor savings and avoided future loss "
      "stay out of the case until real baselines exist.",
      b8)


# 9 Trust
def b9(s):
    cards = [
        ("Governed access", ["Row filters and masks follow the signed-in viewer",
                             "Least-privilege access tested with a non-admin identity"]),
        ("Checked AI", ["Named score components explain every priority",
                        "An independent judge checks generated text for grounding",
                        "People verify, recover and escalate"]),
        ("Traceable record", ["Every case change writes immutable history",
                              "Lineage runs from raw file to case and answer"]),
    ]
    w, gap, x, y, h = 3.72, 0.25, 0.82, 2.05, 3.95
    for head, bullets in cards:
        s.rect(x, y, w, 0.06, RED)
        s.text(x, y + 0.06, w, 0.75, [P(R(head, 22, NAVY, True))], fill=OAT, valign="MIDDLE")
        s.text(x, y + 0.81, w, h - 0.81, [P(R(b, 18, NAVY)) for b in bullets],
               fill=OAT, valign="TOP", spacing=12, bullets=True)
        x += w + gap


slide("basic", "Every recommendation is governed, explainable and traceable",
      "[YOUR WORDS] Trust comes from boundaries we can test. Access is enforced by Unity Catalog for the person "
      "viewing the data, prioritisation is explainable, generated language is checked by an independent judge, "
      "and every operational change creates history in the database. A model signal is never treated as a "
      "fraud decision.",
      b9)


# 10 Platform
def b10(s):
    tiles = [
        ("1  Lakeflow", "Auto Loader ingestion, quality rules, reconciliation and identity features"),
        ("2  Unity Catalog", "Governed table with row filters, masks, tags and lineage"),
        ("3  AI + MLflow", "Explainable scoring, ai_query explanations and judge evaluation"),
        ("4  Lakebase", "Mutable case state with database-enforced history"),
        ("5  Genie", "Governed answers for leadership over the same table"),
        ("6  Databricks App", "Review, act and ask in one place, as the signed-in user"),
    ]
    w, gap, h = 3.72, 0.25, 1.70
    for i, (head, body) in enumerate(tiles):
        x = 0.82 + (i % 3) * (w + gap)
        y = 1.95 + (i // 3) * (h + 0.20)
        s.rect(x, y, 0.07, h, RED)
        s.text(x + 0.07, y, w - 0.07, h, [P(R(head, 20, NAVY, True)), P(R(body, 16, NAVY))],
               fill=OAT, valign="MIDDLE", spacing=6)
    s.text(0.82, 5.85, 11.66, 0.85,
           [P(R("Identity boundary: ", 16, CORAL, True),
              R("analytics and Genie run as the signed-in viewer; the app identity writes only to the operational "
                "case store. One queued Lakeflow Job runs every stage in order.", 16, WHITE))],
           fill=NAVY, valign="MIDDLE")


slide("basic", "One platform connects ingestion, governance, AI, operations and answers",
      "[YOUR WORDS] One page for the technical buyer. It is one connected journey, not six demos: each stage "
      "consumes the previous stage's output, and one queued job runs them in dependency order. Governed "
      "analytics run with the viewer's identity, while shared case writes use a least-privilege app identity "
      "and database-enforced history.",
      b10)


# 11 Pilot
def b11(s):
    phases = [
        ("1  Discover and map",
         "Approved definitions, source lineage and a measured baseline process",
         "Source owners, data access, policy owners and historical outcomes"),
        ("2  Prove and operate",
         "Reconciled evidence reaches investigators; every action leaves a complete trail",
         "Rebate operations time, legal and compliance guardrails"),
        ("3  Validate and decide",
         "Verified-fraud, recovery, aging and effort measures support an investment decision",
         "Finance validation, executive review and agreed scale criteria"),
    ]
    w, gap, x, y, h = 3.72, 0.25, 0.82, 1.95, 3.85
    for head, crit, need in phases:
        s.text(x, y, w, 0.70, [P(R(head, 20, WHITE, True))], fill=NAVY, valign="MIDDLE")
        s.text(x, y + 0.70, w, h - 0.70,
               [P(R("Success criterion", 15, CORAL, True)), P(R(crit, 16, NAVY)),
                P(R("What we need from you", 15, CORAL, True)), P(R(need, 16, NAVY))],
               fill=OAT, valign="TOP", spacing=8)
        x += w + gap
    s.text(0.82, 6.00, 11.66, 0.70,
           [P(R("Boundaries: ", FOOT_PT, CORAL, True),
              R("no automated denial, payment hold, recovery demand or legal escalation; no value claim "
                "without adjudicated outcomes.", FOOT_PT, MUTED))], valign="MIDDLE")


slide("basic", "A bounded pilot turns suspected exposure into validated recovery economics",
      "[YOUR WORDS] Position the pilot as a controlled learning loop. You supply definitions, data access, "
      "subject-matter time and outcome validation. The pilot succeeds when it produces trustworthy operating "
      "measures and a decision-quality value case, not when it simply recreates the synthetic demo.",
      b11)


# 12 Close
def b12(s):
    steps = [
        ("Approve the pilot", "Align operations, contracting, finance, legal and data owners"),
        ("Measure honestly", "Separate suspected exposure, verified fraud and recovered cash"),
        ("Scale what works", "Expand the control only when the evidence supports the economics"),
    ]
    w, gap, x, y, h = 3.72, 0.25, 0.82, 3.35, 2.35
    for i, (head, body) in enumerate(steps):
        s.rect(x, y, w, 0.06, RED)
        s.text(x, y + 0.06, w, h - 0.06,
               [P(R(str(i + 1), 30, CORAL, True)), P(R(head, 22, WHITE, True)), P(R(body, 17, OFFWHITE))],
               fill=TEAL, valign="TOP", spacing=8)
        x += w + gap


slide("power", "Start with your data, prove recovered value, then scale the control",
      "[YOUR WORDS] Close on the decision. The prototype shows the connected operating model works end to end "
      "on synthetic data. The bounded pilot decides whether it produces verified fraud findings, defensible "
      "recovery and a control that scales in your environment.",
      b12)


# ---------- build ----------

def placeholders(slide_obj):
    out = {}
    for e in slide_obj.get("pageElements", []):
        ph = e.get("shape", {}).get("placeholder")
        if ph:
            out[(ph["type"], ph.get("index", 0))] = e
    return out


def set_box(oid, el, x, y, w, h):
    bw = el["size"]["width"]["magnitude"]
    bh = el["size"]["height"]["magnitude"]
    return {"updatePageElementTransform": {"objectId": oid, "applyMode": "ABSOLUTE", "transform": {
        "scaleX": emu(w) / bw, "scaleY": emu(h) / bh, "shearX": 0, "shearY": 0,
        "translateX": emu(x), "translateY": emu(y), "unit": "EMU"}}}


def fill_text(oid, text, size, color=None, bold=None):
    style = {"fontFamily": FONT, "fontSize": {"magnitude": size, "unit": "PT"}}
    fields = ["fontFamily", "fontSize"]
    if color is not None:
        style["foregroundColor"] = {"opaqueColor": rgb(color)}
        fields.append("foregroundColor")
    if bold is not None:
        style["bold"] = bold
        fields.append("bold")
    return [{"insertText": {"objectId": oid, "insertionIndex": 0, "text": text}},
            {"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"}, "style": style,
                                 "fields": ",".join(fields)}}]


def main(pid):
    pres = get(pid)
    originals = [s["objectId"] for s in pres["slides"]]
    anchor_idx = originals.index(ANCHOR_SLIDE)
    master_of = {s["objectId"]: s["slideProperties"]["masterObjectId"] for s in pres["slides"]}
    assert master_of[ANCHOR_SLIDE] == LIGHT_MASTER

    ids = [f"rf_s{i + 1:02d}" for i in range(len(SLIDES))]
    # Insert each new slide directly after the anchor slide (same master), newest last so order is preserved.
    reqs = []
    for i, (sid, spec) in enumerate(zip(ids, SLIDES)):
        reqs.append({"createSlide": {"objectId": sid, "insertionIndex": anchor_idx + 1 + i,
                                     "slideLayoutReference": {"layoutId": LAYOUT[spec["layout"]]}}})
    batch(pid, reqs)
    # Move the new slides into place at the front of the deck.
    batch(pid, [{"updateSlidesPosition": {"slideObjectIds": ids, "insertionIndex": 0}}])

    pres = get(pid)
    by_id = {s["objectId"]: s for s in pres["slides"]}
    for sid, spec in zip(ids, SLIDES):
        sl = by_id[sid]
        assert sl["slideProperties"]["masterObjectId"] == LIGHT_MASTER, sid
        ph = placeholders(sl)
        reqs = []
        keep = set()
        if spec["layout"] == "title":
            t = ph[("CENTERED_TITLE", 0)]
            reqs += [set_box(t["objectId"], t, 0.83, 1.35, 7.40, 2.30)]
            reqs += fill_text(t["objectId"], spec["title"], 40, OFFWHITE, True)
            st = ph[("SUBTITLE", 0)]
            reqs += [set_box(st["objectId"], st, 0.83, 3.95, 7.00, 0.95)]
            reqs += fill_text(st["objectId"], spec["subtitle"], 20, OFFWHITE, False)
            ft = ph[("SUBTITLE", 1)]
            reqs += [set_box(ft["objectId"], ft, 0.83, 6.29, 7.00, 0.45)]
            reqs += fill_text(ft["objectId"], spec["footer"], 15, CORAL, False)
            keep = {t["objectId"], st["objectId"], ft["objectId"]}
        elif spec["layout"] == "power":
            t = ph[("TITLE", 0)]
            reqs += [set_box(t["objectId"], t, 0.83, 0.75, 11.66, 2.20)]
            reqs += fill_text(t["objectId"], spec["title"], 40, OFFWHITE, True)
            keep = {t["objectId"]}
        else:
            t = ph[("TITLE", 0)]
            reqs += [set_box(t["objectId"], t, 0.82, 0.45, 11.66, 1.15)]
            reqs += fill_text(t["objectId"], spec["title"], TITLE_PT, NAVY, True)
            keep = {t["objectId"]}
        for (ptype, _), el in ph.items():
            if ptype == "SLIDE_NUMBER":
                continue
            if el["objectId"] not in keep:
                reqs.append({"deleteObject": {"objectId": el["objectId"]}})
        s = Slide(sid)
        spec["build"](s)
        reqs += s.reqs
        # Speaker notes.
        notes_id = sl["slideProperties"]["notesPage"]["notesProperties"]["speakerNotesObjectId"]
        reqs.append({"insertText": {"objectId": notes_id, "insertionIndex": 0, "text": spec["notes"]}})
        batch(pid, reqs)
        print("built", sid, spec["title"][:60])

    # Remove the template sample slides.
    batch(pid, [{"deleteObject": {"objectId": o}} for o in originals])
    final = get(pid)
    print(json.dumps({"presentationId": pid, "slides": len(final["slides"]),
                      "url": f"https://docs.google.com/presentation/d/{pid}/edit"}))


if __name__ == "__main__":
    main(sys.argv[1])
