# Loophole hunt: brief for each domain

Goal: repeat, on another part of the US tax code, what `LegalProofs/USTax/Retirement/` did for retirement accounts
(read `Rules.lean` and `Search.lean` there first, 250 lines): write down what each provision permits and what it
taxes, **without any planning idea in mind**, then let a blind search over every allowed sequence of moves find the
plans that beat the obvious one. The retirement search found the backdoor Roth and the mega backdoor unprompted. We
want the same for your domain, and above all we want plans that are **not already known**. Speed matters: a first
search result inside ~20 minutes, then widen.

## Hard rules

- Work only in `~\Documents\global-law-lean\lean-proofs`. Write only:
  `LegalProofs/USTax/Hunt/<Name>.lean` (one self-contained file, `import Std` only, your namespace
  `Legal.USTax.Hunt.<Name>`), `LegalProofs/USTax/Hunt/<Name>.FINDINGS.md`, and scratch under `tools/hunt/out/<Name>/`.
- Run with `lake env lean LegalProofs/USTax/Hunt/<Name>.lean` from `lean-proofs/`. Never `lake build`, never edit
  `lakefile.toml`, never touch `TaxCode/` (another session is working there) or any existing file. No git commands
  that change anything (no add/commit/stash/checkout). Do not kill any process you did not start. No subagents.
- Lean 4.35 core + Std, no Mathlib. `until` is a keyword. Derive `BEq, Hashable, Repr` on the state and dedupe with
  `Std.HashSet`. Keep each run under ~2 minutes (limit depth/amount grid, not the rule set).
- Statute text is local: `python -I tools/hunt/sec.py 408 d 9` prints §408(d)(9); `python -I tools/hunt/sec.py 224`
  a whole section; `--grep "regex"` lists sections matching. It is the OLRC release point through Pub. L. 119-138,
  so it includes the 2025 Act (Pub. L. 119-21). **Read the text of every provision you encode** and encode what it
  says, including the limits and anti-abuse rules that are in the statute. Cite the provision on every rule.
  Indexed dollar figures: use the 2025 (or 2026 where the rule starts in 2026) figures you know; say which.

## Method

1. **Rules** (first part of the file): a state, a list of moves, `step : State → Move → Option State`. Each move is
   one thing the Code lets a taxpayer do, with its conditions and its tax effect. Nothing in this part may name or
   anticipate a technique. If a rule is uncertain or depends on regulations/case law, either leave the move out or
   encode the conservative reading and note it.
2. **Search** (second part): breadth-first or exhaustive over move sequences, amounts taken from the "natural" values
   the position offers (each limit's remaining room, each balance, each threshold). A generic objective: total tax
   paid, or after-tax wealth, or amount ending in a tax-free form. Compare to the baseline (do the plain thing).
   Print the best plans and the runner-up families (group by which moves they use), not just one winner.
3. **Widen** two or three times: add neighbouring provisions and re-run. Prefer text that has had little scrutiny:
   anything added or amended by Pub. L. 119-21 (2025) and by SECURE 2.0 (2022); limits stated per person / per
   return / per employer / per plan / per donee / per trust / per year where nothing aggregates them; orderings
   ("treated as made first from…"); definitions that cross-refer to another section's term; phase-outs that use
   different income definitions; elections with timing. While reading, note drafting gaps even if you cannot model
   them.
4. **Judge each plan honestly.** For every distinct plan the search returns that beats baseline, classify:
   - KNOWN: name the technique as practitioners call it.
   - VARIANT: a known technique in a new combination or under new (2025) law.
   - CANDIDATE: you do not know it as a published technique.
   For VARIANT and CANDIDATE: is it a model artifact (something you left out) or does the statutory text really allow
   it? List exactly what outside the model could defeat it: a regulation, §7701(o) economic substance, step
   transaction, assignment of income, substance over form, a specific anti-abuse section. You may spend up to 6 web
   searches (standard mode) checking whether a CANDIDATE is already written about or already shut down. A candidate
   that survives your own attack is worth far more than ten that do not; say plainly when nothing novel turned up.

## Deliverable

`<Name>.FINDINGS.md`: provisions encoded; search size; a table of plans (moves, dollar effect vs baseline, provisions
combined, class, what could defeat it, sources checked); traps found (rules that cost money unexpectedly); drafting
gaps noticed. Then reply with at most 350 words: the CANDIDATE and VARIANT items first, each in two lines, then
counts. No padding, no claims the search output does not support.
