# round7/audit: blind-audit tooling (agent `audit`)

Clock times from `date` (GMT). Started 22:45, tooling done and self-test passing 23:07.

## What was done

- 22:45 read DESIGN7 (§0, §2, §3, §7), the round-6 tooling (`round6/history/audit/`: brief, auditlib, make_packs,
  score_audit, selftest_delta, runs v1/v2/r1/a3) and the round-5 audits (`round5/audit/`, `round5/audit_strata.py`).
- 22:50-23:00 wrote `audit7lib.py`, `decoys7.py`, `make_packs7.py`, `more_text7.py`, `score_audit7.py`,
  `AUDITOR_BRIEF7.md`, `selftest7.py` (Write tool, LF).
- 23:00 built the decoy pools; 23:01 scale check: 80 rows of `round5/recog/cert` in 1 min 53 s, 2 packs of 45 items
  (40 real + 5 decoys), about 2.8 KB per item. Output deleted afterwards.
- 23:07 self-test PASS (`selftest7/SELF_TEST_RESULT.txt`).

No auditor was started. Nothing outside `round7/audit/` was written. No answer key was read (§0): the inputs are
the certified deltas, the round-5/6 audit keys, answers and verdicts (for decoys), graph/nodes.tsv, the r6lib node
facts, the reader's common.py, the cue table (operative_whole, for the demotion rule) and texts from git.

## Usage

```
python -X utf8 round7/audit/decoys7.py                     # once (done): decoy_pool_A.jsonl, decoy_pool_B.jsonl
python -X utf8 round7/audit/make_packs7.py --class <name> --cert <delta folder or rows file> [--cert ...] \
       --n 80 --out round7/audit/<run>/ [--exclude round7/audit/<earlier run>/sample.tsv ...] \
       [--match claim=doctrine | rel=antecedent | src=REGEX | table=history ...] [--ids FILE] \
       [--lean-classes round7/out/<v>/classes.tsv] [--decoy-families REGEX] [--seed N] [--dry-run]
# launch one reader per pack: brief = round7/audit/<run>/BRIEF.md, pack = <run>/pack_<k>.md,
#   answers -> <run>/answers/ans_<k>.jsonl (a second reader: ans_<k>_<tag>.jsonl)
python -X utf8 round7/audit/score_audit7.py <run>          # score.md, score.json, errors.tsv
python -X utf8 round7/audit/selftest7.py                   # tool self-test
```

- `<run>` must be a neutral name (e.g. `r7a01`): it is printed in the packs, so make_packs7 refuses a name that
  carries the class or a rule word.
- A certify7 folder holding both tables needs `--match table=treatments` or `--match table=history`.
- B2 scope rewrite: `--ids <the --replace file>` with the rewritten rows as `--cert`; read `right + extent`.
- `by_match_overrides.tsv` (item, answer file or `*`, yes|no) in the run folder overrides the automatic match of a
  reader's `other_decision` to the row's Y (recognised rows); score_audit7 lists every `by` failure in errors.tsv.

## Item types

- **A (treatments rows)**: speaking decision W (for a recognised row the witness, else the acting court), decision X,
  passages of W's text around the main quote and any joined quotes (paragraph and one paragraph each side, 500-1600
  chars each side plus random jitter, merged when close; quotes not marked; machine part labels). Questions:
  speaks_of_x, act (overrule | reject_doctrine | report_other | limit | nothing | other | unsure), extent (whole |
  part | other_grounds | unclear), own_opinion, other_decision (for report_other), doctrine, words, confidence, note.
  Row effect classes: own_whole, own_part (scope partial or operativeWords demoted), doctrine, report_whole,
  report_part (witness rows). right = speaks_of_x yes + own_opinion yes + act in the class's set (+ other_decision
  names Y for report_*); right_extent adds extent whole for *_whole.
- **B (history rows)**: acting and target decisions (with docket), which text is shown, its opening, passages around
  the main quote and the anchor quote. Questions as the round-6 brief (same_case, acted_on, disposition, whole,
  evidence, confidence, note), plus a sentence on order-list / judgment-line orders printed at the head (orderHead)
  and "set aside" under vacated. right = link + kind (round-6 COMPAT); also link_effect; right_extent adds whole for
  scope all.
- `more_text7.py <item> [chars|all] [--target]` gives readers a wider stretch of the shown text or the target's text.

## Decoy pools (counts available, `decoy_pool_summary.tsv`)

| type | known wrong | known right | sources |
|---|---|---|---|
| A | 71 | 377 | round-5 opw1 (rejected 47 operative rows; confirmed 93 incl. 19 self-announced controls), recog1 (rejected 10; confirmed 260 incl. 27 self controls), test_it0 (13 synthetic wrong-X/Y + 1 rejected; confirmed 24 incl. 16 self controls) |
| B | 292 | 974 | round-6 v1/v2/r1/a3: rows every verdict found not linked, conf >= medium (193); wrong-target decoys every verdict rejected (99); rows confirmed with kind + scope, all high confidence (945); base controls confirmed (29) |

Rejected = failed on stated / x / y by every answer (extent-only failures are not used); confirmed = right_and_extent
by every answer (round 5) or link_kind_scope with high confidence (round 6). Per pack: at least max(ceil(real/9),
0.12 x real) decoys (>= 10% of the pack), about 60% known wrong; a decoy never shares a decision with a sampled row;
`--exclude` also excludes the earlier run's decoys. A decoy's earlier verdict stays in the key (`decoy_why`).
At ~6 known-wrong A decoys per 80-row run the A pool lasts about 12 runs without reuse.

## Self-test (selftest7.py, 23:07: PASS)

Synthetic inputs in `selftest7/` (round-5 opwords + recognised rows, ids rewritten, one doctrine row with a
doctrineTie line, two antecedent lines; round-6 a3 history rows with anchors and two setAside claims). Three runs
(A n=12, B n=12, A joined-only n=5 with `--exclude`); planted answers (wrong, extent-wrong, a missed decoy, a second
reader that disagrees once); every reported number checked: right / right_extent counts, Wilson bounds, decoy
accuracy per pack, readers, agreement, errors.tsv lines, >= 10% decoys per pack, no leaks of row ids / rule ids /
class / kind / scope / "decoy" into packs or BRIEF.md, more_text7 both modes, no overlap with an excluded run.

## Open points

- certify7.py does not exist yet; load_cert reads the DESIGN7 §4 delta names (treatments_delta, treatment_class_delta,
  joined_delta, history_delta, history_anchor_delta, history_claim_delta). If certify7 writes other names, add them
  to `audit7lib.SIDE`.
- report_* matching of the reader's other decision to Y is automatic (citation, else a case-name token); check the
  `by` lines of errors.tsv and add overrides where the match is wrong.
- Round-5 A decoys carry no quote text; they are used only when the text at HEAD still has the audited sha.
