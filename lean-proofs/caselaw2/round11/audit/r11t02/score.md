# Blind audit score: r11t02 (type B)

- items in the key: 12 (10 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 12; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_u2n | 10 | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] | 10/10 = 1.000 [0.723, 1.000] | 8/10 = 0.800 [0.490, 0.943] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_u2n: right 0.800 [0.800, 0.800] (read in full); right + extent 0.800 [0.800, 0.800] (read in full)

Answers on sampled rows (every reader): stlink_u2n: affirmed 1, modified 2, reversed 12, reversed_or_vacated_in_part 5

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_u2n: kind 3

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:v2:below/sc/sc_a1 | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a21:rh_sa | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 12 | 8/10 = 0.800 [0.490, 0.943] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 12 | 9/10 = 0.900 [0.596, 0.982] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 12; same right answer 11/12 = 0.917 [0.646, 0.985]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_u2n | state | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] |
| stlink_u2n | 1900s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2n | 1910s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| stlink_u2n | 1920s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| stlink_u2n | 1960s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2n | 1970s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| stlink_u2n | 1980s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2n | 2000s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2n | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_u2n | reversed | 9 | 7/9 = 0.778 [0.453, 0.937] | 7/9 = 0.778 [0.453, 0.937] |
| stlink_u2n | stratum state|1900s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2n | stratum state|1910s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| stlink_u2n | stratum state|1920s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| stlink_u2n | stratum state|1960s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2n | stratum state|1970s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| stlink_u2n | stratum state|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_u2n | stratum state|2000s (population 1, sampled 1) | 1 | 1/1 | 1/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (3 lines).
