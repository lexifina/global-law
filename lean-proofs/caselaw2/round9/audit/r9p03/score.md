# Blind audit score: r9p03 (type B)

- items in the key: 16 (14 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 16; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| PJR | 14 | 14 | 13/14 = 0.929 [0.685, 0.987] | 13/14 = 0.929 [0.685, 0.987] | 14/14 = 1.000 [0.785, 1.000] | 14/14 = 1.000 [0.785, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- PJR: right 0.929 [0.929, 0.929] (read in full); right + extent 0.929 [0.929, 0.929] (read in full)

Answers on sampled rows (every reader): PJR: withdrawn_or_superseded 28

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): PJR: kind (same status effect) 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 16 | 13/14 = 0.929 [0.685, 0.987] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 16 | 13/14 = 0.929 [0.685, 0.987] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 16; same right answer 16/16 = 1.000 [0.806, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| PJR | fed | 14 | 13/14 = 0.929 [0.685, 0.987] | 13/14 = 0.929 [0.685, 0.987] |
| PJR | 1990s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| PJR | 2000s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| PJR | 2010s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| PJR | vacated | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| PJR | withdrawn | 13 | 13/13 = 1.000 [0.772, 1.000] | 13/13 = 1.000 [0.772, 1.000] |
| PJR | stratum fed|1990s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| PJR | stratum fed|2000s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| PJR | stratum fed|2010s (population 6, sampled 6) | 6 | 6/6 | 6/6 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
