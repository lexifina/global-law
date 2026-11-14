# Blind audit score: r8b04 (type B)

- items in the key: 34 (30 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 34; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb8_rest | 30 | 30 | 29/30 = 0.967 [0.833, 0.994] | 29/30 = 0.967 [0.833, 0.994] | 29/30 = 0.967 [0.833, 0.994] | 29/30 = 0.967 [0.833, 0.994] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb8_rest: right 0.967 [0.967, 0.967] (read in full); right + extent 0.967 [0.967, 0.967] (read in full)

Answers on sampled rows (every reader): scdb8_rest: none 1, reversed 47, reversed_or_vacated_in_part 4, vacated 8

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb8_rest: link 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/8 = 1.000 [0.676, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 34 | 30/30 = 1.000 [0.886, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 0 | 1 |
| ans_1_b.jsonl | 1 | 34 | 29/30 = 0.967 [0.833, 0.994] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |

Items read twice: 34; same right answer 33/34 = 0.971 [0.851, 0.995]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb8_rest | fed | 30 | 29/30 = 0.967 [0.833, 0.994] | 29/30 = 0.967 [0.833, 0.994] |
| scdb8_rest | 1890s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_rest | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_rest | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_rest | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_rest | 1940s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb8_rest | 1950s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb8_rest | 1960s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_rest | 1970s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb8_rest | 1980s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| scdb8_rest | 1990s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| scdb8_rest | 2000s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb8_rest | 2010s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb8_rest | 2020s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb8_rest | reversed | 26 | 25/26 = 0.962 [0.811, 0.993] | 25/26 = 0.962 [0.811, 0.993] |
| scdb8_rest | vacated | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb8_rest | stratum fed|1890s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_rest | stratum fed|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_rest | stratum fed|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_rest | stratum fed|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_rest | stratum fed|1940s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb8_rest | stratum fed|1950s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb8_rest | stratum fed|1960s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_rest | stratum fed|1970s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scdb8_rest | stratum fed|1980s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| scdb8_rest | stratum fed|1990s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| scdb8_rest | stratum fed|2000s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb8_rest | stratum fed|2010s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scdb8_rest | stratum fed|2020s (population 2, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (1 lines).
