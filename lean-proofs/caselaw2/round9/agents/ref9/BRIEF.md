# Agent `ref9` (round 9): the Python reference for round-9 rules, and the differential

Read `round9/DESIGN9.md` and `round9/agents/COMMON.md`. Folder `round9/agents/ref9/` (NOTES.md). You are the ONLY
writer of the Python reference `global-law-lean/lean-proofs/tools/caselaw2/ref/` (`precedent_ref.py`, `diff.py`,
`labels.json`, `REF_NOTES.md`). **You never read the Lean sources** (`LegalProofs/CaseLaw2/**`, `round9/LEAN9.md`,
`round8/LEAN8.md` §1–2): you implement from DESIGN9 sections alone, and ask the lead about anything they leave open
(write `round9/agents/ref9/REF_QUESTIONS9.md`; continue on a stated reading).
Model on round 8's `round8/agents/ref8/` (NOTES.md, BRIEF.md, make_r8.py, difftest8.sh, check_regress8.*).

Do:
1. Backup the reference to `round9/pre/ref/` first.
2. Implement DESIGN9 §4 (part zones), round-9 mode by presence (absent ⇒ the round-8 reference output exactly; check
   with the stored regressions). Further sections (§5 joined gap, §6 New Jersey successor authority, §7 …) arrive in
   `round9/agents/ref9/INBOX.md` from the lead; check it every ~15 minutes.
3. Universes: a generator for round-9 cases (zones: inside, straddling, other part, overlapping/malformed, missing;
   then each later rule) with expectations; self-checks; once `round9/LEAN_READY` exists, the differential against the
   round-9 Lean binary (`~/caselaw2/r9_bin/caselaw2_lean9`) on kept universes, a sweep, a probe set, the 435+ earlier
   universes, and real data (`wsl/r9_run.sh <variant> ref` with the lead's variants). Every disagreement explained
   (which side is wrong against DESIGN9).
Report: what was implemented, readings, universes and disagreement counts, real-data diff.
