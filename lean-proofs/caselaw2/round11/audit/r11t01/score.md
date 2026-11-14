# Blind audit score: r11t01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_u2 | 543 | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | 78/80 = 0.975 [0.913, 0.993] | 78/80 = 0.975 [0.913, 0.993] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_u2: right 0.952 [0.868, 0.983] (n_eff 63); right + extent 0.952 [0.868, 0.983] (n_eff 63)

Answers on sampled rows (every reader): stlink_u2: modified 14, none 4, reversed 121, reversed_or_vacated_in_part 11, vacated 10

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_u2: kind (same status effect) 2, link 4

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
| r10:r10f11:fjc10b_h | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t01:stlink_s1 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t02:stlink_g2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 4/4 = 1.000 [0.510, 1.000] |
| r7:r7a15:b4e_rp | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k01:remandtext | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_u2 | state | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] |
| stlink_u2 | 1890s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| stlink_u2 | 1900s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| stlink_u2 | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2 | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2 | 1940s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2 | 1950s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| stlink_u2 | 1960s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_u2 | 1970s | 11 | 10/11 = 0.909 [0.623, 0.984] | 10/11 = 0.909 [0.623, 0.984] |
| stlink_u2 | 1980s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| stlink_u2 | 1990s | 11 | 10/11 = 0.909 [0.623, 0.984] | 10/11 = 0.909 [0.623, 0.984] |
| stlink_u2 | 2000s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| stlink_u2 | 2010s | 11 | 10/11 = 0.909 [0.623, 0.984] | 10/11 = 0.909 [0.623, 0.984] |
| stlink_u2 | modified | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_u2 | reversed | 67 | 65/67 = 0.970 [0.897, 0.992] | 65/67 = 0.970 [0.897, 0.992] |
| stlink_u2 | vacated | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| stlink_u2 | stratum state|1890s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| stlink_u2 | stratum state|1900s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| stlink_u2 | stratum state|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2 | stratum state|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2 | stratum state|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2 | stratum state|1950s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| stlink_u2 | stratum state|1960s (population 9, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_u2 | stratum state|1970s (population 41, sampled 11) | 11 | 10/11 | 10/11 |
| stlink_u2 | stratum state|1980s (population 129, sampled 12) | 12 | 12/12 | 12/12 |
| stlink_u2 | stratum state|1990s (population 130, sampled 11) | 11 | 10/11 | 10/11 |
| stlink_u2 | stratum state|2000s (population 101, sampled 12) | 12 | 12/12 | 12/12 |
| stlink_u2 | stratum state|2010s (population 118, sampled 11) | 11 | 10/11 | 10/11 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (6 lines).
