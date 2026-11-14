# Blind audit score: r11f02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc11_fu2 | 245 | 80 | 52/80 = 0.650 [0.541, 0.746] | 51/80 = 0.637 [0.528, 0.734] | 60/80 = 0.750 [0.645, 0.832] | 53/80 = 0.662 [0.554, 0.756] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc11_fu2: right 0.673 [0.564, 0.766] (n_eff 79); right + extent 0.668 [0.558, 0.762] (n_eff 79)

Answers on sampled rows (every reader): fjc11_fu2: affirmed 11, modified 2, none 37, reversed 61, reversed_or_vacated_in_part 29, vacated 20

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc11_fu2: kind 12, kind (same status effect) 3, link 37, scope 1

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
| r10:r10k02:capC2 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t03:stlink_T | 4/4 = 1.000 [0.510, 1.000] |
| r10:r10y01:syl10_RO_hist | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f04:fjc9J | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p02:PJH | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 20/27 = 0.741 [0.553, 0.868] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 19/27 = 0.704 [0.515, 0.842] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 18/27 = 0.667 [0.478, 0.814] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |
| ans_2_b.jsonl | 2 | 30 | 17/27 = 0.630 [0.442, 0.785] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |
| ans_3.jsonl | 3 | 29 | 17/26 = 0.654 [0.462, 0.806] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 17/26 = 0.654 [0.462, 0.806] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |

Items read twice: 89; same right answer 85/89 = 0.955 [0.890, 0.982]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc11_fu2 | fed | 80 | 52/80 = 0.650 [0.541, 0.746] | 51/80 = 0.637 [0.528, 0.734] |
| fjc11_fu2 | 1900s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc11_fu2 | 1940s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| fjc11_fu2 | 1950s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| fjc11_fu2 | 1960s | 7 | 3/7 = 0.429 [0.158, 0.750] | 3/7 = 0.429 [0.158, 0.750] |
| fjc11_fu2 | 1970s | 14 | 9/14 = 0.643 [0.388, 0.837] | 9/14 = 0.643 [0.388, 0.837] |
| fjc11_fu2 | 1980s | 14 | 9/14 = 0.643 [0.388, 0.837] | 8/14 = 0.571 [0.326, 0.786] |
| fjc11_fu2 | 1990s | 14 | 9/14 = 0.643 [0.388, 0.837] | 9/14 = 0.643 [0.388, 0.837] |
| fjc11_fu2 | 2000s | 13 | 8/13 = 0.615 [0.355, 0.823] | 8/13 = 0.615 [0.355, 0.823] |
| fjc11_fu2 | 2010s | 13 | 10/13 = 0.769 [0.497, 0.918] | 10/13 = 0.769 [0.497, 0.918] |
| fjc11_fu2 | modified | 3 | 1/3 = 0.333 [0.061, 0.792] | 1/3 = 0.333 [0.061, 0.792] |
| fjc11_fu2 | reversed | 57 | 37/57 = 0.649 [0.519, 0.760] | 36/57 = 0.632 [0.502, 0.745] |
| fjc11_fu2 | vacated | 20 | 14/20 = 0.700 [0.481, 0.855] | 14/20 = 0.700 [0.481, 0.855] |
| fjc11_fu2 | stratum fed|1900s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| fjc11_fu2 | stratum fed|1940s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| fjc11_fu2 | stratum fed|1950s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| fjc11_fu2 | stratum fed|1960s (population 7, sampled 7) | 7 | 3/7 | 3/7 |
| fjc11_fu2 | stratum fed|1970s (population 32, sampled 14) | 14 | 9/14 | 9/14 |
| fjc11_fu2 | stratum fed|1980s (population 18, sampled 14) | 14 | 9/14 | 8/14 |
| fjc11_fu2 | stratum fed|1990s (population 43, sampled 14) | 14 | 9/14 | 9/14 |
| fjc11_fu2 | stratum fed|2000s (population 62, sampled 13) | 13 | 8/13 | 8/13 |
| fjc11_fu2 | stratum fed|2010s (population 78, sampled 13) | 13 | 10/13 | 10/13 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (53 lines).
