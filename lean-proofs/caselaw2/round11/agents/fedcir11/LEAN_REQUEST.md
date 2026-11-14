# fedcir11 LEAN_REQUEST (for the lead): tribunal-name anchor cues for the Federal Circuit / CCPA, claim-gated

## Rule
A Federal Circuit (or CCPA) opinion names the decision under review by its tribunal: "The Court of International
Trade sustained Commerce's remand results. Foo Corp. v. United States, 123 F.Supp.2d 456 (CIT 2000).", "the Court of
Federal Claims granted summary judgment ... 45 Fed.Cl. 678", "the Claims Court held ...", "the Customs Court
overruled the protest ... C.D. 4321", "the Veterans Court affirmed the Board". The anchor cue list (`anchor`) holds
"district court", "trial court", "court below", "court of claims", "tax court", ... but none of these tribunal
names, so such anchors fail `anchorNoCue`. Round 6 also classed Court of International Trade / Customs Court /
veterans targets as "not reviewed" (`target_phrases`), so no linker has looked at them except the round-5 regex
reader.

## Proposed check (new claim value, presence-gated; no existing list changes)
New history claim value `anchorTribunal` in `history_claim.tsv` (DESIGN7 §3 claim mechanism). For an anchored history
row WITH this claim, the anchor-cue test (check 2 of `checkAnchored`) uses `anchor ++ anchor_wide ++ anchor_wide9 ++
anchor_tribunal` (the `anchorWide` lists plus the new list), substring test on the normalised, lower-cased anchor
quote as now. New list `anchor_tribunal` (cue-table key, `_note_round11`):

    "court of international trade", "customs court", "court of federal claims", "claims court",
    "veterans court", "court of veterans appeals"

Every other check unchanged (disqualify_anchor, target evidence inside the anchor quote, anchor part, the
disposition quote's cue / disqualifier / part, date order, authority). A claim on a row with no anchor line has no
effect (counted). Without the claim nothing changes, so v10d (and every earlier regression) is byte-identical.

## Theorems
`anchorTribunal_no_claim` (without the claim the anchored check is the round-10 one); `anchorTribunal_sound`
(an admitted anchored row with the claim has an anchor cue of `anchor ++ anchor_wide ++ anchor_wide9 ++
anchor_tribunal`, and every other anchored check holds). Mutant: apply `anchor_tribunal` without the claim.

## Effect (linker run `a`, corpus-wide, 14 Nov 2026; counts updated in NOTES.md as the rules change)
Rows of the fedcir11 linker whose only anchor cue is a tribunal name (all other checks as for certifiable rows):
"court of federal claims" 91 (32 reversed / vacated / modified), "claims court" 56 (21), "court of international
trade" 69 (30), "customs court" 95 (26), "veterans court" / "court of veterans appeals" 3, "trade court" 2 —
about 316 rows, ~110 status-changing. Rows whose anchor already carries a cue of `anchor` ("trial court", "court
below", "appeal from", "opinion of", ...) certify today (~140 rows, ~40 status-changing) and are staged without the
claim. "trial judge" anchors use the existing `anchorWide` claim (anchor_wide9).

## Status
Requested at about 05:20 (14 Nov). fedcir11 continues with the rows that certify today; the claim rows are kept in a
separate delta (`delta_<v>_tribunal/`) and are staged only if the lead adds a §5 section.
