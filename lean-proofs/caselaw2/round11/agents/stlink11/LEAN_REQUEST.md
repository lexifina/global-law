# stlink11 LEAN_REQUEST (optional; the lead decides; delta_u2c does NOT need it)

## Rule
Class U2 (`below:stlink11_u2`, delta_u2c, 543 rows) is certified today as plain anchored history rows: the anchor
quote is D's majority sentence naming T's court acting, with `name:<surname>` evidence. The Lean checks that quote and
the judgment line. The identity ties that pick T (full party names in both captions + T's docket number, T's
reporter citation or T's decision date printed in D) are not checked; only the audit covers them (r11t01, 0.963).

## Check (proposed `identityTie` claim, like DESIGN10 section 4's remandDocket)
An optional table `history_identity.tsv`: row id, form (docket | date | cite), D span [s, e) and T span [s, e). Each
span is a quote of its own decision's text at git HEAD (sha as in decisions2):
- docket: `compact(D quote) == compact(T quote)`, >= 4 characters, at least one digit; T's quote lies in T's front
  matter `docket:` line or its head matter; D's quote lies outside D's own `docket:` line.
- date: both quotes parse to the same (year, month, day); T's quote is T's `decided:` field.
- cite: D's quote is one of T's citations under the round-6 citation-key normaliser (`Wn.` = `Wash.`).
Effect: a U2 row is admitted only when its identity line passes (rows without a line keep today's behaviour).

## Theorem
identityTie_sound: when the line passes, D's text holds the token / date / citation printed in T's own text
(a string-equality statement over the two windows, no new trust).

## Effect
543 U2 rows today: 95 have a docket tie, 88 a date tie, 421 a citation tie (forms overlap). No status change.
