# Blind audit score: r7a02 (type A)

- items in the key: 34 (30 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 34; answer files: 1
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| opwwhole | 30 | 30 | 10/30 = 0.333 [0.192, 0.512] | 7/30 = 0.233 [0.118, 0.409] | 30/30 = 1.000 [0.886, 1.000] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- opwwhole: right 0.333 [0.333, 0.333] (read in full); right + extent 0.233 [0.233, 0.233] (read in full)

Answers on sampled rows (every reader): opwwhole: limit 15, overrule 10, reject_doctrine 3, report_other 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): opwwhole: act 20, extent 3

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 3/4 = 0.750 [0.301, 0.954]
- known wrong, not confirmed: 1/2 = 0.500 [0.095, 0.905]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 3/4 = 0.750 [0.301, 0.954] | 1/2 = 0.500 [0.095, 0.905] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:recog1:control-self | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-pattern | 0/1 = 0.000 [0.000, 0.793] |
| r5:recog1:recog-read-part | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-round4 | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 34 | 10/30 = 0.333 [0.192, 0.512] | 3/4 = 0.750 [0.301, 0.954] | 0 | 1 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| opwwhole | fed | 5 | 4/5 = 0.800 [0.376, 0.964] | 3/5 = 0.600 [0.231, 0.882] |
| opwwhole | state | 25 | 6/25 = 0.240 [0.115, 0.434] | 4/25 = 0.160 [0.064, 0.346] |
| opwwhole | 1860s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| opwwhole | 1920s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| opwwhole | 1960s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| opwwhole | 1980s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| opwwhole | 1990s | 8 | 2/8 = 0.250 [0.071, 0.591] | 1/8 = 0.125 [0.022, 0.471] |
| opwwhole | 2000s | 7 | 1/7 = 0.143 [0.026, 0.513] | 1/7 = 0.143 [0.026, 0.513] |
| opwwhole | 2010s | 7 | 2/7 = 0.286 [0.082, 0.641] | 0/7 = 0.000 [0.000, 0.354] |
| opwwhole | 2020s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| opwwhole | own_whole | 30 | 10/30 = 0.333 [0.192, 0.512] | 7/30 = 0.233 [0.118, 0.409] |
| opwwhole | stratum fed|1960s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| opwwhole | stratum fed|1990s (population 2, sampled 2) | 2 | 1/2 | 0/2 |
| opwwhole | stratum fed|2020s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| opwwhole | stratum state|1860s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| opwwhole | stratum state|1920s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| opwwhole | stratum state|1980s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| opwwhole | stratum state|1990s (population 6, sampled 6) | 6 | 1/6 | 1/6 |
| opwwhole | stratum state|2000s (population 7, sampled 7) | 7 | 1/7 | 1/7 |
| opwwhole | stratum state|2010s (population 7, sampled 7) | 7 | 2/7 | 0/7 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (24 lines).
