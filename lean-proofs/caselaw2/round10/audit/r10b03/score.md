# Blind audit score: r10b03 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 4
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb10_a10n | 81 | 80 | 66/80 = 0.825 [0.727, 0.893] | 62/80 = 0.775 [0.672, 0.853] | 73/80 = 0.912 [0.830, 0.957] | 66/80 = 0.825 [0.727, 0.893] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb10_a10n: right 0.825 [0.816, 0.835] (n_eff 6335); right + extent 0.775 [0.765, 0.785] (n_eff 6335)

Answers on sampled rows (every reader): scdb10_a10n: affirmed 58, modified 2, none 14, reversed 62, reversed_or_vacated_in_part 19, review_dismissed 2, vacated 3

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb10_a10n: kind 9, link 14, scope 12

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
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/weak | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a12:ohv | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f01:fjc9G | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k01:remandtext | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9p03:PJR | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 32/40 = 0.800 [0.652, 0.895] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 45 | 36/40 = 0.900 [0.769, 0.960] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 34/40 = 0.850 [0.709, 0.929] | 5/5 = 1.000 [0.566, 1.000] | 1 | 1 |
| ans_2_b.jsonl | 2 | 45 | 35/40 = 0.875 [0.739, 0.945] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

Items read twice: 90; same right answer 85/90 = 0.944 [0.876, 0.976]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb10_a10n | fed | 80 | 66/80 = 0.825 [0.727, 0.893] | 62/80 = 0.775 [0.672, 0.853] |
| scdb10_a10n | 1900s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb10_a10n | 1930s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb10_a10n | 1940s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| scdb10_a10n | 1950s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb10_a10n | 1960s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| scdb10_a10n | 1970s | 6 | 4/6 = 0.667 [0.300, 0.903] | 4/6 = 0.667 [0.300, 0.903] |
| scdb10_a10n | 1980s | 28 | 24/28 = 0.857 [0.685, 0.943] | 22/28 = 0.786 [0.605, 0.898] |
| scdb10_a10n | 1990s | 22 | 19/22 = 0.864 [0.667, 0.953] | 17/22 = 0.773 [0.566, 0.899] |
| scdb10_a10n | 2000s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| scdb10_a10n | 2010s | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] |
| scdb10_a10n | 2020s | 3 | 1/3 = 0.333 [0.061, 0.792] | 1/3 = 0.333 [0.061, 0.792] |
| scdb10_a10n | affirmed | 31 | 29/31 = 0.935 [0.793, 0.982] | 25/31 = 0.806 [0.637, 0.908] |
| scdb10_a10n | modified | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| scdb10_a10n | reversed | 45 | 34/45 = 0.756 [0.613, 0.858] | 34/45 = 0.756 [0.613, 0.858] |
| scdb10_a10n | vacated | 3 | 2/3 = 0.667 [0.208, 0.939] | 2/3 = 0.667 [0.208, 0.939] |
| scdb10_a10n | stratum fed|1900s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb10_a10n | stratum fed|1930s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb10_a10n | stratum fed|1940s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| scdb10_a10n | stratum fed|1950s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| scdb10_a10n | stratum fed|1960s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| scdb10_a10n | stratum fed|1970s (population 6, sampled 6) | 6 | 4/6 | 4/6 |
| scdb10_a10n | stratum fed|1980s (population 29, sampled 28) | 28 | 24/28 | 22/28 |
| scdb10_a10n | stratum fed|1990s (population 22, sampled 22) | 22 | 19/22 | 17/22 |
| scdb10_a10n | stratum fed|2000s (population 3, sampled 3) | 3 | 3/3 | 3/3 |
| scdb10_a10n | stratum fed|2010s (population 10, sampled 10) | 10 | 8/10 | 8/10 |
| scdb10_a10n | stratum fed|2020s (population 3, sampled 3) | 3 | 1/3 | 1/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (35 lines).
