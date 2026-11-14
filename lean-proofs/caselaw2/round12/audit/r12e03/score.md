# Blind audit score: r12e03 (type B)

- items in the key: 8 (6 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 8; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| enbanc12_op12 | 7 | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- enbanc12_op12: right 0.833 [0.694, 0.917] (n_eff 42); right + extent 0.833 [0.694, 0.917] (n_eff 42)

Answers on sampled rows (every reader): enbanc12_op12: none 2, vacated 10

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): enbanc12_op12: link 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r11:r11t05:stlink_u2wide | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 8 | 5/6 = 0.833 [0.436, 0.970] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 8 | 5/6 = 0.833 [0.436, 0.970] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 8; same right answer 8/8 = 1.000 [0.676, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| enbanc12_op12 | fed | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| enbanc12_op12 | 2020s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| enbanc12_op12 | vacated | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| enbanc12_op12 | stratum fed|2020s (population 7, sampled 6) | 6 | 5/6 | 5/6 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
