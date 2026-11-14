# Blind audit score: r10y02 (type A)

- items in the key: 4 (3 sampled rows, 1 known-wrong decoys, 0 known-right decoys); answered: 4; answer files: 2
- right: speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and other_decision names Y). right + extent: right and (own_whole / report_whole => extent whole). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | 0.90 rule |
|---|---|---|---|---|---|---|
| syl10_RO_treat | 3 | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- syl10_RO_treat: right 1.000 [1.000, 1.000] (read in full); right + extent 1.000 [1.000, 1.000] (read in full)

Answers on sampled rows (every reader): syl10_RO_treat: overrule 6

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): syl10_RO_treat: none

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 2/2 = 1.000 [0.342, 1.000]
- known wrong, not confirmed: 2/2 = 1.000 [0.342, 1.000]
- known right, confirmed: -

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] | - |

| per decoy family | accuracy |
|---|---|
| r5:opw1:operative-part | 2/2 = 1.000 [0.342, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 4 | 3/3 = 1.000 [0.439, 1.000] | 1/1 = 1.000 [0.206, 1.000] | 0 | 0 |
| ans_1_b.jsonl | 1 | 4 | 3/3 = 1.000 [0.439, 1.000] | 1/1 = 1.000 [0.206, 1.000] | 0 | 0 |

Items read twice: 4; same right answer 4/4 = 1.000 [0.510, 1.000]. A measure holds only if it holds for every reader.

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| syl10_RO_treat | fed | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| syl10_RO_treat | 2010s | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| syl10_RO_treat | own_part | 2 | 2/2 = 1.000 [0.342, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| syl10_RO_treat | own_whole | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| syl10_RO_treat | stratum fed|2010s (population 3, sampled 3) | 3 | 3/3 | 3/3 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (0 lines).
