# Round 8 sealed runs (one line per run)

- 2026-11-14 01:59:13 fresh sealed, 4th use (score_fresh7 --split test, label r8-v8e): 
- 2026-11-14T01:59:21+00:00 | args: --split sealed --out ~/Documents/us-caselaw-lean-work/caselaw-lean-2/round8/out/v8e --data ~/Documents/us-caselaw-lean-work/caselaw-lean-2/round8/stage/v8e --results ~/Documents/us-caselaw-lean-work/caselaw-lean-2/round8/results/v8e/sealed/shep | status.tsv sha1 da6f3c30f9b5a71536c253fc26744e565a71d89e | certs.tsv sha1 1a60f798de838ae50635ce38426ffc970c94a591 | history.tsv sha1 734b63e5515e1a679a74eb80a558bb51fa332495 | FREEZE.md sha1 17e6fa870f45301131cabed097d84d9957a044c5, 176 file hashes checked | results ~\Documents\us-caselaw-lean-work\caselaw-lean-2\round8\results\v8e\sealed\shep | recall NEG strict 123/252 (123/250) | recall NEG lenient 133/252 (133/250) | PART 6/16 (6/15) | precision strict 123/133 (123/133) | precision lenient 124/133 (124/133) | CLEAN 9577/9586 (9577/9586) | MOD 12/13 (12/13) | agreement 9718/9867 (9718/9864)
- 2026-11-14 01:59:13 Shepardized sealed, 3rd use (compare.py --split sealed, v8e): 
- 2026-11-14 01:59:13 fjc_idb_appeals h1 (benchmarks/fjc_idb_appeals/score.py --label round8, v8e): fjc_idb_appeals h1 clean 5943/6116 clean_docket 9302/9483 link_rate 16414/120366 part 619/1461 part_docket 623/2094 precision 1566/1758 precision_docket 1571/1772 precision_lenient 1691/1758 precision_lenient_docket 1699/1772 recall 1566/2864 recall_docket 1571/4126 recall_lenient 1730/2864 recall_lenient_docket 1738/4126
- 2026-11-14 01:59:13 shadow_docket h1 (benchmarks/shadow_docket/score.py --label round8, v8e): shadow_docket h1 clean 43577/43613 link_rate 45932/104457 precision 426/466 recall 426/1093
- 2026-11-14 01:59:13 scdb_disposition h1 (benchmarks/scdb_disposition/score.py --label round8, v8e): scdb_disposition h1 clean 1855/1910 link_rate 4393/13699 part 46/83 precision 1810/1863 precision_lenient 1817/1863 recall 1810/2400 recall_lenient 1864/2400
- 2026-11-14 01:59:13 state_overruled_tables h1 (benchmarks/state_overruled_tables/score.py --label round8, v8e): state_overruled_tables h1 actor_agreement 11/11 link_rate 173/281 recall 11/142 recall_any 11/142
- (lead, from the same single run's output files `round8/results/v8e/sealed/`; the two lines above came out empty
  because the script's grep patterns did not match the scorers' output) fresh sealed, 4th use: strict model 32/127 =
  0.252 [0.184, 0.334]; strict attributed 57/127 = 0.449 [0.365, 0.536]; lenient 77/127 = 0.606 [0.519, 0.687].
  Shepardized sealed, 3rd use: NEG strict 123/252 = 48.8% [42.7, 55.0]; lenient 133/252; precision strict 123/133 =
  92.5% [86.7, 95.9]; CLEAN 9,577/9,586; en banc different 7/33; panel withdrawn 5/25; SC reversed 80/132; SC
  vacated 31/61; PART 6/16.
