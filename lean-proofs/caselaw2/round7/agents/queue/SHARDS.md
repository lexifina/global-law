# Shards of the B1 reading queue (agent `queue`, round 7)

Each shard is 3-4 packs for one reader sub-agent, in priority order (P1 first). Brief: `round7/agents/queue/READER_BRIEF_RECOG.md`; packs in `round7/agents/queue/packs/`; answers to `round7/agents/queue/ans/ans_<pack name without .md>.jsonl`; then `bash round7/agents/queue/certify.sh`.

33 shards, 131 packs, 6,219 items. P1 = S001-S014 and the first pack of S015 (57 packs, 2,761 items: S001-S003
hold the 497 typed feed notes on novel pairs, then T1F); P2 = rest of S015 to S029; P3 = last pack of S029 to S033. See INVENTORY.md section 4 for why stopping after P1 is reasonable. Shards are
disjoint; every queued item is in exactly one pack (`packs/items_index.tsv`).

| shard | packs | items | priority | sources |
|---|---|---|---|---|
| S001 | pack_P1_CUTT2_001.md pack_P1_OG_001.md pack_P1_OG_002.md pack_P1_OG_003.md | 160 | P1 | CUT/OG |
| S002 | pack_P1_OG_004.md pack_P1_OG_005.md pack_P1_OG_006.md pack_P1_OG_007.md | 196 | P1 | OG |
| S003 | pack_P1_OG_008.md pack_P1_OG_009.md pack_P1_OG_010.md pack_P1_T1F_001.md | 191 | P1 | OG/T1F |
| S004 | pack_P1_T1F_002.md pack_P1_T1F_003.md pack_P1_T1F_004.md pack_P1_T1F_005.md | 200 | P1 | T1F |
| S005 | pack_P1_T1F_006.md pack_P1_T1F_007.md pack_P1_T1F_008.md pack_P1_T1F_009.md | 200 | P1 | T1F |
| S006 | pack_P1_T1F_010.md pack_P1_T1F_011.md pack_P1_T1F_012.md pack_P1_T1F_013.md | 200 | P1 | T1F |
| S007 | pack_P1_T1F_014.md pack_P1_T1F_015.md pack_P1_T1F_016.md pack_P1_T1F_017.md | 200 | P1 | T1F |
| S008 | pack_P1_T1F_018.md pack_P1_T1F_019.md pack_P1_T1F_020.md pack_P1_T1F_021.md | 200 | P1 | T1F |
| S009 | pack_P1_T1F_022.md pack_P1_T1F_023.md pack_P1_T1F_024.md pack_P1_T1F_025.md | 200 | P1 | T1F |
| S010 | pack_P1_T1F_026.md pack_P1_T1F_027.md pack_P1_T1F_028.md pack_P1_T1F_029.md | 200 | P1 | T1F |
| S011 | pack_P1_T1F_030.md pack_P1_T1F_031.md pack_P1_T1F_032.md pack_P1_T1F_033.md | 200 | P1 | T1F |
| S012 | pack_P1_T1F_034.md pack_P1_T1F_035.md pack_P1_T1F_036.md pack_P1_T1F_037.md | 200 | P1 | T1F |
| S013 | pack_P1_T1F_038.md pack_P1_T1F_039.md pack_P1_T1F_040.md pack_P1_T1F_041.md | 200 | P1 | T1F |
| S014 | pack_P1_T1F_042.md pack_P1_T1F_043.md pack_P1_T1F_044.md pack_P1_T1F_045.md | 200 | P1 | T1F |
| S015 | pack_P1_T1F_046.md pack_P2_CUTT2_001.md pack_P2_CUTT2_002.md pack_P2_CUTT2_003.md | 164 | P1/P2 | CUT/T1F |
| S016 | pack_P2_CUTT2_004.md pack_P2_CUTT2_005.md pack_P2_CUTT2_006.md pack_P2_CUTT2_007.md | 200 | P2 | CUT |
| S017 | pack_P2_CUTT2_008.md pack_P2_CUTT2_009.md pack_P2_CUTT2_010.md pack_P2_CUTT2_011.md | 200 | P2 | CUT |
| S018 | pack_P2_CUTT2_012.md pack_P2_CUTT2_013.md pack_P2_CUTT2_014.md pack_P2_CUTT2_015.md | 200 | P2 | CUT |
| S019 | pack_P2_CUTT2_016.md pack_P2_CUTT2_017.md pack_P2_CUTT2_018.md pack_P2_CUTT2_019.md | 200 | P2 | CUT |
| S020 | pack_P2_CUTT2_020.md pack_P2_CUTT2_021.md pack_P2_CUTT2_022.md pack_P2_CUTT2_023.md | 200 | P2 | CUT |
| S021 | pack_P2_CUTT2_024.md pack_P2_CUTT2_025.md pack_P2_CUTT2_026.md pack_P2_CUTT2_027.md | 200 | P2 | CUT |
| S022 | pack_P2_CUTT2_028.md pack_P2_CUTT2_029.md pack_P2_CUTT2_030.md pack_P2_CUTT2_031.md | 200 | P2 | CUT |
| S023 | pack_P2_CUTT2_032.md pack_P2_CUTT2_033.md pack_P2_CUTT2_034.md pack_P2_CUTT2_035.md | 200 | P2 | CUT |
| S024 | pack_P2_CUTT2_036.md pack_P2_OG_001.md pack_P2_OG_002.md pack_P2_OG_003.md | 189 | P2 | CUT/OG |
| S025 | pack_P2_OG_004.md pack_P2_OG_005.md pack_P2_OG_006.md pack_P2_OG_007.md | 196 | P2 | OG |
| S026 | pack_P2_OG_008.md pack_P2_OG_009.md pack_P2_OG_010.md pack_P2_OG_011.md | 196 | P2 | OG |
| S027 | pack_P2_OG_012.md pack_P2_OG_013.md pack_P2_OG_014.md pack_P2_OG_015.md | 196 | P2 | OG |
| S028 | pack_P2_OG_016.md pack_P2_OG_017.md pack_P2_OG_018.md pack_P2_OG_019.md | 196 | P2 | OG |
| S029 | pack_P2_OG_020.md pack_P2_OG_021.md pack_P2_T1F_001.md pack_P3_CUTT2_001.md | 130 | P2/P3 | CUT/OG/T1F |
| S030 | pack_P3_CUTT3_001.md pack_P3_CUTT3_002.md pack_P3_OG_001.md pack_P3_T3_001.md | 127 | P3 | CUT/OG/T3 |
| S031 | pack_P3_T3_002.md pack_P3_T3_003.md pack_P3_T3_004.md pack_P3_T3_005.md | 188 | P3 | T3 |
| S032 | pack_P3_T3_006.md pack_P3_T3_007.md pack_P3_T3_008.md pack_P3_T3_009.md | 188 | P3 | T3 |
| S033 | pack_P3_T3_010.md pack_P3_T3_011.md pack_P3_T1F_001.md | 102 | P3 | T1F/T3 |
