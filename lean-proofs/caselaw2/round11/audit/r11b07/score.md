# Blind audit score: r11b07 (type B)

- items in the key: 7 (5 sampled rows, 1 known-wrong decoys, 1 known-right decoys); answered: 7; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| scdb11_r4rm | 5 | 5 | 0/5 = 0.000 [0.000, 0.434] | 0/5 = 0.000 [0.000, 0.434] | 0/5 = 0.000 [0.000, 0.434] | 0/5 = 0.000 [0.000, 0.434] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- scdb11_r4rm: right 0.000 [0.000, 0.000] (read in full); right + extent 0.000 [0.000, 0.000] (read in full)

Answers on sampled rows (every reader): scdb11_r4rm: none 10

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): scdb11_r4rm: link 10

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 4/4 = 1.000 [0.510, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: 2/2 = 1.000 [0.342, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 4/4 = 1.000 [0.510, 1.000] | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r10:r10k03:capC9 | 2/2 = 1.000 [0.342, 1.000] |
| r6:a3:below/sc/weak2 | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 7 | 0/5 = 0.000 [0.000, 0.434] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 7 | 0/5 = 0.000 [0.000, 0.434] | 2/2 = 1.000 [0.342, 1.000] | 0 | 0 |

Items read twice: 7; same right answer 7/7 = 1.000 [0.646, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| scdb11_r4rm | fed | 5 | 0/5 = 0.000 [0.000, 0.434] | 0/5 = 0.000 [0.000, 0.434] |
| scdb11_r4rm | 1960s | 3 | 0/3 = 0.000 [0.000, 0.561] | 0/3 = 0.000 [0.000, 0.561] |
| scdb11_r4rm | 1970s | 2 | 0/2 = 0.000 [0.000, 0.658] | 0/2 = 0.000 [0.000, 0.658] |
| scdb11_r4rm | reversed | 5 | 0/5 = 0.000 [0.000, 0.434] | 0/5 = 0.000 [0.000, 0.434] |
| scdb11_r4rm | stratum fed|1960s (population 3, sampled 3) | 3 | 0/3 | 0/3 |
| scdb11_r4rm | stratum fed|1970s (population 2, sampled 2) | 2 | 0/2 | 0/2 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (10 lines).
