# Blind audit score: r8f04 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc8_oc | 183 | 80 | 63/80 = 0.787 [0.686, 0.863] | 63/80 = 0.787 [0.686, 0.863] | 72/80 = 0.900 [0.815, 0.949] | 63/80 = 0.787 [0.686, 0.863] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc8_oc: right 0.790 [0.667, 0.876] (n_eff 56); right + extent 0.790 [0.667, 0.876] (n_eff 56)

Answers on sampled rows (every reader): fjc8_oc: affirmed 10, modified 4, none 15, reversed 99, reversed_or_vacated_in_part 28, vacated 4

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc8_oc: kind 18, link 15

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
| r6:r1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/other | 4/4 = 1.000 [0.510, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 20/27 = 0.741 [0.553, 0.868] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 20/27 = 0.741 [0.553, 0.868] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |
| ans_3.jsonl | 3 | 29 | 21/26 = 0.808 [0.621, 0.915] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 20/26 = 0.769 [0.580, 0.890] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc8_oc | fed | 80 | 63/80 = 0.787 [0.686, 0.863] | 63/80 = 0.787 [0.686, 0.863] |
| fjc8_oc | 1920s | 9 | 5/9 = 0.556 [0.267, 0.811] | 5/9 = 0.556 [0.267, 0.811] |
| fjc8_oc | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc8_oc | 1940s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| fjc8_oc | 1950s | 14 | 9/14 = 0.643 [0.388, 0.837] | 9/14 = 0.643 [0.388, 0.837] |
| fjc8_oc | 1960s | 18 | 18/18 = 1.000 [0.824, 1.000] | 18/18 = 1.000 [0.824, 1.000] |
| fjc8_oc | 1970s | 18 | 14/18 = 0.778 [0.548, 0.910] | 14/18 = 0.778 [0.548, 0.910] |
| fjc8_oc | 1980s | 17 | 14/17 = 0.824 [0.590, 0.938] | 14/17 = 0.824 [0.590, 0.938] |
| fjc8_oc | modified | 4 | 2/4 = 0.500 [0.150, 0.850] | 2/4 = 0.500 [0.150, 0.850] |
| fjc8_oc | reversed | 66 | 55/66 = 0.833 [0.726, 0.904] | 55/66 = 0.833 [0.726, 0.904] |
| fjc8_oc | vacated | 10 | 6/10 = 0.600 [0.313, 0.832] | 6/10 = 0.600 [0.313, 0.832] |
| fjc8_oc | stratum fed|1920s (population 9, sampled 9) | 9 | 5/9 | 5/9 |
| fjc8_oc | stratum fed|1930s (population 2, sampled 1) | 1 | 1/1 | 1/1 |
| fjc8_oc | stratum fed|1940s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| fjc8_oc | stratum fed|1950s (population 15, sampled 14) | 14 | 9/14 | 9/14 |
| fjc8_oc | stratum fed|1960s (population 24, sampled 18) | 18 | 18/18 | 18/18 |
| fjc8_oc | stratum fed|1970s (population 112, sampled 18) | 18 | 14/18 | 14/18 |
| fjc8_oc | stratum fed|1980s (population 18, sampled 17) | 17 | 14/17 | 14/17 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (33 lines).
