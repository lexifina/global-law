# Blind audit score: r7a08 (type A)

- items in the key: 64 (56 sampled rows, 4 known-wrong decoys, 4 known-right decoys); answered: 64; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| sc | 56 | 56 | 55/56 = 0.982 [0.905, 0.997] | 54/56 = 0.964 [0.879, 0.990] | 56/56 = 1.000 [0.936, 1.000] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- sc: right 0.982 [0.982, 0.982] (read in full); right + extent 0.964 [0.964, 0.964] (read in full)

Answers on sampled rows (every reader): sc: overrule 55, report_other 1

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): sc: act 1, extent 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 5/8 = 0.625 [0.306, 0.863]
- known wrong, not confirmed: 2/4 = 0.500 [0.150, 0.850]
- known right, confirmed: 3/4 = 0.750 [0.301, 0.954]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 2/4 = 0.500 [0.150, 0.850] | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| pack_2 | 3/4 = 0.750 [0.301, 0.954] | 1/2 = 0.500 [0.095, 0.905] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:control-self | 1/1 = 1.000 [0.206, 1.000] |
| r5:opw1:operative-part | 0/1 = 0.000 [0.000, 0.793] |
| r5:opw1:operative-whole | 1/2 = 0.500 [0.095, 0.905] |
| r5:recog1:control-self | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-read-part | 1/2 = 0.500 [0.095, 0.905] |
| r5:test_it0:recognised | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 32 | 27/28 = 0.964 [0.823, 0.994] | 2/4 = 0.500 [0.150, 0.850] | 0 | 0 |
| ans_2.jsonl | 2 | 32 | 28/28 = 1.000 [0.879, 1.000] | 3/4 = 0.750 [0.301, 0.954] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| sc | fed | 7 | 6/7 = 0.857 [0.487, 0.974] | 5/7 = 0.714 [0.359, 0.918] |
| sc | state | 49 | 49/49 = 1.000 [0.927, 1.000] | 49/49 = 1.000 [0.927, 1.000] |
| sc | 1920s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| sc | 1950s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| sc | 1960s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| sc | 1970s | 13 | 13/13 = 1.000 [0.772, 1.000] | 13/13 = 1.000 [0.772, 1.000] |
| sc | 1980s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| sc | 1990s | 11 | 10/11 = 0.909 [0.623, 0.984] | 10/11 = 0.909 [0.623, 0.984] |
| sc | 2000s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| sc | 2010s | 11 | 11/11 = 1.000 [0.741, 1.000] | 10/11 = 0.909 [0.623, 0.984] |
| sc | own_whole | 56 | 55/56 = 0.982 [0.905, 0.997] | 54/56 = 0.964 [0.879, 0.990] |
| sc | stratum fed|1970s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| sc | stratum fed|1990s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| sc | stratum fed|2010s (population 4, sampled 4) | 4 | 4/4 | 3/4 |
| sc | stratum state|1920s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| sc | stratum state|1950s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| sc | stratum state|1960s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| sc | stratum state|1970s (population 11, sampled 11) | 11 | 11/11 | 11/11 |
| sc | stratum state|1980s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| sc | stratum state|1990s (population 10, sampled 10) | 10 | 10/10 | 10/10 |
| sc | stratum state|2000s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| sc | stratum state|2010s (population 7, sampled 7) | 7 | 7/7 | 7/7 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (5 lines).
