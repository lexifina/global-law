"""Write the US tax write-up (HTML) from the Lean search output.

    python tools/tax_writeup.py [OUT.html]     (default: ~/Documents/html-reports/us-tax-cliffs-lean.html)
"""
import html, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTF = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents" / "html-reports" / "us-tax-cliffs-lean.html"
E = html.escape
inv = json.loads((ROOT / "tools/out/tax_interest_cliff.json").read_text())
wage = json.loads((ROOT / "tools/out/tax_wage_cliffs.json").read_text())
real = [c for c in wage if c["drop"] >= 10]
noise = len(wage) - len(real)
land = json.loads((ROOT / "tools/out/tax_landscape.json").read_text())


def line_chart(series, w=900, h=330, xmax=70000, ymax=8500):
    pad_l, pad_b, pad_t, pad_r = 64, 40, 16, 16
    X = lambda v: pad_l + v / xmax * (w - pad_l - pad_r)
    Y = lambda v: h - pad_b - v / ymax * (h - pad_b - pad_t)
    out = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img" aria-label="Dollars lost to one extra dollar of interest, by wages">']
    for gy in range(0, ymax + 1, 2000):
        out.append(f'<line x1="{pad_l}" x2="{w - pad_r}" y1="{Y(gy):.1f}" y2="{Y(gy):.1f}" class="grid"/>'
                   f'<text x="{pad_l - 8}" y="{Y(gy) + 4:.1f}" class="ax" text-anchor="end">${gy:,}</text>')
    for gx in range(0, xmax + 1, 10000):
        out.append(f'<text x="{X(gx):.1f}" y="{h - 14}" class="ax" text-anchor="middle">${gx // 1000}k</text>')
    for label, color, pts in series:
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.1f},{Y(y):.1f}" for i, (x, y) in enumerate(pts))
        out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.4"/>')
        lx, ly = pts[len(pts) // 3]
        out.append(f'<text x="{X(lx) + 6:.1f}" y="{Y(ly) - 8:.1f}" class="lab" fill="{color}">{E(label)}</text>')
    out.append("</svg>")
    return "".join(out)


def series(status, kids):
    pts = {c["wages"]: c["drop"] for c in inv if c["status"] == status and c["kids"] == kids}
    return [(w, pts.get(w, 0)) for w in range(0, 70001, 500)]


chart = line_chart([("married, 3 children", "#c2410c", series("mfj", 3)), ("single, 3 children", "#2563eb", series("single", 3)),
                    ("single, 1 child", "#059669", series("single", 1)), ("no children", "#7c3aed", series("single", 0))])

# heat map: what the tax system adds (+) or takes (-) for a single parent of two, over wages x interest
rows = land["rows"]; nz, nx = len(rows), len(rows[0])
vals = [[r[i] - i * land["wageStep"] - j * land["interestStep"] for i in range(nx)] for j, r in enumerate(rows)]
vmax = max(abs(v) for r in vals for v in r)
cells = []
cw, ch = 900 / nx, 300 / nz
for j, r in enumerate(vals):
    for i, v in enumerate(r):
        t = min(1, abs(v) / vmax) ** .7
        col = f"hsl(152,62%,{12 + 44 * t:.0f}%)" if v >= 0 else f"hsl(18,78%,{12 + 40 * t:.0f}%)"
        cells.append(f'<rect x="{i * cw:.2f}" y="{300 - (j + 1) * ch:.2f}" width="{cw + .3:.2f}" height="{ch + .3:.2f}" fill="{col}"/>')
cliff_y = 300 - (11950 / land["interestStep"]) * ch
heat = (f'<svg viewBox="0 0 900 330" class="chart" role="img" aria-label="What the tax system adds or takes, by wages and interest">' + "".join(cells)
        + f'<line x1="0" x2="900" y1="{cliff_y:.1f}" y2="{cliff_y:.1f}" stroke="#fff" stroke-dasharray="6 5" stroke-width="1.6"/>'
        f'<text x="8" y="{cliff_y - 6:.1f}" class="lab" fill="#fff">interest $11,950: above this line the EITC is gone</text>'
        f'<text x="0" y="322" class="ax">wages $0</text><text x="900" y="322" class="ax" text-anchor="end">$72,000</text></svg>')

sav = "".join(f"<tr><td>{c['status'].upper() if c['status'] != 'single' else 'Single'}</td><td class=r>{c['kids']}</td><td class=r>${c['ira']:,}</td>"
              f"<td class=r>${c['wages']:,} → ${c['wages'] + 1:,}</td><td class=r>${c['drop']:,}</td></tr>" for c in sorted(real, key=lambda c: -c["drop"]))
maxinv = max(inv, key=lambda c: c["drop"])

page = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Tax Cliffs, Proved</title>
<link rel=stylesheet href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root{{--bg:#f6f4ef;--s:#fffdf9;--ink:#1c1e22;--m:#5b5f66;--rule:#dcd8cf;--a:#1d4ed8;--code:#f1eee7}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#111316;--s:#181b1f;--ink:#e9e7e2;--m:#a0a4ab;--rule:#2d3137;--a:#8db8e3;--code:#1f2328;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#111316;--s:#181b1f;--ink:#e9e7e2;--m:#a0a4ab;--rule:#2d3137;--a:#8db8e3;--code:#1f2328;color-scheme:dark}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.65 'IBM Plex Sans',system-ui,sans-serif}}
.w{{max-width:900px;margin:0 auto;padding:48px 16px 96px}}
h1{{font:700 46px/1.08 'Source Serif 4',Georgia,serif;margin:0 0 14px}}h2{{font:600 30px/1.2 'Source Serif 4',Georgia,serif;margin:56px 0 10px}}
h3{{font:600 15px 'IBM Plex Sans';letter-spacing:.08em;text-transform:uppercase;color:var(--m);margin:30px 0 6px}}
.lede{{font:400 21px/1.55 'Source Serif 4',serif}}.m{{color:var(--m);font-size:14px}}a{{color:var(--a)}}
.grid4{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:26px 0}}
.k{{background:var(--s);border:1px solid var(--rule);border-radius:10px;padding:14px 16px}}.k b{{display:block;font:700 34px/1.1 'Source Serif 4',serif}}.k span{{font-size:14px;color:var(--m)}}
pre{{background:var(--code);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;overflow-x:auto;font:400 13.5px/1.6 'JetBrains Mono',monospace}}
code{{font:400 .92em 'JetBrains Mono',monospace;background:var(--code);padding:1px 5px;border-radius:5px}}
.chart{{width:100%;height:auto;background:var(--s);border:1px solid var(--rule);border-radius:10px;margin:10px 0}}
.chart .grid{{stroke:var(--rule)}}.chart .ax{{font:12px 'IBM Plex Sans';fill:var(--m)}}.chart .lab{{font:600 13px 'IBM Plex Sans'}}
table{{width:100%;border-collapse:collapse;font-size:15px;margin:10px 0}}th,td{{text-align:left;padding:7px 8px;border-bottom:1px solid var(--rule)}}th{{color:var(--m);font-size:13px}}.r{{text-align:right}}
.callout{{border-left:3px solid #c2410c;background:var(--s);padding:12px 16px;border-radius:0 10px 10px 0;margin:18px 0}}
</style></head><body><div class=w>
<p class=m>Lean 4 · global-law / lean-proofs · tax year 2025</p>
<h1>Finding the cliffs in the US tax code with a theorem prover</h1>
<p class=lede>We wrote a slice of the 2025 federal income tax as executable Lean code, proved that the rate schedule
on its own can never take more than an extra dollar, and then let Lean search two million households for the places
where the rest of the code does. It found {len(real) + len(inv):,} genuine cliffs, and proved every one of them.</p>
<div class=grid4>
<div class=k><b>${maxinv['drop']:,}</b><span>lost to one extra dollar of interest (married, three children, ${maxinv['wages']:,} wages)</span></div>
<div class=k><b>$799</b><span>lost to one extra dollar of wages, at a Saver's Credit tier</span></div>
<div class=k><b>$3,511</b><span>a year: the price of marrying for two single parents on $20,000 each</span></div>
<div class=k><b>{len(real) + len(inv):,}</b><span>cliffs found by search, each re-proved by Lean's kernel</span></div>
</div>

<h2>Why a theorem prover</h2>
<p>A tax calculator can tell you what one household owes. It cannot tell you that something is true for <i>every</i>
household, and it cannot be trusted further than its code. Lean does both jobs. The model is ordinary code that runs, so
it can search; and statements about it are theorems, which Lean only accepts with a proof its small kernel checks. A
search that finds a cliff hands Lean the two households; Lean recomputes both and confirms the loss to the dollar. A claim
that holds everywhere, like "the brackets never take more than 100%", is proved for all incomes at once, not sampled.</p>

<h2>The model</h2>
<p>One household, one year: filing status (single, married filing jointly, head of household), qualifying children,
wages, taxable interest and deductible IRA contributions. It computes:</p>
<ul>
<li>employee payroll tax (6.2% Social Security up to $176,100, 1.45% Medicare);</li>
<li>adjusted gross income, the standard deduction ($15,750 / $31,500 / $23,625 after Pub. L. 119-21) and the 2025 rate
schedule (Rev. Proc. 2024-40 §2.01);</li>
<li>the Earned Income Tax Credit (§32; Rev. Proc. 2024-40 §2.06), including the §32(i) limit on investment income
($11,950 for 2025);</li>
<li>the Child Tax Credit ($2,200 a child) and its refundable part (up to $1,700 a child, 15% of earnings over $2,500);</li>
<li>the Saver's Credit (§25B; tiers from Notice 2024-80).</li>
</ul>
<p>Net income is wages plus interest, minus income and payroll tax, plus refundable credits. IRA contributions are
treated as the household's own money, so contributing does not count as a loss. All arithmetic is in whole dollars.
Every figure was checked against the IRS and the statute; the sources are listed at the end.</p>

<h2>Result 1: the brackets alone never take the whole dollar</h2>
<p>A common fear is that a raise can push you into a higher bracket and leave you with less. For the rate schedule this
is impossible, and Lean proves it for every filing status and every taxable income:</p>
<pre>theorem scheduleTax_step (s : Status) (x : Nat) :
    scheduleTax s (x + 1) ≤ scheduleTax s x + 1</pre>
<p>The proof does not test incomes. It shows that one more dollar adds that bracket's rate (at most 37 cents) to the
unrounded tax, because exactly one bracket contains any income, and then that rounding cannot turn 37 cents into more
than a dollar. So every cliff below comes from somewhere else: from credits that switch off at a threshold.</p>

<h2>Result 2: the investment-income cliff</h2>
<p>§32(i)(1): "No credit shall be allowed under subsection (a) for the taxable year if the aggregate amount of
disqualified income of the taxpayer for the taxable year exceeds $10,000" (indexed to $11,950 for 2025). The rule is
all-or-nothing, so the dollar that crosses the limit removes the whole credit:</p>
<pre>theorem investment_cliff_8045 :
    net ⟨.mfj, 3, 18000, 11951, 0⟩ + 8045 = net ⟨.mfj, 3, 18000, 11950, 0⟩ := by decide</pre>
<p>The search ran the model at every $500 of wages for every family type and found {len(inv)} households where that
dollar costs money. The chart shows the loss: it is the household's whole EITC, so it is largest exactly where the
credit is largest.</p>
{chart}
<p class=m>Dollars lost when taxable interest goes from $11,950 to $11,951, by wages. Computed by the Lean model; every
point is a proved theorem.</p>
{heat}
<p class=m>What the tax system adds (green: credits exceed taxes) or takes (orange) for a single parent with two
children, over wages (left to right) and taxable interest (bottom to top, $0 to $15,000). The green band of the EITC
ends at the dashed line, all at once: that edge is the cliff.</p>
<div class=callout><b>The loophole and the trap.</b> Disqualified income counts taxable interest, dividends, capital
gains, rents and royalties, and even tax-exempt interest; it does not count earnings inside an IRA or 401(k). For a
family near the limit, moving savings into a retirement account, or letting a certificate of deposit mature in January
instead of December, is worth up to ${maxinv['drop']:,}. The theorem <code>arbitrage_value</code> states it for the
first family: the same household with one dollar less of taxable interest is $8,045 better off.</div>

<h2>Result 3: Saver's Credit tiers</h2>
<p>§25B(b) gives a credit of 50%, 20% or 10% of retirement contributions (up to $2,000 a person) depending on AGI, with
hard edges between the tiers. The search found {len(real)} wage levels where one more dollar of pay costs money, all of
them at those edges:</p>
<table><tr><th>Filing</th><th class=r>Children</th><th class=r>Contributions</th><th class=r>Wages</th><th class=r>Loss</th></tr>{sav}</table>
<pre>theorem savers_cliff_799 :
    net ⟨.mfj, 0, 51501, 0, 4000⟩ + 799 = net ⟨.mfj, 0, 51500, 0, 4000⟩ := by decide
theorem ira_dollar_value :
    net ⟨.mfj, 0, 51501, 0, 4001⟩ - net ⟨.mfj, 0, 51501, 0, 4000⟩ = 800 := by decide</pre>
<p>The second theorem is the arbitrage: for the couple one dollar over the tier, contributing one more dollar to an IRA
pulls AGI back under it and is worth $800.</p>

<h2>Result 4: marriage penalties</h2>
<p>The EITC and the standard deduction do not double on marriage, so two low earners can lose by marrying:</p>
<pre>theorem marriage_penalty_3511 :
    net ⟨.mfj, 2, 40000, 0, 0⟩ + 3511 =
      net ⟨.hoh, 1, 20000, 0, 0⟩ + net ⟨.hoh, 1, 20000, 0, 0⟩ := by decide
theorem marriage_penalty_1999 :
    net ⟨.mfj, 2, 44000, 0, 0⟩ + 1999 =
      net ⟨.hoh, 2, 22000, 0, 0⟩ + net ⟨.single, 0, 22000, 0, 0⟩ := by decide</pre>

<h2>How the search works</h2>
<p><code>Search.lean</code> runs the model, unchanged, over every whole-dollar wage from $0 to $120,000 for 17
household types (2.04 million household-years) and over the interest limit at every $500 of wages. It keeps each point
where one more dollar leaves the household with less. {noise:,} of those are drops of $1 or $2 caused by whole-dollar
rounding in the model, and are set aside; the rest, {len(real) + len(inv):,} genuine cliffs, are written into Lean files
by <code>gen_tax_certs.py</code>, and <code>lake build</code> has the kernel recompute each one. The whole run takes under
a minute; checking every certificate takes seven seconds.</p>

<h2>What this does not show</h2>
<ul>
<li>It is a model of part of the code: no state tax, itemised deductions, other credits, self-employment tax, or
benefits outside the tax code (SNAP, Medicaid, housing), which create larger cliffs of their own.</li>
<li>The EITC uses the statutory formula; the IRS tables round in $50 bands, so table amounts can differ by a few dollars
and the exact dollar at which a phase-out amount changes can move.</li>
<li>Tax-exempt interest counts as disqualified income in the statute but is not modelled separately.</li>
<li>A proof shows the stated figure follows from the model. It does not show the model is the law: the parameters and
rules were checked by hand against the sources below. This is research, not tax advice.</li>
</ul>

<h2>Reproduce</h2>
<pre>cd lean-proofs
lake env lean LegalProofs/USTax/Search.lean   # search: writes tools/out/tax_*.json
python tools/gen_tax_certs.py                 # one Lean theorem per cliff
lake build                                    # Lean checks every proof and every cliff
python tools/tax_writeup.py                   # this page</pre>

<h3>Sources</h3>
<ul class=m>
<li>Rev. Proc. 2024-40 (2025 brackets, EITC): <a href="https://www.irs.gov/pub/irs-drop/rp-24-40.pdf">irs.gov/pub/irs-drop/rp-24-40.pdf</a></li>
<li>Notice 2024-80 (2025 Saver's Credit limits): <a href="https://www.irs.gov/pub/irs-drop/n-24-80.pdf">irs.gov/pub/irs-drop/n-24-80.pdf</a></li>
<li>26 U.S.C. §32, §25B, §24, §63: <a href="https://www.law.cornell.edu/uscode/text/26/32">law.cornell.edu/uscode/text/26</a></li>
<li>IRS Child Tax Credit (2025 amounts after Pub. L. 119-21): <a href="https://www.irs.gov/credits-deductions/individuals/child-tax-credit">irs.gov</a></li>
<li>Publication 596 (2025), EIC tables: <a href="https://www.irs.gov/publications/p596">irs.gov/publications/p596</a></li>
</ul>
</div></body></html>"""
OUTF.write_text(page, encoding="utf-8")
print("wrote", OUTF)
