# state9 LEAN_REQUEST (round 9) — accepted by the lead as DESIGN9 §5 (R-B) and §7 (R-A), D9-5

Three sections, one per part of the brief. Each is claim-gated / presence-gated: with none of the new claim values
present, the output is byte-identical to `round8/out/v8e` (DESIGN9 §1).

## R-A. Claim `implicitReject` (part A: implicit overruling, at-risk only)

**Rule.** A treatments row of a **soft** kind (`declinedToFollow`, `questioned`; never a status-changing kind) whose
class line carries claim `implicitReject` uses, for its cue test, the kind's plain cue list **plus** the new cue-table
list `implicit_reject` (phrases of the acting court's own rejection that the soft lists lack): "cannot agree",
"do not agree", "unpersuaded", "not convinced", "wrongly decided", "incorrectly decided", "erroneously decided",
"unsound", "erroneous", "incorrect", "mistaken", "undermined", "eroded", "discredited", "called into question",
"contrary to", "depart from", "departs from". Every other check unchanged (hash, window, quote, part, date order;
soft kinds need no power, as today). A row with the claim and a status-changing kind fails (`implicitBadKind`).
**Effect.** None on status: a soft kind has `changesStatus = false`, so `treatEffect = none`; the row reaches the
findings only as `atRisk soft:<kind>` (Findings.softRisk), as the 6,644 v8e `declinedToFollow` rows do today.
**Why a claim.** Widening the soft cue list without a claim would flip v8e rows whose quote fails the cue test today
(not byte-identical).
**Theorems.** `implicitReject_never_neg` (for any list `l` and an admitted row with the claim:
`status (effects row ++ l) = status l`; i.e. its effects are empty), `implicitReject_soft` (admitted with the claim ⇒
`kind.softNegative = true`), `implicitReject_no_claim` (without the claim the cue test is the round-8 one).
Mutants: claim on an `overruled` row admitted; implicit cue accepted without the claim.
**Needed only for** the rows whose quote has no plain soft cue (reading of 520 of 21,029 candidates: 42 rows, 35 with a plain cue, 7 need the claim, 6 certify with it); rows whose quote
already holds a plain `declinedToFollow` / `questioned` cue are certifiable today without any Lean change.

## R-B. Claim `joinedFar` (part B: joined antecedent gap > 300)

**Rule.** DESIGN7 §2.2 relation `antecedent` keeps `start − j_end ≤ 300` (`joined_gap_max`). A row whose class line
carries claim `joinedFar` may instead have `300 < start − j_end ≤ joined_far_max` (cue-table constant; value set from
the reading: **1,200**; reader-chosen targets in the 455 anaphor items read: <=600 15, <=900 49, <=1200 75, all 117) **if all hold** (checked on the text; the row supplies a
usable window of its own text that covers `[j_end, start)`):
1. (DROPPED after reading: the same-paragraph test keeps only 32 of the 75 reader-chosen targets within 1,200;
   the act usually opens a new paragraph after the discussion that names X. Not a condition.)
2. no other index key between: no compact citation in `[j_end, start)` that the index maps to a node other than the
   row's target (as DESIGN8 5b for bridges);
3. the main quote holds an `anaphor` phrase (as §2.2) and a cue of the row's kind (as §2.2);
4. every other `checkJoined` step unchanged (joined quote in the same text, allowed part, disqualifiers, evidence in
   the joined quote alone).
Failure reasons `joinedFarGap`, `joinedFarKey`, `joinedFarWindow` (gap not covered by a window).
**Effect.** As an explicit row of its kind and scope (as `antecedent`).
**Theorems.** `antecedentFar_gap` (admitted with the claim ⇒ `j_end ≤ start ∧ start − j_end ≤ joined_far_max`, no
no other index key in the gap, anaphor + kind cue in the main quote), `joinedFar_no_claim` (without the
claim the round-7/8 `antecedent` check, gap ≤ 300), `joinedFar_extends` (every row admitted without the claim is
admitted with it). Measured (B): 455 anaphor far items read, 117 reader-chosen targets; 57 rows pass gap <= 1200 + other-key; 52 certify
(5 already in base); blind audit r9s01 52/52 [0.931, 1.000].
Mutants: drop the other-key test; accept a gap above the bound.

## R-C. Doctrine own-tie (part C): WITHDRAWN — no request

The 69 rule-ok own-tie items of round-8 doctrine8 (`round8/agents/doctrine8/work/own_alt_items.jsonl`) were read by
two opus readers (round-7 doctrine brief, unchanged): reject + tie both true 14/69 (13 (W, X) pairs); 10 of those
pairs already have an explicit `overruled` / `disapproved` row in v8e. New pairs: 3. Far below the 25-row bar, so no
per-system uniqueness change is asked for. (Note: the Lean's `doctrineAmbiguous` is table-wide, not corpus-wide; the
corpus-wide uniqueness is a linker guarantee, so 3 rows would not even need a Lean change; not built.)
