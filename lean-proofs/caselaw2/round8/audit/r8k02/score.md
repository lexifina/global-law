# Blind audit score: r8k02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| kl_status | 565 | 80 | 68/80 = 0.850 [0.756, 0.912] | 68/80 = 0.850 [0.756, 0.912] | 74/80 = 0.925 [0.846, 0.965] | 68/80 = 0.850 [0.756, 0.912] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- kl_status: right 0.826 [0.703, 0.905] (n_eff 52); right + extent 0.826 [0.703, 0.905] (n_eff 52)

Answers on sampled rows (every reader): kl_status: none 10, reversed_or_vacated_in_part 10, vacated 140

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): kl_status: kind 10, link 10

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
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a21:rh_sa | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 21/26 = 0.808 [0.621, 0.915] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 85/89 = 0.955 [0.890, 0.982]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| kl_status | fed | 80 | 68/80 = 0.850 [0.756, 0.912] | 68/80 = 0.850 [0.756, 0.912] |
| kl_status | 1970s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| kl_status | 1980s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| kl_status | 2000s | 39 | 32/39 = 0.821 [0.673, 0.910] | 32/39 = 0.821 [0.673, 0.910] |
| kl_status | 2010s | 39 | 34/39 = 0.872 [0.733, 0.944] | 34/39 = 0.872 [0.733, 0.944] |
| kl_status | vacated | 80 | 68/80 = 0.850 [0.756, 0.912] | 68/80 = 0.850 [0.756, 0.912] |
| kl_status | stratum fed|1970s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| kl_status | stratum fed|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| kl_status | stratum fed|2000s (population 506, sampled 39) | 39 | 32/39 | 32/39 |
| kl_status | stratum fed|2010s (population 57, sampled 39) | 39 | 34/39 | 34/39 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (20 lines).
