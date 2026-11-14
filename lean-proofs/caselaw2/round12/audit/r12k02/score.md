# Blind audit score: r12k02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| shNew | 321 | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- shNew: right 0.962 [0.906, 0.985] (n_eff 104); right + extent 0.962 [0.906, 0.985] (n_eff 104)

Answers on sampled rows (every reader): shNew: none 4, reversed_or_vacated_in_part 5, vacated 151

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): shNew: link 4

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
| r10:r10k03:capC9 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t03:stlink_T | 2/2 = 1.000 [0.342, 1.000] |
| r11:r11k01:capC11 | 2/2 = 1.000 [0.342, 1.000] |
| r11:r11k03:olK9 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p02:PJH | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 1 | 1 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 87/89 = 0.978 [0.922, 0.994]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| shNew | fed | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] |
| shNew | 2000s | 78 | 75/78 = 0.962 [0.893, 0.987] | 75/78 = 0.962 [0.893, 0.987] |
| shNew | 2020s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| shNew | vacated | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] |
| shNew | stratum fed|2000s (population 319, sampled 78) | 78 | 75/78 | 75/78 |
| shNew | stratum fed|2020s (population 2, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (4 lines).
