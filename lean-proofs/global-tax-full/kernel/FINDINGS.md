# Kernel-level findings

### K1 The German tariff is not a bracket schedule (kernel gap, by design)
EStG § 32a (1) writes zones 2 and 3 as quadratics in the zvE ("(932,30 • y + 1 400) • y"), so its marginal rate rises
continuously; no `Schedule` (piecewise-constant marginal rates) can express it. The kernel takes such a tariff as a
plain `Int → Int`: every `Unit` theorem (`splitting_le_separate` etc.) is stated for any `f`, the surcharge and social
parts apply unchanged (fidelity: DE tariff, splitting, Soli and four contributions equal to `detax` on 2,926 units).
Of the existing five, only Germany needs this; France's quotient applies a bracket schedule per part.

### K2 Splitting needs monotonicity as well as convexity (theorem condition)
`splitting_le_separate` needs `Convex f` **and** `Monotone' f`: with an odd joint income the half is rounded down,
and for a convex but decreasing `f` (e.g. `f x = -x`) twice the tax on the rounded-down half exceeds the two
separate taxes by 1. Every progressive `Schedule` satisfies both (`ticks_convex`, `ticks_mono_of_progressive`).
Germany's cent-rounded formula is not exactly convex, which is why the five-country work found splitting can cost
€1 (`cmp/de`, `splitting_costs_one_euro`).

### K3 Joint aggregation on one schedule is a marriage penalty (generic)
`separate_le_joint`: for any convex tax function with no tax on nothing, `f a + f b ≤ f (a + b)`. A country that
aggregates a couple's income on the single schedule without widening the bands (or splitting) taxes marriage;
the filing-unit scanner measures it on the exes.

### K4 Surcharges with an exemption limit and no glide zone are notches (generic)
`Surcharge.exempt_notch`: one unit of base past the limit costs `rate × (limit + 1 − deduct)`; `glide_no_notch`: a
glide zone (Germany's Soli Milderungszone, Australia's Medicare levy shade-in) caps the step at the glide rate.

### K5 The OECD's take-home pay leaves some compulsory levies out (validation convention, 3 countries so far)
With each country's own mapping (`oecd_map.py`), the contract's net income differs from the OECD's take-home pay on
all eight household types in NZ, PL and MX, and agrees on all eight once the lines the OECD does not count are left
out (`harness/runs/oecd20/oecd_check_{NZ,PL,MX}.json`: take-home pay within 1 % 0/8 from the contract net, 8/8 from
the mapped lines). The country files name the items: PL F1 (the 3.65 % subkonto share of the pension contribution),
MX F1 (cesantía y vejez booked as a non-tax payment); NZ maps the ACC earners' levy to no OECD line. A reader comparing
"take-home pay" across countries from Taxing Wages should know the OECD's employee-contribution line is narrower than
what leaves the pay packet in these countries.

### K6 Lead (existing five, from the generic scanners): France's family-allowance resource test and dividends
`metr.py` finds, for a single parent with two children and 1 AW of dividends, €904 of net income lost for one more
euro of wages at €57,737 (detail lines `rni`, `afResources`), and €450 for couples; the five-country cliff scan did
not include investment income. Not yet checked against CSS art. L521-1, D521-1 and D521-3 (complément dégressif,
which is meant to smooth the threshold): recorded as a lead in `harness/search/REGRESSION.md`; France is read-only
for this project, so it stays a lead for the French model's owner.

### K7 Contribution ceilings make the combined top rate the wrong yardstick (scanner design)
In CZ, SE, NL and PL (among others) the combined marginal rate at 10 AW is lower than in the middle of the distribution because
employee contributions stop at a ceiling; a first version of the phase-out scanner therefore reported "rates above
the top rate" at high pay that were not withdrawals. The scanner now compares rates without employee contributions
(`top_rate_ex_social`); the ceiling itself is a kernel theorem (`Contribution.ticks_above_ceiling`).

### K8 The contract's `married` flag is not the law's couple everywhere (contract semantics)
`cmp/shared/CONTRACT.md` has one flag: married / civil partners. Canada (common-law partners, ITA s. 248(1)) and
Australia (de facto partners) treat a cohabiting couple as a couple for family benefits and couple-based credits. A
model reading `married: false` with two adults as two unrelated adults makes the filing-unit scanner report a large
"marriage penalty" (CA 16.0 %, AU 16.1 % of AW: e.g. CA at 0.8 AW, 50:50, two children: income tax 4,861 vs 440,
benefits 8,668 vs 18,847 CAD) that is really the difference between a couple and two singles. Proposal for the
contract (not changed: CONTRACT20 is binding): an optional `"cohabiting": true` field, read by the countries whose law
has de facto couples. Noted in LEADS.md for the Westminster models.

Resolved (2026-11-19): `catax` and `autax` now read `cohabiting` (and AU `deFacto`) as a couple; the unit scanner,
rerun on both, finds marriage changes nothing anywhere on the grid (`harness/search/results/{CA,AU}/unit.md`).

### K9 Eurostat's net-earnings series is not Taxing Wages from 2024, and its NET line does not always add up (referee quality; 38-country phase)
Eurostat's `earn_nt_net` ("built on the OECD-EC tax-benefit model") equals OECD Taxing Wages up to 2023 (Germany 2023,
single at 100 % AW: gross 60,428, income tax 10,166, employee contributions 12,354 in both) and its published NET equals
GRS − TAX − SOC + FAM in 363 of 363 cases for 2023. From 2024 (flag b, break in series) it uses its own average-worker
earnings (Germany 2025: 58,008 against the OECD's 66,700), books family benefits the OECD leaves out (German single
parent, two children: 12,432 against Kindergeld 6,120) and its published NET differs from the sum of its own lines in 74
of 351 cases for 2025 (all 13 Irish and all 13 Italian types; Czech single at 67 %: NET 381,326 against
442,859 − 35,589 − 51,372 = 355,898 CZK). On 11 EU models that reproduce Taxing Wages 2025, Eurostat 2025 agrees on income
tax within 1 % in 26 of 143 cases and on net income within 2 % of gross in 107 of 143
(`harness/runs/eurostat38/CALIBRATION.md`, `harness/eurostat_calibrate.py`). Consequence: for Bulgaria, Croatia,
Cyprus, Malta and Romania (not in Taxing Wages) Eurostat is a sanity bound, not a referee; the official calculators,
worked examples and EUROMOD parameters decide. Useful to researchers who take "tax wedge" or "net earnings" for
non-OECD EU members from Eurostat.

### K10 A zero band is never worth less than the same allowance given at the lowest rates (generic theorem, 1.2)
`lowBand_le_zeroBand`: for a progressive schedule, `s.ticks (x − a) ≤ s.ticks x − s.ticks a` for `0 ≤ a ≤ x`. A
Grundfreibetrag written as a zero band (DE, AT, LU) is worth the taxpayer's top marginal rate on `a`; Belgium's quotité
exemptée (CIR 92 art. 131, 134) is worth the lowest rates on `a`, the same for everyone who can use it. The difference
`s.ticks x − s.ticks a − s.ticks (x − a)` is what a higher earner gains from the zero-band design (toy: 25,000,000 ticks
= 2,500 units on income 60,000 with allowance 10,000, `examples/Parts38.lean`). The germanic family can state the BE
and AT/LU instances directly.

### K11 Open company-side data misstate the rate a one-person company pays (owner-manager scan; 38-country phase)
`harness/search/company38.py` first filled the 18 countries' company side from open data (OECD Corporate Tax
Statistics CIT_C 2025, the OECD dividend table, employer contributions implied by Taxing Wages or by Eurostat's labour
cost); the country agents then supplied statute-cited entries, and `company.json` records each difference
(`open_data_conflict`). The OECD's combined CIT rate is the top statutory rate, not the small company's: Slovakia 24 %
(revenue above 5 million EUR) against 21 % / 10 % (ZDP § 15), Croatia 18 % against 10 % below 1 million EUR (ZPDobit
čl. 28), Luxembourg 23.87 % against 21.73 % below 175,000 EUR, Belgium 25 % against 20 % on the first 100,000 EUR when
the director is paid 50,000 EUR; Cyprus is not in the table at all. Employer sides inferred from published household
figures miss ceilings (Greece) or take a referee's error with them (Bulgaria: a ceiling of 25,340 BGN implied by
Eurostat's 2025 labour cost against the statute's 48,435, the Eurostat parameter error of BG F1-F2). A cross-country
owner-manager comparison built on headline rates overstates the company route's cost in the small-company cases it is
meant for; the scan uses the statute-cited entries.
