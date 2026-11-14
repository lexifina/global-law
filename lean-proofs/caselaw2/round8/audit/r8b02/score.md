# Blind audit score: r8b02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb8_anchor | 111 | 80 | 72/80 = 0.900 [0.815, 0.949] | 72/80 = 0.900 [0.815, 0.949] | 76/80 = 0.950 [0.878, 0.980] | 72/80 = 0.900 [0.815, 0.949] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb8_anchor: right 0.902 [0.848, 0.938] (n_eff 170); right + extent 0.902 [0.848, 0.938] (n_eff 170)

Answers on sampled rows (every reader): scdb8_anchor: modified 2, none 6, other 2, reversed 120, reversed_or_vacated_in_part 16, vacated 14

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb8_anchor: kind 6, link 6

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
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 21/26 = 0.808 [0.621, 0.915] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |

Items read twice: 89; same right answer 85/89 = 0.955 [0.890, 0.982]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb8_anchor | fed | 80 | 72/80 = 0.900 [0.815, 0.949] | 72/80 = 0.900 [0.815, 0.949] |
| scdb8_anchor | 1870s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_anchor | 1890s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_anchor | 1900s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| scdb8_anchor | 1910s | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| scdb8_anchor | 1920s | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| scdb8_anchor | 1960s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb8_anchor | 1980s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| scdb8_anchor | 1990s | 14 | 12/14 = 0.857 [0.601, 0.960] | 12/14 = 0.857 [0.601, 0.960] |
| scdb8_anchor | 2000s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| scdb8_anchor | 2010s | 13 | 11/13 = 0.846 [0.578, 0.957] | 11/13 = 0.846 [0.578, 0.957] |
| scdb8_anchor | 2020s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| scdb8_anchor | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_anchor | reversed | 70 | 64/70 = 0.914 [0.825, 0.960] | 64/70 = 0.914 [0.825, 0.960] |
| scdb8_anchor | vacated | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| scdb8_anchor | stratum fed|1870s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_anchor | stratum fed|1890s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_anchor | stratum fed|1900s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| scdb8_anchor | stratum fed|1910s (population 35, sampled 13) | 13 | 12/13 | 12/13 |
| scdb8_anchor | stratum fed|1920s (population 15, sampled 13) | 13 | 12/13 | 12/13 |
| scdb8_anchor | stratum fed|1960s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb8_anchor | stratum fed|1980s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| scdb8_anchor | stratum fed|1990s (population 14, sampled 14) | 14 | 12/14 | 12/14 |
| scdb8_anchor | stratum fed|2000s (population 8, sampled 8) | 8 | 8/8 | 8/8 |
| scdb8_anchor | stratum fed|2010s (population 20, sampled 13) | 13 | 11/13 | 11/13 |
| scdb8_anchor | stratum fed|2020s (population 4, sampled 4) | 4 | 3/4 | 3/4 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (12 lines).
