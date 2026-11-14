# Blind audit score: r8k01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| kb_status | 235 | 80 | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- kb_status: right 0.988 [0.929, 0.998] (n_eff 74); right + extent 0.988 [0.929, 0.998] (n_eff 74)

Answers on sampled rows (every reader): kb_status: none 1, reversed_or_vacated_in_part 10, vacated 149

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): kb_status: link 2

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
| r6:r1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 4/4 = 1.000 [0.510, 1.000] |
| r6:v2:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a12:ohv | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a15:b4e_rp | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 1 | 1 |
| ans_1_b.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| kb_status | fed | 80 | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] |
| kb_status | 1960s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| kb_status | 1970s | 13 | 13/13 = 1.000 [0.772, 1.000] | 13/13 = 1.000 [0.772, 1.000] |
| kb_status | 1980s | 16 | 16/16 = 1.000 [0.806, 1.000] | 16/16 = 1.000 [0.806, 1.000] |
| kb_status | 1990s | 16 | 15/16 = 0.938 [0.717, 0.989] | 15/16 = 0.938 [0.717, 0.989] |
| kb_status | 2000s | 15 | 15/15 = 1.000 [0.796, 1.000] | 15/15 = 1.000 [0.796, 1.000] |
| kb_status | 2010s | 16 | 16/16 = 1.000 [0.806, 1.000] | 16/16 = 1.000 [0.806, 1.000] |
| kb_status | 2020s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| kb_status | reversed | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| kb_status | vacated | 79 | 78/79 = 0.987 [0.932, 0.998] | 78/79 = 0.987 [0.932, 0.998] |
| kb_status | stratum fed|1960s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| kb_status | stratum fed|1970s (population 13, sampled 13) | 13 | 13/13 | 13/13 |
| kb_status | stratum fed|1980s (population 31, sampled 16) | 16 | 16/16 | 16/16 |
| kb_status | stratum fed|1990s (population 47, sampled 16) | 16 | 15/16 | 15/16 |
| kb_status | stratum fed|2000s (population 35, sampled 15) | 15 | 15/15 | 15/15 |
| kb_status | stratum fed|2010s (population 105, sampled 16) | 16 | 16/16 | 16/16 |
| kb_status | stratum fed|2020s (population 3, sampled 3) | 3 | 3/3 | 3/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
