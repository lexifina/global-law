# Blind audit score: r8c01 (type C)

- items in the key: 46 (40 sampled rows, 4 known-wrong decoys, 2 known-right decoys); answered: 46; answer files: 4
- right: link and the disposition agrees with the kind of row 1 (row2_*: of row 2). right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | row 2 right | row 2 right + extent | row 2 link + effect | only row 1 right | only row 2 right | 0.90 rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| final_line | 245 | 40 | 27/40 = 0.675 [0.520, 0.799] | 27/40 = 0.675 [0.520, 0.799] | 39/40 = 0.975 [0.871, 0.996] | 27/40 = 0.675 [0.520, 0.799] | 7/40 = 0.175 [0.087, 0.320] | 7/40 = 0.175 [0.087, 0.320] | 7/40 = 0.175 [0.087, 0.320] | 27/40 = 0.675 [0.520, 0.799] | 7/40 = 0.175 [0.087, 0.320] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- final_line: right 0.582 [0.403, 0.741] (n_eff 29); right + extent 0.582 [0.403, 0.741] (n_eff 29)

Answers on sampled rows (every reader): final_line: affirmed 30, none 2, reversed 10, reversed_or_vacated_in_part 34, vacated 4

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): final_line: kind 14, kind; row 2: kind 10, link; row 2: link 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 12/12 = 1.000 [0.757, 1.000]
- known wrong, not confirmed: 8/8 = 1.000 [0.676, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 23 | 12/20 = 0.600 [0.387, 0.781] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 23 | 12/20 = 0.600 [0.387, 0.781] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 23 | 15/20 = 0.750 [0.531, 0.888] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 23 | 15/20 = 0.750 [0.531, 0.888] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 46; same right answer 46/46 = 1.000 [0.923, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| final_line | fed | 20 | 16/20 = 0.800 [0.584, 0.919] | 16/20 = 0.800 [0.584, 0.919] |
| final_line | state | 20 | 11/20 = 0.550 [0.342, 0.742] | 11/20 = 0.550 [0.342, 0.742] |
| final_line | 1910s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| final_line | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| final_line | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| final_line | 1940s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| final_line | 1950s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| final_line | 1960s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| final_line | 1970s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| final_line | 1980s | 6 | 3/6 = 0.500 [0.188, 0.812] | 3/6 = 0.500 [0.188, 0.812] |
| final_line | 1990s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| final_line | 2000s | 5 | 3/5 = 0.600 [0.231, 0.882] | 3/5 = 0.600 [0.231, 0.882] |
| final_line | 2010s | 5 | 3/5 = 0.600 [0.231, 0.882] | 3/5 = 0.600 [0.231, 0.882] |
| final_line | affirmed/all vs reversed/all | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| final_line | affirmed/unknown vs reversed/all | 14 | 7/14 = 0.500 [0.268, 0.732] | 7/14 = 0.500 [0.268, 0.732] |
| final_line | affirmed/unknown vs vacated/all | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| final_line | reversed/all vs affirmed/all | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| final_line | reversed/all vs certDenied/all | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| final_line | reversed/unknown vs affirmed/all | 14 | 11/14 = 0.786 [0.524, 0.924] | 11/14 = 0.786 [0.524, 0.924] |
| final_line | vacated/all vs certDenied/all | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| final_line | vacated/unknown vs affirmed/all | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| final_line | stratum fed|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| final_line | stratum fed|1940s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| final_line | stratum fed|1960s (population 7, sampled 3) | 3 | 2/3 | 2/3 |
| final_line | stratum fed|1970s (population 4, sampled 2) | 2 | 2/2 | 2/2 |
| final_line | stratum fed|1980s (population 29, sampled 3) | 3 | 1/3 | 1/3 |
| final_line | stratum fed|1990s (population 30, sampled 3) | 3 | 3/3 | 3/3 |
| final_line | stratum fed|2000s (population 13, sampled 3) | 3 | 3/3 | 3/3 |
| final_line | stratum fed|2010s (population 16, sampled 3) | 3 | 2/3 | 2/3 |
| final_line | stratum state|1910s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| final_line | stratum state|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| final_line | stratum state|1940s (population 4, sampled 2) | 2 | 2/2 | 2/2 |
| final_line | stratum state|1950s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| final_line | stratum state|1960s (population 7, sampled 3) | 3 | 2/3 | 2/3 |
| final_line | stratum state|1970s (population 23, sampled 2) | 2 | 1/2 | 1/2 |
| final_line | stratum state|1980s (population 35, sampled 3) | 3 | 2/3 | 2/3 |
| final_line | stratum state|1990s (population 29, sampled 2) | 2 | 1/2 | 1/2 |
| final_line | stratum state|2000s (population 26, sampled 2) | 2 | 0/2 | 0/2 |
| final_line | stratum state|2010s (population 15, sampled 2) | 2 | 1/2 | 1/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (26 lines).
