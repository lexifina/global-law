# Blind audit score: r8b03 (type B)

- items in the key: 38 (34 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 38; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb8_trial | 34 | 34 | 32/34 = 0.941 [0.809, 0.984] | 32/34 = 0.941 [0.809, 0.984] | 33/34 = 0.971 [0.851, 0.995] | 32/34 = 0.941 [0.809, 0.984] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb8_trial: right 0.941 [0.941, 0.941] (read in full); right + extent 0.941 [0.941, 0.941] (read in full)

Answers on sampled rows (every reader): scdb8_trial: modified 2, none 2, reversed 54, reversed_or_vacated_in_part 4, vacated 6

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb8_trial: kind 2, link 2

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
| r6:v1:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 38 | 32/34 = 0.941 [0.809, 0.984] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 38 | 32/34 = 0.941 [0.809, 0.984] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |

Items read twice: 38; same right answer 38/38 = 1.000 [0.908, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb8_trial | fed | 34 | 32/34 = 0.941 [0.809, 0.984] | 32/34 = 0.941 [0.809, 0.984] |
| scdb8_trial | 1890s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_trial | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_trial | 1920s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb8_trial | 1930s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| scdb8_trial | 1940s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| scdb8_trial | 1950s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb8_trial | 1960s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb8_trial | 1970s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| scdb8_trial | 1980s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb8_trial | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_trial | reversed | 30 | 28/30 = 0.933 [0.787, 0.982] | 28/30 = 0.933 [0.787, 0.982] |
| scdb8_trial | vacated | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb8_trial | stratum fed|1890s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_trial | stratum fed|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_trial | stratum fed|1920s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| scdb8_trial | stratum fed|1930s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| scdb8_trial | stratum fed|1940s (population 10, sampled 10) | 10 | 9/10 | 9/10 |
| scdb8_trial | stratum fed|1950s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scdb8_trial | stratum fed|1960s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scdb8_trial | stratum fed|1970s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| scdb8_trial | stratum fed|1980s (population 2, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (4 lines).
