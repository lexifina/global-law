# Cross-country synthesis: 38 tax systems

As of 2026-11-19 (final: all 18 countries of the 38-country phase done, on top of the 20 of `CROSS.md`). Sources, all
on the build server: the kernel (`kernel/API.md` 1.2.1, proofs in `TaxKernel/Theorems/`, `kernel/FINDINGS.md` K1-K11),
the OECD and Eurostat data and checks (`harness/runs/oecd20/`, `harness/runs/eurostat38/`), the generic scanners on all
38 (`harness/search/results/<CC>/`, refreshed 2026-11-19 by `report/refresh_all.sh`), the four family syntheses
(`germanic/FAMILY.md`, `baltic/FAMILY_NOTES.md`, `central/PROGRESS.md`, `southeast/PROGRESS.md`) and the 18 countries'
`FINDINGS.md`, `USEFUL.md` and `results/summary.json` (AT CH LU BE, FI IS EE LV LT, SK SI HU HR, GR CY MT BG RO).
A finding is cited as `CC Fn`. Only findings with a confirmed, certain, proved, explained or model-proved status (or a
named Lean proof) are used below; leads, open readings and novelty claims without a recorded search are in section 7,
"Needs checking". The ranked list of the most useful findings is `report/USEFUL38.md` (shown at the top of the report).
Everything about the first 20 that is not repeated here is in `report/CROSS.md`, which stays valid.

## 1. One kernel, 38 systems

- **All 33 kernel-built models require `TaxKernel`** (the 15 of the first phase and the 18 of this one; the five
  existing models are wrapped). Found in the sources of the 18 (`report/cross_tables.json`): a band `Schedule` and the
  kernel's `Rounding` in 18 of 18, the `Unit` theorems in 14, `Taper` in 9, `Social` contributions in 9, `Table` /
  `perPeriod` in 5 (EE HR MT BG RO), `Surcharge` in 3 (LU FI LV), the 1.2 `Family` parts in 4 (BE LV HU HR), the
  `Multiplier` in 1 (CH: canton 98 % and City 119 % of the simple cantonal tax), `Credit` in 1 (IS). Across all 33:
  Schedule 33, Rounding 30, Unit 23, Taper 15, Social 14, Table 7, Credit 6, Surcharge 6, Family 4, Multiplier 1, Dual 1.
  No model of the 18 has a `sorry` (12,594 Lean lines, 730 theorems, 876 provisions cited across the 18).
- **The pattern that dominates the 18 is not the tariff but what is withdrawn on top of it.** Every one of the 18 has
  a band tariff (unlike Germany's § 32a formula, K1); the work is in the allowances, credits and benefits that are
  tapered or switched off with income. That is why `Taper` (9) and the family-benefit code carry the findings.
- **What the kernel gained for the 38 (1.2, 1.2.1).** Multipliers on a base tax and tax at an average rate (Swiss
  Steuerfuss, progression clause, rate splitting), credit allocation over several taxes (FI, IS), child scales by rank,
  by family size and as cumulative totals, income attribution between spouses (BE quotient conjugal), an allowance
  given at the lowest rates (BE) and spilling into another levy (HU), a stepped withdrawal (GR), tariffs printed as
  columns or as "rate × income − subtraction" (MT, and the NL fault of the first phase), and, from the gaps the 18
  reported: a taper rounded half-up (SK, IS), a spill capped at the receiving levy (HU), an exempt sum valued on its own
  tariff (BE), parameters that change during the year (BG, HU, RO, SI, EE, LT) and a contribution rate chosen by the
  size of the whole base (AT). Each comes with toy checks (`examples/Parts38.lean`) and proofs (`Parts38.lean`,
  `Extra38.lean`): a zero band is never worth less than the same allowance given at the lowest rates (K10); complete
  steps never withdraw more than the proportional reading of the same words, and each step is a notch.
- **Where a generic theorem fails, the statute is unusual.** Switzerland's federal tariff (DBG Art. 36) ends in a
  13.2 % band and then taxes the whole income at 11.5 %: it is not convex, so `Schedule.ticks_convex` and
  `splitting_le_separate` fail (proved, `ChTax.fedSingle_not_convex`, CH F2); it is the only one of the 18 where a
  generic theorem fails. Belgium values its exempt sum on the pre-2017 tariff with a 30 % band the income tariff no
  longer has, so above 11,460 € the exemption is worth more than the tax on the income it exempts (proved, BE F5,
  `exempt_tariff_gap`). Every other generic theorem instantiated by the 18 holds.
- **Kernel gaps that remain (written locally, by design):** eligibility tests and their reference periods (previous
  year's income, income per family member, equivalence scales), deemed-expense regimes taxed finally (SI, HR paušal,
  RO micro), monthly withholding with an annual true-up (EE LT LV), and distribution-only company tax with retention
  (EE LV). As in the first phase, the arithmetic is shared; the definitions of who and what is counted are not.

## 2. What the 18 add

- **Germanic / Benelux (AT CH LU BE): layered taxes and three units of assessment.** Band tariffs at every level, with
  rounded second statements of the tariff (CH rows 4-7 Rappen below their band sum, CH F1; LU's salary table −10 to
  +15 € from the assessment, LU F4); the family's cliffs are all in child and credit rules, never in the tariff
  (AT F9, F11, F12; CH F8-F10; LU F12-F14; BE F1, F14). Unit of assessment: individual (AT), joint with a married tariff
  (CH: the largest marriage penalty of the 38's federal layers, +71 % federal tax for two earners at 2 × 100,000 CHF,
  +135 % with two children, CH F12), tax classes (LU: married parents pay up to 1,155 € more than unmarried ones, LU F11),
  individual with the quotient conjugal (BE). 214 of 224 OECD lines within one unit at the OECD's conventions; the
  official calculators of AT, CH and LU reproduced on 1,494 to 24,003 cases.
- **Nordic + Baltic (FI IS EE LV LT): the worst marginal rates in the middle.** FI and IS are dual income taxes like
  SE/NO/DK, with credits spread over several taxes (the kernel gap Sweden reported, now `allocateOrdered` /
  `allocateProportional`); EE LV LT are flat or two-rate taxes with an allowance withdrawn with income, and EE and LV tax
  company profit only on distribution. Withdrawals put the highest rates between 0.5 and 1 AW: Estonia's "tax hump",
  37.99 % income tax (40.8 % with contributions) on 14,400-25,200 € against a 22 % flat rate (EE F3); Lithuania's 49.3 %
  on 12,456-28,647 € against 38.98 % at the top (LT F5); Finland's 2025 work-credit withdrawal at 56.0 %, above the
  54.85 % top rate, up to 125,240 € (FI F2).
- **Central Europe (SK SI HU HR): family support through the tax, and who claims it.** Hungary's family tax base
  allowance is proved to act as a credit of 15 % of the frame against tax and contributions together
  (`famBurden_closed_form`); Slovakia's 2025 child-bonus withdrawal is computed on the claimant's own base, so a couple
  avoids it by letting the lower earner claim (2,400 € with 60,000 + 12,000 € and two children, SK F5); Slovenia's
  child allowances cost up to 1,422 € if the wrong parent claims (SI F13); Croatia's default equal split wastes
  1,707 € a year for a couple with 36,000 + 9,000 € and three children (HR L04). OECD 168/168 lines exact for SK SI HU;
  Croatia agrees with Porezna uprava's own calculator on 4,176 of 4,176 cases.
- **South-east / Mediterranean (GR CY MT BG RO): amounts that live outside the code, and the only four countries with
  no Taxing Wages referee.** Bulgaria's real child relief (6,000 / 12,000 / 18,000 лв.) exists only in each year's budget
  act while ЗДДФЛ чл. 22в prints 200 / 400 / 600 (BG F3); Cyprus charges 8.8 % social insurance where the law prints
  8.9 % (CY F1); Romania's 300-lei facility sits in an emergency ordinance outside the Codul fiscal; Malta's 2025
  contribution schedule was not published by October 2026 (MT F11). Malta's default joint computation costs two-earner
  couples up to 8,850 € a year unless they elect separate computation (MT F6, `separate_saving_le`). Romania's stepped
  personal deduction makes one more leu cost take-home pay at 40 points between 4,050 and 6,050 lei a month
  (RO F1, F2, proved).

## 3. Which design features cause which problems (all 38)

**All-or-nothing limits on family benefits: the largest effective marginal rates in the 38.** The generic METR scanner
finds marginal rates above 1,000 % in 9 of the 18 without being told where to look (peaks: CY 6,862 %, MT 3,364 %,
LT 3,129 %, BG 2,163 %, HR 1,674 %, SI 1,579 %, GR 1,307 %, BE 1,260 %, AT 1,123 %; `report/cross_tables.md`), and every
peak is a benefit or credit limit the country file names and proves: a lone parent of two in Cyprus loses 4,708 € of
child and single-parent benefit at 49,000.01 € (CY F4); Brussels' Famiris ceilings cost 548-2,954 € a year for one
euro (BE F1); Lithuania's additional child benefit costs 1,730 € for one euro with two children (LT F1); Slovenia's
eight child-benefit classes cost 300-940 € (SI F7); Croatia's doplatak za djecu 741 € between 40,899 € and 40,900 € of
pay (HR F10); Bulgaria's child allowance 784 лв. for 10 лв. of gross (BG F4); Greece's child benefit 671 € for a 2 €
raise (GR F4); Austria's Kindermehrbetrag partner test up to 1,400 € (AT F9). With the first phase (MX's employment
subsidy, AU's FTB B, CZ's child allowance, IE's working family payment, PT, IT, KR) that is at least 15 of 38 countries
where one unit of income can cost a family more than a month's pay. Malta (a tapered children's allowance) and the
kernel's own theorem (`Taper.amount_step`: a taper has no jump) show the fix. Many of these tests read the previous
year's income (CY, SI, HR, BG), so the timing of a bonus decides a whole year's benefit.

**Withdrawn allowances and credits put the highest marginal rates in the middle of the distribution.** A band schedule
never exceeds its top rate (kernel theorem), so every rate above it is a withdrawal: EE F3 (the hump, abolished from
2026), LT F5 (the NPD taper), FI F2 (the 2025 work credit, removed for 2026), GR F1 (the art. 16 tax reduction withdrawn
by 20 € per 1,000 €: a hidden 46 % band above the declared 44 % top rate up to 91,000 €), LU F14 (the minimum-wage
credit, 64-74 % between 36,000 and 43,400 €), SK F6 (the bonus withdrawal stacked on the allowance taper: 51-55 % for
families between about 29,700 and 43,600 €), SI F12 (53.7 % between about 13,100 and 16,832 €), IS F4 (54 % for
single parents with young children). Three of these were removed or changed for 2026 (EE, FI, IS), which makes the
2025-2026 boundary itself a timing opportunity (section 3, timing).

**All-or-nothing entry thresholds for contributions.** One unit of income switches on a whole contribution: Austria's
Geringfügigkeitsgrenze (551.10 € a month; 606 € a year) and the unemployment-insurance rate chosen by the size of the
whole pay (steps of 217-300 €, AT F10); Finland's päivärahamaksu (141.64 € for one cent at 16,862 €, FI F1); Iceland's
two flat levies (36,814 kr. for one króna, IS F3); Latvia's self-employed minimum base (1,393 € a year for one euro over
740 € a month, LV F1); Slovakia's 8,580 € self-employed social-insurance threshold (2,844 €) and its 100,000 € revenue
test (2,555 €, SK F8, F9); Switzerland's BVG entry threshold (84.63 CHF, CH F9); Bulgaria's free-profession minimum
base (3,472.78 лв. from the first lev, BG F10). In the first phase: NO's sole-trader band and CZ/PL entry rules. The
kernel states the general fact once (`Contribution.floor_notch`); `Surcharge.glide` and a phase-in are the fixes the
country files propose.

**Income tests that count income the tax does not, and taxes that test income they do not tax.** Estonia's basic
exemption is withdrawn by untaxed Estonian dividends (10,800 € of dividends cost 1,726.56 € of tax on wages, EE F4);
Lithuania tests the NPD on all income but deducts it only from wages, so the "15 %" on dividends is 24.8 % for most
employees (LT F2); Slovenia's child-benefit test sees the deemed 20 % profit of a flat-rate sole trader, not the
revenue (SI F11). With Korea's child incentive (KR F9) and Czechia's after-tax test (CZ F5) of the first phase: each is
a test that reads one definition of income while the tax reads another.

**Who claims the child, and the unit of assessment.** Where a relief or a withdrawal is computed per claimant, the
choice of claimant is worth more than most planning: SK F5 (2,400 €), LV F4 (2,258 € a year for wages 7,000 + 30,000 €
with three children), HR L04 (1,707 €), SI F13 (1,422 €), AT (Familienbonus allocation, 1,050 €); Bulgaria and
Croatia let an unused part pass to the other parent. Joint taxation without full splitting penalises two-earner
couples: Switzerland's federal married tariff (+71 %/+135 %, CH F12) and Malta's default joint computation (up to
8,850 €, avoidable by election, MT F6). Couples' rules also penalise marriage against cohabitation: Luxembourg's class
1a for unmarried parents (up to 1,155 €, LU F11), Belgian de facto cohabitants keeping the single-parent supplement
(about 750 €, BE F6), a Finnish single parent who marries losing about 930 € per child (FI F7). Spouse reliefs that end
at the spouse's first euro of pay are notches: LV F3 (765 €), SI F9 (455-1,420 €), HR F11 (828 €), RO F4.

**Thresholds frozen while the amounts around them are indexed; amounts not updated with the amount they depend on.**
Austria's Werbungskostenpauschale of 132 € (since at least 2005) and Mehrkindzuschlag limit of 55,000 € (AT F12, F13);
Luxembourg's 67,400 / 76,600 € child-bonus phase-out (LU F7); Belgium's 550 € child-credit cap excluded from indexation
(BE F4); Iceland's barnabætur frozen while the bands rose 5.8 % (IS F15); Hungary's családi pótlék unchanged since at
least 2009 (HU F11, a policy choice); Malta's dividend-refund thresholds left at the YA 2025 band points (MT F1);
Slovenia's 2006 amounts in ZDoh-2 čl. 112(1) and 117(1), 21.5 % below the operative ones (SI F6); Estonia's birth-benefit
cap tied to an exemption that became income-dependent (EE F13). With IE, PL, CZ, IT, ES, AU, NZ, MX and CA in the first
phase, this is the most common drafting fault of the 38. The fix is the same everywhere: write the dependent amount as a
function of the amount it depends on.

**The statute says one thing and the state applies another.** Bulgaria's child relief (200 лв. in the code, 6,000 in
the budget act, BG F3); Cyprus's social insurance rate (8.9 % printed, 8.8 % charged, CY F1); Latvia's IIN 12(1) (570 €
printed, 510 € in force, LV F10); Austria's "unter 700 Euro" administered as 700 € per child (AT F7); Hungary's
"(667 százaléka)" for 666.67 % (HU F2); Greece's two amounts for five children (1,780 € in the list, 1,800 € by the
"for each child after the fourth" sentence, GR F2: which one AADE applies is open). Dead references after renumbering
or repeal: IS F1, F2; EE F14, F15; LV F11, F12; LU F7; GR F11, F12; SK F4. Dead law: Slovakia's zamestnanecká prémia
cannot be positive for any income while the minimum wage is at least 554 € (proved, SK F12).

**Withholding that departs from the annual tax.** Latvia withholds 25.5 % all year and collects the 33 % band and the
solidarity-tax adjustment at the return (4,492 € on 150,000 €, LV F7); a low-paid Austrian single parent of two has
117 € withheld and is owed 3,083 € back on assessment, because withholding never pays the refundable credits (AT F4);
Estonian and Lithuanian monthly withholding of an annual allowance ends in refunds or bills of up to 1,727 € (EE F9,
LT F8); Brussels residents are over-withheld (BE F9), Zagreb residents were in January-February 2025 (HR F8), Reykjavík
residents slightly under-withheld (IS F6). With KR, AU, NO, PT, ES, SE, PL, CZ, NL in the first phase: the government's
own year-round computation departs from its annual statute in at least 16 of 38 countries.

**Timing pays wherever the schedule is not convex, and at every reform boundary.** The kernel's timing scanner finds
two-year bunching gains above 1 % of AW in 17 of the 18 (all but Latvia; largest: CY, BG, LT, SK; scanner leads in `cross_tables.md`); the country files prove
the main ones: LT up to 3,526 € per two years with children (LT F3), SK 2,384 € (SK F7), EE 1,727 € (EE F5), LV 1,277 €
(LV F2, reading-dependent), FI 950 € (FI F3), IS up to 481,655 kr. (IS F17), LU 7,276 € for a single parent across the
end of the CIM (LU F15). Reform dates add one-off gains: EE up to 1,727 € by paying in January 2026 (EE F12), LT 5 % of
a December 2025 payment (LT F7), CY 600 € on a 12,000 € bonus moved to January 2026 (CY F8), HU 214,553 HUF for a lone
parent of three (HU F6), RO's dividend rate rising from 10 % to 16 % for distributions from 2026 (RO F7).

**Credits that need tax to absorb them.** A non-refundable credit is worth nothing to someone with no tax (kernel
`applyCredits_waste`): Finland's unused work credit is lost (FI USEFUL), Latvia's child relief is lost on the claiming
parent's low income (LV F4), Iceland's 22/31 rule let retirees use the unused credit against capital income until 2026
(IS F10). Austria and Belgium turned child reliefs into refundable credits (AT Kindermehrbetrag, BE 550 € cap), which
is why their cliffs sit on the refundability tests instead.

## 4. Owner-managers across the 18

`harness/search/owner.py` on all 18 (company side in `harness/search/company.json`; statute-cited entries from the
country agents for CY GR MT BG RO SK HR FI IS EE LV LT, the rest partial: section 7). Total tax as % of a profit of
1 / 3 / 10 AW, best split against all salary:

| | 1 AW best / salary | 3 AW best / salary | 10 AW best / salary | design |
|---|---|---|---|---|
| EE | 22.0 / 38.8 | 22.0 / 42.5 | 22.0 / 42.5 | distribution tax 22/78, no personal tax: flat 22 % at every profit; retention untaxed (EE F7) |
| LV | 20.0 / 38.7 | 20.0 / 43.6 | 20.0 / 47.1 | distribution tax 20/80, no personal tax (2025; UIN changes in 2026) |
| BG | 14.5 / 34.8 | 14.5 / 34.6 | 14.5 / 17.6 | 10 % + 5 %; full salary wins again far above the contribution ceiling (BG F6) |
| HR | 20.4 / 40.4 | 20.7 / 44.9 | 20.8 / 46.1 | 10 % small-company CIT + 12 %; the director's minimum base is not in the scan (HR F16) |
| GR | 25.9 / 37.2 | 25.9 / 50.0 | 25.9 / 48.8 | 22 % + 5 % (GR F8) |
| SK | 26.5 / 42.5 | 26.5 / 47.2 | 26.5 / 50.5 | 21 % + 7 % (10 % small-company CIT not in the scan: SK F10 finds 81-83 % kept at 50,000 €) |
| LT | 27.8 / 39.6 | 28.6 / 40.6 | 28.6 / 40.3 | 16 % + 15 % (6 % small company: 20.1 %, LT F6) |
| HU | 33.4 / 41.1 | 26.2 / 41.1 | 23.7 / 41.1 | 9 % + 15 % + szocho to its ceiling; an active Kft member's minimum bases are not in the scan |
| MT | 18.7 / 29.4 | 29.6 / 30.1 | 33.4 / 33.5 | 35 % with full imputation: dividends win only below the art. 12 thresholds (MT F1, F9) |
| CY | 25.0 / 27.4 | 28.0 / 37.7 | 28.2 / 38.4 | 12.5 % + SDC 17 % + GESY: salary of 22,000-24,500 € plus dividends (CY F6) |
| CH | 22.2 / 23.0 | 28.1 / 35.3 | 34.8 / 43.9 | Zürich, qualifying participation taxed at 70 % / 50 % (CH F13) |
| LU | 23.5 / 37.8 | 33.8 / 49.0 | 38.6 / 52.1 | small salary + 50 %-exempt dividends (LU F16) |
| FI | 25.1 / 37.6 | 33.8 / 51.9 | 45.3 / 59.0 | the 8 % net-asset rule decides it (FI F4) |
| IS | 29.7 / 31.0 | 34.9 / 41.1 | 36.8 / 45.8 | salary to 5,900,065 kr., dividends above; reiknað endurgjald minimum binds first (IS F16) |
| SI | 39.0 / 44.4 | 40.8 / 50.8 | 41.2 / 61.2 | salary to the end of the zero-tax zone, dividends above (SI F16) |
| AT | 38.1 / 44.2 | 42.1 / 47.4 | 43.6 / 47.3 | GmbH, salary about 34,000 € + dividends if dividends bear no GSVG (AT F15) |
| BE | 35.5 / 48.8 | 43.5 / 61.0 | 46.3 / 65.4 | flat 25 % CIT in the scan; the 20 % SME rate needs a 50,000 € director's pay (BE F12) |
| RO | 28.5 / 42.8 | 27.1 / 42.8 | 25.2 / 42.8 | 16 % CIT + 10 % (2025); the micro-enterprise route is cheaper (RO F10) |

What it shows, across 38. In every one of the 18 a company paying dividends costs less than salary at 3 AW of profit
(by 0.5 points in Malta, where full imputation nearly equalises them, to about 20-24 points in Estonia, Latvia, Croatia,
Greece and Slovakia). The countries with the lowest owner-manager rates are those that tax company profit only on
distribution (EE, LV) or combine a low CIT with a low final dividend tax (BG, HR, GR, SK); the boundary is policed not
by the tax but by minimum contribution bases for owners (HR, HU, IS, LV board members, SK self-payers) and, in Belgium,
by a corporate rate that depends on the director's pay. With the first phase (AU and NZ imputation: the split barely
matters; IE: salary always wins; PL 26.3 % flat): integration decides it, in 38 countries as in 20.

## 5. What the referees do differently

- **OECD Taxing Wages 2025 is wrong or off-statute in at least 5 of the 13 new OECD members, always on family benefits
  or on a parameter's vintage**: AT pays the 6-year-old the 10+ Familienbeihilfe (+285.60 €, AT F2) and a 4,000.32 €
  Familienbonus to the single parent (AT F3); CH uses 268 CHF a month per child where Zürich pays 215 under 12 and prints
  a federal tariff mixing 2023 and 2024 values (CH F3, F4); LU's allocations familiales are 4.48 € high (LU F2, open);
  BE's age supplements are unfrozen (+640.98 €, BE F2) and its local line implies 6.0 % where the City of Brussels levies
  4.9 % (BE F10); IS's 2025 row uses the 2024 levies (IS F5). EE's worker pays no II-pillar contribution and every
  single parent gets the single-parent allowance (EE F1, F2: conventions); the OECD's married Greek households earn
  1.1 × the single wage (a 10 % marriage allowance in gross pay). The harness check (each model's own defaults) and the
  family checks (the OECD's conventions) therefore differ for CH, FI (Helsinki 5.30 % vs the OECD's 7.54 % municipal
  rate), EE, BE and GR; at the OECD's conventions the family checks have every compared line within one unit in FI, IS, EE (48/48), BE, LV, SK, SI, HU (56/56), 55/56 in AT, CH and LT, LU 48/56 (LU F2 open)
  and Greece 168/168 at the OECD's own gross.
- **Eurostat's earn_nt_net 2025 is a different product (kernel K9).** It equals Taxing Wages up to 2023 and not from
  2024; on 11 models that reproduce Taxing Wages it agrees on income tax within 1 % in 26 of 143 cases. The south-east
  family traced the disagreements in its countries to Eurostat/EC parameter errors: Bulgaria's January-March 2025
  ceilings and allowance limits (BG F1, F2), Croatia's 22.4 % lower rate that no city applied (HR F1), Malta's
  contribution maxima (MT F11); Romania's per-child deduction per earner is open (RO F12). Cyprus agrees to the cent
  (52/52, CY). It is a sanity bound, not a referee.
- **EUROMOD's country reports contain errors in five countries**: CY (GESY deduction ceiling, CY F9), MT (lone-parent
  maintenance condition stated backwards, MT F10), RO (a linear taper for a stepped deduction, the 300-lei facility
  missing, RO F13, F14), LT (three NPD inconsistencies, LT F9-F11) and HR (the pensioners' 50 % reduction given to
  every pensioner, HR F5).
- **Official calculators**: exact in LU (24,390 cases), SK (18 bonus examples), FI (287 + 32 table rows), HR (4,176
  cases), AT for employees (90/90); wrong for Austrian pensioners in April 2025 (6 % health insurance where the law gave
  5.1 %, AT F5), Swiss families (the ESTV calculator omits taxable family allowances, about 970 CHF, CH F6), Croatian
  young workers and two municipalities (HR F3, F4, F9), Icelandic barnabætur under 5,000 kr. (IS F8), a Hungarian NAV
  booklet example (HU F3).
- **Open company-side data versus the statute (kernel K11).** The OECD's 2025 combined CIT rate for Slovakia is 24 %
  (the top rate, for revenue above 5 million €); a one-person company pays 21 % or 10 %. Croatia's 18 % is 10 % below
  1 million € of revenue; Luxembourg's 23.87 % is 21.73 % below 175,000 €; Belgium's 25 % is 20 % on the first
  100,000 € if the director is paid 50,000 €; Bulgaria's employer ceiling implied by Eurostat's labour cost is
  25,340 лв. where the statute's is 48,435 лв. (Eurostat's BG parameters, BG F1-F2). A cross-country owner-manager
  comparison built on headline CIT rates overstates the company route's cost in exactly the small-company cases it is
  meant for.

## 6. The most useful findings

Ranked, with evidence and audience, at the top of the report: `report/USEFUL38.md`.

## 7. Needs checking

A spot-check of every headline finding (kind loophole-new, gov-error or statute-fault) of all 33 kernel-built
countries for an authority and evidence (`report/spotcheck.py`, `report/spotcheck.json`, `report/spotcheck.txt`:
312 headline findings, 127 flagged by its pattern match; for the 18: 166 checked, 68 flagged). Most flags are format
(no "status:" line on a block that names its Lean proof or run, e.g. CH F2, F4, F6, F8-F12, BE F5, F9, F12, F14, HR F11, F16, MT F3-F6, AT F12, F13, GR
F9-F12); those blocks are used above only where the proof is named. The ones below do not yet carry the claim their
label makes:

- **Leads and open readings (not used as findings above).** GR F5 (unmarried parents declaring the children with the
  lower earner: +665 €, needs OPEKA practice); MT F9 (exempt dividend plus the 6/7 refund, needs the CfR); SK F14 (a
  token salary instead of the self-payer health minimum, needs the insurers' practice); LU F13 (CISSM and non-periodic
  pay, under the anti-abuse clause); LV F2 (fewer months, reading-dependent: the month in which income arises); LT F15
  (the 25 % cap's base, a reading); GR F2 (which of 1,780 € or 1,800 € AADE applies); LU F6 (the 1976 law's 104 %:
  needs the 2012/2013 amending law); HR F4 (Knin's rate at assessment); SK F4 (stale transitional provisions: lex
  posterior settles it in practice); RO F12 (Eurostat's per-child deduction per earner); LT F7 (the 2026 window, open
  for individual activity); BE F2, F3 and LU F2 (draft notes to the OECD and SPF Finances, open).
- **Novelty not recorded, yet labelled loophole-new.** CH F8, F9, F10; LU F9, F12, F14, F15; BE F14; SI F9, F14; LT F7.
  The amounts are proved; only "new" is unsupported (search before citing them as new).
- **Authority not quoted in the block** (pattern match; the statute is usually named in the country's CATALOGUE or
  Params): AT F7, LU F9, F14, BE F9, F10, IS F14, LV F8, F12, LT F11, F12, F14, F16, SI F3, F5, HU F12, HR F9, CY F12.
- **Owner-manager scan (`owner.py`) against the country agents' own results.** The scan cannot express minimum
  contribution bases or pay floors for owners (HR director's base 0.65 AW, HU active member's TB and szocho bases, IS
  reiknað endurgjald, LV board member's minimum object, SK self-payer health minimum), the Belgian director-pay condition
  for the 20 % rate, Malta's 6/7 refund, small-company and micro regimes (SK 10 %, LT 6 %, RO micro, HU KIVA, LU bands
  are in), or Finland's net-asset rule beyond the agent's 500,000 € assumption; the country files' own scans
  (`tools/owner_*.py`) are the authority where they differ. Company sides still partly from open OECD data: AT, CH
  (employer), LU (employer), BE, SI (confirmed by the SI agent), HU (`company.json` "completeness").
- **First-phase items still open** are listed in `report/CROSS.md` section 5.
