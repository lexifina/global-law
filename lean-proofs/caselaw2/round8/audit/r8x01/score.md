# Blind audit score: r8x01 (type B)

- items in the key: 23 (20 sampled rows, 2 known-wrong decoys, 1 known-right decoys); answered: 23; answer files: 1
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| rh_eb | 748 | 20 | 19/20 = 0.950 [0.764, 0.991] | 19/20 = 0.950 [0.764, 0.991] | 20/20 = 1.000 [0.839, 1.000] | 20/20 = 1.000 [0.839, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- rh_eb: right 0.999 [0.792, 1.000] (n_eff 15); right + extent 0.999 [0.792, 1.000] (n_eff 15)

Answers on sampled rows (every reader): rh_eb: modified 1, rehearing_en_banc_only 7, reversed_or_vacated_in_part 2, vacated 9, withdrawn_or_superseded 1

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): rh_eb: kind (same status effect) 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 3/3 = 1.000 [0.439, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 1/1 = 1.000 [0.206, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 1/1 = 1.000 [0.206, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 23 | 19/20 = 0.950 [0.764, 0.991] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| rh_eb | fed | 18 | 18/18 = 1.000 [0.824, 1.000] | 18/18 = 1.000 [0.824, 1.000] |
| rh_eb | state | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| rh_eb | 1970s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| rh_eb | 1980s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| rh_eb | 1990s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| rh_eb | 2000s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| rh_eb | 2010s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| rh_eb | 2020s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rh_eb | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rh_eb | rehearingEnBancGranted | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| rh_eb | vacated | 12 | 11/12 = 0.917 [0.646, 0.985] | 11/12 = 0.917 [0.646, 0.985] |
| rh_eb | stratum fed|1970s (population 48, sampled 4) | 4 | 4/4 | 4/4 |
| rh_eb | stratum fed|1980s (population 157, sampled 3) | 3 | 3/3 | 3/3 |
| rh_eb | stratum fed|1990s (population 199, sampled 3) | 3 | 3/3 | 3/3 |
| rh_eb | stratum fed|2000s (population 148, sampled 3) | 3 | 3/3 | 3/3 |
| rh_eb | stratum fed|2010s (population 193, sampled 4) | 4 | 4/4 | 4/4 |
| rh_eb | stratum fed|2020s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rh_eb | stratum state|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rh_eb | stratum state|2000s (population 1, sampled 1) | 1 | 0/1 | 0/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (1 lines).
