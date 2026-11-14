# Blind audit score: r11b02 (type B)

- items in the key: 49 (44 sampled rows, 3 known-wrong decoys, 2 known-right decoys); answered: 49; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb11_r1rm | 45 | 44 | 0/44 = 0.000 [0.000, 0.080] | 0/44 = 0.000 [0.000, 0.080] | 0/44 = 0.000 [0.000, 0.080] | 0/44 = 0.000 [0.000, 0.080] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb11_r1rm: right 0.000 [0.000, 0.002] (n_eff 1841); right + extent 0.000 [0.000, 0.002] (n_eff 1841)

Answers on sampled rows (every reader): scdb11_r1rm: none 88

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb11_r1rm: link 88

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 10/10 = 1.000 [0.723, 1.000]
- known wrong, not confirmed: 6/6 = 1.000 [0.610, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 10/10 = 1.000 [0.723, 1.000] | 6/6 = 1.000 [0.610, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10k02:capC2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/self | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 49 | 0/44 = 0.000 [0.000, 0.080] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 49 | 0/44 = 0.000 [0.000, 0.080] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |

Items read twice: 49; same right answer 49/49 = 1.000 [0.927, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb11_r1rm | fed | 44 | 0/44 = 0.000 [0.000, 0.080] | 0/44 = 0.000 [0.000, 0.080] |
| scdb11_r1rm | 1960s | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| scdb11_r1rm | 1970s | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| scdb11_r1rm | 1980s | 10 | 0/10 = 0.000 [0.000, 0.278] | 0/10 = 0.000 [0.000, 0.278] |
| scdb11_r1rm | 1990s | 6 | 0/6 = 0.000 [0.000, 0.390] | 0/6 = 0.000 [0.000, 0.390] |
| scdb11_r1rm | 2000s | 12 | 0/12 = 0.000 [0.000, 0.242] | 0/12 = 0.000 [0.000, 0.242] |
| scdb11_r1rm | 2010s | 10 | 0/10 = 0.000 [0.000, 0.278] | 0/10 = 0.000 [0.000, 0.278] |
| scdb11_r1rm | 2020s | 3 | 0/3 = 0.000 [0.000, 0.561] | 0/3 = 0.000 [0.000, 0.561] |
| scdb11_r1rm | affirmed | 7 | 0/7 = 0.000 [0.000, 0.354] | 0/7 = 0.000 [0.000, 0.354] |
| scdb11_r1rm | reversed | 29 | 0/29 = 0.000 [0.000, 0.117] | 0/29 = 0.000 [0.000, 0.117] |
| scdb11_r1rm | vacated | 8 | 0/8 = 0.000 [0.000, 0.324] | 0/8 = 0.000 [0.000, 0.324] |
| scdb11_r1rm | stratum fed|1960s (population 2, sampled 2) | 2 | 0/2 | 0/2 |
| scdb11_r1rm | stratum fed|1970s (population 1, sampled 1) | 1 | 0/1 | 0/1 |
| scdb11_r1rm | stratum fed|1980s (population 11, sampled 10) | 10 | 0/10 | 0/10 |
| scdb11_r1rm | stratum fed|1990s (population 6, sampled 6) | 6 | 0/6 | 0/6 |
| scdb11_r1rm | stratum fed|2000s (population 12, sampled 12) | 12 | 0/12 | 0/12 |
| scdb11_r1rm | stratum fed|2010s (population 10, sampled 10) | 10 | 0/10 | 0/10 |
| scdb11_r1rm | stratum fed|2020s (population 3, sampled 3) | 3 | 0/3 | 0/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (88 lines).
