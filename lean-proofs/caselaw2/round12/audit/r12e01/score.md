# Blind audit score: r12e01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| enbanc12_eb12 | 117 | 80 | 65/80 = 0.812 [0.713, 0.883] | 65/80 = 0.812 [0.713, 0.883] | 67/80 = 0.838 [0.742, 0.902] | 65/80 = 0.812 [0.713, 0.883] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- enbanc12_eb12: right 0.834 [0.774, 0.880] (n_eff 187); right + extent 0.834 [0.774, 0.880] (n_eff 187)

Answers on sampled rows (every reader): enbanc12_eb12: none 25, reversed_or_vacated_in_part 4, vacated 131

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): enbanc12_eb12: kind 4, link 25

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
| r10:r10y01:syl10_RO_hist | 2/2 = 1.000 [0.342, 1.000] |
| r11:r11c02:c11b | 2/2 = 1.000 [0.342, 1.000] |
| r11:r11f02:fjc11_fu2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a17:rh_eb | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 21/27 = 0.778 [0.592, 0.894] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 21/27 = 0.778 [0.592, 0.894] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3.jsonl | 3 | 29 | 22/26 = 0.846 [0.665, 0.939] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 21/26 = 0.808 [0.621, 0.915] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| enbanc12_eb12 | fed | 78 | 65/78 = 0.833 [0.735, 0.900] | 65/78 = 0.833 [0.735, 0.900] |
| enbanc12_eb12 | state | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| enbanc12_eb12 | 1960s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| enbanc12_eb12 | 1970s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| enbanc12_eb12 | 1980s | 15 | 12/15 = 0.800 [0.548, 0.929] | 12/15 = 0.800 [0.548, 0.929] |
| enbanc12_eb12 | 1990s | 16 | 12/16 = 0.750 [0.505, 0.898] | 12/16 = 0.750 [0.505, 0.898] |
| enbanc12_eb12 | 2000s | 15 | 10/15 = 0.667 [0.417, 0.848] | 10/15 = 0.667 [0.417, 0.848] |
| enbanc12_eb12 | 2010s | 15 | 13/15 = 0.867 [0.621, 0.963] | 13/15 = 0.867 [0.621, 0.963] |
| enbanc12_eb12 | 2020s | 15 | 15/15 = 1.000 [0.796, 1.000] | 15/15 = 1.000 [0.796, 1.000] |
| enbanc12_eb12 | vacated | 78 | 65/78 = 0.833 [0.735, 0.900] | 65/78 = 0.833 [0.735, 0.900] |
| enbanc12_eb12 | withdrawn | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| enbanc12_eb12 | stratum fed|1960s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| enbanc12_eb12 | stratum fed|1970s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| enbanc12_eb12 | stratum fed|1980s (population 15, sampled 15) | 15 | 12/15 | 12/15 |
| enbanc12_eb12 | stratum fed|1990s (population 29, sampled 15) | 15 | 12/15 | 12/15 |
| enbanc12_eb12 | stratum fed|2000s (population 20, sampled 15) | 15 | 10/15 | 10/15 |
| enbanc12_eb12 | stratum fed|2010s (population 14, sampled 14) | 14 | 13/14 | 13/14 |
| enbanc12_eb12 | stratum fed|2020s (population 33, sampled 15) | 15 | 15/15 | 15/15 |
| enbanc12_eb12 | stratum state|1990s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| enbanc12_eb12 | stratum state|2010s (population 1, sampled 1) | 1 | 0/1 | 0/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (29 lines).
