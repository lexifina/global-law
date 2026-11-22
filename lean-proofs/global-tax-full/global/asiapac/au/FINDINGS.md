# AU (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **AU FTR-1 (1200 CIT, model fix).** The model charged 30 % unless the company carried the flag `baseRate`. ITRA 1986
  s. 23 (2) (a) gives 25 % to a base rate entity, and s. 23AA defines one by the entity's own facts: "(a) no more than
  80% of its assessable income ... is base rate entity passive income; and (b) its aggregated turnover ... is less than
  $50 million" (Compilation No. 65, in force 2025-07-01, `au/law/fedleg/itra_20250701.html`). The test now runs on the
  entity's turnover and portfolio dividends (s. 23AB (1) (a)); flags override. 7 `#guard`s (the $50 m edge, the 80 %
  test). `au_ft_cit_darnosint_grid` dev 394 -> 674 / 674. PIT unchanged (56-household grid, the three AU FT grids).
- **AU 1100 gains (open, pattern 2).** Gains on disposals are a grade-C entry (not modelled); the exe does not flag the
  heading for a disposal entity, so `au_ft_cgt_darnosint_grid` scores 0 as covered (257 / 711, all misses at 0). The
  builder's note that the page uses the 2023-24 rates (19 % / 32.5 %, flat 2 % levy) is a software error to confirm
  once gains are modelled (ITAA 1997 Div. 102, 115, 118; ITRA 1986 Sch. 7).

## FT review, third pass (2026-11-21; dev cases only; IMPROVE_FT.md "Third pass")
- **AU FTR-2 (4400, NSW transfer duty).** Duties Act 1997 (NSW) (Internet Archive 2025-04-30): s. 32 per $100 or part; s. 32A premium 7 % above $3,636,000 (indexed at the model's A/B 1,196); s. 104U (1) surcharge 9 % (was 8 %), its own charge; s. 78A (1) first home exemption to $800,000 / $350,000, citizens and permanent residents only (s. 73 (5)); the s. 78A (2) concession not computed. Revenue NSW calculator grid dev 320 -> 691 / 691; the two private tools: AU FTS-2.

- **AU FTS-3 (DarnOsint CGT, `au_ft_cgt_darnosint_grid`, open; FT review 6).** 264 covered non-exact dev cases. The model
  follows ITRA 1986 Sch. 7 (2024-25 rates as amended by the Cost of Living Tax Cuts Act 2024), LITO and the Medicare levy with
  its low-income phase-in, stacked: e00876 (wages 9 070, short-held listed-share gain 187 831 after costs): TI 196 901, tax
  54 743 + Medicare 3 938 = **58 681** = model; e00942 (wages 29 678, 39-month gain 33 743, discounted 16 871): 5 382 - 1 382
  = **4 000** = model. The referee is above by up to ~3 000 at wages near 0 (falling about 2 % of wages, ~1 900 at 20-60 k,
  0 above 135 k) and below by up to ~250 at 20-40 k wages with small gains: its schedule below the 135 k band and its Medicare
  low-income handling differ from the statute. Recorded as a referee error (not reproduced exactly); no model change.
- **AU FTS-3 closed (FT review 7): the referee's schedule reproduced.** DarnOsint `script.js` (commit 82a4ac8) `TAX_BRACKETS`
  labelled "2025-26": 19 % to 45 000 and 32,5 % to 135 000 (the pre-Stage-3 rates on the Stage-3 thresholds), 37 % to 190 000
  with base 34 342, 45 % above with base 54 682 (its own rates give 54 692), `income - min + 1` per bracket; Medicare 2 % flat
  (no low-income phase-in); no LITO. That schedule reproduces the referee on **711 / 711** dev cases within $1
  (`ftreview/rv7/au_repro.py`). The statute for 2024-25 (ITRA 1986 Sch. 7 Part I as amended by the Cost of Living Tax Cuts
  Act 2024: 16 % / 30 % / 37 % / 45 %), LITO (ITAA 1997 s. 61-115) and the Medicare levy phase-in reproduce the model on 707 / 711
  (`rv7/au_stat.py`); the other 4 are disposals held exactly 12 months (1 July 2024 to 1 July 2025) where model and referee
  both give the 50 % discount (s. 115-25 (1); whether the days of acquisition and of the CGT event count is not settled here:
  noted, not changed). Category S; the model is not changed.
