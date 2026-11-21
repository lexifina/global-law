# Cross-country synthesis

As of 2026-11-19 (final version: all 15 new countries done). Sources, all verified: the kernel's proofs and
fidelity checks, the OECD data and checks for all 20, the five-country results (`~/cmp/compare/RESULTS.md`), and the
findings of the 15 new countries (CA, AU, IE, NZ, SE, NO, DK, IT, ES, NL, PT, PL, CZ, KR, MX; about 240 blocks). A country finding is cited as `CC Fn`; only findings whose status
is confirmed, certain, proved, known or explained are used for the patterns below; the ones that are not are listed
under "Needs checking" (section 5). The ranked list of the most useful findings is at the top of the report
(`report/USEFUL20.md`). Scanner figures are labelled as leads. The generated tables under this text (shape of each
system, OECD validation, kernel parts per country, findings index) rebuild themselves with the report.

## 1. One kernel carried 15 new tax systems

- **Shared parts.** All 15 new models build on the shared Lean kernel (`TaxKernel`, required by every lakefile).
  From the country sources: a progressive `Schedule` in 15, the kernel's `Rounding` rules in 12, the unit of
  assessment (`splitting`/`quotient`/allowance transfer) in 8, `Taper` in 6, `Social` contributions in 5, `Credit`
  in 5, `Surcharge` in 3, `Dual` in 1 (Sweden; Norway and Denmark wrote capital income as ordinary schedules), and
  the generic theorems instantiated in all 15. A band schedule and a rounding rule are in every income tax; the
  richer parts were often rewritten locally because eligibility tests and period rules differ more between countries
  than the arithmetic does.
- **The kernel carries real statutes exactly.** Rebuilt from kernel parts only, the UK income tax, Class 1 and the
  child benefit charge equal the UK model to the penny on 10,279 households; Germany's § 32a tariff, splitting, Soli
  and four social contributions equal the German model on 2,926 assessment units (`kernel/fidelity/RESULTS.md`).
- **Proved once, used everywhere.** No `sorry`, only Lean's standard axioms (`kernel/audit/axioms.out`). A band
  schedule's marginal rate is its band's rate, it never jumps, never exceeds its top rate and is convex when its rates
  rise; splitting never costs more than separate assessment for a convex, monotone tax (both conditions are needed,
  K2); joint aggregation on one schedule never costs less (K3); an exemption limit without a glide zone is a notch
  (K4; AU F6 instantiates it for the Medicare levy surcharge); inside a taper band `den` more income costs
  `r·(den + num)`.
- **What did not fit, and why.** Germany's tariff is a formula, not bands (K1). The gaps the countries reported are
  of three kinds: **tables that govern over their formula** (KR 근로장려금, MX tarifas, withholding tables: added to
  the kernel as `Table` in 1.1), **rules on periods shorter than the year** (monthly contributions in CZ and KR, July-
  June bases, NO's composite rates; `perPeriod` in 1.1), and **parts defined through other parts** (Swedish credits
  applied in a fixed order to municipal then state tax, a cap on a group of taxes as a share of income, Norway's
  phase-in cap on trygdeavgift). The last kind is where tax systems are least alike.

## 2. Which design features cause which problems

**A threshold that is not indexed while the amounts around it are.** The most common fault across the 12 countries,
found by reading each amount's history in versioned law:
- Ireland's €12 PRSI credit, unchanged since 2016 through five rate rises: the €352 notch grows from €2.08 to €4.54 a
  week under enacted law (IE F9);
- Poland's one-child relief limits 112,000 / 56,000 zł, unchanged since 2013 (PL F12), and an old bracket threshold
  still in the zero-PIT exemptions (PL F11);
- Czechia's spouse-credit income limit, unchanged since 2008 (CZ F11);
- Italy's dependants' income limit, unchanged since 1995, in a TUIR that still counts in lire (IT F9);
- Spain's 6,500 € other-income condition, never updated while the reduction it switches off doubled: one cent of
  interest above it costs a 14,000 € worker more than 1,650 € (ES F4, F5);
- Australia's FTB A supplement test at $80,000, never indexed (AU F4); New Zealand's personal-services threshold of
  $70,000 that no longer matches the rate thresholds it protects (NZ F8); Mexico's fixed nominal thresholds beside
  indexed tables (MX F14); Canada's child benefit amounts indexed separately so that they no longer meet (CA F10);
  Portugal's art. 68 n.º 2 still names the old 8,059 € threshold under the 2026 table (PT F13, a lead on the 2026
  text) and its automatic indexation rule against the budget's thresholds (PT F6).
The fix is the same everywhere: write the dependent amount as a function of the amount it depends on (IE F9: the
credit as rate × €352), or index both together.

**References and tables not updated with the provision they point to.** Dead or wrong cross-references after a
renumbering or repeal: CA F11, CZ F3, IT F10, NO F5-F8, MX F5 (statute still counts in salario mínimo), and an
amending act that had to be amended before it came into force (SE F8), two laws of the same day rewriting one
paragraph with the same words (PT F5), a Dutch article citing "artikel 8,10" (NL F15) and a term the act does not
define (NL F14), Denmark's reform renaming "topskat" to "mellemskat" in two other laws 19 months early and a dead
cross-reference in the 2025 topskat base (DK F6, F7). Published text that differs from the law:
Korea's official text of the top bracket (KR F2), Lovdata's links (NO F8). Tables that differ from their own formula:
Korea's incentive table in 40 of 447 rows (KR F3), Mexico's tarifas, which are not monotone at 6 row edges (MX F4),
Sweden's 2025 formulas, which jump at their joints (SE F4), the Dutch statutory tariff, which falls by cents where
the rounded "kolom III" meets the next band (NL F5, F6), and Portugal's rounded average rates, under which one more
cent of income can lower the tax (PT F3). Credits that never reach their stated maximum (NL F7) or end a few euros away
from the bracket they are meant to match (NL F8) are the same drafting pattern. Where the table was checked and found exact, that is
worth saying too: New Zealand's PAYE tables (NZ F13), Sweden's withholding tables (SE F6).

**Withholding drifts from the statute, and mostly in the state's favour.** The government's own year-round
computation was off in 9 of the 12 countries: stale parameters (Australia's Schedule 1 uses the 2023-24 Medicare levy
parameters, AU F8; Korea's monthly table the 2024 child credit, 200,040 won a year for two children, KR F5);
by-design over-withholding (Norway 2,430 NOK a year from every employee above 200,000, NO F1; Stockholm about 3,300 kr,
SE F5; Australia up to $765 by leaving the low income offset to the return, AU F9; Poland up to 2,641 zł for under-26s,
PL F8; Czechia 100-123 Kč on average, CZ F10); and the reverse, Spain's under-withholding band and a minimum-wage
earner withheld 300 € who owes nothing (ES F2, F3), Portugal's August-September 2025 cut, which returned about 13 times
what January-July had over-withheld and left almost everyone under-withheld (PT F7), and its one-earner table that
under-withholds against the joint return (PT F9). The most striking case is Korea's monthly table, computed with the
2014 earned-income credit and the 2017 pension ceiling (7,098 of 7,106 cells reproduced by the kernel from that
rule; over-withholding up to 28,040 won a month, KR F8) as well as the 2024 child credit (KR F5). The Lean models make each of these a proved difference between
two functions.

**All-or-nothing tests make the notches; tapers make the bands; stacking makes both worse.** A band schedule cannot
exceed its top rate (kernel theorem), so every marginal rate above it is a withdrawal. Notches from eligibility
limits, minimum payments and entry thresholds: AU F5 (FTB B, $3,883.60 for one dollar), CZ F7 (child allowance,
35,280-51,238 Kč for one crown) and CZ F8 (flat-tax band edges, up to 124,728 Kč), MX F6-F9 (the employment subsidy:
one centavo costs 474.65 a month), PL F3, IE F17 (€1,035 at the working family payment's €20 minimum), NZ F9, F11,
F12, ES F6, F7, SE F1. Tapers stacked on the top rate: Danish parents pay 56.3 % from 997,878 kr. of pay, above the 52.07 % tax ceiling,
because the child benefit taper is not a tax rate (DK F13); Korea's earned-income credit limit withdrawal gives 79 %
and 96 % bands (KR F10). Tapers that withdraw 100 % or more: NZ F10 (the minimum family tax credit, 101.67 %; 113.67 %
with a student loan), ES F12 (72.8 % for single workers on 16,700-18,276 €). Portugal's abono de família and the joint mínimo de existência (PT F10, F11: 250-1,914 €); Mexico's employment
subsidy (MX F6-F8) and its RESICO single-rate table, which taxes the whole revenue at one rate (MX F10). Stacking:
Italy's cliff at 8,500 € where
one euro of pay costs 300 € (IT F4) and its double edge at 35,000 € (IT F6). Countries that replaced a cliff with a
taper show the fix: Czechia's 2025-10 reform replaces the child-allowance cliff with a withdrawal (CZ F7).

**Means-tests on income that leave some income out.** Korea's child incentive tests eligibility on total income
including dividends but sets the amount by earnings, so one won more of wages can cost 1,750,000 won (KR F9, found
by the METR scanner unprompted); dividends outside Czechia's child-allowance income test (CZ F14), the ryczałt outside Poland's one-child test (PL F10), and the order of claims inside a couple (CZ F5, F6:
letting the low earner claim the children lowers counted income) are each a route around a test that reads one
definition of income while the tax reads another.

**The unit of assessment decides who gains from being a couple.** Individual taxation rewards moving income to the
lower earner (SE F10, up to 178,832 kr; CA F2, F3; NO F12, F13; MX F15); splitting and quotients give bonuses that grow
with income (scanner: DE 22 %, FR 28 % of AW at the top of the grid; ES F8 joint filing 945-1,420 €; Poland's joint
filing up to 27,600 zł, PL F6). Joint means-tests make the penalties, and they bite on couples, not on marriage:
being a couple costs up to $16,652 a year in Canadian benefits (CA F4), living together costs a Norwegian single
parent the extended child benefit (NO F16), Korea's household incentive test penalises marriage (KR F14); and in
Denmark marriage moves a spouse's interest income into the higher earner's topskat (up to 24,362 kr., DK F9); the US penalty of 8.1 % of AW is a marriage penalty because the US taxes
cohabitants as singles. (The filing-unit scanner first compared a married couple with two adults the model treated as
unrelated; with the optional `cohabiting` field, which the CA and AU models now read, marriage changes nothing in
either country, and the false "marriage penalty" of about 16 % of AW is gone: kernel K8.)

**Timing pays wherever a benefit or a ceiling is non-convex.** The kernel's timing scanner found, without being told,
two-year bunching gains in Poland (up to 7,020 zł across the contribution ceiling, PL F16), Mexico (7,112 across the
subsidy cliff, MX F16), the Netherlands (up to €8,234 for a single parent across the end of the arbeidskorting taper,
NL F17), Australia (up to 12 % of AW for families, AU F14) and Canada (CA F6); Sweden's state tax makes
the opposite case, 800,000 kr in one year costs 72,458 kr more than two years of 400,000 (SE F11).

**Credits versus allowances.** A non-refundable credit is worth nothing to someone without tax to absorb it (kernel
`applyCredits_waste`): Norway's BSU and pension credits are lost where tax is low (NO F20); Sweden's pension-fee
credit only displaces the earned-income credit for working pensioners (SE F2); Spain's personal minimum is in effect a
credit at the bottom rate (ES F9, a theorem).

## 3. What the OECD's model does differently

One script checked all 20 models against the OECD Taxing Wages 2025 tables. Where they differ, the country files
traced every cause:
- **levies the OECD does not count as contributions**: New Zealand's ACC earners' levy, so NZ shows no employee
  contribution in OECD comparisons (NZ F1), Mexico's cesantía y vejez (MX F1), Poland's 3.65 % subkonto share
  (PL F1); with those left out the take-home pay of all eight households agrees in all three (K5);
- **regional defaults**: the OECD's Spanish regional tax is not Madrid's (ES F1); it leaves out Lazio's 2025 reliefs
  (IT F1);
- **rounding and periods**: the statutes' roundings are not applied (CZ F1, PL F2, IT F2, KR F7, IE F4) and monthly
  rules are annualised (CZ F2, MX F2), New Zealand's 2024-25 tax is day-weighted instead of the Act's composite rates
  (NZ F2);
- **assumptions**: an energy supplement closed to new claimants since 2016-17 (AU F2), Korean families with children
  under 8 (KR F1), Sweden's three conventions (SE F7);
- **undocumented assumptions found by reproducing the table**: Denmark's worker has an unstated 15 % occupational
  pension and keeps ATP in the tax bases (DK F3), and its basic-tax-credit line counts a one-earner couple's
  personfradrag three times (DK F2, presentation only);
- **errors**: Ireland's PRSI rise of 1 October 2025 not applied and USC booked before credits for one household type
  (IE F1, F2), a rounded long-term-care ratio in Korea (KR F6).
A reader comparing take-home pay across countries from Taxing Wages should know the employee-contribution line is
narrower than the pay slip in at least three countries.

## 3b. Owner-managers across the countries

`harness/search/owner.py`: a one-person company with a pre-tax profit of 1, 3 and 10 AW pays its owner the
salary/dividend split that leaves the most after company tax, employer contributions and the owner's personal taxes,
all profit paid out in the year; company side cited per country in `harness/search/company.json`. It reproduces the
country agents' own results where they exist (UK to the penny; SE, NO, KR, NZ, IE, DK; `harness/search/REGRESSION.md`).
Computed for 16 countries; not computed for FR, IT, PT, CA, where the employer contributions or the corporate rates
are not in the files (or, for CA, the model cannot tax a non-eligible dividend). Total tax as % of profit, best split
against all salary:

| | 1 AW: best salary share, tax best / all salary | 3 AW | 10 AW | design |
|---|---|---|---|---|
| IE | 100 %, 25.1 / 25.1 | 100 %, 42.9 / 42.9 | 100 %, 49.3 / 49.3 | classical, no relief: salary always best (Class S, no employer PRSI) |
| AU | any split: 23.5 | any: 36.6 | any: 43.9 | full imputation with refundable credits: the split does not matter |
| NZ | 28 %, 21.3 / 22.5 | 0 %, 30.6 / 31.6 | 0 %, 36.5 / 36.8 | imputation; dividends avoid only the ACC levy |
| DK | 100 %, 35.1 / 35.1 | 92 %, 46.3 / 46.9 | 98 %, 52.0 / 52.2 | salary, plus dividends inside the 27 % band |
| NO | 88 % (all salary), 35.1 / 35.1 | 39 %, 45.9 / 47.0 | 12 %, 49.8 / 51.8 | salary to the trinn 4 threshold, dividends above |
| KR | 56 %, 21.0 / 23.3 | 70 %, 30.1 / 32.7 | 90 %, 42.3 / 43.3 | salary, dividends up to the 20m-won separate-taxation limit |
| MX | 59 %, 20.7 / 21.7 | 36 %, 27.6 / 29.0 | 95 %, 33.1 / 33.1 | 30 % + 10 % on dividends: dividends only up to the lower brackets (employer side approximate) |
| SE | 40 %, 36.0 / 38.8 | 28 %, 46.9 / 51.8 | 8 %, 56.6 / 59.2 | 3:12: salary to 475,100 kr, dividends above |
| NL | 56 %, 30.0 / 33.2 | 21 %, 38.4 / 45.9 | 11 %, 45.3 / 48.4 | box 2; the gebruikelijk loon (56,000) is not enforced by the scan |
| UK | 22 %, 21.6 / 30.3 | 3 %, 44.1 / 46.7 | 78 %, 51.5 / 51.7 | small salary + dividends; salary wins again at the top |
| US | 21 %, 19.5 / 23.0 | 7 %, 28.1 / 30.2 | 2 %, 33.7 / 35.7 | C corporation 21 % + qualified dividends (federal only) |
| ES | 8 %, 33.1 / 38.4 | 2 %, 37.0 / 45.0 | 5 %, 39.6 / 44.1 | savings-base dividends far below salary with Régimen General contributions |
| CZ | 36 %, 34.4 / 39.9 | 13 %, 33.4 / 43.4 | 4 %, 33.0 / 39.7 | 21 % + 15 %: a flat 33 % against rising salary costs |
| PL | 0 %, 26.3 / 39.6 | 0 %, 26.3 / 48.5 | 0 %, 26.3 / 45.9 | 9 % + 19 % = 26.3 % flat at every profit (partial: see Needs checking) |
| DE | 10 %, 35.2 / 47.5 | 8 %, 42.0 / 48.2 | 2 %, 42.8 / 47.2 | lower bound (Gewerbesteuer at the minimum Hebesatz) |
| JP | 18 %, 17.3 / 31.2 | 5 %, 30.3 / 38.6 | 2 %, 46.8 / 48.2 | lower bound (local corporate taxes missing) |

What it shows. **Integration decides it.** Where the company's tax is credited to the owner (AU's refundable
franking, NZ's imputation) the split hardly matters; where dividends bear a low final rate on top of a low corporate
rate (PL 26.3 % flat, CZ about 33 %, ES, US, DE) a company paying dividends beats salary by 2 (US) to 22 (PL) points of
profit at 3-10 AW, and the gain grows with income: the owner-manager route is a way out of the top personal rate in exactly
the classical systems. Ireland is the exception that taxes dividends at full personal rates after 12.5 %, so salary
always wins. The Nordic dual systems police the boundary with salary requirements (SE 3:12, NO's 1.72 uplift), so
the best split pays salary up to a statutory threshold and dividends above it; the gains are real but bounded
(against all salary: SE 72,000-145,000 kr at 2-10 AW, NO up to 161,000 kr at 10 AW).

## 4. The most useful findings

Ranked, with evidence and audience, at the top of the report: `report/USEFUL20.md`.

## 5. Needs checking

A spot-check of every headline finding (kind loophole-new, gov-error or statute-fault) of the 13 countries with
findings, for an authority (statute or official source) and evidence (a Lean statement, a script or a quoted text)
(`report/spotcheck.py`, results in `report/spotcheck.json`). Almost all have both; the ones below do not yet carry
the claim their label makes, and should not be cited as findings until they do:

- **Novelty not searched, yet labelled loophole-new.** PT F10, F11, F12 (PT NOVEL.md: "no search could be run for
  these (the session's search limit was reached), so none is called new", while FINDINGS.md labels them
  loophole-new); AU F14 (a lead from the kernel's timing scanner, "not searched for in the literature"); NO F18
  ("not searched for in the literature"); MX F7, F8 (search recorded for F6 and F9, not for these two variants);
  KR F11, F15 (no search recorded) and KR F10 (the rule is public; only the size of the bands is new).
  The amounts are proved; only "new" is unsupported.
- **Authority not read.** NZ F7 (the IETC composite formula as printed in IRD's special report; "the Act's own text
  could not be read") and NZ F8 (the $70,000 personal-services threshold, taken from IRD guidance; "the threshold is
  in the Act; not read"). Both need the Income Tax Act 2007 text.
- **Reading-dependent.** CZ F5, F6 (assume the Úřad práce counts the tax actually withheld), NZ F9 (rests on IRD's
  web wording "entitled to and receive"), SE F3 (which tax a two-tax credit consumes first: a genuine gap, with
  Skatteverket's order as the adopted reading). Each needs the authority that settles the reading before it is
  advice.
- **Cause not verified.** NO F9 (the 2025 low-income limits raised retroactively in December 2025: the amendment is
  certain, its classification as a fault in the original amount is not).
- **Checks that passed, filed as errors.** AU F12 ("Consistency checks that passed"), PL F13 ("Government figures for
  2025 re-derived: all correct"), SE F9 ("The year's amounts follow their indexation rules"), CZ F13 ("checked,
  clean") are labelled gov-error or statute-fault; they are useful negative results and should not be counted in
  the countries' error totals.
- **Owner-manager scan against the country agents' own results** (`harness/search/owner.py`; not overridden):
  AU K9 / F16 says franked dividends cost $5,751 more than salary + SG at $200,000 (the super concession), but autax
  itself, with the same household as the AU agent's K6 case, taxes salary + SG and the franked dividend identically
  (income tax 56,138 vs 6,138 after the 50,000 credit, Medicare 4,000 each: the same net 139,862), so the scan finds no
  difference at any profit; one of the two needs checking. ES F13 finds a best salary of about 57,000 at 60,000-100,000
  of profit, the scan a salary near zero: F13 pays the salary as self-employment income with RETA ignored, the scan as a
  Régimen General wage with about 30 % employer contributions (company.json); which regime applies to a controlling
  socio decides it. NL K1 fixes the salary at the gebruikelijk loon (56,000, Wet LB 12a); the scan's best salary falls
  below it from 2 AW, so its NL gains (12,000-21,000) overstate what the law allows. CZ L04 (dividends only saves
  58,378 Kč at 1,000,000) is larger than the scan's all-dividends gain, which charges no health premium to an owner
  without salary (ZPVZP § 3b). PL's 9 % small-taxpayer rate is cited only from a policy paper (CATALOGUE K14), and a
  sole shareholder pays ZUS as self-employed (SUS art. 8 ust. 6 pkt 4), so the PL flat 26.3 % is unchecked.
  DE and JP are lower bounds (Gewerbesteuer at the 200 % minimum Hebesatz; Japan's local corporate taxes missing).
- **Draft notes still open** (evidence is complete; the error is awaiting the publisher): IE F1, F2 (OECD), IE F5-F7
  (Revenue, LRC), NL F4 (OECD, €0.18), KR F1, F2, F6. These are fine to cite as errors; they are listed so that no one
  reports them as acknowledged.
