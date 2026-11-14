# Agent `contradict` (round 8, move 6): base rows contradicted by a newer two-quote row

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/contradict/` (NOTES.md).

## Background
`round7/agents/b4sc/NOTES.md`, section "Base rows contradicted by a new two-quote row": round-6 certify6 rejected
482 new anchored rows (`conflictBase`) that contradict a base row of the same (by, target) pair; in 436 below_other
pairs the new judgment quote lies after the base quote in the same text (the base row quoted an earlier sentence).
Proposed rule ("the final judgment line decides"): the new row replaces the base row when (i) it passes every check,
(ii) its judgment quote is the acting opinion's final own disposition and lies after the base row's quote in the same
text, (iii) if scopes differ the new one is `unknown`. Round 6 read 12: 10 favoured the new row.

## Do
1. Rebuild the pairs against v3 (base rows still present and admitted in `round7/out/v3/certs.tsv`; new rows from the
   round-6 rejected set, `round6/history/` — find the conflictBase rejects and `disagreements.tsv`). Count per sub-case.
2. Blind audit of ~40 pairs first (random by fixed seed, stratified by court/decade): build the pack under
   `round8/audit/contra/` with the round-8 audit tooling (`round8/audit/HOWTO.md`, wait for `round8/audit/READY`; if
   it lacks a two-quote form, write a small pack builder in your folder following its conventions). Each item shows
   the acting text around both quotes (both quotes, unlabelled, order as in the text) and the target's identity, and
   asks: what did the acting court do to the target as its own act (reversed / vacated / affirmed / modified / mixed,
   and scope)? Two blind opus auditors, decoys included. The auditor never learns which quote is the base row.
3. Decide by the audit: if the new row is right in ≥ ~90% of pairs where they differ, write the replacement as a
   general rule script producing `remove_ids.txt` (base ids) + a delta folder (new rows, certify8); otherwise report
   and stop. If the audit supports it, run a second fresh audit of ≥ 80 replaced pairs before installation.
4. Measure (stage with `--remove` + `--delta`, run, score): Shepardized dev precision/recall, CLEAN kept clean, FJC and
   SCDB h0 precision/recall (`round8/results/<v>/bench/`).

Final report: pair counts, audit (k/n, Wilson), decision, delta + remove files, dev/h0 effect.
