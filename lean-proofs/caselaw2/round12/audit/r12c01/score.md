# Blind audit score: r12c01 (type B)

- items in the key: 55 (49 sampled rows, 4 known-wrong decoys, 2 known-right decoys); answered: 55; answer files: 4
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| c12m | 49 | 49 | 25/49 = 0.510 [0.375, 0.644] | 25/49 = 0.510 [0.375, 0.644] | 26/49 = 0.531 [0.394, 0.663] | 25/49 = 0.510 [0.375, 0.644] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- c12m: right 0.510 [0.510, 0.510] (read in full); right + extent 0.510 [0.510, 0.510] (read in full)

Answers on sampled rows (every reader): c12m: affirmed 2, none 43, other 1, reversed 36, reversed_or_vacated_in_part 2, vacated 14

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): c12m: kind 3, link 43

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 12/12 = 1.000 [0.757, 1.000]
- known wrong, not confirmed: 8/8 = 1.000 [0.676, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r11:r11b05:scdb11_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r11:r11k01:capC11 | 2/2 = 1.000 [0.342, 1.000] |
| r11:r11k03:olK9 | 2/2 = 1.000 [0.342, 1.000] |
| r11:r11k04:ol2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 28 | 15/25 = 0.600 [0.407, 0.766] | 3/3 = 1.000 [0.439, 1.000] | 0 | 3 |
| ans_1_b.jsonl | 1 | 28 | 17/25 = 0.680 [0.484, 0.828] | 3/3 = 1.000 [0.439, 1.000] | 0 | 4 |
| ans_2.jsonl | 2 | 27 | 10/24 = 0.417 [0.245, 0.612] | 3/3 = 1.000 [0.439, 1.000] | 0 | 4 |
| ans_2_b.jsonl | 2 | 27 | 10/24 = 0.417 [0.245, 0.612] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |

Items read twice: 55; same right answer 53/55 = 0.964 [0.877, 0.990]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| c12m | fed | 49 | 25/49 = 0.510 [0.375, 0.644] | 25/49 = 0.510 [0.375, 0.644] |
| c12m | 1950s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| c12m | 1980s | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| c12m | 1990s | 13 | 7/13 = 0.538 [0.291, 0.768] | 7/13 = 0.538 [0.291, 0.768] |
| c12m | 2000s | 19 | 10/19 = 0.526 [0.317, 0.727] | 10/19 = 0.526 [0.317, 0.727] |
| c12m | 2010s | 13 | 6/13 = 0.462 [0.232, 0.709] | 6/13 = 0.462 [0.232, 0.709] |
| c12m | 2020s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| c12m | reversed | 37 | 18/37 = 0.486 [0.335, 0.641] | 18/37 = 0.486 [0.335, 0.641] |
| c12m | vacated | 12 | 7/12 = 0.583 [0.320, 0.807] | 7/12 = 0.583 [0.320, 0.807] |
| c12m | stratum fed|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| c12m | stratum fed|1980s (population 2, sampled 2) | 2 | 0/2 | 0/2 |
| c12m | stratum fed|1990s (population 13, sampled 13) | 13 | 7/13 | 7/13 |
| c12m | stratum fed|2000s (population 19, sampled 19) | 19 | 10/19 | 10/19 |
| c12m | stratum fed|2010s (population 13, sampled 13) | 13 | 6/13 | 6/13 |
| c12m | stratum fed|2020s (population 1, sampled 1) | 1 | 1/1 | 1/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (46 lines).
