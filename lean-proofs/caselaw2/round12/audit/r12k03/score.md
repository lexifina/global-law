# Blind audit score: r12k03 (type B)

- items in the key: 19 (17 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 19; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| shSub | 17 | 17 | 13/17 = 0.765 [0.527, 0.904] | 13/17 = 0.765 [0.527, 0.904] | 13/17 = 0.765 [0.527, 0.904] | 13/17 = 0.765 [0.527, 0.904] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- shSub: right 0.765 [0.765, 0.765] (read in full); right + extent 0.765 [0.765, 0.765] (read in full)

Answers on sampled rows (every reader): shSub: none 7, reversed_or_vacated_in_part 2, vacated 25

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): shSub: link 7

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10f12:fjc10b_xs | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 19 | 13/17 = 0.765 [0.527, 0.904] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 19 | 14/17 = 0.824 [0.590, 0.938] | 2/2 = 1.000 [0.342, 1.000] | 0 | 1 |

Items read twice: 19; same right answer 18/19 = 0.947 [0.754, 0.991]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| shSub | fed | 17 | 13/17 = 0.765 [0.527, 0.904] | 13/17 = 0.765 [0.527, 0.904] |
| shSub | 2000s | 13 | 10/13 = 0.769 [0.497, 0.918] | 10/13 = 0.769 [0.497, 0.918] |
| shSub | 2020s | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| shSub | vacated | 17 | 13/17 = 0.765 [0.527, 0.904] | 13/17 = 0.765 [0.527, 0.904] |
| shSub | stratum fed|2000s (population 13, sampled 13) | 13 | 10/13 | 10/13 |
| shSub | stratum fed|2020s (population 4, sampled 4) | 4 | 3/4 | 3/4 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (7 lines).
