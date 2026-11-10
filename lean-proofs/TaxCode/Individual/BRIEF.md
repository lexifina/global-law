# Brief for agents formalizing the individual income tax (tax year 2025)

You are copying one group of provisions of the Internal Revenue Code (Title 26) into Lean 4, the way the CPython
formalization (broyojo.com/python-formalization) copied CPython: line by line from the source, then testing, proving
and recording findings. The "source" here is the statute as amended through Pub. L. 119-138 (OLRC release point
119-138), for tax year 2025, including the changes made by Pub. L. 119-21 (4 July 2025, the "2025 Act").

## Where things are
- Lean project: `C:\Users\alany\Documents\global-law-lean\lean-proofs` (Lean 4.35, core only, NO Mathlib; elan is at
  `$HOME/.elan/bin`). Shared interface: `TaxCode/Individual/Household.lean` (read it first; do not edit it; if you need
  a field it lacks, say so in your report instead).
- Official statute text, one file per title (USLM XML): `C:\Users\alany\Documents\tax-formalization-data\xml\usc26.xml`.
  Search it with Grep for `identifier="/us/usc/t26/s32"` etc. This is the primary source: read the actual text of every
  provision you copy, including definitions it points to.
- Earlier, smaller Lean tax work you can read for style (do not import it): `LegalProofs/USTax/Model.lean`,
  `LegalProofs/USTax/Schedule.lean` (has a hand proof that the rate schedule never exceeds 100%).

## The four steps, for every provision in your group
1. **Copy.** Write the provision as Lean definitions in your own file(s) under `TaxCode/Individual/<YourGroup>/`. Follow
   the statute's structure and words: one definition per operative rule, a docstring citing the exact subdivision
   (e.g. `§32(b)(2)(A)`) and quoting at most a short phrase. Use whole dollars (`Int`), basis points for rates, and the
   rounding rules the statute or the IRS forms actually use (say which). 2025 dollar amounts: cite their source (Rev.
   Proc. 2024-40; the 2025 Act's text for amounts it set; Rev. Proc. 2025-32 or IRS notices where the IRS published
   2025 figures after the Act). Where the IRS form or worksheet departs from the statute (tables in $50 bands,
   rounding), model the statute and note the difference.
2. **Test.** For each provision, reproduce worked examples or table values from official IRS material for 2025 (Form
   1040 instructions and worksheets, Pub 17, Pub 596 EIC table, Pub 972, Pub 915, Pub 970, Pub 503, Form 8962/8812/8863
   instructions, etc.) as `theorem ... := by decide` or `#guard` checks, each citing the document and page/line. If you
   cannot reach a document, say so; never invent an example. Aim for several per provision.
3. **Prove.** State properties the provision should have and prove them in Lean for ALL inputs (no `sorry`, no
   `native_decide`, no axioms beyond Lean's standard three). Good properties: phase-outs never push the amount below
   zero or above the maximum; the amount is monotone where the statute says it should be; the marginal rate a
   phase-out adds is bounded; a cliff exists or does not; two definitions that should agree do agree (e.g. different
   "modified AGI" definitions). If a property you expected is FALSE, prove the counterexample instead and record it —
   that is a finding. Avoid trivial "the definition equals itself" theorems: a proof that holds for a broken version of
   the function too is not worth stating. `omega` handles linear integer arithmetic with literal multiplication and
   division; for nonlinear facts prove lemmas by hand (`grind` exists but often fails on nonlinear goals).
4. **Record.** Write `TaxCode/Individual/<YourGroup>/FINDINGS.md`: every place where the statute is ambiguous,
   internally inconsistent, has a cliff or notch, points at something that does not exist, or where IRS guidance
   departs from the statute — each with the statutory citation, what you proved, and how sure you are. Also list what
   you did NOT model.

## Rules
- Only create/edit files under `TaxCode/Individual/<YourGroup>/` (plus nothing else). Other agents work in parallel on
  other groups; never touch their folders, never run `git` commands, never edit lakefile.toml.
- Check your files with `cd <project> && export PATH="$HOME/.elan/bin:$PATH" && lake env lean TaxCode/Individual/<YourGroup>/<File>.lean`.
  If you split into several files that import each other, build them with `lake build TaxCode.Individual.<YourGroup>.<File>`;
  if lake reports a lock, wait a little and retry. Never run a bare `lake build` of the whole project.
- Web: at most 10 web searches/fetches in total, only for official IRS/congress.gov/govinfo/Cornell LII sources.
- Do not kill or touch any process you did not start.
- Finish with: every file compiling, `#print axioms` on your main theorems showing only propext/Classical.choice/Quot.sound,
  and a short report: provisions covered, number of tests (and their sources), number of proved properties, findings,
  gaps. Work until the group is complete; do not stop at a first draft.
