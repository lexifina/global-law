# Blind audit score: r7a13 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| b4a_r3 | 431 | 80 | 71/80 = 0.887 [0.800, 0.940] | 71/80 = 0.887 [0.800, 0.940] | 75/80 = 0.938 [0.862, 0.973] | 73/80 = 0.912 [0.830, 0.957] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- b4a_r3: right 0.892 [0.801, 0.945] (n_eff 73); right + extent 0.892 [0.801, 0.945] (n_eff 73)

Answers on sampled rows (every reader): b4a_r3: affirmed 1, modified 4, none 5, reversed 59, reversed_or_vacated_in_part 4, vacated 7

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): b4a_r3: kind 2, kind (same status effect) 2, link 5

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 9/10 = 0.900 [0.596, 0.982]
- known wrong, not confirmed: 5/6 = 0.833 [0.436, 0.970]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/5 = 0.800 [0.376, 0.964] | 2/3 = 0.667 [0.208, 0.939] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 5/5 = 1.000 [0.566, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:a3:rehear/docket | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/self | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:below/other | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/other | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/sc/sc_a1 | 0/1 = 0.000 [0.000, 0.793] |
| r6:v2:decoy_base | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 36/40 = 0.900 [0.769, 0.960] | 4/5 = 0.800 [0.376, 0.964] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 35/40 = 0.875 [0.739, 0.945] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| b4a_r3 | fed | 80 | 71/80 = 0.887 [0.800, 0.940] | 71/80 = 0.887 [0.800, 0.940] |
| b4a_r3 | 1880s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| b4a_r3 | 1890s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| b4a_r3 | 1900s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| b4a_r3 | 1910s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_r3 | 1920s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3 | 1930s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_r3 | 1940s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3 | 1950s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| b4a_r3 | 1960s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3 | 1970s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3 | 1980s | 6 | 3/6 = 0.500 [0.188, 0.812] | 3/6 = 0.500 [0.188, 0.812] |
| b4a_r3 | 1990s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3 | 2000s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| b4a_r3 | 2010s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_r3 | 2020s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3 | modified | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| b4a_r3 | reversed | 66 | 60/66 = 0.909 [0.816, 0.958] | 60/66 = 0.909 [0.816, 0.958] |
| b4a_r3 | vacated | 10 | 7/10 = 0.700 [0.397, 0.892] | 7/10 = 0.700 [0.397, 0.892] |
| b4a_r3 | stratum fed|1880s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| b4a_r3 | stratum fed|1890s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| b4a_r3 | stratum fed|1900s (population 20, sampled 5) | 5 | 4/5 | 4/5 |
| b4a_r3 | stratum fed|1910s (population 11, sampled 5) | 5 | 5/5 | 5/5 |
| b4a_r3 | stratum fed|1920s (population 16, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_r3 | stratum fed|1930s (population 51, sampled 5) | 5 | 5/5 | 5/5 |
| b4a_r3 | stratum fed|1940s (population 58, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_r3 | stratum fed|1950s (population 37, sampled 6) | 6 | 4/6 | 4/6 |
| b4a_r3 | stratum fed|1960s (population 38, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_r3 | stratum fed|1970s (population 51, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_r3 | stratum fed|1980s (population 52, sampled 6) | 6 | 3/6 | 3/6 |
| b4a_r3 | stratum fed|1990s (population 28, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_r3 | stratum fed|2000s (population 12, sampled 6) | 6 | 5/6 | 5/6 |
| b4a_r3 | stratum fed|2010s (population 27, sampled 5) | 5 | 5/5 | 5/5 |
| b4a_r3 | stratum fed|2020s (population 24, sampled 6) | 6 | 6/6 | 6/6 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (10 lines).
