# Blind audit score: r8h02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| rehear8/nodate | 368 | 80 | 72/80 = 0.900 [0.815, 0.949] | 71/80 = 0.887 [0.800, 0.940] | 79/80 = 0.988 [0.932, 0.998] | 74/80 = 0.925 [0.846, 0.965] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- rehear8/nodate: right 0.911 [0.807, 0.962] (n_eff 55); right + extent 0.876 [0.764, 0.939] (n_eff 55)

Answers on sampled rows (every reader): rehear8/nodate: modified 42, none 2, reinstated 32, reversed_or_vacated_in_part 10, vacated 42, withdrawn_or_superseded 32

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): rehear8/nodate: kind 10, kind (same status effect) 4, link 2, scope 2

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
| r6:a3:rehear/enbanc-cite | 4/4 = 1.000 [0.510, 1.000] |
| r6:v1:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 24/26 = 0.923 [0.759, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 24/26 = 0.923 [0.759, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| rehear8/nodate | fed | 80 | 72/80 = 0.900 [0.815, 0.949] | 71/80 = 0.887 [0.800, 0.940] |
| rehear8/nodate | 1900s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rehear8/nodate | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rehear8/nodate | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rehear8/nodate | 1940s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| rehear8/nodate | 1950s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| rehear8/nodate | 1960s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| rehear8/nodate | 1970s | 12 | 10/12 = 0.833 [0.552, 0.953] | 10/12 = 0.833 [0.552, 0.953] |
| rehear8/nodate | 1980s | 12 | 10/12 = 0.833 [0.552, 0.953] | 10/12 = 0.833 [0.552, 0.953] |
| rehear8/nodate | 1990s | 11 | 9/11 = 0.818 [0.523, 0.949] | 9/11 = 0.818 [0.523, 0.949] |
| rehear8/nodate | 2000s | 12 | 12/12 = 1.000 [0.757, 1.000] | 11/12 = 0.917 [0.646, 0.985] |
| rehear8/nodate | 2010s | 12 | 10/12 = 0.833 [0.552, 0.953] | 10/12 = 0.833 [0.552, 0.953] |
| rehear8/nodate | modified | 18 | 18/18 = 1.000 [0.824, 1.000] | 18/18 = 1.000 [0.824, 1.000] |
| rehear8/nodate | reinstated | 16 | 16/16 = 1.000 [0.806, 1.000] | 15/16 = 0.938 [0.717, 0.989] |
| rehear8/nodate | vacated | 31 | 24/31 = 0.774 [0.602, 0.886] | 24/31 = 0.774 [0.602, 0.886] |
| rehear8/nodate | withdrawn | 15 | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] |
| rehear8/nodate | stratum fed|1900s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rehear8/nodate | stratum fed|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rehear8/nodate | stratum fed|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rehear8/nodate | stratum fed|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| rehear8/nodate | stratum fed|1950s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| rehear8/nodate | stratum fed|1960s (population 12, sampled 11) | 11 | 11/11 | 11/11 |
| rehear8/nodate | stratum fed|1970s (population 31, sampled 12) | 12 | 10/12 | 10/12 |
| rehear8/nodate | stratum fed|1980s (population 57, sampled 12) | 12 | 10/12 | 10/12 |
| rehear8/nodate | stratum fed|1990s (population 38, sampled 11) | 11 | 9/11 | 9/11 |
| rehear8/nodate | stratum fed|2000s (population 153, sampled 12) | 12 | 12/12 | 11/12 |
| rehear8/nodate | stratum fed|2010s (population 67, sampled 12) | 12 | 10/12 | 10/12 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (18 lines).
