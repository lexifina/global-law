# Blind audit score: r8h01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| rehear8/grant | 299 | 80 | 76/80 = 0.950 [0.878, 0.980] | 75/80 = 0.938 [0.862, 0.973] | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- rehear8/grant: right 0.957 [0.888, 0.984] (n_eff 80); right + extent 0.954 [0.883, 0.983] (n_eff 80)

Answers on sampled rows (every reader): rehear8/grant: none 5, rehearing_en_banc_only 90, vacated 54, withdrawn_or_superseded 11

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): rehear8/grant: kind (same status effect) 2, link 5, scope 1

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
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| rehear8/grant | fed | 40 | 38/40 = 0.950 [0.835, 0.986] | 38/40 = 0.950 [0.835, 0.986] |
| rehear8/grant | state | 40 | 38/40 = 0.950 [0.835, 0.986] | 37/40 = 0.925 [0.801, 0.974] |
| rehear8/grant | 1930s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| rehear8/grant | 1950s | 1 | 1/1 = 1.000 [0.206, 1.000] | 0/1 = 0.000 [0.000, 0.793] |
| rehear8/grant | 1970s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| rehear8/grant | 1980s | 13 | 13/13 = 1.000 [0.772, 1.000] | 13/13 = 1.000 [0.772, 1.000] |
| rehear8/grant | 1990s | 19 | 18/19 = 0.947 [0.754, 0.991] | 18/19 = 0.947 [0.754, 0.991] |
| rehear8/grant | 2000s | 18 | 18/18 = 1.000 [0.824, 1.000] | 18/18 = 1.000 [0.824, 1.000] |
| rehear8/grant | 2010s | 18 | 16/18 = 0.889 [0.672, 0.969] | 16/18 = 0.889 [0.672, 0.969] |
| rehear8/grant | 2020s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| rehear8/grant | rehearingEnBancGranted | 50 | 48/50 = 0.960 [0.865, 0.989] | 48/50 = 0.960 [0.865, 0.989] |
| rehear8/grant | vacated | 25 | 24/25 = 0.960 [0.805, 0.993] | 24/25 = 0.960 [0.805, 0.993] |
| rehear8/grant | withdrawn | 5 | 4/5 = 0.800 [0.376, 0.964] | 3/5 = 0.600 [0.231, 0.882] |
| rehear8/grant | stratum fed|1970s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| rehear8/grant | stratum fed|1980s (population 29, sampled 7) | 7 | 7/7 | 7/7 |
| rehear8/grant | stratum fed|1990s (population 36, sampled 8) | 8 | 7/8 | 7/8 |
| rehear8/grant | stratum fed|2000s (population 24, sampled 7) | 7 | 7/7 | 7/7 |
| rehear8/grant | stratum fed|2010s (population 46, sampled 8) | 8 | 7/8 | 7/8 |
| rehear8/grant | stratum fed|2020s (population 18, sampled 7) | 7 | 7/7 | 7/7 |
| rehear8/grant | stratum state|1930s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| rehear8/grant | stratum state|1950s (population 1, sampled 1) | 1 | 1/1 | 0/1 |
| rehear8/grant | stratum state|1980s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| rehear8/grant | stratum state|1990s (population 41, sampled 11) | 11 | 11/11 | 11/11 |
| rehear8/grant | stratum state|2000s (population 78, sampled 11) | 11 | 11/11 | 11/11 |
| rehear8/grant | stratum state|2010s (population 16, sampled 10) | 10 | 9/10 | 9/10 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (8 lines).
