# Round 7 sealed runs (one line per run)

- 2026-11-14 00:08:11 fresh sealed (score_fresh7 --split test, label r7-v3): 
- 2026-11-14T00:08:41+00:00 | args: --split sealed --out ~/Documents/us-caselaw-lean-work/caselaw-lean-2/round7/out/v3 --data ~/Documents/us-caselaw-lean-work/caselaw-lean-2/round7/stage/v3 --results ~/Documents/us-caselaw-lean-work/caselaw-lean-2/round7/results/v3/sealed/shep | status.tsv sha1 25972da2762435840f6ed51dbf83ec7c286984ce | certs.tsv sha1 0de61f209b85c2e96a8e5041469a43ad45113059 | history.tsv sha1 f19a257e77453a7834b5c5b053970ebfc3cedb5d | FREEZE.md sha1 e4a776585b6a8f79b6ee0d6ce70d2315c2321135, 127 file hashes checked | results ~\Documents\us-caselaw-lean-work\caselaw-lean-2\round7\results\v3\sealed\shep | recall NEG strict 120/252 (120/250) | recall NEG lenient 129/252 (129/250) | PART 6/16 (6/15) | precision strict 120/130 (120/130) | precision lenient 121/130 (121/130) | CLEAN 9577/9586 (9577/9586) | MOD 12/13 (12/13) | agreement 9715/9867 (9715/9864)
- 2026-11-14 00:08 (lead's summary of the fresh sealed line above, from results/v3/sealed/fresh_test.txt): 127 pairs;
  model view strict 32 = 25.2% [18.4, 33.4], lenient 77 = 60.6% [51.9, 68.7]; attributed view strict 57 = 44.9%
  [36.5, 53.6], lenient 77. Third use of this half.
- 2026-11-14 00:09 the first Shepardized attempt (00:08, score_sealed7.sh → compare.py) was REFUSED before reading
  anything: compare.py checks round6/history/FREEZE.md, whose Lean hashes round 7 changed on purpose. Re-run through
  round7/shep_sealed7.py (compare.py unchanged; freeze check pointed at round7/FREEZE.md): the line above. Second use
  of this half. Time-split key: scored once on r6-final2 and once on r7-v3 (round7/heldout/RUNS.log).
