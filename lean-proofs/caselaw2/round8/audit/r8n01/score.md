# Blind audit score: r8n01 (type A)

- items in the key: 45 (39 sampled rows, 4 known-wrong decoys, 2 known-right decoys); answered: 45; answer files: 4
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| NT8 | 39 | 39 | 38/39 = 0.974 [0.868, 0.996] | 38/39 = 0.974 [0.868, 0.996] | 39/39 = 1.000 [0.910, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- NT8: right 0.974 [0.974, 0.974] (read in full); right + extent 0.974 [0.974, 0.974] (read in full)

Answers on sampled rows (every reader): NT8: limit 2, overrule 74, reject_doctrine 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): NT8: act 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 12/12 = 1.000 [0.757, 1.000]
- known wrong, not confirmed: 8/8 = 1.000 [0.676, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:operative-part | 2/2 = 1.000 [0.342, 1.000] |
| r5:recog1:recog-round4 | 2/2 = 1.000 [0.342, 1.000] |
| r5:test_it0:recognised | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a07:ante | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a08:sc | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a09:scctl | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 23 | 19/20 = 0.950 [0.764, 0.991] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 23 | 19/20 = 0.950 [0.764, 0.991] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 22 | 19/19 = 1.000 [0.832, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 22 | 19/19 = 1.000 [0.832, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 45; same right answer 45/45 = 1.000 [0.921, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| NT8 | fed | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| NT8 | state | 37 | 36/37 = 0.973 [0.862, 0.995] | 36/37 = 0.973 [0.862, 0.995] |
| NT8 | 1900s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| NT8 | 1910s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| NT8 | 1920s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| NT8 | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| NT8 | 1940s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| NT8 | 1950s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| NT8 | 1960s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| NT8 | 1970s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| NT8 | 1980s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| NT8 | 1990s | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| NT8 | 2000s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| NT8 | 2010s | 5 | 5/5 = 1.000 [0.566, 1.000] | 5/5 = 1.000 [0.566, 1.000] |
| NT8 | 2020s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| NT8 | own_part | 27 | 26/27 = 0.963 [0.817, 0.993] | 26/27 = 0.963 [0.817, 0.993] |
| NT8 | own_whole | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| NT8 | stratum fed|2020s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| NT8 | stratum state|1900s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| NT8 | stratum state|1910s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| NT8 | stratum state|1920s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| NT8 | stratum state|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| NT8 | stratum state|1940s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| NT8 | stratum state|1950s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| NT8 | stratum state|1960s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| NT8 | stratum state|1970s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| NT8 | stratum state|1980s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| NT8 | stratum state|1990s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| NT8 | stratum state|2000s (population 6, sampled 6) | 6 | 6/6 | 6/6 |
| NT8 | stratum state|2010s (population 5, sampled 5) | 5 | 5/5 | 5/5 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (2 lines).
