# round8/audit: blind-audit tooling (agent `audit8`)

Clock times from `date` (GMT).

- 00:17 started; read DESIGN8, COMMON, BRIEF, round7/audit (all tools, brief, NOTES, run manifests and scores).
- 00:19 plan: port round7/audit to round8/audit (audit8lib, make_packs8, decoys8, more_text8, score_audit8,
  selftest8, AUDITOR_BRIEF8.md); add the round-7 audited rows to the decoy pools; add a pair form (type C: two
  history rows of the same acting/target pair, both quotes shown unlabelled in text order) for agent `contradict`.
- 00:20-00:22 port written (copies of the round-7 files, then edits; LF checked, no CRLF).
- 00:22 decoys8.py built the pools (3 s).
- 00:24 selftest8 PASS (A, B, joined-only A with --exclude, pair form C in a nested run folder).
- 00:25 dry run r8x01 built (17 s); 00:25-00:26 one blind opus auditor (prompt = read BRIEF.md + pack_1.md, write
  ans_1.jsonl; 59 s); 00:26 scored.
- 00:27 HOWTO.md and READY written.

Nothing outside `round8/audit/` was written. No answer key was read: inputs are certified deltas / stage folders,
round-5/6/7 audit folders (keys, answers, verdicts: decoys only), graph/nodes.tsv, r6lib node facts, the reader's
common.py, the cue table (operative_whole, for the demotion rule, read live from tools/caselaw2/cues) and texts at
git HEAD.

## What changed against round 7

- Paths: `round8/audit/`; run folders may be nested (`**/sample.tsv`, `**/store/index.tsv`), the run path relative to
  `round8/audit/` is what is printed in packs and BRIEF.md and what the name guard checks (round 7 printed the
  basename only, which gave a wrong path for nested runs).
- Name guard: extra telling words (contra, pair, base, new, old, multi, state, ownact, dock, shadow, fjc, scdb, same,
  remand, dismiss, deni, modif). HOWTO gives each agent a letter for neutral run names `r8<letter><nn>`.
- `--pairs FILE` (type C): lines `<row 1 id> TAB <row 2 id>`, both history rows of one (by, target), looked up in
  every `--cert` (give `round7/stage/v3` for base rows). Spans = row 1 quote + anchor, row 2 quote + anchor; packs
  use the type-B layout and brief B; decoys from pool B. Key adds `row2_id, kind2, scope2, src2, quote_order`.
  `--exclude` also excludes earlier `row2_id`s; decoys never share a row id with row 1 or row 2.
- `--lean-certs round8/out/<v>/certs.tsv`: keep rows (both tables) whose `result_all` starts with ok
  (`--lean-classes` only covers treatments).
- score_audit8: type C measures (row 1: right, right_extent, link, link_effect; row 2: row2_right,
  row2_right_extent, row2_link_effect; only1_right, only2_right); errors.tsv has row2 columns (empty otherwise).
- AUDITOR_BRIEF8.md = brief 7 with paths, plus one neutral sentence in brief B: if the passages describe what was
  done to the target in more than one place and they disagree, answer what the acting court itself did, reading
  the decision as a whole, and say so in `note` (no hint which place governs).
- decoys8.py: round-5 (A) and round-6 (B) pools rebuilt byte-identical to round 7's; plus round-7 audited rows
  (r7a01-r7a21, sampled rows only, judged with the round-7 rules): known right = every answer right + extent with
  high confidence; known wrong = every answer not right (A: x/own/act/by, never extent-only) / not linked (B), none
  unsure, confidence >= medium. Rows reloaded from each run's own --cert inputs.

## Decoy pools (decoy_pool_summary.tsv)

| type | known wrong | known right | sources |
|---|---|---|---|
| A | 150 (r5 71 + r7 79) | 794 (r5 377 + r7 417) | round-5 audits; round-7 r7a01-a09, a11 |
| B | 332 (r6 292 + r7 40) | 1570 (r6 974 + r7 596) | round-6 audits; round-7 r7a10, a12-a17, a19-a21 |

## Self-test (selftest8.py, 00:24, PASS; selftest8/SELF_TEST_RESULT.txt)

Same checks as round 7 (A n=12, B n=12, joined-only A n=5 with --exclude; right / right_extent counts, Wilson,
decoy accuracy per pack, readers, agreement, errors.tsv lines, >= 10% decoys per pack, no leaks, more_text both
modes), with round-8 ids (`t8:st:...`, `h8:st:...`). New: pair run C (49 synthetic second rows `h8:st2:...` = the
sentence before row 1's quote with a kind of the other status effect; nested folder selftest8/nest/run_C; planted
answers row 1 / row 2 / not linked): type C, brief B, nested paths in BRIEF.md, row 1 right 6/12, row 2 right 3/12,
only-1 6, only-2 3, link 9, decoys 4/4, quote_order known, no leaks, >= 10% decoys, more_text on a nested run.

## Dry run r8x01 (round-7 class rh_eb, 00:25-00:26)

`make_packs8.py --class rh_eb --cert round7/agents/b4rehear/cert_enbanc_act --cert .../cert_enbanc_order
--ids round7/audit/ids_rh_enbanc_actorder.txt --n 20 --pack-size 24 --out round8/audit/r8x01` -> 23 items (20 rows,
2 known-wrong + 1 known-right decoys), one pack, 61 KB. One blind opus auditor (59 s, 6 tool calls).
Score: right 19/20 = 0.950 [0.764, 0.991], link 20/20, link + effect 20/20; decoys 3/3. All 20 rows were also in the
round-7 sample r7a17: the auditor's (same_case, acted_on, disposition) equals both round-7 readers' on 20/20 (the
one "wrong" row was answered withdrawn_or_superseded for a `vacated` row by the round-7 readers too). Round trip
confirmed. (Round-7 class figures, not a round-8 result.)

## Open points

- certify8.py is not out yet (INFRA_READY absent at 00:27); load_cert ignores id prefixes, tested with `t8:` / `h8:`
  ids. If certify8 adds side tables with new names, add them to `audit8lib.SIDE`.
- A pair file's header line is counted in the "rows not both in the inputs" warning (harmless).
- More readers than two per pack: the strict reading (every reader right) is used, as in round 7.
