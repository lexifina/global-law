# Blind audit score: r9k01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| remandtext | 328 | 80 | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- remandtext: right 0.964 [0.875, 0.990] (n_eff 53); right + extent 0.964 [0.875, 0.990] (n_eff 53)

Answers on sampled rows (every reader): remandtext: none 2, reversed 8, reversed_or_vacated_in_part 4, vacated 146

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): remandtext: link 2

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
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| remandtext | fed | 80 | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] |
| remandtext | 1940s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| remandtext | 1950s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| remandtext | 1960s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| remandtext | 1970s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| remandtext | 1980s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| remandtext | 1990s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| remandtext | 2000s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| remandtext | 2010s | 12 | 11/12 = 0.917 [0.646, 0.985] | 11/12 = 0.917 [0.646, 0.985] |
| remandtext | 2020s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| remandtext | reversed | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| remandtext | vacated | 76 | 75/76 = 0.987 [0.929, 0.998] | 75/76 = 0.987 [0.929, 0.998] |
| remandtext | stratum fed|1940s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| remandtext | stratum fed|1950s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| remandtext | stratum fed|1960s (population 14, sampled 11) | 11 | 11/11 | 11/11 |
| remandtext | stratum fed|1970s (population 31, sampled 11) | 11 | 11/11 | 11/11 |
| remandtext | stratum fed|1980s (population 68, sampled 12) | 12 | 12/12 | 12/12 |
| remandtext | stratum fed|1990s (population 38, sampled 12) | 12 | 12/12 | 12/12 |
| remandtext | stratum fed|2000s (population 24, sampled 11) | 11 | 11/11 | 11/11 |
| remandtext | stratum fed|2010s (population 142, sampled 12) | 12 | 11/12 | 11/12 |
| remandtext | stratum fed|2020s (population 5, sampled 5) | 5 | 5/5 | 5/5 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
