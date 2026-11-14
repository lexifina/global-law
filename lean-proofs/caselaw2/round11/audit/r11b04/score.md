# Blind audit score: r11b04 (type B)

- items in the key: 55 (49 sampled rows, 4 known-wrong decoys, 2 known-right decoys); answered: 55; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb11_r2v3 | 88 | 49 | 44/49 = 0.898 [0.782, 0.956] | 43/49 = 0.878 [0.758, 0.943] | 48/49 = 0.980 [0.893, 0.996] | 44/49 = 0.898 [0.782, 0.956] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb11_r2v3: right 0.906 [0.828, 0.951] (n_eff 89); right + extent 0.892 [0.810, 0.941] (n_eff 89)

Answers on sampled rows (every reader): scdb11_r2v3: none 1, rehearing_en_banc_only 20, reinstated 6, reversed_or_vacated_in_part 2, vacated 63, withdrawn_or_superseded 6

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb11_r2v3: kind 8, link 1, scope 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 12/12 = 1.000 [0.757, 1.000]
- known wrong, not confirmed: 8/8 = 1.000 [0.676, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 12/12 = 1.000 [0.757, 1.000] | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10k01:capC6 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t05:stlink_u1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a15:b4e_rp | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f03:fjc9G2 | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 55 | 44/49 = 0.898 [0.782, 0.956] | 6/6 = 1.000 [0.610, 1.000] | 0 | 1 |
| ans_1_b.jsonl | 1 | 55 | 45/49 = 0.918 [0.808, 0.968] | 6/6 = 1.000 [0.610, 1.000] | 0 | 1 |

Items read twice: 55; same right answer 54/55 = 0.982 [0.904, 0.997]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb11_r2v3 | fed | 49 | 44/49 = 0.898 [0.782, 0.956] | 43/49 = 0.878 [0.758, 0.943] |
| scdb11_r2v3 | 1980s | 7 | 5/7 = 0.714 [0.359, 0.918] | 5/7 = 0.714 [0.359, 0.918] |
| scdb11_r2v3 | 1990s | 18 | 16/18 = 0.889 [0.672, 0.969] | 15/18 = 0.833 [0.608, 0.942] |
| scdb11_r2v3 | 2000s | 16 | 15/16 = 0.938 [0.717, 0.989] | 15/16 = 0.938 [0.717, 0.989] |
| scdb11_r2v3 | 2010s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| scdb11_r2v3 | rehearingEnBancGranted | 24 | 21/24 = 0.875 [0.690, 0.957] | 20/24 = 0.833 [0.641, 0.933] |
| scdb11_r2v3 | vacated | 23 | 21/23 = 0.913 [0.732, 0.976] | 21/23 = 0.913 [0.732, 0.976] |
| scdb11_r2v3 | withdrawn | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb11_r2v3 | stratum fed|1980s (population 14, sampled 7) | 7 | 5/7 | 5/7 |
| scdb11_r2v3 | stratum fed|1990s (population 23, sampled 18) | 18 | 16/18 | 15/18 |
| scdb11_r2v3 | stratum fed|2000s (population 27, sampled 16) | 16 | 15/16 | 15/16 |
| scdb11_r2v3 | stratum fed|2010s (population 17, sampled 8) | 8 | 8/8 | 8/8 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (11 lines).
