"""Collect the audit results and write the write-up and the film's data.

    python -I tools/hunt/audit_writeup.py
-> tools/hunt/out/audit/audit.json, video/audit_data.json, ~/Documents/html-reports/tax-loophole-audit.html

Test results come from LegalProofs/USTax/Hunt/Audit/<Name>/red.json and blind.json and from
tools/hunt/out/audit/mechanical.json. The per-claim notes below restate what RED.md and BLIND.md report.
"""
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUD = ROOT / "LegalProofs/USTax/Hunt/Audit"
OUTF = Path.home() / "Documents" / "html-reports" / "tax-loophole-audit.html"
E = html.escape
SRC = (ROOT / "tools/tax_writeup.py").read_text(encoding="utf-8")
CSS = SRC[SRC.index("<link rel=stylesheet"):SRC.index("</style>")].replace("{{", "{").replace("}}", "}")

TESTS = [
    ("blind", "Blind twin", "A second encoder, given the statute and a starting position and not told the result, writes the rules again and runs a search.", "The original encoder wrote the answer in."),
    ("T1", "Text fidelity", "Every rule the plan uses is read against the statute's words; each difference is fixed in a copy and the search re-run.", "A rule more generous than the text, or a restriction left out."),
    ("T2", "Close the gap", "One edit, the one Congress would make. The plan must disappear and the baseline must not move.", "A gain that comes from somewhere other than the claimed provision."),
    ("T3", "Ablation", "Remove each move the plan uses (it must fail) and every move it does not use (it must survive).", "Moves that are decoration, or a plan that leans on something unstated."),
    ("T4", "Earlier law", "Restore the text as it stood before the amendment the plan relies on.", "A plan that does not depend on what it says it depends on."),
    ("T5", "Free lunch", "Point the search at absurd goals and check conservation over every position reached.", "A model loose enough to create money."),
    ("T6", "Kernel", "Replay the plan and the closed-gap result as theorems checked by Lean's kernel; list the axioms.", "A result that exists only in compiled search code."),
    ("T7", "Arithmetic", "Recompute the figures in Python from the statute text, not from the Lean.", "An arithmetic slip shared by the search and its report."),
    ("T8", "Authority", "Regulations, IRS instructions and notices, practitioner writing.", "A plan already closed, or already in print."),
]

# name -> what was claimed, what is left, and the points the write-up and film quote
C = [
    dict(name="Accounts", short="Trump account as a backdoor Roth", sec="§530A(h)(4)",
         claim="An adult who kept a childhood Trump account contributes $7,000 a year to it and converts that account alone, tax-free, despite $100,000 of pre-tax money in another IRA.",
         claimed="+$3,500", restated="$0 of tax in the model's own terms", share=0,
         moves=["contribute $7,000", "convert the account"],
         words="Section 408(d)(2) shall be applied separately with respect to Trump Accounts and other individual retirement plans.",
         fix="For any taxable year beginning before the first day of the calendar year in which the account beneficiary attains age 18, ",
         fix_pos="before",
         found="Two moves; 14 positions find it. The search added nothing to reading the sentence.",
         worst="The +$3,500 is the objective's 25% premium on $14,000 of Roth money, not tax saved. It is zero with no premium, with equal rates now and later, or once the $100,000 is rolled into an employer plan, a move the model lacks.",
         outside="IRS Notice 2025-68 states both halves: Trump accounts are disregarded \"at all times\" for other IRAs' basis, and contributions after 18 follow the ordinary IRA rules. Nothing closes it. Treasury has announced further guidance.",
         blind="Reproduced. Contribute $7,000 and convert the account; the other IRA stays out of the ratio. The account's own $8,000 of untaxed money is taxed on the way."),
    dict(name="Household", short="Two unmarried adopters, two refunds", sec="§23(a)(4)",
         claim="Two unmarried adults who adopt together split the expenses and each receive the $5,000 refundable part of the adoption credit; a married couple receives one.",
         claimed="$6,951", restated="$0 to $574 over six years; $5,000 arrives a year or more early", share=8,
         moves=["A pays part", "B pays the rest", "each claims"],
         words="…regulations which treat unmarried individuals who pay or incur qualified adoption expenses with respect to the same child as 1 taxpayer for purposes of applying the dollar amounts in subsections (a)(3) and (b)(1)…",
         fix="(a)(4), ", fix_pos="in",
         found="Found by the search, on a grid of 0%, 50% or 100% of the expenses.",
         worst="$1,951 of the $6,951 is a baseline error that remains with the refundable rule deleted. The rest is timing: the household collects the full $17,280 either way through the carryforward, which the model counted as lost. The 50/50 split the search reported is worse than one adult paying everything.",
         outside="Nothing divides the $5,000 between co-adopters; Notice 97-9 and the Form 8839 instructions divide only the $17,280. The 2025 instructions and two 2026 IRS releases say \"$5,000 per eligible child\", which is not the statute's wording.",
         blind="Reproduced. Each adult who pays at least $5,000 gets a separate $5,000; gain $6,037 with the carryforward reported separately."),
    dict(name="Instruments", short="Fund dividend, then a wash sale", sec="§852(b)(4)(A)",
         claim="Buy fund shares the day before a capital gain dividend, sell and rebuy on the ex-date, sell the new shares 33 days after the first purchase: the dividend is long-term gain, the loss short-term.",
         claimed="$1,768 per $10,000", restated="$0 more than holding six months", share=0,
         moves=["buy before the dividend", "sell at a loss", "rebuy the same day", "sell the new lot"],
         words="…any loss on the sale or exchange of such share shall, to the extent of the amount described in clause (i), be treated as a long-term capital loss.",
         fix=" (or of any stock or securities the basis of which is determined under section 1091(d) by reference to such share)", fix_pos="after-share",
         found="Not a search result. The original output never printed it; it is a hand-written check line. A search returns it only once plain holding is excluded.",
         worst="It saves exactly what holding the shares for six months saves. Its only advantage is 33 days of exposure against 201, which the search's score does not value.",
         outside="Regulations 1.852-4, 1.1091-1, 1.1091-2 and 1.1223-1 and Publication 550 are silent. Committee reports and paywalled literature were not reached.",
         blind="Reproduced as one of three families tied at $1,700; the six-month hold is the simplest."),
    dict(name="Transfer", short="A new spouse splits a QTIP release", sec="§2519 + §2513",
         claim="A widow holding her late husband's property in a QTIP trust remarries, gives up her income interest, and splits the resulting transfer with the new spouse, whose exclusion shelters half.",
         claimed="$30M to $33M at year 25", restated="$9.6M with no growth; not allowed at $100M on a strict reading", share=30,
         moves=["remarry", "both consent", "release the income interest"],
         words="A gift made by one spouse to any person other than his spouse shall, for the purposes of this chapter, be considered as made one-half by him and one-half by his spouse…",
         fix=" (other than a transfer treated as made under section 2519)", fix_pos="after-gift",
         found="Found by the search, first through a modelling error that was then closed; it stayed first after the fix.",
         worst="The gain is ordinary gift-splitting with a later spouse whose exclusion is spent at no cost, not an effect of §2519: 70% to 100% of it survives the closing edit. As found, the trust pays the new spouse's $14M of gift tax, for which §2207A(b) gives no right.",
         outside="Regulation 25.2519-1 supports treating the transfer as the widow's gift and confirms it is two gifts. Nothing found closes or describes the plan; treatises were not retrieved.",
         blind="Reproduced: $82M reaches the child against $72M, with no growth."),
    dict(name="Corporate", short="Second §1202 limit via a holding company", sec="§1202(b)(1), (h)(4)",
         claim="A founder sells a fifth of qualified small business stock directly, moves the rest into a new holding company under §351, and sells the holding company: a second per-issuer limit.",
         claimed="$1,857,000", restated="$428,000 against selling over two years", share=23,
         moves=["sell one fifth", "contribute 80% to a new company", "sell that company"],
         words="…the aggregate amount of such gain from dispositions of stock issued by such corporation which may be taken into account…",
         fix="(stock treated as qualified small business stock under subsection (h)(4) being treated as issued by the corporation whose stock was exchanged) ", fix_pos="in",
         found="Found by the search, but the second limit is one hand-written line in the sale move.",
         worst="Already in print: a QSBS specialist writes that the issuer of replacement stock \"would be treated as a separate corporation\" for the limit. The gap dates from 1993, not 2025. Regulation 1.269-1 reaches a company formed to obtain an exclusion; the findings said no statute applied.",
         outside="Scott Dolson (FBT Gibbons) states the separate limit. No ruling and no §1202(k) regulation found.",
         blind="Reproduced, and bettered: a different order of transfers saves $3.57M."),
    dict(name="NewDeductions", short="SALT cap on separate returns", sec="§164(b)(6)–(7)",
         claim="Married equal earners at $300,000 each file separately; the phase-down reduces the full cap before it is halved, so each keeps $13,075 of deduction where halving first gives $5,950.",
         claimed="$11,024 over two years", restated="$9,974, and it is the IRS's own computation", share=90,
         moves=["file separately", "each itemizes", "each pays own tax"],
         words="…shall not exceed the applicable limitation amount (half the applicable limitation amount in the case of a married individual filing a separate return).",
         fix="; and in the case of such a return the reduction under paragraph (7)(B) shall be applied to that half", fix_pos="after",
         found="The reading was a switch set by hand. The search found only that separate returns win once it is on.",
         worst="The findings said the IRS worksheet halves first and that a taxpayer would be filing against the form. That is false: the 2025 Schedule A worksheet reduces, floors at $10,000, then halves. This is how the form already works, not a gap.",
         outside="Instructions for Schedule A (2025), line 5e worksheet. The Joint Committee explanation could not be retrieved.",
         blind="Reproduced: the text-order reading gives $13,075, and the encoder judged it the one the words support best."),
    dict(name="Residence", short="Expatriate and stay", sec="§877A(a)",
         claim="A long-term green-card holder gives up the card as a covered expatriate but stays in the US; the deemed sale excludes $890,000 of gain and raises basis by all of it.",
         claimed="$211,820", restated="a loss of $380,580 if the asset later goes to US persons from abroad", share=-100,
         moves=["give up the card", "decline to certify", "stay", "sell"],
         words="The amount which would (but for this paragraph) be includible in the gross income of any individual by reason of paragraph (1) shall be reduced (but not below zero) by $600,000.",
         fix=" This paragraph shall not apply to an individual who is a resident of the United States for the calendar year following the expatriation date.", fix_pos="after",
         found="Found by the search.",
         worst="Covered status is permanent, and §2801 taxes later gifts and bequests to US persons at 40%. The original charged it on one move only. The 2025 §2801 regulations read \"resident\" as domicile, so staying on a temporary visa may not switch it off.",
         outside="Notice 2009-85 Example 3 confirms the full basis adjustment. Nothing found closes or describes the plan.",
         blind="Reproduced to the dollar: $26,180 against $238,000."),
]

mech = json.loads((ROOT / "tools/hunt/out/audit/mechanical.json").read_text(encoding="utf-8"))
tot = {"pass": 0, "partial": 0, "fail": 0}
for c in C:
    red = json.loads((AUD / c["name"] / "red.json").read_text(encoding="utf-8"))
    bl = json.loads((AUD / c["name"] / "blind.json").read_text(encoding="utf-8"))
    c["tests"] = {"blind": {"r": "found", "d": c["blind"]}}
    for t in red["tests"]:
        c["tests"][t["id"]] = {"r": t["result"], "d": t["detail"]}
        tot[t["result"]] += 1
    c["verdict"] = red["verdict"]
    c["reason"] = red["verdict_reason"]
    c["authority"] = [a for a in red.get("authority", []) if a.get("url")]
    c["divergences"] = len(red.get("divergences", []))
    c["blind_positions"] = bl.get("positions")
(ROOT / "tools/hunt/out/audit/audit.json").write_text(json.dumps({"tests": TESTS, "claims": C, "totals": tot}, indent=1), encoding="utf-8")
npass = lambda tid: sum(1 for c in C if c["tests"][tid]["r"] in ("pass", "found"))
holds = sum(1 for c in C if c["verdict"].startswith("holds"))

# ---------------------------------------------------------------- film data
by = {c["name"]: i for i, c in enumerate(C)}
code = lambda s: s
SC = [
    dict(test="blind", focus=by["Residence"], anim="twin", title="A second encoder,<br>not told the answer",
         sub="Seven fresh encoders got the statute and a starting position. Nothing else.",
         card="<span class='c'>original search</span>   $26,180 against $238,000\n<span class='c'>blind twin</span>        $26,180 against $238,000\n<span class='ok'>same plan, same dollar</span>",
         count=f"{npass('blind')} / 7", countLabel="reproduced the result"),
    dict(test="T1", focus=by["Transfer"], anim="text", title="Read every rule<br>against the words",
         sub="Each difference from the statute is fixed in a copy, and the search run again.",
         card="<span class='c'>§2207A(b): who may recover the gift tax</span>\n<span class='q'>the person receiving the property</span>\n<span class='bad'>the model let the trust pay the new spouse's $14M</span>",
         count=f"{npass('T1')} / 7", countLabel="matched with nothing to fix"),
    dict(test="T2", focus=by["Accounts"], anim="break", title="Close the gap<br>with one edit",
         sub="If the gain is really from this sentence, changing it must end the plan and move nothing else.",
         card="<span class='c'>§530A(h)(4), with the words Congress would add</span>\n<span class='add'>For any taxable year beginning before … age 18,</span>\n<span class='q'>section 408(d)(2) shall be applied separately with respect to Trump Accounts and other individual retirement plans.</span>",
         count=f"{npass('T2')} / 7", countLabel="vanished cleanly"),
    dict(test="T3", focus=by["Instruments"], anim="ablate", title="Take the moves away,<br>one at a time",
         sub="A move the plan needs must break it. A move it does not need is decoration.",
         card="<span class='ok'>needed</span>      §1091(a), §1091(d), §852(b)(3)(B)\n<span class='bad'>decoration</span>  holding-period tacking, the second lot, the exit trade",
         count=f"{npass('T3')} / 7", countLabel="needed every load-bearing move"),
    dict(test="T4", focus=by["Corporate"], anim="past", title="Run it under<br>the earlier law",
         sub="A plan credited to the 2025 Act should not exist in the 2024 Code.",
         card="<span class='c'>§1202 as it stood from 1993 to 2025</span>\n5,045 against 6,902   <span class='bad'>the same saving</span>\n<span class='c'>the gap is 32 years old</span>",
         count=f"{npass('T4')} / 7", countLabel="depended on what they said"),
    dict(test="T5", focus=by["Transfer"], anim="lunch", title="Ask the model<br>for a free lunch",
         sub="Absurd goals on the unmodified rules; conservation checked over every position reached.",
         card="<span class='c'>positions checked across the seven</span>   about 2.4 million\n<span class='ok'>on each plan's path: nothing created</span>\n<span class='bad'>elsewhere in one model: $4,444,551 from nowhere</span>",
         count=f"{npass('T5')} / 7", countLabel="created no money anywhere"),
    dict(test="T6", focus=by["Household"], anim="kernel", title="Make the kernel<br>replay it",
         sub="Search output is compiled code. A theorem is checked by Lean's kernel.",
         card="<span class='kw'>theorem</span> closed_rule_cap : ∀ moves, refundable ≤ <span class='n'>5000</span>\n<span class='kw'>#print axioms</span> closed_rule_cap\n<span class='ok'>propext, Quot.sound</span>   <span class='c'>no sorryAx, no native_decide</span>",
         count=f"{npass('T6')} / 7", countLabel="replayed, standard axioms only"),
    dict(test="T7", focus=by["NewDeductions"], anim="text", title="Do the sums again,<br>from the statute",
         sub="A short Python script written from the text, not translated from the Lean.",
         card="<span class='c'>separate return, $300,000, 2026</span>\n40,400 − 30% × (300,000 − 252,500) = 26,150\nhalf of 26,150 = <span class='ok'>13,075</span>   <span class='c'>Lean: 13,075</span>",
         count=f"{npass('T7')} / 7", countLabel="agreed to the dollar"),
    dict(test="T8", focus=by["Corporate"], anim="text", title="Look outside<br>the statute",
         sub="Regulations, IRS instructions and notices, then practitioner writing.",
         card="<span class='c'>a QSBS specialist, already in print</span>\n<span class='q'>“would be treated as a separate corporation for purposes of Section 1202's gain exclusion cap”</span>\n<span class='bad'>already published</span>",
         count=f"{npass('T8')} / 7", countLabel="nothing closing or describing it"),
]
for i, s in enumerate(SC): s["kicker"] = f"Test {i + 1} of {len(SC)}"
chip = lambda c: (c["verdict"] if not c["verdict"].startswith("holds") else "holds on the text") + " · " + c["restated_chip"]
FILM = {"Accounts": "Trump account", "Household": "Adoption refund", "Instruments": "Fund dividend", "Transfer": "QTIP and a new spouse",
        "Corporate": "QSBS holding company", "NewDeductions": "SALT, separate returns", "Residence": "Expatriate and stay"}
CHIPS = {"Accounts": "$0 of tax saved", "Household": "$574, not $6,951", "Instruments": "no better than holding", "Transfer": "$9.6M, not $33M",
         "Corporate": "$428k, not $1.86M", "NewDeductions": "the IRS form does this", "Residence": "a loss after §2801"}
film = {
    "title": "<div class='bk'>Lean 4 · seven claims · nine tests</div><div class='bt'>Did the search<br>cheat?</div><div class='bs'>a blind search of the tax code returned seven plans; we tried to break every one</div>",
    "charge": {"kicker": "The charge", "title": "Last time, the loophole<br>was written into<br>the definitions",
               "sub": "That attempt was thrown out as circular. So each new claim gets nine tests it could fail."},
    "tests": [{"id": t[0], "name": t[1].lower()} for t in TESTS],
    "candidates": [{"short": FILM[c["name"]], "sec": c["sec"], "moves": c["moves"], "tests": {k: {"r": v["r"]} for k, v in c["tests"].items()},
                    "verdict": ("holds on the text" if c["verdict"].startswith("holds") else c["verdict"]) + " · " + CHIPS[c["name"]]} for c in C],
    "scenes": SC,
    "verdictCard": {"kicker": "Verdicts", "title": "None was circular.<br>No dollar figure<br>survived.", "sub": ""},
    "end": f"<div class='row'><span style='color:#3fdc9a'>0 of 7</span>written into the definitions</div>"
           f"<div class='row'><span style='color:#3fdc9a'>7 of 7</span>reproduced by an encoder who was not told</div>"
           f"<div class='row'><span style='color:#f2b24a'>{holds} of 7</span>hold on the statute's words; 1 was already in print</div>"
           f"<div class='row'><span style='color:#ff5a46'>0 of 7</span>dollar figures came through unchanged</div>"
           f"<div class='foot'>lean-proofs / LegalProofs / USTax / Hunt / Audit</div>",
}
(ROOT / "video/audit_data.json").write_text(json.dumps(film), encoding="utf-8")

# ---------------------------------------------------------------- write-up
COL = {"pass": "#059669", "found": "#059669", "partial": "#d97706", "fail": "#c2410c"}
SYM = {"pass": "✓", "found": "✓", "partial": "◐", "fail": "✕"}
WORD = {"pass": "passed", "found": "reproduced", "partial": "partly", "fail": "failed"}


def grid():
    w, left, top, cw, rh = 900, 300, 96, 64, 44
    h = top + rh * len(C) + 14
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img" aria-label="Seven claims against nine tests">']
    for j, t in enumerate(TESTS):
        x = left + j * cw + cw / 2
        o.append(f'<text x="{x}" y="{top - 12}" class="ax" transform="rotate(-38 {x} {top - 12})" style="font-size:13px;fill:currentColor">{E(t[1])}</text>')
    for i, c in enumerate(C):
        y = top + i * rh
        o.append(f'<text x="{left - 12}" y="{y + 20}" class="ax" text-anchor="end" style="font-size:13.5px;fill:currentColor">{E(c["short"])}</text>')
        o.append(f'<text x="{left - 12}" y="{y + 35}" class="ax" text-anchor="end">{E(c["sec"])}</text>')
        for j, t in enumerate(TESTS):
            r = c["tests"][t[0]]["r"]
            o.append(f'<rect x="{left + j * cw + 4}" y="{y + 5}" width="{cw - 8}" height="{rh - 10}" rx="5" fill="{COL[r]}"><title>{E(t[1])}: {E(WORD[r])}. {E(c["tests"][t[0]]["d"])}</title></rect>')
            o.append(f'<text x="{left + j * cw + cw / 2}" y="{y + 28}" text-anchor="middle" fill="#fff" style="font:600 16px IBM Plex Sans">{SYM[r]}</text>')
    o.append("</svg>")
    return "".join(o)


def survived():
    w, left, rowh, top = 900, 300, 40, 10
    h = top * 2 + rowh * len(C)
    zero = left + 150
    X = lambda v: zero + v / 100 * (w - zero - 150)
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img" aria-label="Share of each claimed gain that survived">',
         f'<line x1="{zero}" y1="{top}" x2="{zero}" y2="{h - top}" class="grid"/>']
    for i, c in enumerate(sorted(C, key=lambda c: -c["share"])):
        y = top + i * rowh; s = c["share"]
        col = "#059669" if s >= 60 else "#d97706" if s > 0 else "#c2410c" if s < 0 else "#64748b"
        o.append(f'<text x="{left - 12}" y="{y + 24}" class="ax" text-anchor="end" style="font-size:13.5px;fill:currentColor">{E(c["short"])}</text>')
        x0, x1 = (zero, X(s)) if s >= 0 else (zero - 110, zero)
        o.append(f'<rect x="{x0:.1f}" y="{y + 8}" width="{max(2, x1 - x0):.1f}" height="22" rx="3" fill="{col}"/>')
        lab = f"{s}%" if s >= 0 else "a net loss"
        o.append(f'<text x="{x1 + 8:.1f}" y="{y + 24}" class="lab" fill="{col}">{lab}</text>')
    o.append("</svg>")
    return "".join(o)


def statute(c):
    w, f = E(c["words"]), f'<ins>{E(c["fix"])}</ins>'
    if c["fix_pos"] == "before": return f + w[0].lower() + w[1:]
    if c["fix_pos"] == "after": return w + f
    if c["fix_pos"] == "after-share": return w.replace("such share shall", f"such share{f} shall")
    if c["fix_pos"] == "after-gift": return w.replace("A gift made by one spouse", f"A gift{f} made by one spouse")
    if c["name"] == "Household": return w.replace("subsections (a)(3) and (b)(1)", f"subsections (a)(3), {f}and (b)(1)")
    return w.replace("stock issued by such corporation which", f"stock issued by such corporation {f}which")


def card(c):
    rows = "".join(f'<tr><td style="white-space:nowrap"><b style="color:{COL[c["tests"][t[0]]["r"]]}">{SYM[c["tests"][t[0]]["r"]]}</b> {E(t[1])}</td><td>{E(c["tests"][t[0]]["d"])}</td></tr>' for t in TESTS)
    auth = "".join(f'<li><a href="{E(a["url"])}">{E(a["source"])}</a> <span class=m>({E(a.get("effect", ""))})</span></li>' for a in c["authority"][:6])
    vc = "#059669" if c["verdict"].startswith("holds") else "#d97706"
    return f"""<section class=claim id="{c['name']}">
<h2>{E(c['short'])}</h2>
<p class=m>{E(c['sec'])} · verdict: <b style="color:{vc}">{E(c['verdict'])}</b></p>
<p>{E(c['claim'])}</p>
<div class=two><div class=k><span>Claimed</span><b>{E(c['claimed'])}</b></div><div class=k><span>After the audit</span><b class=sm>{E(c['restated'])}</b></div></div>
<h3>The words, and the edit that closes it</h3>
<blockquote>{statute(c)}</blockquote>
<h3>Worst weakness</h3><p>{E(c['worst'])}</p>
<h3>Was it found by the search?</h3><p>{E(c['found'])}</p>
<h3>Outside the statute</h3><p>{E(c['outside'])}</p>
<details><summary>All nine tests</summary><table>{rows}</table>{f'<h3>Sources read</h3><ul>{auth}</ul>' if auth else ''}</details>
</section>"""


mrows = "".join(
    f'<tr><td>{E(k)}</td><td class=r>{r["rules_lines"]}</td><td class=r>{r["moves"]}</td><td class=r>{len(r["bypass_constructs"])}</td>'
    f'<td class=r>{len(r["technique_words_in_rule_code"])}</td><td class=r>{r["sections_cited"]}</td>'
    f'<td class=r>{len(r["figures_in_statute"])} / {r["figures_in_rules"]}</td></tr>' for k, r in mech.items())
trows = "".join(f"<tr><td style='white-space:nowrap'><b>{E(t[1])}</b></td><td>{E(t[2])}</td><td>{E(t[3])}</td></tr>" for t in TESTS)

page = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Loophole Search Audit</title>
{CSS}
td.r,th.r{{text-align:right}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 0}}@media(max-width:600px){{.two{{grid-template-columns:1fr}}}}
.k span{{display:block;margin-bottom:4px}}.k b.sm{{font-size:21px;line-height:1.3}}
blockquote{{margin:10px 0;padding:14px 18px;background:var(--s);border:1px solid var(--rule);border-radius:10px;font:400 17px/1.6 'Source Serif 4',serif}}
ins{{text-decoration:none;background:rgba(5,150,105,.16);color:#047857;border-radius:4px;padding:1px 3px}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]) ins{{color:#6ee7b7}}}}
.claim{{border-top:1px solid var(--rule);margin-top:44px}}details{{margin:14px 0}}summary{{cursor:pointer;color:var(--a)}}
video{{width:100%;border-radius:10px;border:1px solid var(--rule);background:#000;margin:10px 0}}
td{{vertical-align:top}}
</style></head><body><div class=w>
<p class=m>Lean 4 · global-law / lean-proofs / LegalProofs / USTax / Hunt / Audit · 10 November 2026</p>
<h1>Did the loophole search cheat?</h1>
<p class=lede>A blind search over twelve areas of the tax code returned seven plans that looked new. An earlier attempt at
this had been thrown out because the loophole was written into the definitions. So each of the seven was given nine
tests it could fail: a second encoder who was not told the answer, a one-line fix that should kill it, the law as it
stood before, and six more. None of the seven turned out to be circular. None of their dollar figures survived.</p>
<div class=grid4>
<div class=k><b>7 of 7</b><span>reproduced by a second encoder working only from the statute</span></div>
<div class=k><b>0 of 7</b><span>written into the definitions</span></div>
<div class=k><b>{holds} of 7</b><span>hold on the statute's words; one was already in print</span></div>
<div class=k><b>0 of 7</b><span>dollar figures came through unchanged</span></div>
</div>
<video controls preload=metadata src="tax-loophole-audit.mp4"></video>

<h2>The nine tests</h2>
<p>Each test is something the result could have failed. Eight were run by a reviewer told to break the claim and
rewarded for doing so; the first was run by an encoder who was told nothing.</p>
<table><tr><th>Test</th><th>What was done</th><th>What it would catch</th></tr>{trows}</table>

<h2>Results</h2>
<p>Green passed, amber passed in part, red failed. Hover a cell for the finding. Of the 56 red-team tests,
{tot['pass']} passed, {tot['partial']} passed in part and {tot['fail']} failed.</p>
{grid()}
<p>The columns that are solid green are the mechanical ones: remove a move, replay through the kernel, redo the
arithmetic. The amber is concentrated in the two that need judgment: whether the rules say what the statute says, and
whether the closing edit removes all of the gain. That is where the original searches were weak.</p>

<h2>How much of each claimed gain was left</h2>
{survived()}
<p>The readings held. The sizes did not. Three kinds of error account for nearly all of it:</p>
<ul>
<li><b>The objective.</b> The Trump-account gain was a 25% premium the scoring function gave to sheltered money, not tax.
The adoption gain counted a five-year carryforward as lost.</li>
<li><b>The baseline.</b> The small-business-stock plan was compared with the worst ordinary sale, not the two-year sale
the same search had printed. The adoption baseline put the expenses on the adult with no tax to offset.</li>
<li><b>What was left out.</b> The expatriation plan omitted a 40% tax on later gifts to US persons. The QTIP plan let
the trust pay a tax bill the statute gives it no right to pay.</li>
</ul>
<div class=callout><b>Three of the seven were not really found by the search.</b> The fund-dividend plan was a
hand-written check line. The SALT reading was a switch set by hand. The Trump-account plan is one sentence entered
as two moves, which fourteen positions find. In those three the search confirmed a reading somebody already had.</div>

{''.join(card(c) for c in C)}

<h2>The mechanical scan, all twelve files</h2>
<p>A script (<code>tools/hunt/audit.py</code>) checked what needs no judgment, over every search file and not only
the seven claims. No file uses <code>sorry</code>, <code>native_decide</code>, a declared axiom or <code>unsafe</code>.
No rule names a planning technique, with one exception: a helper in the accounts file is called <code>stripPre</code>.
Lean also requires a definition to come before its use, so no rule can refer to the search that follows it.</p>
<table><tr><th>File</th><th class=r>Rule lines</th><th class=r>Moves</th><th class=r>Checker bypasses</th><th class=r>Technique words in rule code</th><th class=r>Sections cited</th><th class=r>Dollar figures found in the cited text</th></tr>{mrows}</table>
<p class=m>Figures not found in the text are mostly indexed amounts (brackets, standard deductions) and scenario values. They were not checked against the revenue procedures.</p>

<h2>What this does and does not show</h2>
<ul>
<li><b>It shows the encodings were not circular.</b> Seven independent encoders reached the same plans from the text;
a one-line edit removed {npass('T2')} of the seven outright and left every baseline alone; kernel replays carry only Lean's standard
axioms.</li>
<li><b>It does not show the plans are new.</b> One is in print, one is the IRS's own worksheet, and prior-art checks
were eight to ten web searches each. Treatises, committee reports and paywalled journals were mostly not reached.</li>
<li><b>It does not show they work.</b> Economic substance, step transaction and the anti-avoidance sections are
outside every model.</li>
<li><b>The universal theorems are narrower than they sound.</b> Each "for all move sequences" proof is over a
cut-down model; its agreement with the full rules was checked by evaluation, not proved.</li>
<li><b>The red team did not reach everything.</b> One calendar run timed out twice. Several primary sources returned
errors.</li>
</ul>

<h2>Rules for the next round</h2>
<ul>
<li>The objective is tax paid, in dollars, with carryforwards valued. No premiums.</li>
<li>The baseline is the best ordinary plan the same search finds, not the worst.</li>
<li>A reading of the text is never a switch. If two readings exist, both are encoded and the result is reported under each.</li>
<li>A plan counts as found only if the search printed it before anyone wrote it down.</li>
<li>Every claim gets the blind twin and the closing edit before it is reported.</li>
</ul>

<h2>Files</h2>
<p><code>LegalProofs/USTax/Hunt/Audit/&lt;Name&gt;/</code> holds, for each claim, <code>BLIND.md</code> and
<code>Blind.lean</code> (the second encoding), <code>RED.md</code> and <code>red.json</code> (the nine tests) and the
Lean and Python files behind them. <code>tools/hunt/audit.py</code> is the mechanical scan and
<code>tools/hunt/audit_writeup.py</code> builds this page from those results.</p>
</div></body></html>"""
OUTF.write_text(page, encoding="utf-8")
print(OUTF, len(page), "bytes;", tot, "holds", holds, {t[0]: npass(t[0]) for t in TESTS})
