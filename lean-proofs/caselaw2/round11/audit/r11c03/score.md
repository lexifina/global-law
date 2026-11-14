# Blind audit score: r11c03 (type C)

- items in the key: 68 (60 sampled rows, 4 known-wrong decoys, 4 known-right decoys); answered: 68; answer files: 4
- right: link and the disposition agrees with the kind of row 1 (row2_*: of row 2). right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | row 2 right | row 2 right + extent | row 2 link + effect | only row 1 right | only row 2 right | 0.90 rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c11r | 60 | 60 | 53/60 = 0.883 [0.778, 0.942] | 53/60 = 0.883 [0.778, 0.942] | 58/60 = 0.967 [0.886, 0.991] | 54/60 = 0.900 [0.798, 0.953] | 3/60 = 0.050 [0.017, 0.137] | 3/60 = 0.050 [0.017, 0.137] | 4/60 = 0.067 [0.026, 0.159] | 53/60 = 0.883 [0.778, 0.942] | 3/60 = 0.050 [0.017, 0.137] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- c11r: right 0.883 [0.883, 0.883] (read in full); right + extent 0.883 [0.883, 0.883] (read in full)

Answers on sampled rows (every reader): c11r: affirmed 7, modified 1, none 4, reversed 6, reversed_or_vacated_in_part 96, vacated 6

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): c11r: kind 6, kind (same status effect) 1, kind; row 2: kind 2, link; row 2: link 4

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 14/16 = 0.875 [0.640, 0.965]
- known wrong, not confirmed: 6/8 = 0.750 [0.409, 0.928]
- known right, confirmed: 8/8 = 1.000 [0.676, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| pack_2 | 6/8 = 0.750 [0.409, 0.928] | 2/4 = 0.500 [0.150, 0.850] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10b03:scdb10_a10n | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t06:stlink_d2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 0/2 = 0.000 [0.000, 0.658] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p03:PJR | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 34 | 25/30 = 0.833 [0.664, 0.927] | 4/4 = 1.000 [0.510, 1.000] | 0 | 1 |
| ans_1_b.jsonl | 1 | 34 | 25/30 = 0.833 [0.664, 0.927] | 4/4 = 1.000 [0.510, 1.000] | 0 | 1 |
| ans_2.jsonl | 2 | 34 | 28/30 = 0.933 [0.787, 0.982] | 3/4 = 0.750 [0.301, 0.954] | 0 | 0 |
| ans_2_b.jsonl | 2 | 34 | 29/30 = 0.967 [0.833, 0.994] | 3/4 = 0.750 [0.301, 0.954] | 0 | 1 |

Items read twice: 68; same right answer 67/68 = 0.985 [0.921, 0.997]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| c11r | fed | 60 | 53/60 = 0.883 [0.778, 0.942] | 53/60 = 0.883 [0.778, 0.942] |
| c11r | 1950s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| c11r | 1970s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| c11r | 1980s | 8 | 6/8 = 0.750 [0.409, 0.928] | 6/8 = 0.750 [0.409, 0.928] |
| c11r | 1990s | 12 | 11/12 = 0.917 [0.646, 0.985] | 11/12 = 0.917 [0.646, 0.985] |
| c11r | 2000s | 24 | 22/24 = 0.917 [0.742, 0.977] | 22/24 = 0.917 [0.742, 0.977] |
| c11r | 2010s | 12 | 10/12 = 0.833 [0.552, 0.953] | 10/12 = 0.833 [0.552, 0.953] |
| c11r | modified/unknown vs affirmed/all | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| c11r | reversed/unknown vs affirmed/all | 27 | 23/27 = 0.852 [0.675, 0.941] | 23/27 = 0.852 [0.675, 0.941] |
| c11r | reversed/unknown vs affirmed/unknown | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| c11r | vacated/unknown vs affirmed/all | 14 | 14/14 = 1.000 [0.785, 1.000] | 14/14 = 1.000 [0.785, 1.000] |
| c11r | vacated/unknown vs affirmed/unknown | 7 | 6/7 = 0.857 [0.487, 0.974] | 6/7 = 0.857 [0.487, 0.974] |
| c11r | stratum fed|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| c11r | stratum fed|1970s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| c11r | stratum fed|1980s (population 8, sampled 8) | 8 | 6/8 | 6/8 |
| c11r | stratum fed|1990s (population 12, sampled 12) | 12 | 11/12 | 11/12 |
| c11r | stratum fed|2000s (population 24, sampled 24) | 24 | 22/24 | 22/24 |
| c11r | stratum fed|2010s (population 12, sampled 12) | 12 | 10/12 | 10/12 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (15 lines).
