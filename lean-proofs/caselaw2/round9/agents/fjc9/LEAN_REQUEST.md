# fjc9 LEAN_REQUEST (optional, for the lead): judge-form anchor cues

## Rule
A federal court of appeals opinion often names the court below only as a judge: "the district judge, 332 F.Supp.
316, found ...", "Judge Sweet dismissed the indictment. 777 F.Supp. 258.", "the magistrate judge ...". The round-8
anchor cue lists (`anchor`, and `anchor_wide` under the claim `anchorWide`) hold "district court", "trial court",
"court below", "bankruptcy" but no judge form, so an anchor quote that names the court below only as a judge cannot
be certified (anchorNoCue). Proposed: under the existing claim `anchorWide` (DESIGN8 §5), extend `anchor_wide` with
"district judge", "magistrate judge", "trial judge" (substring test on the normalised, lower-cased anchor quote, as
now). "Judge <Name>" is not a fixed string and is NOT proposed (it would need a name test against the target's
judge, which the corpus does not carry).

## Check
Unchanged except the cue list: anchored history row with claim `anchorWide` -> anchor quote contains a cue of
`anchor ++ anchor_wide` (with the three new strings). Every other anchored check unchanged.

## Effect (fjc9 W linker drops, corpus-wide, before the disposition step)
Of 2,541 F1-style candidates dropped by W for want of a court phrase (`wide_no_phrase` 2,045, `wide_no_court_act`
496), 1,133 name the court below as a judge ("district / magistrate / trial / bankruptcy judge" or "Judge <Name>")
in the citation sentence or the 600 characters before it (`judgeform.py`). The fixed-string forms are a subset
(not separated yet). Expected rows after the disposition / guard steps: of the order of 100-200 status-changing.

## Round-9 mode by presence
The new strings act only on rows with the `anchorWide` claim; no v8e row carries the claim with a judge-only anchor
(the 110 v8e `anchorWide` rows all pass today), so v8e output is unchanged. Theorem: as `anchorWide_sound` with the
extended list; mutant: apply the judge strings without the claim.

## Status
Not needed for what fjc9 stages now (rule W anchors contain "district court" / "trial court" / "court below").
Lead decides; fjc9 has not built rows for it.
