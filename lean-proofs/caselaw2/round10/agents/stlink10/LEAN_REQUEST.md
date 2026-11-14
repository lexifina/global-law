# stlink10 LEAN_REQUEST (optional; lowest priority; not needed for delta_s1)

## Class T: the court of last resort reverses the TRIAL judgment that the intermediate court had affirmed

Corpus diagnosis (round10/agents/stlink10/NOTES.md, read1): 2,057 state court-of-last-resort opinions whose own
judgment line acts only on the trial court's judgment ("The judgment of the district court is reversed", or a bare
"Reversed and remanded to the trial court"), with exactly one cited same-caption decision T of the state's
intermediate court 0..5 years before. Readers: T was the decision under review in 8/8, and D's judgment in effect
undid T in 7/8 (T had affirmed the trial judgment). Round 6 refuses these on purpose ("a disposition that names only
another court gives no row"), because D's words alone do not say what happens to T.

### Rule
Row `history` (by D, target T, kind reversed | vacated, scope as D's line) with TWO quotes:
1. D's own judgment line (majority / per curiam zone): a `hist` cue of the kind and a trial-court phrase (cue-table
   list, new: `trial_court_names` = "trial court", "district court", "circuit court", "superior court", "county
   court", "court of common pleas", "chancery court", "probate court", "court below"), and no intermediate-court
   phrase of the anchor list ("court of appeals", "appellate division", ...);
2. T's own judgment line (T's majority / per curiam zone, T's text hash as for bridge quotes): the cue "affirm"
   (`hist.affirmed`) and no negative cue (reversed / vacated / set aside) — T affirmed the trial judgment;
plus the usual anchor in D (T's citation + an anchor cue, one contiguous quote).

### Check `trialBridge` (only on rows with the new claim `trialBridge`; absent ⇒ byte-identical to v9c)
court(T) is an intermediate court of D's system; date(T) < date(D) ≤ date(T) + 1,826; quote 1 as above in D; quote
2 as above in T; the round-9 verdict on the anchor admits. Failure ⇒ reason `trialBridgeD` / `trialBridgeT`.
Effect: as a reversed / vacated row on T.
Theorems: `no_trialBridge_claim_no_change`; `trialBridge_sound` (admitted ⇒ D's line names a trial court with the
kind's cue, T's line affirms, dates and courts as above, anchor admitted).
Mutants: T's line reverses; D's line names the intermediate court; T of another system; T dated after D.

Not built in round 10 by stlink10 (no Lean support); estimated yield ~1,800 rows (2,057 x 7/8), to be audited
(item type B) once the claim exists.
