"""Write the loopholes write-up (HTML) from the Lean search output (tools/out/loopholes.json).

    lake env lean LegalProofs/USTax/Loopholes/Search.lean
    python tools/loopholes_writeup.py [OUT.html]   (default: ~/Documents/html-reports/us-tax-loopholes-lean.html)
"""
import html, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTF = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents" / "html-reports" / "us-tax-loopholes-lean.html"
E = html.escape
D = json.loads((ROOT / "tools/out/loopholes.json").read_text())
SRC = (ROOT / "tools/tax_writeup.py").read_text(encoding="utf-8")
CSS = SRC[SRC.index("<link rel=stylesheet"):SRC.index("</style>")].replace("{{", "{").replace("}}", "}")
money = lambda v: f"${v:,.0f}"
mill = lambda v: f"${v / 1e6:,.1f}M" if v < 1e9 else f"${v / 1e9:,.2f}B"


def chart(series, xmin, xmax, ymin, ymax, xfmt, yfmt, xticks, yticks, label, w=900, h=330, step=False, marks=()):
    pl, pb, pt, pr = 78, 40, 18, 18
    X = lambda v: pl + (v - xmin) / (xmax - xmin) * (w - pl - pr)
    Y = lambda v: h - pb - (v - ymin) / (ymax - ymin) * (h - pb - pt)
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img" aria-label="{E(label)}">']
    for gy in yticks:
        o.append(f'<line x1="{pl}" x2="{w - pr}" y1="{Y(gy):.1f}" y2="{Y(gy):.1f}" class="grid"/>'
                 f'<text x="{pl - 8}" y="{Y(gy) + 4:.1f}" class="ax" text-anchor="end">{yfmt(gy)}</text>')
    for gx in xticks:
        o.append(f'<text x="{X(gx):.1f}" y="{h - 14}" class="ax" text-anchor="middle">{xfmt(gx)}</text>')
    for x, text in marks:
        o.append(f'<line x1="{X(x):.1f}" x2="{X(x):.1f}" y1="{pt}" y2="{h - pb}" stroke="currentColor" stroke-dasharray="5 5" opacity=".45"/>'
                 f'<text x="{X(x) + 6:.1f}" y="{pt + 14}" class="ax">{E(text)}</text>')
    for name, color, pts, at in series:
        if step:
            d = f"M{X(pts[0][0]):.1f},{Y(pts[0][1]):.1f}" + "".join(f"H{X(x):.1f}V{Y(y):.1f}" for x, y in pts[1:])
        else:
            d = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.1f},{Y(y):.1f}" for i, (x, y) in enumerate(pts))
        o.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.6"/>')
        if not name: continue
        lx, ly = pts[int(len(pts) * at)]
        o.append(f'<text x="{X(lx) + 6:.1f}" y="{Y(ly) - 9:.1f}" class="lab" fill="{color}">{E(name)}</text>')
    o.append("</svg>")
    return "".join(o)


# --- buy, borrow, die
life = D["life"]
life_chart = chart(
    [("heirs receive: sell to live", "#c2410c", [(r["year"], r["sellHeirs"]) for r in life], .88),
     ("heirs receive: borrow to live", "#059669", [(r["year"], r["borrowHeirs"]) for r in life], .55),
     ("debt", "#7c3aed", [(r["year"], r["debt"]) for r in life], .8)],
    0, 40, 0, 1.2e10, lambda v: f"year {v}", lambda v: f"${v / 1e9:.0f}B", range(0, 41, 10), [i * 2e9 for i in range(7)],
    "What the heirs receive, selling versus borrowing", marks=[(30, "death at year 30")])
y30 = life[30]

# --- GRAT surface
fs = D["grat"]["factors"]; G = D["grat"]["heirs"]; n = len(fs); gmax = max(max(r) for r in G)
cells = []; cw = 560 / n
for i, row in enumerate(G):
    for j, v in enumerate(row):
        t = (v / gmax) ** .6 if v else 0
        col = f"hsl(152,58%,{14 + 48 * t:.0f}%)" if v else "var(--code)"
        cells.append(f'<rect x="{120 + j * cw:.1f}" y="{20 + (n - 1 - i) * cw:.1f}" width="{cw + .4:.1f}" height="{cw + .4:.1f}" fill="{col}"><title>year 1 {fs[i] / 100 - 100:+.0f}%, year 2 {fs[j] / 100 - 100:+.0f}%: heirs {money(v)}</title></rect>')
ticks = "".join(f'<text x="{120 + j * cw + cw / 2:.1f}" y="{20 + n * cw + 18:.1f}" class="ax" text-anchor="middle">{fs[j] / 100 - 100:+.0f}%</text>' for j in range(0, n, 3))
ticks += "".join(f'<text x="112" y="{20 + (n - 1 - i) * cw + cw / 2 + 4:.1f}" class="ax" text-anchor="end">{fs[i] / 100 - 100:+.0f}%</text>' for i in range(0, n, 3))
grat_chart = (f'<svg viewBox="0 0 900 640" class="chart" role="img" aria-label="Heirs receive, by growth in each GRAT year">{"".join(cells)}{ticks}'
              f'<text x="400" y="{20 + n * cw + 40:.0f}" class="ax" text-anchor="middle">growth in year 2</text>'
              f'<text x="24" y="320" class="ax" transform="rotate(-90 24 320)" text-anchor="middle">growth in year 1</text>'
              f'<text x="700" y="80" class="lab">gift tax: $0</text><text x="700" y="102" class="ax">in every cell</text>'
              f'<text x="700" y="150" class="lab" fill="#059669">green: passes to heirs</text><text x="700" y="172" class="ax">up to {mill(gmax)}</text>'
              f'<text x="700" y="220" class="lab">grey: a wash</text><text x="700" y="242" class="ax">all back to the grantor</text></svg>')

# --- QSBS
q = D["qsbs"]
QC = ["#94a3b8", "#2563eb", "#059669", "#c2410c", "#7c3aed"]
qs_legend = " · ".join(f'<b style="color:{c}">{mill(r["exit"])} exit</b>' for r, c in zip(q, QC))
qs_chart = chart([("", c, [(k + 1, t) for k, t in enumerate(r["tax"])], .05)
                  for r, c in zip(q, ["#94a3b8", "#2563eb", "#059669", "#c2410c", "#7c3aed"])],
                 1, 21, 0, 1.2e8, lambda v: f"{v}", lambda v: f"${v / 1e6:.0f}M", [1, 5, 10, 15, 20], [i * 2e7 for i in range(7)],
                 "Federal tax on a founder-stock sale by number of separate taxpayers", step=True)

# --- SALT marginal rate
salt_chart = chart([("federal marginal rate", "#c2410c", [(w, r / 100) for w, r in D["salt"]], .5)],
                   300000, 800000, 30, 50, lambda v: f"${v // 1000}k", lambda v: f"{v:.0f}%", range(300000, 800001, 100000), range(30, 51, 5),
                   "Federal marginal income tax rate on wages, single filer in a high-tax state", step=True,
                   marks=[(500000, "$500k: cap starts to shrink"), (600000, "$600k")])

# --- ACA
aca_chart = chart([("premium tax credit", "#2563eb", [(m, c) for m, c in D["aca"]], .2)],
                  70000, 110000, 0, 30000, lambda v: f"${v // 1000}k", lambda v: f"${v / 1000:.0f}k", range(70000, 110001, 10000), range(0, 30001, 5000),
                  "Premium tax credit for a married couple aged 60, by income", step=True, marks=[(84600, "400% of poverty: $84,600")])

bil = D["billion"]; th = D["thiel"]

STORIES = [
 ("roth", "A $5 billion retirement account", "§408A", f"""
<p>A Roth IRA caps what goes in, not what it becomes. The 1999 limit was $2,000. ProPublica reported in 2021, from IRS
records, that Peter Thiel used about $1,700 of it to buy 1.7 million PayPal founder shares, and that the account held about
$5 billion by 2019. A qualified distribution from a Roth is not income (§408A(d)(1)), so none of that growth will ever be
taxed.</p>
<pre>theorem roth_growth_never_taxed (cost value : Nat) : cashOutTax .roth cost value = 0
theorem limit_ignores_value (limit cost value₁ value₂ : Nat) (h : contributionAllowed limit cost = true) : …
theorem thiel_roth :
    cashOutTax .taxable 1700 5000000000 = 1189999595 ∧ cashOutTax .roth 1700 5000000000 = 0</pre>
<p>The first two hold for every amount: the limit test never looks at value, and no value is ever taxed. The third puts
a number on it: in a taxable account the same gain would owe <b>{money(th['taxable'])}</b> at today's top rates.</p>
<p class=m>Objection: the contribution has to be of shares bought at fair value, or it is a prohibited transaction
(§4975) that can disqualify the account. PayPal's pre-IPO filing described the founders' shares as sold "below fair
value"; the IRS has never publicly challenged the account.</p>"""),
 ("bbd", "Buy, borrow, die", "§§1001, 1014", f"""
<p>Three ordinary rules: a gain is taxed only when you sell (§1001); a loan is not income; and inherited property takes
its value at death as its basis (§1014). Together: never sell, borrow against the shares to live, and die holding them.
The gain is taxed by no one.</p>
<pre>theorem borrow_plan_no_income_tax (spend growth rate years : Nat) (s : Life) (h : s.incomeTax = 0) :
    (live (borrowYear spend growth rate) years s).incomeTax = 0
theorem step_up_erases (h : Holding) : gainOnSale (inherit h) = 0</pre>
<p>Both are proved for every spending need, growth rate, interest rate, life span and holding, by induction over the
years. Then the model runs a founder with $1 billion of shares who spends $20 million a year for 30 years (shares grow
7%, the loan costs 5%):</p>
{life_chart}
<p>Selling pays {mill(y30['sellTax'])} of income tax over the life; borrowing pays none. At death the borrower's heirs get
<b>{mill(y30['borrowHeirs'])}</b> against {mill(y30['sellHeirs'])}: {mill(y30['borrowHeirs'] - y30['sellHeirs'])} more, even
after repaying {mill(y30['debt'])} of debt. The estate tax is larger, because the estate is: that is what the next
structure is for.</p>"""),
 ("grat", "A bet you cannot lose", "§2702 · Walton v. Commissioner", f"""
<p>A grantor retained annuity trust pays the grantor a fixed annuity for a few years and leaves the rest to the heirs.
The gift is valued on day one: the assets minus the present value of the annuity at the §7520 rate. In <i>Walton v.
Commissioner</i> (115 T.C. 589, 2000) the Tax Court accepted an annuity worth the whole contribution, so the gift was zero;
the IRS conceded in Notice 2003-72. If the assets beat the §7520 rate, the excess goes to the heirs free of gift and
estate tax. If not, everything comes back to the grantor. Rolled every two years, it catches every good run.</p>
<pre>theorem zero_gift (P r : Nat) : gift P r = 0
theorem nothing_leaks (P r f₁ f₂ : Nat) : … toGrantor + toHeirs = everything the trust paid out
theorem heads : run 100000000 560 14000 13000 = ⟨108476266, 57252294⟩ ∧ gift 100000000 560 = 0
theorem tails : run 100000000 560 8000 9000 = ⟨77423813, 0⟩</pre>
<p><code>zero_gift</code> holds for every contribution and every §7520 rate: the annuity is chosen so its present value
covers the contribution, and the proof shows the gift is exactly zero after rounding. The map shows a two-year, $100
million GRAT at the October 2026 rate (5.6%) under every combination of returns from −30% to +60%:</p>
{grat_chart}
<p>Two good years (+40%, +30%) pass <b>$57.3M</b> to the heirs, sparing {mill(57252294 * .4)} of estate tax. Two bad
years return everything. There is no cell where the grantor loses anything but fees.</p>"""),
 ("qsbs", "Ten trusts, no tax", "§1202 · §643(f)", f"""
<p>Gain on qualifying startup stock held five years is excluded up to a cap per taxpayer: for stock issued after 4 July
2025, the greater of $15 million or ten times basis (§1202(b), as amended in 2025). A non-grantor trust is its own
taxpayer, and a gift keeps the stock's status (§1202(h)). So founders give shares to trusts before an exit, and each trust
takes its own $15 million. The limit is §643(f): trusts with the same grantor and primary beneficiary, set up mainly to
avoid tax, are treated as one.</p>
<pre>theorem under_cap_free (gain basis : Nat) (h : gain ≤ cap basis) : taxOn gain basis = 0
theorem merge_costs (g₁ g₂ : Nat) : taxOn g₁ 0 + taxOn g₂ 0 ≤ taxOn (g₁ + g₂) 0
theorem stacking : saleTax alone = 32130000 ∧ saleTax stacked = 0 ∧ saleTax naive = 21420000</pre>
<p><code>merge_costs</code> is the engine, for all amounts: one taxpayer never owes less than two. A $150 million exit
owes <b>$32.13M</b> held alone and <b>$0</b> spread across founder, spouse and eight trusts, each with a different
grantor–beneficiary pair. Draft the eight trusts all for one child and §643(f) folds them into two: $21.42M is due after
all.</p>
{qs_chart}
<p class=m>Tax on a sale of founder stock (basis zero) split evenly across 1 to 21 separate taxpayers: {qs_legend}.</p>"""),
 ("salt", "The 45.5% band, and the way round it", "§164(b)(7) · Notice 2020-75", f"""
<p>The 2025 Act raised the cap on deducting state and local taxes to $40,000, but cut it by 30% of income above
$500,000, down to $10,000. Inside that band each extra $1,000 of pay also takes $300 of deduction: at the 35% rate, a
45.5% marginal rate.</p>
<pre>theorem torpedo (x : Nat) (h₁ : 500000 ≤ x) (h₂ : x + 1000 ≤ 600000) :
    saltCap (x + 1000) + 300 = saltCap x
theorem torpedo_band : … every $1,000 step from $500,000 to $600,000 costs $454–$456
theorem ptet_saves : earner 1000000 - ownerTax 1000000 100000 35000 = 33300</pre>
{salt_chart}
<p class=m>Single filer, state income tax 10% of wages, $35,000 of other itemised deductions.</p>
<p>The cap only binds taxes an individual pays. If a partnership or S corporation pays the state's tax itself, it is a
business deduction, outside the cap; the IRS accepted these "PTET" elections in Notice 2020-75 and the 2025 Act left
them alone. Same $1 million of income, same $100,000 of state tax: the employee deducts $10,000, the owner deducts all of
it, and pays <b>$33,300</b> less federal tax.</p>"""),
 ("aca", "The $23,402 dollar", "§36B (2026)", f"""
<p>The extra health-insurance subsidies of 2021–2025 expired on 31 December 2025. From 2026 the premium tax credit stops
completely above 400% of the poverty line. A married couple aged 60 faces a benchmark plan costing about $31,828 a year;
at $84,600 of income they pay 9.96% of it and the credit pays the rest. At $84,601 they pay all of it.</p>
<pre>theorem none_above (magi : Nat) (h : 4 * fplTwo < magi) : credit magi = 0
theorem cliff : credit 84600 = 23402 ∧ credit 84601 = 0
theorem ira_dollar : credit (magi 84601 1) - credit (magi 84601 0) = 23402</pre>
{aca_chart}
<p>Income here is modified AGI, which a traditional IRA or HSA contribution lowers. So the couple one dollar over can put
<b>one dollar</b> in an IRA and get $23,402 back; a couple earning $100,000 who save $15,400 between them (within the
2026 limits after age 50) recover the whole credit and keep their savings.</p>
<p class=m>This one is a loophole for the middle, not the top: it rewards whoever knows the rule, and it punishes,
by $23,402, the couple whose raise was one dollar too big.</p>"""),
]

toc = "".join(f'<li><a href="#{k}">{E(t)}</a> <span class=m>{E(c)}</span></li>' for k, t, c, _ in STORIES)
body = "".join(f'<h2 id="{k}">{i + 1}. {E(t)}</h2><h3>{E(c)}</h3>{b}' for i, (k, t, c, b) in enumerate(STORIES))

page = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Tax Loopholes, Proved</title>
{CSS}
.big{{font:700 64px/1 'Source Serif 4',serif;margin:6px 0}}.vs{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:26px 0}}
.vs .k b{{font-size:42px}}ol.toc li{{margin:4px 0}}
@media (max-width:560px){{.vs{{grid-template-columns:1fr}}h1{{font-size:36px}}}}
</style></head><body><div class=w>
<p class=m>Lean 4 · global-law / lean-proofs · federal tax 2025–2026</p>
<h1>Six loopholes in the US tax code, proved</h1>
<p class=lede>Two people each make a billion dollars. One is paid it. The other owns it. We wrote the rules that decide
what each owes as Lean code, and had Lean prove, for every amount and not for one example, the facts each loophole rests
on. Then we ran them.</p>
<div class=vs>
<div class=k><span>a billion dollars of pay</span><b>{money(bil['salary'])}</b><span>federal income and payroll tax: <code>salary_billion</code></span></div>
<div class=k><span>a billion dollars of founder's stock</span><b>{money(bil['founder'])}</b><span>federal income tax: <code>founder_billion</code></span></div>
</div>
<p>The founder's zero is not one trick. It is the stories below stacked: shares that are never sold and are borrowed
against (no gain is realised), the part that is sold spread across trusts under the startup-stock cap, growth handed to
heirs through annuity trusts with a gift value of zero, and a basis reset to market value at death. Each piece is lawful
and in use; each is a theorem in <code>LegalProofs/USTax/Loopholes/</code>.</p>
<ol class=toc>{toc}</ol>
{body}
<h2>Why prove it</h2>
<p>Every number here could come from a spreadsheet. What a spreadsheet cannot give is the general statements: that the
borrowing plan owes nothing <i>whatever</i> the rates and the years, that the GRAT's gift is zero <i>for every</i> amount
and §7520 rate, that merging taxpayers <i>never</i> lowers the tax, that <i>every</i> dollar in the SALT band costs
45.5 cents. Those are what make a loophole a loophole and not a coincidence of one example, and they are exactly what
Lean checks. The worked figures are then evaluated by the same definitions, and re-checked by the kernel on every build.</p>

<h2>What this does not show</h2>
<ul>
<li>Each model is the core of the rule, not all of it: no state tax (except the SALT example's assumed rate), no
alternative minimum tax, no §199A, no gift-tax use of the trusts in the QSBS example (gifts to non-grantor trusts use
lifetime exemption), no generation-skipping tax, and in the founder's life, a basis of zero and steady returns.</li>
<li>Courts and the IRS can attack the edges: §4975 for the Roth, step-transaction and §643(f) for stacking, and
economic-substance doctrine for all of them. The theorems say what follows if the structure is respected.</li>
<li>Figures that are reported (the Thiel account), assumed (returns, interest, the benchmark premium) or announced
(the §7520 rate) are marked as such in each file. This is research into how the code works, not tax advice.</li>
</ul>

<h2>Reproduce</h2>
<pre>cd lean-proofs
lake build                                              # proves everything in LegalProofs/USTax/Loopholes
lake env lean LegalProofs/USTax/Loopholes/Search.lean   # maps each loophole: tools/out/loopholes.json
python tools/loopholes_writeup.py                       # this page</pre>

<h3>Sources</h3>
<ul class=m>
<li>ProPublica, "Lord of the Roths" (2021): <a href="https://www.propublica.org/article/lord-of-the-roths-how-tech-mogul-peter-thiel-turned-a-retirement-account-for-the-middle-class-into-a-5-billion-dollar-tax-free-piggy-bank">propublica.org</a></li>
<li><i>Walton v. Commissioner</i>, 115 T.C. 589 (2000): <a href="https://en.wikipedia.org/wiki/Walton_v._Commissioner">summary</a>; Notice 2003-72</li>
<li>§7520 rates, IRS: <a href="https://www.irs.gov/businesses/small-businesses-self-employed/section-7520-interest-rates">irs.gov</a> (October 2026: 5.6%)</li>
<li>§1202 after the 2025 Act; stacking and §643(f): <a href="https://www.foley.com/insights/publications/2026/05/qsbs-stacking-leveraging-gifts-and-trusts-for-additional-section-1202-exclusions/">Foley</a>,
<a href="https://www.fidelity.com/learning-center/wealth-management-insights/using-trusts-to-maximize-salt-deduction">Fidelity</a></li>
<li>SALT cap and PTET after the 2025 Act: <a href="https://www.cooley.com/news/insight/2025/2025-07-15-federal-tax-legislation-extends-and-increases-salt-cap-preserves-ptet-workarounds">Cooley</a>;
the 45.5% band: <a href="https://www.nbcnews.com/business/personal-finance/trumps-big-beautiful-bill-deliver-salt-torpedo-high-earners-rcna218328">NBC News</a></li>
<li>2026 premium tax credit: Rev. Proc. 2025-25 (<a href="https://www.currentfederaltaxdevelopments.com/blog/2025/7/18/rev-proc-2025-25-a-technical-review-of-2026-premium-tax-credit-and-affordability-adjustments">review</a>);
benchmark premium at 60: <a href="https://www.kff.org/affordable-care-act/how-will-the-loss-of-enhanced-premium-tax-credits-affect-older-adults/">KFF</a></li>
<li>26 U.S.C. §§408A, 1001, 1014, 1202, 164, 2702, 36B, 643: <a href="https://www.law.cornell.edu/uscode/text/26">law.cornell.edu</a></li>
</ul>
</div></body></html>"""
OUTF.write_text(page, encoding="utf-8")
print("wrote", OUTF)
