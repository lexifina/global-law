# Blind audit score: r11k02 (type B)

- items in the key: 89 (80 sampled rows, 6 known-wrong decoys, 3 known-right decoys); answered: 89; answer files: 6
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| olC6 | 395 | 80 | 80/80 = 1.000 [0.954, 1.000] | 80/80 = 1.000 [0.954, 1.000] | 80/80 = 1.000 [0.954, 1.000] | 80/80 = 1.000 [0.954, 1.000] | ok |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- olC6: right 1.000 [0.962, 1.000] (n_eff 96); right + extent 1.000 [0.962, 1.000] (n_eff 96)

Answers on sampled rows (every reader): olC6: vacated 160

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): olC6: none

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
| r10:r10b03:scdb10_a10n | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10t06:stlink_d2 | 2/2 = 1.000 [0.342, 1.000] |
| r10:r10y01:syl10_RO_hist | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:decoy_wrong | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/caption | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:memo/cap-2g | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9b01:scdb9_judg | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f02:fjc9W | 2/2 = 1.000 [0.342, 1.000] |
| r9:r9f04:fjc9J | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_2_b.jsonl | 2 | 30 | 27/27 = 1.000 [0.875, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |
| ans_3_b.jsonl | 3 | 29 | 26/26 = 1.000 [0.871, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 0 | 0 |

Items read twice: 89; same right answer 89/89 = 1.000 [0.959, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| olC6 | fed | 80 | 80/80 = 1.000 [0.954, 1.000] | 80/80 = 1.000 [0.954, 1.000] |
| olC6 | 2000s | 40 | 40/40 = 1.000 [0.912, 1.000] | 40/40 = 1.000 [0.912, 1.000] |
| olC6 | 2020s | 40 | 40/40 = 1.000 [0.912, 1.000] | 40/40 = 1.000 [0.912, 1.000] |
| olC6 | vacated | 80 | 80/80 = 1.000 [0.954, 1.000] | 80/80 = 1.000 [0.954, 1.000] |
| olC6 | stratum fed|2000s (population 234, sampled 40) | 40 | 40/40 | 40/40 |
| olC6 | stratum fed|2020s (population 161, sampled 40) | 40 | 40/40 | 40/40 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (0 lines).
