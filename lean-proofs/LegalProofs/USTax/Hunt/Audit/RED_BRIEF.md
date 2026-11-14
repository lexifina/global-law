# Red-team brief: did the search cheat?

A Lean file under `LegalProofs/USTax/Hunt/` encodes part of the tax code and a blind search over it returned a plan
(your task names the file, the findings file and the plan). An earlier attempt at this project was thrown out because
the "loophole" had been written into the definitions, so the result was circular. Your job is to **try to show that
this one is circular, wrong or a model artifact**. You are rewarded for breaking it, not for confirming it. Report a
test as passed only when you ran it and it could have failed.

Rules: work only in `~\Documents\global-law-lean\lean-proofs`. Never edit the original files; copy what
you need into `LegalProofs/USTax/Hunt/Audit/<Name>/` and write only there (`Red*.lean`, `RED.md`, `red.json`, scratch).
Do not open `Blind.lean`, `BLIND.md` or `blind.json` in that folder (a separate blind replication is running there).
Run with `lake env lean <file>` from `lean-proofs/`; never `lake build`; never touch `TaxCode/`; no git commands that
change anything; kill no process you did not start; no run over 3 minutes; no subagents. Lean 4.35 core + Std.
Statute text: `python -I tools/hunt/sec.py <section> [subdivisions…]`.

Run every test below; give each a result `pass` (the result survived), `fail` (you broke it), or `partial`, with the
numbers.

- **T1 Text fidelity.** Read the rules part line by line against the statute text of every provision the plan uses
  and every provision that restricts those moves. List each place the encoding is more generous than the words, each
  restriction in the statute that is missing, and each field or move that exists only to make this plan possible.
  Fix every divergence in a copy and re-run: does the plan survive the strict reading?
- **T2 Close the gap.** Change the copy the way Congress would close this (one minimal edit to the encoded rule, say
  which words you are adding to the statute). The plan must disappear and the baseline must not move. If the plan
  survives the fix, the gain is coming from somewhere else: find where.
- **T3 Ablation.** Remove each move the plan uses, one at a time: the plan must fail each time (or say which moves
  were decoration). Remove every move the plan does not use: the plan must still be found with the same figure.
- **T4 Earlier law.** Where the plan depends on a recent amendment, restore the earlier text in the copy: the search
  must return nothing above the baseline (or only what was already known then).
- **T5 Free lunch.** Point the search at absurd goals on the unmodified rules: tax below zero where no refundable
  rule exists, money created from nothing, the same dollar deducted twice, a limit exceeded. Check a conservation
  law over every position reached (money in = money out + tax). Anything absurd the model allows is a finding.
- **T6 Kernel.** `#eval` is compiled code, not proof. Write `theorem`s that replay the plan and the closed-gap result
  through the kernel (`by decide`; cut the state down if `decide` is too slow, and say so), and where you can, one
  statement over **all** move sequences (by induction on the list), for example that under the closed-gap rule no
  sequence reaches the plan's result. Then `#print axioms` on each: no `sorryAx`, no `Lean.ofReduceBool`
  (`native_decide`), no axioms of your own.
- **T7 Independent arithmetic.** Recompute the plan's dollar result and the baseline in a short Python script written
  from the statute text, not translated from the Lean. Do the figures agree?
- **T8 Outside the statute.** Up to 10 web searches (standard), fetching primary sources where you can: Treasury
  regulations (final and proposed), IRS form instructions, notices, publications, committee reports, then
  practitioner writing. Does anything already close this, or already describe it? Quote the passage and give the URL.
  Say what you could not retrieve.

Deliver `RED.md` (each test: what you did, what happened, numbers; then every weakness you found, ranked) and
`red.json`: `{"name":…, "plan":…, "claimed_gain":…, "tests":[{"id":"T1","result":"pass|fail|partial","detail":"one
sentence","numbers":{…}}, …], "divergences":[…], "authority":[{"source":…,"url":…,"effect":"closes|supports|silent",
"quote":…}], "verdict":"holds on the text|artifact|circular|closed by authority|already published",
"verdict_reason":…}`. Reply in at most 300 words: the verdict, the tests that failed or were partial, and the worst
weakness. No padding; do not soften a failure.
