# Blind audit score: r10k01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| capC6 | 126 | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- capC6: right 0.976 [0.934, 0.992] (n_eff 134); right + extent 0.976 [0.934, 0.992] (n_eff 134)

Answers on sampled rows (every reader): capC6: none 5, reversed 20, reversed_or_vacated_in_part 3, vacated 132

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): capC6: link 6

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
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 4/4 = 1.000 [0.510, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 1 | 1 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| capC6 | fed | 80 | 77/80 = 0.963 [0.895, 0.987] | 77/80 = 0.963 [0.895, 0.987] |
| capC6 | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| capC6 | 1920s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| capC6 | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| capC6 | 1940s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| capC6 | 1950s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| capC6 | 1960s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| capC6 | 1970s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| capC6 | 1980s | 14 | 13/14 = 0.929 [0.685, 0.987] | 13/14 = 0.929 [0.685, 0.987] |
| capC6 | 1990s | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| capC6 | 2000s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| capC6 | 2010s | 29 | 29/29 = 1.000 [0.883, 1.000] | 29/29 = 1.000 [0.883, 1.000] |
| capC6 | 2020s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| capC6 | reversed | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| capC6 | vacated | 70 | 67/70 = 0.957 [0.881, 0.985] | 67/70 = 0.957 [0.881, 0.985] |
| capC6 | stratum fed|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| capC6 | stratum fed|1920s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| capC6 | stratum fed|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| capC6 | stratum fed|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| capC6 | stratum fed|1950s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| capC6 | stratum fed|1960s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| capC6 | stratum fed|1970s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| capC6 | stratum fed|1980s (population 14, sampled 14) | 14 | 13/14 | 13/14 |
| capC6 | stratum fed|1990s (population 10, sampled 10) | 10 | 9/10 | 9/10 |
| capC6 | stratum fed|2000s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| capC6 | stratum fed|2010s (population 75, sampled 29) | 29 | 29/29 | 29/29 |
| capC6 | stratum fed|2020s (population 5, sampled 5) | 5 | 5/5 | 5/5 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (6 lines).
