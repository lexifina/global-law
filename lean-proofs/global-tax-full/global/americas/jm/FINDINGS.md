- **JM FTR-1 (1200 dividends to non-residents, year in force; FT review 7).** The 15 % came from PwC's page reviewed 29 Sep 2026.
  Dated copies: reviewed 3 March 2025 (Internet Archive 2025-08-03): non-treaty non-resident corporations 33 1/3 %, individuals 25 %;
  reviewed 12 August 2025 (capture 2025-12-16): 15 %. The rate changed during 2025; the provision and its date are not held, so the
  rule is withdrawn: entry B -> **C** (block appended to `tools/specs/JM_Corporate.py`). Dev: `ftd_oecd_wht_rates_2025` JM-wht-dividend
  (OECD 33.33 %) 9 000 000 vs 19 998 000 -> not reached (grade C); the other three JM rows exact as before. `build1.sh JM`: A identical,
  B/C 56/56, 18 guards, 0 sorry; `cmpcc.sh JM` 6 529 lines: pit 0, only 1200 (1 line).
