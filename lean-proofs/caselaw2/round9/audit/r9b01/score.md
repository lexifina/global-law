# Blind audit score: r9b01 (type B)

- items in the key: 34 (30 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 34; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb9_judg | 30 | 30 | 26/30 = 0.867 [0.703, 0.947] | 26/30 = 0.867 [0.703, 0.947] | 29/30 = 0.967 [0.833, 0.994] | 27/30 = 0.900 [0.744, 0.965] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb9_judg: right 0.867 [0.867, 0.867] (read in full); right + extent 0.867 [0.867, 0.867] (read in full)

Answers on sampled rows (every reader): scdb9_judg: affirmed 8, none 2, reversed 16, reversed_or_vacated_in_part 4, vacated 30

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb9_judg: kind 4, kind (same status effect) 2, link 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/8 = 1.000 [0.676, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:a3:rehear/enbanc-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 34 | 26/30 = 0.867 [0.703, 0.947] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 34 | 26/30 = 0.867 [0.703, 0.947] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |

Items read twice: 34; same right answer 34/34 = 1.000 [0.898, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb9_judg | fed | 30 | 26/30 = 0.867 [0.703, 0.947] | 26/30 = 0.867 [0.703, 0.947] |
| scdb9_judg | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb9_judg | 1950s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb9_judg | 1960s | 11 | 9/11 = 0.818 [0.523, 0.949] | 9/11 = 0.818 [0.523, 0.949] |
| scdb9_judg | 1970s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| scdb9_judg | 1980s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb9_judg | 1990s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| scdb9_judg | 2000s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb9_judg | 2010s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb9_judg | 2020s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb9_judg | affirmed | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| scdb9_judg | reversed | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| scdb9_judg | vacated | 18 | 15/18 = 0.833 [0.608, 0.942] | 15/18 = 0.833 [0.608, 0.942] |
| scdb9_judg | stratum fed|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb9_judg | stratum fed|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb9_judg | stratum fed|1960s (population 11, sampled 11) | 11 | 9/11 | 9/11 |
| scdb9_judg | stratum fed|1970s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| scdb9_judg | stratum fed|1980s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| scdb9_judg | stratum fed|1990s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| scdb9_judg | stratum fed|2000s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb9_judg | stratum fed|2010s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb9_judg | stratum fed|2020s (population 2, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (8 lines).
