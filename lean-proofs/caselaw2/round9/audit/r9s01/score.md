# Blind audit score: r9s01 (type A)

- items in the key: 58 (52 sampled rows, 4 known-wrong decoys, 2 known-right decoys); answered: 58; answer files: 6
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| S9B | 52 | 52 | 52/52 = 1.000 [0.931, 1.000] | 52/52 = 1.000 [0.931, 1.000] | 52/52 = 1.000 [0.931, 1.000] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- S9B: right 1.000 [1.000, 1.000] (read in full); right + extent 1.000 [1.000, 1.000] (read in full)

Answers on sampled rows (every reader): S9B: overrule 149, reject_doctrine 7

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): S9B: none

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 10/18 = 0.556 [0.337, 0.754]
- known wrong, not confirmed: 4/12 = 0.333 [0.138, 0.609]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/12 = 0.333 [0.138, 0.609] | 0/8 = 0.000 [0.000, 0.324] | 4/4 = 1.000 [0.510, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:control-self | 2/2 = 1.000 [0.342, 1.000] |
| r5:opw1:operative-part | 2/2 = 1.000 [0.342, 1.000] |
| r5:opw1:operative-whole | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-pattern | 0/4 = 0.000 [0.000, 0.490] |
| r7:r7a04:ante | 0/4 = 0.000 [0.000, 0.490] |
| r7:r7a11:dct | 4/4 = 1.000 [0.510, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 29 | 26/26 = 1.000 [0.871, 1.000] | 1/3 = 0.333 [0.061, 0.792] | 0 | 1 |
| ans_1_b.jsonl | 1 | 29 | 26/26 = 1.000 [0.871, 1.000] | 1/3 = 0.333 [0.061, 0.792] | 0 | 0 |
| ans_1_c.jsonl | 1 | 29 | 26/26 = 1.000 [0.871, 1.000] | 1/3 = 0.333 [0.061, 0.792] | 0 | 1 |
| ans_1_d.jsonl | 1 | 29 | 26/26 = 1.000 [0.871, 1.000] | 1/3 = 0.333 [0.061, 0.792] | 0 | 2 |
| ans_2.jsonl | 2 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 58; same right answer 58/58 = 1.000 [0.938, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| S9B | fed | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| S9B | state | 49 | 49/49 = 1.000 [0.927, 1.000] | 49/49 = 1.000 [0.927, 1.000] |
| S9B | 1870s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| S9B | 1890s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| S9B | 1900s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| S9B | 1910s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| S9B | 1920s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| S9B | 1930s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| S9B | 1940s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| S9B | 1950s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| S9B | 1960s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| S9B | 1970s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| S9B | 1980s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| S9B | 1990s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| S9B | 2000s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| S9B | own_part | 47 | 47/47 = 1.000 [0.924, 1.000] | 47/47 = 1.000 [0.924, 1.000] |
| S9B | own_whole | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| S9B | stratum fed|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9B | stratum fed|1990s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9B | stratum fed|2000s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9B | stratum state|1870s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9B | stratum state|1890s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| S9B | stratum state|1900s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9B | stratum state|1910s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| S9B | stratum state|1920s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| S9B | stratum state|1930s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| S9B | stratum state|1940s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| S9B | stratum state|1950s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| S9B | stratum state|1960s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| S9B | stratum state|1970s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| S9B | stratum state|1980s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| S9B | stratum state|1990s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| S9B | stratum state|2000s (population 2, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (8 lines).
