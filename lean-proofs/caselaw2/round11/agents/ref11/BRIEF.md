# Agent `ref11` (round 11): the Python reference for round-11 rules, and the differential

Read `round11/DESIGN11.md` and `round11/agents/COMMON.md` (disk rule!). Folder `round11/agents/ref11/` (NOTES.md, a
line every 10 minutes). You are the ONLY writer of the Python reference `global-law-lean/lean-proofs/tools/caselaw2/ref/`
(`precedent_ref.py`, `diff.py`, `labels.json`, `REF_NOTES.md`). **You never read the Lean sources**
(`LegalProofs/CaseLaw2/**`, `round11/LEAN11.md`, `round10/LEAN10.md` §1–2, `round9/LEAN9.md` §1–2): implement from
DESIGN11 §5 sections alone; ask the lead about anything they leave open (`round11/agents/ref11/REF_QUESTIONS11.md`;
continue on a stated reading). Model on round 10's `round10/agents/ref10/` (NOTES.md, BRIEF.md, make_r10.py,
difftest10.sh, gen10.sh, kept10.sh, check_regress10.*, realv9c.sh). Put new code in NEW files (after
`round11/FREEZE.md` exists, change nothing it hashes).

Do:
1. Backup the reference to `round11/pre/ref/` first.
2. Implement each DESIGN11 §5 section, round-11 mode by presence (absent ⇒ the round-10 reference output exactly;
   check with the stored regressions and on real data: the reference on `round10/stage/v10d` must equal
   `round10/out/v10d`). Further sections arrive in `round11/agents/ref11/INBOX.md`; check it every ~10 minutes.
3. Universes: a generator for round-11 cases (each failure reason, duplicates, bad lines, absent table, rows
   without a line / claim, a failing round-10 verdict with a line) with expectations; self-checks; once
   `round11/LEAN_READY` exists, the differential against `~/caselaw2/r11_bin/caselaw2_lean11` on kept universes, a
   sweep, the earlier universes, and real data (`wsl/r11_run.sh <variant> ref` on the lead's variants; a separate
   difftest folder per variant name). Every disagreement explained (which side is wrong against DESIGN11).
Report: what was implemented, readings, universes and disagreement counts, real-data diff.
