# The DGFiP's own correction history: would a statute model have caught its bugs? (17 November 2026)

Question: between two releases of the M code for the same income year, every change that alters a computed result is
either a correction the DGFiP made to its production program or a change of law applied mid-year. For each change,
does the Lean model (income 2020 to 2025) agree with the old release or with the corrected one?

**Short answer: the dataset this needs does not exist publicly for 2020–2025.** The DGFiP publishes one release per
income year: the last one. For Lean's years there are no two releases of the same year to compare, so no
within-year correction can be scored against Lean: the count is **0 corrections scored, on 0 of which Lean agreed with
the corrected release**. The one public within-year pair is for income 2018 (6.3 and 6.7), which is outside Lean's
years. That pair was built, run and classified below. Section 5 adds a cross-year check: deviations Lean flagged in
year N that the DGFiP changed in a later millésime. That is not the requested within-year dataset.

Files: harness/hist_*.py; runs/hist/; Mlang builds in ~/fr/hist/ (bin/cal_<release>, releases/, pristine/,
mlang/ = copy of ~/fr/mlang with its own m_ext/2018h63, 2018h67); progress log PROGRESS_history.md.

## 1. Releases found, and where each came from

| Source | What it holds | History / versions |
|---|---|---|
| gitlab.adullact.net/dgfip/ir-calcul (plain `git clone`, no challenge; full history, 31 commits) | sources2010m_7_1, 2011m_9_6, 2012m_3_13, 2013m_3_8, 2014m_2_15, 2015m_4_6, 2016m_4_5, 2017m_6_10, **2018m_6_3, 2018m_6_7**, 2019m_8_0, 2020m_6_5, 2021m_5_7, 2022m_6_1, 2023m_8_0, 2024m_3_13, 2025m_3_11 | Each year was added once, by one commit (2019-05 … 2026-11-09). Afterwards only: a missing `;` in 2020m_6_5 chap-85.m rule 851325 (aa214f9, parse fix, no output change); a missing `regle 401000:` header in 2018m_6_7 chap-4.m (e9db11c, parse fix); a Latin-1 to UTF-8 conversion of 2019/2020 (02dc47d); 46 `tmpchap-*.m` duplicates added with 2024 and removed (fc8b85a): identical to the published files apart from encoding and header comments. The README states the version numbers: 6.3 "3 premières émissions", 6.7 "4e émission et batch de réactivité fiscale". |
| …/impots-nationaux-revenu-patrimoine-particuliers/calculette-ir (Adullact) | the same 17 directories | same tree |
| github.com/etalab/calculette-impots-m-source-code (10 commits, 2017–2020) | 2010m_7_1 … 2014m_2_15, 2015m_4_6, in Latin-1 and UTF-8 | the files the DGFiP added in May 2019 (tgvI, errI, tgvB, errB). **Data-quality finding:** in the Adullact ir-calcul tree, 10 to 15 files per year of 2010–2014 are truncated (2010–2013 at exactly 32,768 bytes; 2014 chap-4.m is 31 kB against 633 kB here). The etalab copies are complete. |
| github.com/openfisca/calculette-impots-m-source-code (2016) | one tree, its README says "version 2.5 … revenus 2014" | identical, rule for rule (comments aside), to etalab's 2014m_2_15: "2.5" is a typo for 2.15, not a second 2014 release. Its fork rgaidot/… is the same. |
| framagit.org/denismerigoux/ir-calcul | 2010–2018 | Merigoux's parse fixes (empty `verif`, missing rule): not DGFiP releases. framagit.org/dgfip/ir-calcul now needs a login. |
| Mlang (github.com/MLanguage/mlang, 2,311 commits; Adullact Mlang, 2,557 commits, 17 branches) | ir-calcul only as a submodule (pointers to the commits above or to Merigoux's fork); m_ext drivers; DGFiP test files tests/2018 … 2025 | No M source of any other release on any branch. The test directories were regenerated over time (tests/2024 June → Sept 2026, tests/2025 July → Aug 2026); harness/hist_testrev.py found **no test whose inputs stayed the same while its expected results changed** (2,719 same-input tests for 2024, 1 for 2025), so they reveal no internal release change. |
| Software Heritage (archive.softwareheritage.org) | visits of gitlab.adullact.net/dgfip/ir-calcul 2020–2026, framagit.org/dgfip/ir-calcul 2019 | every snapshot head is a commit already in the Adullact history: nothing else archived. |
| GitHub code search, data.gouv.fr API | — | no other copy of any release (one third-party repo, erwanpaccard/irpp-mcp, uses 2023m_8_0). |

Not obtainable: every intermediate release (2024 3.1–3.12, 2025 3.1–3.10, 2023 8.0's predecessors, 2018 6.4–6.6, and so
on). The DGFiP keeps them in an internal SVN (Mlang's makefile has an `M_SVN_$(REPO)` mode pointing at it).

## 2. Pairs per income year

| Income year | Releases public | Consecutive pairs | Output-changing changes |
|---|---|---|---|
| 2020, 2021, 2022, 2023, 2024, 2025 | 1 each (6.5, 5.7, 6.1, 8.0, 3.13, 3.11) | **0** | — |
| 2019, 2017, 2016, 2015, 2010–2013 | 1 each | 0 | — |
| 2014 | 1 (2.15; the "2.5" copy is the same code) | 0 | — |
| **2018** | **2 (6.3, 6.7)** | **1 (not consecutive: 6.4–6.6 missing)** | **10 change clusters (C1, C1b, C2–C9 below): 2 bug fixes shown by the diff and the statute (C2, C4) and a rounding fix (C8); 1 mid-year change of law (C1, with C1b); 2 unclear (C3, C5b); the rest processing or intermediate** |

## 3. How the 2018 pair was built and run

- Compiler: the Mlang binary of ~/fr/mlang (commit 572aa0e), called directly with the options of
  `make compile_dgfip_c_backend` (`-A iliad --precision double --comparison_error_margin=0.000001
  --dgfip_options=-g,-O,-k4,-m<year>,-X`), the same C driver (ml_primitif/c_driver) and gcc flags
  (~/fr/hist/build_release.sh). Check: rebuilding 2020m_6_5 this way gives byte-identical outputs to ~/fr/bin/cal2020
  on 400 random returns.
- Mlang does not compile 2018 ("ne compile pas" in its own makefile) and has an empty m_ext/2018 driver. Patches, all
  identical on both releases and recorded in ~/fr/hist/releases/PATCHES.txt: (1) parse only, an empty
  `verif isf 196341` removed from coc7.m (as Merigoux's fork did); (2) eight variables named T07/T24 that clash with the
  cells of a table T renamed TQ07/TQ24 (harness/hist_fix_tables.py); (3) a driver per release from m_ext/2019/cibles.m,
  minus the barème-pass blocks storing variables the release does not declare (harness/hist_adapt_driver.py):
  6.3 drops V_BARINDTAZ, V_BARIITAZIR, V_BARIRTOTAL; 6.7 drops V_BARINDTAZ, V_BARIRTOTAL and keeps
  `V_BARIITAZIR = IITAZIR`.
- Validation: cal 6.7 passes **all** of Mlang's 2018 DGFiP tests (fuzzing 275/275, randomized 1,267/1,267). Cal 6.3
  passes 202/275 and 1,257/1,267; every miss is on variables that changed between 6.3 and 6.7 (RASTXFOYER, PASTOTAL,
  IINETCIMR, the RAS* instalments). So the tests were produced by 6.7, and the 6.3 build differs exactly where the code does.
- Diff (harness/hist_mdiff.py, runs/hist/mdiff_2018_6_3_6_7.json): 115 rules changed, 5 added, 2 `verif` changed;
  42 declarations changed (23 constants), 267 added, 325 removed.
- Returns (harness/hist_cases.py, runs/hist/2018_6_3_6_7/cases.jsonl.gz): 30,000 random households (harness/gen.py,
  year 2018, boxes both releases accept) and 9,600 returns aimed at the 120 changed rules that read declared boxes: 80
  each, a random household plus 1–3 of the boxes the rule reads (one level through the variables it uses), half with a
  high salary. The 2020–2025 target sets (targets.jsonl, family, ofsuite, pas) were not used: they are for years that
  have no pair.
- Comparison (harness/hist_pair.py): every variable that both releases restitute, per return. **26,628 of 39,600
  returns change in at least one restituted variable**; of the 30,000 random ones, 20,286 change, and **none in a final tax
  or income figure** (IRN, IINET, NAPCR, RNI, RFR, parts, …). Clusters: harness/hist_clusters_2018.py →
  runs/hist/2018_6_3_6_7/clusters.json.

## 4. Every output-changing change, income 2018, release 6.3 → 6.7

Lean column: income 2018 is outside the Lean model, so no change can be scored (Lean was not extended, as instructed).
"Statute" says which release the text supports, where the diff and the text settle it.

| # | M rules / variables | What changed (probe: 6.3 → 6.7) | Class | Statute | Returns affected (random / targeted) | Lean | Production (calc-2019.cgi, income 2018) |
|---|---|---|---|---|---|---|---|
| C1 | constants TX_MOD2–6, LIM_INF/SUP_MOD, PLAREM2–6, SEUIL_BARCOT1/2; rule 401140 (DEC11/12/13/6: décote coefficient `11/18` → `45.25/100` under FLAG_BAREM); taux 201640 (RASTXFOYER from V_BARTXFOYER) | The withholding rate (taux de prélèvement) computed on 2018 income moves to the scale 9,964 / 25,405 / 72,643 / 156,244 € at 11/30/41/45 %, décote 769 € / 1,273 € − 45.25 %. Single, salary 30,000 €: rate 8.0 % → 7.3 %. Random households: 17,775 rates change, all but 9 down, mean −0.72 point (min −2.5, max +0.9). | **Change of law applied mid-year**: the "batch de réactivité fiscale", rates for January–August 2020 | Loi n° 2019-1479 du 28 décembre 2019 (LF 2020), art. 2, III, A, 1: exactly these figures, "pour le calcul du taux … relatif aux versements et retenues effectués entre le 1er janvier et le 31 août 2020"; CGI art. 204 H, I. 6.3 is the rate under the 2018 scale (art. 197). | 20,872 (17,910 / 2,962) | n/a | not displayed |
| C1b | IITAZIR, IINETCIMR, IRESTCIMR (res-ser2 222000: IITAZIR taken from the barème pass) | "Tax without CIMR" shown for the withholding computation recomputed with the C1 scale (2,385 → 2,177 €) | intermediate, part of C1 | as C1 | 20,677 (17,987 / 2,690) | n/a | not displayed |
| C2 | CIMRC = REVTOT (chap-3 1268; REVTOT now includes ESFP, box 8ZZ "revenus d'origine indéterminée") | CIMR ratio denominator. Salary 30,000 € + 8ZZ 5,000 €: CIMR 3,802 → 3,208 €, income tax 0 → 594 € (RNI 32,000 in both). In 6.3 the CIMR wiped out the tax on the 8ZZ income too. | **Bug fix** | Loi n° 2016-1917, art. 60, II, B (as in force 2019): tax × net non-exceptional 204 A income ÷ "le revenu net imposable au barème progressif … hors déficits, charges et abattements"; 8ZZ income is taxed at the barème, so it is in the denominator; II, A limits the credit to non-exceptional 204 A income. 6.7 = statute. | 4 (0 / 4) | n/a | **= 6.3**: CIMR 3,802, impôt net 0, net à payer 860 € (social levies only). Production still runs the uncorrected logic for this case. |
| C3 | CIMR2 (chap-3 201905): `× positif(null(7-CMAJ)+…)` for a penalty code; CIMRCSGP/CIMRPSOLP (301375) for social levies; FLAG_RETARD/FLAG_DEFAUT in 201120, 221360, 23111 | With a penalty code other than 07 (9YT, IFI 9XT), the CIMR is withheld. Salary 30,000 €, interest 2,000 €, 9YT = 8: CIMR 2,385 → 0, income tax 256 → 2,641 €, net to pay 358 → 3,697 €. Social levies change likewise. | **Unclear** | No text found: art. 60 (as in force 2019) has no penalty condition; the condition may come from BOFiP or another provision not checked. | 349 (0 / 349) | n/a | refused ("date de dépôt" missing); not pursued |
| C4 | REPRCMAR (chap-82 82014): `DEFRCM5` missing from the second branch's sum; it feeds DFRCM5 and DFRCM (restituted: capital-income deficits left to carry forward) | Interest 1,000 € (2OP), deficits 2AN 400, 2AQ 800, 2AR 500 (1,700 in all, 1,000 used): deficit left to carry forward DFRCM 1,400 → 700 €, DFRCM5 1,200 → 500 € (the 2017 deficit is only 500). | **Bug fix** | CGI art. 156, I, 8°: capital-income deficits are set against the same income of the six following years; 1,700 − 1,000 leaves 700. 6.7 = statute. | 6 (0 / 6) generated returns change DFRCM*; 5 of them also change RNI or the tax, from the C5b rules, so C4 and C5b are not separated on generated returns; the probe isolates C4 | n/a | not displayed on the simulator page |
| C5 | 821060 (BRCMBIS adds 2VN/2VO/2VP/2YY/2ZZ), 8201404, 821175, 821003 | (a) BRCMBISB/REPRCMB, the capital-income base kept for art. 1731 bis, now includes the life-insurance boxes (2ZZ 210 €, 2TS 203 €: 203 → 413 €). (b) With prior capital-income deficits and life-insurance income under 2OP, RNI 1,100–3,700 € lower on 6 targeted returns. A single 2VN + 2AR probe does not change. | (a) intermediate; (b) unclear, not isolated | CGI art. 156, I, 8°; art. 1731 bis | (a) 1,199 (861 / 338); (b) 6 (0 / 6) | n/a | — |
| C6 | 111600, 111630 (RNI, TTPVQ × (1 − ANNUL2042)), isf 77280, 221360, 221990 | Box 9YA "annulation de la déclaration": 6.7 gives RNI 0 (27,000 → 0) and no refund | Processing (cancelled return), not a tax rule | — | 218 (0 / 218) | n/a | — |
| C7 | 201040 IRNIN (+CODZRA), 201060, 221250–221280 (BRASAR × V_CNR → BRASAR) | Box ZRA (tax under the non-resident regime) now in IRNIN, the base of interest and penalties: 0 → 800 €; net to pay unchanged (800) | Intermediate (penalty base) | — | 164 (0 / 164); final figures change on 4 | n/a | — |
| C8 | 821002 (RAVCNORM1 etc. re-parenthesised) | RNG 58,119.79 → 58,120 € (life-insurance 2CH/RCH case) | Bug fix, presentation-size | income rounded to the euro (CGI art. 193) | 1 (0 / 1) | n/a | — |
| C9 | IRBASE, CSBASE_MAJO, PSOLBASE_MAJO, RDBASE_MAJO and the corrective-chapter rules (chap-inr, chap-cinr, chap-majo, chap-cmajo: CIMR → CIMR2, 02/03 codes) | Bases for late-payment interest and penalties | Intermediate | — | 25,997 (19,839 / 6,158) | n/a | — |

Also in the diff, with no output change found in these runs: Scellier/Pinel/furnished-rental carry-forward caps
(401300, 401314, 401316, 401320, 401470, 401680, 402140: new BCEL*/BILM* bases), tourism-residence reduction (401340
DTOURREP), 7KZ and FIP-DOM for non-residents (401835, 401190), 4666 TOTRI3WG + APENTCY, CEHR for a marriage/divorce
year (80000), 0AX/0AY `present` → `positif` (verif 102421). The targeted returns reached most of them; a change that
needs a specific combination (for example a carry-forward above its cap with 1731 bis) may still be unreached.

**Headline for 2018:** of the output-changing changes, 2 are bug fixes that the diff and the statute both show (C2, C4),
plus a cents-level rounding fix (C8); 1 is a mid-year change of law (C1, with C1b); 2 are unclear (C3, C5b);
the rest are processing or intermediate (C5a, C6, C7, C9). In 30,000 random households not one final tax figure changes:
the corrections are all in corners (8ZZ income, deficit carry-forwards, penalty codes, cancelled returns). Lean would
need a 2018 model to score them. The production simulator for income 2018 still shows the uncorrected 6.3 result on
C2.

## 5. Cross-year check for 2020–2025: deviations Lean flagged that the DGFiP changed later

This is not the requested within-year dataset. It lists the existing Lean ≠ M findings (FINDINGS.md) whose M rule
changed in a later published millésime. Code checked in the published releases:

| Finding | M, by millésime | Lean | Later change |
|---|---|---|---|
| F1 union-dues credit, overtime limit (CGI 199 quater C, 81 quater; 7,500 € from income 2022) | SOMBCOSV: `COD1GH - LIM7500` (2020), `LIM5000` (2021, 2022, 2023, 2024), `COD1GHRET` (2025) | statute (7,500 €) | **corrected in the 2025 code**; 2022–2024 not corrected (production = M, FINDINGS P) |
| F2 CEHR with flat-levy income (art. 223 sexies) | CHRTEFF proration in every millésime 2020–2025 (formula rewritten in 2023, still prorated) | statute | none |
| W2 withholding rate ending .x4995–.x4999 (art. 204 H, I, 3) | rounds up 2020–2024; the 2025 code truncates first (FINDINGS W2) | statute | changed in 2025, as stated in FINDINGS.md W2; not re-checked here |
| W5 quarter-part cap in couple rates | rounded with the tax 2020–2024, on its own in 2025 (FINDINGS W5) | on its own | changed in 2025, as stated in FINDINGS.md W5; not re-checked here |

So for 2020–2024, 3 of the statute deviations Lean flagged were changed by the DGFiP in the 2025 program in Lean's
direction (F1, W2, W5); F1 is the only one of the three that changes the income tax itself. None was corrected for the
earlier years.

## 6. What could not be obtained or done

- No intermediate release of any year 2020–2025 is public (Adullact, GitHub, Software Heritage, framagit, data.gouv.fr
  checked). The step-2/3/5 pipeline for those years has nothing to run on; no Lean scoring was possible.
- 2014: the "2.5" copy is 2.15. 2010–2014 in the Adullact tree are truncated (use the etalab copies).
- 2018: Mlang has no 2018 driver; the drivers here are adapted from 2019 (section 3). 6.7 reproduces all of the DGFiP's
  2018 tests, so the adaptation is good for 6.7; for 6.3 there is no independent test.
- C3 (CIMR withheld under a penalty code) is left unclear: no statutory text found. Production refused the probe
  without a filing date; it was not retried.
- No Lean source was changed, and no Lean problem was found (Lean was not run: no pair falls in its years).
