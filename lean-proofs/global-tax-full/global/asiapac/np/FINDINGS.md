# NP (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **NP FTR-1 (1200/1100 withholding, model fix).** Withholding was a grade-C entry ("rates not located in the text")
  and the exe did not flag it, so payments abroad scored 0. ITA 2058 s. 88 (1) (FA 2082 consolidation): interest,
  royalties, service fees with a source in Nepal "कुल भुक्तानी रकमको पन्ध्र प्रतिशतका दरले" (15 %); s. 88 (2) (क) dividends
  5 %. 4 `#guard`s. `np_ft_wht_nepalitax_grid` dev 0 -> 356 / 718 (the 362 payments to individuals booked under 1100;
  with every withheld charge 718 / 718). The provisos' special rates are not modelled.
