# Blind audit score: r7a01 (type A)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| opwpart | 906 | 80 | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] | 80/80 = 1.000 [0.954, 1.000] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- opwpart: right 0.999 [0.848, 1.000] (n_eff 22); right + extent 0.999 [0.848, 1.000] (n_eff 22)

Answers on sampled rows (every reader): opwpart: limit 1, overrule 52, reject_doctrine 27

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): opwpart: act 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/10 = 0.800 [0.490, 0.943]
- known wrong, not confirmed: 4/6 = 0.667 [0.300, 0.903]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/5 = 0.800 [0.376, 0.964] | 2/3 = 0.667 [0.208, 0.939] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 4/5 = 0.800 [0.376, 0.964] | 2/3 = 0.667 [0.208, 0.939] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:operative-part | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:control-self | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-pattern | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-read-part | 0/1 = 0.000 [0.000, 0.793] |
| r5:recog1:recog-read-whole | 1/2 = 0.500 [0.095, 0.905] |
| r5:recog1:recog-round4 | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:decoy | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:recognised | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:selfAnnounced-control | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 39/40 = 0.975 [0.871, 0.996] | 4/5 = 0.800 [0.376, 0.964] | 0 | 1 |
| ans_2.jsonl | 2 | 45 | 40/40 = 1.000 [0.912, 1.000] | 4/5 = 0.800 [0.376, 0.964] | 0 | 1 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| opwpart | fed | 40 | 39/40 = 0.975 [0.871, 0.996] | 39/40 = 0.975 [0.871, 0.996] |
| opwpart | state | 40 | 40/40 = 1.000 [0.912, 1.000] | 40/40 = 1.000 [0.912, 1.000] |
| opwpart | 1840s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| opwpart | 1870s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| opwpart | 1880s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| opwpart | 1890s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| opwpart | 1900s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| opwpart | 1910s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| opwpart | 1920s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| opwpart | 1930s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| opwpart | 1940s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| opwpart | 1950s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| opwpart | 1960s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| opwpart | 1970s | 11 | 10/11 = 0.909 [0.623, 0.984] | 10/11 = 0.909 [0.623, 0.984] |
| opwpart | 1980s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| opwpart | 1990s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| opwpart | 2000s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| opwpart | 2010s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| opwpart | 2020s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| opwpart | own_part | 80 | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] |
| opwpart | stratum fed|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| opwpart | stratum fed|1950s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| opwpart | stratum fed|1960s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum fed|1970s (population 9, sampled 9) | 9 | 8/9 | 8/9 |
| opwpart | stratum fed|1980s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| opwpart | stratum fed|1990s (population 13, sampled 8) | 8 | 8/8 | 8/8 |
| opwpart | stratum fed|2000s (population 9, sampled 8) | 8 | 8/8 | 8/8 |
| opwpart | stratum fed|2010s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum fed|2020s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| opwpart | stratum state|1840s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| opwpart | stratum state|1870s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| opwpart | stratum state|1880s (population 5, sampled 2) | 2 | 2/2 | 2/2 |
| opwpart | stratum state|1890s (population 11, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum state|1900s (population 13, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum state|1910s (population 14, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum state|1920s (population 13, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum state|1930s (population 20, sampled 2) | 2 | 2/2 | 2/2 |
| opwpart | stratum state|1940s (population 34, sampled 2) | 2 | 2/2 | 2/2 |
| opwpart | stratum state|1950s (population 46, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum state|1960s (population 45, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum state|1970s (population 85, sampled 2) | 2 | 2/2 | 2/2 |
| opwpart | stratum state|1980s (population 178, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum state|1990s (population 161, sampled 3) | 3 | 3/3 | 3/3 |
| opwpart | stratum state|2000s (population 117, sampled 2) | 2 | 2/2 | 2/2 |
| opwpart | stratum state|2010s (population 114, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (3 lines).
