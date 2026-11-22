# CM (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **CM FTR-1 (5111 VAT, model fix).** The centimes additionnels communaux on VAT were not modelled. CGI (édition 2024)
  art. C 53: centimes additionnels "sur ... la taxe sur la valeur ajoutée (TVA)"; art. C 54 (1): "fixé à 10 % du
  principal de l'impôt concerné". One 5111 charge at 19.25 %; the tobacco excise's VAT divisor moved to 1.1925 with it.
  `cm_ft_vat_ekwo_grid` dev 0 -> 350 / 704 (w1% 704). PIT unchanged.
