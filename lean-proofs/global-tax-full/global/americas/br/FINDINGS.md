# BR (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **BR FTS-1, node-sales-tax (`br_ft_vat_nodesalestax_grid`, software error).** The library gives Brazil a single
  "vat 0.17"; Brazil levies no national VAT (ICMS is a state tax: São Paulo Lei 6.374/1989 art. 34 I, 18 %; PIS/COFINS
  federal, Leis 10.637/2002 and 10.833/2003). Grid withdrawal requested (HANDOFF_FT_vat R2).
