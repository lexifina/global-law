# Blind audit score: r7a06 (type A)

- items in the key: 71 (63 sampled rows, 4 known-wrong decoys, 4 known-right decoys); answered: 71; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| ante | 63 | 63 | 54/63 = 0.857 [0.750, 0.923] | 54/63 = 0.857 [0.750, 0.923] | 62/63 = 0.984 [0.915, 0.997] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- ante: right 0.857 [0.857, 0.857] (read in full); right + extent 0.857 [0.857, 0.857] (read in full)

Answers on sampled rows (every reader): ante: limit 3, nothing 1, overrule 54, report_other 5

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): ante: act 8, x+own+act 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 7/8 = 0.875 [0.529, 0.978]
- known wrong, not confirmed: 3/4 = 0.750 [0.301, 0.954]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 3/4 = 0.750 [0.301, 0.954] | 1/2 = 0.500 [0.095, 0.905] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:control-self | 1/1 = 1.000 [0.206, 1.000] |
| r5:opw1:operative-part | 1/1 = 1.000 [0.206, 1.000] |
| r5:opw1:operative-whole | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-pattern | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-read-whole | 0/1 = 0.000 [0.000, 0.793] |
| r5:recog1:recog-round4 | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:decoy | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 36 | 27/32 = 0.844 [0.682, 0.931] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 35 | 27/31 = 0.871 [0.712, 0.949] | 3/4 = 0.750 [0.301, 0.954] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| ante | state | 63 | 54/63 = 0.857 [0.750, 0.923] | 54/63 = 0.857 [0.750, 0.923] |
| ante | 1850s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| ante | 1870s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| ante | 1890s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| ante | 1900s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| ante | 1910s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| ante | 1920s | 4 | 2/4 = 0.500 [0.150, 0.850] | 2/4 = 0.500 [0.150, 0.850] |
| ante | 1930s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| ante | 1940s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| ante | 1950s | 13 | 13/13 = 1.000 [0.772, 1.000] | 13/13 = 1.000 [0.772, 1.000] |
| ante | 1960s | 7 | 6/7 = 0.857 [0.487, 0.974] | 6/7 = 0.857 [0.487, 0.974] |
| ante | 1970s | 5 | 3/5 = 0.600 [0.231, 0.882] | 3/5 = 0.600 [0.231, 0.882] |
| ante | 1980s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| ante | 1990s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| ante | 2000s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| ante | own_part | 49 | 42/49 = 0.857 [0.733, 0.929] | 42/49 = 0.857 [0.733, 0.929] |
| ante | own_whole | 14 | 12/14 = 0.857 [0.601, 0.960] | 12/14 = 0.857 [0.601, 0.960] |
| ante | stratum state|1850s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| ante | stratum state|1870s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| ante | stratum state|1890s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| ante | stratum state|1900s (population 4, sampled 4) | 4 | 3/4 | 3/4 |
| ante | stratum state|1910s (population 4, sampled 4) | 4 | 3/4 | 3/4 |
| ante | stratum state|1920s (population 4, sampled 4) | 4 | 2/4 | 2/4 |
| ante | stratum state|1930s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| ante | stratum state|1940s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| ante | stratum state|1950s (population 13, sampled 13) | 13 | 13/13 | 13/13 |
| ante | stratum state|1960s (population 7, sampled 7) | 7 | 6/7 | 6/7 |
| ante | stratum state|1970s (population 5, sampled 5) | 5 | 3/5 | 3/5 |
| ante | stratum state|1980s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|1990s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|2000s (population 5, sampled 5) | 5 | 5/5 | 5/5 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (10 lines).
