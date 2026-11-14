# Blind audit score: r11b05 (type B)

- items in the key: 36 (32 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 36; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb11_r3 | 32 | 32 | 16/32 = 0.500 [0.336, 0.664] | 16/32 = 0.500 [0.336, 0.664] | 29/32 = 0.906 [0.758, 0.968] | 17/32 = 0.531 [0.364, 0.691] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb11_r3: right 0.500 [0.500, 0.500] (read in full); right + extent 0.500 [0.500, 0.500] (read in full)

Answers on sampled rows (every reader): scdb11_r3: affirmed 2, none 6, reversed 33, reversed_or_vacated_in_part 21, vacated 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb11_r3: kind 23, kind (same status effect) 2, link 6

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/8 = 1.000 [0.676, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10t03:stlink_T | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a12:ohv | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 36 | 17/32 = 0.531 [0.364, 0.691] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 36 | 16/32 = 0.500 [0.336, 0.664] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |

Items read twice: 36; same right answer 35/36 = 0.972 [0.858, 0.995]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb11_r3 | fed | 32 | 16/32 = 0.500 [0.336, 0.664] | 16/32 = 0.500 [0.336, 0.664] |
| scdb11_r3 | 1900s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb11_r3 | 1910s | 9 | 4/9 = 0.444 [0.189, 0.733] | 4/9 = 0.444 [0.189, 0.733] |
| scdb11_r3 | 1920s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| scdb11_r3 | 1930s | 4 | 2/4 = 0.500 [0.150, 0.850] | 2/4 = 0.500 [0.150, 0.850] |
| scdb11_r3 | 1940s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| scdb11_r3 | 1950s | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| scdb11_r3 | 1960s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| scdb11_r3 | 1970s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb11_r3 | 1980s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb11_r3 | 1990s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb11_r3 | reversed | 30 | 16/30 = 0.533 [0.361, 0.698] | 16/30 = 0.533 [0.361, 0.698] |
| scdb11_r3 | vacated | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| scdb11_r3 | stratum fed|1900s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| scdb11_r3 | stratum fed|1910s (population 9, sampled 9) | 9 | 4/9 | 4/9 |
| scdb11_r3 | stratum fed|1920s (population 6, sampled 6) | 6 | 4/6 | 4/6 |
| scdb11_r3 | stratum fed|1930s (population 4, sampled 4) | 4 | 2/4 | 2/4 |
| scdb11_r3 | stratum fed|1940s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| scdb11_r3 | stratum fed|1950s (population 2, sampled 2) | 2 | 0/2 | 0/2 |
| scdb11_r3 | stratum fed|1960s (population 4, sampled 4) | 4 | 3/4 | 3/4 |
| scdb11_r3 | stratum fed|1970s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| scdb11_r3 | stratum fed|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb11_r3 | stratum fed|1990s (population 1, sampled 1) | 1 | 0/1 | 0/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (31 lines).
