# Blind audit score: r9s02 (type A)

- items in the key: 40 (36 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 40; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| S9A | 36 | 36 | 8/36 = 0.222 [0.117, 0.381] | 8/36 = 0.222 [0.117, 0.381] | 36/36 = 1.000 [0.904, 1.000] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- S9A: right 0.222 [0.222, 0.222] (read in full); right + extent 0.222 [0.222, 0.222] (read in full)

Answers on sampled rows (every reader): S9A: limit 26, nothing 4, other 10, overrule 8, reject_doctrine 17, report_other 7

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): S9A: act 42, own+act 4

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 6/8 = 0.750 [0.409, 0.928]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 2/4 = 0.500 [0.150, 0.850]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 6/8 = 0.750 [0.409, 0.928] | 4/4 = 1.000 [0.510, 1.000] | 2/4 = 0.500 [0.150, 0.850] |

| per decoy family | accuracy |
|---|---|
| r5:opw1:operative-whole | 0/2 = 0.000 [0.000, 0.658] |
| r7:r7a02:opwwhole | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a08:sc | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a09:scctl | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 40 | 8/36 = 0.222 [0.117, 0.381] | 3/4 = 0.750 [0.301, 0.954] | 0 | 0 |
| ans_1_b.jsonl | 1 | 40 | 18/36 = 0.500 [0.345, 0.655] | 3/4 = 0.750 [0.301, 0.954] | 0 | 3 |

Items read twice: 40; same right answer 30/40 = 0.750 [0.598, 0.858]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| S9A | fed | 16 | 4/16 = 0.250 [0.102, 0.495] | 4/16 = 0.250 [0.102, 0.495] |
| S9A | state | 20 | 4/20 = 0.200 [0.081, 0.416] | 4/20 = 0.200 [0.081, 0.416] |
| S9A | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| S9A | 1930s | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| S9A | 1950s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| S9A | 1960s | 3 | 1/3 = 0.333 [0.061, 0.792] | 1/3 = 0.333 [0.061, 0.792] |
| S9A | 1970s | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| S9A | 1980s | 10 | 3/10 = 0.300 [0.108, 0.603] | 3/10 = 0.300 [0.108, 0.603] |
| S9A | 1990s | 4 | 1/4 = 0.250 [0.046, 0.699] | 1/4 = 0.250 [0.046, 0.699] |
| S9A | 2000s | 6 | 2/6 = 0.333 [0.097, 0.700] | 2/6 = 0.333 [0.097, 0.700] |
| S9A | 2010s | 5 | 0/5 = 0.000 [0.000, 0.434] | 0/5 = 0.000 [0.000, 0.434] |
| S9A | 2020s | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| S9A | limit | 36 | 8/36 = 0.222 [0.117, 0.381] | 8/36 = 0.222 [0.117, 0.381] |
| S9A | stratum fed|1960s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| S9A | stratum fed|1970s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| S9A | stratum fed|1980s (population 5, sampled 5) | 5 | 2/5 | 2/5 |
| S9A | stratum fed|1990s (population 3, sampled 3) | 3 | 0/3 | 0/3 |
| S9A | stratum fed|2000s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9A | stratum fed|2010s (population 2, sampled 2) | 2 | 0/2 | 0/2 |
| S9A | stratum fed|2020s (population 2, sampled 2) | 2 | 0/2 | 0/2 |
| S9A | stratum state|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9A | stratum state|1930s (population 2, sampled 2) | 2 | 0/2 | 0/2 |
| S9A | stratum state|1950s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| S9A | stratum state|1960s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| S9A | stratum state|1970s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| S9A | stratum state|1980s (population 5, sampled 5) | 5 | 1/5 | 1/5 |
| S9A | stratum state|1990s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| S9A | stratum state|2000s (population 5, sampled 5) | 5 | 1/5 | 1/5 |
| S9A | stratum state|2010s (population 3, sampled 3) | 3 | 0/3 | 0/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (48 lines).
