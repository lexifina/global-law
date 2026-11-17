# French income tax: Catala head-to-head with Lean, M (Mlang) and OpenFisca (17 November 2026)

Catala: the DGFiP/Inria proof of concept `impot_revenu` in CatalaLang/catala-examples (master 9e251b9, 28 October
2026; imported from the DGFiP's ir-catala; CeCILL 2.1 header and LICENSE), compiled with Catala 1.3.2. Referee: the
DGFiP production simulator (calc-2023.cgi = income 2022, calc-2024.cgi = income 2023). Harness `harness/catala_*.py`,
driver `catala/ocaml/driver/catala_ir.ml`, outputs `runs/catala/` on the build server.

## 1. Setup

| Item | What was done | Time / result |
|---|---|---|
| Catala version | catala-examples pins `catala {= 1.0.0~alpha}` in its opam file and its CI uses the latest CI image; the checkout (28 Oct) sits between releases 1.3.0 (1 Oct) and 1.3.2 (16 Nov). 1.3.2 used; it builds and passes every impot_revenu test. | — |
| Toolchain | Local opam switch `~/fr/catala/sw` (no sudo): OCaml 4.14.2, then `opam install catala.1.3.2` (48 packages). Ninja (needed by clerk; the system has none and `apt` was not available) from pip in `~/fr/catala/venv`, opam told `--assume-depexts`. GitHub has no prebuilt binary for 1.3.x (only a 1.0/1.1 .deb). | compiler 53 s; packages 35 s (12 jobs) |
| Source | `~/fr/refs/catala-examples` (already cloned from GitHub; Adullact not used) | 9e251b9 |
| Tests | `clerk test impot_revenu/tests` (interpreter) and `--backend=ocaml` | 54/54 interpreted, 27/27 OCaml; 1.5 s and 1.8 s |
| Build | `clerk build impot-revenu` (Catala to OCaml, from clean) | 0.27 s; 9,129 generated OCaml lines |
| Batch driver | `catala/ocaml/driver/catala_ir.ml` (dune project copied from `_targets/ocaml`): reads `id;year;BOX=val,...`, builds the Catala input records, calls the scopes `NombreDeParts`, `TraitementsSalairesFoyerFiscal`, `BénéficesIndustrielsCommerciauxFoyerFiscal`, `BénéficesNonCommerciauxFoyerFiscal`, prints the outputs or the Catala error (assertion, no applicable rule). Needs `-linkall` (the generated modules register themselves at load time; without it every call raises Not_found). | build 0.7 s |
| Failures met | (1) `opam install` stops on the missing system package ninja-build: fixed with pip ninja + `--assume-depexts`. (2) `Not_found` at start-up: `-linkall`. (3) Our driver printed money with `%g`, which drops digits above 10^6 (four false RBG differences of 2–4 €): fixed (`%.2f`) and every run redone. No failure in the Catala code itself. | — |

Catala's Python backend is not usable for this module: `Oracles` (deficit imputation, rounding-preserving pro rata) is an
external OCaml module, so clerk builds `impot-revenu` for OCaml only.

## 2. Scope map

**What the Catala code computes** (income 2022 and 2023 only; any other year stops with "no applicable rule",
`prologue.catala_fr:810`): the number of parts (art. 194, 195, 196 A bis, 196 B) and the art. 196 B allowance; net
salaries and pensions per person (art. 79–83, 158, 5, a; 81 quater; loi 2022-1158 value-sharing bonus), annuities
(158, 6), the household's salaries-and-pensions total; BIC and BNC, professional and not, micro and real regimes,
furnished letting, short- and long-term gains, current and prior deficits (art. 34–39 quindecies, 50-0, 93, 102 ter,
156), the flat levies of art. 151-0, 39 quindecies, 93 quater and 163 bis (pensions in capital 7.5 %). It does **not**
compute the revenu brut global of the household (each category scope returns its own), the revenu net global or
imposable, the RFR (the brief's "RFR" is not in the code: `revenu_fiscal_de_référence` appears nowhere; four
`TODO ... revenu fiscal de référence` comments), or any tax. Our driver adds the three category totals less the
professional deficits to get a household RBG (`RBG`); that sum is ours.

**Inputs** (`tests/interface.catala_fr` gives defaults): per person, 26 salary/pension fields mapped to 1AJ, 1AP, 1AA,
1GB, 1GF, 1GH, 1AK, 1AS, 1AT, 1AI, 1AZ, 1AO, 1PB, 1AD, 1AV, 1TP, 1TT, 1GG, 1PM, 1NX, 1NY, 1AF, 1AL, 1AG, 1AM and the
same rows for declarant 2 and dependants (1B., 1C. ..., 1H., 1I. ...); household: 1AW–1DW, 1AR–1DR, 1TZ; BIC/BNC per
column V, C, PAC (the 5K./5L./5M., 5N./5O./5P., 5Q./5R./5S., 5H./5I./5J. families, 5UI, 5ND, 5NG, 5QS, 5NA, 5NY,
5EY, 5NW, 5NJ, 5NM, 5WE, 5DF, 5UR, 5XJ, 5XS ...), prior deficits 5HT–5MT, 5RN–5RW, 5GA–5GJ (year from the box's
position); family: 0AM, 0AO, 0AC, 0AD, 0AV, 0CF, 0CG, 0CH, 0CI, 0CR, 0DJ, 0DN, 0BT, 0AL, 0AP, 0AF, 0AW, 0AS, 0AG.

**What Catala does not cover** (boxes in our sets it does not read): investment income and gains (2xx, 3xx), property
income (4xx), charges and retirement savings (6xx, ceilings APS..), reductions and credits (7xx), farm profits (5HC..),
micro-entrepreneur flat-levy turnover (5TA, 5TB, 5TE: the fields are commented out in the prologue; only 5TJ/5TK
exist and the interface forces them to 0), the declarants' birth years (no ages anywhere: the 74-year conditions of
art. 195, 1, f and 6 cannot be applied), box N, box Z, exceptional income 0XX in box form (Catala takes a structured
list instead), and a fractional 0DN is accepted by Catala but has no box value. In the random households
(2022–2023), Catala reads every box of 1,503 of 10,067 returns (14.9 %); the most frequent boxes it cannot read are
2BH 3,457, 2TR 3,007, 2DC 2,882, 2CK 2,539, 7DB 1,203, 7UF 1,009, 6DE 820.

**Shared ground used below**: parts on every return (they depend only on the family boxes); RBG on each return reduced
to the boxes Catala reads ("projected"), where Lean's RNG equals its RBG (no charges remain) and M's `RBG1` applies;
category nets against M (`TSPR`, `BNN`+`BNCIF`); carried BNC deficits against M (`BNCDF1..6`).

## 3. Scoreboards

### (a) Catala's own tests (`harness/catala_tests_run.py`, `runs/catala/tests/`)

27 test scopes: 4 are unit tests of the OCaml oracles (ProRata1–3, DéficitsAntérieurs1; no household); 6 use the
structured exceptional-income list (BIC2, BIC3, TS7, TS8, TS9, TS11), which has no box form in our format. The 17
others were converted to boxes (situation box and birth years added so that M accepts them; NombreDeParts3's
0DN = 1.5 dropped, which does not change its parts).

| Program | Equal to the test's stated values | Differ | Not computed / out of scope |
|---|---|---|---|
| Catala (our driver) | 17 | 0 | 0 |
| Mlang | 17 | 0 | 0 |
| Lean | 10 | 0 | 7 (boxes outside its scope: non-professional BIC/BNC, 5QS, 1AT, 1CT, prior deficits) |
| OpenFisca-France (0fb80f6) | 10 | 2 | 5 (5QS, 5MD, 1AT, 1CT have no current OpenFisca variable; BNC2's carried deficit is not an output) |

Production simulator on five of them: BIC1 RBG 65,863, BNC3 2,900, TS5 68,177, BNC1 and BNC4 taxable income 0
(both deficits): the stated values are right. OpenFisca's two differences are one bug (O1 below).
NombreDeParts3 (widow, box G, one child, two attached adult children) passes in M by compensation: Catala adds 0.5
for G (P5) and gives the attached children 0.5 each (P1); M gives no half part for G and counts the second attached
child as a third child (+1). Both differences are Catala's.

### (b) Random households, income 2022 and 2023 (`runs/old`, 10,067 returns; `runs/catala/random/`)

| Figure | Catala = M | Catala = Lean | Lean = M |
|---|---|---|---|
| Parts, full return | 9,500 / 9,906 (95.9 %) | 9,646 / 10,067 (95.8 %) | 9,906 / 9,906 |
| RBG, projected return | 9,982 / 10,045 (99.4 %) | 10,003 / 10,067 | 10,045 / 10,045 |
| Salaries, pensions, annuities net (M `TSPR`) | 9,982 / 10,045 | — | — |
| BNC net (M `BNN`+`BNCIF`) | 10,045 / 10,045 | — | — |

Catala stops on none of these returns; M refuses 161 full and 22 projected returns. Every difference falls in a class
of §4: parts P1 274, P2 94, P4 38, P5 11, P6 4; RBG R1 63. No unclassified difference.
OpenFisca on the same projected returns (indicative: our box map is OpenFisca's cerfa_field table, checked only on
the tests; 1GH has no current OpenFisca box): 8,238 run, RBG = M on 8,188 / 8,220, parts on 8,140 / 8,220 (78 of the
80 involve 0CR, either our mapping of the disabled adult or OpenFisca; not investigated).

### (c) Family structures and targeted sets

| Set (income 2022–2023 only) | Returns | Catala stops | Parts Catala = M | Parts Catala = Lean | Parts Lean = M | RBG Catala = M |
|---|---|---|---|---|---|---|
| `runs/fam.jsonl` (family_stress.py, 30,000 → 10,072 in 2022–23) | 10,072 | 3,361 (M refuses 3,106 of them; M computes 169 widow + T, 86 L + T) | 3,990 / 4,788 | 4,324 / 5,597 | 4,458 / 4,458 | 5,085 / 5,085 |
| `runs/targets.jsonl` + `fam_targets.jsonl` (2022–23) | 101 | 12 (M refuses 8) | 49 / 51 | 76 / 86 | 53 / 53 | 71 / 71 |

Classes in the family set: P1 360, P2 282, P3 158, P4 140, P5 393, P6 52, P7 3; in the targets P1 4, P2 1, P3 2, P5 3.
The family set's RBG agrees everywhere because its incomes are salaries only (one kind of pension per person at most).

### (d) Production simulator (`harness/catala_sim_score.py`, `runs/catala/sim.jsonl`, `sim_score.txt`)

24 new requests (one or more per class, strictly sequential, 1.2 s apart, under `flock ~/fr/.sim.lock`) and the 211
answers for 2022–2023 saved by earlier sessions (`harness/catala_saved_sim.py`).

| Program | Parts equal / compared | RBG equal / compared | Refuses what production computes | Computes what production refuses |
|---|---|---|---|---|
| Catala | 191 / 209 | 83 / 86 | 3 (widow + T ×2, L + T) | 13 |
| Mlang | 180 / 180 | 80 / 80 | 32 | 0 |
| Lean | 195 / 195 | 81 / 81 | 0 | 18 (no input controls) |

## 4. Disagreement classes, with the production verdict

Every class below is Catala against M, Lean and production together; in no class did Lean and M disagree, and in every
class production sided with M and Lean (Lean alone where M refuses).

| Class | Example (income year, boxes) | Catala | M | Lean | Production | Verdict |
|---|---|---|---|---|---|---|
| **R1** Pension allowance (art. 158, 5, a) taken per *kind* of pension (1AS, 1AZ, 1AO ... separately: 10 %, rounding and the 422/442 € minimum each), not per pensioner | 2022, 1AS 27,666, 1AO 2,143 | RBG 26,620 | 26,828 | 26,828 | 26,828 (3/3) | **Catala error.** The article (quoted in the Catala file itself): the minimum "s'applique au montant des pensions ou retraites perçu par chaque retraité ou pensionné"; BOI-RSA-PENS-30-10-10 § 160 "s'apprécie par rapport à l'ensemble des pensions ou retraites perçues par chaque bénéficiaire", § 180 (the paragraph the Catala comment cites) "calculés, pour chaque titulaire, sur l'ensemble des pensions et retraites qu'il a perçues". `cgi_revenus.catala_fr` 4160–4360. Over-allowance up to the minimum per extra kind (≤ 442 €), or ±1 € of rounding. |
| **P1** Attached adult children (0DJ): Catala adds a flat half part per person after everything else; production counts them as dependent children (rank: third child = 1 part; a widow(er) with them keeps two base parts; they open box T) | 2022, couple, 0CF 2, 0DJ 1 | 3.5 | 4.0 | 4.0 | 4.0 (7/7: rank, widow 2.5, W + DJ 1.5, shared residence + DJ 2.5, T + DJ 2.0 ×3) | **Unsettled reading, production against Catala.** Catala follows the first sentence of art. 196 B word for word ("une demi-part supplémentaire de quotient familial par personne ainsi rattachée"; `cgi_revenus` 5697–5735, `archives_cgi` 531–560). Production, M and Lean treat the attached child as a dependant under art. 194 and 196 (rank, base, T). We found no BOFiP paragraph stating the rank rule for attached children in the in-force corpus (BOI-IR-LIQ-10-10-10-20 § 1: "Ces derniers bénéficient alors d'une majoration de quotient familial"). |
| **P2** Disabled person living under the roof (0CR, art. 196 A bis): Catala adds only the disability half part | 2022, single, 0CR 1 | 1.5 | 2.0 | 2.0 | 2.0 (3/3) | **Catala error.** Art. 196 A bis: such persons are "à sa charge, au sens de l'article 196"; BOI-IR-LIQ-10-10-10-30 § 10: "assimilées à des enfants à charge pour le calcul du nombre de parts". Catala's own comment says "le même nombre de parts qu'un enfant mineur invalide" but the code adds 0CR to the disabled-children count only (`cgi_revenus` 5685–5695), not to the children count of art. 194 (a 0CG child is in 0CF too; a 0CR person is not). |
| **P3** Boxes W and S without the age condition (Catala has no birth dates) | 2022, single, born 1960, 0AW | 1.5 | refuses (I012) | 1.0 | 1.0 (2/2: W; S for a couple aged 72 and 50: 2.0) | **Catala error (scope).** Art. 195, 1, f and 195, 6 require "âgé de plus de 74 ans"; the Catala input has no age. |
| **P4** Widow(er) whose children are all in shared residence keeps one base part | 2022, 0AV, 0CH 2 | 1.5 | 2.5 | 2.5 | 2.5 (2/2; 0CH 1: 2.25) | **Catala error.** Art. 194, I counts children in shared residence as "à charge ... réputée également partagée" (also the wording of 195, 1 and 5); the widower's base of two parts applies. Catala's base (`cgi_revenus` 5185–5225) looks at 0CF only. |
| **P5** Box G (war widow's pension) with children, not a couple: Catala adds the art. 195, 5 half part | 2022, 0AV, 0AG, 0CF 3 | 4.5 | 4.0 | 4.0 | 4.0; divorced + G refused ("incohérence entre la situation D et le code G"), as M; Catala and Lean compute | **Catala error (reading).** Art. 195, 5 grants the half part to parents who meet "l'une des conditions d'invalidité fixées aux c, d ou d bis du 1"; a pension held "à titre de veuve" (1, c) is not an invalidity condition. `cgi_revenus` 5586–5598. |
| **P6** Couple with P (or F) and S: Catala adds both art. 195, 3 and 195, 6 | 2022, both born 1940/1942, 0AP, 0AS | 3.0 | 2.5 | 2.5 | 2.5 (2/2) | **Catala error.** Art. 195, 6, second paragraph: "Les contribuables qui bénéficient des dispositions des 3 ou 4 ne peuvent bénéficier des dispositions du premier alinéa" (BOI-IR-LIQ-10-20-20-20 § 105). The Catala file quotes that sentence and codes it (`cgi_revenus` 5630–5647) as an exception on `situation_195_1_applicable`, the condition of 195, 1, which is never true for a couple; the half part of 195, 6 (`paragraphe_6_195`, 5614) is untouched. The rule is a no-op. |
| **P7** Box L with box N (not living alone) | 2023, single, 0AL, 0AN | 1.5 | 1.0 | 1.0 (when run) | 1.0 | **Catala error (scope).** Art. 195, 1, a, b, e: "vivent seuls"; Catala has no box N. |
| **X1** Box T for a widow(er): Catala stops (assertion `vérifications.catala_fr` 170) | 2023, 0AV, 0BT, 0CF 3, 0CH 1 | stops | computes | computes | computes (2/2 saved) | **Catala stricter than production.** Production computes without the T half part (art. 194, II: "célibataires ou divorcés"). |
| **X2** Boxes L and T together: Catala stops (assertion 98) | 2022, 0AD, 0AL, 0BT, 0CF 1 | stops | 2.0 | 2.0 | 2.0 | **Catala stricter than production.** |
| **O1** OpenFisca: current-year non-professional BNC deficit (5JJ, `cncn_adef`) is used by no formula | Catala test BNC4, 2023: 5KU 12,399, 5JG 52,676, 5JJ 76,988 | RBG 0 | 0 | out of scope | taxable income 0 | **OpenFisca error** (art. 156, I, 2°: such deficits come off non-professional BNC income of the year; OpenFisca gives RBG 60,859). |
| Mapping on our side | Six tests use the structured 0XX list; NombreDeParts3's 0DN = 1.5; Catala has no household RBG (our sum) | — | — | — | — | scope / mapping |

Input checks: Catala's 10 assertions (`vérifications.catala_fr`) reject situation combinations (G, L, W for a couple;
S, T for the wrong situation); on the family set they refuse 3,361 returns, 3,106 of which M refuses too. Production
refuses 13 returns Catala computes (e.g. divorced + G, which Catala reads under 195, 5).

**No Lean error found.** Lean equals production on every one of the 195 parts and 81 RBG answers above, and equals M on
every shared RBG (15,458 projected returns across the three sets) and every parts figure M computes (14,417).

## 5. Pros and cons: measurements

Speed on the build server (same machine, one core, 2,000 random 2023 returns repeated): Catala's driver evaluates four scopes;
Lean, M and OpenFisca compute the whole tax, so per-household times are not like for like.

| | Catala (impot_revenu) | Lean (FrTax) | M (ir-calcul + Mlang) | OpenFisca-France |
|---|---|---|---|---|
| Years | income 2022, 2023 (other years: "no applicable rule") | 2020–2025 | one public source per income year 2010–2025; binaries cal2019–cal2025 on the build server | formulas dated; IR tests from 2005 to 2027 (OFSUITE.md) |
| Outputs | parts, art. 196 B allowance, category nets, deficits carried, flat levies; no RBG of the household, no RNG/RNI, no RFR, no tax | parts, RNG, RNI, tax, décote, reductions, credits, RFR, social levies, CEHR, CDHR, withholding rates (12+ figures) | every figure of the notice (thousands of variables) | ~ the notice's main figures and most credits |
| Share of the computation | categories and parts only (about 5 % by the Inria 2024 report); Catala reads every box of 14.9 % of our random returns | ~ boxes of the random generator (`in_lean_scope`); 7 of 17 Catala tests out of its scope | complete (the DGFiP's production program) | broad; gaps found (F4, F8, O1) |
| Lines | 8,933 lines of `.catala_fr` (2,773 code lines, 600 comment lines, 3,714 lines of statute text and headings, the rest blank or fences) + 508 OCaml lines (oracles); tests 6,107 lines | 2,224 Lean lines (1,606 computation incl. docstrings; 618 proof files) | 84,359 M lines for 2023 (74,509 non-blank non-comment, 46 files) + Mlang 19,524 OCaml lines | 37,994 Python lines (impot_revenu module) + 24,278 YAML parameter lines (880 files) |
| Tie to the statute | literate: 50 articles (CGI, loi 2022-1158, LFR 2022, OECD model) with their Légifrance ids, the article text interleaved with the code that implements each paragraph; 10 "TODO juridique" | docstrings quoting and citing articles (179 lines cite "art.") | none in the code (variables carry box aliases and short French labels) | `reference` attributes (77 in the IR module, 26 Légifrance links) and parameter references |
| Proofs | none (10 run-time assertions on inputs) | 132 theorems, kernel-checked (some via native_decide) | none (Mlang has a formal semantics of M, not of the tax) | none (YAML test suite) |
| Speed per household | 41 µs (4 scopes, compiled OCaml; 67 µs with I/O); interpreter ~0.8 s per `clerk run` | 48 µs with I/O for the full calculation (14 µs compute, RESULTS #15) | 3.5 ms with I/O here (cal2023, 2,000-file batch); 0.32 ms compute (RESULTS #15) | 0.42 ms vectorised (4,104 returns, 7 outputs, 1.7 s) |
| Build | local opam switch + 48 packages (~1.5 min with 12 jobs) + ninja; Catala→OCaml 0.27 s; driver 0.7 s; the module needs an OCaml-only oracle, so no Python/C/Java target | elan + Lean 4.35, no dependencies; executable 2.7 s; library with proofs 2 min 11 s (130 s in Loopholes.lean) | opam switch (Mlang's own deps), M→C per year, hand-written drivers per era (F6) | pip install in a venv; no compilation |
| Licence | CeCILL 2.1 (file headers, LICENSE); catala-examples Apache-2.0; compiler Apache-2.0 | none stated (this project) | M: CeCILL 2.1 (DGFiP); Mlang GPL-3.0 | AGPL-3.0 |
| Maintainer, activity | DGFiP + Inria (headers: C. Flori, D. Merigoux, L. Gesbert); 35 commits on `impot_revenu` in catala-examples, 2 Oct 2024 – 28 Oct 2026 (L. Gesbert 21, D. Merigoux 7, V. Botbol 7) | this project | DGFiP (one public release per income year); Mlang: Inria/DGFiP | OpenFisca community, LexImpact, Etalab |
| Disagreement classes here | 8 classes against production (R1, P1–P7) and 2 refusal classes (X1, X2); 6 are coding or scope errors with statute evidence, P1 a reading the administration does not follow | none (= production in every class) | none on this ground; refuses 32 returns production computes (S/W under 74, G combinations) | O1 (5JJ ignored) on the tests; 0CR parts on the random set unexamined |

Qualitative points backed by the runs above:
- The literate form made every Catala difference quick to locate and to judge: each one sits under the paragraph it
  claims to implement, and in R1 and P6 the quoted paragraph itself contradicts the code below it.
- Catala's default/exception structure did not prevent a no-op exception (P6): the exception targets a variable that
  is false for couples, and nothing flags an exception that can never fire.
- Catala's assertions are stricter than production on two combinations (X1, X2) and looser on others (13 returns
  production refuses).
- Per-household speed of the compiled Catala is of the same order as Lean's and well under M's and OpenFisca's, for
  ~5 % of the computation.

## 6. What could not be done

- No RFR comparison: the Catala code has no RFR. No taxable income or tax: it stops before them.
- Six Catala tests (exceptional and deferred income, art. 163-0 A) have no box form in our format; four are unit
  tests of the oracles.
- Income 2020, 2021, 2024, 2025: the Catala code covers 2022 and 2023 only.
- Lean category figures were compared only through RNG on the projected returns (Lean prints no category totals; no
  Lean source was touched).
- OpenFisca on the random set is indicative only (box map not validated beyond the tests; the 0CR differences are
  not investigated).

## Files (the build server `~/fr`, mirrored under `~\Documents\the build server-work\fr\`)

| File | Role |
|---|---|
| `catala/ocaml/driver/catala_ir.ml`, `dune` | batch driver over the generated OCaml |
| `harness/catala_lib.py` | runners: Catala driver, Lean, Mlang (configurable M variables) |
| `harness/catala_tests_dump.py`, `catala_tests_run.py` | step 3a: dump and score the Catala tests |
| `harness/catala_openfisca.py` | OpenFisca on box returns (cerfa_field map, family by hand) |
| `harness/catala_compare.py`, `catala_classify.py` | steps 3b/3c and the class table |
| `harness/catala_saved_sim.py`, `catala_sim_cases.py`, `catala_sim_score.py` | step 3d |
| `runs/catala/{tests,random,fam,targets,saved}/`, `sim.jsonl`, `sim_score.txt`, `speed_*.txt` | outputs |
