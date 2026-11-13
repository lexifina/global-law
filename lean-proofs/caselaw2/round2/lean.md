# Round 2, agent `lean`: log

Owner of the Lean model, the runner, the audit, the fixtures and the reference engine. Times are local, 12 Nov 2026.

## Task A: split successors without a firm adoption row (DEVIATIONS 73, closed)

**Question.** Does a court created by splitting an old court hold the old court's decisions as its own precedent
when no adoption is shown?

**Sources** (4 web searches, the budget; primary first).
- *Bonner v. City of Prichard*, 661 F.2d 1206, 1209 (11th Cir. 1981) (en banc): the Eleventh Circuit took the
  former Fifth Circuit's decisions by its own decision. *Estate of McMorris*, 243 F.3d 1254, 1258 (10th Cir. 2001):
  the Tenth Circuit, made from the Eighth in 1929, did not take the Eighth's (doctrine F10). A split alone
  therefore transfers nothing.
- Alabama Act No. 987 of 1969, effective 1 Oct 1969. *Coalite, Inc. v. Aldridge* (Ala. Civ. App. 1969): the case
  "was transferred from the Court of Appeals, now the Court of Criminal Appeals, to this, the Court of Civil
  Appeals, on October 1, 1969, pursuant to Act 987, Acts of Alabama 1969" (found through three case-law mirrors:
  law.counselstack.com, app.midpage.ai, hallapproved.com). The Alabama judicial branch history page
  (judicial.alabama.gov/Appellate/CR_History, as quoted in the search results; the site refused a direct fetch):
  the three judges of the Court of Appeals became the first judges of the Court of Criminal Appeals.
- The courts' own words in the corpus (certified treatment rows): Ala. Crim. App., node 110729 (17 Aug 1971): "We
  overrule Willis, supra, so far as it might restrain us from acting ex mero motu" (a 1964 Court of Appeals
  decision). Ala. Civ. App., node 106047 (29 June 2007): "to the extent that Colquitt is inconsistent with our
  opinion in this case, Colquitt is overruled" (a 1964 Court of Appeals decision).
- Not found: any statute or decision saying the Court of Civil Appeals adopted the old court's decisions.

**Decision.**
1. Reading (both sides): a `split` succession row never by itself makes the new court hold the old court's
   decisions. Only an adoption row does; each run reads its own adoption rows. The Lean already did this. The
   reference changed (R2-73).
2. The Court of Criminal Appeals is the old Court of Appeals continued. It holds its own decisions. The adoption
   row is verified.
3. The Court of Civil Appeals was a new court. No adoption is shown. Its row stays U.

**Data edit (one row, `data/adoption.tsv`, 21:53, by tmp + rename; original saved as
`data/adoption.pre_round2.tsv`).** Courts agent: please keep it.

    before: 3	1	19690930	all	binding	successor intermediate courts (criminal)	U
    after:  3	1	19690930	all	binding	Act No. 987 (1969), eff. 1 Oct 1969: the Court of Appeals continued as the Court of Criminal Appeals (same court, same judges; Coalite, Inc. v. Aldridge, Ala. Civ. App. 1969: "the Court of Appeals, now the Court of Criminal Appeals"), so its decisions are its own precedent (H3); round2 lean, DEVIATIONS 73	S

Suggestion for the courts agent (not done here): `succession.tsv` row `1 -> 3` is typed `split`; by Act 987 it is
a continuation (`rename`). With the adoption row tagged S the two give the same verdicts.

## Task B: status per line of authority everywhere (DEVIATIONS 74-79)

**Reading.** DEVIATIONS 74 (views, lines, original court gone, dates outside an epoch), 75 (`status_lines.tsv`), 76
(treatment-level families), 77 (conflicts, splits), 78 (Horty bases, `horty.tsv`), 79 (generator). The reference was
written from these by a separate subagent that did not read the Lean (REF_NOTES "Revisions: round 2").

**Output format (departure from the brief's wording).** The per-heir rows are in a new file `status_lines.tsv`
(the `status.tsv` columns plus a last column `line` = `orig` or the heir's court id), not in `status.tsv`. Reason:
`score.py`, `audit_score.py`, `horty_py.py`, `make_report.py` and three hunt scripts read `status.tsv` by position
and would take a line's row for the union row. `status.tsv` is byte for byte unchanged, so none of them was edited.
Also new: `horty.tsv` (family, court, verdict, cases, firm) and the summary counter `status_line_rows`.

**Lean.**
- New module `Spec/Lines.lean`; `Run.lean` edited (status rows, treatment-level families, contraryBinding,
  conflicts, splits, Horty); `Core.lean` and `Exec/Verdicts.lean` import it; `Examples.lean`, `Mutants.lean`.
- Theorems: 114 before, **137** after. The 23 new ones (all in `Spec/Lines`, locked, STATEMENTS.log 22:08):
  `filter_congr_mem`, `any_congr_mem`, `reaches_congr`, `statusFor_congr`, `lineStatus_heir_agrees`,
  `lineStatus_orig_agrees`, `lineStatus_all`, `linesOf_all`, `status_filter_le`, `statusFor_le_status`,
  `good_in_every_line`, `goodIn_ignores_unreaching`, `goodIn_all`, `effectsFor_known`, `mem_heldIn_iff`,
  `heldIn_ignores_unreaching`, `conflict_in_line_ignores_unreaching`, `heldIn_all`, `heldUnion_sub_heldIn`,
  `mem_lineBase_iff`, `lineBase_all`, `unionBase_sub_lineBase`, `lineBase_consistent_union`.
- Mutants: M23 line rows report the union status; M24 splits and conflicts on the union status; M25 Horty base
  keeps precedents overruled in the line; M26 heir rows drop effects that reach every line. Four new properties.
  Kill matrix 26 x 26, complete (the three matrix `#guard`s pass).
- `#guard`s: 176 before, 211 after (35 new in `Examples.lean`: Bonner / Salinas-Adamson rows, conflict and Horty
  base by line, M.A.P., Federal Circuit / CCPA, dates outside an epoch, a court with no epoch reads the union).
- No locked statement changed. No sorry, axiom or native_decide. `audit.py check`: 137 theorems, 0 problems.
- `fixtures/make_fixtures.py`: a per-line case (nodes 20-24, issue `fx.laches`, holdings hL20 / hL22, treatment 7).
- `run_lean.sh` (two lines: merge `status_lines` and `horty`). It is not in my ownership list; the runner cannot
  ship the new files without it.
- New helper scripts: `wsl/r2_verify.sh` (regress / sweep on 24 cores), `wsl/r2_cmp.sh`, `wsl/r2_show.sh`,
  `wsl/r2_show2.sh`.

**Reference** (subagent; `tools/caselaw2/ref/`): `precedent_ref.py` (R2-73 split rule, views, `status_lines.tsv`,
76, 77, Horty bases and `horty.tsv`, b5), `diff.py` (`lines`, `horty`; skipped when a side lacks the file),
`gen.py` (`lines` layer, `--no-lines`, `LEAN_HEADERS`), `drt.py` (`FILES`), `REF_NOTES.md`. Its own checks: old
fixtures and the 111 regression universes unchanged except one `splits.tsv` history date; `--no-lines` reproduces
old universes on 8 seeds; 200 universes with the layer on, 198 with per-line rows, 64 with the original court gone.

**Results** (WSL, 24 cores).

| Check | Result |
|---|---|
| Build | green |
| `audit check` -> `audit lock` -> build -> `audit check` | 137 theorems, 4 with no axioms, 0 statement changes, 0 problems |
| Fixtures | 0 disagreements (lines 4 keys, horty 3 keys compared) |
| Regression set, 111 universes (`regress9`, `regress10`) | 0 disagreements; 52 lines keys compared |
| Sweep 54000-54099, n = 60 (`drt7a`) | 8 universes: status 5, findings 3, lines 3, splits 1, conflicts 3 keys |
| Same sweep after reference fix b5 (`drt7b`) | **3 universes: splits 1/1,924, conflicts 3/859; status, findings, certs, lines (1,409), horty (298) all 0** |
| Real data, Lean only, snapshot 22:09 (`real18pre`) | `status.tsv` = real17's but 5 firm flags; findings: 5 firm flags, 1 new `atRisk soft` row; 546 per-line rows for 41 decisions (34 Eleventh Circuit, 3 D.C., 3 Alabama, 1 New York); 44 Horty bases. 3 min 40 s |
| Real data, reference only, before / after (no edges) | identical but the Civil Appeals firm flag (1 -> 0) and the same new `atRisk soft` row |

Not run (time box, left to the coordinator): the 500-round sweep and the two-sided real diff `real18a`.

**Task A residual.** Expected 0 of the 11 `firm` keys: seen one side at a time (Lean: 10 Criminal Appeals keys now
firm = 1; reference: the Civil Appeals key now firm = 0), not yet in a two-sided diff.

## Commands that work

    cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2
    ./run_lean_wsl.sh build
    ./run_lean_wsl.sh audit check
    ./run_lean_wsl.sh sync data                                   # note the snapshot time
    ./run_lean_wsl.sh sh 'bash wsl/verify.sh fixtures'
    ./run_lean_wsl.sh sh 'bash wsl/r2_verify.sh regress regress11'              # 24 jobs, about 40 s
    ./run_lean_wsl.sh sh 'bash wsl/r2_verify.sh sweep 55000 500 drt7c'          # 100 rounds take about 70 s
    ./run_lean_wsl.sh sh 'bash wsl/verify.sh real real18a'                       # Lean 8 shards + reference + diff
    ./run_lean_wsl.sh sh 'bash wsl/collect.sh real18a'                           # copies lean/*.tsv to out/

`collect.sh` copies every `lean/*.tsv`, so `out/status_lines.tsv` and `out/horty.tsv` arrive with the rest. The diff
prints two more lines (`lines`, `horty`). `build` and `audit` sync the code first; `sh` does not, so run
`./run_lean_wsl.sh sync code` after any edit made outside them.

## Next round

1. **Conflict at an adopter of a ceased court** (sweep seeds 54044, 54056; 3 keys, reference only). A decision of
   the ceased court, good law only in that adopter's line, against SCOTUS holdings the other way. The Lean lets
   SCOTUS prevail by precedence; the reference reports both answers. Likely about displacement when the decision's
   own court has no epoch on asOf (67). Not triaged.
2. **Split Eleventh Circuit / E.D. La.** (seed 54046; 1 key, reference only), in a universe where the Fifth
   Circuit's epoch ended and a reorganised court took its place. Not triaged.
   Both classes arise only in the new `lines` generator layer. The sweep will show them at about 3 universes in 100
   until they are settled; with `--no-lines` universes they cannot arise (drt.py has no switch for that yet).
3. Readings the reference chose where 74-78 were silent (REF_NOTES round 2; they agree with the Lean on every
   compared key so far, but are not written into DEVIATIONS): a reach with the original line and every heir reached
   is `all`; an examined court with no epoch on asOf gives no Horty base; unknown force keeps a case out of a base.
4. `succession.tsv` `1 -> 3` (Alabama) is typed `split`; Act 987 makes it a continuation. For the courts agent.
5. The self bases (`hortySelfInconsistent`) and the Horty finding rows stay Lean only.
6. `TRUST.md` "Tested only" still has two stale lines from before WSL (run B's Lean half, Horty not exercised).

## After the coordinator's 500-round sweep (drt8: 15 universes)

- `firm` flags (7 rounds), Horty bases missing in the reference (3), one split: one root, reference wrong (b6). Its
  reading "a decision of a court ended by a split has no holder" is replaced by: the deciding court on the decision's
  date stays the holder of its own decisions. Fixed by the reference subagent (`holders`).
- Final: `regress13` 0 disagreements. Sweep `drt9` (57000-57499): 8 of 500 universes, **conflicts 17/4,977 only**;
  status, findings, certs, splits, lines (7,332 keys), horty (1,450 keys) all 0.
- Open (Next round 1, unchanged): conflict rows only in the reference at an adopter of a ceased court (courts 1222,
  1223, 1203 in the generator). Not triaged. "Next round" item 2 (the split) is closed by b6.
- Courts agent notes: (i) both sides drop `citesLaterNegated` when the citing court has no epoch on the negating
  date (no disagreement in any run; not changed); (ii), (iii) not examined.
