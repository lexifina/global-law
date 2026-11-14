# Blind audit score: r7a19 (type B)

- items in the key: 62 (55 sampled rows, 4 known-wrong decoys, 3 known-right decoys); answered: 62; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| rh_sil | 55 | 55 | 54/55 = 0.982 [0.904, 0.997] | 53/55 = 0.964 [0.877, 0.990] | 54/55 = 0.982 [0.904, 0.997] | 54/55 = 0.982 [0.904, 0.997] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- rh_sil: right 0.982 [0.982, 0.982] (read in full); right + extent 0.964 [0.964, 0.964] (read in full)

Answers on sampled rows (every reader): rh_sil: none 1, rehearing_en_banc_only 46, vacated 8

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): rh_sil: link 1, scope 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 7/7 = 1.000 [0.646, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 3/3 = 1.000 [0.439, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 1/1 = 1.000 [0.206, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/docket | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:memo/caption | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:decoy_base | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 32 | 27/28 = 0.964 [0.823, 0.994] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| rh_sil | fed | 53 | 52/53 = 0.981 [0.901, 0.997] | 51/53 = 0.962 [0.873, 0.990] |
| rh_sil | state | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| rh_sil | 1970s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| rh_sil | 1980s | 15 | 14/15 = 0.933 [0.702, 0.988] | 13/15 = 0.867 [0.621, 0.963] |
| rh_sil | 1990s | 15 | 15/15 = 1.000 [0.796, 1.000] | 15/15 = 1.000 [0.796, 1.000] |
| rh_sil | 2000s | 15 | 15/15 = 1.000 [0.796, 1.000] | 15/15 = 1.000 [0.796, 1.000] |
| rh_sil | 2010s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| rh_sil | rehearingEnBancGranted | 55 | 54/55 = 0.982 [0.904, 0.997] | 53/55 = 0.964 [0.877, 0.990] |
| rh_sil | stratum fed|1970s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| rh_sil | stratum fed|1980s (population 15, sampled 15) | 15 | 14/15 | 13/15 |
| rh_sil | stratum fed|1990s (population 15, sampled 15) | 15 | 15/15 | 15/15 |
| rh_sil | stratum fed|2000s (population 13, sampled 13) | 13 | 13/13 | 13/13 |
| rh_sil | stratum fed|2010s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| rh_sil | stratum state|2000s (population 2, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
