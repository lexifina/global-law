# Blind audit score: r9f01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc9G | 218 | 80 | 65/80 = 0.812 [0.713, 0.883] | 65/80 = 0.812 [0.713, 0.883] | 76/80 = 0.950 [0.878, 0.980] | 67/80 = 0.838 [0.742, 0.902] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc9G: right 0.809 [0.714, 0.878] (n_eff 87); right + extent 0.809 [0.714, 0.878] (n_eff 87)

Answers on sampled rows (every reader): fjc9G: modified 2, none 8, reinstated 4, reversed 84, reversed_or_vacated_in_part 36, vacated 26

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc9G: kind 17, kind (same status effect) 4, link 8

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 18/18 = 1.000 [0.824, 1.000]
- known wrong, not confirmed: 12/12 = 1.000 [0.757, 1.000]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 4/4 = 1.000 [0.510, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_1_b.jsonl | 1 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 19/26 = 0.731 [0.539, 0.863] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 18/26 = 0.692 [0.500, 0.835] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc9G | fed | 80 | 65/80 = 0.812 [0.713, 0.883] | 65/80 = 0.812 [0.713, 0.883] |
| fjc9G | 1930s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| fjc9G | 1940s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| fjc9G | 1950s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| fjc9G | 1960s | 11 | 9/11 = 0.818 [0.523, 0.949] | 9/11 = 0.818 [0.523, 0.949] |
| fjc9G | 1970s | 10 | 5/10 = 0.500 [0.237, 0.763] | 5/10 = 0.500 [0.237, 0.763] |
| fjc9G | 1980s | 11 | 10/11 = 0.909 [0.623, 0.984] | 10/11 = 0.909 [0.623, 0.984] |
| fjc9G | 1990s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| fjc9G | 2000s | 10 | 6/10 = 0.600 [0.313, 0.832] | 6/10 = 0.600 [0.313, 0.832] |
| fjc9G | 2010s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| fjc9G | 2020s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc9G | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc9G | reversed | 64 | 50/64 = 0.781 [0.666, 0.865] | 50/64 = 0.781 [0.666, 0.865] |
| fjc9G | vacated | 15 | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] |
| fjc9G | stratum fed|1930s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| fjc9G | stratum fed|1940s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| fjc9G | stratum fed|1950s (population 14, sampled 10) | 10 | 9/10 | 9/10 |
| fjc9G | stratum fed|1960s (population 18, sampled 11) | 11 | 9/11 | 9/11 |
| fjc9G | stratum fed|1970s (population 40, sampled 10) | 10 | 5/10 | 5/10 |
| fjc9G | stratum fed|1980s (population 60, sampled 11) | 11 | 10/11 | 10/11 |
| fjc9G | stratum fed|1990s (population 36, sampled 10) | 10 | 10/10 | 10/10 |
| fjc9G | stratum fed|2000s (population 21, sampled 10) | 10 | 6/10 | 6/10 |
| fjc9G | stratum fed|2010s (population 21, sampled 10) | 10 | 9/10 | 9/10 |
| fjc9G | stratum fed|2020s (population 1, sampled 1) | 1 | 1/1 | 1/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (29 lines).
