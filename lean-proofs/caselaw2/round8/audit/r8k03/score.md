# Blind audit score: r8k03 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| kb_other | 6091 | 80 | 79/80 = 0.988 [0.932, 0.998] | 78/80 = 0.975 [0.913, 0.993] | 79/80 = 0.988 [0.932, 0.998] | 79/80 = 0.988 [0.932, 0.998] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- kb_other: right 1.000 [0.835, 1.000] (n_eff 20); right + extent 0.995 [0.827, 1.000] (n_eff 20)

Answers on sampled rows (every reader): kb_other: affirmed 4, review_denied 152, review_dismissed 4

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): kb_other: link 1, scope 2

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
| r6:a3:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 4/4 = 1.000 [0.510, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 1 | 1 |
| ans_2_b.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| kb_other | fed | 80 | 79/80 = 0.988 [0.932, 0.998] | 78/80 = 0.975 [0.913, 0.993] |
| kb_other | 1920s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| kb_other | 1930s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| kb_other | 1940s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| kb_other | 1950s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| kb_other | 1960s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| kb_other | 1970s | 8 | 8/8 = 1.000 [0.676, 1.000] | 7/8 = 0.875 [0.529, 0.978] |
| kb_other | 1980s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| kb_other | 1990s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| kb_other | 2000s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| kb_other | 2010s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| kb_other | 2020s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| kb_other | affirmed | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| kb_other | certDenied | 76 | 75/76 = 0.987 [0.929, 0.998] | 74/76 = 0.974 [0.909, 0.993] |
| kb_other | reviewDismissed | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| kb_other | stratum fed|1920s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| kb_other | stratum fed|1930s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| kb_other | stratum fed|1940s (population 15, sampled 8) | 8 | 7/8 | 7/8 |
| kb_other | stratum fed|1950s (population 30, sampled 7) | 7 | 7/7 | 7/7 |
| kb_other | stratum fed|1960s (population 71, sampled 8) | 8 | 8/8 | 8/8 |
| kb_other | stratum fed|1970s (population 227, sampled 8) | 8 | 8/8 | 7/8 |
| kb_other | stratum fed|1980s (population 466, sampled 8) | 8 | 8/8 | 8/8 |
| kb_other | stratum fed|1990s (population 771, sampled 8) | 8 | 8/8 | 8/8 |
| kb_other | stratum fed|2000s (population 665, sampled 8) | 8 | 8/8 | 8/8 |
| kb_other | stratum fed|2010s (population 3733, sampled 8) | 8 | 8/8 | 8/8 |
| kb_other | stratum fed|2020s (population 104, sampled 8) | 8 | 8/8 | 8/8 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (3 lines).
