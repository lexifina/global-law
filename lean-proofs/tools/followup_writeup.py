"""Write the follow-up write-up (grantor trusts and wash sales) as HTML.

    python tools/followup_writeup.py [OUT.html]   (default: ~/Documents/html-reports/lean-trusts-wash-sales.html)

Figures are the ones the Lean files print and re-check (Trusts/Search.lean, Trusts/Found.lean, WashSale/Search.lean,
WashSale/Found.lean).
"""
import html, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTF = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents" / "html-reports" / "lean-trusts-wash-sales.html"
E = html.escape
SRC = (ROOT / "tools/tax_writeup.py").read_text(encoding="utf-8")
CSS = SRC[SRC.index("<link rel=stylesheet"):SRC.index("</style>")].replace("{{", "{").replace("}}", "}")
REPO = "https://github.com/lexifina/global-law/tree/main/lean-proofs/LegalProofs/USTax"


def hbars(rows, label, fmt, w=900, unit_max=None):
    """Horizontal bars: rows of (name, value, colour, note)."""
    top, rowh, left, right = 14, 46, 330, 150
    h = top * 2 + rowh * len(rows)
    vmax = unit_max or max(v for _, v, _, _ in rows)
    X = lambda v: left + v / vmax * (w - left - right)
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img" aria-label="{E(label)}">']
    for i, (name, v, col, note) in enumerate(rows):
        y = top + i * rowh
        o.append(f'<text x="{left - 12}" y="{y + 20}" class="ax" text-anchor="end" style="font-size:13.5px;fill:currentColor">{E(name)}</text>')
        if note:
            o.append(f'<text x="{left - 12}" y="{y + 36}" class="ax" text-anchor="end">{E(note)}</text>')
        o.append(f'<rect x="{left}" y="{y + 6}" width="{max(1, X(v) - left):.1f}" height="24" rx="3" fill="{col}"/>')
        o.append(f'<text x="{X(v) + 8:.1f}" y="{y + 23}" class="lab" fill="{col}">{E(fmt(v))}</text>')
    o.append("</svg>")
    return "".join(o)


plans = hbars([
    ("Sell to a defective trust, swap back", 259488570, "#059669", "the search's best plan"),
    ("Sell to a defective trust, no swap", 205213184, "#34d399", "heirs pay tax on the old basis"),
    ("Sell to a trust that is neither", 191701578, "#2563eb", "gain taxed on the sale"),
    ("Keep the asset", 177212259, "#64748b", "the baseline"),
    ("Sell to a trap trust", 159525459, "#c2410c", "taxed on the sale, still in the estate"),
], "What the heirs keep under each plan", lambda v: f"${v / 1e6:,.1f}M")

statuses = hbars([
    ("Defective", 9648, "#059669", "income tax: grantor's · estate: out"),
    ("Incomplete", 8741, "#64748b", "the grantor's for both"),
    ("Complete", 1378, "#2563eb", "the grantor's for neither"),
    ("Trap", 333, "#c2410c", "estate: in · income tax: not the grantor's"),
], "Trust instruments by how the two tests come out", lambda v: f"{v:,}")

page = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Trusts and Wash Sales</title>
{CSS}
td.r,th.r{{text-align:right}}.ok{{color:#059669;font-weight:600}}.no{{color:#c2410c;font-weight:600}}
</style></head><body><div class=w>
<p class=m>Lean 4 · global-law / lean-proofs · follow-up to the retirement-account search</p>
<h1>Two more gaps in the tax code, found by search and checked in Lean</h1>
<p class=lede>The retirement-account work showed that a blind search over rules written straight from the statute can
find a known loophole without being told about it, and that Lean can prove things about every possible plan rather
than one example. This page applies the same method to two other places where the Code&apos;s provisions do not quite
line up: the two tests of who owns a trust, and the reach of the wash-sale rule.</p>
<div class=grid4>
<div class=k><b>9,648</b><span>of 20,100 trust instruments that the income tax treats as the grantor&apos;s while the estate tax does not</span></div>
<div class=k><b>+$82.3M</b><span>for the heirs from the search&apos;s best trust plan, against keeping a $50M stake for 20 years</span></div>
<div class=k><b>333</b><span>trap instruments: in the estate, but not the grantor&apos;s for income tax</span></div>
<div class=k><b>3</b><span>ways the search found to take a loss without leaving the market</span></div>
</div>

<h2>1. Who owns a trust? Two tests that disagree</h2>
<p>The income tax and the estate tax both ask whether a trust is still, in substance, the grantor&apos;s, but they ask
it in different parts of the Code and in different words. The grantor trust rules (§§672–677) make the grantor the
owner for income tax if the grantor or a nonadverse party holds any of a list of powers: to revoke, to apply income for
the grantor or the grantor&apos;s spouse, to pay premiums on insurance on the grantor&apos;s life, to borrow without
adequate security, to reacquire property by substituting property of equal value, and others. The estate tax
(§§2036–2038, 2042) brings trust property into the estate if the grantor kept the income, a power over who enjoys
the property, a power to alter or revoke, a reversion, or the incidents of ownership of a policy on the grantor&apos;s
life.</p>
<p>We wrote each test from its own provisions, over a single power described by what it does, who holds it, whether
in a fiduciary capacity, and whether it is limited by an ascertainable standard. Neither test refers to the other.
Applied to every instrument of one or two powers, 20,100 in all, they disagree on almost half:</p>
{statuses}
<p class=m>Counts from <code>Trusts/Search.lean</code>. A trust is &quot;defective&quot; in practitioners&apos; terms when
the grantor pays its income tax but its property is outside the estate.</p>
<p>The defective trusts include those with a power, held by the grantor outside any fiduciary capacity, to take back
trust property by substituting property of equal value (§675(4)(C); the IRS ruled in Rev. Rul. 2008-22 that the power
does not bring the property into the estate), and those where income may be applied to premiums on the grantor&apos;s
life (§677(a)(3); paying premiums is not an incident of ownership under §2042). The cleanest trap is a grantor who, as
trustee, votes the shares of a company the grantor controls: §2036(b) brings the shares into the estate whatever the
capacity, but §675(4)(A) makes the grantor the income-tax owner only outside a fiduciary capacity.</p>

<h3>What the mismatch is worth</h3>
<p>Which status a trust has decides what happens when the grantor sells it an appreciating asset for a note. If the
trust is the grantor&apos;s for income tax, grantor and trust are one taxpayer: the sale is not a sale and the interest
is not income (Rev. Rul. 85-13), and the grantor keeps paying the tax on the trust&apos;s income, which is not treated as
a further gift (Rev. Rul. 2004-64). If the trust is outside the estate, its growth never reaches the estate tax. A
substitution power adds one more move: just before death the grantor can take the asset back for cash of equal value,
so that the asset is in the estate and takes a basis equal to its value (§1014), while the cash stays in the trust.</p>
<p>The search scored every plan (keep the asset, sell it to the trust, sell it and swap it back) on every instrument,
for a founder&apos;s $50 million stake with a $5 million basis, growing 8% a year with a 3% taxable yield, held for 20
years, with a note at 4.6% and the estate-tax exclusion already used. The best plan it found is the one estate planners
use: a sale to a defective trust with a substitution power, then the swap.</p>
{plans}
<p class=m>What the heirs keep after estate tax and after capital-gains tax on selling what they inherit. Every figure
is re-checked by Lean in <code>Trusts/Found.lean</code>.</p>

<h3>What is proved, for every path of returns</h3>
<p>The figures above depend on the assumed returns. The theorems in <code>Trusts/Sale.lean</code> do not: they hold for
every sequence of yearly growth and yield, positive or negative, of any length.</p>
<ul>
<li><b>The defective trust is income-tax neutral</b> (<code>defective_neutral</code>). On any path, selling the asset to a
defective trust leaves the family exactly as rich, after exactly the same income tax, as keeping it.</li>
<li><b>Everything the trust gains leaves the estate</b> (<code>estate_shrinks</code>). The estate is smaller by exactly what
the trust holds net of the note.</li>
<li><b>With the swap, the heirs never do worse than keeping the asset</b> (<code>swap_never_worse</code>), whenever the
trust ends with anything net of the note; the difference is exactly the estate tax saved.</li>
<li><b>Without the swap, the cost is precisely the old basis</b> (<code>no_swap_cost</code>): the capital-gains tax on the
asset&apos;s growth over the grantor&apos;s original basis.</li>
<li><b>The trap is never better than doing nothing</b> (<code>trap_never_better</code>). The sale&apos;s gain and the
interest are taxed while nothing leaves the estate.</li>
</ul>
<p>The proofs go by induction over the years. The trap theorem needed one fact about the estate tax worked out by hand,
that the heirs&apos; share after estate tax never falls when the estate grows, which holds at the statutory 40% rate the
model uses.</p>

<h2>2. The wash-sale rule&apos;s reach</h2>
<p>A loss on selling property is deductible (§165). §1091 takes it away, for now, in one case: a loss on a sale of
stock or securities where the taxpayer acquired substantially identical stock or securities within 30 days before or
after. The loss is added to the basis of the replacement (§1091(d)), so it comes back when that is sold. We wrote an
executor that applies those rules to any sequence of trades, matching each loss sale to a replacement inside the 61-day
window if there is one.</p>
<p>Three things are proved for every sequence of trades (<code>WashSale/Theorems.lean</code>):</p>
<ul>
<li><b>Deferral, not forgiveness</b> (<code>deferral_not_forgiveness</code>). Once every position is closed, the gain
recognised equals cash in minus cash out: every loss the rule disallowed along the way has come back.</li>
<li><b>The rule&apos;s reach</b> (<code>outside_scope</code>). Assets that are not stock or securities never have a loss
disallowed, however the trades are timed.</li>
<li><b>The window</b> (<code>outside_window</code>). An acquisition 31 or more days from the sale is never treated as a
replacement.</li>
</ul>
<p>The search was then given an investor holding three positions at a loss (an index fund, a single stock and
bitcoin), plus a second index fund that tracks a different index of the same market and a bitcoin exchange-traded
fund. It tried every sequence of up to four trades on two trading days 31 days apart, kept those that never left the
investor without exposure to each market, and looked for the largest loss recognised, then the least capital tied
up.</p>
<table>
<tr><th>Position</th><th>What the search found</th><th class=r>Loss recognised</th><th class=r>Sell and buy back same day</th></tr>
<tr><td>Index fund A ($3,000 loss)</td><td>Sell A, buy fund B on the same day</td><td class="r ok">$3,000</td><td class="r no">disallowed</td></tr>
<tr><td>Stock X ($4,000 loss)</td><td>Buy a second share, wait 31 days, sell the old one</td><td class="r ok">$4,000</td><td class="r no">disallowed</td></tr>
<tr><td>Bitcoin ($5,000 loss)</td><td>Sell and buy back on the same day</td><td class="r ok">$5,000</td><td class="r ok">allowed</td></tr>
<tr><td>Bitcoin ETF ($5,000 loss)</td><td>(the same same-day trade)</td><td class=r>—</td><td class="r no">disallowed</td></tr>
</table>
<p class=m>Each row is re-run by the kernel in <code>WashSale/Found.lean</code>.</p>
<p>The fund switch works because the model treats two funds tracking different indexes as not substantially identical.
The IRS has never said whether they are, so this is an input, not a result. The stock has no substitute, so the only
way to stay invested is to hold two shares for 31 days. Bitcoin is property, not a security (IRS Notice 2014-21), so
the rule does not reach it at all, while the same trade in a bitcoin ETF, whose shares are securities, is caught. Bills
to extend §1091 to digital assets have been introduced several times since 2021, and one (H.R. 10357) was reported to
have cleared the Ways and Means Committee in September 2026, with an effective date of 14 September 2026; none is law
as of November 2026.</p>

<h2>What this does not show</h2>
<ul>
<li>The trust model covers one power or two at a time, and simplifies: §674&apos;s exceptions are reduced to an
ascertainable standard and independent trustees, state-law questions (whether the grantor&apos;s creditors can reach
the trust) are assumed, and the spouse is treated as the grantor where §672(e) says so.</li>
<li>Practitioners do not rely on the substitution power alone. Whether a power is held &quot;in a nonfiduciary
capacity&quot; is a question of fact, and Rev. Rul. 2008-22 protects it only where the trustee must confirm that the
values are equal and the power cannot shift benefits among beneficiaries.</li>
<li>The trust figures use one set of assumed returns and rates, a note at 4.6%, and an exclusion already used; the
swap assumes the grantor can raise cash (or substitute another asset) equal to the asset&apos;s value.</li>
<li>The wash-sale executor trades one unit at a time, identifies sales first in, first out, and matches replacements in
the order they appear; the regulations&apos; rules for matching partial lots are more detailed.</li>
<li>A proof shows that the stated result follows from the rules as written in the model. Each rule was checked by hand
against the Code and the rulings cited; that check is the part to question. This is research, not tax advice.</li>
</ul>

<h2>Reproduce</h2>
<pre>cd lean-proofs
lake build                                         # every proof and every re-checked figure
lake env lean LegalProofs/USTax/Trusts/Search.lean   # the trust search
lake env lean LegalProofs/USTax/WashSale/Search.lean # the wash-sale search
python tools/followup_writeup.py                   # this page</pre>
<p class=m>Code: <a href="{REPO}/Trusts">Trusts</a> · <a href="{REPO}/WashSale">WashSale</a> (in lexifina/global-law, once pushed).</p>

<h3>Sources</h3>
<ul class=m>
<li>26 U.S.C. §§672–677, 2036–2038, 2042, 1014, 1091, 165: <a href="https://www.law.cornell.edu/uscode/text/26">law.cornell.edu/uscode/text/26</a></li>
<li>Rev. Rul. 2008-22, 2008-16 I.R.B. 796 (substitution power and estate inclusion): <a href="https://webarchive.library.unt.edu/web/20090507055801/http:/www.irs.gov/irb/2008-16_IRB/ar11.html">IRS Internal Revenue Bulletin (archived)</a></li>
<li>Rev. Rul. 85-13 (transactions between a grantor and a grantor trust disregarded) and Rev. Rul. 2004-64 (grantor&apos;s payment of the trust&apos;s income tax not a gift)</li>
<li>Rev. Rul. 2011-28 (substitution power over a life-insurance policy not an incident of ownership): <a href="https://plannedgiving.mssu.edu/giftlawpro/glawpro_revrul.jsp?ID=84">summary</a></li>
<li>IRS Notice 2014-21 (virtual currency treated as property): <a href="https://www.irs.gov/pub/irs-drop/n-14-21.pdf">irs.gov/pub/irs-drop/n-14-21.pdf</a></li>
<li>The crypto wash-sale gap in 2026: <a href="https://gordonlaw.com/learn/crypto-wash-sale-rule-in-2026-is-the-loophole-finally-closed/">Gordon Law</a>, <a href="https://www.coincenter.org/the-wash-sale-rule-would-break-crypto-tax-compliance/">Coin Center</a></li>
</ul>
</div></body></html>"""
OUTF.write_text(page, encoding="utf-8")
print("wrote", OUTF)
