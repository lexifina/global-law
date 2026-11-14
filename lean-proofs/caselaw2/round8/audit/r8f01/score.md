# Blind audit score: r8f01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc8_f1neg | 761 | 80 | 71/80 = 0.887 [0.800, 0.940] | 70/80 = 0.875 [0.785, 0.931] | 75/80 = 0.938 [0.862, 0.973] | 71/80 = 0.887 [0.800, 0.940] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc8_f1neg: right 0.954 [0.864, 0.985] (n_eff 57); right + extent 0.942 [0.848, 0.979] (n_eff 57)

Answers on sampled rows (every reader): fjc8_f1neg: affirmed 4, modified 4, none 10, reversed 82, reversed_or_vacated_in_part 32, vacated 28

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc8_f1neg: kind 8, link 10, scope 1

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
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc8_f1neg | fed | 80 | 71/80 = 0.887 [0.800, 0.940] | 70/80 = 0.875 [0.785, 0.931] |
| fjc8_f1neg | 1920s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| fjc8_f1neg | 1930s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| fjc8_f1neg | 1940s | 8 | 6/8 = 0.750 [0.409, 0.928] | 6/8 = 0.750 [0.409, 0.928] |
| fjc8_f1neg | 1950s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| fjc8_f1neg | 1960s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| fjc8_f1neg | 1970s | 8 | 8/8 = 1.000 [0.676, 1.000] | 7/8 = 0.875 [0.529, 0.978] |
| fjc8_f1neg | 1980s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| fjc8_f1neg | 1990s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| fjc8_f1neg | 2000s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| fjc8_f1neg | 2010s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| fjc8_f1neg | 2020s | 9 | 4/9 = 0.444 [0.189, 0.733] | 4/9 = 0.444 [0.189, 0.733] |
| fjc8_f1neg | modified | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| fjc8_f1neg | reversed | 57 | 51/57 = 0.895 [0.789, 0.951] | 50/57 = 0.877 [0.767, 0.939] |
| fjc8_f1neg | vacated | 20 | 18/20 = 0.900 [0.699, 0.972] | 18/20 = 0.900 [0.699, 0.972] |
| fjc8_f1neg | stratum fed|1920s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| fjc8_f1neg | stratum fed|1930s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| fjc8_f1neg | stratum fed|1940s (population 25, sampled 8) | 8 | 6/8 | 6/8 |
| fjc8_f1neg | stratum fed|1950s (population 29, sampled 8) | 8 | 7/8 | 7/8 |
| fjc8_f1neg | stratum fed|1960s (population 52, sampled 8) | 8 | 8/8 | 8/8 |
| fjc8_f1neg | stratum fed|1970s (population 72, sampled 8) | 8 | 8/8 | 7/8 |
| fjc8_f1neg | stratum fed|1980s (population 124, sampled 8) | 8 | 7/8 | 7/8 |
| fjc8_f1neg | stratum fed|1990s (population 136, sampled 8) | 8 | 8/8 | 8/8 |
| fjc8_f1neg | stratum fed|2000s (population 147, sampled 8) | 8 | 8/8 | 8/8 |
| fjc8_f1neg | stratum fed|2010s (population 151, sampled 8) | 8 | 8/8 | 8/8 |
| fjc8_f1neg | stratum fed|2020s (population 18, sampled 9) | 9 | 4/9 | 4/9 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (19 lines).
