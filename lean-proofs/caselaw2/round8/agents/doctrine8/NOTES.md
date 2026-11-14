# Round 8, agent `doctrine8`: notes

Times from `date` (Git Bash; the clock prints "GMTST").

- 00:18 start. Read DESIGN8 §0, COMMON, BRIEF, round7/agents/doctrine/NOTES.md, build_registry.py, make_items.py.
  Plan: measure the dominance opportunity from the round-7 scan (ties.jsonl.gz resolved, scan/*.jsonl.gz rejections);
  no new corpus pass; no answer key read.
- 00:19 measure.py (reads round-7 ties.jsonl.gz + scan/*.jsonl.gz, node arrays, round7/stage/v3/treatments.tsv for
  base-pair overlap; no key). 39,142 court-of-last-resort rejection-label sentences carry a label that is ambiguous in
  the round-7 registry (strict ties to >= 2 decisions). With x = the dominant target x1: 8,978 drop on order,
  28,532 on power (x1 mostly a SCOTUS / other-system case, e.g. state courts on "exclusionary rule"), 1,632 left
  (work/dom_cands.jsonl, work/curve.json).
- 00:20 make_items.py (round 7, unchanged, --cands/--out into work/) on the loosest threshold (n1 >= 3, n1 >= 2 x n2;
  426 sentences): tie sentence for x1 found in W 118, rule_ok 19 (16 pairs). Rows estimated with the round-7 read
  yields (rule_ok -> both-yes 18/38 = 0.47; tie found but rule no -> 12/206 = 0.058).

  Curve (sentences after order/power -> tie found in W -> rule_ok (pairs) -> est. reader-yes rows; pairs in base):
  | n1 >= | ratio >= | sentences | W   | pairs | targets | tie found | rule_ok (pairs) | est rows | base pairs* |
  | 3     | 2        | 426       | 342 | 350   | 133     | 118       | 19 (16)         | 14.7     | 16          |
  | 3     | 3        | 330       | 265 | 269   | 105     | 79        | 9 (6)           | 8.3      | 9           |
  | 5     | 2        | 307       | 247 | 253   | 83      | 79        | 13 (10)         | 9.9      | 8           |
  | 5     | 3        | 231       | 186 | 190   | 61      | 47        | 6 (3)           | 5.2      | 3           |
  | 5     | 4        | 193       | 151 | 155   | 51      | 42        | 6 (3)           | 4.9      | 2           |
  | 5     | 6        | 155       | 122 | 124   | 41      | 36        | 5 (2)           | 4.1      | 2           |
  | 10    | 4        | 134       | 108 | 110   | 31      | 26        | 1 (1)           | 1.9      | 2           |
  | 10    | 10       | 101       | 85  | 85    | 20      | 20        | 1 (1)           | 1.6      | 2           |
  | 20    | 10       | 45        | 35  | 35    | 15      | 14        | 1 (1)           | 1.2      | 1           |
  (* base pairs = (W, x1) pairs of all sentences at that threshold that already have a treatments.tsv row in v3.)
  My own look at the 19 rule_ok items at (3,2): ~9 are real rejections of x1's doctrine (Garg->Sumner,
  Brooks->Anderson, Wolfe/Colonial/Harper->Clark v. Mercer Oil, Rye->Hannan, Board of Regents->Atwater, ...),
  4-5 of those pairs already have an explicit base row; the rest are quotations, statute-caused, or misread
  (Ex parte Harding x4, Oregon v. Kennedy, United States v. Powell). Dominance adds nothing at strict thresholds.
- Decision (brief step 2): fewer than ~25 new rows at every threshold (best ~15 estimated, ~5 new pairs) -> STOP.
  No rows, no certify, no audit, no LEAN_REQUEST.
- For comparison only (not built; a different rule): "own-tie" disambiguation (W's own strict ties name exactly one
  decision xo, order/power with xo): 605 sentences, 502 with tie found, rule_ok 69 (56 pairs, 17 in base; xo is the
  corpus-dominant target in only 14), est. ~57 reader-yes rows at round-7 yields. A random look at 12 rule_ok items:
  about half are real (Brown/Hudkins, Alcorn->Cottle, Wolfe->Clark, Darling->charitable immunity is tied to Parks
  only loosely). It conflicts with the Lean table check `doctrineAmbiguous` / `doctrine_unique` (corpus-wide label
  uniqueness), so it would need the uniqueness scoped to (label, W's own tie) or (label, system): an open point for
  the lead, not this round's brief. Files: work/own_alt_cands.jsonl, work/own_alt_items.jsonl.
- 00:21 done. Files: measure.py, work/{dom_cands,dom32_cands,dom32_items,own_alt_cands,own_alt_items}.jsonl,
  work/curve.json, work/*.log. Nothing committed; no processes left running; Lean tree untouched.
