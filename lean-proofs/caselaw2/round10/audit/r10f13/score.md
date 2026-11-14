# Blind audit score: r10f13 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc10b_hp | 456 | 80 | 73/80 = 0.912 [0.830, 0.957] | 73/80 = 0.912 [0.830, 0.957] | 78/80 = 0.975 [0.913, 0.993] | 73/80 = 0.912 [0.830, 0.957] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc10b_hp: right 0.907 [0.823, 0.954] (n_eff 79); right + extent 0.907 [0.823, 0.954] (n_eff 79)

Answers on sampled rows (every reader): fjc10b_hp: affirmed 3, modified 4, none 4, reversed 77, reversed_or_vacated_in_part 44, vacated 28

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc10b_hp: kind 8, link 4

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 17/18 = 0.944 [0.742, 0.990]
- known wrong, not confirmed: 11/12 = 0.917 [0.646, 0.985]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 5/6 = 0.833 [0.436, 0.970] | 3/4 = 0.750 [0.301, 0.954] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 3/4 = 0.750 [0.301, 0.954] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 25/27 = 0.926 [0.766, 0.979] | 2/3 = 0.667 [0.208, 0.939] | 0 | 1 |
| ans_1_b.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3_b.jsonl | 3 | 29 | 24/26 = 0.923 [0.759, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |

Items read twice: 89; same right answer 86/89 = 0.966 [0.905, 0.989]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc10b_hp | fed | 80 | 73/80 = 0.912 [0.830, 0.957] | 73/80 = 0.912 [0.830, 0.957] |
| fjc10b_hp | 1940s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| fjc10b_hp | 1950s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| fjc10b_hp | 1960s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| fjc10b_hp | 1970s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| fjc10b_hp | 1980s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| fjc10b_hp | 1990s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| fjc10b_hp | 2000s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| fjc10b_hp | 2010s | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] |
| fjc10b_hp | modified | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| fjc10b_hp | reversed | 59 | 53/59 = 0.898 [0.795, 0.953] | 53/59 = 0.898 [0.795, 0.953] |
| fjc10b_hp | vacated | 19 | 18/19 = 0.947 [0.754, 0.991] | 18/19 = 0.947 [0.754, 0.991] |
| fjc10b_hp | stratum fed|1940s (population 20, sampled 10) | 10 | 9/10 | 9/10 |
| fjc10b_hp | stratum fed|1950s (population 28, sampled 10) | 10 | 10/10 | 10/10 |
| fjc10b_hp | stratum fed|1960s (population 30, sampled 10) | 10 | 9/10 | 9/10 |
| fjc10b_hp | stratum fed|1970s (population 63, sampled 10) | 10 | 9/10 | 9/10 |
| fjc10b_hp | stratum fed|1980s (population 85, sampled 10) | 10 | 9/10 | 9/10 |
| fjc10b_hp | stratum fed|1990s (population 100, sampled 10) | 10 | 9/10 | 9/10 |
| fjc10b_hp | stratum fed|2000s (population 62, sampled 10) | 10 | 10/10 | 10/10 |
| fjc10b_hp | stratum fed|2010s (population 56, sampled 10) | 10 | 8/10 | 8/10 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (13 lines).
