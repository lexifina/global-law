# Blind audit score: r10t01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_s1 | 1014 | 80 | 74/80 = 0.925 [0.846, 0.965] | 74/80 = 0.925 [0.846, 0.965] | 75/80 = 0.938 [0.862, 0.973] | 74/80 = 0.925 [0.846, 0.965] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_s1: right 0.980 [0.888, 0.997] (n_eff 45); right + extent 0.980 [0.888, 0.997] (n_eff 45)

Answers on sampled rows (every reader): stlink_s1: affirmed 2, modified 4, none 9, reversed 120, reversed_or_vacated_in_part 18, vacated 6, withdrawn_or_superseded 1

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_s1: kind 2, kind (same status effect) 1, link 9

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
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f04:fjc9J | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p03:PJR | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_1_b.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_s1 | state | 80 | 74/80 = 0.925 [0.846, 0.965] | 74/80 = 0.925 [0.846, 0.965] |
| stlink_s1 | 1890s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| stlink_s1 | 1900s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| stlink_s1 | 1910s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| stlink_s1 | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_s1 | 1930s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_s1 | 1940s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| stlink_s1 | 1950s | 8 | 6/8 = 0.750 [0.409, 0.928] | 6/8 = 0.750 [0.409, 0.928] |
| stlink_s1 | 1960s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_s1 | 1970s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| stlink_s1 | 1980s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_s1 | 1990s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_s1 | 2000s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_s1 | 2010s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_s1 | modified | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| stlink_s1 | reversed | 74 | 68/74 = 0.919 [0.834, 0.962] | 68/74 = 0.919 [0.834, 0.962] |
| stlink_s1 | vacated | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| stlink_s1 | stratum state|1890s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| stlink_s1 | stratum state|1900s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| stlink_s1 | stratum state|1910s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| stlink_s1 | stratum state|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_s1 | stratum state|1930s (population 12, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_s1 | stratum state|1940s (population 8, sampled 8) | 8 | 7/8 | 7/8 |
| stlink_s1 | stratum state|1950s (population 32, sampled 8) | 8 | 6/8 | 6/8 |
| stlink_s1 | stratum state|1960s (population 62, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_s1 | stratum state|1970s (population 74, sampled 8) | 8 | 7/8 | 7/8 |
| stlink_s1 | stratum state|1980s (population 167, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_s1 | stratum state|1990s (population 235, sampled 7) | 7 | 7/7 | 7/7 |
| stlink_s1 | stratum state|2000s (population 250, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_s1 | stratum state|2010s (population 165, sampled 8) | 8 | 8/8 | 8/8 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (12 lines).
