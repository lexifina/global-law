/-!
# Rule identifiers: the nodes of the default trees

Every branch of the Spec's default trees (force, canChangeStatus, status) is labelled by one `RuleId`, and every
verdict carries the list of labels it passed through: its justification path (DESIGN D8). Each label names the
doctrine.md rule it implements; `assume*` labels mark a fallback taken because the data left something unknown
(DESIGN D5: never silent).
-/

namespace CaseLaw2

inductive RuleId where
  -- authority: who binds whom
  /-- H1: a court of last resort is not bound by itself or by its predecessor (stare decisis, not binding). -/
  | H1self
  /-- F1: SCOTUS binds every court on federal law. -/
  | F1
  /-- F1 scope: a SCOTUS reading of state law does not bind. -/
  | F1stateLaw
  /-- E1: before *Erie* (25 Apr 1938) federal general law is not state law. -/
  | E1preErie
  /-- E1 corollary: federal decisions never bind state courts on state law. -/
  | E1fedOnState
  /-- E1: a state's highest court binds federal courts on that state's law. -/
  | E1
  /-- E1 (*West v. AT&T*): intermediate state decisions are data not to be disregarded. -/
  | E1West
  /-- E1 (*King*): state trial decisions are not controlling. -/
  | E1King
  /-- E3: only SCOTUS binds state courts on federal law; lower federal courts are persuasive. -/
  | E3
  /-- E3 table row (`stateFollowsCircuit`). -/
  | E3table
  /-- E3: state decisions on federal law do not bind federal courts. -/
  | E3stateOnFederal
  /-- Courts of different systems on a third system's law: persuasive. -/
  | otherSystem
  /-- F13, §4.4: trial courts bind no one. -/
  | F13
  /-- F12: a special court's own precedent (Tax Court stare decisis). -/
  | F12self
  /-- F11(b): the Federal Circuit binds all federal trial courts on patent law. -/
  | F11b
  /-- F7: a court of appeals binds the trial courts of its circuit (Golsen: the Tax Court by appeal venue). -/
  | F7circuit
  /-- F7: another circuit's decisions are persuasive. -/
  | F7otherCircuit
  /-- Horizontal rule `strong` (F7, §4.1). -/
  | hStrong
  /-- Horizontal rule `soft`. -/
  | hSoft
  /-- Horizontal rule `none`. -/
  | hNone
  /-- Horizontal rule `withinUnitOnly`, same unit. -/
  | hWithinUnit
  /-- Horizontal rule `withinUnitOnly`, other unit. -/
  | hOtherUnit
  /-- H1: the highest court binds every lower court of its system. -/
  | H1
  /-- H2: dual courts of last resort do not bind each other. -/
  | H2dual
  /-- A lower court does not bind a higher one. -/
  | lowerToHigher
  /-- S-TX: TRAP 41.3 transfer, the transferee follows the transferor. -/
  | TXtransfer
  /-- Sister intermediate courts: persuasive. -/
  | sisterCourt
  /-- §4.1 V: trial scope statewide. -/
  | Vstatewide
  /-- §4.1 V: statewide, trial court chooses on conflict. -/
  | Vchoose
  /-- §4.1 V: own unit binds. -/
  | VownUnit
  /-- §4.1 V: other unit binds absent conflict (ownUnitThenAny). -/
  | VotherUnit
  /-- §4.1 V: other unit only persuasive (ownUnitOnly). -/
  | VownUnitOnly
  /-- §4.4: an appellate division of a trial court binds the courts below it in its area. -/
  | appDivBinds
  /-- §4.4: trial-level decisions are persuasive. -/
  | S44
  /-- F10/F11/H3/*M.A.P.*: an adopted decision counts as the adopter's. -/
  | adopted
  /-- S-TX-3: writ/pet. refused gives the opinion last-resort authority. -/
  | TXpromoted
  /-- F9: unpublished-force table row. -/
  | F9table
  /-- F5: an equally divided court decides nothing for other cases. -/
  | F5
  /-- F6: plurality without a Marks holding: persuasive. -/
  | F6
  /-- F6: plurality with a Marks holding. -/
  | F6marks
  /-- HD/WV/TC: memorandum dispositions are persuasive at most. -/
  | memorandum
  -- power to change status
  /-- A treatment cannot act on a later decision. -/
  | cLater
  /-- F1/F14: SCOTUS changes the status of any decision on federal law, and of any federal decision. -/
  | F1abrogate
  /-- v1 `mayOverrule`: a higher court of the same system (a circuit only within its circuit). -/
  | higherCourt
  /-- H1/H3: a court of last resort may overrule itself or its predecessor. -/
  | lastResortSelf
  /-- Same court, horizontal soft/none: any bench. -/
  | sameCourtSoft
  /-- F7, F8: same court, strong rule: en banc (or an equivalent) needed. -/
  | strongNeedsEnBanc
  /-- FL: within the unit only en banc may recede. -/
  | withinUnitEnBanc
  /-- A sister unit has no power. -/
  | otherUnitNoPower
  /-- F10/F11: only the adopter's en banc may overrule an adopted decision. -/
  | adoptedEnBanc
  /-- No rule gives power. -/
  | noPower
  -- status
  /-- §5.1A: same-case history event. -/
  | history
  /-- §5.1B, T1(b,c): admitted treatment. -/
  | treatment
  /-- §7 AB1: supersession by enactment. -/
  | supersession
  /-- T3: the overruling decision lapsed (vacated, reversed, withdrawn): revival. -/
  | revival
  /-- TM2: prospective overruling (*Sunburst*). -/
  | prospective
  -- fallbacks for unknown data (DESIGN D5)
  /-- Issue domain unknown: the source court's home domain (§8.2 anonymous issue). -/
  | assumeHomeDomain
  /-- Publication unknown: treated as published. -/
  | assumePublished
  /-- Form unknown: treated as a full opinion. -/
  | assumeFullForm
  /-- No unpublished-force row: persuasive. -/
  | assumeUnpubPersuasive
  /-- No horizontal row: soft for force (persuasiveStrong). -/
  | assumeHorizontalSoft
  /-- No horizontal row: strong for power (en banc required; conservative). -/
  | assumeStrongForPower
  /-- No trial-scope row: statewide (the majority rule, §4.3). -/
  | assumeStatewide
  /-- Bench unknown: treated as a panel (conservative). -/
  | assumePanel
  /-- Temporal unknown: retroactive (*Harper*). -/
  | assumeRetroactive
  deriving Repr, DecidableEq, Inhabited

def RuleId.toString (r : RuleId) : String := (reprStr r).replace "CaseLaw2.RuleId." ""

instance : ToString RuleId := ⟨RuleId.toString⟩

/-- Render a justification path. -/
def pathString (p : List RuleId) : String := ">".intercalate (p.map RuleId.toString)

end CaseLaw2
