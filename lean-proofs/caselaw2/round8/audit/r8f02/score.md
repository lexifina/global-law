# Blind audit score: r8f02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc8_f2neg | 448 | 80 | 62/80 = 0.775 [0.672, 0.853] | 61/80 = 0.762 [0.659, 0.842] | 70/80 = 0.875 [0.785, 0.931] | 62/80 = 0.775 [0.672, 0.853] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc8_f2neg: right 0.846 [0.739, 0.914] (n_eff 65); right + extent 0.830 [0.721, 0.902] (n_eff 65)

Answers on sampled rows (every reader): fjc8_f2neg: affirmed 4, modified 6, none 20, reversed 69, reversed_or_vacated_in_part 42, vacated 19

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc8_f2neg: kind 12, link 20, scope 4

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
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 20/27 = 0.741 [0.553, 0.868] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 21/27 = 0.778 [0.592, 0.894] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 21/27 = 0.778 [0.592, 0.894] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 21/26 = 0.808 [0.621, 0.915] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 22/26 = 0.846 [0.665, 0.939] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 85/89 = 0.955 [0.890, 0.982]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc8_f2neg | fed | 80 | 62/80 = 0.775 [0.672, 0.853] | 61/80 = 0.762 [0.659, 0.842] |
| fjc8_f2neg | 1930s | 4 | 1/4 = 0.250 [0.046, 0.699] | 1/4 = 0.250 [0.046, 0.699] |
| fjc8_f2neg | 1940s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| fjc8_f2neg | 1950s | 9 | 6/9 = 0.667 [0.354, 0.879] | 6/9 = 0.667 [0.354, 0.879] |
| fjc8_f2neg | 1960s | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] |
| fjc8_f2neg | 1970s | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] |
| fjc8_f2neg | 1980s | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] |
| fjc8_f2neg | 1990s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc8_f2neg | 2000s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| fjc8_f2neg | 2010s | 10 | 9/10 = 0.900 [0.596, 0.982] | 8/10 = 0.800 [0.490, 0.943] |
| fjc8_f2neg | 2020s | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| fjc8_f2neg | modified | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| fjc8_f2neg | reversed | 60 | 45/60 = 0.750 [0.628, 0.842] | 44/60 = 0.733 [0.610, 0.829] |
| fjc8_f2neg | vacated | 16 | 14/16 = 0.875 [0.640, 0.965] | 14/16 = 0.875 [0.640, 0.965] |
| fjc8_f2neg | stratum fed|1930s (population 4, sampled 4) | 4 | 1/4 | 1/4 |
| fjc8_f2neg | stratum fed|1940s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| fjc8_f2neg | stratum fed|1950s (population 9, sampled 9) | 9 | 6/9 | 6/9 |
| fjc8_f2neg | stratum fed|1960s (population 28, sampled 10) | 10 | 8/10 | 8/10 |
| fjc8_f2neg | stratum fed|1970s (population 50, sampled 10) | 10 | 8/10 | 8/10 |
| fjc8_f2neg | stratum fed|1980s (population 85, sampled 10) | 10 | 8/10 | 8/10 |
| fjc8_f2neg | stratum fed|1990s (population 96, sampled 9) | 9 | 8/9 | 8/9 |
| fjc8_f2neg | stratum fed|2000s (population 98, sampled 10) | 10 | 9/10 | 9/10 |
| fjc8_f2neg | stratum fed|2010s (population 70, sampled 10) | 10 | 9/10 | 8/10 |
| fjc8_f2neg | stratum fed|2020s (population 2, sampled 2) | 2 | 0/2 | 0/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (36 lines).
