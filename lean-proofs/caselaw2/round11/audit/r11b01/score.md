# Blind audit score: r11b01 (type B)

- items in the key: 46 (41 sampled rows, 3 known-wrong decoys, 2 known-right decoys); answered: 46; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb11_r1 | 42 | 41 | 40/41 = 0.976 [0.874, 0.996] | 40/41 = 0.976 [0.874, 0.996] | 41/41 = 1.000 [0.914, 1.000] | 41/41 = 1.000 [0.914, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb11_r1: right 0.974 [0.965, 0.981] (n_eff 1604); right + extent 0.974 [0.965, 0.981] (n_eff 1604)

Answers on sampled rows (every reader): scdb11_r1: affirmed 10, reversed 55, reversed_or_vacated_in_part 2, vacated 15

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb11_r1: kind (same status effect) 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 10/10 = 1.000 [0.723, 1.000]
- known wrong, not confirmed: 6/6 = 1.000 [0.610, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 10/10 = 1.000 [0.723, 1.000] | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10b02:scdb10_a10t | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k01:remandtext | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 46 | 40/41 = 0.976 [0.874, 0.996] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 46 | 41/41 = 1.000 [0.914, 1.000] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

Items read twice: 46; same right answer 45/46 = 0.978 [0.887, 0.996]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb11_r1 | fed | 41 | 40/41 = 0.976 [0.874, 0.996] | 40/41 = 0.976 [0.874, 0.996] |
| scdb11_r1 | 1960s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb11_r1 | 1970s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb11_r1 | 1980s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| scdb11_r1 | 1990s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| scdb11_r1 | 2000s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| scdb11_r1 | 2010s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| scdb11_r1 | 2020s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb11_r1 | affirmed | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| scdb11_r1 | reversed | 29 | 28/29 = 0.966 [0.828, 0.994] | 28/29 = 0.966 [0.828, 0.994] |
| scdb11_r1 | vacated | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| scdb11_r1 | stratum fed|1960s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb11_r1 | stratum fed|1970s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb11_r1 | stratum fed|1980s (population 11, sampled 10) | 10 | 9/10 | 9/10 |
| scdb11_r1 | stratum fed|1990s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| scdb11_r1 | stratum fed|2000s (population 11, sampled 11) | 11 | 11/11 | 11/11 |
| scdb11_r1 | stratum fed|2010s (population 9, sampled 9) | 9 | 9/9 | 9/9 |
| scdb11_r1 | stratum fed|2020s (population 3, sampled 3) | 3 | 3/3 | 3/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (1 lines).
