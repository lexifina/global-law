# Blind audit score: r10f12 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc10b_xs | 471 | 80 | 57/80 = 0.713 [0.605, 0.800] | 57/80 = 0.713 [0.605, 0.800] | 65/80 = 0.812 [0.713, 0.883] | 57/80 = 0.713 [0.605, 0.800] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc10b_xs: right 0.804 [0.686, 0.885] (n_eff 59); right + extent 0.804 [0.686, 0.885] (n_eff 59)

Answers on sampled rows (every reader): fjc10b_xs: affirmed 6, modified 4, none 30, reversed 54, reversed_or_vacated_in_part 42, review_dismissed 2, vacated 22

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc10b_xs: kind 16, link 30

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 18/18 = 1.000 [0.824, 1.000]
- known wrong, not confirmed: 12/12 = 1.000 [0.757, 1.000]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p03:PJR | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 19/27 = 0.704 [0.515, 0.842] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 19/27 = 0.704 [0.515, 0.842] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3.jsonl | 3 | 29 | 16/26 = 0.615 [0.425, 0.776] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 16/26 = 0.615 [0.425, 0.776] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc10b_xs | fed | 80 | 57/80 = 0.713 [0.605, 0.800] | 57/80 = 0.713 [0.605, 0.800] |
| fjc10b_xs | 1930s | 7 | 5/7 = 0.714 [0.359, 0.918] | 5/7 = 0.714 [0.359, 0.918] |
| fjc10b_xs | 1940s | 9 | 5/9 = 0.556 [0.267, 0.811] | 5/9 = 0.556 [0.267, 0.811] |
| fjc10b_xs | 1950s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| fjc10b_xs | 1960s | 8 | 3/8 = 0.375 [0.137, 0.694] | 3/8 = 0.375 [0.137, 0.694] |
| fjc10b_xs | 1970s | 8 | 6/8 = 0.750 [0.409, 0.928] | 6/8 = 0.750 [0.409, 0.928] |
| fjc10b_xs | 1980s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| fjc10b_xs | 1990s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc10b_xs | 2000s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc10b_xs | 2010s | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| fjc10b_xs | 2020s | 8 | 4/8 = 0.500 [0.215, 0.785] | 4/8 = 0.500 [0.215, 0.785] |
| fjc10b_xs | modified | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| fjc10b_xs | reversed | 58 | 38/58 = 0.655 [0.527, 0.764] | 38/58 = 0.655 [0.527, 0.764] |
| fjc10b_xs | vacated | 20 | 17/20 = 0.850 [0.640, 0.948] | 17/20 = 0.850 [0.640, 0.948] |
| fjc10b_xs | stratum fed|1930s (population 7, sampled 7) | 7 | 5/7 | 5/7 |
| fjc10b_xs | stratum fed|1940s (population 13, sampled 9) | 9 | 5/9 | 5/9 |
| fjc10b_xs | stratum fed|1950s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| fjc10b_xs | stratum fed|1960s (population 16, sampled 8) | 8 | 3/8 | 3/8 |
| fjc10b_xs | stratum fed|1970s (population 49, sampled 8) | 8 | 6/8 | 6/8 |
| fjc10b_xs | stratum fed|1980s (population 82, sampled 8) | 8 | 7/8 | 7/8 |
| fjc10b_xs | stratum fed|1990s (population 81, sampled 9) | 9 | 8/9 | 8/9 |
| fjc10b_xs | stratum fed|2000s (population 100, sampled 9) | 9 | 8/9 | 8/9 |
| fjc10b_xs | stratum fed|2010s (population 101, sampled 9) | 9 | 7/9 | 7/9 |
| fjc10b_xs | stratum fed|2020s (population 17, sampled 8) | 8 | 4/8 | 4/8 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (46 lines).
