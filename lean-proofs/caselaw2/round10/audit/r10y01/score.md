# Blind audit score: r10y01 (type B)

- items in the key: 11 (9 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 11; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| syl10_RO_hist | 9 | 9 | 6/9 = 0.667 [0.354, 0.879] | 6/9 = 0.667 [0.354, 0.879] | 7/9 = 0.778 [0.453, 0.937] | 6/9 = 0.667 [0.354, 0.879] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- syl10_RO_hist: right 0.667 [0.667, 0.667] (read in full); right + extent 0.667 [0.667, 0.667] (read in full)

Answers on sampled rows (every reader): syl10_RO_hist: affirmed 6, none 4, reversed 2, reversed_or_vacated_in_part 2, vacated 4

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): syl10_RO_hist: kind 2, link 4

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:v2:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p02:PJH | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 11 | 6/9 = 0.667 [0.354, 0.879] | 2/2 = 1.000 [0.342, 1.000] | 1 | 1 |
| ans_1_b.jsonl | 1 | 11 | 6/9 = 0.667 [0.354, 0.879] | 2/2 = 1.000 [0.342, 1.000] | 1 | 1 |

Items read twice: 11; same right answer 11/11 = 1.000 [0.741, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| syl10_RO_hist | fed | 9 | 6/9 = 0.667 [0.354, 0.879] | 6/9 = 0.667 [0.354, 0.879] |
| syl10_RO_hist | 1980s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| syl10_RO_hist | 1990s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| syl10_RO_hist | 2000s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| syl10_RO_hist | 2010s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| syl10_RO_hist | 2020s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| syl10_RO_hist | affirmed | 5 | 3/5 = 0.600 [0.231, 0.882] | 3/5 = 0.600 [0.231, 0.882] |
| syl10_RO_hist | reversed | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| syl10_RO_hist | vacated | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| syl10_RO_hist | stratum fed|1980s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| syl10_RO_hist | stratum fed|1990s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| syl10_RO_hist | stratum fed|2000s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| syl10_RO_hist | stratum fed|2010s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| syl10_RO_hist | stratum fed|2020s (population 3, sampled 3) | 3 | 3/3 | 3/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (6 lines).
