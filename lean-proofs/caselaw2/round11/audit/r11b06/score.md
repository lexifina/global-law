# Blind audit score: r11b06 (type B)

- items in the key: 6 (4 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 6; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb11_r4 | 4 | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb11_r4: right 1.000 [1.000, 1.000] (read in full); right + extent 1.000 [1.000, 1.000] (read in full)

Answers on sampled rows (every reader): scdb11_r4: reversed 8

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb11_r4: none

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:v2:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 6 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 6 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 6; same right answer 6/6 = 1.000 [0.610, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb11_r4 | fed | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb11_r4 | 1960s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb11_r4 | 1970s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb11_r4 | reversed | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb11_r4 | stratum fed|1960s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scdb11_r4 | stratum fed|1970s (population 1, sampled 1) | 1 | 1/1 | 1/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (0 lines).
