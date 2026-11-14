# Blind audit score: r7a17 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| rh_eb | 748 | 80 | 78/80 = 0.975 [0.913, 0.993] | 78/80 = 0.975 [0.913, 0.993] | 80/80 = 1.000 [0.954, 1.000] | 79/80 = 0.988 [0.932, 0.998] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- rh_eb: right 0.981 [0.919, 0.996] (n_eff 75); right + extent 0.981 [0.919, 0.996] (n_eff 75)

Answers on sampled rows (every reader): rh_eb: modified 1, rehearing_en_banc_only 39, reinstated 1, reversed_or_vacated_in_part 2, review_denied 1, vacated 35, withdrawn_or_superseded 1

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): rh_eb: kind 1, kind (same status effect) 1

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
| r6:a3:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:rehear/docket | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:rehear/enbanc-cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/self | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/sc/sc_a1 | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 39/40 = 0.975 [0.871, 0.996] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 39/40 = 0.975 [0.871, 0.996] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| rh_eb | fed | 78 | 77/78 = 0.987 [0.931, 0.998] | 77/78 = 0.987 [0.931, 0.998] |
| rh_eb | state | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| rh_eb | 1970s | 16 | 16/16 = 1.000 [0.806, 1.000] | 16/16 = 1.000 [0.806, 1.000] |
| rh_eb | 1980s | 16 | 16/16 = 1.000 [0.806, 1.000] | 16/16 = 1.000 [0.806, 1.000] |
| rh_eb | 1990s | 15 | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] |
| rh_eb | 2000s | 16 | 15/16 = 0.938 [0.717, 0.989] | 15/16 = 0.938 [0.717, 0.989] |
| rh_eb | 2010s | 16 | 16/16 = 1.000 [0.806, 1.000] | 16/16 = 1.000 [0.806, 1.000] |
| rh_eb | 2020s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rh_eb | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rh_eb | rehearingEnBancGranted | 43 | 42/43 = 0.977 [0.879, 0.996] | 42/43 = 0.977 [0.879, 0.996] |
| rh_eb | reinstated | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rh_eb | vacated | 35 | 34/35 = 0.971 [0.855, 0.995] | 34/35 = 0.971 [0.855, 0.995] |
| rh_eb | stratum fed|1970s (population 48, sampled 16) | 16 | 16/16 | 16/16 |
| rh_eb | stratum fed|1980s (population 157, sampled 15) | 15 | 15/15 | 15/15 |
| rh_eb | stratum fed|1990s (population 199, sampled 15) | 15 | 14/15 | 14/15 |
| rh_eb | stratum fed|2000s (population 148, sampled 15) | 15 | 15/15 | 15/15 |
| rh_eb | stratum fed|2010s (population 193, sampled 16) | 16 | 16/16 | 16/16 |
| rh_eb | stratum fed|2020s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rh_eb | stratum state|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rh_eb | stratum state|2000s (population 1, sampled 1) | 1 | 0/1 | 0/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
