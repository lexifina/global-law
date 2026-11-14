# Blind audit score: r10k02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| capC2 | 107 | 80 | 50/80 = 0.625 [0.515, 0.723] | 50/80 = 0.625 [0.515, 0.723] | 51/80 = 0.637 [0.528, 0.734] | 50/80 = 0.625 [0.515, 0.723] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- capC2: right 0.630 [0.570, 0.686] (n_eff 261); right + extent 0.630 [0.570, 0.686] (n_eff 261)

Answers on sampled rows (every reader): capC2: none 44, reversed 18, reversed_or_vacated_in_part 2, vacated 96

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): capC2: kind 2, link 48

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
| r6:a3:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a12:ohv | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 4/4 = 1.000 [0.510, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f04:fjc9J | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k01:remandtext | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 21/27 = 0.778 [0.592, 0.894] | 3/3 = 1.000 [0.439, 1.000] | 4 | 2 |
| ans_1_b.jsonl | 1 | 30 | 21/27 = 0.778 [0.592, 0.894] | 3/3 = 1.000 [0.439, 1.000] | 1 | 2 |
| ans_2.jsonl | 2 | 30 | 12/27 = 0.444 [0.276, 0.627] | 3/3 = 1.000 [0.439, 1.000] | 3 | 3 |
| ans_2_b.jsonl | 2 | 30 | 13/27 = 0.481 [0.307, 0.660] | 3/3 = 1.000 [0.439, 1.000] | 7 | 4 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 18/26 = 0.692 [0.500, 0.835] | 3/3 = 1.000 [0.439, 1.000] | 2 | 2 |

Items read twice: 89; same right answer 79/89 = 0.888 [0.805, 0.938]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| capC2 | fed | 80 | 50/80 = 0.625 [0.515, 0.723] | 50/80 = 0.625 [0.515, 0.723] |
| capC2 | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| capC2 | 1920s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| capC2 | 1950s | 12 | 10/12 = 0.833 [0.552, 0.953] | 10/12 = 0.833 [0.552, 0.953] |
| capC2 | 1960s | 7 | 5/7 = 0.714 [0.359, 0.918] | 5/7 = 0.714 [0.359, 0.918] |
| capC2 | 1970s | 13 | 9/13 = 0.692 [0.424, 0.873] | 9/13 = 0.692 [0.424, 0.873] |
| capC2 | 1980s | 12 | 8/12 = 0.667 [0.391, 0.862] | 8/12 = 0.667 [0.391, 0.862] |
| capC2 | 1990s | 12 | 5/12 = 0.417 [0.193, 0.680] | 5/12 = 0.417 [0.193, 0.680] |
| capC2 | 2000s | 9 | 4/9 = 0.444 [0.189, 0.733] | 4/9 = 0.444 [0.189, 0.733] |
| capC2 | 2010s | 12 | 6/12 = 0.500 [0.254, 0.746] | 6/12 = 0.500 [0.254, 0.746] |
| capC2 | reversed | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| capC2 | vacated | 71 | 42/71 = 0.592 [0.475, 0.698] | 42/71 = 0.592 [0.475, 0.698] |
| capC2 | stratum fed|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| capC2 | stratum fed|1920s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| capC2 | stratum fed|1950s (population 17, sampled 12) | 12 | 10/12 | 10/12 |
| capC2 | stratum fed|1960s (population 7, sampled 7) | 7 | 5/7 | 5/7 |
| capC2 | stratum fed|1970s (population 24, sampled 13) | 13 | 9/13 | 9/13 |
| capC2 | stratum fed|1980s (population 16, sampled 12) | 12 | 8/12 | 8/12 |
| capC2 | stratum fed|1990s (population 19, sampled 12) | 12 | 5/12 | 5/12 |
| capC2 | stratum fed|2000s (population 9, sampled 9) | 9 | 4/9 | 4/9 |
| capC2 | stratum fed|2010s (population 12, sampled 12) | 12 | 6/12 | 6/12 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (50 lines).
