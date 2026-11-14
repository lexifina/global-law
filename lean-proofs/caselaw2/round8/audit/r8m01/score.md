# Blind audit score: r8m01 (type A)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| multicase | 706 | 80 | 76/80 = 0.950 [0.878, 0.980] | 76/80 = 0.950 [0.878, 0.980] | 80/80 = 1.000 [0.954, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- multicase: right 0.943 [0.831, 0.983] (n_eff 43); right + extent 0.943 [0.831, 0.983] (n_eff 43)

Answers on sampled rows (every reader): multicase: overrule 137, reject_doctrine 19, report_other 4

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): multicase: act 6

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 16/18 = 0.889 [0.672, 0.969]
- known wrong, not confirmed: 10/12 = 0.833 [0.552, 0.953]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/6 = 0.667 [0.300, 0.903] | 2/4 = 0.500 [0.150, 0.850] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:recog1:recog-pattern | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-read-part | 0/2 = 0.000 [0.000, 0.658] |
| r5:recog1:recog-read-whole | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-round4 | 2/2 = 1.000 [0.342, 1.000] |
| r5:test_it0:recognised | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a01:opwpart | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a02:opwwhole | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a06:ante | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a11:dct | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 2/3 = 0.667 [0.208, 0.939] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 2/3 = 0.667 [0.208, 0.939] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 87/89 = 0.978 [0.922, 0.994]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| multicase | fed | 24 | 24/24 = 1.000 [0.862, 1.000] | 24/24 = 1.000 [0.862, 1.000] |
| multicase | state | 56 | 52/56 = 0.929 [0.830, 0.972] | 52/56 = 0.929 [0.830, 0.972] |
| multicase | 1860s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| multicase | 1870s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| multicase | 1880s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| multicase | 1890s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| multicase | 1900s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| multicase | 1910s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| multicase | 1920s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| multicase | 1930s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| multicase | 1940s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| multicase | 1950s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| multicase | 1960s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| multicase | 1970s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| multicase | 1980s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| multicase | 1990s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| multicase | 2000s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| multicase | 2010s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| multicase | own_part | 73 | 72/73 = 0.986 [0.926, 0.998] | 72/73 = 0.986 [0.926, 0.998] |
| multicase | own_whole | 7 | 4/7 = 0.571 [0.251, 0.842] | 4/7 = 0.571 [0.251, 0.842] |
| multicase | stratum fed|1930s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| multicase | stratum fed|1940s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| multicase | stratum fed|1960s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum fed|1970s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum fed|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| multicase | stratum fed|1990s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| multicase | stratum fed|2000s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum fed|2010s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum state|1860s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| multicase | stratum state|1870s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| multicase | stratum state|1880s (population 5, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum state|1890s (population 17, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum state|1900s (population 15, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum state|1910s (population 27, sampled 3) | 3 | 3/3 | 3/3 |
| multicase | stratum state|1920s (population 13, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum state|1930s (population 31, sampled 4) | 4 | 3/4 | 3/4 |
| multicase | stratum state|1940s (population 48, sampled 3) | 3 | 3/3 | 3/3 |
| multicase | stratum state|1950s (population 69, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum state|1960s (population 51, sampled 4) | 4 | 3/4 | 3/4 |
| multicase | stratum state|1970s (population 69, sampled 3) | 3 | 3/3 | 3/3 |
| multicase | stratum state|1980s (population 74, sampled 4) | 4 | 3/4 | 3/4 |
| multicase | stratum state|1990s (population 84, sampled 4) | 4 | 4/4 | 4/4 |
| multicase | stratum state|2000s (population 76, sampled 3) | 3 | 3/3 | 3/3 |
| multicase | stratum state|2010s (population 99, sampled 4) | 4 | 4/4 | 4/4 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (8 lines).
