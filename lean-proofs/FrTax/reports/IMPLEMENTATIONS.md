# Other implementations of French income tax — survey and head to head (17 November 2026)

Companion to RESULTS.md / FINDINGS.md. Lean (lean/FrTax), M (DGFiP M code via Mlang, `bin/cal2019..2025`) and
OpenFisca-France are covered there; Catala (DGFiP/Inria `impot_revenu`) is covered by a separate piece of work and is not
repeated here. Referee: the DGFiP production simulator (calc-2021 … calc-2026 = income 2020 … 2025).
Files: harness `harness/impl_*.py|.R|.mjs`, outputs `runs/impl/<key>/`, installs `refs/impl/` (the build server), progress
`PROGRESS_impl.md`.

## 1. Survey

Facts from the repositories themselves (GitHub/GitLab APIs, package metadata, the code), checked 17 November 2026.
"Runnable here" = run on the build server without sudo.

| # | Implementation | Language | Maintainer | Licence | Last activity | Years / scope | Derived from | Runnable here |
|---|---|---|---|---|---|---|---|---|
| 1 | **Publicodes `modele-social`** 11.1.0 (npm; `modele-social/règles/impôt.publicodes` in betagouv/mon-entreprise, 337 ★) | Publicodes (YAML DSL) on a JS engine | Urssaf / beta.gouv.fr (mon-entreprise team) | MIT | 2026-11-17 (repo); npm 2026-07-16 | Parameters for payment years 2021–2026 (income 2020–2025). Family situation (single/couple/widow), n children, single-parent half part, one salary (10 % allowance), "other taxable income", scale, QF cap, décote, CEHR, neutral PAS rate grids, PFU on dividends. No pensions allowance, art. 157 bis, half-parts L/P/F/W/S/G, shared custody, reductions, credits | Independent (hand-written; each rule cites service-public / BOFiP / Légifrance) | **Yes** (node 22 tarball + `npm i modele-social publicodes`) |
| 2 | **INES** (Insee, Drees, Cnaf), gitlab.com/insee_drees_cnaf/ines-public, tag Ines_2024.1 | R (since vintage 2023; vintages 2016–2022 in SAS on Adullact) | Insee / Drees / Cnaf "chargés de modèle" (public mirror of a closed GitLab) | Programs CeCILL 2.1; parameters ODbL (+ DbCL) | 2026-06-16 | Legislation up to the tax paid in 2025 (income 2024). Box-level: ~913–1,013 2042 boxes read by the tax chain per year (incl. reductions, credits, CEHR, PFU, quotient). Microsimulation on the ERFS survey (restricted data) | Independent (statistical model, written from CGI/brochure) | **Yes, without SAS**: R 4.4 via micromamba; its tax chain driven on box tables built by our wrapper (the ERFS input is not public) |
| 3 | **EUROMOD** FR country model (JRC), release J2.0+ (Feb 2026), systems FR_2006…FR_2025 | Model: XML policy rules; engine C# (.NET); Python connector `euromod` 0.5.1 | European Commission JRC (FR model by national team) | Rules CC BY 4.0; engine source EUPL-1.2 (github.com/ec-jrc/JRC-EUROMOD-software-source-code); classic installer EULA | Engine 2026-10-23; model Feb 2026 | IR policy `tin_fr` (17 functions: scale, QF, "imax" cap, complementary reduction, décote, CEHR) + `tinkt_fr` (flat-tax branch); survey-style inputs (EU-SILC, restricted; synthetic FR training data shipped) | Independent | **Yes** (officially Windows-only; the connector wheel ran on Linux via pythonnet + user-level .NET 8 runtime) |
| 4 | OpenFisca-France (319 ★) | Python | OpenFisca community / LexImpact | AGPL-3.0 | 2026-11-16 | see RESULTS.md (#6, 7, 11, 12, 16) | Independent | already tested (RESULTS) |
| 5 | LexImpact (Assemblée nationale), leximpact-socio-fiscal-api/ui | Python/JS | Assemblée nationale (LexImpact) | AGPL-3.0 | API mirror 2021-05; app active | Uses OpenFisca-France (+ reforms) | OpenFisca-France | Not run separately (same engine; FINDINGS F4: three LexImpact tests follow OpenFisca's art. 157 bis bug) |
| 6 | TAXIPP (IPP), gitlab.com/ipp/partage-public-ipp/taxipp, v2.4.2 | Python (simulation) + Stata (matching) | Institut des politiques publiques | AGPL-3.0 with additional terms | 2026-08-20 | Pins `openfisca-france==174.2.6`; administrative data via CASD (restricted) | OpenFisca-France | Not run separately (its tax rules are OpenFisca-France 174.2.6; its data are confidential) |
| 7 | Catala `impot_revenu` (DGFiP/Inria, CatalaLang/catala-examples) | Catala | Inria / DGFiP | Apache-2.0 | active | — | Independent (literate, from CGI) | Other agent |
| 8 | Mlang + Coq semantics of M + Z3 prototype (Merigoux, Monat, Gaie 2019; Merigoux, Monat, Protzenko 2021) | OCaml / Coq / Python | Inria → DGFiP (MLanguage/mlang 204 ★, Adullact mirror) | GPL-3.0 | 2026-01-20 | the M code | M | Already "M" here; the Coq semantics proves properties of M, not of the tax |
| 9 | #CodeImpot 2016 translations: openfisca/calculette-impots-m-language-parser (AST, 5 ★), etalab/…-m-language-parser (15 ★, 2020-02), openfisca/calculette-impots-python (generated Python, 9 ★), …-vector-computing (NumPy), …-web-api, …-web-explorer | Python / Jupyter | Etalab / OpenFisca (C. Benz et al.), fork michelbl (2017) | AGPL-3.0 (openfisca) / CeCILL-2.1 (etalab) | 2016-04-01 (openfisca); 2020-02 (etalab) | Income 2014 M sources only (released 1 April 2016) | M | Not head to head: income 2014 only, and no referee for that year here (Lean 2020–2025, Mlang drivers 2019–2025, production calc-2021+) |
| 10 | M source mirrors (etalab/calculette-impots-m-source-code 21 ★, openfisca/… 35 ★, Adullact dgfip/ir-calcul) | M | DGFiP / Etalab | CeCILL | 2020 / 2025 | — | is M | sources, not a separate implementation |
| 11 | PolicyEngine | Python | PolicyEngine | AGPL-3.0 | — | **No France model** (100 public repos: US, UK, Canada, …; `policyengine-core` is a fork of OpenFisca-Core) | — | n/a |
| 12 | IPP Barèmes | spreadsheets | IPP | — | — | Parameters only, no calculator | — | n/a |
| 13 | GitHub calculators with any coverage of scale + QF + décote: nbald/simulateur-impots (LFI programme, 14 ★, no licence, 2024-06), clairfisc/calculateurs-fiscaux (3 ★, AGPL, active), jffourmond/freelance-impot (3 ★, 2019), adauguet/ImpotRevenu (Java, 2015), bertrand-benoit/incomeTaxCalculator (shell, GPL, 0 ★, moved to GitLab), ~60 others with 0–2 ★ | JS/TS/Java/shell | individuals | mostly none | various | barème + QF at most | Independent | Skipped: none above 15 ★; single-author toys or reform demonstrators, as the brief asked |
| 14 | Coq / Isabelle / F* / Blawx / LegalRuleML models of French IR | — | — | — | — | **None found** beyond #7, #8 and our Lean model | — | — |

INES licence detail: `Licence_Programmes.txt` (CeCILL V2.1, "© Logiciel élaboré par l'État, via l'Insee et la Drees");
`Licence_Parametres.txt` (ODbL). Older SAS vintages: access on request through Adullact. INES is runnable without SAS
since the 2023 R rewrite; the full pipeline still needs the ERFS (Insee, restricted), so only its tax functions can be
run on non-ERFS data, as done here.

## 2. How each was run

| | Publicodes | INES | EUROMOD |
|---|---|---|---|
| Install (no sudo) | node 22.11 tarball; `npm i modele-social publicodes` (2 packages, seconds) | micromamba + conda-forge `r-base 4.4` and 12 packages (~5 min, 1.6 GB); `git clone` | `.NET 8` runtime by `dotnet-install.sh` into `refs/impl/euromod/dotnet`; venv `pip install euromod` (pythonnet); model zip 206 MB (1.8 GB unpacked); `PYTHONNET_RUNTIME=coreclr` and an absolute model path |
| Converter | `impl_publicodes.py`: boxes → Publicodes situation (`date` = income year + 1; `salarié . rémunération . net . imposable` = 1AJ; 4BA → "autres revenus imposables") | `impl_ines_run.R` + `impl_ines.py`: boxes → INES's three ERFS-shaped tables (household SIF fields, long personal and household box tables) with INES's own per-year box dictionary (`maj_dico_cases_fiscales`); runs `calcule_rbg → charges → part → prelev_forf → deduc → impot_du` unchanged except that `calcule_impot_du` also returns its intermediate figures | not box-based (gross monthly survey incomes): `impl_euromod.py` runs FR_2021…FR_2025 on the 2,397 synthetic training households and compares, per fiscal unit, EUROMOD's tax after QF cap and décote with Lean `tableTax` at EUROMOD's own taxable income, parts and situation |
| Scope used | one salary or none, 4BA, 0AC/0AD/0AM/0AO/0AV, 0CF, 0BT | every box its tax chain reads that year + all family boxes, income 2020–2024 | the scale/QF/décote stage only |
| Outputs compared | parts, RNI, RFR, gross tax after cap, décote, tax after décote, CEHR | same + net tax (impot_du − CEHR) where no flat-tax income (INES books the PFU in the payment year from a lagged row) | tax after cap and décote |

Scoring: an amount counts as equal when the implementation's value rounded to the euro (0.50 up) equals the reference;
parts must be equal. Referees: printed brochure cells, stated figures of official examples, Lean and M (which agree on
all of these returns), and production answers (1,563 saved answers from earlier work, reused when the return is in
scope, + 8 new requests).

## 3. Head-to-head scoreboards

### Publicodes modele-social 11.1.0

| Benchmark | In scope | Tax after cap and décote exact | within 2 € | Every compared figure exact |
|---|---|---|---|---|
| Brochure scale tables 2020–2025 (printed cells) | 13,013 of 20,489 | 9,697 (74.5 %) | 10,174 (78.2 %) | — |
| Official worked examples | 13 of 46 | — | — | 8/13 stated; 12/13 vs Lean and M |
| Random households 2020–2025 (runs/final + runs/old) | 4,646 of 118,616 | 4,153 (89.4 %) vs Lean = M | 4,630 (99.7 %) | 1,670 (35.9 %); parts 100 %, RNI 92.8 % |
| Statutory edges (boundaries.py) | 36 of 132 | 25 (69.4 %) | 26 | 13 (36.1 %) |
| Saved production answers in scope | 96 | 72/94 (76.6 %) | 84/94 | 53/96 |
| New production requests | 2 | 0/2 (widow cap: +5,575 €, +5,625 €) | 0/2 | — |
| Speed (engine, one core) | | 1.3–1.5 ms / household | | |

### INES 2024.1 (income 2020–2024)

| Benchmark | In scope | Tax after cap and décote exact | within 2 € | Every compared figure exact |
|---|---|---|---|---|
| Brochure scale tables 2020–2024 | 11,259 | 10,638 (94.5 %) | **11,259 (100 %)** | — |
| Official worked examples | 14 | 1/4 stated (3 are 8TI effective-rate cases); IDRS 7/7 | | 11/14 stated; 11/14 vs Lean |
| Random households 2020–2024 | 59,409 of 69,443 | 50,518 (85.0 %) vs Lean = M | 58,288 (98.1 %) | 33,996 (57.2 %); parts 99.5 %, RNI 82.9 %, RFR 72.1 % |
| Statutory edges | 63 of 66 | 59 (93.7 %) | 63 (100 %) | 54 (85.7 %) |
| Saved production answers in scope | 820 (89 refused by production left out) | 626/745 (84.0 %) | 705/745 (94.6 %) | 509/820 (62.1 %) |
| New production requests | 6 | 0/6 side with INES; 6/6 = Lean = M | | |
| Speed (vectorised R, per household, excl. 3–5 s R start) | | ~1.0–1.5 ms | | |

### EUROMOD J2.0+ (FR_2021…FR_2025 = income 2020…2024; tax after cap and décote vs Lean `tableTax`)

| System | Fiscal units | Equal | within 2 € | Units with tax > 0: equal |
|---|---|---|---|---|
| FR_2021 | 3,279 | 2,019 (61.6 %) | 2,163 | 862/2,122 |
| FR_2022 | 3,279 | 2,061 (62.9 %) | 2,144 | 852/2,070 |
| FR_2023 | 3,279 | 2,088 (63.7 %) | 2,102 | 834/2,025 |
| FR_2024 | 3,279 | 2,084 (63.6 %) | 2,146 | 762/1,957 |
| FR_2025 | 3,279 | 1,789 (54.6 %) | 2,057 | 456/1,946 |

EUROMOD runs the whole tax-benefit system for 2,397 households (7,482 people) in 0.9–3.5 s (≈0.4–1.5 ms per household,
everything included). Lean `tableTax` equals all 20,489 printed brochure cells (RESULTS #2), so it stands for the DGFiP
scale here; no production request was spent on EUROMOD because its inputs cannot be turned into 2042 boxes.

## 4. Disagreement classes and verdicts

Production column: "saved" = settled by answers already in `runs/*.jsonl`; "new" = requests made here
(`runs/impl/sim.jsonl`, 8 requests, flock, 1.2 s apart).

### Publicodes

| Class | Count (bench) | Example | Statute | Production | Verdict |
|---|---|---|---|---|---|
| P1 Widow(er) with children: QF cap computed against 1 part and only the children's half-parts; the widow's own extra part gives nothing once the cap binds; no widow's complementary reduction | 2,839 printed cells; 21 random | 2024, widow, 1 child, 93,100 €: Publicodes 20,325 €, Lean = M = INES 14,750 € | art. 194 I (extra part), 197 I 2 (cap per half-part beyond one part; complementary reduction for widow(er)s) | new: 14,750 € (2024), 15,152 € (2025, 2 children, Publicodes 20,777 €) | **Implementation error** (up to ~5,600 € too much tax) |
| P2 No rounding to the euro of the 10 % allowance, gross tax, décote | 477 cells; 644 random; 18 saved | single, 1AJ 22,386 € (2024): 493.12 → 493, Lean = M 494 | art. 193, 1657-1; BOI-IR-LIQ-20-20-40 | saved: = Lean on all 18 | **Implementation error** (±1 €) |
| P3 Art. 157 bis allowance (65+, low income) absent | 10 random; 10 edges; 10 saved | single born 1950, 4BA 17,509 € (2024): tax 72 €, prod 0 € | art. 157 bis | saved: = Lean on all 10 | **Scope** (not modelled; Publicodes is an employer/self-employed estimator) |
| P4 Décote reported before its cap at the gross tax (tax after décote right) | 2,181 random; 12 edges/saved | no income: décote 889 € | reporting only | saved: production prints the capped décote | Reporting, no tax effect |

### INES

| Class | Count (random / saved) | Example | Statute | Production | Verdict |
|---|---|---|---|---|---|
| I1 No rounding to the euro (allowances, tax, décote) | 13,184 / 128; 621 printed cells (all ±1–2 €) | — | art. 193, 1657-1 | saved: = Lean | Implementation (microsimulation convention) |
| I2 RFR: exempt overtime added back gross | 6,257 / 57 | 1AJ 13,955, 1GH 4,470 (2024): INES RFR 17,030, prod 16,582 | art. 1417 IV 1° c ("montant net") | saved: = Lean | **INES error** (RFR only) |
| I3 RFR: dividends taxed at the scale (2OP) added back after the 40 % allowance | 2,316 / 48 | 1AJ 30,000, 2DC 10,000, 2OP (2024): INES 33,000, prod 37,000 | art. 1417 IV 1° (allowance of art. 158, 3, 2° added back) | new + saved: = Lean | **INES error** (RFR only) |
| I4 RFR: deductible charges (6DD…) not subtracted | 661 / 11 | 1AJ 30,000, 6DD 2,000: INES 27,000, prod 25,000 | art. 1417 IV (RFR from the revenu net global) | new + saved: = Lean | **INES error** (RFR only) |
| I5 Micro-entrepreneur flat levy (5TA/5TB/5TE): INES decides the option from its lagged RFR | 1,743 / 49 | 5TB 5,462 couple: RNI +2,731 € | art. 151-0 (option conditioned on N−2 RFR) | saved: = Lean | **Mapping/scope** (INES needs a multi-year panel) |
| I6 Levies at source (2DH life insurance, 3VZ property gains, PFU) outside INES's `impot_du` | 502 + 12 | 2DH 2,422: net tax −183 € | art. 125-0 A, 150 U, 200 A | — | **Scope/mapping** (INES books them elsewhere / in the payment year) |
| I7 Widow(er) with only shared-custody children: no widow's extra part | 165 / 2 | widow, 0CH 2, 1AJ 50,000 (2024): INES 1.5 parts, tax 4,875 €; prod 2.5 parts, 1,708 € | art. 194 I (the widow(er)'s extra part with children at their charge, shared residence included) | new: = Lean | **INES error** (calcule_part tests `npcha > 0`, ignoring `sif_nbh`) |
| I8 Case W half-part granted with case T and dependants | 106 / 1 | single 0AW 0BT 0DJ 1, 1AS 45,000 (2024): INES 2.5 parts, 1,006 €; prod 2.0, 1,924 € | art. 195, 1, f (only for those without dependants); 194 II | new: = Lean | **INES error** |
| I9 Invalidity/veteran half-part with a binding QF cap: complementary reduction too large | 134 random | single 0AP born 1934, pension 52,083 € + 4BA 44,489 € (2024): INES 17,400 €, prod 18,160 € | art. 197 I 2 (complementary reduction limited to the cap's excess) | new: = Lean | **INES error** (760 € too little tax) |
| I10 Exempt overtime cap 5,000 € for income 2020 | 29 / 1 | 1AJ 30,000, 1GH 7,000 (2020): INES RNI 28,800, prod 27,000 | art. 81 quater I as amended by loi 2020-473 art. 4 (7,500 € for 2020) | new: = Lean | **INES parameter error** |
| I11 Actual expenses above the salary capped at the salary | 5 / 11 | 1AJ 6,939, 1AK 9,281, pension 28,180 (2020): RNI +2,342 € | art. 83 3°, 156 I | saved (F7): production nets the excess = Lean | **INES error** (the error Lean had before F7) |
| I12 Art. 157 bis exactly at the lower threshold (17,510 € in 2024): INES gives the half allowance | 1 edge / 1 | single born 1950, 4BA 17,510: INES RNI 16,112, prod 14,714 | art. 157 bis ("n'excède pas") | saved: = Lean | **INES error** (`<=` on the wrong band) |
| I13 Exempt income for the effective rate (8TI) not used | 3 examples | 8TI 45,000 | art. 197 C | — | Scope |

### EUROMOD

| Class | Count (per system, of 3,279 units) | Example | Statute | Verdict |
|---|---|---|---|---|
| E1 Décote computed from the wrong variable: `tin_fr` takes 45.25 % of `i_tingt1` — the flat-tax branch's tax (`tinkt_fr`), already after its own décote — instead of the gross tax `i_tingt2` it tests; décote too large, tax too low | 874–1,064 | FR_2025, single, taxable 17,119 €: EUROMOD 0 €, statute 9 € (décote 884.8 instead of 609.4) | art. 197 I 4 a (décote = forfait − 45.25 % of the tax from the scale) | **Implementation error** |
| E2 Single parent (case T) with one child: QF cap doubled (7,408 € = 2 × 3,704 € for income 2020) | ~40–50 per system | FR_2021, T 2 parts, 53,056 €: 3,929 € vs 6,219 € | art. 197 I 2 (single parent's first child: one full part capped at 3,704 € for income 2020) | **Implementation error** |
| E3 No rounding to the euro | 14–268 | | art. 193, 1657-1 | Implementation (±1–2 €) |

No class in any of the three implementations has production siding with the implementation against Lean/M: every
class with a production answer (the 8 new requests and the saved answers) gets the Lean answer, which is M's on these returns.

## 5. Pros/cons facts

| | Publicodes modele-social | INES | EUROMOD (FR) | (for reference) Lean / M / OpenFisca |
|---|---|---|---|---|
| Years | income 2020–2025 (payment-year parameters 2021–2026) | income ≤ 2024 (INES 2025); vintages back to 2016 (SAS) | systems 2006–2025 (= income ≤ 2024) | Lean 2020–2025; M 2010–2025 sources; OpenFisca multi-decade |
| Outputs | parts, revenu imposable, impôt brut, décote, IR, CEHR, PAS neutral rates | full chain: RBG→RNG→RNI→RFR, parts, PFU, reductions, credits, CEHR, recovery threshold, PAS rate | IR after QF/décote, CEHR, flat tax; whole tax-benefit system | see RESULTS |
| Size | `impôt.publicodes` 1,455 lines (rules file); package 656 rules | `07_impot_revenus.R` 5,089 lines (+ dictionary 1,347 boxes, parameter workbook) | `tin_fr` 17 functions (FR.xml, all policies: 57 MB) | Lean `lean/FrTax`; M ~ir-calcul |
| Statute ↔ code | each rule has `références` URLs (service-public, BOFiP, Légifrance) | comments name CGI articles and brochure; parameter sheet gives a source per parameter | comment per function; parameter Excel "policy" sheets | Lean: article per definition |
| Proofs | none | none (testthat unit tests of the run engine only) | none | Lean: kernel-checked theorems |
| Speed on the build server (one core) | 1.3–1.5 ms / household (engine) | ~1–1.5 ms / household vectorised, + 3–5 s R start | ~0.4–1.5 ms / household for the whole model | Lean 14 µs; M 0.32 ms; OpenFisca 0.6 ms |
| Setup | trivial (node + 2 npm packages) | moderate: R + 12 packages; no public input path for a single return (our 160-line wrapper builds ERFS-shaped tables) | moderate: .NET runtime + pythonnet; Linux unsupported officially but works; inputs are survey variables, not boxes | — |
| Licence | MIT | CeCILL 2.1 (programs), ODbL (parameters) | CC BY 4.0 (rules), EUPL-1.2 (engine), EULA (installer) | Lean ours; M CeCILL; OpenFisca AGPL-3.0 |
| Maintainer / activity | Urssaf beta.gouv team, daily commits | Insee/Drees/Cnaf, monthly public drops Nov–Apr | JRC, yearly model releases, engine monthly | — |
| Accuracy vs DGFiP (this work) | scale cells 74.5 % exact (78.2 % ≤ 2 €); random in scope 89.4 % exact tax (99.7 % ≤ 2 €); widow(er)s with capped QF up to ~5,600 € too much | scale cells 94.5 % exact, 100 % ≤ 2 €; random 85.0 % exact tax (98.1 % ≤ 2 €); RFR 72 % (I2–I4); 6 production-confirmed errors | 55–64 % of fiscal units exact; décote error in 874–1,064 units per system | Lean 699/700 random production; M 691/691 computed |

## 6. What could not be run, and why

- **Catala**: handled by the other agent.
- **#CodeImpot 2016 Python translations of M** (calculette-impots-python, m-language-parser, vector-computing): they
  carry the income-2014 M code only; nothing here can referee 2014 (Lean 2020–2025, Mlang drivers 2019–2025, production
  simulator from calc-2021). Being translations of M, they would test M 2014, not a new reading of the law.
- **INES full pipeline** (and its own validation against aggregates): needs the ERFS (Insee, restricted). Only its tax
  functions were run, on tables our wrapper builds; classes I5 and I6 come from that bypass, not from INES's law.
- **EUROMOD on our returns**: inputs are gross monthly survey incomes (EU-SILC naming), not 2042 boxes; no exact
  inverse from net taxable salary to gross pay, so only the tax stage was compared, on EUROMOD's training data. The
  EU-SILC input data need a Eurostat research proposal.
- **TAXIPP**: its tax rules are OpenFisca-France 174.2.6 (pinned); its data are CASD-confidential.
- **LexImpact**: OpenFisca-France underneath; already covered by the OpenFisca results (F4).
- **PolicyEngine**: has no France model.
- GitHub calculators: none with more than 14 stars; skipped as toys/reform demonstrators.

## 7. Reproduce

```
cd ~/fr/harness
python3 impl_score.py impl_publicodes          # bareme,examples,random,bound,sim -> runs/impl/publicodes/
python3 impl_score.py impl_ines                # -> runs/impl/ines/  (R: refs/impl/mamba/renv)
python3 impl_classify.py publicodes; python3 impl_classify.py ines
cd ~/fr/refs/impl/euromod && DOTNET_ROOT=$PWD/dotnet PYTHONNET_RUNTIME=coreclr ./venv/bin/python ~/fr/harness/impl_euromod.py
flock ~/fr/.sim.lock python3 impl_sim.py       # production requests, runs/impl/sim_cases.jsonl -> runs/impl/sim.jsonl
```
