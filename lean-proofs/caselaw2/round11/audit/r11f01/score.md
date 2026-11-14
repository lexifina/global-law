# Blind audit score: r11f01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc11_x2b | 140 | 80 | 68/80 = 0.850 [0.756, 0.912] | 68/80 = 0.850 [0.756, 0.912] | 76/80 = 0.950 [0.878, 0.980] | 70/80 = 0.875 [0.785, 0.931] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc11_x2b: right 0.849 [0.786, 0.896] (n_eff 163); right + extent 0.849 [0.786, 0.896] (n_eff 163)

Answers on sampled rows (every reader): fjc11_x2b: affirmed 6, modified 2, none 8, reversed 77, reversed_or_vacated_in_part 40, review_dismissed 4, vacated 23

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc11_x2b: kind 12, kind (same status effect) 3, link 8

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
| r10:r10f12:fjc10b_xs | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10k01:capC6 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t03:stlink_T | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t05:stlink_u1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 4/4 = 1.000 [0.510, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 21/26 = 0.808 [0.621, 0.915] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 22/26 = 0.846 [0.665, 0.939] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc11_x2b | fed | 80 | 68/80 = 0.850 [0.756, 0.912] | 68/80 = 0.850 [0.756, 0.912] |
| fjc11_x2b | 1930s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| fjc11_x2b | 1940s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| fjc11_x2b | 1960s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| fjc11_x2b | 1970s | 14 | 12/14 = 0.857 [0.601, 0.960] | 12/14 = 0.857 [0.601, 0.960] |
| fjc11_x2b | 1980s | 14 | 12/14 = 0.857 [0.601, 0.960] | 12/14 = 0.857 [0.601, 0.960] |
| fjc11_x2b | 1990s | 13 | 11/13 = 0.846 [0.578, 0.957] | 11/13 = 0.846 [0.578, 0.957] |
| fjc11_x2b | 2000s | 14 | 12/14 = 0.857 [0.601, 0.960] | 12/14 = 0.857 [0.601, 0.960] |
| fjc11_x2b | 2010s | 13 | 13/13 = 1.000 [0.772, 1.000] | 13/13 = 1.000 [0.772, 1.000] |
| fjc11_x2b | 2020s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| fjc11_x2b | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc11_x2b | reversed | 59 | 51/59 = 0.864 [0.755, 0.930] | 51/59 = 0.864 [0.755, 0.930] |
| fjc11_x2b | vacated | 20 | 16/20 = 0.800 [0.584, 0.919] | 16/20 = 0.800 [0.584, 0.919] |
| fjc11_x2b | stratum fed|1930s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| fjc11_x2b | stratum fed|1940s (population 5, sampled 3) | 3 | 2/3 | 2/3 |
| fjc11_x2b | stratum fed|1960s (population 6, sampled 6) | 6 | 4/6 | 4/6 |
| fjc11_x2b | stratum fed|1970s (population 18, sampled 14) | 14 | 12/14 | 12/14 |
| fjc11_x2b | stratum fed|1980s (population 30, sampled 14) | 14 | 12/14 | 12/14 |
| fjc11_x2b | stratum fed|1990s (population 28, sampled 13) | 13 | 11/13 | 11/13 |
| fjc11_x2b | stratum fed|2000s (population 30, sampled 14) | 14 | 12/14 | 12/14 |
| fjc11_x2b | stratum fed|2010s (population 19, sampled 13) | 13 | 13/13 | 13/13 |
| fjc11_x2b | stratum fed|2020s (population 2, sampled 1) | 1 | 0/1 | 0/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (23 lines).
