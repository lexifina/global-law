# Blind audit score: run_B (type B)  (SELF-TEST)

**Self-test of the audit tools**: synthetic input, answers written by the self-test. The numbers say nothing about any rule.

- items in the key: 16 (12 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 16; answer files: 3
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| selftest-hist | 80 | 12 | 8/12 = 0.667 [0.391, 0.862] | 8/12 = 0.667 [0.391, 0.862] | 8/12 = 0.667 [0.391, 0.862] | 8/12 = 0.667 [0.391, 0.862] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- selftest-hist: right 0.681 [0.335, 0.901] (n_eff 7); right + extent 0.681 [0.335, 0.901] (n_eff 7)

Answers on sampled rows (every reader): selftest-hist: modified 3, none 5, rehearing_en_banc_only 2, vacated 6, withdrawn_or_superseded 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): selftest-hist: link 5

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
| r6:r1:rehear/docket | 0/2 = 0.000 [0.000, 0.658] |
| r6:v1:below/other | 1/1 = 1.000 [0.206, 1.000] |
| r7:r7a20:rh_docket | 1/1 = 1.000 [0.206, 1.000] |
| r9:r9b02:scdb9_other | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 8 | 5/6 = 0.833 [0.436, 0.970] | 1/2 = 0.500 [0.095, 0.905] | 0 | 0 |
| ans_1_b.jsonl | 1 | 8 | 4/6 = 0.667 [0.300, 0.903] | 1/2 = 0.500 [0.095, 0.905] | 0 | 0 |
| ans_2.jsonl | 2 | 8 | 4/6 = 0.667 [0.300, 0.903] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 8; same right answer 7/8 = 0.875 [0.529, 0.978]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| selftest-hist | fed | 12 | 8/12 = 0.667 [0.391, 0.862] | 8/12 = 0.667 [0.391, 0.862] |
| selftest-hist | 1960s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| selftest-hist | 1970s | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| selftest-hist | 1980s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| selftest-hist | 1990s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| selftest-hist | 2000s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| selftest-hist | 2010s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| selftest-hist | modified | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| selftest-hist | rehearingEnBancGranted | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| selftest-hist | vacated | 4 | 3/4 = 0.750 [0.301, 0.954] | 3/4 = 0.750 [0.301, 0.954] |
| selftest-hist | withdrawn | 3 | 1/3 = 0.333 [0.061, 0.792] | 1/3 = 0.333 [0.061, 0.792] |
| selftest-hist | stratum fed|1960s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| selftest-hist | stratum fed|1970s (population 3, sampled 3) | 3 | 2/3 | 2/3 |
| selftest-hist | stratum fed|1980s (population 9, sampled 2) | 2 | 1/2 | 1/2 |
| selftest-hist | stratum fed|1990s (population 27, sampled 2) | 2 | 2/2 | 2/2 |
| selftest-hist | stratum fed|2000s (population 33, sampled 2) | 2 | 1/2 | 1/2 |
| selftest-hist | stratum fed|2010s (population 7, sampled 2) | 2 | 1/2 | 1/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (7 lines).
