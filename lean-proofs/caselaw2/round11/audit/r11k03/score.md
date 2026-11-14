# Blind audit score: r11k03 (type B)

- items in the key: 40 (36 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 40; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| olK9 | 36 | 36 | 35/36 = 0.972 [0.858, 0.995] | 35/36 = 0.972 [0.858, 0.995] | 35/36 = 0.972 [0.858, 0.995] | 35/36 = 0.972 [0.858, 0.995] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- olK9: right 0.972 [0.972, 0.972] (read in full); right + extent 0.972 [0.972, 0.972] (read in full)

Answers on sampled rows (every reader): olK9: none 2, vacated 70

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): olK9: link 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/8 = 1.000 [0.676, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10t01:stlink_s1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p03:PJR | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 40 | 35/36 = 0.972 [0.858, 0.995] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 40 | 35/36 = 0.972 [0.858, 0.995] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |

Items read twice: 40; same right answer 40/40 = 1.000 [0.912, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| olK9 | fed | 36 | 35/36 = 0.972 [0.858, 0.995] | 35/36 = 0.972 [0.858, 0.995] |
| olK9 | 2000s | 27 | 27/27 = 1.000 [0.875, 1.000] | 27/27 = 1.000 [0.875, 1.000] |
| olK9 | 2020s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| olK9 | vacated | 36 | 35/36 = 0.972 [0.858, 0.995] | 35/36 = 0.972 [0.858, 0.995] |
| olK9 | stratum fed|2000s (population 27, sampled 27) | 27 | 27/27 | 27/27 |
| olK9 | stratum fed|2020s (population 9, sampled 9) | 9 | 8/9 | 8/9 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
