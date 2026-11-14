# Blind audit score: r11t05 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_u2wide | 149 | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | 79/80 = 0.988 [0.932, 0.998] | 78/80 = 0.975 [0.913, 0.993] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_u2wide: right 0.952 [0.884, 0.981] (n_eff 84); right + extent 0.952 [0.884, 0.981] (n_eff 84)

Answers on sampled rows (every reader): stlink_u2wide: modified 14, none 1, reversed 113, reversed_or_vacated_in_part 16, vacated 16

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_u2wide: kind 2, kind (same status effect) 2, link 1

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
| r10:r10k01:capC6 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t05:stlink_u1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 4/4 = 1.000 [0.510, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a15:b4e_rp | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k01:remandtext | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3_b.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_u2wide | state | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] |
| stlink_u2wide | 1890s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| stlink_u2wide | 1900s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| stlink_u2wide | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2wide | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2wide | 1940s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2wide | 1950s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| stlink_u2wide | 1960s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| stlink_u2wide | 1970s | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| stlink_u2wide | 1980s | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| stlink_u2wide | 1990s | 13 | 13/13 = 1.000 [0.772, 1.000] | 13/13 = 1.000 [0.772, 1.000] |
| stlink_u2wide | 2000s | 13 | 13/13 = 1.000 [0.772, 1.000] | 13/13 = 1.000 [0.772, 1.000] |
| stlink_u2wide | 2010s | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| stlink_u2wide | modified | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_u2wide | reversed | 66 | 63/66 = 0.955 [0.875, 0.984] | 63/66 = 0.955 [0.875, 0.984] |
| stlink_u2wide | vacated | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_u2wide | stratum state|1890s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| stlink_u2wide | stratum state|1900s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| stlink_u2wide | stratum state|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2wide | stratum state|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2wide | stratum state|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2wide | stratum state|1950s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| stlink_u2wide | stratum state|1960s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| stlink_u2wide | stratum state|1970s (population 17, sampled 13) | 13 | 12/13 | 12/13 |
| stlink_u2wide | stratum state|1980s (population 61, sampled 13) | 13 | 12/13 | 12/13 |
| stlink_u2wide | stratum state|1990s (population 27, sampled 13) | 13 | 13/13 | 13/13 |
| stlink_u2wide | stratum state|2000s (population 14, sampled 13) | 13 | 13/13 | 13/13 |
| stlink_u2wide | stratum state|2010s (population 15, sampled 13) | 13 | 12/13 | 12/13 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (5 lines).
