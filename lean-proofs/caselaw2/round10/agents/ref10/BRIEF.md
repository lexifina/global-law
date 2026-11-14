# Agent `ref10` (round 10): the Python reference for round-10 rules, and the differential

Read `round10/DESIGN10.md` and `round10/agents/COMMON.md` (disk rule!). Folder `round10/agents/ref10/` (NOTES.md).
You are the ONLY writer of the Python reference `global-law-lean/lean-proofs/tools/caselaw2/ref/`
(`precedent_ref.py`, `diff.py`, `labels.json`, `REF_NOTES.md`). **You never read the Lean sources**
(`LegalProofs/CaseLaw2/**`, `round10/LEAN10.md`, `round9/LEAN9.md` §1–2, `round8/LEAN8.md` §1–2): you implement from
DESIGN10 sections alone, and ask the lead about anything they leave open (write `round10/agents/ref10/REF_QUESTIONS10.md`;
continue on a stated reading). Model on round 9's `round9/agents/ref9/` (NOTES.md, NOTES2.md, BRIEF.md, make_r9.py,
difftest9*.sh, run_all9*.sh, check_regress9.*). Put new generator/universe code in NEW files (round 9's sealed run
was once refused because `make_r9.py` changed after the freeze; after `round10/FREEZE.md` exists, change nothing that
it hashes).

Do:
1. Backup the reference to `round10/pre/ref/` first.
2. Implement DESIGN10 §4 (remand bridge), round-10 mode by presence (absent ⇒ the round-9 reference output exactly;
   check with the stored regressions and on real data v9c: the reference on `round9/stage/v9c` must equal
   `round9/out/v9c`). Further sections (§5 …) arrive in `round10/agents/ref10/INBOX.md` from the lead; check it every
   ~15 minutes.
3. Universes: a generator for round-10 cases (remand lines: each failure reason, duplicates, bad lines, absent table,
   rows without a line, a failing round-9 verdict with a line) with expectations; self-checks; once `round10/LEAN_READY`
   exists, the differential against the round-10 Lean binary (`~/caselaw2/r10_bin/caselaw2_lean10`) on kept universes,
   a sweep, a probe set, the earlier universes, and real data (`wsl/r10_run.sh <variant> ref` with the lead's variants;
   a separate difftest folder per variant name). Every disagreement explained (which side is wrong against DESIGN10).
Report: what was implemented, readings, universes and disagreement counts, real-data diff.
