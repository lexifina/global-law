# Blind audit score: r11b03 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 4
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb11_r2 | 196 | 80 | 41/80 = 0.512 [0.405, 0.619] | 41/80 = 0.512 [0.405, 0.619] | 44/80 = 0.550 [0.441, 0.654] | 41/80 = 0.512 [0.405, 0.619] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb11_r2: right 0.489 [0.397, 0.581] (n_eff 110); right + extent 0.489 [0.397, 0.581] (n_eff 110)

Answers on sampled rows (every reader): scdb11_r2: none 72, rehearing_en_banc_only 8, reinstated 4, reversed_or_vacated_in_part 1, vacated 73, withdrawn_or_superseded 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb11_r2: kind 5, link 72, scope 1

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 20/20 = 1.000 [0.839, 1.000]
- known wrong, not confirmed: 12/12 = 1.000 [0.757, 1.000]
- known right, confirmed: 8/8 = 1.000 [0.676, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 10/10 = 1.000 [0.723, 1.000] | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| pack_2 | 10/10 = 1.000 [0.723, 1.000] | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10f11:fjc10b_h | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10k03:capC9 | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/other | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p03:PJR | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 20/40 = 0.500 [0.352, 0.648] | 5/5 = 1.000 [0.566, 1.000] | 0 | 2 |
| ans_1_b.jsonl | 1 | 45 | 20/40 = 0.500 [0.352, 0.648] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 21/40 = 0.525 [0.375, 0.671] | 5/5 = 1.000 [0.566, 1.000] | 0 | 1 |
| ans_2_b.jsonl | 2 | 45 | 22/40 = 0.550 [0.398, 0.693] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

Items read twice: 90; same right answer 89/90 = 0.989 [0.940, 0.998]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb11_r2 | fed | 79 | 40/79 = 0.506 [0.398, 0.614] | 40/79 = 0.506 [0.398, 0.614] |
| scdb11_r2 | state | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb11_r2 | 1970s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb11_r2 | 1980s | 17 | 9/17 = 0.529 [0.310, 0.738] | 9/17 = 0.529 [0.310, 0.738] |
| scdb11_r2 | 1990s | 17 | 4/17 = 0.235 [0.096, 0.473] | 4/17 = 0.235 [0.096, 0.473] |
| scdb11_r2 | 2000s | 17 | 12/17 = 0.706 [0.469, 0.867] | 12/17 = 0.706 [0.469, 0.867] |
| scdb11_r2 | 2010s | 17 | 9/17 = 0.529 [0.310, 0.738] | 9/17 = 0.529 [0.310, 0.738] |
| scdb11_r2 | 2020s | 11 | 7/11 = 0.636 [0.354, 0.848] | 7/11 = 0.636 [0.354, 0.848] |
| scdb11_r2 | rehearingEnBancGranted | 40 | 20/40 = 0.500 [0.352, 0.648] | 20/40 = 0.500 [0.352, 0.648] |
| scdb11_r2 | vacated | 40 | 21/40 = 0.525 [0.375, 0.671] | 21/40 = 0.525 [0.375, 0.671] |
| scdb11_r2 | stratum fed|1970s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| scdb11_r2 | stratum fed|1980s (population 38, sampled 16) | 16 | 8/16 | 8/16 |
| scdb11_r2 | stratum fed|1990s (population 60, sampled 17) | 17 | 4/17 | 4/17 |
| scdb11_r2 | stratum fed|2000s (population 55, sampled 17) | 17 | 12/17 | 12/17 |
| scdb11_r2 | stratum fed|2010s (population 30, sampled 17) | 17 | 9/17 | 9/17 |
| scdb11_r2 | stratum fed|2020s (population 11, sampled 11) | 11 | 7/11 | 7/11 |
| scdb11_r2 | stratum state|1980s (population 1, sampled 1) | 1 | 1/1 | 1/1 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (78 lines).
