# Blind audit score: r8k04 (type B)

- items in the key: 36 (32 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 36; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| kr_all | 32 | 32 | 32/32 = 1.000 [0.893, 1.000] | 32/32 = 1.000 [0.893, 1.000] | 32/32 = 1.000 [0.893, 1.000] | 32/32 = 1.000 [0.893, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- kr_all: right 1.000 [1.000, 1.000] (read in full); right + extent 1.000 [1.000, 1.000] (read in full)

Answers on sampled rows (every reader): kr_all: review_denied 14, vacated 50

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): kr_all: none

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/8 = 1.000 [0.676, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:r1:decoy_base | 2/2 = 1.000 [0.342, 1.000] |
| r6:v1:memo/cite | 2/2 = 1.000 [0.342, 1.000] |
| r6:v2:below/sc/hm | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a14:b4a_w | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 36 | 32/32 = 1.000 [0.893, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 36 | 32/32 = 1.000 [0.893, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |

Items read twice: 36; same right answer 36/36 = 1.000 [0.904, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| kr_all | fed | 32 | 32/32 = 1.000 [0.893, 1.000] | 32/32 = 1.000 [0.893, 1.000] |
| kr_all | 1960s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| kr_all | 1970s | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| kr_all | 1990s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| kr_all | 2010s | 27 | 27/27 = 1.000 [0.875, 1.000] | 27/27 = 1.000 [0.875, 1.000] |
| kr_all | certDenied | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| kr_all | vacated | 25 | 25/25 = 1.000 [0.867, 1.000] | 25/25 = 1.000 [0.867, 1.000] |
| kr_all | stratum fed|1960s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| kr_all | stratum fed|1970s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| kr_all | stratum fed|1990s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| kr_all | stratum fed|2010s (population 27, sampled 27) | 27 | 27/27 | 27/27 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (0 lines).
