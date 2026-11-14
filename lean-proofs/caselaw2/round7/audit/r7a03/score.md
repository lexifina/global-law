# Blind audit score: r7a03 (type A)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| rcg | 317 | 80 | 80/80 = 1.000 [0.954, 1.000] | 80/80 = 1.000 [0.954, 1.000] | 80/80 = 1.000 [0.954, 1.000] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- rcg: right 1.000 [0.930, 1.000] (n_eff 51); right + extent 1.000 [0.930, 1.000] (n_eff 51)

Answers on sampled rows (every reader): rcg: report_other 80

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): rcg: none

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 10/10 = 1.000 [0.723, 1.000]
- known wrong, not confirmed: 6/6 = 1.000 [0.610, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 5/5 = 1.000 [0.566, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 5/5 = 1.000 [0.566, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:operative-whole | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:control-self | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-pattern | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-read-part | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-read-whole | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-round4 | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:decoy | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:selfAnnounced-control | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 40/40 = 1.000 [0.912, 1.000] | 5/5 = 1.000 [0.566, 1.000] | 1 | 0 |
| ans_2.jsonl | 2 | 45 | 40/40 = 1.000 [0.912, 1.000] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| rcg | fed | 17 | 17/17 = 1.000 [0.816, 1.000] | 17/17 = 1.000 [0.816, 1.000] |
| rcg | state | 63 | 63/63 = 1.000 [0.943, 1.000] | 63/63 = 1.000 [0.943, 1.000] |
| rcg | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rcg | 1950s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| rcg | 1960s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| rcg | 1970s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| rcg | 1980s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| rcg | 1990s | 14 | 14/14 = 1.000 [0.785, 1.000] | 14/14 = 1.000 [0.785, 1.000] |
| rcg | 2000s | 15 | 15/15 = 1.000 [0.796, 1.000] | 15/15 = 1.000 [0.796, 1.000] |
| rcg | 2010s | 18 | 18/18 = 1.000 [0.824, 1.000] | 18/18 = 1.000 [0.824, 1.000] |
| rcg | 2020s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rcg | report_part | 80 | 80/80 = 1.000 [0.954, 1.000] | 80/80 = 1.000 [0.954, 1.000] |
| rcg | stratum fed|1980s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| rcg | stratum fed|1990s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| rcg | stratum fed|2000s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| rcg | stratum fed|2010s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| rcg | stratum fed|2020s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rcg | stratum state|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rcg | stratum state|1950s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| rcg | stratum state|1960s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| rcg | stratum state|1970s (population 16, sampled 10) | 10 | 10/10 | 10/10 |
| rcg | stratum state|1980s (population 25, sampled 10) | 10 | 10/10 | 10/10 |
| rcg | stratum state|1990s (population 37, sampled 11) | 11 | 11/11 | 11/11 |
| rcg | stratum state|2000s (population 108, sampled 11) | 11 | 11/11 | 11/11 |
| rcg | stratum state|2010s (population 104, sampled 11) | 11 | 11/11 | 11/11 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (0 lines).
