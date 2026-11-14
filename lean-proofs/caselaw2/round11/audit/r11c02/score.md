# Blind audit score: r11c02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| c11b | 127 | 80 | 73/80 = 0.912 [0.830, 0.957] | 73/80 = 0.912 [0.830, 0.957] | 74/80 = 0.925 [0.846, 0.965] | 73/80 = 0.912 [0.830, 0.957] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- c11b: right 0.908 [0.859, 0.942] (n_eff 190); right + extent 0.908 [0.859, 0.942] (n_eff 190)

Answers on sampled rows (every reader): c11b: modified 2, none 10, other 1, reversed 106, reversed_or_vacated_in_part 23, review_dismissed 2, vacated 16

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): c11b: kind 3, link 10

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
| r10:r10b01:scdb10_a10 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t01:stlink_s1 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t02:stlink_g2 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10y01:syl10_RO_hist | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a15:b4e_rp | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k01:remandtext | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p02:PJH | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_1_b.jsonl | 1 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| c11b | fed | 80 | 73/80 = 0.912 [0.830, 0.957] | 73/80 = 0.912 [0.830, 0.957] |
| c11b | 1950s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| c11b | 1960s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| c11b | 1970s | 15 | 15/15 = 1.000 [0.796, 1.000] | 15/15 = 1.000 [0.796, 1.000] |
| c11b | 1980s | 15 | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] |
| c11b | 1990s | 15 | 12/15 = 0.800 [0.548, 0.929] | 12/15 = 0.800 [0.548, 0.929] |
| c11b | 2000s | 16 | 16/16 = 1.000 [0.806, 1.000] | 16/16 = 1.000 [0.806, 1.000] |
| c11b | 2010s | 15 | 12/15 = 0.800 [0.548, 0.929] | 12/15 = 0.800 [0.548, 0.929] |
| c11b | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| c11b | reversed | 66 | 60/66 = 0.909 [0.816, 0.958] | 60/66 = 0.909 [0.816, 0.958] |
| c11b | vacated | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| c11b | stratum fed|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| c11b | stratum fed|1960s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| c11b | stratum fed|1970s (population 25, sampled 15) | 15 | 15/15 | 15/15 |
| c11b | stratum fed|1980s (population 19, sampled 15) | 15 | 14/15 | 14/15 |
| c11b | stratum fed|1990s (population 33, sampled 15) | 15 | 12/15 | 12/15 |
| c11b | stratum fed|2000s (population 27, sampled 16) | 16 | 16/16 | 16/16 |
| c11b | stratum fed|2010s (population 19, sampled 15) | 15 | 12/15 | 12/15 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (13 lines).
