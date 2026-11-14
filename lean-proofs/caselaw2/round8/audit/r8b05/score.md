# Blind audit score: r8b05 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb8_wide | 83 | 80 | 78/80 = 0.975 [0.913, 0.993] | 78/80 = 0.975 [0.913, 0.993] | 78/80 = 0.975 [0.913, 0.993] | 78/80 = 0.975 [0.913, 0.993] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb8_wide: right 0.976 [0.968, 0.982] (n_eff 2050); right + extent 0.976 [0.968, 0.982] (n_eff 2050)

Answers on sampled rows (every reader): scdb8_wide: none 4, reversed 112, reversed_or_vacated_in_part 10, vacated 34

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb8_wide: link 4

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 16/18 = 0.889 [0.672, 0.969]
- known wrong, not confirmed: 10/12 = 0.833 [0.552, 0.953]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 4/6 = 0.667 [0.300, 0.903] | 2/4 = 0.500 [0.150, 0.850] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 0/2 = 0.000 [0.000, 0.658] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a17:rh_eb | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 1 |
| ans_3_b.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb8_wide | fed | 80 | 78/80 = 0.975 [0.913, 0.993] | 78/80 = 0.975 [0.913, 0.993] |
| scdb8_wide | 1890s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_wide | 1960s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_wide | 1970s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_wide | 1980s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb8_wide | 1990s | 17 | 17/17 = 1.000 [0.816, 1.000] | 17/17 = 1.000 [0.816, 1.000] |
| scdb8_wide | 2000s | 25 | 25/25 = 1.000 [0.867, 1.000] | 25/25 = 1.000 [0.867, 1.000] |
| scdb8_wide | 2010s | 25 | 25/25 = 1.000 [0.867, 1.000] | 25/25 = 1.000 [0.867, 1.000] |
| scdb8_wide | 2020s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| scdb8_wide | reversed | 62 | 61/62 = 0.984 [0.914, 0.997] | 61/62 = 0.984 [0.914, 0.997] |
| scdb8_wide | vacated | 18 | 17/18 = 0.944 [0.742, 0.990] | 17/18 = 0.944 [0.742, 0.990] |
| scdb8_wide | stratum fed|1890s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_wide | stratum fed|1960s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_wide | stratum fed|1970s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_wide | stratum fed|1980s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| scdb8_wide | stratum fed|1990s (population 17, sampled 17) | 17 | 17/17 | 17/17 |
| scdb8_wide | stratum fed|2000s (population 25, sampled 25) | 25 | 25/25 | 25/25 |
| scdb8_wide | stratum fed|2010s (population 28, sampled 25) | 25 | 25/25 | 25/25 |
| scdb8_wide | stratum fed|2020s (population 6, sampled 6) | 6 | 4/6 | 4/6 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (6 lines).
