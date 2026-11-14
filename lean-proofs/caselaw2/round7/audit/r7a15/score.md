# Blind audit score: r7a15 (type B)

- items in the key: 90 (80 sampled rows, 6 known-wrong decoys, 4 known-right decoys); answered: 90; answer files: 2
- right: link and the disposition agrees with the kind. right + extent: right and (scope all => whole yes). `unsure` is never right; several readers: strict reading. Wilson 95%.

## Per class

| class | population | answered | right | right + extent | link | link + effect | 0.90 rule |
|---|---|---|---|---|---|---|---|
| b4e_rp | 208 | 80 | 72/80 = 0.900 [0.815, 0.949] | 72/80 = 0.900 [0.815, 0.949] | 73/80 = 0.912 [0.830, 0.957] | 72/80 = 0.900 [0.815, 0.949] | interval reaches below 0.90 |

Corpus-weighted (strata = federal / state x decade, weighted by population):

- b4e_rp: right 0.881 [0.769, 0.943] (n_eff 54); right + extent 0.881 [0.769, 0.943] (n_eff 54)

Answers on sampled rows (every reader): b4e_rp: modified 4, none 7, reversed 61, reversed_or_vacated_in_part 6, vacated 2

Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other decision is not Y, extent = whole wanted): b4e_rp: kind 1, link 7

## Decoys (reader accuracy on items whose answer is known)

- all decoy answers: 10/10 = 1.000 [0.723, 1.000]
- known wrong, not confirmed: 6/6 = 1.000 [0.610, 1.000]
- known right, confirmed: 4/4 = 1.000 [0.510, 1.000]

| per pack | accuracy | known wrong rejected | known right confirmed |
|---|---|---|---|
| pack_1 | 5/5 = 1.000 [0.566, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] |
| pack_2 | 5/5 = 1.000 [0.566, 1.000] | 3/3 = 1.000 [0.439, 1.000] | 2/2 = 1.000 [0.342, 1.000] |

| per decoy family | accuracy |
|---|---|
| r6:a3:below/sc/weak2 | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:rehear/docket | 1/1 = 1.000 [0.206, 1.000] |
| r6:a3:rehear/enbanc-cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/docket | 2/2 = 1.000 [0.342, 1.000] |
| r6:r1:rehear/panel-cite | 1/1 = 1.000 [0.206, 1.000] |
| r6:r1:rehear/self | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:below/sc | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:decoy_wrong | 1/1 = 1.000 [0.206, 1.000] |
| r6:v1:memo/cite | 1/1 = 1.000 [0.206, 1.000] |

## Readers

| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |
|---|---|---|---|---|---|---|
| ans_1.jsonl | 1 | 45 | 38/40 = 0.950 [0.835, 0.986] | 5/5 = 1.000 [0.566, 1.000] | 0 | 0 |
| ans_2.jsonl | 2 | 45 | 34/40 = 0.850 [0.709, 0.929] | 5/5 = 1.000 [0.566, 1.000] | 0 | 1 |

## Per class: federal / state, decade, effect, stratum

| class | cut | answered | right | right + extent |
|---|---|---|---|---|
| b4e_rp | fed | 37 | 34/37 = 0.919 [0.787, 0.972] | 34/37 = 0.919 [0.787, 0.972] |
| b4e_rp | state | 43 | 38/43 = 0.884 [0.755, 0.949] | 38/43 = 0.884 [0.755, 0.949] |
| b4e_rp | 1890s | 1 | 1/1 = 1.000 [0.206, 1.000] | 1/1 = 1.000 [0.206, 1.000] |
| b4e_rp | 1900s | 2 | 1/2 = 0.500 [0.095, 0.905] | 1/2 = 0.500 [0.095, 0.905] |
| b4e_rp | 1910s | 7 | 6/7 = 0.857 [0.487, 0.974] | 6/7 = 0.857 [0.487, 0.974] |
| b4e_rp | 1920s | 9 | 8/9 = 0.889 [0.565, 0.980] | 8/9 = 0.889 [0.565, 0.980] |
| b4e_rp | 1930s | 7 | 7/7 = 1.000 [0.646, 1.000] | 7/7 = 1.000 [0.646, 1.000] |
| b4e_rp | 1940s | 6 | 6/6 = 1.000 [0.610, 1.000] | 6/6 = 1.000 [0.610, 1.000] |
| b4e_rp | 1950s | 6 | 5/6 = 0.833 [0.436, 0.970] | 5/6 = 0.833 [0.436, 0.970] |
| b4e_rp | 1960s | 4 | 2/4 = 0.500 [0.150, 0.850] | 2/4 = 0.500 [0.150, 0.850] |
| b4e_rp | 1970s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| b4e_rp | 1980s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| b4e_rp | 1990s | 10 | 10/10 = 1.000 [0.723, 1.000] | 10/10 = 1.000 [0.723, 1.000] |
| b4e_rp | 2000s | 5 | 4/5 = 0.800 [0.376, 0.964] | 4/5 = 0.800 [0.376, 0.964] |
| b4e_rp | 2010s | 9 | 9/9 = 1.000 [0.701, 1.000] | 9/9 = 1.000 [0.701, 1.000] |
| b4e_rp | modified | 4 | 4/4 = 1.000 [0.510, 1.000] | 4/4 = 1.000 [0.510, 1.000] |
| b4e_rp | reversed | 73 | 65/73 = 0.890 [0.798, 0.943] | 65/73 = 0.890 [0.798, 0.943] |
| b4e_rp | vacated | 3 | 3/3 = 1.000 [0.439, 1.000] | 3/3 = 1.000 [0.439, 1.000] |
| b4e_rp | stratum fed|1890s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| b4e_rp | stratum fed|1900s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| b4e_rp | stratum fed|1910s (population 6, sampled 6) | 6 | 5/6 | 5/6 |
| b4e_rp | stratum fed|1920s (population 7, sampled 7) | 7 | 7/7 | 7/7 |
| b4e_rp | stratum fed|1930s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| b4e_rp | stratum fed|1940s (population 2, sampled 2) | 2 | 2/2 | 2/2 |
| b4e_rp | stratum fed|1950s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| b4e_rp | stratum fed|1970s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| b4e_rp | stratum fed|1980s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| b4e_rp | stratum fed|1990s (population 5, sampled 5) | 5 | 5/5 | 5/5 |
| b4e_rp | stratum fed|2000s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| b4e_rp | stratum fed|2010s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| b4e_rp | stratum state|1910s (population 1, sampled 1) | 1 | 1/1 | 1/1 |
| b4e_rp | stratum state|1920s (population 2, sampled 2) | 2 | 1/2 | 1/2 |
| b4e_rp | stratum state|1930s (population 7, sampled 5) | 5 | 5/5 | 5/5 |
| b4e_rp | stratum state|1940s (population 5, sampled 4) | 4 | 4/4 | 4/4 |
| b4e_rp | stratum state|1950s (population 4, sampled 4) | 4 | 4/4 | 4/4 |
| b4e_rp | stratum state|1960s (population 17, sampled 4) | 4 | 2/4 | 2/4 |
| b4e_rp | stratum state|1970s (population 24, sampled 4) | 4 | 3/4 | 3/4 |
| b4e_rp | stratum state|1980s (population 20, sampled 5) | 5 | 5/5 | 5/5 |
| b4e_rp | stratum state|1990s (population 21, sampled 5) | 5 | 5/5 | 5/5 |
| b4e_rp | stratum state|2000s (population 25, sampled 4) | 4 | 3/4 | 3/4 |
| b4e_rp | stratum state|2010s (population 45, sampled 5) | 5 | 5/5 | 5/5 |

Wrong items and missed decoys, with the readers' words: `errors.tsv` (8 lines).
