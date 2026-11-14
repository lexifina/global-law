# Blind audit score: r7a20 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| rh_docket | 240 | 80 | 74/80 = 0.925 [0.846, 0.965] | 74/80 = 0.925 [0.846, 0.965] | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- rh_docket: right 0.929 [0.864, 0.964] (n_eff 107); right + extent 0.929 [0.864, 0.964] (n_eff 107)

Answers on sampled rows (every reader): rh_docket: modified 4, none 1, reinstated 4, reversed_or_vacated_in_part 4, vacated 31, withdrawn_or_superseded 36

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): rh_docket: kind (same status effect) 5, link 1

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
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/self | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:below/other | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:memo/caption | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/sc/sc_a1 | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 37/40 = 0.925 [0.801, 0.974] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 37/40 = 0.925 [0.801, 0.974] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| rh_docket | fed | 80 | 74/80 = 0.925 [0.846, 0.965] | 74/80 = 0.925 [0.846, 0.965] |
| rh_docket | 1970s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| rh_docket | 1980s | 17 | 16/17 = 0.941 [0.730, 0.990] | 16/17 = 0.941 [0.730, 0.990] |
| rh_docket | 1990s | 18 | 18/18 = 1.000 [0.824, 1.000] | 18/18 = 1.000 [0.824, 1.000] |
| rh_docket | 2000s | 18 | 14/18 = 0.778 [0.548, 0.910] | 14/18 = 0.778 [0.548, 0.910] |
| rh_docket | 2010s | 18 | 18/18 = 1.000 [0.824, 1.000] | 18/18 = 1.000 [0.824, 1.000] |
| rh_docket | modified | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| rh_docket | reinstated | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| rh_docket | vacated | 38 | 34/38 = 0.895 [0.759, 0.958] | 34/38 = 0.895 [0.759, 0.958] |
| rh_docket | withdrawn | 34 | 32/34 = 0.941 [0.809, 0.984] | 32/34 = 0.941 [0.809, 0.984] |
| rh_docket | stratum fed|1970s (population 9, sampled 9) | 9 | 8/9 | 8/9 |
| rh_docket | stratum fed|1980s (population 40, sampled 17) | 17 | 16/17 | 16/17 |
| rh_docket | stratum fed|1990s (population 63, sampled 18) | 18 | 18/18 | 18/18 |
| rh_docket | stratum fed|2000s (population 62, sampled 18) | 18 | 14/18 | 14/18 |
| rh_docket | stratum fed|2010s (population 66, sampled 18) | 18 | 18/18 | 18/18 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (6 lines).
