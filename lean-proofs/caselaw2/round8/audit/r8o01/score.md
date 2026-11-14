# Blind audit score: r8o01 (type A)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| o1 | 677 | 80 | 76/80 = 0.950 [0.878, 0.980] | 76/80 = 0.950 [0.878, 0.980] | 79/80 = 0.988 [0.932, 0.998] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- o1: right 0.854 [0.687, 0.940] (n_eff 30); right + extent 0.854 [0.687, 0.940] (n_eff 30)

Answers on sampled rows (every reader): o1: limit 5, nothing 2, overrule 98, reject_doctrine 55

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): o1: act 5, x+own+act 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 18/18 = 1.000 [0.824, 1.000]
- known wrong, not confirmed: 12/12 = 1.000 [0.757, 1.000]
- known right, confirmed: 6/6 = 1.000 [0.610, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_3 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:recog1:control-self | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-read-whole | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-round4 | 2/2 = 1.000 [0.342, 1.000] |
| r5:test_it0:recognised | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a01:opwpart | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a02:opwwhole | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a07:ante | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a08:sc | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a09:scctl | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 25/27 = 0.926 [0.766, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 26/27 = 0.963 [0.817, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 25/26 = 0.962 [0.811, 0.993] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 88/89 = 0.989 [0.939, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| o1 | fed | 40 | 40/40 = 1.000 [0.912, 1.000] | 40/40 = 1.000 [0.912, 1.000] |
| o1 | state | 40 | 36/40 = 0.900 [0.769, 0.960] | 36/40 = 0.900 [0.769, 0.960] |
| o1 | 1880s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| o1 | 1900s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| o1 | 1910s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| o1 | 1920s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| o1 | 1930s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| o1 | 1940s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| o1 | 1950s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| o1 | 1960s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| o1 | 1970s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| o1 | 1980s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| o1 | 1990s | 8 | 8/8 = 1.000 [0.676, 1.000] | 8/8 = 1.000 [0.676, 1.000] |
| o1 | 2000s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| o1 | 2010s | 8 | 7/8 = 0.875 [0.529, 0.978] | 7/8 = 0.875 [0.529, 0.978] |
| o1 | own_part | 75 | 71/75 = 0.947 [0.871, 0.979] | 71/75 = 0.947 [0.871, 0.979] |
| o1 | own_whole | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| o1 | stratum fed|1930s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| o1 | stratum fed|1940s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| o1 | stratum fed|1950s (population 8, sampled 5) | 5 | 5/5 | 5/5 |
| o1 | stratum fed|1960s (population 7, sampled 5) | 5 | 5/5 | 5/5 |
| o1 | stratum fed|1970s (population 34, sampled 5) | 5 | 5/5 | 5/5 |
| o1 | stratum fed|1980s (population 35, sampled 5) | 5 | 5/5 | 5/5 |
| o1 | stratum fed|1990s (population 56, sampled 5) | 5 | 5/5 | 5/5 |
| o1 | stratum fed|2000s (population 34, sampled 5) | 5 | 5/5 | 5/5 |
| o1 | stratum fed|2010s (population 11, sampled 4) | 4 | 4/4 | 4/4 |
| o1 | stratum state|1880s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| o1 | stratum state|1900s (population 7, sampled 3) | 3 | 3/3 | 3/3 |
| o1 | stratum state|1910s (population 9, sampled 3) | 3 | 3/3 | 3/3 |
| o1 | stratum state|1920s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| o1 | stratum state|1930s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| o1 | stratum state|1940s (population 7, sampled 3) | 3 | 3/3 | 3/3 |
| o1 | stratum state|1950s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| o1 | stratum state|1960s (population 11, sampled 4) | 4 | 4/4 | 4/4 |
| o1 | stratum state|1970s (population 38, sampled 3) | 3 | 2/3 | 2/3 |
| o1 | stratum state|1980s (population 74, sampled 3) | 3 | 2/3 | 2/3 |
| o1 | stratum state|1990s (population 127, sampled 3) | 3 | 3/3 | 3/3 |
| o1 | stratum state|2000s (population 131, sampled 3) | 3 | 2/3 | 2/3 |
| o1 | stratum state|2010s (population 71, sampled 4) | 4 | 3/4 | 3/4 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (7 lines).
