# SN findings

## FT review, third pass (2026-11-21; dev cases only; IMPROVE_FT.md "Third pass")
- **SN 1200.** CGI art. 36 base rounding to 1 000 F is the statute; the ekwo pack does not round (SN FTS-1).

- **SN FTS-2, payroll_africa employer (`sn_ft_employer_payrollafrica_grid`, software error; FT review 4).** The app charges the
  CSS 7 % on the IPRES ceiling (432 000 a month); the CSS ceiling is 63 000 a month (the model: CSS 8 % incl. work injury to
  63 000, IPRES 8,4 % to 432 000). All 690 dev cases at ratio ~0,62.
