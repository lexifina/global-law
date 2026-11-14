# Blind audit score: r12k01 (type B)

- items in the key: 76 (67 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 76; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| shC8 | 67 | 67 | 64/67 = 0.955 [0.876, 0.985] | 64/67 = 0.955 [0.876, 0.985] | 64/67 = 0.955 [0.876, 0.985] | 64/67 = 0.955 [0.876, 0.985] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- shC8: right 0.955 [0.955, 0.955] (read in full); right + extent 0.955 [0.955, 0.955] (read in full)

Answers on sampled rows (every reader): shC8: none 4, reversed_or_vacated_in_part 1, vacated 129

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): shC8: link 4

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
| r10:r10f12:fjc10b_xs | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 4/4 = 1.000 [0.510, 1.000] |
| r7:r7a12:ohv | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 26 | 20/23 = 0.870 [0.679, 0.955] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |
| ans_1_b.jsonl | 1 | 26 | 22/23 = 0.957 [0.790, 0.992] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 25 | 22/22 = 1.000 [0.851, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 25 | 22/22 = 1.000 [0.851, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 25 | 22/22 = 1.000 [0.851, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 25 | 22/22 = 1.000 [0.851, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 76; same right answer 74/76 = 0.974 [0.909, 0.993]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| shC8 | fed | 67 | 64/67 = 0.955 [0.876, 0.985] | 64/67 = 0.955 [0.876, 0.985] |
| shC8 | 1970s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| shC8 | 1980s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| shC8 | 1990s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| shC8 | 2000s | 17 | 17/17 = 1.000 [0.816, 1.000] | 17/17 = 1.000 [0.816, 1.000] |
| shC8 | 2010s | 20 | 18/20 = 0.900 [0.699, 0.972] | 18/20 = 0.900 [0.699, 0.972] |
| shC8 | 2020s | 14 | 13/14 = 0.929 [0.685, 0.987] | 13/14 = 0.929 [0.685, 0.987] |
| shC8 | vacated | 67 | 64/67 = 0.955 [0.876, 0.985] | 64/67 = 0.955 [0.876, 0.985] |
| shC8 | stratum fed|1970s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| shC8 | stratum fed|1980s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| shC8 | stratum fed|1990s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| shC8 | stratum fed|2000s (population 17, sampled 17) | 17 | 17/17 | 17/17 |
| shC8 | stratum fed|2010s (population 20, sampled 20) | 20 | 18/20 | 18/20 |
| shC8 | stratum fed|2020s (population 14, sampled 14) | 14 | 13/14 | 13/14 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (4 lines).
