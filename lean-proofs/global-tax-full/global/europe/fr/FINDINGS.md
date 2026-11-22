# FR (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **FR FTR-1 (4200 IFI, model fix).** CGI art. 979 I (plafonnement: IFI + taxes on the income at most 75 % of the
  income net of frais professionnels) was not applied, and the 30 % of art. 973 went to every home. Now: one
  residence principale (the first home), and the cap read with the 1.x line's rni, income tax and CSG/CRDS on wages
  (the entity's own year; flagged). 4 guards. `fr_ft_wealth_openfisca_grid` dev: the 20 model-above misses gone.
- **FR FTS-1, OpenFisca-France IFI (`fr_ft_wealth_openfisca_grid`, software error).** Adds a 5 % forfait mobilier to
  the IFI base (an ISF rule); art. 964-965: the IFI base is real estate only. The 73 remaining dev misses.
- **FR FTR-2 (4300 DMTG, model fix).** Gifts between spouses were not charged; art. 790 E (80 724) and art. 777
  Tableau II now apply; art. 790 B (31 865 on a grandchild's gift) and art. 788 IV (1 594 on an inheritance share
  without another abatement) added. 5 guards. Gifts: 79 -> 109 exact on dev.
- **FR FTS-2, OpenFisca-France DMTG (`fr_ft_inheritance_openfisca_grid`, software error).** Returns 0 for gifts and
  inheritances to grandchildren, nephews and nieces, other relatives, non-relatives and some parents; art. 777
  Tableaux I and III (55 %, 60 %), art. 779, 788 IV give positive tax. Children's gifts get an extra 31 865 (art.
  790 G conditions not in the entity: convention).
- **FR FTR-3 (2200, 3000: employer contributions, FT review fourth pass).** (a) Réduction générale (CSS L. 241-13; D. 241-7 I:
  (T/0,6) × (1,6 × SMIC an / pay − 1), 4 decimals, at most T; T 0,3194 to April and 0,3193 from 1 May 2025 by décret n° 2025-318
  art. 1 5° a, art. 5; SMIC an 1 820 × 11,88 €, décret n° 2024-951) was not applied: low pay was overstated by up to 30 % of pay.
  (b) The 7 % maladie and 3,45 % famille rates now run to 2,25 and 3,3 × the SMIC applicable au 1er janvier 2025 (D. 241-1-2,
  D. 241-3-2 as replaced by décret n° 2025-318 art. 1 1°, 3°: 48 648,60 € and 71 351,28 €); the model had the SMIC at 31.12.2023
  (the CLEISS note). (c) Added FNAL (CCH L. 813-5: 0,1 % within the plafond under 50 employees, 0,5 % otherwise), the contribution
  au dialogue social (Code du travail D. 2135-34: 0,016 %), AT/MP at the taux net moyen national 2,12 % (arrêté du 29 avril 2025
  art. 2; **declared convention**: the establishment's rate is not in the entity, and this is URSSAF's published default),
  and 3000: CFP (Code du travail L. 6331-1 0,55 % / L. 6331-3 1 %) and taxe d'apprentissage (L. 6241-1-1 II: 0,68 %).
  **Declared convention:** a household's wages are paid by a private employer of fewer than eleven employees, liable to the
  taxe d'apprentissage and to VAT (so no taxe sur les salaires, CGI art. 231); a company uses its headcount. Texts:
  `fr/law/css_D241-7_wb2024.*`, `decret2025-318_wb.*`, `smic_decret2024-951_wb.*`, `cch_L813-5_wb.*`, `atmp_arrete20250429_wb.*`,
  `ct_D2135-34_wb.*`, `ct_cfp_lt11_wb.*`, `ct_cfp_ge11_wb.*`, `ct_ta_L6241_wb.*`. 14 guards (2 updated). Dev:
  `fr_ft_employer_urssaf_grid` 2200 0 -> **634 / 705 w1%** (every case within 14 units below: whole-unit rounding of 14 items),
  3000 family not modelled -> **360 exact, 690 / 705 w1%** (all within 2 units); `fr_ft_employer_openfisca_grid` 2200
  8 -> 615 / 699 w1%, 3000 -> 352 exact / 682 w1%; `fr_ft_employer_euromod_grid` 2200 275 -> 0 w1% (EUROMOD's FR_2025 books
  no AT/MP, FNAL 0,5 %, a lower Agirc-Arrco tranche-2 ceiling: FR FTC-1). pit unchanged on all 25 674 FR dev lines.
- **FR FTC-1, EUROMOD FR_2025 employer contributions (`fr_ft_employer_euromod_grid`, referee convention / suspected software error).**
  `tscerot_s` (AT/MP) is 0 for every entity; housing `tscerho_s` is 0,5 % (FNAL of an employer of 50 or more); the pension
  item stops growing near 3,1 plafonds (Agirc-Arrco tranche 2 runs to 8 plafonds: CLEISS 2025 "de 3 925 à 31 400 €"); CFP
  0,45 %. Not the model's employer: recorded, rows read as convention (rule 8).

## FT review, fifth pass (2026-11-21)
- **OpenFisca employer grid, the 84 misses traced** (`fr_ft_employer_openfisca_grid`): the referee's 2200 line includes
  CUFPA (taxe d'apprentissage + CFP, also its 3000 line: test side), AT/MP at OpenFisca's default 0,70 % (**FR FTC-2**;
  the model's declared 2,12 %) and AGS 0,20 % (**FR FTS-2**; 0,25 % for 2025). Every other item agrees to the cent.
- Taxe sur les salaires (companies with VAT-exempt sales): still open; CGI 231 / 1679 A not held.
