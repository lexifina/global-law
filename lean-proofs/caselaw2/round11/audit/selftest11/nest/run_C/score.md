# Blind audit score: run_C (type C)  (SELF-TEST)

**Self-test of the audit tools**: synthetic input, answers written by the self-test. The numbers say nothing about any rule.

- items in the key: 16 (12 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 16; answer files: 2
- right: link and the disposition agrees with the kind of row 1 (row2_*: of row 2). right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | row 2 right | row 2 right + extent | row 2 link + effect | only row 1 right | only row 2 right | 0.90 rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| selftest-pair | 49 | 12 | 6/12 = 0.500 [0.254, 0.746] | 6/12 = 0.500 [0.254, 0.746] | 9/12 = 0.750 [0.468, 0.911] | 6/12 = 0.500 [0.254, 0.746] | 3/12 = 0.250 [0.089, 0.532] | 3/12 = 0.250 [0.089, 0.532] | 3/12 = 0.250 [0.089, 0.532] | 6/12 = 0.500 [0.254, 0.746] | 3/12 = 0.250 [0.089, 0.532] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- selftest-pair: right 0.347 [0.136, 0.641] (n_eff 10); right + extent 0.347 [0.136, 0.641] (n_eff 10)

Answers on sampled rows (every reader): selftest-pair: affirmed 3, none 3, rehearing_en_banc_only 1, reinstated 2, vacated 1, withdrawn_or_superseded 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): selftest-pair: kind 3, link; row 2: link 3

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 2/2 = 1.000 [0.342, 1.000] | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| pack_2 | 2/2 = 1.000 [0.342, 1.000] | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10b01:scdb10_a10 | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:decoy_base | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:memo/cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:v2:below/other | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 8 | 2/6 = 0.333 [0.097, 0.700] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 8 | 4/6 = 0.667 [0.300, 0.903] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| selftest-pair | fed | 12 | 6/12 = 0.500 [0.254, 0.746] | 6/12 = 0.500 [0.254, 0.746] |
| selftest-pair | 1970s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| selftest-pair | 1980s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| selftest-pair | 1990s | 3 | 0/3 = 0.000 [0.000, 0.561] | 0/3 = 0.000 [0.000, 0.561] |
| selftest-pair | 2000s | 3 | 1/3 = 0.333 [0.061, 0.792] | 1/3 = 0.333 [0.061, 0.792] |
| selftest-pair | 2010s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| selftest-pair | modified/unknown vs reversed/all | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| selftest-pair | rehearingEnBancGranted/all vs affirmed/all | 4 | 1/4 = 0.250 [0.046, 0.699] | 1/4 = 0.250 [0.046, 0.699] |
| selftest-pair | reinstated/all vs reversed/all | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| selftest-pair | reinstated/unknown vs reversed/all | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| selftest-pair | vacated/all vs affirmed/all | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| selftest-pair | withdrawn/all vs affirmed/all | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| selftest-pair | stratum fed|1970s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| selftest-pair | stratum fed|1980s (population 3, sampled 2) | 2 | 2/2 | 2/2 |
| selftest-pair | stratum fed|1990s (population 15, sampled 3) | 3 | 0/3 | 0/3 |
| selftest-pair | stratum fed|2000s (population 24, sampled 3) | 3 | 1/3 | 1/3 |
| selftest-pair | stratum fed|2010s (population 6, sampled 3) | 3 | 3/3 | 3/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (6 lines).
