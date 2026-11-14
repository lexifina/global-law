# Blind audit score: r12e02 (type B)

- items in the key: 30 (27 sampled rows, 2 known-wrong decoys, 1 known-right decoys); answered: 30; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| enbanc12_eb12b | 101 | 27 | 26/27 = 0.963 [0.817, 0.993] | 26/27 = 0.963 [0.817, 0.993] | 26/27 = 0.963 [0.817, 0.993] | 26/27 = 0.963 [0.817, 0.993] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- enbanc12_eb12b: right 0.974 [0.846, 0.996] (n_eff 30); right + extent 0.974 [0.846, 0.996] (n_eff 30)

Answers on sampled rows (every reader): enbanc12_eb12b: none 2, vacated 52

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): enbanc12_eb12b: link 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 6/6 = 1.000 [0.610, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p02:PJH | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 30; same right answer 30/30 = 1.000 [0.886, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| enbanc12_eb12b | fed | 27 | 26/27 = 0.963 [0.817, 0.993] | 26/27 = 0.963 [0.817, 0.993] |
| enbanc12_eb12b | 1990s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| enbanc12_eb12b | 2020s | 17 | 16/17 = 0.941 [0.730, 0.990] | 16/17 = 0.941 [0.730, 0.990] |
| enbanc12_eb12b | vacated | 27 | 26/27 = 0.963 [0.817, 0.993] | 26/27 = 0.963 [0.817, 0.993] |
| enbanc12_eb12b | stratum fed|1990s (population 25, sampled 10) | 10 | 10/10 | 10/10 |
| enbanc12_eb12b | stratum fed|2020s (population 31, sampled 17) | 17 | 16/17 | 16/17 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
