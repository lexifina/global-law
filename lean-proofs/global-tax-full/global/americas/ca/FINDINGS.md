# CA (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **CA FTR-1 (4400 Ontario LTT, model fix).** The model applied the s. 2 (1) (b) half per cent above $2,000,000 to
  every purchase and had no first-time purchaser refund. LTTA s. 2 (1) (b): only "a conveyance of land that contains at
  least one and not more than two single family residences"; s. 9.2 (2), (2.1) (b): refund of the tax on a qualifying
  home, "$4,000 if the conveyance ... occurs on or after January 1, 2017" (e-Laws consolidation; amendment notes show
  the 2025 wording). 5 `#guard`s. `ca_ft_ltt_kormans_grid` dev 277 -> 370 / 718 (w1% 510 -> 626). Toronto MLTT rates
  checked against the City's 2025 rates page (unchanged). PIT unchanged.
- **CA FTS-1, Kormans LTT calculator (`ca_ft_ltt_kormans_grid`, software error).** Above $2,000,000 the page applies
  the provincial 0.5 % and Toronto's residential luxury tiers to non-residential land (LTTA s. 2 (1) (b); Toronto
  Municipal Code § 760-9.2 B: 0.5 / 1 / 1.5 / 2 %), and for homes above $3,000,000 tiers that are not the 2025 ones
  (the City's rates page, Wayback 2025-08-02: 3.5 % / 4.5 % / 5.5 % / 6.5 % / 7.5 %). All 92 remaining dev misses are
  above $2,000,000.
- **CA FTS-2, Canada capital gains calculator (darnosint, `ca_ft_cgt_darnosint_grid`, software error).** The builder's
  note confirmed on the large gains: the page includes two thirds of the gain above $250,000 (ITA s. 38 (a): one half in
  2025; the proposal was cancelled), and uses mixed-year federal brackets and a 15 % lowest rate. Model-above misses at
  low incomes come from statutory items the page lacks (Ontario Health Premium, Taxation Act 2007 s. 33.1; the LIFT
  credit phase-out) and from the 1.x model's tax net of the refundable Canada Workers Benefit, whose phase-out the
  stacked charge counts (pattern 5 in IMPROVE_FT, open).
- **CA FTS-3, darnosint payroll tab (`ca_ft_employer_darnosint_grid`, software error).** 2025 constants: YMPE 73,200
  (2025: 71,300) and an EI employer rate of 1.666 % (Employment Insurance Act s. 68: 1.4 times the employee's 1.64 %);
  at the maxima the model's 4,430 (CPP + CPP2) + 1,508 (EI) against the page's 4,467 + 1,095.

## FT review, fifth pass (2026-11-21)
- **CA FTR-2 (4400 Toronto MLTT and Ontario LTT, model fix).** The model gave the first-time purchaser rebate / refund to a
  purchaser flagged `nonResident`. Toronto Municipal Code ch. 760 § 760-1 "FIRST TIME PURCHASER" B (conveyance on or after
  1 March 2017): "an individual who is at least 18 years of age, is a Canadian citizen or permanent resident of Canada";
  § 760-60 A rebates tax "by a first time purchaser"; G: a non-citizen is eligible only on becoming a citizen or permanent
  resident within 18 months. LTTA s. 9.2 (1) "purchaser" (c) and (2.0.1): the same. `nonResident` is read as not a citizen
  or permanent resident on the conveyance date (as the AU model reads it; the City calculator's MNRST type has no rebate).
  3 `#guard`s. `ca_ft_mltt_torontocalc_grid` dev 687 -> **694 / 694**. PIT unchanged; only 4400 changed (22 dev lines).
  `ca_ft_ltt_kormans_grid` 370 -> 360: its adapter turns the first-time toggle on for non-residents (test side, HANDOFF_FT_cap).
