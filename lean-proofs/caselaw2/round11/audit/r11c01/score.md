# Blind audit score: r11c01 (type B)

- items in the key: 71 (63 sampled rows, 4 known-wrong decoys, 4 known-right decoys); answered: 71; answer files: 4
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| c11a | 63 | 63 | 53/63 = 0.841 [0.732, 0.911] | 53/63 = 0.841 [0.732, 0.911] | 57/63 = 0.905 [0.807, 0.956] | 55/63 = 0.873 [0.769, 0.934] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- c11a: right 0.841 [0.841, 0.841] (read in full); right + extent 0.841 [0.841, 0.841] (read in full)

Answers on sampled rows (every reader): c11a: affirmed 6, none 12, reversed 72, reversed_or_vacated_in_part 26, vacated 10

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): c11a: kind 4, kind (same status effect) 4, link 12

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 16/16 = 1.000 [0.806, 1.000]
- known wrong, not confirmed: 8/8 = 1.000 [0.676, 1.000]
- known right, confirmed: 8/8 = 1.000 [0.676, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| pack_2 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10b03:scdb10_a10n | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10f13:fjc10b_hp | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t04:stlink_T4 | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f04:fjc9J | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 36 | 26/32 = 0.812 [0.647, 0.911] | 4/4 = 1.000 [0.510, 1.000] | 0 | 3 |
| ans_1_b.jsonl | 1 | 36 | 26/32 = 0.812 [0.647, 0.911] | 4/4 = 1.000 [0.510, 1.000] | 0 | 2 |
| ans_2.jsonl | 2 | 35 | 27/31 = 0.871 [0.712, 0.949] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 35 | 27/31 = 0.871 [0.712, 0.949] | 4/4 = 1.000 [0.510, 1.000] | 0 | 1 |

Items read twice: 71; same right answer 71/71 = 1.000 [0.949, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| c11a | fed | 63 | 53/63 = 0.841 [0.732, 0.911] | 53/63 = 0.841 [0.732, 0.911] |
| c11a | 1940s | 5 | 2/5 = 0.400 [0.118, 0.769] | 2/5 = 0.400 [0.118, 0.769] |
| c11a | 1950s | 10 | 7/10 = 0.700 [0.397, 0.892] | 7/10 = 0.700 [0.397, 0.892] |
| c11a | 1960s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| c11a | 1970s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| c11a | 1980s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| c11a | 1990s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| c11a | 2000s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| c11a | 2010s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| c11a | 2020s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| c11a | modified | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| c11a | reversed | 54 | 46/54 = 0.852 [0.734, 0.923] | 46/54 = 0.852 [0.734, 0.923] |
| c11a | vacated | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| c11a | stratum fed|1940s (population 5, sampled 5) | 5 | 2/5 | 2/5 |
| c11a | stratum fed|1950s (population 10, sampled 10) | 10 | 7/10 | 7/10 |
| c11a | stratum fed|1960s (population 9, sampled 9) | 9 | 8/9 | 8/9 |
| c11a | stratum fed|1970s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| c11a | stratum fed|1980s (population 9, sampled 9) | 9 | 9/9 | 9/9 |
| c11a | stratum fed|1990s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| c11a | stratum fed|2000s (population 10, sampled 10) | 10 | 10/10 | 10/10 |
| c11a | stratum fed|2010s (population 6, sampled 6) | 6 | 4/6 | 4/6 |
| c11a | stratum fed|2020s (population 1, sampled 1) | 1 | 1/1 | 1/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (20 lines).
