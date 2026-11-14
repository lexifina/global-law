# Blind audit score: r13k01 (type B)

- items in the key: 17 (15 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 17; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| shadow13_D | 16 | 15 | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- shadow13_D: right 0.938 [0.894, 0.964] (n_eff 192); right + extent 0.938 [0.894, 0.964] (n_eff 192)

Answers on sampled rows (every reader): shadow13_D: none 2, vacated 28

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): shadow13_D: link 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a17:rh_eb | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 17 | 14/15 = 0.933 [0.702, 0.988] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 17 | 14/15 = 0.933 [0.702, 0.988] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 17; same right answer 17/17 = 1.000 [0.816, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| shadow13_D | fed | 15 | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] |
| shadow13_D | 1980s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| shadow13_D | 2000s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| shadow13_D | 2010s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| shadow13_D | 2020s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| shadow13_D | vacated | 15 | 14/15 = 0.933 [0.702, 0.988] | 14/15 = 0.933 [0.702, 0.988] |
| shadow13_D | stratum fed|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| shadow13_D | stratum fed|2000s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| shadow13_D | stratum fed|2010s (population 4, sampled 3) | 3 | 3/3 | 3/3 |
| shadow13_D | stratum fed|2020s (population 6, sampled 6) | 6 | 5/6 | 5/6 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
