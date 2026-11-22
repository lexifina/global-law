# TJ (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **TJ FTR-1 (5111 VAT, model fix).** The model had 15 % (art. 264 (1)); Tax Code art. 397 (4): "Rates of value added
  tax established by paragraph 1) of part 1 of Article 264 ... from January 1, 2024 to December 31, 2026 - 14 percent".
  Consumption.lean (hand-written) edited, guards moved to 14 %. `tj_ft_vat_ekwo_grid` dev 51 -> 200 / 672 (w1% 594;
  the rest is per-line rounding). PIT unchanged.
