# Blind audit score: r10t04 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_T4 | 245 | 80 | 68/80 = 0.850 [0.756, 0.912] | 68/80 = 0.850 [0.756, 0.912] | 77/80 = 0.963 [0.895, 0.987] | 74/80 = 0.925 [0.846, 0.965] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_T4: right 0.859 [0.781, 0.913] (n_eff 107); right + extent 0.859 [0.781, 0.913] (n_eff 107)

Answers on sampled rows (every reader): stlink_T4: affirmed 2, none 6, reversed 112, reversed_or_vacated_in_part 28, vacated 12

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_T4: kind 6, kind (same status effect) 12, link 6

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
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 4/4 = 1.000 [0.510, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p02:PJH | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3.jsonl | 3 | 29 | 22/26 = 0.846 [0.665, 0.939] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_3_b.jsonl | 3 | 29 | 22/26 = 0.846 [0.665, 0.939] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_T4 | state | 80 | 68/80 = 0.850 [0.756, 0.912] | 68/80 = 0.850 [0.756, 0.912] |
| stlink_T4 | 1950s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| stlink_T4 | 1960s | 8 | 6/8 = 0.750 [0.409, 0.928] | 6/8 = 0.750 [0.409, 0.928] |
| stlink_T4 | 1970s | 14 | 11/14 = 0.786 [0.524, 0.924] | 11/14 = 0.786 [0.524, 0.924] |
| stlink_T4 | 1980s | 14 | 12/14 = 0.857 [0.601, 0.960] | 12/14 = 0.857 [0.601, 0.960] |
| stlink_T4 | 1990s | 13 | 11/13 = 0.846 [0.578, 0.957] | 11/13 = 0.846 [0.578, 0.957] |
| stlink_T4 | 2000s | 14 | 13/14 = 0.929 [0.685, 0.987] | 13/14 = 0.929 [0.685, 0.987] |
| stlink_T4 | 2010s | 14 | 12/14 = 0.857 [0.601, 0.960] | 12/14 = 0.857 [0.601, 0.960] |
| stlink_T4 | reversed | 73 | 65/73 = 0.890 [0.798, 0.943] | 65/73 = 0.890 [0.798, 0.943] |
| stlink_T4 | vacated | 7 | 3/7 = 0.429 [0.158, 0.750] | 3/7 = 0.429 [0.158, 0.750] |
| stlink_T4 | stratum state|1950s (population 13, sampled 3) | 3 | 3/3 | 3/3 |
| stlink_T4 | stratum state|1960s (population 19, sampled 8) | 8 | 6/8 | 6/8 |
| stlink_T4 | stratum state|1970s (population 39, sampled 14) | 14 | 11/14 | 11/14 |
| stlink_T4 | stratum state|1980s (population 43, sampled 14) | 14 | 12/14 | 12/14 |
| stlink_T4 | stratum state|1990s (population 44, sampled 13) | 13 | 11/13 | 11/13 |
| stlink_T4 | stratum state|2000s (population 39, sampled 14) | 14 | 13/14 | 13/14 |
| stlink_T4 | stratum state|2010s (population 40, sampled 14) | 14 | 12/14 | 12/14 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (24 lines).
