# Blind audit score: r10b01 (type B)

- items in the key: 85 (75 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 85; answer files: 4
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb10_a10 | 75 | 75 | 70/75 = 0.933 [0.853, 0.971] | 70/75 = 0.933 [0.853, 0.971] | 73/75 = 0.973 [0.908, 0.993] | 70/75 = 0.933 [0.853, 0.971] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb10_a10: right 0.933 [0.933, 0.933] (read in full); right + extent 0.933 [0.933, 0.933] (read in full)

Answers on sampled rows (every reader): scdb10_a10: affirmed 40, none 4, reversed 86, reversed_or_vacated_in_part 8, review_dismissed 4, vacated 8

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb10_a10: kind 6, link 4

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 18/20 = 0.900 [0.699, 0.972]
- known wrong, not confirmed: 10/12 = 0.833 [0.552, 0.953]
- known right, confirmed: 8/8 = 1.000 [0.676, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/10 = 0.800 [0.490, 0.943] | 4/6 = 0.667 [0.300, 0.903] | 4/4 = 1.000 [0.510, 1.000] |
| pack_2 | 10/10 = 1.000 [0.723, 1.000] | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:below/sc | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/sc_a1 | 0/2 = 0.000 [0.000, 0.658] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p02:PJH | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 43 | 36/38 = 0.947 [0.827, 0.985] | 4/5 = 0.800 [0.376, 0.964] | 0 | 0 |
| ans_1_b.jsonl | 1 | 43 | 36/38 = 0.947 [0.827, 0.985] | 4/5 = 0.800 [0.376, 0.964] | 0 | 0 |
| ans_2.jsonl | 2 | 42 | 34/37 = 0.919 [0.787, 0.972] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 42 | 34/37 = 0.919 [0.787, 0.972] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

Items read twice: 85; same right answer 85/85 = 1.000 [0.957, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb10_a10 | fed | 75 | 70/75 = 0.933 [0.853, 0.971] | 70/75 = 0.933 [0.853, 0.971] |
| scdb10_a10 | 1910s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb10_a10 | 1930s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| scdb10_a10 | 1940s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| scdb10_a10 | 1950s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| scdb10_a10 | 1960s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| scdb10_a10 | 1970s | 19 | 16/19 = 0.842 [0.624, 0.945] | 16/19 = 0.842 [0.624, 0.945] |
| scdb10_a10 | 1980s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| scdb10_a10 | 1990s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| scdb10_a10 | 2000s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb10_a10 | 2010s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb10_a10 | affirmed | 24 | 20/24 = 0.833 [0.641, 0.933] | 20/24 = 0.833 [0.641, 0.933] |
| scdb10_a10 | reversed | 45 | 44/45 = 0.978 [0.884, 0.996] | 44/45 = 0.978 [0.884, 0.996] |
| scdb10_a10 | reviewDismissed | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb10_a10 | vacated | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb10_a10 | stratum fed|1910s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| scdb10_a10 | stratum fed|1930s (population 8, sampled 8) | 8 | 7/8 | 7/8 |
| scdb10_a10 | stratum fed|1940s (population 9, sampled 9) | 9 | 9/9 | 9/9 |
| scdb10_a10 | stratum fed|1950s (population 10, sampled 10) | 10 | 10/10 | 10/10 |
| scdb10_a10 | stratum fed|1960s (population 8, sampled 8) | 8 | 8/8 | 8/8 |
| scdb10_a10 | stratum fed|1970s (population 19, sampled 19) | 19 | 16/19 | 16/19 |
| scdb10_a10 | stratum fed|1980s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| scdb10_a10 | stratum fed|1990s (population 8, sampled 8) | 8 | 8/8 | 8/8 |
| scdb10_a10 | stratum fed|2000s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scdb10_a10 | stratum fed|2010s (population 2, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (12 lines).
