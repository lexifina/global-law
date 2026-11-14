# Blind audit score: r8o02 (type A)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| o2 | 591 | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | 80/80 = 1.000 [0.954, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- o2: right 0.975 [0.884, 0.995] (n_eff 48); right + extent 0.975 [0.884, 0.995] (n_eff 48)

Answers on sampled rows (every reader): o2: nothing 2, other 2, overrule 74, reject_doctrine 80, report_other 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): o2: act 3, own+act 3

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 16/18 = 0.889 [0.672, 0.969]
- known wrong, not confirmed: 10/12 = 0.833 [0.552, 0.953]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 5/6 = 0.833 [0.436, 0.970] | 3/4 = 0.750 [0.301, 0.954] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 5/6 = 0.833 [0.436, 0.970] | 3/4 = 0.750 [0.301, 0.954] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:operative-whole | 1/2 = 0.500 [0.095, 0.905] |
| r5:recog1:recog-read-whole | 4/4 = 1.000 [0.510, 1.000] |
| r5:recog1:recog-round4 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a01:opwpart | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a04:ante | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a06:ante | 3/4 = 0.750 [0.301, 0.954] |
| r7:r7a07:ante | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 25/27 = 0.926 [0.766, 0.979] | 2/3 = 0.667 [0.208, 0.939] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 87/89 = 0.978 [0.922, 0.994]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| o2 | fed | 40 | 38/40 = 0.950 [0.835, 0.986] | 38/40 = 0.950 [0.835, 0.986] |
| o2 | state | 40 | 39/40 = 0.975 [0.871, 0.996] | 39/40 = 0.975 [0.871, 0.996] |
| o2 | 1900s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| o2 | 1910s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| o2 | 1940s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| o2 | 1950s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| o2 | 1960s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| o2 | 1970s | 12 | 10/12 = 0.833 [0.552, 0.953] | 10/12 = 0.833 [0.552, 0.953] |
| o2 | 1980s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| o2 | 1990s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| o2 | 2000s | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| o2 | 2010s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| o2 | own_part | 77 | 74/77 = 0.961 [0.892, 0.987] | 74/77 = 0.961 [0.892, 0.987] |
| o2 | own_whole | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| o2 | stratum fed|1950s (population 7, sampled 3) | 3 | 3/3 | 3/3 |
| o2 | stratum fed|1960s (population 7, sampled 2) | 2 | 2/2 | 2/2 |
| o2 | stratum fed|1970s (population 32, sampled 7) | 7 | 6/7 | 6/7 |
| o2 | stratum fed|1980s (population 35, sampled 7) | 7 | 7/7 | 7/7 |
| o2 | stratum fed|1990s (population 48, sampled 7) | 7 | 7/7 | 7/7 |
| o2 | stratum fed|2000s (population 33, sampled 8) | 8 | 7/8 | 7/8 |
| o2 | stratum fed|2010s (population 10, sampled 6) | 6 | 6/6 | 6/6 |
| o2 | stratum state|1900s (population 7, sampled 4) | 4 | 4/4 | 4/4 |
| o2 | stratum state|1910s (population 9, sampled 4) | 4 | 4/4 | 4/4 |
| o2 | stratum state|1940s (population 6, sampled 3) | 3 | 3/3 | 3/3 |
| o2 | stratum state|1960s (population 11, sampled 5) | 5 | 5/5 | 5/5 |
| o2 | stratum state|1970s (population 32, sampled 5) | 5 | 4/5 | 4/5 |
| o2 | stratum state|1980s (population 63, sampled 5) | 5 | 5/5 | 5/5 |
| o2 | stratum state|1990s (population 104, sampled 4) | 4 | 4/4 | 4/4 |
| o2 | stratum state|2000s (population 107, sampled 5) | 5 | 5/5 | 5/5 |
| o2 | stratum state|2010s (population 63, sampled 5) | 5 | 5/5 | 5/5 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (8 lines).
