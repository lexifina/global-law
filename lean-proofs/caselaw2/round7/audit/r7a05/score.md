# Blind audit score: r7a05 (type A)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| ante | 574 | 80 | 78/80 = 0.975 [0.913, 0.993] | 77/80 = 0.963 [0.895, 0.987] | 80/80 = 1.000 [0.954, 1.000] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- ante: right 0.953 [0.821, 0.989] (n_eff 32); right + extent 0.952 [0.819, 0.988] (n_eff 32)

Answers on sampled rows (every reader): ante: overrule 78, report_other 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): ante: act 2, extent 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/10 = 0.800 [0.490, 0.943]
- known wrong, not confirmed: 4/6 = 0.667 [0.300, 0.903]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 3/5 = 0.600 [0.231, 0.882] | 1/3 = 0.333 [0.061, 0.792] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 5/5 = 1.000 [0.566, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:operative-part | 1/1 = 1.000 [0.206, 1.000] |
| r5:opw1:operative-whole | 2/3 = 0.667 [0.208, 0.939] |
| r5:recog1:control-self | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-read-whole | 1/2 = 0.500 [0.095, 0.905] |
| r5:test_it0:decoy | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:recognised | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:selfAnnounced-control | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 39/40 = 0.975 [0.871, 0.996] | 3/5 = 0.600 [0.231, 0.882] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 39/40 = 0.975 [0.871, 0.996] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| ante | fed | 40 | 40/40 = 1.000 [0.912, 1.000] | 39/40 = 0.975 [0.871, 0.996] |
| ante | state | 40 | 38/40 = 0.950 [0.835, 0.986] | 38/40 = 0.950 [0.835, 0.986] |
| ante | 1870s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| ante | 1880s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| ante | 1890s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| ante | 1900s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| ante | 1910s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| ante | 1920s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| ante | 1930s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| ante | 1940s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| ante | 1950s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| ante | 1960s | 7 | 7/7 = 1.000 [0.646, 1.000] | 6/7 = 0.857 [0.487, 0.974] |
| ante | 1970s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| ante | 1980s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| ante | 1990s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| ante | 2000s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| ante | 2010s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| ante | 2020s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| ante | own_part | 68 | 67/68 = 0.985 [0.921, 0.997] | 67/68 = 0.985 [0.921, 0.997] |
| ante | own_whole | 12 | 11/12 = 0.917 [0.646, 0.985] | 10/12 = 0.833 [0.552, 0.953] |
| ante | stratum fed|1930s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum fed|1940s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum fed|1950s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum fed|1960s (population 4, sampled 4) | 4 | 4/4 | 3/4 |
| ante | stratum fed|1970s (population 8, sampled 5) | 5 | 5/5 | 5/5 |
| ante | stratum fed|1980s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| ante | stratum fed|1990s (population 9, sampled 6) | 6 | 6/6 | 6/6 |
| ante | stratum fed|2000s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum fed|2010s (population 7, sampled 5) | 5 | 5/5 | 5/5 |
| ante | stratum fed|2020s (population 8, sampled 5) | 5 | 5/5 | 5/5 |
| ante | stratum state|1870s (population 4, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum state|1880s (population 7, sampled 2) | 2 | 1/2 | 1/2 |
| ante | stratum state|1890s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|1900s (population 9, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|1910s (population 23, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum state|1920s (population 31, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|1930s (population 18, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum state|1940s (population 35, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|1950s (population 18, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|1960s (population 19, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|1970s (population 64, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum state|1980s (population 67, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|1990s (population 87, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|2000s (population 70, sampled 3) | 3 | 2/3 | 2/3 |
| ante | stratum state|2010s (population 68, sampled 3) | 3 | 3/3 | 3/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (5 lines).
