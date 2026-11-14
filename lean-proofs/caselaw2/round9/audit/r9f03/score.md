# Blind audit score: r9f03 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc9G2 | 180 | 80 | 67/80 = 0.838 [0.742, 0.902] | 64/80 = 0.800 [0.700, 0.873] | 76/80 = 0.950 [0.878, 0.980] | 70/80 = 0.875 [0.785, 0.931] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc9G2: right 0.869 [0.792, 0.920] (n_eff 106); right + extent 0.830 [0.747, 0.889] (n_eff 106)

Answers on sampled rows (every reader): fjc9G2: affirmed 8, modified 2, none 8, reversed 85, reversed_or_vacated_in_part 28, vacated 29

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc9G2: kind 11, kind (same status effect) 6, link 8, scope 6

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
| r6:a3:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 4/4 = 1.000 [0.510, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 4/4 = 1.000 [0.510, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 21/27 = 0.778 [0.592, 0.894] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 20/27 = 0.741 [0.553, 0.868] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc9G2 | fed | 80 | 67/80 = 0.838 [0.742, 0.902] | 64/80 = 0.800 [0.700, 0.873] |
| fjc9G2 | 1950s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| fjc9G2 | 1960s | 7 | 7/7 = 1.000 [0.646, 1.000] | 6/7 = 0.857 [0.487, 0.974] |
| fjc9G2 | 1970s | 18 | 15/18 = 0.833 [0.608, 0.942] | 14/18 = 0.778 [0.548, 0.910] |
| fjc9G2 | 1980s | 18 | 18/18 = 1.000 [0.824, 1.000] | 17/18 = 0.944 [0.742, 0.990] |
| fjc9G2 | 1990s | 18 | 13/18 = 0.722 [0.491, 0.875] | 13/18 = 0.722 [0.491, 0.875] |
| fjc9G2 | 2000s | 7 | 4/7 = 0.571 [0.251, 0.842] | 4/7 = 0.571 [0.251, 0.842] |
| fjc9G2 | 2010s | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| fjc9G2 | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc9G2 | reversed | 56 | 50/56 = 0.893 [0.785, 0.950] | 48/56 = 0.857 [0.743, 0.926] |
| fjc9G2 | vacated | 23 | 16/23 = 0.696 [0.491, 0.844] | 15/23 = 0.652 [0.449, 0.812] |
| fjc9G2 | stratum fed|1950s (population 13, sampled 3) | 3 | 3/3 | 3/3 |
| fjc9G2 | stratum fed|1960s (population 16, sampled 7) | 7 | 7/7 | 6/7 |
| fjc9G2 | stratum fed|1970s (population 35, sampled 18) | 18 | 15/18 | 14/18 |
| fjc9G2 | stratum fed|1980s (population 50, sampled 18) | 18 | 18/18 | 17/18 |
| fjc9G2 | stratum fed|1990s (population 25, sampled 18) | 18 | 13/18 | 13/18 |
| fjc9G2 | stratum fed|2000s (population 16, sampled 7) | 7 | 4/7 | 4/7 |
| fjc9G2 | stratum fed|2010s (population 17, sampled 9) | 9 | 7/9 | 7/9 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (31 lines).
