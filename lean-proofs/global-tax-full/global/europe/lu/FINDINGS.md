# LU findings

## FT review, third pass (2026-11-21; dev cases only; IMPROVE_FT.md "Third pass")
- **LU FTR-1 (5111).** Annexe A 1° (gaz): 8 %. TEDB dev exact.

## FT review, fifth pass (2026-11-21; dev only)
- **LU FTR-2 (2200, model fix).** Mutualité des employeurs added at class 2, 0,99 % on the capped base: CSS art. 52-55
  (compulsory affiliation, art. 34-36 base), Statuts art. 6 ("Tout nouvel affilié obligatoire ou volontaire cotise dans
  la classe 2": the entity has no absenteeism record), CCSS "Taux de cotisation au 01.01.2025" (avis 14.03.2025,
  `law/ccss_20250314_avis_80.pdf`: 0,07 / 0,99 / 1,48 / 2,64 %). OECD 2200 by the Interpretative Guide §40-41 (a
  contingent sickness benefit from a social security institution). Santé au travail (STM) left out: Code du travail
  L. 322-1 2., L. 323-1 (5), a cotisation only of employers "optant pour le recours à ce service", set on its budget: a
  fee, not a tax (Guide §12). 2 guards; PIT unchanged; only 2200 changed.
- **LU FTC-1 (CLEISS)**: class 1 (0,07 %) + STM 0,14 %; **LU FTC-2 (EUROMOD)**: a representative MDE rate + STM.
- **LU FTR-3 (1100 art. 99ter gains of 2025 at a quarter of the global rate; FT review 7, Dataset round 5 R5-6).** Loi du 22 mai
  2024 (Mémorial A 219) art. 14: net income realised 1.1.2024-31.12.2024 under L.I.R. art. 99ter is extraordinary income taxed
  under art. 131 (1) d (a quarter of the global rate); end date "30 juin 2025" (Loi du 4 avril 2025, Mémorial A 121, art. 7,
  effect 1.1.2025) and "30 septembre 2025" (Loi du 27 juin 2025, Mémorial A 271, art. 7, in force 1.7.2025). Texts from the
  legilux filestore (`lu/law/loi_2024_a219.*`, `loi_2025_a121.*`, `loi_2025_a271.*`, SHA256SUMS). Pass 14 had half (art. 131
  (1) c) for every 2025 sale; the ACD A-Z page (16/04/2025) states the quarter to 30 June (written before the June extension).
  The 99ter rule now takes shareBp 2500; art. 100 stays at half. Kernel 2.6.0 `StackRule` has no date window, so a sale of
  1.10-31.12.2025 (half) is not separated: entry A -> **B**, flagged; kernel request filed (KERNEL_REQUESTS "FT reviewer 7").
  Hand case: single, wages 80 000, real estate held 10 years, gain 300 000: 1100 65 563 -> 40 861 (the stacked part 49 404 ->
  24 702 = 250 000 x the global rate / 4). `b1.sh LU`: A identical, B/C 56/56, 39 guards (2 new), 0 sorry; `cmpcc.sh LU` 17 153
  dev lines: pit 0, no heading changed (no dev case has a 99ter sale).
