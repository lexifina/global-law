# Blind audit score: r10k03 (type B)

- items in the key: 65 (57 sampled rows, 4 known-wrong decoys, 4 known-right decoys); answered: 65; answer files: 4
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| capC9 | 57 | 57 | 40/57 = 0.702 [0.573, 0.805] | 40/57 = 0.702 [0.573, 0.805] | 40/57 = 0.702 [0.573, 0.805] | 40/57 = 0.702 [0.573, 0.805] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- capC9: right 0.702 [0.702, 0.702] (read in full); right + extent 0.702 [0.702, 0.702] (read in full)

Answers on sampled rows (every reader): capC9: none 32, reversed 18, vacated 64

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): capC9: link 34

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
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f03:fjc9G2 | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p02:PJH | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 33 | 19/29 = 0.655 [0.473, 0.801] | 4/4 = 1.000 [0.510, 1.000] | 2 | 1 |
| ans_1_b.jsonl | 1 | 33 | 19/29 = 0.655 [0.473, 0.801] | 4/4 = 1.000 [0.510, 1.000] | 1 | 1 |
| ans_2.jsonl | 2 | 32 | 21/28 = 0.750 [0.566, 0.873] | 4/4 = 1.000 [0.510, 1.000] | 1 | 1 |
| ans_2_b.jsonl | 2 | 32 | 21/28 = 0.750 [0.566, 0.873] | 4/4 = 1.000 [0.510, 1.000] | 1 | 0 |

Items read twice: 65; same right answer 65/65 = 1.000 [0.944, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| capC9 | fed | 57 | 40/57 = 0.702 [0.573, 0.805] | 40/57 = 0.702 [0.573, 0.805] |
| capC9 | 1900s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| capC9 | 1910s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| capC9 | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| capC9 | 1950s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| capC9 | 1960s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| capC9 | 1970s | 6 | 3/6 = 0.500 [0.188, 0.812] | 3/6 = 0.500 [0.188, 0.812] |
| capC9 | 1980s | 11 | 5/11 = 0.455 [0.213, 0.720] | 5/11 = 0.455 [0.213, 0.720] |
| capC9 | 1990s | 5 | 3/5 = 0.600 [0.231, 0.882] | 3/5 = 0.600 [0.231, 0.882] |
| capC9 | 2000s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| capC9 | 2010s | 19 | 15/19 = 0.789 [0.567, 0.915] | 15/19 = 0.789 [0.567, 0.915] |
| capC9 | 2020s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| capC9 | reversed | 10 | 9/10 = 0.900 [0.596, 0.982] | 9/10 = 0.900 [0.596, 0.982] |
| capC9 | vacated | 47 | 31/47 = 0.660 [0.517, 0.778] | 31/47 = 0.660 [0.517, 0.778] |
| capC9 | stratum fed|1900s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| capC9 | stratum fed|1910s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| capC9 | stratum fed|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| capC9 | stratum fed|1950s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| capC9 | stratum fed|1960s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| capC9 | stratum fed|1970s (population 6, sampled 6) | 6 | 3/6 | 3/6 |
| capC9 | stratum fed|1980s (population 11, sampled 11) | 11 | 5/11 | 5/11 |
| capC9 | stratum fed|1990s (population 5, sampled 5) | 5 | 3/5 | 3/5 |
| capC9 | stratum fed|2000s (population 4, sampled 4) | 4 | 3/4 | 3/4 |
| capC9 | stratum fed|2010s (population 19, sampled 19) | 19 | 15/19 | 15/19 |
| capC9 | stratum fed|2020s (population 1, sampled 1) | 1 | 1/1 | 1/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (34 lines).
