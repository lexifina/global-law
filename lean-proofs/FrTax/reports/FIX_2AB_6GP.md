# Boxes 2AB and 6GP: statute, doctrine, production, and the Lean fix (17 November 2026)

POPULATION.md § 4 found two new classes where the Lean model and the DGFiP's M code (run with Mlang) part company:
**2AB** (Lean refunded the treaty credit on foreign securities income when it exceeded the tax; M only offsets it)
and **6GP** (M deducts alimony paid under a pre-2006 court decision increased by 25 %; Lean deducted the amount
declared). In both cases the statute, the BOFiP and the production simulator side with M. Lean was wrong, and it is
now fixed (`lean/FrTax/Liquidation.lean`, `lean/FrTax/Income.lean`).

Work files: `~/fr/try/fix_2ab_6gp/` (test returns, simulator answers and pages, regression and population outputs,
the binaries before and after: `frtax_before` built 14:19, `frtax_after` built 16:03).

## 1. Box 2AB: crédit d'impôt sur valeurs étrangères

### Statute (CGI art. 199 ter, text in force since 1 January 2015, unchanged for income 2020–2025)
- I, a, 1st para.: the French withholding ("la somme à la retenue de laquelle ces revenus ont donné lieu, en vertu des
  articles 119 bis et 1678 bis") "est imputée sur le montant de l'impôt sur le revenu".
- I, a, 2nd para.: the refund covers only that French withholding: "les sommes retenues à la source seront
  restituées, dans la mesure où elles ne pourront être admises à imputation sur l'impôt sur le revenu par suite de son
  montant inférieur".
- **I, b**, the treaty credits on foreign securities income: "En ce qui concerne les revenus de source étrangère
  visés aux articles 120 à 125, l'imputation est limitée au montant du crédit correspondant à l'impôt retenu à la
  source à l'étranger ou à la décote en tenant lieu, tel qu'il est prévu par les conventions internationales."
  Imputation only, with no refund clause (I, c, the EU savings-directive withholding, is the only other credit in the
  article that says "En cas d'excédent, celui-ci est restitué", and it ended with directive 2003/48/CE).

### Doctrine (BOFiP)
- BOI-RPPM-RCM-20-20-20191220 § 1 contrasts the two: the PFO (2CK) "peut être restitué totalement ou
  partiellement"; for "des crédits d'impôt attachés aux revenus de source étrangère accordés en vertu des conventions
  internationales (CGI, art. 199 ter, I-b)" it speaks only of imputation and points to BOI-RPPM-RCM-20-10-20-60.
- BOI-RPPM-RCM-20-10-20-60-20161229 § 90: "Le montant du crédit d'impôt [...] qui peut être effectivement imputé sur
  l'impôt français, doit être limité à la fraction de l'impôt français correspondant aux revenus donnant lieu à
  imputation. En d'autres termes, la France ne peut accorder sur son impôt [...] une déduction de l'impôt étranger
  supérieure au montant de l'impôt français afférent aux revenus considérés."
- BOI-INT-DG-20-20-100-20200219 § 43 (method 1): "le crédit d'impôt sera limité au montant de l'impôt français calculé
  à raison des mêmes revenus".

Verdict: the credit is imputed on the income tax and never refunded. (The doctrine's per-income limit, the French tax
on those particular revenues, is computed by the taxpayer on form 2047; neither M nor Lean recomputes it, both take
the declared 2AB and cap it at the whole tax.)

### Test returns (single, born 1980; Lean before / M / production)
| Id | Year | Boxes | Lean before: net | M: CIRCMAVFT, IRN | Production: before credits, net, payable |
|---|---|---|---|---|---|
| S1 | 2024 | 2DC 1 000, 2AB 300 | −172 (refund) | 128, 0 | 128, **0**, 172 (social levies only) |
| S2 | 2024 | 1AJ 10 000, 2DC 500, 2OP, 2AB 200 | −200 | 0, 0 | –, **0**, 87 |
| S3 | 2024 | 1AJ 20 000, 2DC 1 000, 2AB 500 | −222 | 278, 0 | 278, **0**, 172 |
| S4 | 2025 | as S3 | −246 | 254, 0 | 254, **0**, 186 |

Production reads 2AB (S1 and S3 would show 128 and 278 of tax otherwise) and refunds nothing: production = M on
every figure, Lean was wrong. Further returns checked against M only (`cases.txt`, `c61.txt`): 2AB below the tax
(equal before and after), 2AB with a refundable credit (7DB; M imputes 2AB first, then refunds the excess of the
other credit), 2AB with the 2CK prepayment (refunded), and 2AB leaving less than 61 € (T1: tax 150, 2AB 100, M
collects 50: the 61 € test of art. 1657, 1 bis is on the tax before the 2AB imputation, as Lean already did).

### Fix (Liquidation.lean)
- `credits` no longer contains 2AB: it is the refundable credits and prepayments.
- New `foreignCredit d before = max 0 (min 2AB before)`, imputed first on the tax after reductions including the
  flat tax (M: `CIRCMAVFT = max(0, min(IRB + ..., RCMAVFT))`), with the art. 199 ter, I, b text and the BOFiP quotes
  in its comment.
- `net`: `before − foreign − credits`, the 61 € test unchanged (on `before`).
- `Result` gains `foreign`; `beforeCredits` (printed as IAVCR) is now the tax after the 2AB imputation, before the
  refundable credits, i.e. M's IAN. CITOT (= M's IRE) no longer includes 2AB. This keeps the harness's existing
  comparisons consistent (run.py CITOT↔IRE; sim_compare2 IAVCR − CITOT ↔ production "Impôt sur le revenu net";
  official_examples IAVCR↔IAN). Note: production's "Impôt avant crédits d'impôts" is before 2AB (278 in S3), so for
  2AB returns IAVCR is not that figure; sim_compare2 does not score it.
- The CDHR base is unchanged: it already added 2AB back (art. 224, IV, A, 2°), now via `realCredits = credits − 2CK`.

## 2. Box 6GP: alimony under a court decision that became final before 1 January 2006

### Statute
The 25 % is not in art. 156 but in **CGI art. 158, 7, 3°** (the brief's "art. 156, II, 2° as amended in 2006" is
the box's base, not the source of the increase): "Le montant des revenus et charges énumérés ci-après, retenu pour
le calcul de l'impôt selon les modalités prévues à l'article 197, est multiplié par un coefficient de 1,25. Ces
dispositions s'appliquent : [...] 3° Aux sommes mentionnées au 2° du II de l'article 156 versées en vertu d'une
décision de justice devenue définitive avant le 1er janvier 2006". Checked in every version of art. 158 in force
for income 2020–2025 (global-law record, commits 8c04b62e5a9, b1629b1dc38, 184f62e5640, e7ac4c9261a, 1f96e0be7e3):
3° is unchanged and stays at 1,25. The reduced coefficients ("fixé à 1,2 pour [...] 2020, à 1,15 pour [...] 2021
et à 1,1 pour [...] 2022") apply to the 1° (non-members of an approved management centre) only, and 1° was later
repealed. Art. 156, II, 2° also caps the alimony for an adult child: "La déduction est limitée, par enfant majeur,
au montant fixé pour l'abattement prévu par l'article 196 B."

### Doctrine
BOI-IR-BASE-20-30-20-50-20190301 § 110: "A compter de l'imposition des revenus de l'année 2006, l'abattement de 20 %
[...] a été intégré dans le barème [...] (loi n° 2005-1719 du 30 décembre 2005 de finances pour 2006, art. 76). Dès
lors, les décisions de justice devenues définitives avant le 1er janvier 2006 ne pouvaient pas tenir compte des
nouvelles modalités de calcul [...]. C'est pourquoi la loi a prévu de revaloriser à hauteur de 25 % les pensions
alimentaires mentionnées au 2° du II de l'article 156 du CGI versées en vertu d'une décision de justice antérieure à
cette date (CGI, art. 158, 7-3°)." § 120: "le contribuable ne doit pas majorer de lui-même le montant de la pension
alimentaire versée. Il doit reporter sur sa déclaration [...] le montant [...] compte non tenu de la majoration de
25 %" (and the recipient is taxed on the unincreased amount). The same cross-reference appears in
BOI-IR-BASE-20-30-20-10-20190301 § 35 (alimony paid to ascendants) and BOI-IR-BASE-20-30-20-40-20140502 § 20
(alimony between spouses or ex-spouses).

### Which boxes
The increase covers every "somme mentionnée au 2° du II de l'article 156" under a pre-2006 decision. On form 2042
those are **6GP** (other alimony, decision before 2006) and **6GI, 6GJ, 6GK, 6GL** (adult children, decision
before 2006; M variables CHENF1–4). It does not cover 6GU (other alimony) or 6EL–6EQ (adult children, no pre-2006
decision). M: `TOTPA = arr(PAAV × MAJREV) + PAAP` (6GP × 1.25, 6GU as declared) and
`DDPA = Σ min(NCHENFi, LIMDPAE) + min(arr(CHENFi × MAJREV), LIMDPAE) + ...`, so for the adult-child boxes the
increase comes first and the art. 196 B cap after it. The doctrine does not say in which order; production does
it the same way as M (S8).

### Test returns (single, born 1980, salary 1AJ 40 000 € unless noted)
| Id | Year | Boxes | Lean before: RNI, net | M: deduction, RNI, IRN | Production: RNI, net |
|---|---|---|---|---|---|
| S5 | 2024 | 6GP 4 000 | 32 000, 2 765 | 5 000, 31 000, 2 465 | **31 000, 2 465** |
| S6 | 2024 | 6GU 4 000 | 32 000, 2 765 | 4 000, 32 000, 2 765 | 32 000, 2 765 (no increase) |
| S7 | 2024 | 6GI 5 000 | 31 000, 2 465 | 6 250, 29 750, 2 090 | **29 750, 2 090** |
| S8 | 2024 | 6GI 6 000 | 30 000, 2 165 | min(7 500, 6 794) = 6 794, 29 206, 1 940 | **29 206, 1 940** (décote 8) |
| S9 | 2025 | couple, 1AJ 60 000 + 1BJ 20 000, 6GP 3 333 | 68 667, 6 808 | 4 166, 67 834, 6 558 | **67 834, 6 558** |

Production = M on every figure. Lean was wrong on 6GP and also on 6GI/6GJ: it neither increased them nor applied
the 196 B cap to them. Checked against M for income 2020–2025 (`years.txt`, 6GP 3 334 → 4 168, rounded half up as
M's `arr` does; 6GI 5 500 → capped at that year's 196 B amount; 6GJ 1 001 → 1 251): equal in every year.

### Fix (Income.lean)
New `preReformAlimony x = pct 12500 x` (× 1.25, rounded to the euro), quoting art. 158, 7, 3° and BOI § 120; in
`charges`, 6GP is increased, 6GI and 6GJ are increased and then capped at `p.attached` (the art. 196 B amount, with
the art. 156, II, 2° cap quoted), and 6GU is unchanged. 6GK and 6GL (3rd and 4th adult child, pre-2006) and 6EN/6EQ
are still not read by Lean (not in its box list), so they remain out of its scope; the same rule would apply.

## 3. Production simulator
9 requests in total (S1–S9, `simcases.jsonl`), posted with `harness/sim_run.py` (strictly sequential, 1.2 s apart,
the whole batch under `flock ~/fr/.sim.lock`). Answers: `~/fr/try/fix_2ab_6gp/sim.jsonl`, raw pages in
`sim.jsonl.html/`. Every answer equals M; every figure of the fixed Lean equals production (`after_sim.json`).

## 4. Build
`lake build` (default target), `lake build FrTax` (whole library, including Theorems, Loopholes, Brochure67) and
`lake build FrTax.Theorems FrTax.Loopholes`: all succeed, with no `sorry` (the only warnings are the existing
`if_neg` deprecations in Withholding.lean). The theorems and loophole checks did not need changes.

## 5. Regressions (before → after)
Random sets against M (`harness/pas_regress.py frtax_before frtax_after`, 12 jobs):
| Set | Returns | Equal to M on all 12 figures | Output changed |
|---|---|---|---|
| runs/final (2024–2025) | 98 868 | 98 849 → 98 849 | 0 returns (whole output line identical for all) |
| runs/old (2020–2023) | 19 748 | 19 741 → 19 741 | 0 |

No change is expected: gen.py never fills 2AB, 6GP or 6GI–6GL.

Production-scored sets, rescored from the saved answers with no new requests (`sim_compare2.py`, a copy taking the
binary from `FRTAX_BIN`, run directories symlinked so the original `sim_verdicts.json` files were not overwritten):
| Saved answers | Cases | Lean equal / differs (before → after) | M |
|---|---|---|---|
| runs/sim_targets_v2.jsonl | 371 (353 computed) | 301 / 52 → 301 / 52 | 285 / 7, 61 refused |
| runs/sim2.jsonl | 700 | 699 / 1 → 699 / 1 | 691 / 0, 9 refused |
| runs/sim_fam.jsonl | 126 (39 computed) | 39 / 0 → 39 / 0 | 30 / 0, 9 refused |

The reports before and after are byte-identical (none of these returns has 2AB or the alimony boxes) and match the
Lean and M lines of the saved reports (`runs/sim_targets_report.txt`, `sim2_report.txt`, `sim_fam_report.txt`; the
OpenFisca columns were not rerun). The sim2 cases were rebuilt from `runs/final/in<year>/*.irj`.

## 6. Population figures (POPULATION.md § 4), before → after
Only the affected households were rerun through the new Lean: those with 2AB, 6GP, 6GI or 6GJ (2024: 4 184 of the
pool's 250 000, 3 826 with 2AB and 364 with 6GP; 2023: 4 227, 3 866 and 370; none has 6GI/6GJ). The old binary
reproduces the stored `lean.jsonl` exactly on all of them. `pop_report.py` was rerun on a copy of each year with those
lines replaced (`~/fr/try/fix_2ab_6gp/pop/<year>/{before,after}/report.json`).

| Figure | 2024 before | 2024 after | 2023 before | 2023 after |
|---|---|---|---|---|
| class "2AB" households (pool), net Lean − M | 177 091 (971), −29.3 M€ | none | 183 250 (927), −34.5 M€ | 9 (1), +9 € |
| 2AB households whose net differs, all classes | 177 558 (982), −29.3 M€ | 5 (5), +788 € | 184 074 (946), −34.5 M€ | 375 (16), +6 378 € |
| class "6GP" households (pool), net | 6 543 (176), +1.0 M€ | none | 11 492 (175), +2.5 M€ | none |
| 6GP households whose taxable income differs | 22 968 (314), +13.6 M€ | 0 | 29 397 (313), +21.0 M€ | 0 |
| all households whose net differs | 200 439 (1 388) | 16 343 (235) | 221 324 (1 506) | 26 134 (401) |
| net tax, Lean − M | −27.7 M€ | +0.57 M€ | −30.3 M€ | +1.71 M€ |

What remains is the known classes only. F1 is unchanged (9 486 / 17 895 households). F2 is up slightly
(2024: 6 793 → 6 798; 2023: 5 294 → 5 641) because returns that were "2AB+F2" are now plain F2: all 5 residual
2AB returns in 2024 and 13 of the 16 in 2023 differ only in the CEHR with flat-levy micro income. In 2023, "other"
(2 570 → 2 590) gains two 2AB returns of the documented elderly flat-levy case (M's RFR lower by the art. 157 bis
allowance), and one return is the 1 € rounding of a two-person credit. No residual comes from 2AB or 6GP.

So both POPULATION.md figures were artefacts of the Lean error, and the fix removes them: 2AB (177 k households,
−29.3 M€ in 2024; 183 k, −34.5 M€ in 2023) → 0; 6GP (6.5 k, +1.0 M€ in 2024; 11.5 k, +2.5 M€ in 2023) → 0. Lean's
weighted net tax incl. CEHR moves from 112.918 to 112.946 Md€ (2024) and from 108.468 to 108.500 Md€ (2023). M's
column moves by 0.25 M€ (2024) and 0.20 M€ (2023) only because `pop_report.py` fills the households M refuses
with Lean's values. POPULATION.md, FINDINGS.md and RESULTS.md were not edited; the § 4 rows for 2AB and 6GP and the
§ 5 lines describe the old Lean.
