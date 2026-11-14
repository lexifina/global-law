# Blind audit score: r10b02 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 4
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb10_a10t | 86 | 80 | 70/80 = 0.875 [0.785, 0.931] | 70/80 = 0.875 [0.785, 0.931] | 75/80 = 0.938 [0.862, 0.973] | 71/80 = 0.887 [0.800, 0.940] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb10_a10t: right 0.877 [0.854, 0.896] (n_eff 925); right + extent 0.877 [0.854, 0.896] (n_eff 925)

Answers on sampled rows (every reader): scdb10_a10t: affirmed 48, modified 2, none 10, other 1, reversed 84, reversed_or_vacated_in_part 6, review_dismissed 1, vacated 8

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb10_a10t: kind 7, kind (same status effect) 2, link 10

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 19/20 = 0.950 [0.764, 0.991]
- known wrong, not confirmed: 11/12 = 0.917 [0.646, 0.985]
- known right, confirmed: 8/8 = 1.000 [0.676, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 10/10 = 1.000 [0.723, 1.000] | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| pack_2 | 9/10 = 0.900 [0.596, 0.982] | 5/6 = 0.833 [0.436, 0.970] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:rehear/panel-cite | 4/4 = 1.000 [0.510, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a15:b4e_rp | 1/2 = 0.500 [0.095, 0.905] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 35/40 = 0.875 [0.739, 0.945] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 45 | 35/40 = 0.875 [0.739, 0.945] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 36/40 = 0.900 [0.769, 0.960] | 4/5 = 0.800 [0.376, 0.964] | 0 | 1 |
| ans_2_b.jsonl | 2 | 45 | 35/40 = 0.875 [0.739, 0.945] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

Items read twice: 90; same right answer 88/90 = 0.978 [0.923, 0.994]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb10_a10t | fed | 80 | 70/80 = 0.875 [0.785, 0.931] | 70/80 = 0.875 [0.785, 0.931] |
| scdb10_a10t | 1880s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb10_a10t | 1890s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb10_a10t | 1900s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb10_a10t | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb10_a10t | 1920s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb10_a10t | 1930s | 14 | 11/14 = 0.786 [0.524, 0.924] | 11/14 = 0.786 [0.524, 0.924] |
| scdb10_a10t | 1940s | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| scdb10_a10t | 1950s | 13 | 11/13 = 0.846 [0.578, 0.957] | 11/13 = 0.846 [0.578, 0.957] |
| scdb10_a10t | 1960s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| scdb10_a10t | 1970s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| scdb10_a10t | 1980s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| scdb10_a10t | 1990s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| scdb10_a10t | 2000s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb10_a10t | 2010s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb10_a10t | affirmed | 24 | 23/24 = 0.958 [0.798, 0.993] | 23/24 = 0.958 [0.798, 0.993] |
| scdb10_a10t | modified | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| scdb10_a10t | reversed | 48 | 42/48 = 0.875 [0.753, 0.941] | 42/48 = 0.875 [0.753, 0.941] |
| scdb10_a10t | reviewDismissed | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb10_a10t | vacated | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| scdb10_a10t | stratum fed|1880s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| scdb10_a10t | stratum fed|1890s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb10_a10t | stratum fed|1900s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| scdb10_a10t | stratum fed|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb10_a10t | stratum fed|1920s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb10_a10t | stratum fed|1930s (population 15, sampled 14) | 14 | 11/14 | 11/14 |
| scdb10_a10t | stratum fed|1940s (population 18, sampled 13) | 13 | 12/13 | 12/13 |
| scdb10_a10t | stratum fed|1950s (population 13, sampled 13) | 13 | 11/13 | 11/13 |
| scdb10_a10t | stratum fed|1960s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| scdb10_a10t | stratum fed|1970s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| scdb10_a10t | stratum fed|1980s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| scdb10_a10t | stratum fed|1990s (population 8, sampled 8) | 8 | 8/8 | 8/8 |
| scdb10_a10t | stratum fed|2000s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| scdb10_a10t | stratum fed|2010s (population 3, sampled 3) | 3 | 3/3 | 3/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (20 lines).
