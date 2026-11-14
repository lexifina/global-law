# Blind audit score: r11k01 (type B)

- items in the key: 23 (20 sampled rows, 2 known-wrong decoys, 1 known-right decoys); answered: 23; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| capC11 | 20 | 20 | 17/20 = 0.850 [0.640, 0.948] | 17/20 = 0.850 [0.640, 0.948] | 17/20 = 0.850 [0.640, 0.948] | 17/20 = 0.850 [0.640, 0.948] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- capC11: right 0.850 [0.850, 0.850] (read in full); right + extent 0.850 [0.850, 0.850] (read in full)

Answers on sampled rows (every reader): capC11: none 4, vacated 36

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): capC11: link 5

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 6/6 = 1.000 [0.610, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:a3:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 23 | 17/20 = 0.850 [0.640, 0.948] | 3/3 = 1.000 [0.439, 1.000] | 1 | 1 |
| ans_1_b.jsonl | 1 | 23 | 18/20 = 0.900 [0.699, 0.972] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 23; same right answer 22/23 = 0.957 [0.790, 0.992]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| capC11 | fed | 20 | 17/20 = 0.850 [0.640, 0.948] | 17/20 = 0.850 [0.640, 0.948] |
| capC11 | 1970s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| capC11 | 2010s | 18 | 17/18 = 0.944 [0.742, 0.990] | 17/18 = 0.944 [0.742, 0.990] |
| capC11 | 2020s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| capC11 | vacated | 20 | 17/20 = 0.850 [0.640, 0.948] | 17/20 = 0.850 [0.640, 0.948] |
| capC11 | stratum fed|1970s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| capC11 | stratum fed|2010s (population 18, sampled 18) | 18 | 17/18 | 17/18 |
| capC11 | stratum fed|2020s (population 1, sampled 1) | 1 | 0/1 | 0/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (5 lines).
