# Blind audit score: r12t01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_u2t_fdate | 386 | 80 | 76/80 = 0.950 [0.878, 0.980] | 76/80 = 0.950 [0.878, 0.980] | 77/80 = 0.963 [0.895, 0.987] | 76/80 = 0.950 [0.878, 0.980] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_u2t_fdate: right 0.949 [0.861, 0.983] (n_eff 59); right + extent 0.949 [0.861, 0.983] (n_eff 59)

Answers on sampled rows (every reader): stlink_u2t_fdate: affirmed 2, modified 6, none 6, reversed 130, reversed_or_vacated_in_part 10, vacated 6

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_u2t_fdate: kind 2, link 6

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
| r10:r10f11:fjc10b_h | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k01:remandtext | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_u2t_fdate | state | 80 | 76/80 = 0.950 [0.878, 0.980] | 76/80 = 0.950 [0.878, 0.980] |
| stlink_u2t_fdate | 1890s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| stlink_u2t_fdate | 1900s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| stlink_u2t_fdate | 1910s | 7 | 6/7 = 0.857 [0.487, 0.974] | 6/7 = 0.857 [0.487, 0.974] |
| stlink_u2t_fdate | 1920s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| stlink_u2t_fdate | 1930s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| stlink_u2t_fdate | 1940s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| stlink_u2t_fdate | 1950s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_u2t_fdate | 1960s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_u2t_fdate | 1970s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| stlink_u2t_fdate | 1980s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| stlink_u2t_fdate | 1990s | 7 | 6/7 = 0.857 [0.487, 0.974] | 6/7 = 0.857 [0.487, 0.974] |
| stlink_u2t_fdate | 2000s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_u2t_fdate | 2010s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_u2t_fdate | modified | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| stlink_u2t_fdate | reversed | 74 | 70/74 = 0.946 [0.869, 0.979] | 70/74 = 0.946 [0.869, 0.979] |
| stlink_u2t_fdate | vacated | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| stlink_u2t_fdate | stratum state|1890s (population 5, sampled 4) | 4 | 4/4 | 4/4 |
| stlink_u2t_fdate | stratum state|1900s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| stlink_u2t_fdate | stratum state|1910s (population 7, sampled 7) | 7 | 6/7 | 6/7 |
| stlink_u2t_fdate | stratum state|1920s (population 8, sampled 6) | 6 | 6/6 | 6/6 |
| stlink_u2t_fdate | stratum state|1930s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| stlink_u2t_fdate | stratum state|1940s (population 11, sampled 6) | 6 | 6/6 | 6/6 |
| stlink_u2t_fdate | stratum state|1950s (population 26, sampled 7) | 7 | 7/7 | 7/7 |
| stlink_u2t_fdate | stratum state|1960s (population 25, sampled 7) | 7 | 7/7 | 7/7 |
| stlink_u2t_fdate | stratum state|1970s (population 55, sampled 6) | 6 | 5/6 | 5/6 |
| stlink_u2t_fdate | stratum state|1980s (population 69, sampled 6) | 6 | 6/6 | 6/6 |
| stlink_u2t_fdate | stratum state|1990s (population 59, sampled 7) | 7 | 6/7 | 6/7 |
| stlink_u2t_fdate | stratum state|2000s (population 54, sampled 7) | 7 | 7/7 | 7/7 |
| stlink_u2t_fdate | stratum state|2010s (population 57, sampled 7) | 7 | 7/7 | 7/7 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (8 lines).
