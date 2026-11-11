"""Build the standalone write-up: Recreating Tax Court rulings in Lean.

    python tools/taxcourt/writeup.py <taxcourt dir> <out.html>

Reads <dir>/summary.json (from aggregate.py) and <dir>/index.json. Everything is inline; the page needs nothing but
itself (fonts fall back to system fonts offline).
"""
import html, json, sys, collections
from pathlib import Path

D, OUT = Path(sys.argv[1]), Path(sys.argv[2])
S = json.loads((D / "summary.json").read_text(encoding="utf-8"))
E = html.escape
T = collections.Counter(S["totals"])
VERD = [("match", "Matches the court", "#059669"), ("mismatch", "Differs", "#c2410c"),
        ("judgment", "Turns on the court's judgment", "#7c3aed"), ("not-encodable", "Outside the model", "#64748b"),
        ("pending-year", "Tax year not yet modelled", "#94a3b8")]
TAGNAME = {"eitc_32": "Earned income credit (§32)", "qualifying_child_152c": "Qualifying child (§152(c))",
           "head_of_household_2b": "Head of household (§2(b))", "ctc_24": "Child tax credit (§24)",
           "early_distribution_72t": "Early-distribution tax (§72(t))", "social_security_86": "Taxable Social Security (§86)",
           "penalty_6662": "Accuracy penalty (§6662)", "addition_6651a1": "Late filing (§6651(a)(1))",
           "addition_6651a2": "Late payment (§6651(a)(2))", "dependency_151": "Dependency exemption (§151)",
           "qualifying_relative_152d": "Qualifying relative (§152(d))", "ira_distribution_408d": "IRA distributions (§408(d))",
           "rollover_408d3": "60-day rollover (§408(d)(3))", "alimony_71_215": "Alimony (§§71, 215)",
           "education_credit_25a": "Education credits (§25A)", "gambling_165d": "Gambling losses (§165(d))",
           "ira_deduction_219": "IRA deduction (§219)", "se_tax_1401": "Self-employment tax", "gross_income_61": "Gross income (§61)",
           "other": "Other provisions"}

decided = T["match"] + T["mismatch"]
pct = round(100 * T["match"] / decided) if decided else 0
years = sorted({y for c in S["detail"] for y in (c.get("years") or [])})


def chip(v):
    c = dict((k, col) for k, _, col in VERD).get(v, "#64748b")
    lab = dict((k, l) for k, l, _ in VERD).get(v, v)
    return f'<span class="chip" style="--c:{c}">{E(lab)}</span>'


def money(x):
    try:
        return f"${int(float(str(x).replace(',', '').replace('$', ''))):,}"
    except (TypeError, ValueError):
        return E(str(x)) if x not in (None, "") else "—"


# verdict bar
bar = "".join(f'<div style="flex:{T[k]};background:{col}" title="{E(l)}: {T[k]}"></div>' for k, l, col in VERD if T[k])
legend = "".join(f'<li><i style="background:{col}"></i>{E(l)} <b>{T[k]}</b></li>' for k, l, col in VERD if T[k])

# by issue type
rows = []
for tag, c in sorted(S["by_tag"].items(), key=lambda kv: -sum(kv[1].values())):
    n = sum(c.values())
    if not n:
        continue
    m, mm = c.get("match", 0), c.get("mismatch", 0)
    rows.append(f"<tr><td>{E(tag)}</td><td class=r>{m}</td><td class=r>{mm}</td><td class=r>{c.get('judgment', 0)}</td>"
                f"<td class=r>{c.get('not-encodable', 0)}</td><td class=r>{c.get('pending-year', 0)}</td></tr>")

# mismatches and judgments, with diagnoses
def listing(kind, limit=40):
    out = []
    for c in S["detail"]:
        for i in c["issues"]:
            if i["verdict"] == kind:
                out.append(f"<li><b>{E(c['citation'] or c['id'])}</b> — {E(str(i.get('issue', '')))}: court {E(str(i.get('court', '—')))}, "
                           f"Lean {E(str(i.get('lean', '—')))}. <span class=m>{E(str(i.get('diagnosis', '')))}</span></li>")
    return "".join(out[:limit])

# case table
crow = []
for c in sorted(S["detail"], key=lambda c: (c.get("date") or "", c["id"])):
    d = c.get("deficiency") or {}
    chips = " ".join(chip(i["verdict"]) for i in c["issues"])
    crow.append(f"<tr><td><b>{E(c['citation'] or c['id'])}</b><br><span class=m>{E(c.get('name') or '')}</span></td>"
                f"<td>{E(', '.join(str(y) for y in (c.get('years') or [])))}</td><td>{chips}</td>"
                f"<td class=r>{money(d.get('court'))}</td><td class=r>{money(d.get('lean'))}</td></tr>")

page = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Tax Court rulings in Lean</title>
<style>
:root{{--bg:#f6f4ef;--s:#fffdf9;--ink:#1c1e22;--m:#5b5f66;--rule:#dcd8cf;--a:#1d4ed8;--code:#f1eee7}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#111316;--s:#181b1f;--ink:#e9e7e2;--m:#a0a4ab;--rule:#2d3137;--a:#8db8e3;--code:#1f2328;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#111316;--s:#181b1f;--ink:#e9e7e2;--m:#a0a4ab;--rule:#2d3137;--a:#8db8e3;--code:#1f2328;color-scheme:dark}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.65 'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',sans-serif}}
.w{{max-width:940px;margin:0 auto;padding:48px 16px 96px}}
h1{{font:700 44px/1.1 'Source Serif 4',Georgia,serif;margin:0 0 16px}}h2{{font:600 29px/1.2 'Source Serif 4',Georgia,serif;margin:52px 0 10px}}
h3{{font:600 14px system-ui;letter-spacing:.08em;text-transform:uppercase;color:var(--m);margin:28px 0 6px}}
.lede{{font:400 21px/1.55 'Source Serif 4',Georgia,serif}}.m{{color:var(--m);font-size:14px}}a{{color:var(--a)}}
code{{font:400 .9em ui-monospace,'JetBrains Mono',Consolas,monospace;background:var(--code);padding:1px 5px;border-radius:5px}}
pre{{background:var(--code);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;overflow-x:auto;font:400 13px/1.55 ui-monospace,Consolas,monospace}}
.grid4{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:24px 0}}
.k{{background:var(--s);border:1px solid var(--rule);border-radius:10px;padding:14px 16px}}.k b{{display:block;font:700 32px/1.1 Georgia,serif}}.k span{{display:block;font-size:14px;line-height:1.5;color:var(--m)}}
.tw{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-size:15px;margin:10px 0 24px}}th,td{{text-align:left;padding:8px;border-bottom:1px solid var(--rule);vertical-align:top}}th{{color:var(--m);font-size:13px;font-weight:500}}.r{{text-align:right;white-space:nowrap}}
.bar{{display:flex;height:22px;border-radius:6px;overflow:hidden;margin:14px 0 8px}}
ul.lg{{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:6px 18px;font-size:14px}}ul.lg i{{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;vertical-align:-1px}}
.chip{{display:inline-block;font-size:12px;line-height:1.4;padding:1px 7px;border-radius:999px;margin:2px 2px 0 0;border:1px solid var(--c);color:var(--c);white-space:nowrap}}
li{{margin:6px 0}}.callout{{border-left:3px solid #c2410c;background:var(--s);padding:12px 16px;border-radius:0 10px 10px 0;margin:18px 0}}
</style></head><body><div class=w>
<p class=m>Lean 4 · global-law / lean-proofs · follow-up to “Formalizing the US tax code” · November 2026</p>
<h1>Recreating Tax Court rulings in Lean</h1>
<p class=lede>The US Tax Court decides thousands of cases a year, many of them about ordinary family returns: who
counts as a qualifying child, whether a retirement withdrawal carries the 10% additional tax, how much Social Security
is taxable. In many of these the court first finds the facts and then applies the statute to them. We asked whether
a formal model of the statute, given only the facts the court found, reaches the court’s result.</p>
<div class=grid4>
<div class=k><b>{S['cases']}</b><span>Tax Court opinions recreated (summary and memorandum opinions, decided 2019–2025)</span></div>
<div class=k><b>{S['issues']}</b><span>issues the court decided, each checked against the Lean model</span></div>
<div class=k><b>{T['match']} / {decided}</b><span>computable issues where Lean reaches the court’s result ({pct}%)</span></div>
<div class=k><b>{years[0] if years else ''}–{years[-1] if years else ''}</b><span>tax years at issue, each with its own rates, thresholds and rules</span></div>
</div>

<h2>How it works</h2>
<p><b>The opinions.</b> We took recent opinions from the Tax Court’s own public opinion search (DAWSON), chosen
because their outcome turns on applying the statute to found facts rather than on valuing property or weighing
evidence. For each one we extracted the findings of fact, with a short quotation and page reference for each, and the
court’s holding on every issue.</p>
<p><b>The law.</b> A Lean library writes the rules these cases turn on from the Internal Revenue Code, with each tax
year’s figures from that year’s IRS revenue procedure: filing status and head of household (§§2, 7703), qualifying
children and relatives (§152) with the tie-breaker rules, the earned income credit (§32), the child tax credit (§24,
including the 2021 expansion), the 10% tax on early retirement distributions and its exceptions (§72(t)), taxable
Social Security (§86), self-employment tax, the accuracy penalty (§6662) and the late-filing and late-payment additions
(§6651), assembled into a return and a deficiency. Its year figures were checked against every printed row of the
IRS’s EIC and Tax Tables, about 28,000 rows, and reviewed by a second agent that had not written them.</p>
<p><b>The test.</b> Each case is encoded from the court’s findings only, never from its conclusions. Lean then
computes every holding, and we compare. Every difference was traced: an encoding slip (fixed), a gap in the model, an
error in the court’s or the IRS’s own arithmetic, or a step that is the court’s judgment rather than a computation.</p>

<h2>Results</h2>
<div class=bar>{bar}</div><ul class=lg>{legend}</ul>
<p>Where the outcome is a computation from the found facts, Lean reaches the court’s result on <b>{T['match']} of
{decided}</b> issues. The rest of the issues are of two other kinds. Some turn on a judgment that only the court can make,
such as whether a witness was credible or whether the taxpayer had reasonable cause; the model takes the court’s
finding as a fact, and then follows it. Others are questions the model cannot express, such as whether a payment was
income at all on disputed facts.</p>
<h3>By issue type</h3>
<div class=tw><table><tr><th>Issue</th><th class=r>Match</th><th class=r>Differs</th><th class=r>Judgment</th><th class=r>Outside model</th><th class=r>Year pending</th></tr>{''.join(rows)}</table></div>

<h2>Where Lean and the court differ</h2>
<p>Each difference, with its diagnosis:</p>
<ul>{listing('mismatch')}</ul>

<h2>Where the court’s judgment decides</h2>
<ul>{listing('judgment', 20)}</ul>

<h2>Every case</h2>
<div class=tw><table><tr><th>Opinion</th><th>Tax year</th><th>Issues</th><th class=r>Deficiency, court</th><th class=r>Deficiency, Lean</th></tr>{''.join(crow)}</table></div>

<h2>Limits</h2>
<ul>
<li><b>Selection.</b> The opinions were chosen because their issues looked computable; this is not a random sample of
Tax Court cases, most of which turn on substantiation and credibility.</li>
<li><b>Who did the work.</b> The findings were extracted and encoded by AI agents, each quotation checked against the
opinion text. No lawyer has reviewed the encodings.</li>
<li><b>Coverage.</b> The model covers ordinary individual returns. It does not cover business deductions, the
alternative minimum tax or the kiddie tax, so issues that depend on them are outside the model.</li>
<li><b>Agreement is about outcomes.</b> A match means the model reaches the court’s result from the court’s facts; it
does not show the court’s reasoning is the model’s.</li>
</ul>
<p class=m>Code: <code>lean-proofs/LegalProofs/USTax/TaxCourt/</code> (rules, year parameters, case runner) and
<code>lean-proofs/tools/taxcourt/</code>. Data: <code>tax-formalization-data/taxcourt/</code> (opinion texts, extracted
findings, encoded cases, results). Opinions: United States Tax Court, DAWSON public opinion search.</p>
</div></body></html>"""
OUT.write_text(page, encoding="utf-8")
print("wrote", OUT, len(page) // 1024, "KB")
