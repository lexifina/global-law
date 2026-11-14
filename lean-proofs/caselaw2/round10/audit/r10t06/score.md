# Blind audit score: r10t06 (type B)

- items in the key: 38 (34 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 38; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| stlink_d2 | 34 | 34 | 34/34 = 1.000 [0.898, 1.000] | 34/34 = 1.000 [0.898, 1.000] | 34/34 = 1.000 [0.898, 1.000] | 34/34 = 1.000 [0.898, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- stlink_d2: right 1.000 [1.000, 1.000] (read in full); right + extent 1.000 [1.000, 1.000] (read in full)

Answers on sampled rows (every reader): stlink_d2: reversed 50, reversed_or_vacated_in_part 12, vacated 6

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): stlink_d2: none

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/8 = 1.000 [0.676, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a20:rh_docket | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 38 | 34/34 = 1.000 [0.898, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 38 | 34/34 = 1.000 [0.898, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |

Items read twice: 38; same right answer 38/38 = 1.000 [0.908, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| stlink_d2 | state | 34 | 34/34 = 1.000 [0.898, 1.000] | 34/34 = 1.000 [0.898, 1.000] |
| stlink_d2 | 1970s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| stlink_d2 | 1980s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| stlink_d2 | 1990s | 12 | 12/12 = 1.000 [0.757, 1.000] | 12/12 = 1.000 [0.757, 1.000] |
| stlink_d2 | 2000s | 11 | 11/11 = 1.000 [0.741, 1.000] | 11/11 = 1.000 [0.741, 1.000] |
| stlink_d2 | 2010s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| stlink_d2 | reversed | 31 | 31/31 = 1.000 [0.890, 1.000] | 31/31 = 1.000 [0.890, 1.000] |
| stlink_d2 | vacated | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| stlink_d2 | stratum state|1970s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| stlink_d2 | stratum state|1980s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| stlink_d2 | stratum state|1990s (population 12, sampled 12) | 12 | 12/12 | 12/12 |
| stlink_d2 | stratum state|2000s (population 11, sampled 11) | 11 | 11/11 | 11/11 |
| stlink_d2 | stratum state|2010s (population 2, sampled 2) | 2 | 2/2 | 2/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (0 lines).
