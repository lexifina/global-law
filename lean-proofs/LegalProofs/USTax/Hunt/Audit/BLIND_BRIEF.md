# Blind replication brief

You are an independent second encoder. Another team encoded part of the US tax code in Lean and ran a search. We want
to know whether their result came from the law or from how they wrote it down. You are **not told what they found**,
and you must not look: do not open, list, grep or read anything under `LegalProofs/USTax/Hunt/` except this brief and
your own folder, nothing under `tools/hunt/out/` except your own folder, and no memory or notes files. Do not search
the web. If you think you can guess what the other team found, ignore the guess: encode every provision evenly and
report what the search returns, including "nothing beats the baseline". A replication that finds nothing is as
useful to us as one that finds something.

- Work only in `~\Documents\global-law-lean\lean-proofs`. Write only under
  `LegalProofs/USTax/Hunt/Audit/<Name>/` : `Blind.lean` (self-contained, `import Std` only, namespace
  `Legal.USTax.Hunt.Audit.<Name>.Blind`), `BLIND.md`, `blind.json`, scratch in the same folder.
- Run with `lake env lean LegalProofs/USTax/Hunt/Audit/<Name>/Blind.lean` from `lean-proofs/`. Never `lake build`.
  Never touch `TaxCode/` or any existing file. No git commands that change anything. Kill no process you did not
  start; do not leave a run going past 3 minutes. No subagents.
- Lean 4.35 core + Std, no Mathlib. `until` is a keyword. Derive `BEq, Hashable, Repr`; dedupe with `Std.HashSet`.
- Statute text: `python -I tools/hunt/sec.py 408 d 9` prints §408(d)(9); `python -I tools/hunt/sec.py 224` a whole
  section. Read every provision in your list in full and encode what the words say: conditions, limits, orderings,
  who each rule applies to and until when. Where the text is silent, do not add a restriction and do not add a
  permission: note the silence. Where a dollar figure is indexed, use the figure given in your task.
- Method: a state; moves (each one thing the text lets the taxpayer do, cited); `step : State → Move → Option State`;
  breadth-first or exhaustive search over sequences with amounts drawn from the natural values of the position; the
  objective given in your task; compare with the baseline given. Print the best plan and the runner-up families.

Deliver `BLIND.md` (provisions encoded, each silence or judgment call, search size, best plans with dollar figures,
baseline figure) and `blind.json`:
`{"name":…, "positions":N, "baseline":…, "best":{"moves":[…], "value":…, "gain":…}, "runners_up":[…],
"judgment_calls":[…], "silences":[…]}`. Reply in at most 200 words: the best plan, its gain, and the judgment calls.
