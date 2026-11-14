# RealEstate: findings

File: `LegalProofs/USTax/Hunt/RealEstate.lean`. Run from `lean-proofs/`:

- `lake env lean LegalProofs/USTax/Hunt/RealEstate.lean` — quick run (config C, 8 years, about 50 s).
- `HUNT_CFG=A|B|C|D|E|F|G` — the 12-year runs. A, B, E take 1–2 minutes alone. C, D, G are larger: add
  `HUNT_START="dwelling, SL"` (or `"dwelling, bonus"`, `"factory, QPP"`, ...) to run one purchase variant at a time.
- `HUNT_PV=1` ranks by tax discounted at 5% a year instead of nominal tax. `HUNT_CFG=T` prints year-by-year traces.
- Outputs used below are in `tools/hunt/out/RealEstate/` (`run_*.txt`, `run2.txt`, `trace.txt`).

## Set-up

Married couple, joint return, wages $300,000 a year (E: $120,000; F: $600,000). They buy a $1,000,000 property
(F: $4,000,000) with 70% interest-only qualified nonrecourse debt, hold it or a like-kind replacement for 12 years,
then sell or die. Net operating income is 4% of value, appreciation 4% a year, whatever the use, so every plan has
the same pre-tax economics and only tax differs. Baseline: let to a tenant, straight line, sell in year 12:
**$759,899** lifetime tax (wages alone: $601,608). Baseline ending in death: **$601,608**.
Figures are 2025 (joint brackets, $31,500 standard deduction); unindexed statutory amounts as enacted. No inflation.
The main ranking is nominal tax, with no time value of money; that matters and is called out below.

## Provisions encoded (text read for each)

§1(h)(1), (3), (6) (25% gain); §1(j) rates; §121(a), (b)(1)–(3), (b)(5), (d)(6), (d)(10); §163(h)(3) (as an itemised
deduction with $10,000 of taxes); §168(a)–(c), (e)(2), (e)(6), (k)(1), (k)(2)(A), (k)(7), (n)(1), (n)(2), (n)(5);
§172(a)(2) (80%); §280A(c)(5), (d)(1), (e)(1); §461(l)(1)–(3), (6); §465(b)(6) (never binds here); §469(a), (b),
(c)(1), (c)(2), (c)(7), (f)(1), (g)(1), (g)(2), (h)(1), (i)(1)–(3), (i)(6), (j)(8), (j)(10); §1014(a);
§1031(a), (b), (d); §1231(a); §1245(a)(1)–(3), (b)(2), (b)(4); §1250(a)(1), (b)(1), (b)(3), (c), (d)(2), (d)(4);
§1411(a)–(c).

Regulation-based move, labelled in the file (`Cfg.regs`): Temp. Reg. §1.469-1T(e)(3)(ii)(A), the 7-day rule. By
statute alone (§469(j)(8), (c)(2)) every letting is a rental activity and passive; run A is statute only.

Read but not made moves, with the reason:
- §163(j) and its real-property election: §163(j)(3) exempts the taxpayer, so the election only costs (ADS).
- §163(d): rental interest is not investment interest (§163(d)(4)(D), (5)(A)(ii)).
- §179: nothing here beats §168(k) at 100%; §179(b)(3) would only restrict. (See drafting gaps for its reach to QPP.)
- §280A(g): the excluded rent has no tax effect to rank; it is the known "14-day" exclusion.
- §453: defers gain but §453(i) takes recapture up front. Not modelled; see plan 4.
- §1400Z-2: the local text is the version in force for investments through 2026 (deferral ends 31 Dec 2026); the
  2025 amendments apply to later investments and are not in the section text. Not modelled.
- §1402 self-employment tax: not modelled; it could only add tax to short-stay and production uses.

Reading switches: `relax121` (Chief Counsel Advice 201428008 reading of §469(g) where §121 excludes gain; off =
suspended losses are lost), `qppGap` (literal reading of §1245(a)(3)(G), below).

## Search size

Moves per year: 7 uses × (continue / sell / sell without §121 / die) plus a §1031 exchange; at most 2 changes of use
and 1 exchange; 6 purchase variants (dwelling or production building; §168(k) or election out; §168(n) election).

| run | what | positions | finished plans | families |
|---|---|---|---|---|
| A | statute only | 167,873 | 71,971 | 272 |
| B | + 7-day regulation | 311,911 | 139,285 | 276 |
| C | + spouse can meet §469(c)(7)(B) | 659,550 | 292,430 | 488 |
| D | + CCA reading of §469(g), literal §1245(a)(3)(G) | 659,603 | 292,483 | 488 |
| E | B at wages $120,000 | 316,857 | 141,922 | 276 |
| F | D, $4m property, wages $600,000, §168(n) start only | 23,082 | 9,264 | 28 |
| G | C + $150,000 interior improvement in year 2, bonus dwelling start only | 297,119 | 132,949 | 188 |

## Plans that beat the baseline

Dollar effect is nominal lifetime tax against the matching baseline (sell: 759,899; die: 601,608), wages $300,000.

| # | Plan (moves) | Effect | Provisions combined | Class | What could defeat it | Checked |
|---|---|---|---|---|---|---|
| 1 | Live in it all 12 years, sell | −198,338 | §121(a), (b)(2); §163(h)(3) | KNOWN: home-sale exclusion | nothing | — |
| 2 | Live 9, let 3, sell: 590,697. Reverse order (let 3, live 9): 637,520 | −169,202 vs −122,379 | §121(b)(5)(C)(ii)(I), (d)(6) | KNOWN: rent after, not before, residence | — | — |
| 3 | Let 11 years; in the sale year be nonpassive: spouse meets §469(c)(7), or short stays with material participation, or own production use | −26,526 (3.8% of the gain) | §1411(c)(1)(A)(iii), (c)(2)(A); §469(c)(7) or 7-day reg. | KNOWN: found described as "real estate professional / short-term rental / self-rental in the year of sale" | letting must be a §162 trade or business (Reg. §1.1411-4(g)(7) safe harbour: 500 hours); Temp. Reg. §1.469-2T(c)(2)(ii) allocates gain if the property was in another activity within 12 months before sale | 1 search |
| 4 | Plan 3 plus an exchange 1–2 years before sale | −37,117 | plan 3 + §1031(a) (real property only), §1245(a)(1), §168(k) on the newly bought components | VARIANT, largely a model artifact | The gain is only spread over two tax years. It arises because the model treats the 20% components as sold and rebought at an exchange, at pro-rata value. Step transaction and "to be held" (§1031(a)(1)) if sold a year later; §453 does the spreading without any of this | — |
| 5 | Nonpassive years (spouse §469(c)(7), or short stay with material participation), then die | −92,386 (C), −73,391 (B) | §469(c)(7) / reg.; §1014(a); §1245(b)(2); §1250(d)(2) | KNOWN: depreciate against wages, hold to death | §469(g)(2) only matters for passive years | — |
| 6 | Production building, §168(n) election, produce 12 years, die. Also produce 10, let 2, die: −138,243 | −138,896 (building $600,000); F: −730,722 | §168(n)(1), (n)(5) (10 years); §1014(a); §1245(b)(2); §461(l) | VARIANT: plan 5 under the 2025 rule | needs a real manufacturing business and "substantial transformation" (§168(n)(2)(D)); death timing; §461(l) defers the excess (F) | 2 searches |
| 7 | §168(n) building let after year 10 and sold, reading §1245(a)(3)(G) literally | −22,153 against the same plan read as §1245 property (910,524 → 888,371); still worse than not electing | §1245(a)(3)(G) "any qualified production property (as defined in section 168(n)(2))"; §168(n)(2)(A)(ii) present tense; §1250(a)(1)(B)(v); §1(h)(6) | CANDIDATE (drafting gap, small) | IRS reads once-QPP-always-§1245 (Notice 2026-16 summaries say "treated as section 1245 property"); §1250(a) still makes the excess over straight line ordinary, so only the straight-line share moves from 37% to 25% | 2 searches, nothing on point |
| 8 | Interior improvement made in a year the building is let by the night with material participation (so it is qualified improvement property), then let long term, die | −36,389 against letting throughout and dying (601,608 → 565,219) | §168(e)(2)(A)(i) ("for the taxable year"), (e)(6), (k); 7-day reg.; §1014 | VARIANT of the short-term-rental cost-segregation practice | Reg. §1.168(i)-4 change-of-use rules; whether one transient year makes the building nonresidential; if sold instead it is 17,309 worse (plan loses, see traps) | — |

Runner-up families (all in the run outputs): exchange then live in then sell (§121(d)(10), worse than plan 1 by
about 12,000); mixed-use years (always worse, see traps); at wages $120,000 (E) the same families lead, with the
sale-year plan (plan 4 form, with an exchange) worth 61,511 because the §469(i) allowance and lower brackets add to it.

**Nothing novel that survives.** Every plan that beats the baseline is a known technique or the same technique under
the 2025 text. The one item I do not find written about (7) is a reading question worth about 3.7% of the building
cost, and it does not make the election pay on a sale.

## Traps (rules that cost money)

1. **§168(n) election followed by a sale.** Produce 12 years and sell: 855,888 with the election, 753,187 without
   (+102,701 on a $600,000 building; F, $2.4m building: 262,242 worse than the passive-landlord baseline). The
   deduction lands at 10–35% with part pushed into a §172 carryover limited to 80%; the recapture is all ordinary
   (§1245(a)(3)(G)) at 35–37% with no 25% cap. This is nominal; but in the 5% present-value run (`run_B_pv.txt`)
   the best "§168(n)" family that sells is still one that never used the election.
2. **§168(n)(5) change of use inside 10 years**: produce 4, let 8, sell: 857,773. The whole allowance comes back as
   ordinary income in the year of the change (245,407 tax that year).
3. **Exchanging a §168(n) building for an ordinary one**: §1245(b)(4) recognises recapture up to the value of
   non-§1245 property received, i.e. all of it (basis 0 → 600,000 at the exchange in the trace).
4. **Early losses are worth less than late ones (nominal).** Bonus plus one short-stay material-participation year,
   then let, sell: 788,605, worse than the baseline by 28,706. The baseline's suspended losses (362,548) are released
   under §469(g) in the sale year against 35–37% income; the early loss offset 24–35% income. At 5% discounting the
   order reverses (short-stay families save about 26,000 in present value).
5. **§280A(c)(5) carryover has no release on sale.** Let 9, mixed use 3, sell: 764,514; 12,590 of deductions are
   simply lost, and §469(j)(10) takes those years out of §469 so the income cannot absorb suspended losses.
6. **Suspended losses and §121** (conservative reading): let 3, live 9, sell loses 186,590 of suspended losses.
7. **Exchange of a fully depreciated rental**: the non-real-property components are outside §1031 after 2017, so
   their recapture is recognised at the exchange.
8. **Death**: §469(g)(2) wipes suspended losses up to the step-up; the §172 carryover dies too.

## Drafting gaps noticed

- **Circular definition of qualified production property.** §168(n)(2)(A): "that portion of any nonresidential real
  property"; §168(e)(2)(B): nonresidential real property is "section 1250 property which is not…"; §1250(c): section
  1250 property is real property "other than section 1245 property, as defined in section 1245(a)(3)"; §1245(a)(3)(G)
  makes qualified production property section 1245 property. Read strictly, the election removes the property from
  the class the definition starts from. No discussion found.
- **§1245(a)(3)(G) is present tense** and points to a definition that requires current use (plan 7). Clause (B)
  by contrast says "for a period in which such property … was used".
- **§179 reaches §168(n) buildings.** §179(d)(1)(B)(i) covers "section 1245 property (as defined in section
  1245(a)(3))", which now includes them. So the cost of such a building counts toward the $4,000,000 reduction in
  §179(b)(2), which can remove the taxpayer's §179 limit for other property that year. Not modelled; no discussion
  found (the search summary assumed the opposite without authority).
- **§168(n)(5) needs two things**: the property "ceases to be used" in production "and is used by the taxpayer in a
  productive use not described". Idle property, personal use, and a change of use by a transferee are not reached;
  (n)(7)(B) leaves the transferee case to regulations. Secondary summaries of Notice 2026-16 mention only that
  temporary downtime is not a trigger. Not modelled.
- **§469(g)(1)(A)** ("all gain or loss realized … is recognized") against a §121 exclusion: the text does not say.
- **§168(e)(2)(A)(i)** tests residential rental property "for the taxable year", so the class of one building can
  differ by year, and with it whether an interior improvement is §168(e)(6) property (plan 8).
- **§121(d)(6)** taxes depreciation "in respect of such property"; whether separately depreciated components of the
  dwelling are "such property" is not stated (modelled as included).
- **Data check, not a finding**: the local text of §461(l)(1)(A) and (B) reads "before January 1, 2027". I expected
  Pub. L. 119-21 to have removed the end date. The model applies the limit in every year. Worth checking the source
  file before relying on either reading.

## Limits of the model

One property, whole years, fixed economics, no time value in the main ranking, components valued pro rata on every
disposition (maximises recapture), no state tax, no AMT, no §199A, no self-employment tax, no partnerships or gifts.
Family labels show the purchase variant, not whether the §168(n) allowance was actually taken (a plan whose first
year is not production gets none).

## Sources checked (4 searches)

- [How to avoid the NIIT when selling rental property](https://neiljesani.com/blog/how-to-avoid-the-net-investment-income-tax-when-selling-rental-property/) — plan 3 is published.
- [WCG: selling your rental property, passive losses and NIIT](https://wcginc.com/kb-rental-property/selling-your-rental-property-passive-losses-and-niit/)
- [EY on Notice 2026-16](https://taxnews.ey.com/news/2026-0577), [Withum](https://www.withum.com/resources/irs-issues-guidance-on-100-depreciation-for-commercial-real-estate/), [CBIZ](https://www.cbiz.com/insights/newsletters/opportunities-and-uncertainties-with-qualified-production-property-depreciation) — §1245 treatment and the 10-year rule; nothing on the circular definition, §179, or the present-tense point.
