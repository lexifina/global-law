# Blind audit score: r12t02 (type B)

- items in the key: 18 (16 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 18; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_u2t_other | 16 | 16 | 15/16 = 0.938 [0.717, 0.989] | 15/16 = 0.938 [0.717, 0.989] | 16/16 = 1.000 [0.806, 1.000] | 16/16 = 1.000 [0.806, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_u2t_other: right 0.938 [0.938, 0.938] (read in full); right + extent 0.938 [0.938, 0.938] (read in full)

Answers on sampled rows (every reader): stlink_u2t_other: modified 8, reversed 18, reversed_or_vacated_in_part 4, vacated 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_u2t_other: kind (same status effect) 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10b01:scdb10_a10 | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 18 | 15/16 = 0.938 [0.717, 0.989] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 18 | 15/16 = 0.938 [0.717, 0.989] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 18; same right answer 18/18 = 1.000 [0.824, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_u2t_other | state | 16 | 15/16 = 0.938 [0.717, 0.989] | 15/16 = 0.938 [0.717, 0.989] |
| stlink_u2t_other | 1950s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2t_other | 1970s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| stlink_u2t_other | 1980s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| stlink_u2t_other | 1990s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2t_other | 2010s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| stlink_u2t_other | modified | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| stlink_u2t_other | reversed | 12 | 11/12 = 0.917 [0.646, 0.985] | 11/12 = 0.917 [0.646, 0.985] |
| stlink_u2t_other | stratum state|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2t_other | stratum state|1970s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| stlink_u2t_other | stratum state|1980s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| stlink_u2t_other | stratum state|1990s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2t_other | stratum state|2010s (population 6, sampled 6) | 6 | 5/6 | 5/6 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
