# BE findings

## FT review, third pass (2026-11-21; dev cases only; IMPROVE_FT.md "Third pass")
- **BE 1200 losses (open).** CIR 92 art. 207 (corbeille: € 1 m + 70 % of the excess, Loi 25.12.2017) not modelled: `be_ft_cit_ekwo_grid` 60 dev cases at model 0. The 2025 consolidated art. 207 (whether a later programme law changed the 70 %) to read. TEDB hotels / restaurants / electricity: AR n° 20 tableaux to read.
- **BE FTR (4400 securities purchases grade C; FT review 7, Dataset round 5 R5-5).** The 4400 family books the Brussels droits
  d'enregistrement on real estate only, so a purchase of listed shares returned a computed 0 (`be_ft_tob_friedme_grid` dev 0 / 0 /
  681 covered). The taxe sur les opérations de bourse (Code des droits et taxes divers art. 120 ff.) is not held: a purchase of
  listed or unlisted shares now adds a 4400 grade-C line (block appended to `tools/specs/BE_Property.py`). Dev: 681 covered ->
  **0 covered, 681 not reached (grade C)**. `b1.sh BE`: A identical, B/C 56/56, 17 guards, 0 sorry; `cmpcc.sh BE` 16 133 lines: pit 0,
  no heading's numbers changed.
