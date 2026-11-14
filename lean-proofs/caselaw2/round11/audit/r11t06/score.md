# Blind audit score: r11t06 (type B)

- items in the key: 47 (41 sampled rows, 4 known-wrong decoys, 2 known-right decoys); answered: 47; answer files: 4
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_u2parse | 41 | 41 | 34/41 = 0.829 [0.687, 0.915] | 34/41 = 0.829 [0.687, 0.915] | 38/41 = 0.927 [0.806, 0.975] | 37/41 = 0.902 [0.774, 0.961] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_u2parse: right 0.829 [0.829, 0.829] (read in full); right + extent 0.829 [0.829, 0.829] (read in full)

Answers on sampled rows (every reader): stlink_u2parse: affirmed 2, modified 2, none 6, reversed 48, reversed_or_vacated_in_part 14, vacated 10

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_u2parse: kind 2, kind (same status effect) 6, link 6

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 11/12 = 0.917 [0.646, 0.985]
- known wrong, not confirmed: 7/8 = 0.875 [0.529, 0.978]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 5/6 = 0.833 [0.436, 0.970] | 3/4 = 0.750 [0.301, 0.954] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10b02:scdb10_a10t | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10f12:fjc10b_xs | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t01:stlink_s1 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10y01:syl10_RO_hist | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 1/2 = 0.500 [0.095, 0.905] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 24 | 19/21 = 0.905 [0.711, 0.974] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 24 | 19/21 = 0.905 [0.711, 0.974] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 23 | 15/20 = 0.750 [0.531, 0.888] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 23 | 15/20 = 0.750 [0.531, 0.888] | 2/3 = 0.667 [0.208, 0.939] | 0 | 1 |

Items read twice: 47; same right answer 46/47 = 0.979 [0.889, 0.996]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_u2parse | state | 41 | 34/41 = 0.829 [0.687, 0.915] | 34/41 = 0.829 [0.687, 0.915] |
| stlink_u2parse | 1890s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| stlink_u2parse | 1900s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2parse | 1970s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| stlink_u2parse | 1980s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| stlink_u2parse | 1990s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| stlink_u2parse | 2000s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| stlink_u2parse | 2010s | 11 | 7/11 = 0.636 [0.354, 0.848] | 7/11 = 0.636 [0.354, 0.848] |
| stlink_u2parse | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2parse | reversed | 34 | 28/34 = 0.824 [0.665, 0.916] | 28/34 = 0.824 [0.665, 0.916] |
| stlink_u2parse | vacated | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| stlink_u2parse | stratum state|1890s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| stlink_u2parse | stratum state|1900s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2parse | stratum state|1970s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| stlink_u2parse | stratum state|1980s (population 9, sampled 9) | 9 | 8/9 | 8/9 |
| stlink_u2parse | stratum state|1990s (population 12, sampled 12) | 12 | 12/12 | 12/12 |
| stlink_u2parse | stratum state|2000s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| stlink_u2parse | stratum state|2010s (population 11, sampled 11) | 11 | 7/11 | 7/11 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (15 lines).
