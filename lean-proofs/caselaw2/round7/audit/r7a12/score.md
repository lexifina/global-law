# Blind audit score: r7a12 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| ohv | 110 | 80 | 67/80 = 0.838 [0.742, 0.902] | 67/80 = 0.838 [0.742, 0.902] | 72/80 = 0.900 [0.815, 0.949] | 67/80 = 0.838 [0.742, 0.902] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- ohv: right 0.839 [0.793, 0.877] (n_eff 290); right + extent 0.839 [0.793, 0.877] (n_eff 290)

Answers on sampled rows (every reader): ohv: none 7, reversed_or_vacated_in_part 8, vacated 65

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): ohv: kind 5, link 8

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 10/10 = 1.000 [0.723, 1.000]
- known wrong, not confirmed: 6/6 = 1.000 [0.610, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 5/5 = 1.000 [0.566, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 5/5 = 1.000 [0.566, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:a3:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/enbanc-cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/panel-cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:below/other | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:memo/cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/sc/weak | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:memo/cap-2g | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 35/40 = 0.875 [0.739, 0.945] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 32/40 = 0.800 [0.652, 0.895] | 5/5 = 1.000 [0.566, 1.000] | 1 | 2 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| ohv | fed | 80 | 67/80 = 0.838 [0.742, 0.902] | 67/80 = 0.838 [0.742, 0.902] |
| ohv | 2010s | 77 | 65/77 = 0.844 [0.747, 0.908] | 65/77 = 0.844 [0.747, 0.908] |
| ohv | 2020s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| ohv | vacated | 80 | 67/80 = 0.838 [0.742, 0.902] | 67/80 = 0.838 [0.742, 0.902] |
| ohv | stratum fed|2010s (population 107, sampled 77) | 77 | 65/77 | 65/77 |
| ohv | stratum fed|2020s (population 3, sampled 3) | 3 | 2/3 | 2/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (13 lines).
