# Blind audit score: run_A (type A)  (SELF-TEST)

**Self-test of the audit tools**: synthetic input, answers written by the self-test. The numbers say nothing about any rule.

- items in the key: 16 (12 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 16; answer files: 3
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| selftest-treat | 100 | 12 | 7/12 = 0.583 [0.320, 0.807] | 7/12 = 0.583 [0.320, 0.807] | 12/12 = 1.000 [0.757, 1.000] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- selftest-treat: right 0.850 [0.453, 0.975] (n_eff 6); right + extent 0.850 [0.453, 0.975] (n_eff 6)

Answers on sampled rows (every reader): selftest-treat: nothing 5, overrule 9, report_other 4

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): selftest-treat: by 2, own+act 5

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/6 = 0.667 [0.300, 0.903]
- known wrong, not confirmed: 1/3 = 0.333 [0.061, 0.792]
- known right, confirmed: 3/3 = 1.000 [0.439, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 2/4 = 0.500 [0.150, 0.850] | 0/2 = 0.000 [0.000, 0.658] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 2/2 = 1.000 [0.342, 1.000] | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |

| per decoy family | accuracy |
|---|---|
| r5:recog1:control-self | 1/1 = 1.000 [0.206, 1.000] |
| r7:r7a01:opwpart | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a09:scctl | 1/1 = 1.000 [0.206, 1.000] |
| r9:r9s02:S9A | 0/2 = 0.000 [0.000, 0.658] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 8 | 4/6 = 0.667 [0.300, 0.903] | 1/2 = 0.500 [0.095, 0.905] | 0 | 0 |
| ans_1_b.jsonl | 1 | 8 | 3/6 = 0.500 [0.188, 0.812] | 1/2 = 0.500 [0.095, 0.905] | 0 | 0 |
| ans_2.jsonl | 2 | 8 | 4/6 = 0.667 [0.300, 0.903] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 8; same right answer 7/8 = 0.875 [0.529, 0.978]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| selftest-treat | fed | 6 | 3/6 = 0.500 [0.188, 0.812] | 3/6 = 0.500 [0.188, 0.812] |
| selftest-treat | state | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| selftest-treat | 1910s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| selftest-treat | 1930s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| selftest-treat | 1950s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| selftest-treat | 1970s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| selftest-treat | 1980s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| selftest-treat | 1990s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| selftest-treat | 2000s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| selftest-treat | 2010s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| selftest-treat | 2020s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| selftest-treat | own_part | 9 | 6/9 = 0.667 [0.354, 0.879] | 6/9 = 0.667 [0.354, 0.879] |
| selftest-treat | own_whole | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| selftest-treat | report_part | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| selftest-treat | report_whole | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| selftest-treat | stratum fed|1970s (population 2, sampled 1) | 1 | 0/1 | 0/1 |
| selftest-treat | stratum fed|1980s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| selftest-treat | stratum fed|1990s (population 8, sampled 1) | 1 | 1/1 | 1/1 |
| selftest-treat | stratum fed|2000s (population 4, sampled 1) | 1 | 1/1 | 1/1 |
| selftest-treat | stratum fed|2010s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| selftest-treat | stratum fed|2020s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| selftest-treat | stratum state|1910s (population 6, sampled 1) | 1 | 1/1 | 1/1 |
| selftest-treat | stratum state|1930s (population 2, sampled 1) | 1 | 0/1 | 0/1 |
| selftest-treat | stratum state|1950s (population 6, sampled 1) | 1 | 0/1 | 0/1 |
| selftest-treat | stratum state|1980s (population 13, sampled 1) | 1 | 1/1 | 1/1 |
| selftest-treat | stratum state|2000s (population 13, sampled 1) | 1 | 1/1 | 1/1 |
| selftest-treat | stratum state|2010s (population 15, sampled 1) | 1 | 1/1 | 1/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (9 lines).
