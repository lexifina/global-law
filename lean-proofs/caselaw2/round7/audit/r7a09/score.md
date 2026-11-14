# Blind audit score: r7a09 (type A)

- items in the key: 45 (40 sampled rows, 3 known-wrong decoys, 2 known-right decoys); answered: 45; answer files: 1
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| scctl | 40 | 40 | 38/40 = 0.950 [0.835, 0.986] | 38/40 = 0.950 [0.835, 0.986] | 39/40 = 0.975 [0.871, 0.996] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scctl: right 0.950 [0.950, 0.950] (read in full); right + extent 0.950 [0.950, 0.950] (read in full)

Answers on sampled rows (every reader): scctl: nothing 1, overrule 38, report_other 1

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scctl: act 1, x+own+act 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/5 = 0.800 [0.376, 0.964]
- known wrong, not confirmed: 3/3 = 1.000 [0.439, 1.000]
- known right, confirmed: 1/2 = 0.500 [0.095, 0.905]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/5 = 0.800 [0.376, 0.964] | 3/3 = 1.000 [0.439, 1.000] | 1/2 = 0.500 [0.095, 0.905] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:operative-whole | 0/1 = 0.000 [0.000, 0.793] |
| r5:recog1:control-self | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-pattern | 1/1 = 1.000 [0.206, 1.000] |
| r5:recog1:recog-read-whole | 1/1 = 1.000 [0.206, 1.000] |
| r5:test_it0:decoy | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 38/40 = 0.950 [0.835, 0.986] | 4/5 = 0.800 [0.376, 0.964] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scctl | fed | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scctl | state | 38 | 36/38 = 0.947 [0.827, 0.985] | 36/38 = 0.947 [0.827, 0.985] |
| scctl | 1880s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scctl | 1890s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scctl | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scctl | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scctl | 1940s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scctl | 1950s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scctl | 1960s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scctl | 1970s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scctl | 1980s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scctl | 1990s | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| scctl | 2000s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| scctl | 2010s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scctl | own_part | 40 | 38/40 = 0.950 [0.835, 0.986] | 38/40 = 0.950 [0.835, 0.986] |
| scctl | stratum fed|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scctl | stratum fed|2000s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scctl | stratum state|1880s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scctl | stratum state|1890s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scctl | stratum state|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scctl | stratum state|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scctl | stratum state|1940s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scctl | stratum state|1950s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scctl | stratum state|1960s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scctl | stratum state|1970s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scctl | stratum state|1980s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| scctl | stratum state|1990s (population 9, sampled 9) | 9 | 7/9 | 7/9 |
| scctl | stratum state|2000s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| scctl | stratum state|2010s (population 4, sampled 4) | 4 | 4/4 | 4/4 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (3 lines).
