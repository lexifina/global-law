# Blind audit score: r9f02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc9W | 86 | 80 | 72/80 = 0.900 [0.815, 0.949] | 71/80 = 0.887 [0.800, 0.940] | 74/80 = 0.925 [0.846, 0.965] | 72/80 = 0.900 [0.815, 0.949] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc9W: right 0.904 [0.884, 0.921] (n_eff 1008); right + extent 0.889 [0.868, 0.907] (n_eff 1008)

Answers on sampled rows (every reader): fjc9W: affirmed 3, modified 6, none 10, reversed 88, reversed_or_vacated_in_part 35, vacated 18

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc9W: kind 5, link 10, scope 1

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
| r6:a3:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a15:b4e_rp | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |
| ans_2_b.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |
| ans_3.jsonl | 3 | 29 | 23/26 = 0.885 [0.710, 0.960] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |
| ans_3_b.jsonl | 3 | 29 | 22/26 = 0.846 [0.665, 0.939] | 3/3 = 1.000 [0.439, 1.000] | 0 | 2 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc9W | fed | 80 | 72/80 = 0.900 [0.815, 0.949] | 71/80 = 0.887 [0.800, 0.940] |
| fjc9W | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc9W | 1940s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| fjc9W | 1950s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| fjc9W | 1960s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| fjc9W | 1970s | 11 | 10/11 = 0.909 [0.623, 0.984] | 10/11 = 0.909 [0.623, 0.984] |
| fjc9W | 1980s | 12 | 9/12 = 0.750 [0.468, 0.911] | 9/12 = 0.750 [0.468, 0.911] |
| fjc9W | 1990s | 15 | 13/15 = 0.867 [0.621, 0.963] | 13/15 = 0.867 [0.621, 0.963] |
| fjc9W | 2000s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| fjc9W | 2010s | 15 | 15/15 = 1.000 [0.796, 1.000] | 14/15 = 0.933 [0.702, 0.988] |
| fjc9W | 2020s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| fjc9W | modified | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| fjc9W | reversed | 59 | 54/59 = 0.915 [0.817, 0.963] | 53/59 = 0.898 [0.795, 0.953] |
| fjc9W | vacated | 18 | 15/18 = 0.833 [0.608, 0.942] | 15/18 = 0.833 [0.608, 0.942] |
| fjc9W | stratum fed|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| fjc9W | stratum fed|1940s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| fjc9W | stratum fed|1950s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| fjc9W | stratum fed|1960s (population 8, sampled 8) | 8 | 8/8 | 8/8 |
| fjc9W | stratum fed|1970s (population 11, sampled 11) | 11 | 10/11 | 10/11 |
| fjc9W | stratum fed|1980s (population 12, sampled 12) | 12 | 9/12 | 9/12 |
| fjc9W | stratum fed|1990s (population 17, sampled 15) | 15 | 13/15 | 13/15 |
| fjc9W | stratum fed|2000s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| fjc9W | stratum fed|2010s (population 19, sampled 15) | 15 | 15/15 | 14/15 |
| fjc9W | stratum fed|2020s (population 2, sampled 2) | 2 | 1/2 | 1/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (16 lines).
