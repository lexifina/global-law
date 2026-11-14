# Blind audit score: r9p01 (type A)

- items in the key: 26 (23 sampled rows, 2 known-wrong decoys, 1 known-right decoys); answered: 26; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| PJT | 23 | 23 | 23/23 = 1.000 [0.857, 1.000] | 23/23 = 1.000 [0.857, 1.000] | 23/23 = 1.000 [0.857, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- PJT: right 1.000 [1.000, 1.000] (read in full); right + extent 1.000 [1.000, 1.000] (read in full)

Answers on sampled rows (every reader): PJT: overrule 46

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): PJT: none

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/6 = 0.667 [0.300, 0.903]
- known wrong, not confirmed: 2/4 = 0.500 [0.150, 0.850]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/6 = 0.667 [0.300, 0.903] | 2/4 = 0.500 [0.150, 0.850] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:test_it0:recognised | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a02:opwwhole | 0/2 = 0.000 [0.000, 0.658] |
| r7:r7a09:scctl | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 26 | 23/23 = 1.000 [0.857, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 0 |
| ans_1_b.jsonl | 1 | 26 | 23/23 = 1.000 [0.857, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 0 |

Items read twice: 26; same right answer 26/26 = 1.000 [0.871, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| PJT | fed | 23 | 23/23 = 1.000 [0.857, 1.000] | 23/23 = 1.000 [0.857, 1.000] |
| PJT | 1990s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| PJT | 2000s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| PJT | 2010s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| PJT | own_part | 17 | 17/17 = 1.000 [0.816, 1.000] | 17/17 = 1.000 [0.816, 1.000] |
| PJT | own_whole | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| PJT | stratum fed|1990s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| PJT | stratum fed|2000s (population 11, sampled 11) | 11 | 11/11 | 11/11 |
| PJT | stratum fed|2010s (population 6, sampled 6) | 6 | 6/6 | 6/6 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
