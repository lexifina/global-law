# Blind audit score: r10t02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_g2 | 1648 | 80 | 76/80 = 0.950 [0.878, 0.980] | 76/80 = 0.950 [0.878, 0.980] | 78/80 = 0.975 [0.913, 0.993] | 77/80 = 0.963 [0.895, 0.987] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_g2: right 0.969 [0.886, 0.992] (n_eff 57); right + extent 0.969 [0.886, 0.992] (n_eff 57)

Answers on sampled rows (every reader): stlink_g2: affirmed 2, none 3, reversed 136, reversed_or_vacated_in_part 10, vacated 8, withdrawn_or_superseded 1

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_g2: kind 2, kind (same status effect) 3, link 3

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
| r6:a3:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f04:fjc9J | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k02:remandtext2 | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_g2 | state | 80 | 76/80 = 0.950 [0.878, 0.980] | 76/80 = 0.950 [0.878, 0.980] |
| stlink_g2 | 1880s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_g2 | 1890s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_g2 | 1900s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_g2 | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_g2 | 1920s | 5 | 3/5 = 0.600 [0.231, 0.882] | 3/5 = 0.600 [0.231, 0.882] |
| stlink_g2 | 1930s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_g2 | 1940s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_g2 | 1950s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_g2 | 1960s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| stlink_g2 | 1970s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_g2 | 1980s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_g2 | 1990s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| stlink_g2 | 2000s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| stlink_g2 | 2010s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_g2 | reversed | 77 | 73/77 = 0.948 [0.874, 0.980] | 73/77 = 0.948 [0.874, 0.980] |
| stlink_g2 | vacated | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| stlink_g2 | stratum state|1880s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_g2 | stratum state|1890s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_g2 | stratum state|1900s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_g2 | stratum state|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_g2 | stratum state|1920s (population 5, sampled 5) | 5 | 3/5 | 3/5 |
| stlink_g2 | stratum state|1930s (population 44, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_g2 | stratum state|1940s (population 70, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_g2 | stratum state|1950s (population 92, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_g2 | stratum state|1960s (population 135, sampled 8) | 8 | 7/8 | 7/8 |
| stlink_g2 | stratum state|1970s (population 202, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_g2 | stratum state|1980s (population 322, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_g2 | stratum state|1990s (population 336, sampled 8) | 8 | 8/8 | 8/8 |
| stlink_g2 | stratum state|2000s (population 264, sampled 8) | 8 | 7/8 | 7/8 |
| stlink_g2 | stratum state|2010s (population 174, sampled 7) | 7 | 7/7 | 7/7 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (8 lines).
