# Blind audit score: r11t03 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_u2cited | 370 | 80 | 69/80 = 0.863 [0.770, 0.921] | 69/80 = 0.863 [0.770, 0.921] | 75/80 = 0.938 [0.862, 0.973] | 73/80 = 0.912 [0.830, 0.957] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_u2cited: right 0.851 [0.752, 0.915] (n_eff 73); right + extent 0.851 [0.752, 0.915] (n_eff 73)

Answers on sampled rows (every reader): stlink_u2cited: modified 10, none 9, other 2, reversed 108, reversed_or_vacated_in_part 20, vacated 11

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_u2cited: kind 4, kind (same status effect) 7, link 9

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
| r10:r10k03:capC9 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t01:stlink_s1 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t05:stlink_u1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a12:ohv | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_1_b.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |
| ans_2.jsonl | 2 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 87/89 = 0.978 [0.922, 0.994]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_u2cited | state | 80 | 69/80 = 0.863 [0.770, 0.921] | 69/80 = 0.863 [0.770, 0.921] |
| stlink_u2cited | 1930s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| stlink_u2cited | 1940s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| stlink_u2cited | 1950s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2cited | 1960s | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| stlink_u2cited | 1970s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| stlink_u2cited | 1980s | 13 | 12/13 = 0.923 [0.667, 0.986] | 12/13 = 0.923 [0.667, 0.986] |
| stlink_u2cited | 1990s | 13 | 10/13 = 0.769 [0.497, 0.918] | 10/13 = 0.769 [0.497, 0.918] |
| stlink_u2cited | 2000s | 13 | 11/13 = 0.846 [0.578, 0.957] | 11/13 = 0.846 [0.578, 0.957] |
| stlink_u2cited | 2010s | 13 | 11/13 = 0.846 [0.578, 0.957] | 11/13 = 0.846 [0.578, 0.957] |
| stlink_u2cited | modified | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| stlink_u2cited | reversed | 66 | 61/66 = 0.924 [0.835, 0.967] | 61/66 = 0.924 [0.835, 0.967] |
| stlink_u2cited | vacated | 9 | 4/9 = 0.444 [0.189, 0.733] | 4/9 = 0.444 [0.189, 0.733] |
| stlink_u2cited | stratum state|1930s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| stlink_u2cited | stratum state|1940s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| stlink_u2cited | stratum state|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2cited | stratum state|1960s (population 13, sampled 13) | 13 | 12/13 | 12/13 |
| stlink_u2cited | stratum state|1970s (population 27, sampled 12) | 12 | 12/12 | 12/12 |
| stlink_u2cited | stratum state|1980s (population 55, sampled 13) | 13 | 12/13 | 12/13 |
| stlink_u2cited | stratum state|1990s (population 78, sampled 13) | 13 | 10/13 | 10/13 |
| stlink_u2cited | stratum state|2000s (population 111, sampled 13) | 13 | 11/13 | 11/13 |
| stlink_u2cited | stratum state|2010s (population 83, sampled 13) | 13 | 11/13 | 11/13 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (20 lines).
