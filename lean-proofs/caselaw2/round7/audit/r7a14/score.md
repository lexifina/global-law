# Blind audit score: r7a14 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| b4a_w | 297 | 80 | 73/80 = 0.912 [0.830, 0.957] | 73/80 = 0.912 [0.830, 0.957] | 76/80 = 0.950 [0.878, 0.980] | 73/80 = 0.912 [0.830, 0.957] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- b4a_w: right 0.902 [0.810, 0.952] (n_eff 70); right + extent 0.902 [0.810, 0.952] (n_eff 70)

Answers on sampled rows (every reader): b4a_w: affirmed 1, modified 2, none 4, other 1, reversed 61, reversed_or_vacated_in_part 1, vacated 10

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): b4a_w: kind 3, link 4

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
| r6:r1:rehear/enbanc-cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/sc/hm | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:memo/cap-2g | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 38/40 = 0.950 [0.835, 0.986] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 35/40 = 0.875 [0.739, 0.945] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| b4a_w | fed | 80 | 73/80 = 0.912 [0.830, 0.957] | 73/80 = 0.912 [0.830, 0.957] |
| b4a_w | 1880s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_w | 1890s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_w | 1900s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_w | 1910s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| b4a_w | 1920s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| b4a_w | 1930s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| b4a_w | 1940s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_w | 1950s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| b4a_w | 1960s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| b4a_w | 1970s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_w | 1980s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| b4a_w | 1990s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| b4a_w | 2000s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_w | 2010s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_w | 2020s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_w | modified | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| b4a_w | reversed | 67 | 61/67 = 0.910 [0.818, 0.958] | 61/67 = 0.910 [0.818, 0.958] |
| b4a_w | vacated | 11 | 10/11 = 0.909 [0.623, 0.984] | 10/11 = 0.909 [0.623, 0.984] |
| b4a_w | stratum fed|1880s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| b4a_w | stratum fed|1890s (population 12, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_w | stratum fed|1900s (population 14, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_w | stratum fed|1910s (population 19, sampled 6) | 6 | 5/6 | 5/6 |
| b4a_w | stratum fed|1920s (population 9, sampled 5) | 5 | 4/5 | 4/5 |
| b4a_w | stratum fed|1930s (population 23, sampled 5) | 5 | 4/5 | 4/5 |
| b4a_w | stratum fed|1940s (population 43, sampled 5) | 5 | 5/5 | 5/5 |
| b4a_w | stratum fed|1950s (population 32, sampled 5) | 5 | 4/5 | 4/5 |
| b4a_w | stratum fed|1960s (population 36, sampled 6) | 6 | 5/6 | 5/6 |
| b4a_w | stratum fed|1970s (population 41, sampled 5) | 5 | 5/5 | 5/5 |
| b4a_w | stratum fed|1980s (population 26, sampled 6) | 6 | 5/6 | 5/6 |
| b4a_w | stratum fed|1990s (population 14, sampled 5) | 5 | 4/5 | 4/5 |
| b4a_w | stratum fed|2000s (population 10, sampled 5) | 5 | 5/5 | 5/5 |
| b4a_w | stratum fed|2010s (population 6, sampled 5) | 5 | 5/5 | 5/5 |
| b4a_w | stratum fed|2020s (population 7, sampled 5) | 5 | 5/5 | 5/5 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (7 lines).
