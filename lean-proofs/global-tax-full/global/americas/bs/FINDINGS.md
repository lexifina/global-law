# BS (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **BS FTS-1, node-sales-tax (`bs_ft_vat_nodesalestax_grid`, software error).** The library applies 12 %; the model's
  10 % (VAT Act, reprint at 1 July 2024, s. 6 (1) as substituted by the VAT (Amendment) Act, 2025 s. 3) holds for 2025; the ekwo grid agrees with the
  model on every dev case up to rounding. All 692 dev misses at model / referee = (10 / 110) / (12 / 112).
