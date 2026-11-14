# Blind audit score: r10t03 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_T | 322 | 80 | 61/80 = 0.762 [0.659, 0.842] | 61/80 = 0.762 [0.659, 0.842] | 79/80 = 0.988 [0.932, 0.998] | 74/80 = 0.925 [0.846, 0.965] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_T: right 0.699 [0.588, 0.791] (n_eff 75); right + extent 0.699 [0.588, 0.791] (n_eff 75)

Answers on sampled rows (every reader): stlink_T: affirmed 5, none 2, reversed 94, reversed_or_vacated_in_part 29, review_dismissed 1, vacated 29

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_T: kind 10, kind (same status effect) 17, link 2

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
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f03:fjc9G2 | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9k01:remandtext | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 22/27 = 0.815 [0.633, 0.918] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 24/27 = 0.889 [0.719, 0.962] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 19/27 = 0.704 [0.515, 0.842] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 20/26 = 0.769 [0.580, 0.890] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 24/26 = 0.923 [0.759, 0.979] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 80/89 = 0.899 [0.819, 0.946]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_T | state | 80 | 61/80 = 0.762 [0.659, 0.842] | 61/80 = 0.762 [0.659, 0.842] |
| stlink_T | 1910s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| stlink_T | 1930s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| stlink_T | 1940s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| stlink_T | 1950s | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] |
| stlink_T | 1960s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| stlink_T | 1970s | 11 | 9/11 = 0.818 [0.523, 0.949] | 9/11 = 0.818 [0.523, 0.949] |
| stlink_T | 1980s | 10 | 6/10 = 0.600 [0.313, 0.832] | 6/10 = 0.600 [0.313, 0.832] |
| stlink_T | 1990s | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] |
| stlink_T | 2000s | 10 | 6/10 = 0.600 [0.313, 0.832] | 6/10 = 0.600 [0.313, 0.832] |
| stlink_T | 2010s | 10 | 6/10 = 0.600 [0.313, 0.832] | 6/10 = 0.600 [0.313, 0.832] |
| stlink_T | reversed | 70 | 53/70 = 0.757 [0.645, 0.843] | 53/70 = 0.757 [0.645, 0.843] |
| stlink_T | vacated | 10 | 8/10 = 0.800 [0.490, 0.943] | 8/10 = 0.800 [0.490, 0.943] |
| stlink_T | stratum state|1910s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| stlink_T | stratum state|1930s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| stlink_T | stratum state|1940s (population 5, sampled 5) | 5 | 4/5 | 4/5 |
| stlink_T | stratum state|1950s (population 13, sampled 10) | 10 | 8/10 | 8/10 |
| stlink_T | stratum state|1960s (population 19, sampled 11) | 11 | 11/11 | 11/11 |
| stlink_T | stratum state|1970s (population 39, sampled 11) | 11 | 9/11 | 9/11 |
| stlink_T | stratum state|1980s (population 51, sampled 10) | 10 | 6/10 | 6/10 |
| stlink_T | stratum state|1990s (population 55, sampled 10) | 10 | 8/10 | 8/10 |
| stlink_T | stratum state|2000s (population 74, sampled 10) | 10 | 6/10 | 6/10 |
| stlink_T | stratum state|2010s (population 63, sampled 10) | 10 | 6/10 | 6/10 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (29 lines).
