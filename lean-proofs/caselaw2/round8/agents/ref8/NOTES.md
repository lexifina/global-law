# Round 8, agent `ref8`: the Python reference for round-8 rules (bridge evidence, DESIGN8 §4)

Written from `round8/DESIGN8.md` (all), `round7/DESIGN7.md` §0-3, `round6/history/DESIGN6.md` §4,
`round8/agents/orderdock/LEAN_REQUEST.md` (background; DESIGN8 §4 is the contract) and the round-7 reference and
harness (`round7/agents/ref/`). No `.lean` file, nothing under `LegalProofs/`, not `round7/LEAN7.md` and not
`round8/LEAN8.md` were opened. Open readings: `REF_QUESTIONS8.md` (Q8-n) in this folder.

## Log (clock times from `date`)

- 00:47 started; read DESIGN8, COMMON, BRIEF, round-7 ref NOTES / REF_QUESTIONS7, DESIGN7 §0-3, DESIGN6 §4, the
  reference (`precedent_ref.py` history path: `check_cert`, `check_anchored`, `admit`), `make_r7.py`,
  `difftest7.sh`, `r8_run.sh`.
- 00:49 backup: `tools/caselaw2/ref/*.py`, `REF_NOTES.md`, `labels.json` -> `round8/pre/ref/`; `fuzz/*.py` ->
  `round8/pre/fuzz/` (lean8 had already copied the same files there at 00:48; the copies are identical, untouched
  since round 7). `cue_table.json` has no `bridge_cue` / `bridge_max_len` yet: the reference reads them from the
  JSON first and falls back to DESIGN8 §4's lists.
- 00:50-00:56 reference, DESIGN8 §4: `Data` loads `history_bridge.tsv` (bad / unknown id / duplicate, counters,
  W's sha kept), `Engine.check_bridge` (steps 1-7), `admit` uses it for a history row with a bridge line (the
  anchor line of such a row is not used, Q8-2), `ref_stats.tsv` gains `bridge_rows`, `bridge_unknown_ids`,
  `bridge_duplicates`, `bridge_bad_rows` when the file has a line. `diff.py`: SUMMARY_KEYS8 / BAD_ROWS_KEY
  (`history_bridge.tsv` and `history_bridge`); `labels.json`: the bridge reasons.
- 00:56 lead message: DESIGN8 §5 (D8-5) `anchorWide`. Implemented: claim value `anchorWide` (HCLAIMS), the anchor
  cue list `anchor ++ anchor_wide` in `check_anchored` only with the claim, counter `hclaim_anchorwide_unused`
  (written only when some kept claim is anchorWide; Q8-11).
- 00:58-00:59 `make_r8.py` (generator: gen / check / empty / report; imports round 7's `make_r7.py` helpers).
  Self-check 330 expectations / 45 counters, 0 differ; `empty` (bridge absent / empty / blank, anchorWide lines
  dropped, against `round8/pre/ref`): 8 universes, 0 differing files.
- 00:59-01:00 `check_regress8.sh` (WSL, snapshot `~/caselaw2/r8ref`): the current reference on 435 universes (267
  round-6 + 18 round-7 kept + 150 round-7 sweep r7sw3*), no round-8 table: bytes against the stored round-7
  reference output 435/435 the same; canonical diff against the stored round-7 Lean output: only the 7 known
  witness-class W universes (kept u90001, r7sw3 u94016/u94043/u94052, r7sw3p p95009/p95013/p95028; findings 5,
  certs 6, classes 6 keys), as in round 7's run 3. (The "ROUND-8 INPUT PRESENT" flags of that run came from a
  detector not yet edited; fixed.)
- 01:01 lead message: (1) step 5b `bridgeChain` (D8-9); (2) ruling on step 6: the first compact position after p2
  where an index key starts, the longest key there. Both implemented (01:01-01:02); Q8-6 updated, Q8-13 added.
  `cue_table.json` got `bridge_cue`, `bridge_max_len`, `anchor_wide` from lean8 at 00:58 (same lists as DESIGN8);
  the reference reads all three from the JSON (`R7_CUE_SOURCE` = json); `ref/cue_table.py` is not regenerated.
- 01:02-01:03 generator: chain cases (`br_chain`, `pr_chain_ambig`, `pr_chain_xparallel`), `br_parallel_after`;
  prefix probe expectations per the ruling. Kept universes `universes/` (9: v80000-80003 main, q81000-81002 probe,
  g82000-82001 fuzz K=8): self-check 363 expectations, 0 differ; 51 counters, 0 differ (`check_kept_cases.txt`);
  `empty`: 9 universes, 0 differing files (`check_empty.txt`).
- 01:02 real data: `round8/stage/ref8_base` (stage8.py, no delta = base v3); mirror ref synced
  (`~/caselaw2/lean-proofs/tools/caselaw2/ref`, only ref/), `NOBUILD=1 wsl/r8_run.sh ref8_base ref` started.
- `difftest8.sh` written (setup / refsync / regress / kept / sweep / all) for when `round8/LEAN_READY` exists.
- 01:06 lead ruling: Q8-13 literal (X's own parallel citations between X's citation and the cue fail bridgeChain); the code already reads it so. Sent the lead the 68-of-880 finding on orderdock's strict lines (67 bridgeTarget: printed reporter forms with no index key; 1 bridgeActor).
- 01:02-01:08 real data, `NOBUILD=1 wsl/r8_run.sh ref8_base ref` (frozen r7v3 Lean, base v3 data, current reference): diff.txt (`round8/out/ref8_base/diff.txt`) shows only the 2 known witness rows tw:3991335:4086271:4616:4089451 and tw:4018149:4006682:13821:4061823 (certs 2, classes 2) and what follows from them (status 2+2, findings 17, recognised_rows 6478/6480), as at the end of round 7.
- 01:08 started: `r8_run.sh ref8_bridge ref` (stage = v3 + orderdock cert_bridge + cert_bridge_lines, 880 bridge lines; frozen Lean, so only the reference's bridge verdicts are meaningful), then `check_regress8.sh regress8b` (after the 5b / step-6 changes).
- 01:09-01:11 lead asked for the §4 check on `round8/stage/orderdock_d` (879 regenerated lines): `bridge_verdicts8.py` (Data + admit only): 879 kept, 0 bad / unknown / duplicate; verdicts ok 879 (certDenied 811, vacated 54, reviewDismissed 13, reversed 1). Results `results/bridge_verdicts_orderdock_d.{txt,tsv}`. Position semantics sent to the lead (Q8-4).
- 01:08-01:12 `check_regress8.sh regress8b` (after 5b / step 6): 435/435 byte-identical to the stored round-7 reference
  output; canonical diff against the stored round-7 Lean: the same 7 W universes only. `r8_run.sh ref8_bridge ref`
  ran (frozen Lean; reference output in the mirror `difftest/r8_ref8_bridge`).
- 01:12 lead message: DESIGN8 §6 (D8-12) claim `oldCircuit`. Implemented 01:13: HCLAIMS + `OLD_CIRCUIT` (JSON key
  `old_circuit`, fallback the design's two triples), `same_case_power(B, X, claims)` (Q8-14); `hist_rows` passes the
  row's claims. Generator: courts 3901-3908 appended to courts2.tsv, `oc_*` cases (each side of both cut-offs, wrong
  pairs, appeals-court target, B date 0, no claim, claim on a treatments id) with `neg` / `notneg` status checks.
- 01:15 lead message (lean8): ASCII-only lower / alnum; the bridge code already is (Q8-15). Probes `pr_nonascii_ok`,
  `pr_kelvin_x`, `pr_arabic_o`, `pr_dotted_i`. Q8-4 accepted as D8-13.
- 01:15 kept universes regenerated (same seeds): self-check 467 expectations, 0 differ; 52 counters, 0 differ; 56
  never-negative targets, 0 negative; 32 negative-status expectations, 0 differ. `empty` (bridge / anchorWide /
  oldCircuit removed; absent, empty, blank): 9 universes, 0 differing files.
- 01:16 `check_regress8.sh regress8c` (with oldCircuit): 435/435 same bytes, the 7 W universes only. Mirror ref re-synced.
- 01:20 wider self-check (scratch, seeds 84000-84015 main + 85000-85007 probe): 1,768 expectations, 0 differ; 181 counters, 0 differ; 224 never-negative, 0 negative; 128 negative-status, 0 differ. Waiting for round8/LEAN_READY.
- 01:38 round8/LEAN_READY appeared; difftest8.sh all started.
- 01:38-01:39 `difftest8.sh setup` (snapshot ~/caselaw2/r8ref, runner build from LEAN_READY sources; snapshot sha1 in
  results/snapshot.sha1). `kept r8kept1`: 9 universes, 3 with a disagreement, all one case: `pr_chain_ambig` (Lean ok,
  reference bridgeChain; plus the status / finding of its target). Cause: the Lean drops an ambiguous compact key
  (two or more nodes) when it loads the index; the reference had counted such keys in 5b and step 6. Reference
  changed to the Lean's data model (Q8-16; probe `pr_actor_after_ambig` added); every other case agrees: all bridge
  reasons incl. 5b, positions (pr_coord), prefixes, non-ASCII probes, anchorWide, oldCircuit statuses.
- 01:39-01:40 kept universes regenerated: self-check 470 expectations, 0 differ; 53 counters, 0 differ; 32 neg / 56
  notneg status expectations, 0 differ. `refsync`, `kept r8kept2`: 9 universes, 0 with a disagreement.
- 01:40 started (background): sweeps r8sw1 (84000, 40 main), r8sw1p (85000, 20 probe), r8sw1f (86000, 30 fuzz K=8),
  then regress r8reg1 (435 earlier universes, both engines, round-8 code, no round-8 table).
- 01:40 lead ruling D8-15 = Q8-16 as fixed. Mirror ref synced (da8e17ce). The lead's v8e real-data run had already started with the mirror's previous copy (b0fb1e32, pre-Q8-16); v8e's index has no compact key with two nodes (MANIFEST), so Q8-16 cannot change its bridge verdicts.
- 01:40-01:42 differential against the round-8 Lean (runner of LEAN_READY 01:38):
  | tag | universes | disagreeing | what |
  |---|---|---|---|
  | r8kept2 (9 kept) | 9 | 0 | everything agrees |
  | r8sw1 main 84000-84039 | 40 | 3 | W only (base witness rows tr<n>: witnessNoStanding vs noAuthority; atRisk inferred) |
  | r8sw1p probe 85000-85019 | 20 | 0 | |
  | r8sw1f fuzz K=8 86000-86029 | 30 | 2 | base-layer atRisk findings only (g86000 inferred, g86013 citesLaterNegated) |
  | r8reg1 (435 earlier universes, both engines rerun) | 435 | 7 | the 7 known W universes, as in round 7 |
  Self-checks: r8sw1 3,920 expectations / 312 counters / 560 notneg / 320 neg, 0 differ; r8sw1p 520 / 136, 0 differ.
  Every round-8 case (bridge, anchorWide, oldCircuit, probes) agrees in every universe.
- 01:42-01:43 `dirs r8wit1` (scratch_wit/: g86000, g86013, v84006 with history_bridge.tsv and the anchorWide /
  oldCircuit claim lines removed): the same base-layer differences remain, so they are round-5 witness-layer
  differences (the open class W of round 7), not round 8.
- 01:43-01:44 the lead's real-data differential `r8_run.sh v8e ref` (built round-8 runner; mirror reference
  b0fb1e32 = before Q8-16, which cannot matter on v8e: no ambiguous key) — `difftest/r8_v8e/diff.txt` in the mirror:
  the 2 known New Jersey witness rows (tw:3991335:4086271:4616:4089451, tw:4018149:4006682:13821:4061823) and their
  consequences, plus ONE more row of the same New Jersey successor-court class: ownact operative row
  t8:4058244:4016514:17127 (acting 1099 NJ Superior Court Appellate Division, 1962, on target 4016514 of 1095 the old
  NJ Supreme Court, 1948). Lean noAuthority; reference ok: `can` gives yes (9.23.none) with all tables (the U-tagged
  succession 1095 -> 1099) and no (T2.notHigher) with the firm tables. Effects: status 4016514 partial (ref) vs none,
  atRisk:claim 4058244 4016514 (Lean only), operative_rows 1072 vs 1071. No bridge / anchorWide / oldCircuit row
  differs.

## Files

- Reference (single writer): `tools/caselaw2/ref/precedent_ref.py`, `diff.py`, `labels.json`, `REF_NOTES.md`
  (round-8 section). Pre-round-8 copies: `round8/pre/ref/`, `round8/pre/fuzz/` (fuzz unchanged).
- This folder: `REF_QUESTIONS8.md` (Q8-1..Q8-16), `make_r8.py` (generator: gen / check / empty / report),
  `difftest8.sh` (WSL differential driver), `check_regress8.py` / `check_regress8.sh` (reference-only regressions
  against stored round-7 outputs), `bridge_verdicts8.py` (reference bridge verdicts on a staged dir), `universes/` (9
  kept: v80000-80003, q81000-81002, g82000-82001), `check_kept_cases.txt`, `check_empty.txt`, `results/` (regress8a-c,
  r8kept1-2, r8sw1*, r8reg1, r8wit1, bridge_verdicts_orderdock_d), `fail/` (disagreeing universes), `scratch_wit/`.
- Stages written: `round8/stage/ref8_base` (= base v3), `round8/stage/ref8_bridge` (v3 + orderdock cert_bridge +
  cert_bridge_lines, 880 lines; superseded by orderdock_d).

## How to rerun

`MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round8/agents/ref8/difftest8.sh all'`
(after a Lean change: `setup`; after a reference change only: `refsync`; then `kept`, `sweep`, `regress`).
