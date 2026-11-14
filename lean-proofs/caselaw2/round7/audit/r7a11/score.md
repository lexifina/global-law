# Blind audit score: r7a11 (type A)

- items in the key: 22 (19 sampled rows, 2 known-wrong decoys, 1 known-right decoys); answered: 22; answer files: 1
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| dct | 19 | 19 | 19/19 = 1.000 [0.832, 1.000] | 19/19 = 1.000 [0.832, 1.000] | 19/19 = 1.000 [0.832, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- dct: right 1.000 [1.000, 1.000] (read in full); right + extent 1.000 [1.000, 1.000] (read in full)

Answers on sampled rows (every reader): dct: overrule 13, reject_doctrine 6

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): dct: none

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 3/3 = 1.000 [0.439, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 1/1 = 1.000 [0.206, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 1/1 = 1.000 [0.206, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:control-self | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-round4 | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:decoy | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 22 | 19/19 = 1.000 [0.832, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| dct | fed | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| dct | state | 15 | 15/15 = 1.000 [0.796, 1.000] | 15/15 = 1.000 [0.796, 1.000] |
| dct | 1940s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| dct | 1950s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| dct | 1970s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| dct | 1980s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| dct | 1990s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| dct | 2000s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| dct | 2010s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| dct | doctrine | 19 | 19/19 = 1.000 [0.832, 1.000] | 19/19 = 1.000 [0.832, 1.000] |
| dct | stratum fed|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| dct | stratum fed|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| dct | stratum fed|2000s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| dct | stratum fed|2010s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| dct | stratum state|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| dct | stratum state|1970s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| dct | stratum state|1980s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| dct | stratum state|1990s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| dct | stratum state|2010s (population 5, sampled 5) | 5 | 5/5 | 5/5 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (0 lines).
