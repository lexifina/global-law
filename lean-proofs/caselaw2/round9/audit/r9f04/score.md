# Blind audit score: r9f04 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc9J | 176 | 80 | 72/80 = 0.900 [0.815, 0.949] | 72/80 = 0.900 [0.815, 0.949] | 77/80 = 0.963 [0.895, 0.987] | 72/80 = 0.900 [0.815, 0.949] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc9J: right 0.917 [0.847, 0.957] (n_eff 102); right + extent 0.917 [0.847, 0.957] (n_eff 102)

Answers on sampled rows (every reader): fjc9J: modified 16, none 6, reversed 105, reversed_or_vacated_in_part 11, review_dismissed 4, vacated 18

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc9J: kind 9, link 6

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
| r6:a3:rehear/docket | 4/4 = 1.000 [0.510, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 23/27 = 0.852 [0.675, 0.941] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 1 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc9J | fed | 80 | 72/80 = 0.900 [0.815, 0.949] | 72/80 = 0.900 [0.815, 0.949] |
| fjc9J | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc9J | 1930s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| fjc9J | 1940s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc9J | 1950s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| fjc9J | 1960s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc9J | 1970s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc9J | 1980s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| fjc9J | 1990s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| fjc9J | 2000s | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| fjc9J | 2010s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| fjc9J | 2020s | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| fjc9J | modified | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| fjc9J | reversed | 58 | 55/58 = 0.948 [0.859, 0.982] | 55/58 = 0.948 [0.859, 0.982] |
| fjc9J | vacated | 14 | 10/14 = 0.714 [0.454, 0.883] | 10/14 = 0.714 [0.454, 0.883] |
| fjc9J | stratum fed|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| fjc9J | stratum fed|1930s (population 9, sampled 9) | 9 | 9/9 | 9/9 |
| fjc9J | stratum fed|1940s (population 19, sampled 9) | 9 | 8/9 | 8/9 |
| fjc9J | stratum fed|1950s (population 42, sampled 9) | 9 | 9/9 | 9/9 |
| fjc9J | stratum fed|1960s (population 17, sampled 9) | 9 | 8/9 | 8/9 |
| fjc9J | stratum fed|1970s (population 23, sampled 9) | 9 | 8/9 | 8/9 |
| fjc9J | stratum fed|1980s (population 28, sampled 9) | 9 | 8/9 | 8/9 |
| fjc9J | stratum fed|1990s (population 18, sampled 10) | 10 | 10/10 | 10/10 |
| fjc9J | stratum fed|2000s (population 13, sampled 9) | 9 | 7/9 | 7/9 |
| fjc9J | stratum fed|2010s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| fjc9J | stratum fed|2020s (population 2, sampled 2) | 2 | 0/2 | 0/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (15 lines).
