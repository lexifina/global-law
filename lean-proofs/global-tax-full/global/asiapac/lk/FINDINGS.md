# LK (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **LK FTR-1 (1200/1100 withholding, model fix, grade B).** The model charged 15 % on interest and royalties and
  nothing on service fees, citing the Fifth Schedule (which lists qualifying payments and reliefs). The rates are in
  the First Schedule para. 10: (1) (c) (ii) service fees to non-residents (s. 85 (1) (b)) 14 %; (1) (d) (added by Act
  No. 45 of 2022 s. 33 (6)) dividends 15 %, "all other payments except dividend" 14 %, interest 10 % from 2025-04-01
  (Act No. 2 of 2025 s. 3 (3)). Open reading: s. 84A (1A) (the scope of item (d)); item (b) would give 5 % on interest.
  `lk_ft_wht_lktax_grid` dev: 346 / 346 payments to companies exact; the 349 payments to individuals are booked under
  1100 (selector request R1 to the cit builder; with every withheld charge 695 / 695).
