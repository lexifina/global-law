# Agent `ref8` (round 8): the Python reference for round-8 rules (single writer of tools/caselaw2/ref/)

Read `round8/DESIGN8.md` (all; §4 is the first rule) and `round8/agents/COMMON.md`. Folder: `round8/agents/ref8/`
(NOTES.md). You write only `tools/caselaw2/ref/` (and `tools/caselaw2/fuzz/`, universe generators in your folder).
**Never open any `.lean` file, anything under `LegalProofs/`, `round7/LEAN7.md` or `round8/LEAN8.md`.** Work from the
design texts (DESIGN8 §4; DESIGN7 §0–3; round-6/5 designs and REF_QUESTIONS) and the round-7 reference itself, as the
round-7 agent `ref` did (`round7/agents/ref/NOTES.md`, `REF_QUESTIONS7.md`, `make_r7.py`, `r7_drt_run.py`).

Do:
1. Backup the reference/fuzz files to `round8/pre/ref/`, `round8/pre/fuzz/`.
2. Implement DESIGN8 §4 in the reference (`history_bridge.tsv`, `checkBridge`, `bridge_cue`, presence rule). Open
   readings → `REF_QUESTIONS8.md` (Q8-n) with your reading; the lead answers if one changes an effect.
3. Universes: extend the generator with bridge rows (valid; each failure reason; presence/absence), keep them in your
   folder; self-check expectations.
4. Differential (after `round8/LEAN_READY` exists; the round-7 binary meanwhile for the regressions): the 267 round-6
   universes + round-7 kept universes: 0 disagreements; round-8 universes: report every difference; real data: run
   `wsl/r8_run.sh <variant> ref` on a variant the lead names (or `base`), diff.py must show only the 2 known New
   Jersey witness rows.
5. Further rules may arrive by message from the lead; same procedure.

Final report: what was implemented, Q8 readings, universes and differential results.
