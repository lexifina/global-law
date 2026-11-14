# Round 7, agent `infra`: certify7, stage7, r7_run, score7, orderHead rows

Contract: `round7/DESIGN7.md` §0, §1, §3, §4, §5 and `round7/LEAN7.md` §0 (the `lean` agent's readings L7-1..12,
which certify7 follows). Times from `date`. Nothing under `data/`, `out/`, `round5/`, `round6/` was edited; nothing
committed. No answer-key file is read by certify7 / stage7 / build_orderhead (only score7.sh calls scorers).

## Log
- 22:44 start; read DESIGN7, STAGE_NOTES, certify6, stage6, r6_run, score_dev, round5 stage/score_all, certify_recog,
  certify_opwords, memo NOTES, LEAN6 §1.1, Certificate.lean / Run.lean (check, resolves, operative, anchored steps).
- 22:47 `stage7.py`; `stage7.py base` + `--force-write` self-test: the ten tables byte-identical.
- 22:49 `wsl/r7_run.sh`; `NOBUILD=1 r7_run.sh base` (built the base mirror `base_r7_final2`, ~7 min once).
- 22:55 `certify7.py`, unit tests (`test_certify7.py`), real-row self-test (`selftest7.py`).
- 23:01 base run done: **byte-identical to `round6/history/out/final2`** (below).
- 23:05 LEAN7.md readings appeared; certify7 / stage7 aligned (L7-5 joined disqualifiers, L7-7 several claims per
  history row, L7-11 setAside on another kind = no effect, L7-3 uniqueness on the tie labels, `order_head_max_len`).
- 23:05–23:15 orderHead rows (`round7/agents/orderhead/`), `score7.sh` + `score_hist_dev.py` + `old_by_class7.py` +
  `summary7.py`, scored `base`.

## Files (all new)

| file | call |
|---|---|
| `round7/certify7.py` | `python -X utf8 round7/certify7.py --rows R.jsonl [--rows …] --out DIR [--procs N] [--no-base-skip] [--keep-base-conflicts]` |
| `round7/stage7.py` | `python -X utf8 round7/stage7.py <name> [--delta DIR …] [--remove F] [--drop F] [--replace F] [--claims F] [--keep-ids F] [--force-write]` → `round7/stage/<name>/` |
| `wsl/r7_run.sh` | `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc '[NOBUILD=1] bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r7_run.sh <name> [ref]'` → `round7/out/<name>/` |
| `round7/score7.sh` | `bash round7/score7.sh <name> [beh] [noold]` → `round7/results/<name>/` (+ `summary.txt`) |
| `round7/score_hist_dev.py` | Shepardized dev (round6/shepardized/compare.py --split dev) on round-7 paths |
| `round7/old_by_class7.py` | SCDB / CRS by class on round-7 paths (round5/old_by_class.py copy; `doctrine` rows counted, never admitted) |
| `round7/summary7.py` | one-page `summary.txt` |
| `agents/infra/test_certify7.py` | 44 unit checks on synthetic texts |
| `agents/infra/selftest7.py` | certify7 vs the round-6 Lean verdicts on real base rows |
| `agents/infra/selftest_stage7.py` | 56 checks of stage7 |
| `agents/orderhead/` | A1 (iii) rows + B4 (f) figure (its own NOTES.md) |

## certify7 (DESIGN7 §2–4, LEAN7 L7-1..12)

- Treatments rows: `doctrineBadRow` (doctrine claim: kind disapproved and a doctrineTie line) → no joined line:
  `operativeBadRow` (operative claim) then Lean `check` in the row's mode (plain: `treat[kind]`, `disqualify_treat`
  for status-changing kinds, evidence in the window; operative: `operative` + `disqualify_operative`, evidence in
  the quote) → with joined lines: `joinedMismatch`, `joinedPart`, `joinedDisqualified` (kind's plain list +
  `disqualify_joined`, L7-5), `joinedRelation` (antecedent: j_end ≤ start, gap ≤ `joined_gap_max`, `anaphor` and a
  plain cue of the kind in the main quote; doctrineTie: doctrine row, label ≥ 2 words and ≥ 8 chars, in both quotes,
  `doctrine_tie` phrase in the joined quote), `joinedUnresolved` (evidence in one joined quote alone, cite also
  through the index), then the main check with the evidence taken as given (`operativeBadRow` there for an
  operative row; doctrine mode: `doctrine_reject`, `disqualify_treat` + `disqualify_operative`) → after the text
  checks `doctrineAmbiguous` (compact tie labels; base joined/class lines count) → `duplicate`.
  Base skip by (by, target, kind) in base treatments. Ids `t7:<by>:<target>:<start>` (+`b` on a clash).
- History rows: certify6's checks (imported functions, round 6 unchanged) + `setAside` (vacated: cue list + 
  `set_aside`; any other kind: no effect, claim line not written, L7-11) + `orderHead` (part step: headmatter only
  with the claim, Supreme Court (courts2 by name → 2906), date(by) ≥ `order_head_from`, listed kind, `order_line`
  phrase of the kind, ≤ `order_head_max_len`; else `orderHeadNotAllowed`), then duplicate / conflict / conflictBase
  as certify6. A claimed row whose (by, target, kind) is already a base row is checked on the BASE row's own
  certificate (and anchor) with the claim and, if it passes, only a `history_claim` line for the base id is written
  ("h6: rows keep their ids").
- Windows: one per quote `[start-400, end+400)` clipped (main, every joined quote, anchor), SHA-1 in window_sha.
  Cue lists read from `cue_table.json` at run time; DESIGN7's examples are the fallback, `stats.json` `cue_source`
  says which (now: every round-7 key from cue_table.json).
- Not looser than Lean: a quote is checked against one window only; L7-6 (0 or > 2 joined lines) is a badRow here.

## Self-tests

- `test_certify7.py`: **44 checks, 0 failed** (every relation / reason of §2–3, incl. the certifier side of mutants
  M41–M45, M48, M50–M53).
- `selftest7.py --n 2500` (base rows of final2 back through certify7, `--no-base-skip`, vs round-6 Lean verdicts):
  5,165 rows; **5,155 agree, certify7 looser than Lean 0**, stricter 10 (treatment rows whose evidence Lean found
  in a wider round-4 window, > 400 characters from the quote). `agents/infra/selftest/SELFTEST.txt`.
- End-to-end on a real text (Alabama, node 19639 → 17837, "That case is wrong and mnst be overruled." with the
  antecedent "Brinkerhoff & Co., 119 Ala. 528." 251 characters before): admitted, joined_delta line written; the
  same row with a dissent joined part: `joinedPart`.
- `selftest_stage7.py`: **56 checks, 0 failed** — no delta = base (hard links), `--force-write` = base bytes,
  every add / skip rule (ids present, first line per id, (id, claim) for history_claim, two joined lines per id,
  window key clash, cite-index ambiguity), `--remove` / `--drop` / `--replace` / `--claims`, a remove_ids.txt in a
  delta folder is reported not applied, real deltas of round 5 (`round5/opwords/cert`: treatments +665;
  `round5/recog/cert`: +9, 1,450 ids already in final2) and round 6 (`rules/rehear/cert`) accepted; base files'
  sha1 unchanged.

## Base reproduction (the acceptance test of r7_run)

`stage7.py base` (no delta: every table a hard link to final2, empty history_claim / joined) +
`NOBUILD=1 r7_run.sh base` (round-6 runner binary 69ad4a6949bd, built 17:05): **certs, classes, findings, horty,
splits, status, status_lines byte-identical to `round6/history/out/final2`; summary.tsv identical except its 16
`load_ms` / `run_ms` lines.** `score7.sh base` reproduces the round-6 Shepardized dev headline exactly (NEG strict
105/254, lenient 112/254, precision 105/111, CLEAN 9,698/9,704).

Pipeline with a delta (23:16): `stage7.py orderhead --delta agents/orderhead/cert` + `NOBUILD=1 r7_run.sh orderhead`
(round-6 runner, which knows no claims): status, findings, classes, status_lines, splits, horty byte-identical to
base; certs.tsv = base + 119 lines `history h7:… partNotMajority` (expected until the round-7 runner reads
history_claim.tsv). Expected with the round-7 runner: those 119 rows `ok` / `noAuthority`, everything else as base.

## r7_run.sh

- Base mirror `~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/base_r7_final2/`: realpath symlinks of data_r6_final2's
  links + copies of its staged tables; every file `cmp`-checked against Windows `round6/history/stage/final2`
  (29 tables, marker `.verified`; built once under `~/caselaw2/r7_base.lock`).
- `data_r7_<name>`: symlinks to the base mirror, the ten staged tables copied (empty history_anchor / history_claim /
  joined left out). Refuses to sync/build without `round7/LEAN_READY` (exit 3) unless `NOBUILD=1`.
- Build under `~/caselaw2/r6_build.lock` (the same lock as r6_run.sh: one Lean build at a time across both scripts).
- The binary is copied to `~/caselaw2/r7_bin/caselaw2_<name>` before the run, so a concurrent rebuild cannot change
  it mid-run. NOBUILD runs run_lean.sh's steps directly with that copy (no `lake` call at all); a built run calls
  the lean agent's run_lean.sh. Output + `lean.log` + `RUN.txt` (which binary) → `round7/out/<name>/`.

## score7.sh

fresh lists dev (`round5/gold_fresh/score_fresh.py --split dev`, label `r7_<name>`; its three files are moved from
`round5/gold_fresh/dev/results/` into `results/<name>/fresh_dev.*`, so round 5's folder is left as it was), both date
views (`round7/score_fresh7.py --view both --out results/<name>/fresh7`), no-leak, holdout notes (`--out
results/<name>/holdout`), behaviour (`beh`), SCDB / CRS (eval/score.py + old_by_class7.py), Shepardized dev
(score_hist_dev.py → `results/<name>/shepardized/`), `summary.txt`. No sealed / test split anywhere.
`score7.sh base`: 65 s; `round7/results/base/summary.txt`.

## For the lead

1. **orderHead: the CAP form is not in `order_line`** — 119 rows now; 8,166 with three more phrases
   ("petition for writ of certiorari to the", …): `agents/orderhead/NOTES.md`. The cue table is the `lean` agent's.
2. **B4 (f)**: 204,371 of 305,237 Supreme Court orders (67.0%) have no unique match to a lower-court decision
   (definition and breakdown in `agents/orderhead/NOTES.md`).
3. Treatments conflicts: certify7 applies only base skip + duplicate to treatments rows (no positive/negative
   conflict rule for treatment kinds was specified).
4. A doctrine label shared across two certify7 runs (two delta folders) is caught by Lean (`doctrineAmbiguous`), and
   stage7's MANIFEST counts compact labels with two targets (`doctrine class lines …`) — it does not drop them.
5. Disk: a variant with only history changes costs ~330 MB on C: (history, cert_text, window_sha written; the rest
   hard links); `stage/orderhead` exists for the Lean smoke run once LEAN_READY is set.
