"""Round 5 patch 7: Cert.recogOf (the wiring), Examples (guards, Plessy timeline), Mutants (M28-M34)."""
import os
LP = r"~\Documents\global-law-lean\lean-proofs\LegalProofs\CaseLaw2"


def rw(p, pairs):
    p = os.path.join(LP, p)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70], s.count(a))
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="\n").write(s)


rw("Certificate.lean", [
("""/-- The quote disposes of the case as a whole (DESIGN5 §3.3): it contains a whole-case phrase. -/""",
"""/-- What the runner writes on the event of a witness row: the recognition (W, date(W)) when the verdict is
recognised, nothing otherwise. Every `Recog` the runner makes comes from here. -/
def recogOf (v : RResult) (witness : Nat) (date : Date) : Option Recog :=
  if v.isRecognised then some { witness, date, power := true } else none

/-- An event carries a recognition only when the recognised check passed. -/
theorem recogOf_isSome (v : RResult) (witness : Nat) (date : Date) :
    (recogOf v witness date).isSome = v.isRecognised := by
  unfold recogOf; cases v.isRecognised <;> simp

/-- The quote disposes of the case as a whole (DESIGN5 §3.3): it contains a whole-case phrase. -/"""),
])

rw("Run.lean", [
("""          if (Cert.checkRecognised (inp (some true)) (wit L wr)).isRecognised then
            some { witness := wd.id, date := wd.date, power := true }
          else none""",
"""          Cert.recogOf (Cert.checkRecognised (inp (some true)) (wit L wr)) wd.id wd.date"""),
])

rw("Examples.lean", [
("""
end CaseLaw2.Examples""",
"""
/-! ## Round 5: recognised overrulings and operative words (DESIGN5.md)

*Brown v. Board of Education* (17 May 1954) never says it overrules *Plessy v. Ferguson* (1896). A later decision W
of the same court does. The sentences below are test sentences, not quotations (except Brown's own). -/

def recText := "We have since held otherwise. See Plessy v. Ferguson, 163 U. S. 537, overruled by Brown v. Board of Education, 347 U. S. 483, and the cases that followed."
def recQuote := "Plessy v. Ferguson, 163 U. S. 537, overruled by Brown v. Board of Education, 347 U. S. 483"
def recStart : Nat := ((recText.splitOn recQuote).headD "").length
/-- X = *Plessy*, Y = *Brown*; the text is the later decision W's. -/
def recIn : Cert.Input :=
  { kind := .treat .overruled, textSha := "w", start := recStart, stop := recStart + recQuote.length, quote := recQuote,
    evidence := "cite:163 U.S. 537", part := "majority", shas := ["w"],
    windows := [{ start0 := 0, stop0 := recText.length, text := recText }], ordered := true, authority := some true }
def recRow : Cert.Witness :=
  { known := true, explicit := false, changes := true, byEvidence := "cite:347 U.S. 483", by_ := 0,
    witnessOrdered := true, standing := true, claim := true, power := true, datesKnown := true }
-- recognised: W has power, both names are in the quote, the cue is a recognition cue
#guard Cert.checkRecognised recIn recRow == .recognised false
-- "overruled by" is a round-4 disqualifier: without recognition the row asserts nothing
#guard Cert.checkWitness recIn recRow == .fail .disqualified
#guard Cert.checkRecognised recIn { recRow with claim := false } == .witness (.fail .disqualified)
-- W with mere standing (a panel of the same court under a strong rule): never recognised
#guard Cert.checkRecognised recIn { recRow with power := false } == .witness (.fail .disqualified)
#guard Cert.checkRecognised recIn { recRow with datesKnown := false } == .witness (.fail .disqualified)
-- Y's power over X unknown: recognised, unverified (the effect is `unknown powerUnknown`)
#guard Cert.checkRecognised { recIn with authority := none } recRow == .recognised true
#guard !(Cert.checkRecognised { recIn with authority := some false } recRow).isRecognised
#guard !(Cert.checkRecognised { recIn with part := "dissent" } recRow).isRecognised
#guard !(Cert.checkRecognised { recIn with ordered := false } recRow).isRecognised
#guard !(Cert.checkRecognised recIn { recRow with witnessOrdered := false }).isRecognised
#guard !(Cert.checkRecognised recIn { recRow with standing := false }).isRecognised
#guard !(Cert.checkRecognised recIn { recRow with explicit := true }).isRecognised
-- the same evidence for X and Y
#guard !(Cert.checkRecognised recIn { recRow with byEvidence := "cite:163 U.S. 537" }).isRecognised
-- a negated statement
def recNotText := "Plessy v. Ferguson, 163 U. S. 537, was not overruled by Brown v. Board of Education, 347 U. S. 483."
#guard !(Cert.checkRecognised { recIn with quote := recNotText, start := 0, stop := recNotText.length,
    windows := [{ start0 := 0, stop0 := recNotText.length, text := recNotText }] } recRow).isRecognised
-- the round-4 witness example: Y is named in the quote, so with W's power it is recognised; without, it stays
-- an "at risk" witness row
#guard Cert.checkRecognised witIn { witRow with claim := true, power := true, datesKnown := true } == .recognised false
#guard Cert.checkRecognised witIn { witRow with claim := true, power := false, datesKnown := true } == .witness .ok
-- Y named only in the window, not in the quote: the round-4 check passes, recognition does not
def witShortQuote := "the overruling of Fleet Corporation v. Lustgarten, 280 U. S. 320"
def witShortIn : Cert.Input := { witIn with quote := witShortQuote, stop := 12 + witShortQuote.length }
def witClaim : Cert.Witness := { witRow with claim := true, power := true, datesKnown := true }
#guard Cert.checkRecognised witShortIn witClaim == .witness .ok

/-- *Plessy* (node 1), *Brown* (node 2, 17 May 1954) and a later decision W (node 3, dated 29 June 1992 here) of
the same court that says *Plessy* was overruled by *Brown*. -/
def plessyRow : TEvent :=
  { id := 1, by_ := 2, target := 1, date := 19540517, kind := .overruled, scope := .all, temporal := .unknown,
    explicit := false, recog := some { witness := 3, date := 19920629, power := true } }
-- the recognition is the one the checker's verdict gives
#guard Cert.recogOf (Cert.checkRecognised recIn recRow) 3 19920629 == plessyRow.recog
#guard Cert.recogOf (Cert.checkRecognised recIn { recRow with power := false }) 3 19920629 == none
def plessyEffs : List Effect := recogEffects [] [] plessyRow
#guard plessyEffs.length == 2
#guard plessyEffs.all (·.rule == .recognised) && plessyEffs.all (·.actor == some 2)
-- at risk only: no effect
#guard (recogEffects [] [] { plessyRow with recog := none }).isEmpty
-- W vacated: the negative lapses, the unknown stays (Y stands); Y vacated: both lapse
def wVacated : List HEvent := [{ id := 9, target := 3, by_ := none, date := 19950101, kind := .vacated, scope := .all }]
#guard status (recogEffects [] wVacated plessyRow) 0 19940101 19940101 == .neg .overruled
#guard status (recogEffects [] wVacated plessyRow) 0 19960101 19960101 == .unknown .recognisedLater
#guard status (recogEffects wVacated [] plessyRow) 0 19960101 19960101 == .good
-- Y's power unknown: never negative
#guard status (recogEffects [] [] { plessyRow with powerKnown := false }) 0 20000101 20000101 == .unknown .powerUnknown
-- a partial recognition ("overruled in part by"): partly negative on the whole decision, never negative
#guard status (recogEffects [] [] { plessyRow with scope := .someIssue }) 0 20000101 20000101 == .unknown .partialScope

/-- **The Plessy timeline** (round 5): good law until the day before *Brown*; `unknown recognisedLater` from
*Brown* (17 May 1954) until the day before the later court says so; overruled from that day. -/
theorem plessy_timeline :
    status plessyEffs 0 19540516 19540516 = .good ∧
    status plessyEffs 0 19540517 19540517 = .unknown .recognisedLater ∧
    status plessyEffs 0 19920628 19920628 = .unknown .recognisedLater ∧
    status plessyEffs 0 19920629 19920629 = .neg .overruled := by decide

/-- Brown's own sentence (347 U.S. 483, 494-95). -/
def brownText := "Whatever may have been the extent of psychological knowledge at the time of Plessy v. Ferguson, this finding is amply supported by modern authority. Any language in Plessy v. Ferguson contrary to this finding is rejected. We conclude that in the field of public education the doctrine of \\"separate but equal\\" has no place."
def brownQuote := "Any language in Plessy v. Ferguson contrary to this finding is rejected."
def brownStart : Nat := ((brownText.splitOn brownQuote).headD "").length
def brownIn : Cert.Input :=
  { kind := .treat .disapproved, textSha := "b", start := brownStart, stop := brownStart + brownQuote.length,
    quote := brownQuote, evidence := "name:Plessy Ferguson", part := "majority", shas := ["b"],
    windows := [{ start0 := 0, stop0 := brownText.length, text := brownText }], ordered := true, authority := some true }
-- operative words: admitted with the claim; the round-4 check has no such cue for `disapproved`
#guard Cert.checkOperative brownIn true == .ok
#guard Cert.check brownIn == .fail .noCue
-- not the whole case: the scope is demoted
#guard Cert.wholeCase brownQuote == false
#guard Cert.wholeCase "Plessy v. Ferguson is no longer good law." == true
#guard Cert.checkOperative { brownIn with kind := .treat .overruled } true == .fail .operativeBadRow
#guard Cert.checkOperative brownIn false == .fail .operativeBadRow
#guard Cert.checkOperative { brownIn with part := "dissent" } true == .fail .partNotMajority
-- courts reject arguments constantly: an argument is not a case
def brownArgText := "We reject the argument that Plessy v. Ferguson controls this case."
def brownArgIn : Cert.Input :=
  { brownIn with quote := brownArgText, start := 0, stop := brownArgText.length,
    windows := [{ start0 := 0, stop0 := brownArgText.length, text := brownArgText }] }
#guard Cert.checkOperative brownArgIn true == .fail .disqualified
-- the target must be named in the quote itself, not only in the window
def brownTail := "contrary to this finding is rejected."
#guard Cert.checkOperative { brownIn with quote := brownTail,
    start := brownStart + (brownQuote.length - brownTail.length), stop := brownStart + brownQuote.length } true
  == .fail .targetUnresolved
-- classes
#guard Cert.classOf true false brownQuote == .operativeWords
#guard Cert.classOf true false "Betts v. Brady is overruled." == .selfAnnounced
#guard Cert.classOf false true recQuote == .recognised
#guard Cert.classOf false false witQuote == .atRiskWitness

/-- Brown's operative words on Plessy: an explicit `disapproved` row whose scope is demoted (not the whole case). -/
def brownEv : TEvent :=
  { id := 2, by_ := 2, target := 1, date := 19540517, kind := .disapproved, scope := demote .all, temporal := .unknown,
    explicit := true }
#guard status (treatEffects [] brownEv) 0 19540516 19540516 == .good
#guard status (treatEffects [] brownEv) 0 19600101 19600101 == .unknown .partialScope
#guard status (treatEffects [] { brownEv with scope := .all }) 0 19600101 19600101 == .neg .overruled
-- both rows together: the timeline the model now gives for Plessy
#guard status (treatEffects [] brownEv ++ plessyEffs) 0 19540516 19540516 == .good
#guard status (treatEffects [] brownEv ++ plessyEffs) 0 19540517 19540517 == .unknown .recognisedLater
#guard status (treatEffects [] brownEv ++ plessyEffs) 0 19920629 19920629 == .neg .overruled

/-- **No recognised effect without the checker's verdict and W's power**: the runner sets an event's recognition
with `Cert.recogOf` from the recognised check; when W lacks power over X the check never recognises the row
(`Cert.checkRecognised_needs_power`), the event carries no recognition and has no recognised effect. With
`witness_row_no_effect`, such a row has no status effect at all. -/
theorem recognised_effect_needs_power (c : Cert.Input) (w : Cert.Witness) (hp : w.power = false)
    (wn : Nat) (d : Date) (byHist wHist : List HEvent) (tr : TEvent)
    (hr : tr.recog = Cert.recogOf (Cert.checkRecognised c w) wn d) : recogEffects byHist wHist tr = [] := by
  apply witness_without_claim_no_effect
  rw [hr]
  simp [Cert.recogOf, Cert.checkRecognised_needs_power c w hp]

/-- **A recognised row is never an explicit row**: the recognised check passes only on `explicit = 0`, so the
event's `treatEffect` is none: its only effects are the two recognised ones. -/
theorem recognised_row_only_recog_effects (c : Cert.Input) (w : Cert.Witness)
    (h : (Cert.checkRecognised c w).isRecognised = true) (byHist : List HEvent) (tr : TEvent)
    (he : tr.explicit = w.explicit) : treatEffect byHist tr = none :=
  inferred_treatment_no_effect byHist tr (he.trans (Cert.checkRecognised_sound c w h).2.2.2.2.2.1)

end CaseLaw2.Examples"""),
])

rw("Mutants.lean", [
("""  /-- round 2: the Horty binding base in a line -/
  base : (Nat → Bool) → Nat → List (Held Horty.FCase) → List Horty.FCase := Spec.lineBase""",
"""  /-- round 2: the Horty binding base in a line -/
  base : (Nat → Bool) → Nat → List (Held Horty.FCase) → List Horty.FCase := Spec.lineBase
  /-- round 5: the recognised checker, the recognised effects, the operative-words checker, the scope demotion -/
  checkRecognised : Cert.Input → Cert.Witness → Cert.RResult := Cert.checkRecognised
  recogEffects : List HEvent → List HEvent → TEvent → List Effect := Spec.recogEffects
  checkOperative : Cert.Input → Bool → Cert.Result := Cert.checkOperative
  demote : Scope → Scope := Spec.demote"""),
("""def mutants : List (String × Impl) := [""",
"""/-! ### Round 5 mutants -/

/-- Recognition on mere standing: W's power over X is not checked. -/
def m28rec (c : Cert.Input) (w : Cert.Witness) : Cert.RResult := Cert.checkRecognised c { w with power := true }
/-- A recognised row negative from date(Y), as if Y had said so itself. -/
def m29eff (bh wh : List HEvent) (tr : TEvent) : List Effect :=
  (Spec.recogEffects bh wh tr).map ({ · with start := tr.date })
/-- Recognition on the round-4 text checks: a name in the window suffices. -/
def m30rec (c : Cert.Input) (w : Cert.Witness) : Cert.RResult :=
  if w.claim && w.power && w.datesKnown then
    match Cert.checkWitness c w with
    | .ok => .recognised false
    | .okUnverifiedBy => .recognised true
    | r => .witness r
  else .witness (Cert.checkWitness c w)
/-- A recognised row that never becomes negative (the first effect only). -/
def m31eff (bh wh : List HEvent) (tr : TEvent) : List Effect := (Spec.recogEffects bh wh tr).take 1
/-- Operative words keep the scope they claim: no demotion. -/
def m32demote (s : Scope) : Scope := s
/-- An operative-words checker that takes any object: arguments and contentions too. -/
def m33op (c : Cert.Input) (e : Bool) : Cert.Result :=
  match Cert.checkOperative c e with
  | .fail .disqualified => .ok
  | r => r
/-- An "at risk" witness row takes effect: every implicit row counts as recognised on its own date. -/
def m34eff (bh wh : List HEvent) (tr : TEvent) : List Effect :=
  Spec.recogEffects bh wh { tr with recog := tr.recog <|> some { witness := 0, date := tr.date, power := true } }

def eOld : Effect := { eNeg with start := 19000101 }

def properties5 : List (String × (Impl → Bool)) := [
  ("checkRecognised_needs_power", fun i => !(i.checkRecognised recIn { recRow with power := false }).isRecognised),
  ("recognised_never_neg_before_witness", fun i =>
    !isNeg (i.status (i.recogEffects [] [] plessyRow) 0 19600101 19600101)),
  ("checkRecognised_sound: names in the quote", fun i => !(i.checkRecognised witShortIn witClaim).isRecognised),
  ("explicit_recognised_agree_from_witness", fun i =>
    i.status (i.recogEffects [] [] plessyRow) 0 20000101 20000101 ==
      i.status (i.treatEffect [] { plessyRow with explicit := true, recog := none }).toList 0 20000101 20000101),
  ("demoted_never_neg", fun i =>
    !isNeg (i.status (i.treatEffect [] { brownEv with scope := i.demote .all }).toList 0 19600101 19600101)),
  ("checkOperative_sound: object", fun i => !(i.checkOperative brownArgIn true).admitted),
  ("witness_without_claim_no_effect", fun i => (i.recogEffects [] [] { plessyRow with recog := none }).isEmpty),
  ("recognised_never_weakens", fun i =>
    (i.status [eOld] 0 19600101 19600101).rank ≤
      (i.status (i.recogEffects [] [] plessyRow ++ [eOld]) 0 19600101 19600101).rank)
]

def mutants : List (String × Impl) := ["""),
("""  ("M27 witness row may be explicit or lack standing", { checkWitness := m27wit })
]""",
"""  ("M27 witness row may be explicit or lack standing", { checkWitness := m27wit }),
  ("M28 recognition on mere standing", { checkRecognised := m28rec }),
  ("M29 recognised row negative from date(Y)", { recogEffects := m29eff }),
  ("M30 recognition with a name only in the window", { checkRecognised := m30rec }),
  ("M31 recognised row never negative", { recogEffects := m31eff }),
  ("M32 operative words keep scope all", { demote := m32demote }),
  ("M33 operative words on arguments", { checkOperative := m33op }),
  ("M34 at-risk witness row takes effect", { recogEffects := m34eff })
]"""),
("""def killMatrix : List (String × List String) := properties.map fun (n, p) => (n, killers p)

#eval killMatrix
-- every property holds of the specification
#guard properties.all fun (_, p) => p spec
-- every property is falsified by at least one mutant
#guard properties.all fun (_, p) => !(killers p).isEmpty
-- every mutant is caught by at least one property
#guard mutants.all fun (_, m) => properties.any fun (_, p) => !p m""",
"""def killMatrix : List (String × List String) := (properties ++ properties5).map fun (n, p) => (n, killers p)

#eval killMatrix
-- every property holds of the specification
#guard (properties ++ properties5).all fun (_, p) => p spec
-- every property is falsified by at least one mutant
#guard (properties ++ properties5).all fun (_, p) => !(killers p).isEmpty
-- every mutant is caught by at least one property
#guard mutants.all fun (_, m) => (properties ++ properties5).any fun (_, p) => !p m
-- round 5: each new mutant is caught by a round-5 property, and no round-5 mutant breaks a round-4 property's
-- verdict on the specification's own behaviour (the old matrix is unchanged)
#guard (mutants.drop 27).all fun (_, m) => properties5.any fun (_, p) => !p m
#guard (properties.length, properties5.length, mutants.length) == (27, 8, 34)"""),
])
print("patched")
