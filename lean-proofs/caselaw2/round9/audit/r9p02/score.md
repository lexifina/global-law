# Blind audit score: r9p02 (type B)

- items in the key: 40 (36 sampled rows, 2 known-wrong decoys, 2 known-right decoys); answered: 40; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| PJH | 36 | 36 | 26/36 = 0.722 [0.560, 0.842] | 25/36 = 0.694 [0.531, 0.820] | 33/36 = 0.917 [0.782, 0.971] | 26/36 = 0.722 [0.560, 0.842] | BELOW 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- PJH: right 0.722 [0.722, 0.722] (read in full); right + extent 0.694 [0.694, 0.694] (read in full)

Answers on sampled rows (every reader): PJH: affirmed 28, none 6, reversed 10, reversed_or_vacated_in_part 28

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): PJH: kind 14, link 6, scope 2

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 8/8 = 1.000 [0.676, 1.000]
- known wrong, not confirmed: 4/4 = 1.000 [0.510, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 8/8 = 1.000 [0.676, 1.000] | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |

| per decoy family | accuracy |
|---|---|
| r7:r7a10:oh | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a12:ohv | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a15:b4e_rp | 2/2 = 1.000 [0.342, 1.000] |
| r7:r7a19:rh_sil | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 40 | 26/36 = 0.722 [0.560, 0.842] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 40 | 26/36 = 0.722 [0.560, 0.842] | 4/4 = 1.000 [0.510, 1.000] | 0 | 0 |

Items read twice: 40; same right answer 40/40 = 1.000 [0.912, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| PJH | fed | 36 | 26/36 = 0.722 [0.560, 0.842] | 25/36 = 0.694 [0.531, 0.820] |
| PJH | 1990s | 5 | 2/5 = 0.400 [0.118, 0.769] | 2/5 = 0.400 [0.118, 0.769] |
| PJH | 2000s | 17 | 12/17 = 0.706 [0.469, 0.867] | 12/17 = 0.706 [0.469, 0.867] |
| PJH | 2010s | 14 | 12/14 = 0.857 [0.601, 0.960] | 11/14 = 0.786 [0.524, 0.924] |
| PJH | affirmed | 19 | 13/19 = 0.684 [0.460, 0.846] | 12/19 = 0.632 [0.410, 0.808] |
| PJH | reversed | 14 | 12/14 = 0.857 [0.601, 0.960] | 12/14 = 0.857 [0.601, 0.960] |
| PJH | reviewDismissed | 1 | 0/1 = 0.000 [0.000, 0.793] | 0/1 = 0.000 [0.000, 0.793] |
| PJH | vacated | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| PJH | stratum fed|1990s (population 5, sampled 5) | 5 | 2/5 | 2/5 |
| PJH | stratum fed|2000s (population 17, sampled 17) | 17 | 12/17 | 12/17 |
| PJH | stratum fed|2010s (population 14, sampled 14) | 14 | 12/14 | 11/14 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (22 lines).
