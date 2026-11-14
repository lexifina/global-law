# Blind audit score: r7a10 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| oh | 8166 | 80 | 67/80 = 0.838 [0.742, 0.902] | 67/80 = 0.838 [0.742, 0.902] | 67/80 = 0.838 [0.742, 0.902] | 67/80 = 0.838 [0.742, 0.902] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- oh: right 0.871 [0.743, 0.940] (n_eff 45); right + extent 0.871 [0.743, 0.940] (n_eff 45)

Answers on sampled rows (every reader): oh: none 13, review_denied 63, review_dismissed 2, vacated 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): oh: link 13

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/10 = 0.800 [0.490, 0.943]
- known wrong, not confirmed: 4/6 = 0.667 [0.300, 0.903]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/5 = 0.800 [0.376, 0.964] | 2/3 = 0.667 [0.208, 0.939] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 4/5 = 0.800 [0.376, 0.964] | 2/3 = 0.667 [0.208, 0.939] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:a3:below/sc/weak2 | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:rehear/docket | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/docket | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/self | 0/1 = 0.000 [0.000, 0.793] |
| r6:v1:below/sc | 1/2 = 0.500 [0.095, 0.905] |
| r6:v1:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/sc/weak | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 34/40 = 0.850 [0.709, 0.929] | 4/5 = 0.800 [0.376, 0.964] | 0 | 1 |
| ans_2.jsonl | 2 | 45 | 33/40 = 0.825 [0.680, 0.912] | 4/5 = 0.800 [0.376, 0.964] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| oh | fed | 80 | 67/80 = 0.838 [0.742, 0.902] | 67/80 = 0.838 [0.742, 0.902] |
| oh | 2010s | 40 | 35/40 = 0.875 [0.739, 0.945] | 35/40 = 0.875 [0.739, 0.945] |
| oh | 2020s | 40 | 32/40 = 0.800 [0.652, 0.895] | 32/40 = 0.800 [0.652, 0.895] |
| oh | certDenied | 76 | 63/76 = 0.829 [0.729, 0.897] | 63/76 = 0.829 [0.729, 0.897] |
| oh | reviewDismissed | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| oh | vacated | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| oh | stratum fed|2010s (population 7714, sampled 40) | 40 | 35/40 | 35/40 |
| oh | stratum fed|2020s (population 452, sampled 40) | 40 | 32/40 | 32/40 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (15 lines).
