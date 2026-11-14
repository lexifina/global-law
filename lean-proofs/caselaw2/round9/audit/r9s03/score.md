# Blind audit score: r9s03 (type A)

- items in the key: 80 (72 sampled rows, 4 known-wrong decoys, 4 known-right decoys); answered: 80; answer files: 4
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| S9A2 | 72 | 72 | 44/72 = 0.611 [0.496, 0.715] | 44/72 = 0.611 [0.496, 0.715] | 72/72 = 1.000 [0.949, 1.000] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- S9A2: right 0.611 [0.611, 0.611] (read in full); right + extent 0.611 [0.611, 0.611] (read in full)

Answers on sampled rows (every reader): S9A2: limit 109, overrule 5, reject_doctrine 30

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): S9A2: act 35

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 12/16 = 0.750 [0.505, 0.898]
- known wrong, not confirmed: 4/8 = 0.500 [0.215, 0.785]
- known right, confirmed: 8/8 = 1.000 [0.676, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/8 = 0.750 [0.409, 0.928] | 2/4 = 0.500 [0.150, 0.850] | 4/4 = 1.000 [0.510, 1.000] |
| pack_2 | 6/8 = 0.750 [0.409, 0.928] | 2/4 = 0.500 [0.150, 0.850] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:recog1:recog-round4 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a01:opwpart | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a02:opwwhole | 2/4 = 0.500 [0.150, 0.850] |
| r7:r7a04:ante | 2/4 = 0.500 [0.150, 0.850] |
| r7:r7a07:ante | 4/4 = 1.000 [0.510, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 40 | 15/36 = 0.417 [0.271, 0.578] | 3/4 = 0.750 [0.301, 0.954] | 0 | 2 |
| ans_1_b.jsonl | 1 | 40 | 31/36 = 0.861 [0.713, 0.939] | 3/4 = 0.750 [0.301, 0.954] | 0 | 2 |
| ans_2.jsonl | 2 | 40 | 31/36 = 0.861 [0.713, 0.939] | 3/4 = 0.750 [0.301, 0.954] | 0 | 0 |
| ans_2_b.jsonl | 2 | 40 | 32/36 = 0.889 [0.747, 0.956] | 3/4 = 0.750 [0.301, 0.954] | 0 | 0 |

Items read twice: 80; same right answer 59/80 = 0.738 [0.632, 0.821]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| S9A2 | fed | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| S9A2 | state | 63 | 35/63 = 0.556 [0.433, 0.671] | 35/63 = 0.556 [0.433, 0.671] |
| S9A2 | 1880s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| S9A2 | 1910s | 3 | 1/3 = 0.333 [0.061, 0.792] | 1/3 = 0.333 [0.061, 0.792] |
| S9A2 | 1920s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| S9A2 | 1930s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| S9A2 | 1940s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| S9A2 | 1960s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| S9A2 | 1970s | 8 | 5/8 = 0.625 [0.306, 0.863] | 5/8 = 0.625 [0.306, 0.863] |
| S9A2 | 1980s | 21 | 16/21 = 0.762 [0.549, 0.894] | 16/21 = 0.762 [0.549, 0.894] |
| S9A2 | 1990s | 18 | 9/18 = 0.500 [0.290, 0.710] | 9/18 = 0.500 [0.290, 0.710] |
| S9A2 | 2000s | 11 | 7/11 = 0.636 [0.354, 0.848] | 7/11 = 0.636 [0.354, 0.848] |
| S9A2 | 2010s | 4 | 2/4 = 0.500 [0.150, 0.850] | 2/4 = 0.500 [0.150, 0.850] |
| S9A2 | limit | 72 | 44/72 = 0.611 [0.496, 0.715] | 44/72 = 0.611 [0.496, 0.715] |
| S9A2 | stratum fed|1960s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9A2 | stratum fed|1970s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9A2 | stratum fed|1980s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| S9A2 | stratum fed|1990s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| S9A2 | stratum fed|2000s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| S9A2 | stratum state|1880s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| S9A2 | stratum state|1910s (population 3, sampled 3) | 3 | 1/3 | 1/3 |
| S9A2 | stratum state|1920s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| S9A2 | stratum state|1930s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| S9A2 | stratum state|1940s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| S9A2 | stratum state|1970s (population 7, sampled 7) | 7 | 4/7 | 4/7 |
| S9A2 | stratum state|1980s (population 19, sampled 19) | 19 | 14/19 | 14/19 |
| S9A2 | stratum state|1990s (population 16, sampled 16) | 16 | 7/16 | 7/16 |
| S9A2 | stratum state|2000s (population 8, sampled 8) | 8 | 4/8 | 4/8 |
| S9A2 | stratum state|2010s (population 4, sampled 4) | 4 | 2/4 | 2/4 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (39 lines).
