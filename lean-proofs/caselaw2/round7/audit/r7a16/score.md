# Blind audit score: r7a16 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| b4a_r3k | 253 | 80 | 76/80 = 0.950 [0.878, 0.980] | 76/80 = 0.950 [0.878, 0.980] | 77/80 = 0.963 [0.895, 0.987] | 76/80 = 0.950 [0.878, 0.980] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- b4a_r3k: right 0.960 [0.901, 0.985] (n_eff 97); right + extent 0.960 [0.901, 0.985] (n_eff 97)

Answers on sampled rows (every reader): b4a_r3k: none 3, reversed 70, reversed_or_vacated_in_part 3, vacated 4

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): b4a_r3k: kind 1, link 3

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
| r6:a3:below/sc/weak2 | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/enbanc-cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/panel-cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:memo/caption | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/other | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/sc/weak | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:memo/cap-2g | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 38/40 = 0.950 [0.835, 0.986] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 38/40 = 0.950 [0.835, 0.986] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| b4a_r3k | fed | 80 | 76/80 = 0.950 [0.878, 0.980] | 76/80 = 0.950 [0.878, 0.980] |
| b4a_r3k | 1900s | 7 | 5/7 = 0.714 [0.359, 0.918] | 5/7 = 0.714 [0.359, 0.918] |
| b4a_r3k | 1910s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| b4a_r3k | 1920s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_r3k | 1930s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3k | 1940s | 7 | 6/7 = 0.857 [0.487, 0.974] | 6/7 = 0.857 [0.487, 0.974] |
| b4a_r3k | 1950s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| b4a_r3k | 1960s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3k | 1970s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3k | 1980s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| b4a_r3k | 1990s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| b4a_r3k | 2000s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| b4a_r3k | 2010s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4a_r3k | 2020s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| b4a_r3k | modified | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| b4a_r3k | reversed | 74 | 71/74 = 0.960 [0.887, 0.986] | 71/74 = 0.960 [0.887, 0.986] |
| b4a_r3k | vacated | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| b4a_r3k | stratum fed|1900s (population 15, sampled 7) | 7 | 5/7 | 5/7 |
| b4a_r3k | stratum fed|1910s (population 9, sampled 6) | 6 | 5/6 | 5/6 |
| b4a_r3k | stratum fed|1920s (population 10, sampled 5) | 5 | 5/5 | 5/5 |
| b4a_r3k | stratum fed|1930s (population 19, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_r3k | stratum fed|1940s (population 22, sampled 7) | 7 | 6/7 | 6/7 |
| b4a_r3k | stratum fed|1950s (population 13, sampled 7) | 7 | 7/7 | 7/7 |
| b4a_r3k | stratum fed|1960s (population 20, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_r3k | stratum fed|1970s (population 31, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_r3k | stratum fed|1980s (population 39, sampled 7) | 7 | 7/7 | 7/7 |
| b4a_r3k | stratum fed|1990s (population 16, sampled 7) | 7 | 7/7 | 7/7 |
| b4a_r3k | stratum fed|2000s (population 8, sampled 3) | 3 | 3/3 | 3/3 |
| b4a_r3k | stratum fed|2010s (population 24, sampled 6) | 6 | 6/6 | 6/6 |
| b4a_r3k | stratum fed|2020s (population 23, sampled 7) | 7 | 7/7 | 7/7 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (4 lines).
