# Court decisions as test cases (17 November 2026)

Question: administrative courts often state the facts and figures of an income-tax dispute (household, parts,
incomes, allowances, the tax, the court's own corrected figure). Each such statement is an independent,
authoritative expected answer. How many can be found in the open court data, and do Lean, M (Mlang) and the
DGFiP's production simulator reproduce them?

**Short answer.** Out of 1,748,519 administrative decisions (plus 533,323 Cour de cassation decisions), 79,653
mention income tax, 5,361 are income-tax disputes that state a figure of a kind a tax program computes, and 1,020 of
those (every one from income 2015 on that names parts or a figure-rich topic) were read. **None stated a complete
return; after review, one decision gives a complete return** (TA Poitiers, 7 Nov 2023, n° 2200177, income 2021, every
step from gross income to tax due). 76 decisions gave partial cases: 84 cases, 73 of them with a scorable figure,
**86 figures scored**. Lean reproduced **72 of 73** figures it could compute, M **82 of 85**, production **22 of
23**. **No Lean error was found.** The 4 figures some program missed are 1 unstated income in the decision (all three
programs give the same tax) and 1 court figure that departs from the statute's arithmetic, on which M is right
(Lean has no equivalent output there). There is also a set of court statements that no program can test: courts
splitting a year in two, sharing a child's part between unmarried cohabitants, two tribunals reading the veteran's
widow half-part in opposite ways, and arithmetic errors in courts' own capital-gain figures.

Files on the build server: scripts `~/fr/harness/court_*.py`, data `~/fr/data/court/` (stage outputs, decision texts,
`cases.jsonl`, `curation.json`, `triage_*.tsv`), runs `~/fr/runs/court/` (`results.jsonl`, `sim.jsonl` + saved
pages, `scores.json`, `score.txt`, `stats.md`, `case_table.md`), progress log `PROGRESS_courts.md`. Decisions are
cited by court, date and number only.

## 1. Funnel

| Stage | Count | How |
|---|---|---|
| Administrative decisions searched | **1,748,519** | DILA JADE dump of 2026-11-08 (573,525) + justice-administrative open data CE/CAA/TA 2021–2026 (1,174,994), the raw files already on the build server (AUTHORITY.md § 1). `harness/court_filter.py`, 12 processes, 10 min |
| ... mentioning "impôt sur le revenu" | **79,653** | JADE 55,392; open data 24,261 |
| Stage A: income tax + a computation topic | **25,803** | quotient familial/half-parts, frais réels/10 %, alimony, 157 bis, décote/61 €, CEHR, PFU/2OP, micro regimes, property income, capital gains, reductions/credits, plafonnement, quotient (163-0 A), liquidation words |
| Stage B: income-tax disputes stating a program-type figure | **5,361** | `harness/court_candidates.py`: dropped 17,298 with no such figure, 2,258 where income tax is not what is disputed, 132 orders without merits, 754 duplicates (JADE ∩ open data). 2,523 concern income 2015+, 589 income 2020+ |
| Read (triaged one by one) | **1,020** + 7 + 57 | five batches (below); a second pass over the 53,850 income-tax decisions without a named topic for a paragraph stating both a taxable income and a tax (`harness/court_filter_liq.py`: 7 found, 0 usable); the 57 Cour de cassation judgments with figures |
| Usable decisions | **0 complete, 76 partial** | readers' verdicts; after review, 1 complete return (Poitiers) and 1 complete for its question (Versailles n° 2303364) |
| Cases | **84** from 76 decisions | `data/court/cases.jsonl` (one per decision and income year) |
| Cases with a scorable figure | **73** from 67 decisions | 11 excluded on review (§ 4.4) |
| Figures scored | **86** | 53 numbers of parts, 33 amounts |

Reading batches (all decisions of stage B from income 2015, with these figure kinds; the 1,503 other 2015+ stage-B
decisions only mention reductions, capital gains or tax amounts without income, and were not read):

| Batch | Years | Selection | Read | Full | Partial | No program figure | Facts insufficient | Other tax | Procedural | Duplicate |
|---|---|---|---|---|---|---|---|---|---|---|
| b1 | 2020–2025 | parts / half-parts | 196 | 0 | 6 | 45 | 13 | 115 | 12 | 5 |
| b2 | 2020–2025 | income, tax, alimony, 10 %, CEHR, PFU, micro, quotient, décote, 157 bis | 269 | 0 | 11 | 127 | 64 | 29 | 30 | 8 |
| b3 | 2015–2019 | parts / half-parts | 144 | 0 | 41 | 20 | 42 | 23 | 11 | 7 |
| b4a, b4b | 2015–2019 | income + tax, CEHR, quotient, micro, plafonnement, PFU, 10 % | 411 | 0 | 18 | 308 | 30 | 10 | 31 | 14 |
| **all** | | | **1,020** | **0** | **76** | **500** | **149** | **177** | **84** | **34** |

"Other tax" is mostly property-tax and housing-tax exemptions that quote the income-tax parts and RFR ceilings.
"No program figure" is mostly half-part refusals that turn on facts the programs take as input (living alone, which
card, cohabitation) and reassessments whose only figures are the amounts of income added.

Judicial side. Judilibre's API needs a PISTE account and key, so it was not used. The Cour de cassation's own bulk
data is published by DILA alongside JADE and was downloaded (CASS 263.7 MB, INCA 696.0 MB, dumps of 2026-11-08):
533,323 judgments, 2,570 mention income tax, 892 are also criminal tax-fraud cases, 57 contain computation words.
All 57 concern income years before 2012 (most in francs) and state evaded amounts or declared income, never a
reproducible computation: **0 usable**.

## 2. Method

- **Reading.** Each batch was read by a separate reader agent (a Claude subagent) with the same written brief: a
  compact card per decision (`harness/court_cards.py`: the sentences with amounts or parts next to a computation
  word, and the operative part), then the full text of anything promising. The brief asked for strictness, the
  court's own version of the facts in `boxes` (the losing version in `alt_boxes`), every assumption written down, no
  invented incomes, and a quote of at most 25 words. The readers did not run any program. Every case was then
  reviewed by me before scoring; the edits are in `data/court/curation.json`, each with its reason (§ 4.3, 4.4).
- **Mapping.** Boxes of form 2042. Birth years the decisions do not give: declarants 1980, children 10 years before
  the income year (as in the other harnesses); the cases where age matters carry an explicit birth year. Where a
  decision states only a net income (revenu brut global, revenu imposable), it is entered in box 4BA (net property
  income), which enters the taxable income one for one; the input figure itself is then not scored.
- **Programs.** Lean `frtax` for income 2020–2025; M `bin/cal2019`…`cal2025` and the income-2018 release 6.7
  (`hist/bin/cal_sources2018m_6_7`). A figure that does not depend on the year's parameters (number of parts, an
  allowance between its floor and cap, the 66 % / 20 % donation rule, micro allowance rates) for income 2015–2019
  is run as **income 2020 in Lean and 2018 in M ("proxy year")**; other 2015–2017 figures are not scored (no M
  binary for those years). Production: income 2020–2025 only, 25 requests (24 cases + 1 probe), sequential, 1.2 s
  apart, under `flock ~/fr/.sim.lock`, pages saved in `runs/court/sim.jsonl.html/`.
- **Figures.** Direct outputs (parts, taxable income, gross tax, décote, reductions, tax after credits, CEHR) and
  derived ones measured by extra runs: the 10 % deduction (income − taxable income of that income alone), the
  art. 157 bis allowance (with the stated ages vs. under 65), deductible alimony (with vs. without, on a probe salary
  when the decision gives no income), micro allowances, a reduction (with vs. without its boxes), and the tax
  difference between two versions (`TAX_DELTA`). Tolerance: parts exact, amounts ±1 €.

## 3. Scoreboards

| Figure | n | Lean | M | Production |
|---|---|---|---|---|
| Number of parts | 53 | 53/53 | 53/53 | 9/9 |
| Gross tax (droits simples) | 4 | 1/1 | 4/4 | 1/1 |
| Tax difference between two versions | 4 | 2/2 | 4/4 | 2/2 |
| 10 % deduction | 4 | 2/2 | 4/4 | — |
| Deductible alimony | 3 | 2/2 | 2/2 | 2/2 |
| Art. 157 bis allowance | 3 | 3/3 | 3/3 | 3/3 |
| Micro-regime allowance | 3 | 3/3 | 3/3 | — |
| Taxable income | 2 | 1/1 | 2/2 | 1/1 |
| Income tax due | 2 | 1/2 | 1/2 | 1/2 |
| Décote | 1 | 1/1 | 1/1 | 1/1 |
| Donation reduction | 1 | 1/1 | 1/1 | — |
| Credits (home employment + union dues) | 1 | 1/1 | 1/1 | — |
| Revenu brut global | 1 | — | 1/1 | 1/1 |
| CEHR | 1 | 1/1 | 1/1 | 1/1 |
| Compensatory-allowance reduction (art. 199 octodecies) | 1 | — | 1/1 | — |
| Donations retained within the 20 % limit | 1 | — | 0/1 | — |
| Donations carried forward | 1 | — | 0/1 | — |
| **All** | **86** | **72/73** | **82/85** | **22/23** |

Where a program has no score: Lean has no input for quotient income (2 figures), the art. 199 octodecies reduction
(1) or the 2042 C capital-gain allowances (1), no output for the donation base and carry-forward or the revenu brut
global (3), and no year before 2020 except by proxy (6 figures of 2018–2019 that depend on the year). Production was
asked only for income 2020–2025 and only the direct figures (no variant runs for the 10 % and micro allowances).
48 of Lean's 72 matches and 49 of M's 82 are on a proxy year (almost all of them numbers of parts).

How strong the tests are:
- **One complete return.** TA Poitiers, 7 Nov 2023, n° 2200177, income 2021 (a withholding refund case in which the
  court works the whole liquidation): revenu brut global 24,935 €, art. 157 bis allowance 1,242 €, taxable income
  23,693 €, 1.5 parts, tax 919 €, décote 374 €, tax due 545 €. "Ce résultat devait ensuite être multiplié par le
  nombre de parts fiscales de l'intéressée (1,5), ce qui aboutit à un impôt de 919 euros". **Lean, M and production
  reproduce all six figures.**
- **Parts.** 28 of the 53 parts tests are 1 or 2 parts with no dependant and no half-part letter (a half-part the
  court refused): once the holding is encoded, the count is near-mechanical. The other 25 test the counting rules:
  alternate residence (1.25), widowers with children (2.5), the case L + case P non-cumulation (1.5), married couples
  with the veteran half-part, disabled dependants under the roof (6 parts for a couple with two children and two
  disabled dependants), attached adult children.
- **Amounts** come from 20 decisions; most are a single figure (an allowance, a deduction, a tax difference).

## 4. Mismatches and classes

### 4.1 Lean errors: none
No figure separates Lean from M or from production. The only figure Lean misses is one all three programs miss
(§ 4.3).

### 4.2 M or production departures: none against a court
M and production agree with every court figure they could compute, apart from the two shared misses below. One
holding probe (§ 5) shows a check none of the three programs makes.

### 4.3 Mapping or assumption issues: 3 (2 fixed before scoring, 1 unresolved)
- **Default birth year.** TA Orléans, 14 Apr 2023, n° 2100463 (income 2018): a single veteran granted the art. 195,
  1 f half-part. The first run used the runner's default birth year (1980) and gave 1 part in both Lean and M; the
  half-part requires the declarant to be over 74. With 1940 entered: 1.5 parts, = court.
- **Box W vs S.** TA Rennes, 8 Apr 2026, n° 2400289 (income 2015): a married veteran over 74. The reader used box W
  (the box for a person filing alone), giving 2 parts; for a couple the box is S: 2.5 parts, = court.
- **An unstated income.** TA Toulon, 22 Dec 2025, n° 2300633 (income 2021): divorced, two children, salaries 37,144 €
  and pensions 16,323 €; the court gives the tax after granting the parent-isolé half-part as 3,453 € ("ont généré
  un impôt de 3 453 euros après rectification du quotient familial"). Lean, M and production all give 3,010 € from
  the stated incomes, and 5,174 € without the half-part where the court has 5,617 €: both court figures are exactly
  443 € higher, so some item is not stated in the decision. The **difference** the court's holding makes, 2,164 €,
  is reproduced exactly by all three (the gap between the two quotient-familial caps).

### 4.4 Rules outside the models' scope (excluded from scoring or not representable)
- **Capital gains after the holding-period allowance** (5 decisions): the allowance is computed on form 2074 and
  entered in 2042 as an amount; no program computes it from a holding period.
- **One year split in two.** TA Melun, 7 Oct 2022, n° 1901937 (income 2017): a spouse living abroad, then joining
  the household; the court taxes 1 Jan–2 Oct on 1 part and 3 Oct–31 Dec jointly on 2 parts ("est établie sur la base
  d'un quotient familial de deux parts, en tenant compte, pour la période en cause, de leurs revenus"). An annual
  return cannot express it; both periods were scored separately (1 and 2 parts: all agree).
- **Cohabiting unmarried parents sharing a child's half-part** (CAA Lyon, 30 Jun 2026, n° 25LY00435, income 2018;
  TA Paris, 26 Jun 2025, n° 2303071, income 2020): the administration (Lyon) or the court (Paris) gives each parent
  1.25 parts, the alternate-residence quarter-part applied to parents who are not separated. Encoded as alternate
  residence, all programs give 1.25; TA Bordeaux n° 2302070 refused the same split where the mother had declared
  exclusive charge.
- **Transition credit (CIMR, 2018), treaty credits, 2017 non-resident gains outside the RFR** (TA Montreuil, 8 Dec
  2023, n° 2109227: the CEHR is nil because an art. 244 bis A gain was outside the 2017 RFR; from 2018 the RFR
  includes it, so no available program applies 2017's law), and a plafonnement case whose reductions are
  pseudonymised (CAA Versailles, 9 Jan 2025, n° 22VE02688).
- **The quotient system.** TA Versailles, 18 Dec 2025, n° 2303364 (income 2020): a 1.43 M€ stock-option gain under
  the quotient has no effect because the ordinary income is already in the top bracket ("son revenu net taxable hors
  quotient était supérieur à la plus haute fraction marginale"). M reproduces it (difference 1 €, rounding); Lean has
  no quotient input. Note for whoever maps quotient income: **M's box 0XX is a control-only field that its
  computation ignores**; the quotient lines are the 2042 C aliases (RAJ/NAJ for salaries, RAS/NAS for pensions,
  RVG/NVG for gains).

### 4.5 A court figure that differs from every program
- **TA Nantes, 26 May 2023, n° 2004003 (income 2015, donations).** The court states the household's "revenu
  imposable de 64 575 euros" and concludes, "Ainsi, les dons [...] l'étaient dans la limite de 13 376 euros",
  carry-forward 1,397 €. 20 % of 64,575 € is 12,915 €, carry-forward 1,858 €; M (2018 rules, unchanged on this
  point) computes exactly 12,915 € and 1,858 €. 13,376 € is 20 % of 66,880 €. Either the 20 % base included income
  taxed at proportional rates that the decision does not mention (the BOFiP includes it in the "revenu imposable" of
  art. 200), or the court's figure is wrong; the outcome (rejecting a 3,479 € carry-forward) does not change. Lean
  outputs only the reduction actually imputed, which the tax caps here, so it has no equivalent figure.

Court figures that contradict the statute's own arithmetic, outside the programs' scope (form 2074 allowances), found
by the readers and checked by hand:
- CAA Versailles, 26 Jun 2025, n° 23VE00322: "le montant de la plus-value, après abattement, en 2015 s'élève à
  150 345 euros" — that is 65 % of 231,300 €, the allowance itself; the gain after a 65 % allowance is 80,955 €. For
  2017 it gives 420,656 € where 35 % of 1,167,166 € is 408,508 €. Neither changes the outcome (both stay under the
  three-year average income that decides the quotient question).
- CAA Lyon, 6 Nov 2025, n° 23LY01245: 35 % of 418,880 € is 146,608 €, the court writes 146,605 €, and its operative
  part names 418,800 € and 418,000 € for the same base.
- CAA Lyon, 5 Jun 2025, n° 23LY03190: (968,939 − 52,000 − 47,213) × 35 % = 304,404 €, the court upholds 313,504 €
  (fees or a different cost base may be unstated).
- CAA Bordeaux, 3 Jul 2025, n° 23BX01975: the appeal's gain of 1,059,216 € reproduces the 29,869 € CEHR exactly
  (Lean, M and production all give 29,869 €); the first-instance judgments' 1,059,105 € does not.
- Parameters cited for the wrong year, without effect on the outcome: TA Toulouse, 26 May 2026, n° 2307032 (income
  2021) cites the art. 196 B amount "dans sa rédaction applicable au litige" as 5,959 €, the income-2020 figure
  (2021: 6,042 €; the deduction was refused anyway); TA Versailles, 29 Nov 2022, n° 2100638 (income 2019) cites a
  72,600 € micro threshold, the figure from income 2020 (70,000 € for 2019); the rents were far below either.

### 4.6 Courts disagreeing with each other
- **The veteran's widow half-part (art. 195, 1 f).** TA Besançon, 30 Apr 2024, n° 2200884: refused because "son époux
  est décédé avant d'avoir atteint l'âge de 74 ans, âge requis". TA Nantes, 26 May 2025, n° 2103500: refused
  because the husband "n'a jamais bénéficié de la demi-part supplémentaire [...] de son vivant", describing widows of
  husbands who died before 74 with a veteran's pension as eligible. The programs take the condition as an input
  (box G), so they cannot side with either; both widows get 1 part in all programs, as both courts held.
- **Separation during the year.** TA Nice, 8 Apr 2026, n° 2304984 (income 2018): a divorce agreement made effective
  from July 2018 is ignored; the court applies the 1 January situation and grants the couple 3 parts (married, two
  children) instead of the administration's 2. Contrast TA Melun's split year above.

## 5. Holding probes: rules the courts state, run on synthetic returns (income 2020)

| Holding | Probe | Lean | M | Production |
|---|---|---|---|---|
| L and P half-parts do not cumulate; the tax is capped as for P, not L (TA Bordeaux, 16 Mar 2023, n° 2101566; TA Toulouse, 4 Oct 2022, n° 2005467: "les deux demi-parts [...] ne peuvent se cumuler") | single, 100,000 € salary, L+P vs P vs L | 1.5 parts; L+P = P (21,249 €), L alone 21,881 € | same | — |
| An adult child attached to the household cannot also give an alimony deduction (TA Lyon, 28 Jan 2025, n° 2304314) | divorced, case T, one attached adult child + 5,000 € in 6EL | both granted: 2 parts and the deduction (17,065 €) | same | same (17,065 €, 1 request) |
| Unmarried cohabiting parents may share a child's part (§ 4.4) | single, one child in 0CH vs 0CF | 1.25 / 1.5 | same | — |

The second probe is the one rule the courts enforce that **no program enforces**: the form cannot say whether the
attached child and the alimony recipient are the same person, and all three programs, production included, grant
both. That is consistent with how the programs work (they take the return as declared); the check happens in audit.

## 6. Limits

- **Yield.** Courts rarely restate a household and its incomes: of 1,020 decisions read, none did in full, and the
  one complete return comes from a withholding dispute, not an assessment dispute. Most scored figures are numbers of
  parts, and over half of those are near-mechanical once the holding is encoded. This benchmark mainly confirms the
  parts and allowance rules; it says little about the scale, the décote or the caps beyond the Poitiers return, the
  Toulon tax difference and 4 gross-tax figures.
- **Coverage.** Only stage-B decisions about income 2015 onward with parts or figure-rich topics were read (1,020 of
  2,523); the other 1,503 (reductions, capital gains or bare tax amounts) and the 2,838 earlier or undated ones were
  not. Stage B's regular expressions can miss decisions that phrase figures differently. JADE's daily increments of
  9–16 Nov 2026 were not taken.
- **Readers.** Extraction was done by language-model reader agents under one brief, then reviewed: 2 box mappings
  were wrong (§ 4.3) and 11 cases were excluded or trimmed on review (`curation.json`). Other errors of that kind
  may remain in figures where all programs agreed with the court; a wrong mapping that happens to give the court's
  answer would not show.
- **Years.** No M binary for income 2015–2017, so only year-independent figures of those years are scored, on proxy
  years (Lean 2020, M 2018). Lean covers 2020–2025 only.
- **Production** was asked for 24 returns (income 2020–2022) plus 1 probe, well inside the 40-request budget; the
  readers found no complete 2023–2025 case.
- **Judilibre** was not queried (API key required); the Cour de cassation bulk dumps were, with no usable judgment.

## 7. Files (the build server `~/fr`, mirrored locally)

| File | What |
|---|---|
| `harness/court_filter.py` | stage A over the JADE dump and the justice-administrative zips |
| `harness/court_cass_scan.py` | Cour de cassation CASS/INCA dumps: criminal tax-fraud judgments with figures |
| `harness/court_candidates.py` | stage B: income-tax disputes stating program-type figures; `data/court/candidates.jsonl` |
| `harness/court_filter_liq.py` | second pass: liquidation paragraphs in the remaining income-tax decisions |
| `harness/court_cards.py` | the reading cards |
| `harness/court_run.py` | `merge` (cases + curation), `run` (Lean, M, variant runs), `sim` (production), `score` |
| `harness/court_stats.py` | funnel and scoreboard tables (`runs/court/stats.md`) |
| `data/court/cases.jsonl` | the 84 cases: citation, question, facts, boxes, assumptions, court figures, holding, winner, quote |
| `data/court/curation.json` | every review edit, with its reason |
| `data/court/triage_b*.tsv` | the verdict and reason for each of the 1,020 decisions read |
| `runs/court/scores.json`, `case_table.md` | each figure: court value, Lean, M, production |
