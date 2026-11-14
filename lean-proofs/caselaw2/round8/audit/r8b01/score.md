# Blind audit score: r8b01 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb8_disp | 84 | 80 | 67/80 = 0.838 [0.742, 0.902] | 67/80 = 0.838 [0.742, 0.902] | 71/80 = 0.887 [0.800, 0.940] | 67/80 = 0.838 [0.742, 0.902] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb8_disp: right 0.833 [0.813, 0.852] (n_eff 1437); right + extent 0.833 [0.813, 0.852] (n_eff 1437)

Answers on sampled rows (every reader): scdb8_disp: affirmed 2, none 17, reversed 121, reversed_or_vacated_in_part 10, vacated 10

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb8_disp: kind 8, link 17

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
| r6:v1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/other | 4/4 = 1.000 [0.510, 1.000] |
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a13:b4a_r3 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 21/27 = 0.778 [0.592, 0.894] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 21/27 = 0.778 [0.592, 0.894] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |
| ans_2_b.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 21/26 = 0.808 [0.621, 0.915] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 21/26 = 0.808 [0.621, 0.915] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb8_disp | fed | 80 | 67/80 = 0.838 [0.742, 0.902] | 67/80 = 0.838 [0.742, 0.902] |
| scdb8_disp | 1850s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb8_disp | 1880s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_disp | 1890s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb8_disp | 1900s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| scdb8_disp | 1910s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb8_disp | 1920s | 7 | 6/7 = 0.857 [0.487, 0.974] | 6/7 = 0.857 [0.487, 0.974] |
| scdb8_disp | 1930s | 11 | 9/11 = 0.818 [0.523, 0.949] | 9/11 = 0.818 [0.523, 0.949] |
| scdb8_disp | 1940s | 8 | 6/8 = 0.750 [0.409, 0.928] | 6/8 = 0.750 [0.409, 0.928] |
| scdb8_disp | 1950s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| scdb8_disp | 1960s | 11 | 8/11 = 0.727 [0.434, 0.902] | 8/11 = 0.727 [0.434, 0.902] |
| scdb8_disp | 1970s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| scdb8_disp | 1980s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| scdb8_disp | 1990s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb8_disp | 2000s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb8_disp | 2010s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| scdb8_disp | 2020s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| scdb8_disp | modified | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| scdb8_disp | reversed | 72 | 63/72 = 0.875 [0.779, 0.933] | 63/72 = 0.875 [0.779, 0.933] |
| scdb8_disp | vacated | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| scdb8_disp | stratum fed|1850s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| scdb8_disp | stratum fed|1880s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_disp | stratum fed|1890s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| scdb8_disp | stratum fed|1900s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| scdb8_disp | stratum fed|1910s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scdb8_disp | stratum fed|1920s (population 7, sampled 7) | 7 | 6/7 | 6/7 |
| scdb8_disp | stratum fed|1930s (population 12, sampled 11) | 11 | 9/11 | 9/11 |
| scdb8_disp | stratum fed|1940s (population 8, sampled 8) | 8 | 6/8 | 6/8 |
| scdb8_disp | stratum fed|1950s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| scdb8_disp | stratum fed|1960s (population 14, sampled 11) | 11 | 8/11 | 8/11 |
| scdb8_disp | stratum fed|1970s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| scdb8_disp | stratum fed|1980s (population 6, sampled 6) | 6 | 4/6 | 4/6 |
| scdb8_disp | stratum fed|1990s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb8_disp | stratum fed|2000s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb8_disp | stratum fed|2010s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| scdb8_disp | stratum fed|2020s (population 2, sampled 2) | 2 | 1/2 | 1/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (25 lines).
