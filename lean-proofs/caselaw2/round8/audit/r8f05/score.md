# Blind audit score: r8f05 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc8_f1neg | 757 | 80 | 73/80 = 0.912 [0.830, 0.957] | 73/80 = 0.912 [0.830, 0.957] | 76/80 = 0.950 [0.878, 0.980] | 75/80 = 0.938 [0.862, 0.973] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc8_f1neg: right 0.903 [0.805, 0.954] (n_eff 64); right + extent 0.903 [0.805, 0.954] (n_eff 64)

Answers on sampled rows (every reader): fjc8_f1neg: affirmed 2, modified 2, none 7, reversed 93, reversed_or_vacated_in_part 34, vacated 22

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc8_f1neg: kind 2, kind (same status effect) 4, link 7

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 16/18 = 0.889 [0.672, 0.969]
- known wrong, not confirmed: 10/12 = 0.833 [0.552, 0.953]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/6 = 0.667 [0.300, 0.903] | 2/4 = 0.500 [0.150, 0.850] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 0/2 = 0.000 [0.000, 0.658] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a15:b4e_rp | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 1 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 1 |
| ans_2.jsonl | 2 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc8_f1neg | fed | 80 | 73/80 = 0.912 [0.830, 0.957] | 73/80 = 0.912 [0.830, 0.957] |
| fjc8_f1neg | 1940s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| fjc8_f1neg | 1950s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| fjc8_f1neg | 1960s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| fjc8_f1neg | 1970s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc8_f1neg | 1980s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| fjc8_f1neg | 1990s | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| fjc8_f1neg | 2000s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc8_f1neg | 2010s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| fjc8_f1neg | 2020s | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| fjc8_f1neg | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc8_f1neg | reversed | 59 | 55/59 = 0.932 [0.838, 0.973] | 55/59 = 0.932 [0.838, 0.973] |
| fjc8_f1neg | vacated | 20 | 17/20 = 0.850 [0.640, 0.948] | 17/20 = 0.850 [0.640, 0.948] |
| fjc8_f1neg | stratum fed|1940s (population 26, sampled 9) | 9 | 9/9 | 9/9 |
| fjc8_f1neg | stratum fed|1950s (population 29, sampled 9) | 9 | 9/9 | 9/9 |
| fjc8_f1neg | stratum fed|1960s (population 52, sampled 9) | 9 | 9/9 | 9/9 |
| fjc8_f1neg | stratum fed|1970s (population 80, sampled 9) | 9 | 8/9 | 8/9 |
| fjc8_f1neg | stratum fed|1980s (population 124, sampled 8) | 8 | 7/8 | 7/8 |
| fjc8_f1neg | stratum fed|1990s (population 133, sampled 9) | 9 | 7/9 | 7/9 |
| fjc8_f1neg | stratum fed|2000s (population 144, sampled 9) | 9 | 8/9 | 8/9 |
| fjc8_f1neg | stratum fed|2010s (population 145, sampled 9) | 9 | 9/9 | 9/9 |
| fjc8_f1neg | stratum fed|2020s (population 17, sampled 9) | 9 | 7/9 | 7/9 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (15 lines).
