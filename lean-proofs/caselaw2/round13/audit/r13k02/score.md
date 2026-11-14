# Blind audit score: r13k02 (type B)

- items in the key: 11 (9 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 11; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| shadow13_S | 11 | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- shadow13_S: right 1.000 [0.840, 1.000] (n_eff 20); right + extent 1.000 [0.840, 1.000] (n_eff 20)

Answers on sampled rows (every reader): shadow13_S: reversed 2, vacated 16

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): shadow13_S: none

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r7:r7a16:b4a_r3k | 4/4 = 1.000 [0.510, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 11 | 9/9 = 1.000 [0.701, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 11 | 9/9 = 1.000 [0.701, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 11; same right answer 11/11 = 1.000 [0.741, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| shadow13_S | fed | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| shadow13_S | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| shadow13_S | 2000s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| shadow13_S | 2020s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| shadow13_S | reversed | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| shadow13_S | vacated | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| shadow13_S | stratum fed|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| shadow13_S | stratum fed|2000s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| shadow13_S | stratum fed|2020s (population 7, sampled 7) | 7 | 7/7 | 7/7 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (0 lines).
