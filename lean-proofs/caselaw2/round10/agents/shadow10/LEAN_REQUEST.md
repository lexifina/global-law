# shadow10 LEAN_REQUEST (optional; amends DESIGN10 §4 check 4 `remandTie`; the rows do not wait for it)

## Finding (pre-check, `remand10.py`, D10-6 exact; data `cert_remand/`)
367 rows (remandtext-v2 335 + remandcap 32): 241 pass. Ties used: cite key 45, order date 90, tie (b) 106.
Tie (b) ("compact(docket) inside compact(B quote)", the docket shared by B and the target) does not tie B to the
ORDER: B's own docket is in B's own text by construction, so (b) passes whenever B's docket line lies within 600
characters of the cue. Without (b): 137 pass.

## Rule proposed: the reason-case tie (c2)
The court below's remand opinion usually ties itself to the order by the case the order names: the order says
"judgment vacated, and case remanded ... for further consideration in light of Johnson v. United States, 576 U.S.
___ (2015)", and B says "The Supreme Court vacated ... and remanded ... in light of Johnson v. United States, 576
U.S. ___, 135 S. Ct. 2551 (2015)".

Three more columns in `history_remand.tsv` (12 in all): `tie`, `o_start`, `o_end`.
- `[o_start, o_end)` is a span (<= 300 chars) of the ORDER's own text (window-hashed like the other spans);
- check: lower(norm(O span)) holds "in light of"; compact(tie) has >= 8 characters and contains "v" ... (the case
  name as printed, e.g. "Johnson v. United States"); compact(tie) is a substring of compact(O span) AND of
  compact(B quote).
- `remandTie` passes when (a) or (c) (date) or (c2) holds; (b) dropped (or kept, lead's choice).

## Effect (measured in Python)
With (c2) and the order-list page citation of O (a page key that the index cannot map to O alone because several
orders share the page, accepted when it is one of O's own printed citations): 339/367 pass (reason tie 196 rows).
Status counts unchanged (evidence only).

## Theorem
`remandBridge_sound` gains: tie (c2) => compact(tie) is in O's span and in B's quote, O's span holds "in light of".
Mutant: a tie string found in B only.
