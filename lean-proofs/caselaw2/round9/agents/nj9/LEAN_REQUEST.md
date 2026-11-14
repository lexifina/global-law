# LEAN_REQUEST (nj9): successor courts of like jurisdiction hold their predecessor's decisions

Rule and sources: `RULE.md` (this folder). For the lead to decide (D9-n); written for `lean9` and `ref9`.

## The difference, stated over the tables

A non-split succession row (`rename` / `replace` / `absorb`, `old -> new`, dated `d`) means today:
- **reference** (`holders`, R7): `new` holds every decision of `old` dated before `d` **as its own, at the deciding
  court's dated tier** (unless an adoption row covers the pair, which then governs). So `new` has power over them as
  over its own (horizontal rule) when its tier equals the dated tier, as a higher court when above it, none when
  below. U-tagged rows count in the all-tables run only.
- **Lean** (`canChangeStatus`): a succession row gives power only between two courts of last resort
  (`sameOrSuccessor`, `lastResortBench`); otherwise inheritance comes **only from adoption rows** (DEVIATIONS 73: "The
  Lean already read inheritance only from adoption rows").

The researched New Jersey rule is the reference's reading (the Appellate Division treats the old Supreme Court's
opinions as those of a court of "comparable jurisdiction", not binding and open to departure; the Chancery Division
the same for the Court of Chancery, "a court of like jurisdiction"). The three v8e rows that differ are all of this
kind: `t8:4058244:4016514:17127` (1099 -> 1095), `tw:4018149:4006682:13821:4061823` (W 1099 -> 1095),
`tw:3991335:4086271:4616:4089451` (W 1222 -> 1206).

## Recommended: A, data only (no Lean code, no reference code)

The tables already express "a successor of like jurisdiction inherits" as **adoption rows** (H3 rows: Kentucky
`917 913`, Missouri `10081 10106` ..., Alabama `3 1`, New Jersey's own `1096 1094`). New Jersey lacks the two rows for
its intermediate / trial successors. Add (7 columns, `adoption.tsv` format: adopter, source, upTo, filter, force,
note, tag) — file `adoption_add.tsv` here:

    1099	1095	19480914	all	binding	NJ Const. 1947 art. XI sec. IV paras. 3, 8(b) (appeals, writs of error, prerogative writs pending in the Supreme Court -> Appellate Division); In re Estate of Johnson, 240 N.J. Super. 134 (App. Div. 1990): opinions of the former Supreme Court not binding, its jurisdiction 'comparable to the jurisdiction now possessed by this court'	S
    1222	1206	19480914	all	binding	NJ Const. 1947 art. XI sec. IV paras. 3, 8(e), 12; Hagaman v. Board of Education, 112 N.J. Super. 221 (Ch. Div. 1970): former Court of Chancery 'a court of like jurisdiction'; Hogan v. Bergen Brunswig Corp., 151 N.J. Super. 344 (Ch. Div. 1977)	S

and retag (sources found): `succession.tsv` `1095 1099 ... U` -> `S` (note + ¶8(b), *Johnson*); `1206 1222 ... L` ->
`S`; `adoption.tsv` `1096 1094 ... L` -> `S` (*Collopy*, 27 N.J. 29 (1958): "coordinate courts"; *Bernard*, 131 N.J.
91 (1993): "We therefore overrule Willis").

`binding` means "read as a decision of the adopter" (`adoptedForce` = min(force, relation of the adopter)): an App.
Div. decision binds the trial divisions and not other App. Div. panels (`horizontal none`), which is exactly
*Johnson*'s "comparable jurisdiction". Force on the trial courts does not change (the old Supreme Court, tier A of
system 30, already binds them directly; `force` takes the max).

Why both engines then agree (no code change): Lean `canChangeStatus`, adoption branch:
`(adoptionsOf L x).any (·.adopter == b.court) && X.tier.rank ≤ B.tier.rank` (A ≤ A; S ≤ S), `B.tier ≠ last` ->
`benchRule L B B b {x with unit := none}` -> `horizontal 1099|1222, system 30` = `none` -> `(true, sameCourtSoft)`.
The App. Div. over the E&A (tier L > A) stays `noPower`. Reference: R7, the adoption row governs the pair; adoption
holder power = adopter tier ≥ dated tier; same court and tier -> `horizontal none` -> yes. Both firm and all.
H4 reach (`reachOf`): every status-changing treatment of a 1095 / 1206 decision on v8e is by 1096 (above the heir),
by the heir itself, or by the E&A before the cut-off: all reach every line, so no per-line status appears.

Expected v8e effect (the lead should confirm with a run; `stage9.py` stages only the ten row tables, so the two doctrine
tables need a staged copy or a stage9 option):
- `t8:4058244:4016514:17127`: Lean noAuthority -> ok (all and firm); reference firm no -> yes. Status 4016514
  partial (disapproved:partial) from 1962-06-18; finding `atRisk:claim 4058244 4016514` goes away; operative_rows
  1071 -> 1072.
- `tw:3991335:4086271:4616:4089451`: witnessNoStanding -> okRecognised; status 4086271 recognisedLater / negative
  (disapproved) as the reference has it; recognised_rows +1.
- `tw:4018149:4006682:13821:4061823`: disqualified -> okRecognised (+1 recognised; 12 `cites:overruled` + 5
  `atRisk:recognisedLater` findings as in the reference's diff). Caveat: its target 100 N.J.L. 177 is really an E&A
  decision filed under 1095 (RULE.md §5); the status it receives (overruled by the Supreme Court, *In re N.J. Power &
  Light*, 15 N.J. 82 (1954)) is true, but the App. Div.'s standing is only right as filed.
- Differential Lean vs reference on v8e: 0 rows (all three classes close). No other row can move: the new rows
  touch only decisions of 1095 and 1206, and every other acting court on them is 1096 (already yes), lower, or acts
  without a power check (`rows.tsv`).

Lean work under A: none in the Spec. Requested regression evidence (lean9, `Examples.lean`, a NJ fixture of the
four courts with the two adoption rows):

    #guard pw appDiv1962 oldSup1948  == some true    -- Clark v. Piccillo: successor of comparable jurisdiction
    #guard pw appDiv1977 ea1924      == some false   -- bound by the E&A (Gruschow, Haber)
    #guard pw chanDiv1949 chancery1937 == some true  -- Hagaman, Hogan
    #guard pw lawDiv1964 oldSup1944  == some false   -- a trial court changes no status (F13; Weller)
    #guard pw sup1993 ea1922         == some true    -- Bernard v. IMI Systems: overrules the E&A
    #guard pw sup1954 oldSup1924     == some true    -- higher court

Theorem (general, not New Jersey): `adoptedSameTier_power` —
for `b x`, epochs `B X`, `x.date ≤ b.date`, `¬ B.scotus`, `B.tier ≠ .last`, `B.court ≠ X.court`, no earlier branch
applies (`¬ (B.system = X.system ∧ X.tier.rank < B.tier.rank ...)`), an adoption `a ∈ adoptionsOf L x` with
`a.adopter = b.court`, `X.tier.rank ≤ B.tier.rank`, and `L.rules.horizontal B.court B.system x.date ∈ {some .none,
some .soft}`, then `canChangeStatus L b x dom = some (true, .sameCourtSoft)`; and its converse guard
`adopted_lowerTier_noPower`: `B.tier.rank < X.tier.rank` and no higher-court / last-resort branch -> the result's
first component is `false` (Kentucky 1976 / App. Div. under the E&A). Mutant: drop the guard `X.tier.rank ≤
B.tier.rank` in the adoption branch (`mutAdoptAnyTier`): the `appDiv1977 ea1924` guard and the converse theorem
fail (with an adoption row 1099 <- 1094 in the mutant fixture); and `mutNoAdoptPower` (adoption branch removed):
`appDiv1962 oldSup1948` and `chanDiv1949 chancery1937` fail.

## Alternative: B, the general rule in the Lean (only if the lead prefers code to data)

"A non-split succession row without an adoption row on the same pair is read as an implicit adoption
`new <- old`, upTo `date - 1`, filter `all`, force `binding`, firm = the row's firm" — added in `Env.lookups`
(`adoptionsFrom`), so U keeps its one meaning (all-tables only) and the Lean equals the reference's R7 holders.
Theorem `succession_implicit_adoption`: for such a row, `adoptionsOf L x` contains the derived adoption for every `x`
of `old` dated before `d`; with an explicit adoption row on the pair, it contains none (R7: the explicit row governs).
This touches every non-split succession of every state (NY 1778 -> 1769 U, DC 631 -> 518 U, MA 989 -> 951 U, CO, KS,
TX 2948 -> 2927, ...), and adds H4 heirs for them; the reference already reads them so, so the v8e differential is
the test, but it needs the kept/sweep/regress universes rerun (`round8/agents/ref8/difftest8.sh all`) and its effect
on h0/dev measured. B is more general; A settles the New Jersey class with sourced rows and no code risk.

## What the reference must change

Under A: nothing (the adoption rows take the pair over by R7; the retag only moves firm verdicts, the same on both
sides). Under B: nothing either (it is the reference's reading). If the lead instead decided the Lean's reading
(inheritance only by adoption) is the rule everywhere, the reference's succession holders in `holders()` would have
to stop at last-resort pairs — not recommended: the New Jersey sources support inheritance by a successor of like
jurisdiction.

## Not requested here (separate move, RULE.md §5)

Court attribution: 1,607 of 21,129 decisions filed under 1095 carry the E&A vote roll; a general reader rule (E&A vote
roll in the majority part -> court 1094) would correct them. With A installed, the App. Div. would have power over
such a mis-filed decision; on v8e no status-changing App. Div. row targets one.
