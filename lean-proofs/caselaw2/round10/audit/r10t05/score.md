# Blind audit score: r10t05 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_u1 | 1343 | 80 | 59/80 = 0.738 [0.632, 0.821] | 59/80 = 0.738 [0.632, 0.821] | 59/80 = 0.738 [0.632, 0.821] | 59/80 = 0.738 [0.632, 0.821] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_u1: right 0.713 [0.561, 0.829] (n_eff 41); right + extent 0.713 [0.561, 0.829] (n_eff 41)

Answers on sampled rows (every reader): stlink_u1: modified 8, none 41, reversed 101, reversed_or_vacated_in_part 6, vacated 4

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_u1: link 41

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
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 4/4 = 1.000 [0.510, 1.000] |
| r9:r9p02:PJH | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 19/27 = 0.704 [0.515, 0.842] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 18/27 = 0.667 [0.478, 0.814] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 17/26 = 0.654 [0.462, 0.806] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 17/26 = 0.654 [0.462, 0.806] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_u1 | state | 80 | 59/80 = 0.738 [0.632, 0.821] | 59/80 = 0.738 [0.632, 0.821] |
| stlink_u1 | 1870s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u1 | 1880s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| stlink_u1 | 1890s | 6 | 3/6 = 0.500 [0.188, 0.812] | 3/6 = 0.500 [0.188, 0.812] |
| stlink_u1 | 1900s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| stlink_u1 | 1910s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| stlink_u1 | 1920s | 5 | 2/5 = 0.400 [0.118, 0.769] | 2/5 = 0.400 [0.118, 0.769] |
| stlink_u1 | 1930s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| stlink_u1 | 1940s | 5 | 2/5 = 0.400 [0.118, 0.769] | 2/5 = 0.400 [0.118, 0.769] |
| stlink_u1 | 1950s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| stlink_u1 | 1960s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| stlink_u1 | 1970s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| stlink_u1 | 1980s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| stlink_u1 | 1990s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| stlink_u1 | 2000s | 6 | 2/6 = 0.333 [0.097, 0.700] | 2/6 = 0.333 [0.097, 0.700] |
| stlink_u1 | 2010s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| stlink_u1 | modified | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| stlink_u1 | reversed | 71 | 53/71 = 0.747 [0.634, 0.833] | 53/71 = 0.747 [0.634, 0.833] |
| stlink_u1 | vacated | 4 | 2/4 = 0.500 [0.150, 0.850] | 2/4 = 0.500 [0.150, 0.850] |
| stlink_u1 | stratum state|1870s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u1 | stratum state|1880s (population 4, sampled 4) | 4 | 3/4 | 3/4 |
| stlink_u1 | stratum state|1890s (population 8, sampled 6) | 6 | 3/6 | 3/6 |
| stlink_u1 | stratum state|1900s (population 16, sampled 5) | 5 | 5/5 | 5/5 |
| stlink_u1 | stratum state|1910s (population 28, sampled 6) | 6 | 5/6 | 5/6 |
| stlink_u1 | stratum state|1920s (population 30, sampled 5) | 5 | 2/5 | 2/5 |
| stlink_u1 | stratum state|1930s (population 35, sampled 6) | 6 | 6/6 | 6/6 |
| stlink_u1 | stratum state|1940s (population 29, sampled 5) | 5 | 2/5 | 2/5 |
| stlink_u1 | stratum state|1950s (population 31, sampled 6) | 6 | 6/6 | 6/6 |
| stlink_u1 | stratum state|1960s (population 38, sampled 6) | 6 | 4/6 | 4/6 |
| stlink_u1 | stratum state|1970s (population 126, sampled 6) | 6 | 6/6 | 6/6 |
| stlink_u1 | stratum state|1980s (population 257, sampled 6) | 6 | 5/6 | 5/6 |
| stlink_u1 | stratum state|1990s (population 261, sampled 6) | 6 | 5/6 | 5/6 |
| stlink_u1 | stratum state|2000s (population 244, sampled 6) | 6 | 2/6 | 2/6 |
| stlink_u1 | stratum state|2010s (population 235, sampled 6) | 6 | 4/6 | 4/6 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (41 lines).
