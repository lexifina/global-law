# Blind audit score: r8f03 (type B)

- items in the key: 33 (29 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 33; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| fjc8_s1 | 29 | 29 | 24/29 = 0.828 [0.654, 0.924] | 24/29 = 0.828 [0.654, 0.924] | 27/29 = 0.931 [0.780, 0.981] | 24/29 = 0.828 [0.654, 0.924] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- fjc8_s1: right 0.828 [0.828, 0.828] (read in full); right + extent 0.828 [0.828, 0.828] (read in full)

Answers on sampled rows (every reader): fjc8_s1: none 3, reversed 37, reversed_or_vacated_in_part 4, vacated 14

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): fjc8_s1: kind 4, link 3

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/8 = 1.000 [0.676, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a16:b4a_r3k | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 33 | 24/29 = 0.828 [0.654, 0.924] | 4/4 = 1.000 [0.510, 1.000] | 1 | 1 |
| ans_1_b.jsonl | 1 | 33 | 27/29 = 0.931 [0.780, 0.981] | 4/4 = 1.000 [0.510, 1.000] | 1 | 2 |

Items read twice: 33; same right answer 30/33 = 0.909 [0.764, 0.969]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| fjc8_s1 | fed | 29 | 24/29 = 0.828 [0.654, 0.924] | 24/29 = 0.828 [0.654, 0.924] |
| fjc8_s1 | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| fjc8_s1 | 1930s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| fjc8_s1 | 1950s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| fjc8_s1 | 1960s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| fjc8_s1 | 1970s | 7 | 6/7 = 0.857 [0.487, 0.974] | 6/7 = 0.857 [0.487, 0.974] |
| fjc8_s1 | 1980s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| fjc8_s1 | 1990s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| fjc8_s1 | 2000s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| fjc8_s1 | 2010s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| fjc8_s1 | reversed | 21 | 17/21 = 0.809 [0.600, 0.923] | 17/21 = 0.809 [0.600, 0.923] |
| fjc8_s1 | vacated | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| fjc8_s1 | stratum fed|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| fjc8_s1 | stratum fed|1930s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| fjc8_s1 | stratum fed|1950s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| fjc8_s1 | stratum fed|1960s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| fjc8_s1 | stratum fed|1970s (population 7, sampled 7) | 7 | 6/7 | 6/7 |
| fjc8_s1 | stratum fed|1980s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| fjc8_s1 | stratum fed|1990s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| fjc8_s1 | stratum fed|2000s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| fjc8_s1 | stratum fed|2010s (population 2, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (7 lines).
