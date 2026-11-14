# Blind audit score: r7a04 (type A)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| ante | 489 | 80 | 79/80 = 0.988 [0.932, 0.998] | 76/80 = 0.950 [0.878, 0.980] | 80/80 = 1.000 [0.954, 1.000] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- ante: right 0.998 [0.914, 1.000] (n_eff 43); right + extent 0.903 [0.779, 0.961] (n_eff 43)

Answers on sampled rows (every reader): ante: limit 1, overrule 72, reject_doctrine 7

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): ante: act 1, extent 3

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
| r5:opw1:operative-part | 3/3 = 1.000 [0.439, 1.000] |
| r5:opw1:operative-whole | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-read-part | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-read-whole | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:decoy | 2/2 = 1.000 [0.342, 1.000] |
| r5:test_it0:recognised | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 40/40 = 1.000 [0.912, 1.000] | 5/5 = 1.000 [0.566, 1.000] | 0 | 1 |
| ans_2.jsonl | 2 | 45 | 39/40 = 0.975 [0.871, 0.996] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| ante | fed | 18 | 18/18 = 1.000 [0.824, 1.000] | 18/18 = 1.000 [0.824, 1.000] |
| ante | state | 62 | 61/62 = 0.984 [0.914, 0.997] | 58/62 = 0.935 [0.846, 0.975] |
| ante | 1860s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| ante | 1870s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| ante | 1880s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| ante | 1890s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| ante | 1900s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| ante | 1910s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| ante | 1920s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| ante | 1930s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| ante | 1940s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| ante | 1950s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| ante | 1960s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| ante | 1970s | 7 | 7/7 = 1.000 [0.646, 1.000] | 5/7 = 0.714 [0.359, 0.918] |
| ante | 1980s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| ante | 1990s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| ante | 2000s | 7 | 7/7 = 1.000 [0.646, 1.000] | 6/7 = 0.857 [0.487, 0.974] |
| ante | 2010s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| ante | own_part | 66 | 65/66 = 0.985 [0.919, 0.997] | 65/66 = 0.985 [0.919, 0.997] |
| ante | own_whole | 14 | 14/14 = 1.000 [0.785, 1.000] | 11/14 = 0.786 [0.524, 0.924] |
| ante | stratum fed|1930s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum fed|1940s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum fed|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| ante | stratum fed|1970s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum fed|1980s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum fed|1990s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| ante | stratum fed|2000s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum fed|2010s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum state|1860s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum state|1870s (population 4, sampled 4) | 4 | 3/4 | 3/4 |
| ante | stratum state|1880s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| ante | stratum state|1890s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| ante | stratum state|1900s (population 12, sampled 4) | 4 | 4/4 | 4/4 |
| ante | stratum state|1910s (population 13, sampled 4) | 4 | 4/4 | 4/4 |
| ante | stratum state|1920s (population 14, sampled 5) | 5 | 5/5 | 5/5 |
| ante | stratum state|1930s (population 16, sampled 4) | 4 | 4/4 | 4/4 |
| ante | stratum state|1940s (population 26, sampled 5) | 5 | 5/5 | 5/5 |
| ante | stratum state|1950s (population 46, sampled 4) | 4 | 4/4 | 4/4 |
| ante | stratum state|1960s (population 52, sampled 4) | 4 | 4/4 | 4/4 |
| ante | stratum state|1970s (population 76, sampled 4) | 4 | 4/4 | 2/4 |
| ante | stratum state|1980s (population 27, sampled 5) | 5 | 5/5 | 5/5 |
| ante | stratum state|1990s (population 79, sampled 4) | 4 | 4/4 | 4/4 |
| ante | stratum state|2000s (population 34, sampled 4) | 4 | 4/4 | 3/4 |
| ante | stratum state|2010s (population 65, sampled 4) | 4 | 4/4 | 4/4 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (4 lines).
