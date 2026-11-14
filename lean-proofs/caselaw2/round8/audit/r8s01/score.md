# Blind audit score: r8s01 (type A)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| R8S | 132 | 80 | 77/80 = 0.963 [0.895, 0.987] | 76/80 = 0.950 [0.878, 0.980] | 80/80 = 1.000 [0.954, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- R8S: right 0.977 [0.934, 0.993] (n_eff 125); right + extent 0.970 [0.923, 0.988] (n_eff 125)

Answers on sampled rows (every reader): R8S: limit 3, overrule 151, reject_doctrine 6

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): R8S: act 3, extent 2, own 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 16/18 = 0.889 [0.672, 0.969]
- known wrong, not confirmed: 10/12 = 0.833 [0.552, 0.953]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 4/6 = 0.667 [0.300, 0.903] | 2/4 = 0.500 [0.150, 0.850] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:operative-part | 0/2 = 0.000 [0.000, 0.658] |
| r5:opw1:operative-whole | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-pattern | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-round4 | 2/2 = 1.000 [0.342, 1.000] |
| r5:test_it0:recognised | 2/2 = 1.000 [0.342, 1.000] |
| r5:test_it0:selfAnnounced-control | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a01:opwpart | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a04:ante | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a05:ante | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 0 |

Items read twice: 89; same right answer 87/89 = 0.978 [0.922, 0.994]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| R8S | fed | 15 | 15/15 = 1.000 [0.796, 1.000] | 14/15 = 0.933 [0.702, 0.988] |
| R8S | state | 65 | 62/65 = 0.954 [0.873, 0.984] | 62/65 = 0.954 [0.873, 0.984] |
| R8S | 1850s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| R8S | 1860s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| R8S | 1870s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| R8S | 1880s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| R8S | 1890s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| R8S | 1900s | 4 | 2/4 = 0.500 [0.150, 0.850] | 2/4 = 0.500 [0.150, 0.850] |
| R8S | 1910s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| R8S | 1920s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| R8S | 1930s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| R8S | 1940s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| R8S | 1950s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| R8S | 1960s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| R8S | 1970s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| R8S | 1980s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| R8S | 1990s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| R8S | 2000s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| R8S | 2010s | 10 | 10/10 = 1.000 [0.723, 1.000] | 9/10 = 0.900 [0.596, 0.982] |
| R8S | own_part | 66 | 64/66 = 0.970 [0.896, 0.992] | 64/66 = 0.970 [0.896, 0.992] |
| R8S | own_whole | 14 | 13/14 = 0.929 [0.685, 0.987] | 12/14 = 0.857 [0.601, 0.960] |
| R8S | stratum fed|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| R8S | stratum fed|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| R8S | stratum fed|1960s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| R8S | stratum fed|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| R8S | stratum fed|2000s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| R8S | stratum fed|2010s (population 4, sampled 4) | 4 | 4/4 | 3/4 |
| R8S | stratum state|1850s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| R8S | stratum state|1860s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| R8S | stratum state|1870s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| R8S | stratum state|1880s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| R8S | stratum state|1890s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| R8S | stratum state|1900s (population 4, sampled 4) | 4 | 2/4 | 2/4 |
| R8S | stratum state|1910s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| R8S | stratum state|1920s (population 8, sampled 5) | 5 | 5/5 | 5/5 |
| R8S | stratum state|1930s (population 6, sampled 5) | 5 | 5/5 | 5/5 |
| R8S | stratum state|1940s (population 9, sampled 5) | 5 | 5/5 | 5/5 |
| R8S | stratum state|1950s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| R8S | stratum state|1960s (population 14, sampled 5) | 5 | 5/5 | 5/5 |
| R8S | stratum state|1970s (population 11, sampled 5) | 5 | 5/5 | 5/5 |
| R8S | stratum state|1980s (population 18, sampled 5) | 5 | 5/5 | 5/5 |
| R8S | stratum state|1990s (population 15, sampled 5) | 5 | 5/5 | 5/5 |
| R8S | stratum state|2000s (population 10, sampled 5) | 5 | 5/5 | 5/5 |
| R8S | stratum state|2010s (population 7, sampled 6) | 6 | 6/6 | 6/6 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (8 lines).
