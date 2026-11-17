| Corpus | Scanned | Mention income tax | Stage A kept |
|---|---|---|---|
| DILA JADE dump (2026-11-08) | 573,525 | 55,392 | 16,865 |
| Justice administrative open data (CE/CAA/TA 2021-2026) | 1,174,994 | 24,261 | 8,938 |
| **Total** | 1,748,519 | 79,653 | 25,803 |

| Cour de cassation dump | Scanned | Mention income tax | + tax fraud | + computation words |
|---|---|---|---|---|
| Freemium_cass_global_20261108-140000.tar.gz | 145,421 | 611 | 148 | 7 |
| Freemium_inca_global_20261108-140000.tar.gz | 387,902 | 1,959 | 744 | 50 |

Stage B: {"stage_a": 25803, "drop_no_figure": 17298, "ir_computation": 5361, "drop_not_ir_dispute": 2258, "drop_order_no_merits": 132, "drop_duplicate": 754}
stage B candidates 5361 2015+ 2523 2020+ 589
liquidation second pass kept 7

| Batch | Read | usable_full | usable_partial | no_program_figure | facts_insufficient | other_tax | procedural | duplicate |
|---|---|---|---|---|---|---|---|---|
| b1 | 196 | 0 | 6 | 45 | 13 | 115 | 12 | 5 |
| b2 | 269 | 0 | 11 | 127 | 64 | 29 | 30 | 8 |
| b3 | 144 | 0 | 41 | 20 | 42 | 23 | 11 | 7 |
| b4a | 206 | 0 | 7 | 158 | 12 | 8 | 15 | 6 |
| b4b | 205 | 0 | 11 | 150 | 18 | 2 | 16 | 8 |
| **all** | 1020 | 0 | 76 | 500 | 149 | 177 | 84 | 34 |

cases 84 from decisions 76 with scorable figures 73 from decisions 67 excluded 11
completeness Counter({'parts_only': 50, 'partial': 21, 'full': 2})
years [(2015, 14), (2016, 10), (2017, 15), (2018, 6), (2019, 10), (2020, 10), (2021, 6), (2022, 2)]
topics [('qf', 53), ('red_credit', 4), ('157bis', 3), ('frais', 3), ('micro', 3), ('quotient', 2), ('foncier', 2), ('cehr', 1), ('pension', 1), ('other', 1)]
figures scored 86
lean {'match': 72, 'out_of_scope': 4, 'mismatch': 1, 'no_equivalent': 3, 'not_run': 6} of which on a proxy year: {'match': 48, 'out_of_scope': 1, 'no_equivalent': 2}
m {'match': 82, 'mismatch': 3, 'not_run': 1} of which on a proxy year: {'match': 49, 'mismatch': 2}
prod {'match': 22, 'mismatch': 1, 'no_equivalent': 1} of which on a proxy year: {}

| Figure | n | Lean | M | Production |
|---|---|---|---|---|
| NBPT | 53 | 53/53 | 53/53 | 9/9 |
| IDRS | 4 | 1/1 | 4/4 | 1/1 |
| TAX_DELTA | 4 | 2/2 | 4/4 | 2/2 |
| ABAT10 | 4 | 2/2 | 4/4 | — |
| PA_DED | 3 | 2/2 | 2/2 | 2/2 |
| A157BIS | 3 | 3/3 | 3/3 | 3/3 |
| MICRO_ABAT | 3 | 3/3 | 3/3 | — |
| RNI | 2 | 1/1 | 2/2 | 1/1 |
| IR_NET | 2 | 1/2 | 1/2 | 1/2 |
| IDEC | 1 | 1/1 | 1/1 | 1/1 |
| RED_DONS | 1 | 1/1 | 1/1 | — |
| CRED_TOTAL | 1 | 1/1 | 1/1 | — |
| RBG | 1 | — | 1/1 | 1/1 |
| CEHR | 1 | 1/1 | 1/1 | 1/1 |
| RED_PRESTCOMP | 1 | — | 1/1 | — |
| DONS_BASE | 1 | — | 0/1 | — |
| DONS_CARRY | 1 | — | 0/1 | — |
| **all** | 86 | 72/73 | 82/85 | 22/23 |
