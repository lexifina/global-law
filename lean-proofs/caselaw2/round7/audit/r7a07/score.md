# Blind audit score: r7a07 (type A)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| ante | 179 | 80 | 36/80 = 0.450 [0.346, 0.559] | 35/80 = 0.438 [0.334, 0.547] | 80/80 = 1.000 [0.954, 1.000] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- ante: right 0.569 [0.451, 0.679] (n_eff 69); right + extent 0.550 [0.433, 0.661] (n_eff 69)

Answers on sampled rows (every reader): ante: limit 1, other 20, overrule 32, reject_doctrine 4, report_other 23

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): ante: act 44, extent 1

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
| r5:opw1:operative-part | 2/2 = 1.000 [0.342, 1.000] |
| r5:opw1:operative-whole | 3/3 = 1.000 [0.439, 1.000] |
| r5:recog1:recog-read-whole | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-round4 | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:decoy | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:recognised | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:selfAnnounced-control | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 14/40 = 0.350 [0.221, 0.505] | 5/5 = 1.000 [0.566, 1.000] | 0 | 1 |
| ans_2.jsonl | 2 | 45 | 22/40 = 0.550 [0.398, 0.693] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| ante | fed | 27 | 8/27 = 0.296 [0.159, 0.485] | 8/27 = 0.296 [0.159, 0.485] |
| ante | state | 53 | 28/53 = 0.528 [0.397, 0.656] | 27/53 = 0.509 [0.379, 0.639] |
| ante | 1890s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| ante | 1900s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| ante | 1910s | 4 | 2/4 = 0.500 [0.150, 0.850] | 2/4 = 0.500 [0.150, 0.850] |
| ante | 1920s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| ante | 1930s | 5 | 1/5 = 0.200 [0.036, 0.625] | 1/5 = 0.200 [0.036, 0.625] |
| ante | 1940s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| ante | 1950s | 9 | 3/9 = 0.333 [0.121, 0.646] | 3/9 = 0.333 [0.121, 0.646] |
| ante | 1960s | 5 | 1/5 = 0.200 [0.036, 0.625] | 1/5 = 0.200 [0.036, 0.625] |
| ante | 1970s | 7 | 3/7 = 0.429 [0.158, 0.750] | 3/7 = 0.429 [0.158, 0.750] |
| ante | 1980s | 12 | 6/12 = 0.500 [0.254, 0.746] | 5/12 = 0.417 [0.193, 0.680] |
| ante | 1990s | 7 | 3/7 = 0.429 [0.158, 0.750] | 3/7 = 0.429 [0.158, 0.750] |
| ante | 2000s | 10 | 6/10 = 0.600 [0.313, 0.832] | 6/10 = 0.600 [0.313, 0.832] |
| ante | 2010s | 10 | 4/10 = 0.400 [0.168, 0.687] | 4/10 = 0.400 [0.168, 0.687] |
| ante | 2020s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| ante | own_part | 44 | 25/44 = 0.568 [0.422, 0.703] | 25/44 = 0.568 [0.422, 0.703] |
| ante | own_whole | 36 | 11/36 = 0.306 [0.180, 0.469] | 10/36 = 0.278 [0.159, 0.440] |
| ante | stratum fed|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| ante | stratum fed|1950s (population 4, sampled 4) | 4 | 1/4 | 1/4 |
| ante | stratum fed|1970s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum fed|1980s (population 7, sampled 7) | 7 | 2/7 | 2/7 |
| ante | stratum fed|1990s (population 2, sampled 2) | 2 | 0/2 | 0/2 |
| ante | stratum fed|2000s (population 5, sampled 5) | 5 | 2/5 | 2/5 |
| ante | stratum fed|2010s (population 5, sampled 5) | 5 | 0/5 | 0/5 |
| ante | stratum fed|2020s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| ante | stratum state|1890s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| ante | stratum state|1900s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| ante | stratum state|1910s (population 6, sampled 4) | 4 | 2/4 | 2/4 |
| ante | stratum state|1920s (population 7, sampled 5) | 5 | 4/5 | 4/5 |
| ante | stratum state|1930s (population 6, sampled 5) | 5 | 1/5 | 1/5 |
| ante | stratum state|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| ante | stratum state|1950s (population 5, sampled 5) | 5 | 2/5 | 2/5 |
| ante | stratum state|1960s (population 12, sampled 5) | 5 | 1/5 | 1/5 |
| ante | stratum state|1970s (population 13, sampled 5) | 5 | 1/5 | 1/5 |
| ante | stratum state|1980s (population 17, sampled 5) | 5 | 4/5 | 3/5 |
| ante | stratum state|1990s (population 21, sampled 5) | 5 | 3/5 | 3/5 |
| ante | stratum state|2000s (population 29, sampled 5) | 5 | 4/5 | 4/5 |
| ante | stratum state|2010s (population 32, sampled 5) | 5 | 4/5 | 4/5 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (45 lines).
