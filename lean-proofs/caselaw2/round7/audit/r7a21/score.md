# Blind audit score: r7a21 (type B)

- items in the key: 109 (97 sampled rows, 6 known-wrong decoys, 6 known-right decoys); answered: 109; answer files: 3
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| rh_sa | 97 | 97 | 80/97 = 0.825 [0.737, 0.888] | 80/97 = 0.825 [0.737, 0.888] | 97/97 = 1.000 [0.962, 1.000] | 96/97 = 0.990 [0.944, 0.998] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- rh_sa: right 0.825 [0.825, 0.825] (read in full); right + extent 0.825 [0.825, 0.825] (read in full)

Answers on sampled rows (every reader): rh_sa: reversed 3, reversed_or_vacated_in_part 5, vacated 76, withdrawn_or_superseded 13

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): rh_sa: kind 1, kind (same status effect) 16

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 12/12 = 1.000 [0.757, 1.000]
- known wrong, not confirmed: 6/6 = 1.000 [0.610, 1.000]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:a3:rehear/enbanc-cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/other | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:below/sc | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:memo/cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/sc/sc_a1 | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:memo/cap-2g | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 37 | 31/33 = 0.939 [0.804, 0.983] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 36 | 22/32 = 0.688 [0.514, 0.821] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 36 | 27/32 = 0.844 [0.682, 0.931] | 4/4 = 1.000 [0.510, 1.000] | 0 | 1 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| rh_sa | fed | 16 | 12/16 = 0.750 [0.505, 0.898] | 12/16 = 0.750 [0.505, 0.898] |
| rh_sa | state | 81 | 68/81 = 0.840 [0.745, 0.904] | 68/81 = 0.840 [0.745, 0.904] |
| rh_sa | 1900s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| rh_sa | 1910s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| rh_sa | 1920s | 3 | 0/3 = 0.000 [0.000, 0.561] | 0/3 = 0.000 [0.000, 0.561] |
| rh_sa | 1930s | 15 | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] |
| rh_sa | 1940s | 10 | 5/10 = 0.500 [0.237, 0.763] | 5/10 = 0.500 [0.237, 0.763] |
| rh_sa | 1950s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| rh_sa | 1960s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| rh_sa | 1970s | 11 | 10/11 = 0.909 [0.623, 0.984] | 10/11 = 0.909 [0.623, 0.984] |
| rh_sa | 1980s | 22 | 19/22 = 0.864 [0.667, 0.953] | 19/22 = 0.864 [0.667, 0.953] |
| rh_sa | 1990s | 15 | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] |
| rh_sa | 2000s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| rh_sa | 2010s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| rh_sa | vacated | 97 | 80/97 = 0.825 [0.737, 0.888] | 80/97 = 0.825 [0.737, 0.888] |
| rh_sa | stratum fed|1930s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| rh_sa | stratum fed|1940s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| rh_sa | stratum fed|1980s (population 2, sampled 2) | 2 | 0/2 | 0/2 |
| rh_sa | stratum fed|1990s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| rh_sa | stratum fed|2000s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| rh_sa | stratum fed|2010s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| rh_sa | stratum state|1900s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| rh_sa | stratum state|1910s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| rh_sa | stratum state|1920s (population 3, sampled 3) | 3 | 0/3 | 0/3 |
| rh_sa | stratum state|1930s (population 13, sampled 13) | 13 | 13/13 | 13/13 |
| rh_sa | stratum state|1940s (population 7, sampled 7) | 7 | 3/7 | 3/7 |
| rh_sa | stratum state|1950s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| rh_sa | stratum state|1960s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| rh_sa | stratum state|1970s (population 11, sampled 11) | 11 | 10/11 | 10/11 |
| rh_sa | stratum state|1980s (population 20, sampled 20) | 20 | 19/20 | 19/20 |
| rh_sa | stratum state|1990s (population 13, sampled 13) | 13 | 12/13 | 12/13 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (17 lines).
