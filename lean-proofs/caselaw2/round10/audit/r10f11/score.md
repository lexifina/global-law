# Blind audit score: r10f11 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc10b_h | 456 | 80 | 71/80 = 0.887 [0.800, 0.940] | 71/80 = 0.887 [0.800, 0.940] | 76/80 = 0.950 [0.878, 0.980] | 72/80 = 0.900 [0.815, 0.949] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc10b_h: right 0.895 [0.798, 0.949] (n_eff 66); right + extent 0.895 [0.798, 0.949] (n_eff 66)

Answers on sampled rows (every reader): fjc10b_h: modified 8, none 8, reversed 97, reversed_or_vacated_in_part 21, vacated 26

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc10b_h: kind 7, kind (same status effect) 2, link 8

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
| r6:a3:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a12:ohv | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f03:fjc9G2 | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k01:remandtext | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 24/26 = 0.923 [0.759, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc10b_h | fed | 80 | 71/80 = 0.887 [0.800, 0.940] | 71/80 = 0.887 [0.800, 0.940] |
| fjc10b_h | 1920s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| fjc10b_h | 1930s | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| fjc10b_h | 1940s | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| fjc10b_h | 1950s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc10b_h | 1960s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| fjc10b_h | 1970s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| fjc10b_h | 1980s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc10b_h | 1990s | 8 | 6/8 = 0.750 [0.409, 0.928] | 6/8 = 0.750 [0.409, 0.928] |
| fjc10b_h | 2000s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| fjc10b_h | 2010s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| fjc10b_h | modified | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| fjc10b_h | reversed | 60 | 54/60 = 0.900 [0.798, 0.953] | 54/60 = 0.900 [0.798, 0.953] |
| fjc10b_h | vacated | 14 | 13/14 = 0.929 [0.685, 0.987] | 13/14 = 0.929 [0.685, 0.987] |
| fjc10b_h | stratum fed|1920s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| fjc10b_h | stratum fed|1930s (population 9, sampled 9) | 9 | 7/9 | 7/9 |
| fjc10b_h | stratum fed|1940s (population 20, sampled 9) | 9 | 7/9 | 7/9 |
| fjc10b_h | stratum fed|1950s (population 28, sampled 9) | 9 | 8/9 | 8/9 |
| fjc10b_h | stratum fed|1960s (population 30, sampled 8) | 8 | 7/8 | 7/8 |
| fjc10b_h | stratum fed|1970s (population 63, sampled 9) | 9 | 9/9 | 9/9 |
| fjc10b_h | stratum fed|1980s (population 85, sampled 9) | 9 | 8/9 | 8/9 |
| fjc10b_h | stratum fed|1990s (population 100, sampled 8) | 8 | 6/8 | 6/8 |
| fjc10b_h | stratum fed|2000s (population 62, sampled 8) | 8 | 8/8 | 8/8 |
| fjc10b_h | stratum fed|2010s (population 56, sampled 8) | 8 | 8/8 | 8/8 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (17 lines).
