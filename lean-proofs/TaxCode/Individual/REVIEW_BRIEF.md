# Brief for reviewers (step 4 of copy / test / prove / check)

You did not write the group you are reviewing. Your job is to try to break it. Read `TaxCode/Individual/BRIEF.md`
(the authors' brief), the group's Lean files and its `FINDINGS.md`, and the statute text in
`~\Documents\tax-formalization-data\xml\usc26.xml` (Grep for `identifier="/us/usc/t26/s<N>"`).

Check, provision by provision:
1. **Fidelity.** Does each definition say what the statute says, for tax year 2025, including the version in force in
   2025 (the OLRC text can show 2026 amendments; amendment and effective-date notes in the XML say which applies)?
   Dollar amounts and rates: right figure, right source, right rounding?
2. **Tests.** Are the IRS figures real? Spot-check at least 5 against the official document (irs.gov), within a
   budget of 8 web fetches. A test that only restates the definition is not a test.
3. **Proofs.** Would a broken version of the function also satisfy the theorem? (A proof that the result is
   non-negative is also satisfied by a function that always returns 0.) Name every theorem that is too weak to catch a
   plausible mistake, and add a sharper one where you can.
4. **Findings.** Is each claimed finding (cliff, notch, inconsistency, drafting error) actually supported by the
   statute text and by the Lean theorem cited? Downgrade or withdraw any that are not.

You may fix clear errors in the group's own `.lean` files, but keep every public function's name and signature (the
assembly in `TaxCode/Individual/Form1040.lean` depends on them), keep every file compiling (`lake env lean <file>`, or
`lake build TaxCode.Individual.<Group>.<File>`), and do not add `sorry`, `native_decide` or axioms. Do not touch other
groups' folders, `Form1040.lean`, `Run.lean`, lakefile.toml, or git. Do not kill processes you did not start.

Return (as text; you cannot write .md files) a review: errors found and fixed (with the statute citation), errors found
but not fixed, weak theorems, findings confirmed / downgraded / withdrawn, tests verified against the source, and a
one-line verdict on whether the group can be trusted for differential testing.
