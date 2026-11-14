# Blind audit score: r11k04 (type B)

- items in the key: 32 (28 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 32; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| ol2 | 28 | 28 | 27/28 = 0.964 [0.823, 0.994] | 27/28 = 0.964 [0.823, 0.994] | 27/28 = 0.964 [0.823, 0.994] | 27/28 = 0.964 [0.823, 0.994] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- ol2: right 0.964 [0.964, 0.964] (read in full); right + extent 0.964 [0.964, 0.964] (read in full)

Answers on sampled rows (every reader): ol2: none 2, vacated 54

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): ol2: link 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/8 = 1.000 [0.676, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10t01:stlink_s1 | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k02:remandtext2 | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 32 | 27/28 = 0.964 [0.823, 0.994] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 32 | 27/28 = 0.964 [0.823, 0.994] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |

Items read twice: 32; same right answer 32/32 = 1.000 [0.893, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| ol2 | fed | 28 | 27/28 = 0.964 [0.823, 0.994] | 27/28 = 0.964 [0.823, 0.994] |
| ol2 | 2010s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| ol2 | 2020s | 27 | 26/27 = 0.963 [0.817, 0.993] | 26/27 = 0.963 [0.817, 0.993] |
| ol2 | vacated | 28 | 27/28 = 0.964 [0.823, 0.994] | 27/28 = 0.964 [0.823, 0.994] |
| ol2 | stratum fed|2010s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| ol2 | stratum fed|2020s (population 27, sampled 27) | 27 | 26/27 | 26/27 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
