import LegalProofs.CaseLaw2.Examples

/-!
# Falsifiability: would a broken version pass? (DESIGN D3)

`Impl` bundles the functions the theorems are about. `spec` is the real one; each mutant breaks one rule the way a
plausible bug would (Erie both ways, a panel overruling a panel, ignoring the unpublished cap, ignoring partial scope,
retroactive supersession, ignoring revival, a checker that accepts dissents …).

Each property below is the executable instance of a registered theorem (Registry.lean), evaluated on the real-case
record of `Examples.lean`. The `#guard`s check that
* every property holds of `spec`,
* every property fails on at least one mutant (so the theorem has teeth), and
* every mutant is caught by at least one property.
The full kill matrix is printed by `#eval killMatrix` and recorded in `caselaw-lean-2/LEAN.md`.
-/

namespace CaseLaw2.Mutants
open CaseLaw2 CaseLaw2.Spec CaseLaw2.Exec CaseLaw2.Examples

structure Impl where
  relation : Lookups → CourtEpoch → Decision → Domain → Query → Force × RuleId := Spec.relation
  force : Lookups → Decision → Holding → Bool → Query → Option (Force × List RuleId) := Spec.force
  canChange : Lookups → Decision → Decision → Option Domain → Option (Bool × RuleId) := canChangeStatus
  status : List Effect → Nat → Nat → Nat → Status := Spec.status
  treatEffect : List HEvent → TEvent → Option Effect := Spec.treatEffect
  superEffect : SEvent → Option Effect := Spec.superEffect
  check : Cert.Input → Cert.Result := Cert.check
  /-- round 4: the witness-row checker -/
  checkWitness : Cert.Input → Cert.Witness → Cert.WResult := Cert.checkWitness
  resolve : Bool → Option TrialScope → List Cand → List Cand := Spec.resolve
  statusFor : (Nat → Bool) → List Effect → Nat → Nat → Nat → Status := Spec.statusFor
  /-- round 2: the status row of a pure line (`status_lines.tsv`) -/
  lineStatus : Line → List Effect → Nat → Nat → Nat → Status := Spec.lineStatus
  /-- round 2: the holdings that count at a court (splits, conflicts) -/
  held : (List Effect → List Effect) → Nat → List (Held Nat) → List Nat := Spec.heldVia
  /-- round 2: the Horty binding base in a line -/
  base : (Nat → Bool) → Nat → List (Held Horty.FCase) → List Horty.FCase := Spec.lineBase
  /-- round 5: the recognised checker, the recognised effects, the operative-words checker, the scope demotion -/
  checkRecognised : Cert.Input → Cert.Witness → Cert.RResult := Cert.checkRecognised
  recogEffects : List HEvent → List HEvent → TEvent → List Effect := Spec.recogEffects
  checkOperative : Cert.Input → Bool → Cert.Result := Cert.checkOperative
  demote : Scope → Scope := Spec.demote
  /-- round 6: the anchored history checker -/
  checkAnchored : Cert.Input → Cert.Anchor → Cert.Result := Cert.checkAnchored
  /-- round 7: the treatment step (joined and doctrine rows), the doctrine effects, the table's doctrine uniqueness,
  the history step under claims -/
  checkTreatment : Cert.Input → Bool → Cert.TClaim → List Cert.Joined → Cert.Result := Cert.checkTreatment
  doctrineEffects : List HEvent → TEvent → List Effect := Spec.doctrineEffects
  doctrineFinal : List Cert.DoctrineRow → Cert.DoctrineRow → Cert.Result → Cert.Result := Cert.doctrineFinal
  checkHistory7 : Cert.Input → Option Cert.Anchor → Cert.HClaims → Cert.Result := Cert.checkHistory7
  /-- round 8 -/
  checkHistory8 : Cert.Input → Option Cert.Anchor → Option Cert.Bridge → Cert.HClaims → Cert.Result :=
    Cert.checkHistory8
  /-- round 8 (§6): the history authority under an `oldCircuit` claim -/
  histPower : Lookups → Decision → Decision → Bool → Option Bool := Exec.histPower8
  /-- round 9 (§4): a node's zone lines, then the zone test after the row's verdict (the runner's composition) -/
  partZone : List Cert.Zone → Cert.Input → List Cert.Joined → Cert.Result → Cert.Result :=
    fun raw c js r => Cert.zoneThen (Cert.nodeZones raw) c js r
  /-- round 9 batch 2: the treatment step under a `joinedFar` claim (§5) and under an `implicitReject` claim (§7); the
  round-8 history step with the judge-form anchor cues (§8) -/
  checkTreatmentF : Bool → List Nat → Cert.Input → Bool → Cert.TClaim → List Cert.Joined → Cert.Result :=
    Cert.checkTreatmentF
  checkTreatmentI : Bool → Cert.Input → Bool → Cert.TClaim → List Cert.Joined → Cert.Result := Cert.checkTreatmentI
  checkHistory8J : Cert.Input → Option Cert.Anchor → Option Cert.Bridge → Cert.HClaims → Cert.Result :=
    Cert.checkHistory8J
  /-- round 10 (§4): the remand check after the row's round-9 verdict -/
  remandThen : Option Cert.Remand → Cert.Input → Cert.Result → Cert.Result := Cert.remandThen
  /-- round 10 (§6): the round-9 history step with the trial bridge -/
  checkHistory8T : Option Cert.TBridge → Cert.Input → Option Cert.Anchor → Option Cert.Bridge → Cert.HClaims →
    Cert.Result := Cert.checkHistory8T
  /-- round 11 (§5.1): the round-10 history step with the `anchorTribunal` cue test -/
  checkHistory8A : Option Cert.TBridge → Cert.Input → Option Cert.Anchor → Option Cert.Bridge → Cert.HClaims →
    Cert.Result := Cert.checkHistory8A
  /-- round 11 (§5.2): the identity-tie check after the row's round-11 verdict -/
  identityThen : Option Cert.Identity → Cert.Input → Cert.Result → Cert.Result := Cert.identityThen

def spec : Impl := {}

/-! ## Test instances (real courts from `Examples`) -/

def E' (c : Nat) (d : Nat) : CourtEpoch := (L.epochAt c d).getD default
def qAt (c : Decision) : Query := (queryFor L c).getD default
def fedQ := qAt ndtex2005
def caSupQ := qAt { caSuper2010 with court := caSup, id := 90 }
def dcSupQ := qAt dcSuper1990

def ledbetterAct : SEvent :=
  { id := 1, target := 11, scope := .issues [3], enacted := 20090129, effective := 20090129, retroactiveTo := some 20070528,
    explicit := true }
def ePartial : Effect :=
  { eff := .neg .overruled, start := 19950101, lapse := none, scope := .issues [2], conductFrom := 0, rule := .treatment,
    src := 3 }
def eUnknown : Effect := { ePartial with eff := .unknown .enBancRuleUnknown, scope := .all, src := 4 }
def eNeg : Effect := { ePartial with scope := .all }
def vacatedOverruler : List HEvent := [{ id := 5, target := 14, by_ := none, date := 19990101, kind := .vacated, scope := .all }]

def certGideon : Cert.Input := certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 48 "cite:316 U.S. 455" "majority"

/-! ## Properties (one per registered theorem family) -/

def properties : List (String × (Impl → Bool)) := [
  ("scotus_binds_federal", fun i =>
    (i.relation L (E' scotus 19420601) betts .federalGeneral fedQ).1 == .binding),
  ("nothing_binds_last_resort", fun i =>
    [E' scotus 19420601, E' caApp 20010101, E' caSup 19900101, E' ca5 19750301, E' caSuper 19900101].all fun S =>
      (i.relation L S caApp1 (.stateLaw 5) caSupQ).1 != .binding),
  ("erie_one_directional", fun i =>
    (i.relation L (E' gaSup 19950101) gaSup1995 .federalGeneral fedQ).1 != .binding &&
    (i.relation L (E' dcCir 19750101) dcCir1975 (.stateLaw 51) dcSupQ).1 != .binding),
  ("trial_never_binding", fun i =>
    [fedQ, qAt ndtex2010, qAt ndga1950].all fun q =>
      (i.relation L (E' ndtex 20010101) ndtex2001 .federalGeneral q).1.rank ≤ Force.persuasive.rank),
  ("no_panel_overrules_panel_in_strong", fun i => (i.canChange L ca5in1982 ca5in1975 none).map (·.1) == some false),
  ("only_scotus_changes_scotus", fun i =>
    (i.canChange L gaSup1995 bowers none).map (·.1) == some false &&
    (i.canChange L ca5in1982 bowers none).map (·.1) == some false),
  ("status_perm", fun i => i.status [eNeg, eUnknown] 0 20000101 20000101 == i.status [eUnknown, eNeg] 0 20000101 20000101),
  ("partial_touches_only", fun i => i.status [ePartial] 1 20000101 20000101 == .good),
  ("supersession_prospective", fun i =>
    match i.superEffect ledbetterAct with
    | some e => i.status [e] 3 20100101 20060101 == .good && i.status [e] 3 20100101 20080101 == .neg .superseded
    | none => false),
  ("status_mono / dated effect", fun i =>
    i.status [eNeg] 0 19940101 19940101 == .good && i.status [eNeg] 0 19960101 19960101 == .neg .overruled),
  ("revival (lapse honoured)", fun i =>
    match i.treatEffect vacatedOverruler (tr 9 14 13 19950101) with
    | some e => i.status [e] 0 20000101 20000101 == .good
    | none => false),
  ("soft_treatment_no_effect", fun i =>
    (i.treatEffect [] { (tr 9 14 13 19950101) with kind := .questioned }).isNone),
  ("checkCert_sound: part", fun i =>
    !(i.check { certGideon with part := "dissent" }).admitted),
  ("checkCert_sound: disqualifier", fun i =>
    !(i.check { certIn "Appellant's first point of error is overruled" 0 "name:Smith Jones" "majority" with
        windows := [{ start0 := 0, stop0 := ptText.length, text := ptText }] }).admitted),
  ("checkCert_sound: quote at offset", fun i => !(i.check { certGideon with start := 47, stop := 47 + 50 }).admitted),
  ("checkCert_sound: admits Gideon", fun i => i.check certGideon == .ok),
  ("checkCert_window_hash", fun i =>
    !(i.check (certGideonH (some "0000000000000000000000000000000000000000"))).admitted &&
      !(i.check (certGideonH none)).admitted),
  ("checkCert_cite_index", fun i => !(i.check (certGideonI (idx "316us455" (betts.id + 1)))).admitted),
  ("unpublished cap (F9)", fun i =>
    ((queryFor L ndtex2001).bind (i.force L ca5unpub1999 (anon ca5unpub1999) false)).map (·.1) != some .binding),
  ("scotus_resolves_split", fun i =>
    (i.resolve false none (scotusCand :: caCands)).all (·.answer == .yes)),
  ("adopted_status_per_heir (Bonner)", fun i =>
    i.statusFor (inLine L ca11in1990) (effs 6) 0 19900301 19900301 == .good &&
      i.statusFor (inLine L ca5in1990) (effs 6) 0 19900101 19900101 == .neg .overruled),
  ("division_cannot_overrule (M.A.P.)", fun i =>
    (i.canChange L dcCA1990 dcCA1980 none).map (·.1) == some false &&
      (i.canChange L dcCAenBanc dcCA1980 none).map (·.1) == some true),
  -- round 2 (DEVIATIONS 74–78): status per line of authority everywhere
  ("lineStatus_heir_agrees (Bonner rows)", fun i =>
    i.lineStatus (.heir ca11) (effs 6) 0 19900301 19900301 ==
        statusFor (inLine L ca11in1990) (effs 6) 0 19900301 19900301 &&
      i.lineStatus .orig (effs 6) 0 19900101 19900101 == statusFor (inLine L ca5in1990) (effs 6) 0 19900101 19900101 &&
      i.lineStatus (.heir ca11) (effs 39) 0 19950101 19950101 == .neg .overruled &&
      i.lineStatus (.heir dcCA) (effs 27) 0 19900101 19900101 ==
        statusFor (inLine L dcSuper1990) (effs 27) 0 19900101 19900101),
  ("heldIn_ignores_unreaching (Salinas conflict)", fun i =>
    i.held (effectsFor L ca11q) 19950101 heldSalinas == [6, 22] &&
      i.held (effectsFor L ca5q) 19950101 heldSalinas == [39, 22]),
  ("mem_lineBase_iff (Horty base in a line)", fun i =>
    !Horty.consistent (i.base (inLine L ca11q) 19950101 heldHorty) &&
      Horty.consistent (i.base (inLine L ca5q) 19950101 heldHorty)),
  ("lineStatus_all / heldIn_all (no heir: union)", fun i =>
    i.lineStatus (.heir ca11) (effs 0) 0 19700101 19700101 == st 0 0 19700101 19700101 &&
      i.lineStatus .orig [eNeg] 0 20000101 20000101 == .neg .overruled &&
      i.held (effectsFor L ca11q) 20100101
        [{ item := 0, issue := 0, effs := effs 0 }, { item := 1, issue := 0, effs := effs 1 }] == [1]),
  -- round 4: witness rows (an implicit overruling stated by a later court)
  ("checkWitness_sound / witness_row_no_effect", fun i =>
    i.checkWitness witIn witRow == .ok &&
      !(i.checkWitness witIn { witRow with explicit := true }).admitted &&
      !(i.checkWitness witIn { witRow with standing := false }).admitted &&
      !(i.checkWitness witIn { witRow with byEvidence := "cite:999 U.S. 1" }).admitted)
]

/-! ## Mutants -/

def m1rel (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query) : Force × RuleId :=
  if S.system == 0 && !dom.federal && q.dst.system != 0 then (.binding, .F1) else Spec.relation L S x dom q
def m2can (L : Lookups) (b x : Decision) (d : Option Domain) : Option (Bool × RuleId) :=
  match canChangeStatus L b x d with
  | some (false, .strongNeedsEnBanc) => some (true, .sameCourtSoft)
  | r => r
def m3force (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query) : Option (Force × List RuleId) :=
  Spec.force L { x with pub := some .published } h p q
def widen (e : Effect) : Effect :=
  match e.scope with
  | .issues _ => { e with scope := .all }
  | _ => e
def m4status (effs : List Effect) (k t u : Nat) : Status := Spec.status (effs.map widen) k t u
def m5super (s : SEvent) : Option Effect := (Spec.superEffect s).map ({ · with conductFrom := 0 })
def m6treat (h : List HEvent) (t : TEvent) : Option Effect := (Spec.treatEffect h t).map ({ · with lapse := none })
def m7check (c : Cert.Input) : Cert.Result := Cert.check { c with part := "majority" }
def m8check (c : Cert.Input) : Cert.Result :=
  match Cert.check c with
  | .fail .disqualified => .ok
  | r => r
def m9check (c : Cert.Input) : Cert.Result :=
  match Cert.check c with
  | .fail .quoteMismatch => .ok
  | r => r
def m10rel (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query) : Force × RuleId :=
  if S.tier == .trial then (.binding, .F13) else Spec.relation L S x dom q
def m11rel (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query) : Force × RuleId :=
  if S.scotus then (.persuasive, .F1) else Spec.relation L S x dom q
def m12rel (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query) : Force × RuleId :=
  if S.tier == .appellate && q.dst.tier == .last && S.system == q.dst.system then (.binding, .H1)
  else Spec.relation L S x dom q
def m13status (effs : List Effect) (k t u : Nat) : Status :=
  match effs.find? (fun e => e.contrib k t u != .good) with
  | some e => e.contrib k t u
  | none => .good
def m14treat (h : List HEvent) (t : TEvent) : Option Effect := Spec.treatEffect h { t with kind := .overruled }
def m15can (L : Lookups) (b x : Decision) (d : Option Domain) : Option (Bool × RuleId) :=
  match canChangeStatus L b x d with
  | some (false, r) => some (true, r)
  | r => r
def m18check (c : Cert.Input) : Cert.Result := Cert.check { c with start := c.start + 1, stop := c.stop + 1 }
/-- A checker that trusts the window text (no hash recomputed). -/
def m19check (c : Cert.Input) : Cert.Result :=
  Cert.check { c with hashRequired := false, windows := c.windows.map ({ · with hash := none }) }
/-- A checker that only looks for the citation in the text (no index resolution). -/
def m20check (c : Cert.Input) : Cert.Result := Cert.check { c with citeIndex := none }
def m16resolve (_ : Bool) (_ : Option TrialScope) (cs : List Cand) : List Cand := cs.filter Cand.counts
def m17status (effs : List Effect) (k t u : Nat) : Status := Spec.status (effs.map ({ · with start := 0 })) k t u
/-- Status global after an adoption cut-off (the bug hunt H4 found: 25 false `citesOverruled`). -/
def m21statusFor (_ : Nat → Bool) (effs : List Effect) (k t u : Nat) : Status := Spec.status effs k t u
/-- A court of last resort's divisions overrule its decisions freely (hunt H6, against *M.A.P. v. Ryan*). -/
def m22can (L : Lookups) (b x : Decision) (d : Option Domain) : Option (Bool × RuleId) :=
  match canChangeStatus L b x d with
  | some (false, .strongNeedsEnBanc) =>
    if (L.epochAt b.court b.date).any (·.tier == .last) then some (true, .lastResortSelf)
    else some (false, .strongNeedsEnBanc)
  | r => r

/-- Per-line rows that report the union status (what `status.tsv` alone gave before round 2). -/
def m23line (_ : Line) (effs : List Effect) (k t u : Nat) : Status := Spec.status effs k t u
/-- Splits and conflicts judged on the union status: a decision overruled in one line counts in none. -/
def m24held (_ : List Effect → List Effect) (t : Nat) (hs : List (Held Nat)) : List Nat := heldUnion t hs
/-- A Horty base that keeps precedents overruled in the court's line. -/
def m25base (_ : Nat → Bool) (_ : Nat) (hs : List (Held Horty.FCase)) : List Horty.FCase :=
  (hs.filter (·.binds)).map (·.item)
/-- An heir's row that drops the effects reaching every line (history, statutes, SCOTUS). -/
def m26line (ln : Line) (effs : List Effect) (k t u : Nat) : Status :=
  match ln with
  | .orig => Spec.lineStatus .orig effs k t u
  | .heir a => Spec.lineStatus (.heir a) (effs.filter (·.limited)) k t u

/-- A witness checker that takes any later court's remark, also on a row marked explicit (which would change
status). -/
def m27wit (c : Cert.Input) (w : Cert.Witness) : Cert.WResult :=
  Cert.checkWitness c { w with explicit := false, standing := true }

/-! ### Round 5 mutants -/

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

/-! ### Round 6 mutants (anchored history rows, `round6/history/DESIGN6.md` §4) -/

/-- The anchored checker's skeleton with its five anchor tests as parameters. With the real tests it is the real
checker (the `example` below); each mutant replaces one test. -/
def anchoredWith (qOk : Cert.Input → Cert.Anchor → Bool) (cue disq : Cert.Anchor → Bool)
    (res : Cert.Input → Cert.Anchor → Bool) (part : Cert.Anchor → Bool) (c : Cert.Input) (a : Cert.Anchor) :
    Cert.Result :=
  if !qOk c a then .fail .anchorMismatch
  else if !cue a then .fail .anchorNoCue
  else if disq a then .fail .anchorDisqualified
  else if !res c a then .fail .anchorUnresolved
  else if !part a then .fail .anchorPart
  else Cert.check { c with selfText := true }

example : anchoredWith Cert.anchorQuoteOk Cert.anchorHasCue Cert.anchorDisqualified Cert.anchorResolves
    Cert.anchorPartOk = Cert.checkAnchored := rfl

/-- An anchor that names no court or proceeding: the cue test is dropped. -/
def m35anc : Cert.Input → Cert.Anchor → Cert.Result :=
  anchoredWith Cert.anchorQuoteOk (fun _ => true) Cert.anchorDisqualified Cert.anchorResolves Cert.anchorPartOk
/-- An anchor on an earlier proceeding ("former appeal", "see also"): the disqualifier test is dropped. -/
def m36anc : Cert.Input → Cert.Anchor → Cert.Result :=
  anchoredWith Cert.anchorQuoteOk Cert.anchorHasCue (fun _ => false) Cert.anchorResolves Cert.anchorPartOk
/-- The target evidence anywhere in the anchor's window (the one-quote rule), not in the anchor quote. -/
def m37anc : Cert.Input → Cert.Anchor → Cert.Result :=
  anchoredWith Cert.anchorQuoteOk Cert.anchorHasCue Cert.anchorDisqualified
    (fun c a => Cert.resolves { a.input c with selfText := false }) Cert.anchorPartOk
/-- The anchor's window is trusted: its hash is not checked (the disposition's still is). -/
def m38anc : Cert.Input → Cert.Anchor → Cert.Result :=
  anchoredWith (fun c a => Cert.anchorQuoteOk
      { c with hashRequired := false, windows := c.windows.map ({ · with hash := none }) } a)
    Cert.anchorHasCue Cert.anchorDisqualified Cert.anchorResolves Cert.anchorPartOk
/-- Any anchor part: a dissent's description of the case below counts. -/
def m39anc : Cert.Input → Cert.Anchor → Cert.Result :=
  anchoredWith Cert.anchorQuoteOk Cert.anchorHasCue Cert.anchorDisqualified Cert.anchorResolves (fun _ => true)
/-- The anchor may come from another text: every text's windows are searched, not the certificate's own. -/
def m40anc : Cert.Input → Cert.Anchor → Cert.Result :=
  anchoredWith (fun c a => Cert.anchorQuoteOk { c with windows := c.windows ++ ancOtherWins } a)
    Cert.anchorHasCue Cert.anchorDisqualified Cert.anchorResolves Cert.anchorPartOk

/-- Round 6: one property per anchor check; each admits the good row and rejects one bad anchor. -/
def properties6 : List (String × (Impl → Bool)) := [
  ("checkAnchored_sound: anchor cue", fun i =>
    i.checkAnchored ancIn ancOk == .ok && !(i.checkAnchored ancIn ancNoCue).admitted),
  ("checkAnchored_sound: anchor disqualifier", fun i =>
    i.checkAnchored ancIn ancOk == .ok && !(i.checkAnchored ancFormerIn ancFormer).admitted),
  ("checkAnchored_sound: evidence in the anchor quote", fun i =>
    i.checkAnchored ancIn ancOk == .ok && !(i.checkAnchored ancIn ancNoCite).admitted),
  ("checkAnchored_window_hash", fun i =>
    i.checkAnchored (ancInH (some (Sha1.hex ancHead)) (some (Sha1.hex ancTail))) ancOk == .ok &&
      !(i.checkAnchored (ancInH (some ancBadSha) (some (Sha1.hex ancTail))) ancOk).admitted &&
      !(i.checkAnchored (ancInH none (some (Sha1.hex ancTail))) ancOk).admitted),
  ("checkAnchored_sound: anchor part", fun i =>
    i.checkAnchored ancIn ancOk == .ok && !(i.checkAnchored ancIn { ancOk with part := "dissent" }).admitted),
  ("checkAnchored_sound: anchor in the certificate's text", fun i =>
    i.checkAnchored ancIn ancOk == .ok && !(i.checkAnchored ancIn ancForeign).admitted)
]

/-! ### Round 7 mutants (joined certificates, doctrine rows, history claims; `round7/DESIGN7.md` §2–3) -/

/-- The joined checker's skeleton with the count bound, the quote test, the relation and the evidence test as
parameters. With the real tests it is the real checker (the `example` below); each mutant replaces one. -/
def joinedWith (count : List Cert.Joined → Bool) (qOk : Cert.Input → Cert.Joined → Bool)
    (rel : Cert.TClaim → Cert.Input → Cert.Joined → Bool) (res : Cert.Input → Cert.Joined → Bool)
    (c : Cert.Input) (e : Bool) (cl : Cert.TClaim) (js : List Cert.Joined) : Cert.Result :=
  if !(count js && js.all (qOk c)) then .fail .joinedMismatch
  else if !js.all Cert.joinedPartOk then .fail .joinedPart
  else if js.any (Cert.joinedDisqualified c) then .fail .joinedDisqualified
  else if !js.all (rel cl c) then .fail .joinedRelation
  else if !js.any (res c) then .fail .joinedUnresolved
  else Cert.mainCheck { c with selfText := true } e cl

example : joinedWith Cert.joinedCountOk Cert.joinedQuoteOk Cert.relationOk Cert.joinedResolves = Cert.checkJoined :=
  rfl

/-- A treatment step whose joined checker is `joinedWith` with the given tests. -/
def treatWith (count : List Cert.Joined → Bool) (qOk : Cert.Input → Cert.Joined → Bool)
    (rel : Cert.TClaim → Cert.Input → Cert.Joined → Bool) (res : Cert.Input → Cert.Joined → Bool) :
    Cert.Input → Bool → Cert.TClaim → List Cert.Joined → Cert.Result :=
  Cert.checkTreatmentWith (joinedWith count qOk rel res)

example : treatWith Cert.joinedCountOk Cert.joinedQuoteOk Cert.relationOk Cert.joinedResolves = Cert.checkTreatment :=
  rfl

/-- The relation with its antecedent and tie tests as parameters. -/
def relWith (ante : Cert.Input → Cert.Joined → Bool) (tie : Cert.TClaim → Cert.Input → Cert.Joined → Bool)
    (cl : Cert.TClaim) (c : Cert.Input) (j : Cert.Joined) : Bool :=
  match j.rel with
  | .antecedent => ante c j
  | .doctrineTie => tie cl c j

/-- An antecedent sentence anywhere before the act: the gap bound is dropped. -/
def m41 := treatWith Cert.joinedCountOk Cert.joinedQuoteOk
  (relWith (fun c j => decide (j.stop ≤ c.start) && Cert.anaphorCue c.quote && Cert.kindCue c) Cert.tieOk)
  Cert.joinedResolves
/-- An act that does not refer back: the anaphor test is dropped. -/
def m42 := treatWith Cert.joinedCountOk Cert.joinedQuoteOk
  (relWith (fun c j => decide (j.stop ≤ c.start) && decide (c.start - j.stop ≤ Cert.joinedGapMax) && Cert.kindCue c)
    Cert.tieOk)
  Cert.joinedResolves
/-- The evidence anywhere in the main quote's windows (the one-quote rule), not in a joined quote. -/
def m43 := treatWith Cert.joinedCountOk Cert.joinedQuoteOk Cert.relationOk
  (fun c _ => Cert.resolves { c with selfText := false, mode := .plain })
/-- A doctrine "tie" that ties nothing: the tie-cue test is dropped. -/
def m44 := treatWith Cert.joinedCountOk Cert.joinedQuoteOk
  (relWith Cert.antecedentOk (fun cl c j => cl == .doctrine && Cert.labelOk j.label && Cert.labelIn c.quote j.label &&
    Cert.labelIn j.quote j.label))
  Cert.joinedResolves
/-- A doctrine tie whose label is not in both quotes. -/
def m45 := treatWith Cert.joinedCountOk Cert.joinedQuoteOk
  (relWith Cert.antecedentOk (fun cl _ j => cl == .doctrine && Cert.labelOk j.label && Cert.tieCue j.quote))
  Cert.joinedResolves
/-- A doctrine row with the scope it writes: no demotion. -/
def m46 (bh : List HEvent) (tr : TEvent) : List Effect := Spec.treatEffects bh tr
/-- No doctrine uniqueness: a label the table ties to two targets passes. -/
def m47 (_ : List Cert.DoctrineRow) (_ : Cert.DoctrineRow) (v : Cert.Result) : Cert.Result := v
/-- A third joined line (or none): the count bound is dropped. -/
def m48 := treatWith (fun _ => true) Cert.joinedQuoteOk Cert.relationOk Cert.joinedResolves
/-- A joined quote of another text: other texts' windows are searched too. -/
def m49 := treatWith Cert.joinedCountOk (fun c j => Cert.joinedQuoteOk { c with windows := c.windows ++ jForeignWins } j)
  Cert.relationOk Cert.joinedResolves
/-- orderHead for any court. -/
def m50 := Cert.checkHistory7With (fun h c => decide (Cert.orderHeadFrom ≤ h.date) && Cert.orderHeadKind c.kind &&
  Cert.orderLineCue c && decide (c.quote.length ≤ Cert.orderHeadMaxLen)) Cert.claimCueOk
/-- orderHead at any date (the corpus prints older orders with an opinion part). -/
def m51 := Cert.checkHistory7With (fun h c => h.scotus && Cert.orderHeadKind c.kind &&
  Cert.orderLineCue c && decide (c.quote.length ≤ Cert.orderHeadMaxLen)) Cert.claimCueOk
/-- orderHead for any head matter of the kind ("Motion … denied."): the order-line cue is dropped. -/
def m52 := Cert.checkHistory7With (fun h c => h.scotus && decide (Cert.orderHeadFrom ≤ h.date) &&
  Cert.orderHeadKind c.kind && decide (c.quote.length ≤ Cert.orderHeadMaxLen)) Cert.claimCueOk
/-- "Set aside" as a cue of every kind (a reversal that is "set aside"). -/
def m53 := Cert.checkHistory7With Cert.orderHeadOk (fun h c => Cert.hasCue c || (h.setAside && Cert.setAsideCue c))

example : Cert.checkHistory7With Cert.orderHeadOk Cert.claimCueOk = Cert.checkHistory7 := rfl

/-- Round 7: one property per new rule; each admits a good row and rejects one bad row (`Examples`). -/
def properties7 : List (String × (Impl → Bool)) := [
  ("antecedent_gap: gap", fun i =>
    i.checkTreatment (jIn) true .plain [jNearL] == .ok && !(i.checkTreatment (jIn) true .plain [jFarL]).admitted),
  ("antecedent_gap: anaphor", fun i =>
    i.checkTreatment (jIn) true .plain [jNearL] == .ok && !(i.checkTreatment (jIn jNoAna) true .plain [jNearL]).admitted),
  ("checkJoined_sound: evidence in a joined quote", fun i =>
    i.checkTreatment (jIn) true .plain [jNearL] == .ok && !(i.checkTreatment (jIn) true .plain [jWinL]).admitted),
  ("doctrineTie_label: tie cue", fun i =>
    i.checkTreatment (dIn) true .doctrine [dTieL] == .ok && !(i.checkTreatment (dIn) true .doctrine [dl dNoTie]).admitted),
  ("doctrineTie_label: label in both quotes", fun i =>
    i.checkTreatment (dIn) true .doctrine [dTieL] == .ok &&
      !(i.checkTreatment (dIn) true .doctrine [dl dNoLabel]).admitted),
  ("doctrine_never_neg", fun i =>
    Spec.status (i.doctrineEffects [] brownAllEv) 0 19600101 19600101 == .unknown .partialScope),
  ("doctrine_unique", fun i =>
    i.doctrineFinal uRows (uRows.getD 2 default) .ok == .ok &&
      !(i.doctrineFinal uRows (uRows.headD default) .ok).admitted),
  ("checkJoined_bounded", fun i =>
    i.checkTreatment (jIn) true .plain [jNearL] == .ok &&
      !(i.checkTreatment (jIn) true .plain [jNearL, jNearL, jNearL]).admitted),
  ("checkJoined_sound: joined quote in the row's text", fun i =>
    i.checkTreatment (jIn) true .plain [jNearL] == .ok && !(i.checkTreatment (jIn) true .plain [jForeignL]).admitted),
  ("orderHead_sound: court", fun i =>
    i.checkHistory7 (oIn) none oClaim == .ok && !(i.checkHistory7 (oIn) none { oClaim with scotus := false }).admitted),
  ("orderHead_sound: date", fun i =>
    i.checkHistory7 (oIn) none oClaim == .ok &&
      !(i.checkHistory7 (oIn) none { oClaim with date := 20121231 }).admitted),
  ("orderHead_sound: order line", fun i =>
    i.checkHistory7 (oIn) none oClaim == .ok &&
      !(i.checkHistory7 (oIn "Motion for leave to proceed denied.") none oClaim).admitted),
  ("setAside_only_vacated", fun i =>
    i.checkHistory7 (sIn) none { setAside := true } == .ok &&
      !(i.checkHistory7 (sIn .reversed) none { setAside := true }).admitted)
]

/-! ### Round 8 mutants (bridge evidence, wide anchor cues; `round8/DESIGN8.md` §4–5) -/

/-- The round-8 history step with its bridge steps replaced (the anchor cue is the real one). -/
def h8 (bf : Cert.Input → Cert.Bridge → Option Cert.Reason) :
    Cert.Input → Option Cert.Anchor → Option Cert.Bridge → Cert.HClaims → Cert.Result :=
  Cert.checkHistory8With Cert.anchorCueOk bf

example : h8 Cert.bridgeFail = Cert.checkHistory8 := rfl
example : Cert.bridgeFailWith Cert.bridgeQuoteOk Cert.bridgeDateOk Cert.bridgeClauseOk Cert.bridgeP1 Cert.bridgeP2
    Cert.bridgeChainOk Cert.bridgeActorCite = Cert.bridgeFail := rfl

/-- A bridge quote of any length. -/
def m54 := h8 (Cert.bridgeFailWith (fun c b => Cert.quoteOk (b.input c)) Cert.bridgeDateOk Cert.bridgeClauseOk
  Cert.bridgeP1 Cert.bridgeP2 Cert.bridgeChainOk Cert.bridgeActorCite)
/-- A bridge quote of several clauses ("…; …"). -/
def m55 := h8 (Cert.bridgeFailWith Cert.bridgeQuoteOk Cert.bridgeDateOk (fun _ => true)
  Cert.bridgeP1 Cert.bridgeP2 Cert.bridgeChainOk Cert.bridgeActorCite)
/-- O's citation anywhere in the quote (before X's too): the first citation that maps to O. -/
def m56actor (c : Cert.Input) (b : Cert.Bridge) (_ : Nat) : Option (Nat × Nat) :=
  match c.citeIndex with
  | none => none
  | some m => (Cert.firstSuffix (fun s => Cert.citeFirst m b.lens s == some b.actor) (Cert.bridgeAlnum b)).bind
      fun s => (Cert.headPos s).map (·, b.actor)
def m56 := h8 (Cert.bridgeFailWith Cert.bridgeQuoteOk Cert.bridgeDateOk Cert.bridgeClauseOk
  Cert.bridgeP1 Cert.bridgeP2 Cert.bridgeChainOk m56actor)
/-- No cue sought: the citation after X's is taken as the actor. -/
def m57 := h8 (Cert.bridgeFailWith Cert.bridgeQuoteOk Cert.bridgeDateOk Cert.bridgeClauseOk
  Cert.bridgeP1 (fun _ _ q1 => some q1) Cert.bridgeChainOk Cert.bridgeActorCite)
/-- The first citation after the cue, whatever node it maps to. -/
def m58 := h8 (Cert.bridgeFailWith Cert.bridgeQuoteOk Cert.bridgeDateOk Cert.bridgeClauseOk
  Cert.bridgeP1 Cert.bridgeP2 Cert.bridgeChainOk (fun c b q2 => (Cert.bridgeActorCite c b q2).map (fun pn => (pn.1, b.actor))))
/-- A bridge text of any date (before the order too). -/
def m59 := h8 (Cert.bridgeFailWith Cert.bridgeQuoteOk (fun _ => true) Cert.bridgeClauseOk
  Cert.bridgeP1 Cert.bridgeP2 Cert.bridgeChainOk Cert.bridgeActorCite)
/-- The wide anchor cues without the claim. -/
def m60 := Cert.checkHistory8With (fun _ a => Cert.anchorWideCue a) Cert.bridgeFail
/-- No chain test: another citation may stand between X's and the cue (D8-9). -/
def m61 := h8 (Cert.bridgeFailWith Cert.bridgeQuoteOk Cert.bridgeDateOk Cert.bridgeClauseOk
  Cert.bridgeP1 Cert.bridgeP2 (fun _ _ _ => true) Cert.bridgeActorCite)

/-- Old circuits at any date (after the reorganisation too). -/
def m62 := Exec.histPower8With (fun B X _ => Exec.oldCircuitOk B X 1)
/-- The old-circuit power on a treatments row (the claim applied to `canChangeStatus`). -/
def m63 (L : Lookups) (b x : Decision) (d : Option Domain) : Option (Bool × RuleId) :=
  match canChangeStatus L b x d with
  | some (false, r) =>
    match L.epochAt b.court b.date, L.epochAt x.court x.date with
    | some B, some X => if Exec.oldCircuitOk B X b.date then some (true, .higherCourt) else some (false, r)
    | _, _ => some (false, r)
  | r => r

/-- Round 8: one property per new rule; each admits the good row and rejects one bad row (`Examples`). -/
def properties8 : List (String × (Impl → Bool)) := [
  ("bridge_sound: length", fun i =>
    i.checkHistory8 bIn none (some bGoodB) {} == .ok && !(i.checkHistory8 bIn none (some (bw bLong)) {}).admitted),
  ("bridge_sound: one clause", fun i =>
    i.checkHistory8 bIn none (some bGoodB) {} == .ok && !(i.checkHistory8 bIn none (some (bw bSemi)) {}).admitted),
  ("bridge_order", fun i =>
    i.checkHistory8 bIn none (some bGoodB) {} == .ok && !(i.checkHistory8 bIn none (some (bw bOFirst)) {}).admitted),
  ("bridge_sound: cue", fun i =>
    i.checkHistory8 bIn none (some bGoodB) {} == .ok && !(i.checkHistory8 bIn none (some (bw bAffd)) {}).admitted),
  ("bridge_sound: O's citation", fun i =>
    i.checkHistory8 bIn none (some bGoodB) {} == .ok && !(i.checkHistory8 bIn none (some (bw bOther)) {}).admitted),
  ("bridge_sound: date", fun i =>
    i.checkHistory8 bIn none (some bGoodB) {} == .ok &&
      !(i.checkHistory8 bIn none (some { bGoodB with wDate := 20150101 }) {}).admitted),
  ("anchorWide_no_claim", fun i =>
    i.checkHistory8 awIn (some awAnc) none { anchorWide := true } == .ok &&
      !(i.checkHistory8 awIn (some awAnc) none {}).admitted),
  ("bridge_sound: no citation between X's and the cue", fun i =>
    i.checkHistory8 bIn none (some bGoodB) {} == .ok && !(i.checkHistory8 bIn none (some (bw bChain)) {}).admitted),
  ("oldCircuit_sound: date", fun i =>
    i.histPower L ca5in1975 ndga1950 true == some true && i.histPower L ca5in1982 ndga1950 true == some false),
  ("oldCircuit: history rows only", fun i =>
    -- (the higher-court power is never granted to a treatments row; M15 "no power check" grants every refused power
    -- under its own rule id and is M15's, not this property's)
    i.canChange L ca5in1975 ndga1950 none != some (true, .higherCourt) &&
      i.histPower L ca5in1975 ndga1950 true == some true)
]

/-! ### Round 9 mutants (part zones; `round9/DESIGN9.md` §4) -/

/-- The zone test with the containment test as a parameter. -/
def zoneWith (inZ : Nat → Nat → String → Cert.Zone → Bool) (zs : List Cert.Zone) (c : Cert.Input)
    (js : List Cert.Joined) (r : Cert.Result) : Cert.Result :=
  if zs.isEmpty then r
  else if r.admitted && !(zs.any (inZ c.start c.stop c.part) && js.all (fun j => zs.any (inZ j.start j.stop j.part)))
    then .fail .partZone else r

example : zoneWith Cert.inZone = Cert.zoneThen := rfl

/-- A quote that straddles a zone boundary (it only overlaps a zone of its part). -/
def m64 (raw : List Cert.Zone) : Cert.Input → List Cert.Joined → Cert.Result → Cert.Result :=
  zoneWith (fun s e p z => decide (z.start < e) && decide (s < z.stop) && z.part == p) (Cert.nodeZones raw)
/-- A zone of another part. -/
def m65 (raw : List Cert.Zone) : Cert.Input → List Cert.Joined → Cert.Result → Cert.Result :=
  zoneWith (fun s e _ z => decide (z.start ≤ s) && decide (e ≤ z.stop)) (Cert.nodeZones raw)
/-- The zones of an overlapping or malformed node kept. -/
def m66 (raw : List Cert.Zone) : Cert.Input → List Cert.Joined → Cert.Result → Cert.Result := Cert.zoneThen raw

/-- Round 9: one property per new rule; each admits the good row and rejects one bad row (`Examples`). -/
def properties9 : List (String × (Impl → Bool)) := [
  ("partZone_sound: inside one zone", fun i =>
    i.partZone zGood certGideonZ [] (Cert.check certGideonZ) == .ok &&
      !(i.partZone zStraddle certGideonZ [] (Cert.check certGideonZ)).admitted),
  ("partZone_sound: the row's part", fun i =>
    i.partZone zGood certGideonZ [] (Cert.check certGideonZ) == .ok &&
      !(i.partZone zOther certGideonZ [] (Cert.check certGideonZ)).admitted),
  ("zone_bad_node_ignored", fun i =>
    i.partZone zOverlap certGideonZ [] (Cert.check certGideonZ) == .ok &&
      i.partZone zBadPart certGideonZ [] (Cert.check certGideonZ) == .ok)
]


/-! ### Round 9 batch 2 mutants (far antecedents, implicit rejection; `round9/DESIGN9.md` §5, §7, D9-7) -/

/-- The treatment step under a `joinedFar` claim with the far tests replaced. -/
def farStep (fr : List Nat → Cert.Input → Cert.Joined → Option Cert.Reason) (far : Bool) (lens : List Nat) :
    Cert.Input → Bool → Cert.TClaim → List Cert.Joined → Cert.Result :=
  if far then Cert.checkTreatmentWith (Cert.checkJoinedFarWith (fr lens)) else Cert.checkTreatment

example : farStep Cert.farReason = Cert.checkTreatmentF := rfl

/-- A far antecedent past another decision's citation. -/
def m67 := farStep (fun _ => Cert.farReasonWith Cert.joinedFarMax (fun _ _ _ => true)
  (fun c => Cert.anaphorCue c.quote && Cert.kindCue c))
/-- A far antecedent at any distance. -/
def m68 := farStep (fun lens => Cert.farReasonWith 1000000000 (Cert.farKeyOk lens)
  (fun c => Cert.anaphorCue c.quote && Cert.kindCue c))
/-- A far antecedent without an anaphor in the act. -/
def m69 := farStep (fun lens => Cert.farReasonWith Cert.joinedFarMax (Cert.farKeyOk lens) Cert.kindCue)
/-- The implicit cues on any kind (an `overruled` row too). -/
def m70 (imp : Bool) (c : Cert.Input) (e : Bool) (cl : Cert.TClaim) (js : List Cert.Joined) : Cert.Result :=
  if imp then Cert.checkImplicitWith (fun _ => true) (fun c => Cert.hasCue c || Cert.implicitCue c) c e js
  else Cert.checkTreatment c e cl js
/-- The implicit cues on a soft row without the claim. -/
def m71 (_ : Bool) (c : Cert.Input) (e : Bool) (cl : Cert.TClaim) (js : List Cert.Joined) : Cert.Result :=
  if Cert.implicitSoft c.kind then Cert.checkImplicit c e js else Cert.checkTreatment c e cl js


/-- `canChangeStatus` with its adoption branch replaced (`adopt X B` decides whether the branch is taken; `power`
whether it gives power). -/
def canChangeAdopt (adopt : Lookups → Decision → Decision → CourtEpoch → CourtEpoch → Bool) (power : Bool)
    (L : Lookups) (b x : Decision) (dom? : Option Domain) : Option (Bool × RuleId) :=
  match L.epochAt b.court b.date, L.epochAt x.court x.date with
  | some B, some X =>
    let dom := dom?.getD X.home
    some <|
      if b.date < x.date then (false, .cLater)
      else if B.scotus && (dom.federal || X.system == 0) then (true, .F1abrogate)
      else if B.system == X.system && X.tier.rank < B.tier.rank && B.tier != .bap &&
          (!B.federal || B.tier != .appellate || X.circuit == B.circuit ||
            (B.circuit == 13 && dom == .federalPatent)) &&
          (B.tier != .appDivTrial || (b.unit.isSome && b.unit == x.unit)) then (true, .higherCourt)
      else if B.tier == .last && X.tier == .last && B.system == X.system && L.sameOrSuccessor X.court B.court then
        lastResortBench L X B b x
      else if B.court == X.court && (X.tier == .trial || X.tier == .appDivTrial) then (false, .noPower)
      else if B.court == X.court && X.tier.rank ≤ B.tier.rank then benchRule L X B b x
      else if adopt L b x B X then
        if !power then (false, .noPower)
        else if B.tier == .last then adoptedLastResortBench L B b
        else (match benchRule L B B b { x with unit := none } with
         | (ok, .strongNeedsEnBanc) => (ok, .adoptedEnBanc)
         | r => r)
      else (false, .noPower)
  | _, _ => none

example : canChangeAdopt (fun L b x B X => (adoptionsOf L x).any (·.adopter == b.court) && X.tier.rank ≤ B.tier.rank)
    true = canChangeStatus := rfl

/-- M72 `mutAdoptAnyTier`: an adopter holds what it adopted at any tier. -/
def m72 := canChangeAdopt (fun L b x _ _ => (adoptionsOf L x).any (·.adopter == b.court)) true
/-- M73 `mutNoAdoptPower`: an adoption row gives no power. -/
def m73 := canChangeAdopt (fun L b x B X => (adoptionsOf L x).any (·.adopter == b.court) && X.tier.rank ≤ B.tier.rank)
  false

/-- M74: the judge-form anchor cues without the claim. -/
def m74 := Cert.checkHistory8With (fun _ a => Cert.anchorWideCue9 a) Cert.bridgeFail

/-- Round 9 batch 2: one property per new rule; each admits the good row and rejects one bad row (`Examples`). -/
def properties9b : List (String × (Impl → Bool)) := [
  ("antecedentFar_gap: no other key", fun i =>
    i.checkTreatmentF true [6] (fIn fFill) true .plain [fL fFill] == .ok &&
      !(i.checkTreatmentF true [6] (fIn fFillKey) true .plain [fL fFillKey]).admitted),
  ("antecedentFar_gap: bound", fun i =>
    i.checkTreatmentF true [6] (fIn fFill) true .plain [fL fFill] == .ok &&
      !(i.checkTreatmentF true [6] (fIn fFillLong) true .plain [fL fFillLong]).admitted),
  ("antecedentFar_gap: anaphor", fun i =>
    i.checkTreatmentF true [6] (fIn fFill) true .plain [fL fFill] == .ok &&
      !(i.checkTreatmentF true [6] (fIn fFill jNoAna) true .plain [fL fFill jNoAna]).admitted),
  ("implicitReject_soft", fun i =>
    i.checkTreatmentI true iIn true .plain [] == .ok &&
      !(i.checkTreatmentI true { iIn with kind := .treat .overruled } true .plain []).admitted),
  ("implicitReject_no_claim", fun i =>
    i.checkTreatmentI true iIn true .plain [] == .ok && !(i.checkTreatmentI false iIn true .plain []).admitted),
  ("adopted_lowerTier_noPower", fun i =>
    -- (the adopted power is never granted below the target's tier; M15 "no power check" grants every refused power
    -- under its own rule id and is M15's, not this property's)
    i.canChange njLx appDiv1977 ea1924 none != some (true, .sameCourtSoft) &&
      (i.canChange njLx sup1954 oldSup1924 none).map (·.1) == some true),
  ("adoptedSameTier_power (New Jersey successors)", fun i =>
    (i.canChange njL appDiv1962 oldSup1948 none).map (·.1) == some true &&
      (i.canChange njL chanDiv1949 chancery1937 none).map (·.1) == some true),
  ("anchorWide9_no_claim", fun i =>
    i.checkHistory8J jgIn (some jgAnc) none { anchorWide := true } == .ok &&
      !(i.checkHistory8J jgIn (some jgAnc) none {}).admitted)
]

/-! ### Round 10 mutants (remand bridge evidence; `round10/DESIGN10.md` §4, D10-5, D10-6) -/

example : Cert.remandThenWith (Cert.remandFailWith Cert.remandCourtOk Cert.remandDateOk Cert.remandDocketOk
    Cert.remandCueOk Cert.remandTieOk) = Cert.remandThen := rfl

/-- M75: B before the order (the date test without `date(order) ≤ date(B)`). -/
def m75 := Cert.remandThenWith (Cert.remandFailWith Cert.remandCourtOk
  (fun r => Cert.validDate r.oDate && Cert.validDate r.bDate && Cert.validDate r.tDate && decide (r.tDate < r.oDate) &&
    decide (Cert.dayNum r.bDate ≤ Cert.dayNum r.oDate + Cert.remandDaysMax))
  Cert.remandDocketOk Cert.remandCueOk Cert.remandTieOk)
/-- M76: B of another court (any known court). -/
def m76 := Cert.remandThenWith (Cert.remandFailWith (fun r => r.bCourt.isSome) Cert.remandDateOk Cert.remandDocketOk
  Cert.remandCueOk Cert.remandTieOk)
/-- M77: a docket token of B only (the target's span not read). -/
def m77 := Cert.remandThenWith (Cert.remandFailWith Cert.remandCourtOk Cert.remandDateOk
  (fun c r => Cert.docketTokenOk (Cert.compact r.docket) &&
    Cert.spanHas c r.bSha r.bWindows r.bdStart r.bdStop (Cert.compact r.docket))
  Cert.remandCueOk Cert.remandTieOk)
/-- M78: no tie to the order. -/
def m78 := Cert.remandThenWith (Cert.remandFailWith Cert.remandCourtOk Cert.remandDateOk Cert.remandDocketOk
  Cert.remandCueOk (fun _ _ _ => true))
/-- M79 (D10-7): a tie string found in B only (the reason case not sought in the order's text). -/
def m79 := Cert.remandThenWith (Cert.remandFailWith Cert.remandCourtOk Cert.remandDateOk Cert.remandDocketOk
  Cert.remandCueOk (fun c r q => Cert.keyTie c r q || (Cert.dateForms r.oDate).any (Cert.hasSub q) ||
    (decide (Cert.remandTieMin ≤ (Cert.compact r.tie).length) && Cert.hasSub (Cert.compact q) (Cert.compact r.tie))))

/-- Round 10: one property per new rule; each admits the good line and rejects one bad line (`Examples`). -/
def properties10 : List (String × (Impl → Bool)) := [
  ("remandBridge_sound: B after the order", fun i =>
    i.remandThen (some rGood) bIn .ok == .ok &&
      !(i.remandThen (some { rGood with bDate := 20151201 }) bIn .ok).admitted),
  ("remandBridge_sound: same court", fun i =>
    i.remandThen (some rGood) bIn .ok == .ok &&
      !(i.remandThen (some { rGood with bCourt := some 9 }) bIn .ok).admitted),
  ("remandBridge_sound: docket in the target's text", fun i =>
    i.remandThen (some rGood) bIn .ok == .ok && !(i.remandThen (some rBOnly) bIn .ok).admitted),
  ("remandBridge_sound: tie", fun i =>
    i.remandThen (some rGood) bIn .ok == .ok && !(i.remandThen (some (rmQ rNoTie)) bIn .ok).admitted),
  ("remandBridge_sound: reason case in the order's text", fun i =>
    i.remandThen (some (rmQ rReason)) bIn .ok == .ok &&
      !(i.remandThen (some { rmQ rReason with oStart := 0, oStop := 19 }) bIn .ok).admitted)
]

/-! ### Round 10 §6 mutants (the trial-judgment bridge; `round10/DESIGN10.md` §6, D10-8) -/

example : Cert.checkHistory8TWith Cert.trialBridgeDOk
    (Cert.trialFailWith Cert.trialBridgeTOk Cert.trialBridgeDateOk) = Cert.checkHistory8T := rfl

/-- M80: T's quote may reverse (no negative test). -/
def m80 := Cert.checkHistory8TWith Cert.trialBridgeDOk (Cert.trialFailWith
  (fun c t => match Cert.tbridgeQuote c t with
    | some q => Cert.tbridgeCues.any (Cert.hasSub q)
    | none => false) Cert.trialBridgeDateOk)
/-- M81: D's line may name the intermediate court. -/
def m81 := Cert.checkHistory8TWith (fun h c => Cert.claimCueOk h c && Cert.trialCourtNames.any (Cert.hasSub (Cert.dQuote c)))
  (Cert.trialFailWith Cert.trialBridgeTOk Cert.trialBridgeDateOk)
/-- M82: T may be dated after D. -/
def m82 := Cert.checkHistory8TWith Cert.trialBridgeDOk (Cert.trialFailWith Cert.trialBridgeTOk
  (fun t => Cert.validDate t.tDate && Cert.validDate t.dDate &&
    decide (Cert.dayNum t.dDate ≤ Cert.dayNum t.tDate + Cert.tbridgeDaysMax) && t.tCourt.isSome && t.dCourt.isSome &&
    t.tCourt != t.dCourt))
/-- M83: the claim's cue test on an anchored reversed / vacated row without the claim. -/
def m83 (t? : Option Cert.TBridge) (c : Cert.Input) (a? : Option Cert.Anchor) (b? : Option Cert.Bridge)
    (h : Cert.HClaims) : Cert.Result :=
  match t?, a?, b? with
  | none, some a, none =>
    if Cert.trialKind c.kind then
      Cert.anchoredBy (Cert.anchorCueOk9 h)
        (Cert.checkByX (Cert.trialBridgeDOk h) .trialBridgeD (Cert.claimPart Cert.orderHeadOk h) (fun _ => none)) c a
    else Cert.checkHistory8J c a? b? h
  | _, _, _ => Cert.checkHistory8T t? c a? b? h

/-- Round 10 §6: one property per new rule (`Examples`). -/
def properties10b : List (String × (Impl → Bool)) := [
  ("trialBridge_sound: T affirmed", fun i =>
    i.checkHistory8T (some tbGood) (tdIn) (some tdA) none {} == .ok &&
      !(i.checkHistory8T (some tbNeg) (tdIn) (some tdA) none {}).admitted),
  ("trialBridge_sound: trial court only", fun i =>
    i.checkHistory8T (some tbGood) (tdIn) (some tdA) none {} == .ok &&
      !(i.checkHistory8T (some tbGood) (tdIn tdInter) (some tdA) none {}).admitted),
  ("trialBridge_sound: T before D", fun i =>
    i.checkHistory8T (some tbGood) (tdIn) (some tdA) none {} == .ok &&
      !(i.checkHistory8T (some { tbGood with tDate := 20130101 }) (tdIn) (some tdA) none {}).admitted),
  ("trialBridge_no_claim", fun i =>
    i.checkHistory8T none (tdIn tdCoa) (some tdA) none {} == .ok)
]

/-! ### Round 11 mutants (the claim `anchorTribunal`; `round11/DESIGN11.md` §5.1, D11-4) -/

example : Cert.checkHistory8AWith Cert.anchorCueOk11 = Cert.checkHistory8A := rfl

/-- M84: the tribunal cues without the claim. -/
def m84 := Cert.checkHistory8AWith (fun h a => Cert.anchorCueOk11 h a ||
  Cert.anchorTribunalCues.any (Cert.hasSub (Cert.norm a.quote).toLower))
/-- M85: the tribunal list dropped with the claim (the `anchorWide` lists only). -/
def m85 := Cert.checkHistory8AWith (fun h a => if h.anchorTribunal then Cert.anchorWideCue9 a else Cert.anchorCueOk9 h a)
/-- M86: no anchor-cue test under the claim. -/
def m86 := Cert.checkHistory8AWith (fun h a => if h.anchorTribunal then true else Cert.anchorCueOk9 h a)

/-- Round 11 §5.1: one property per mutant (`Examples`). -/
def properties11 : List (String × (Impl → Bool)) := [
  ("anchorTribunal_no_claim", fun i =>
    i.checkHistory8A none (trIn trDc) (some (trAnc trDc)) none {} == .ok &&
      !(i.checkHistory8A none (trIn trCit) (some (trAnc trCit)) none {}).admitted),
  ("anchorTribunal_eq", fun i =>
    i.checkHistory8A none (trIn trCit) (some (trAnc trCit)) none { anchorTribunal := true } == .ok),
  ("anchorTribunal_sound", fun i =>
    !(i.checkHistory8A none (trIn trNone) (some (trAnc trNone)) none { anchorTribunal := true }).admitted)
]

/-! ### Round 11 §5.2 mutants (identity-tie evidence; `round11/DESIGN11.md` §5.2, D11-5) -/

example : Cert.identityThenWith (Cert.identityOkWith Cert.identitySpanMax Cert.identityFormOk) = Cert.identityThen := rfl

/-- M87: a docket / cite token found in D's span only (T's span not read). -/
def m87 := Cert.identityThenWith (Cert.identityOkWith Cert.identitySpanMax (fun i d t =>
  if i.form == "docket" || i.form == "cite" then
    Cert.docketTokenOk (Cert.compact i.token) && Cert.hasSub (Cert.compact d) (Cert.compact i.token)
  else Cert.identityFormOk i d t))
/-- M88: a date token other than date(T) (the spans checked against the token's own date). -/
def m88 := Cert.identityThenWith (Cert.identityOkWith Cert.identitySpanMax (fun i d t =>
  if i.form == "date" then
    decide (i.token.length = 8) && i.token.all Char.isDigit &&
      (Cert.dateForms (i.token.toNat?.getD 0)).any (Cert.hasSub d) && (Cert.dateForms (i.token.toNat?.getD 0)).any (Cert.hasSub t)
  else Cert.identityFormOk i d t))
/-- M89: a span over 200 characters accepted. -/
def m89 := Cert.identityThenWith (Cert.identityOkWith 1000000000 Cert.identityFormOk)

/-- Round 11 §5.2: one property per mutant; each admits the good docket line and rejects one bad line (`Examples`). -/
def properties11b : List (String × (Impl → Bool)) := [
  ("identityTie_sound: token in T's span", fun i =>
    i.identityThen (some iDk) bIn .ok == .ok && !(i.identityThen (some iDOnly) bIn .ok).admitted),
  ("identityTie_sound: date of T", fun i =>
    i.identityThen (some iDk) bIn .ok == .ok &&
      !(i.identityThen (some { iDate with tDate := 20150101 }) bIn .ok).admitted),
  ("identityTie_sound: span bound", fun i =>
    i.identityThen (some iDk) bIn .ok == .ok && !(i.identityThen (some (iLong 1)) bIn .ok).admitted)
]

def mutants : List (String × Impl) := [
  ("M1 Erie both ways", { relation := m1rel }),
  ("M2 panel overrules panel", { canChange := m2can }),
  ("M3 ignore unpublished", { force := m3force }),
  ("M4 ignore partial scope", { status := m4status }),
  ("M5 supersession retroactive", { superEffect := m5super }),
  ("M6 revival ignored", { treatEffect := m6treat }),
  ("M7 cert accepts dissents", { check := m7check }),
  ("M8 cert without disqualifiers", { check := m8check }),
  ("M9 cert without quote check", { check := m9check }),
  ("M10 trial courts bind", { relation := m10rel }),
  ("M11 SCOTUS persuasive", { relation := m11rel }),
  ("M12 intermediate binds last resort", { relation := m12rel }),
  ("M13 order-dependent status", { status := m13status }),
  ("M14 soft treatments count", { treatEffect := m14treat }),
  ("M15 no power check", { canChange := m15can }),
  ("M16 resolver ignores precedence", { resolve := m16resolve }),
  ("M17 effects before their date", { status := m17status }),
  ("M18 cert off-by-one offsets", { check := m18check }),
  ("M19 cert trusts window text", { check := m19check }),
  ("M20 cert ignores citation index", { check := m20check }),
  ("M21 status global after adoption cut-off", { statusFor := m21statusFor }),
  ("M22 divisions overrule the court", { canChange := m22can }),
  ("M23 line rows report the union status", { lineStatus := m23line }),
  ("M24 splits and conflicts on the union status", { held := m24held }),
  ("M25 Horty base keeps precedents overruled in the line", { base := m25base }),
  ("M26 heir rows drop effects that reach every line", { lineStatus := m26line }),
  ("M27 witness row may be explicit or lack standing", { checkWitness := m27wit }),
  ("M28 recognition on mere standing", { checkRecognised := m28rec }),
  ("M29 recognised row negative from date(Y)", { recogEffects := m29eff }),
  ("M30 recognition with a name only in the window", { checkRecognised := m30rec }),
  ("M31 recognised row never negative", { recogEffects := m31eff }),
  ("M32 operative words keep scope all", { demote := m32demote }),
  ("M33 operative words on arguments", { checkOperative := m33op }),
  ("M34 at-risk witness row takes effect", { recogEffects := m34eff }),
  ("M35 anchor without a cue", { checkAnchored := m35anc }),
  ("M36 anchor without disqualifiers", { checkAnchored := m36anc }),
  ("M37 evidence in the anchor's window", { checkAnchored := m37anc }),
  ("M38 anchor window hash not checked", { checkAnchored := m38anc }),
  ("M39 any anchor part", { checkAnchored := m39anc }),
  ("M40 anchor from another text", { checkAnchored := m40anc }),
  ("M41 antecedent without the gap bound", { checkTreatment := m41 }),
  ("M42 antecedent without an anaphor", { checkTreatment := m42 }),
  ("M43 evidence in the main quote's window", { checkTreatment := m43 }),
  ("M44 tie without a tie cue", { checkTreatment := m44 }),
  ("M45 tie without the label in both quotes", { checkTreatment := m45 }),
  ("M46 doctrine row not demoted", { doctrineEffects := m46 }),
  ("M47 no doctrine uniqueness", { doctrineFinal := m47 }),
  ("M48 a third joined line", { checkTreatment := m48 }),
  ("M49 joined quote from another text", { checkTreatment := m49 }),
  ("M50 orderHead without the court test", { checkHistory7 := m50 }),
  ("M51 orderHead without the date test", { checkHistory7 := m51 }),
  ("M52 orderHead without the order-line cue", { checkHistory7 := m52 }),
  ("M53 setAside on any kind", { checkHistory7 := m53 }),
  ("M54 bridge without the length bound", { checkHistory8 := m54 }),
  ("M55 bridge without the ; test", { checkHistory8 := m55 }),
  ("M56 O's citation before X's", { checkHistory8 := m56 }),
  ("M57 bridge without the cue", { checkHistory8 := m57 }),
  ("M58 a citation of another node", { checkHistory8 := m58 }),
  ("M59 bridge without the date test", { checkHistory8 := m59 }),
  ("M60 wide anchor cues without the claim", { checkHistory8 := m60 }),
  ("M61 bridge without the chain test", { checkHistory8 := m61 }),
  ("M62 old circuit without the date test", { histPower := m62 }),
  ("M63 old circuit on a treatments row", { canChange := m63 }),
  ("M64 zone straddles a boundary", { partZone := m64 }),
  ("M65 zone of another part", { partZone := m65 }),
  ("M66 zones of an overlapping node kept", { partZone := m66 }),
  ("M67 far antecedent past another citation", { checkTreatmentF := m67 }),
  ("M68 far antecedent at any distance", { checkTreatmentF := m68 }),
  ("M69 far antecedent without an anaphor", { checkTreatmentF := m69 }),
  ("M70 implicitReject on an overruled row", { checkTreatmentI := m70 }),
  ("M71 implicit cues without the claim", { checkTreatmentI := m71 }),
  ("M72 adoption at any tier (mutAdoptAnyTier)", { canChange := m72 }),
  ("M73 adoption gives no power (mutNoAdoptPower)", { canChange := m73 }),
  ("M74 judge-form anchor cues without the claim", { checkHistory8J := m74 }),
  ("M75 remand decision before the order", { remandThen := m75 }),
  ("M76 remand decision of another court", { remandThen := m76 }),
  ("M77 a docket token of B only", { remandThen := m77 }),
  ("M78 remand without a tie to the order", { remandThen := m78 }),
  ("M79 a reason-case tie found in B only", { remandThen := m79 }),
  ("M80 trial bridge: T's quote reverses", { checkHistory8T := m80 }),
  ("M81 trial bridge: D names the intermediate court", { checkHistory8T := m81 }),
  ("M82 trial bridge: T dated after D", { checkHistory8T := m82 }),
  ("M83 trial-bridge cue test without the claim", { checkHistory8T := m83 }),
  ("M84 tribunal anchor cues without the claim", { checkHistory8A := m84 }),
  ("M85 tribunal anchor cues dropped with the claim", { checkHistory8A := m85 }),
  ("M86 no anchor-cue test under the tribunal claim", { checkHistory8A := m86 }),
  ("M87 identity token in D's span only", { identityThen := m87 }),
  ("M88 identity date token other than date(T)", { identityThen := m88 }),
  ("M89 identity span over 200 characters", { identityThen := m89 })
]

/-! ## The kill matrix -/

def killers (p : Impl → Bool) : List String := (mutants.filter fun (_, m) => !p m).map (·.1)

def allProperties : List (String × (Impl → Bool)) :=
  properties ++ properties5 ++ properties6 ++ properties7 ++ properties8 ++ properties9 ++ properties9b ++ properties10 ++
    properties10b ++ properties11 ++ properties11b

def killMatrix : List (String × List String) := allProperties.map fun (n, p) => (n, killers p)

#eval killMatrix
-- every property holds of the specification
#guard allProperties.all fun (_, p) => p spec
-- every property is falsified by at least one mutant
#guard allProperties.all fun (_, p) => !(killers p).isEmpty
-- every mutant is caught by at least one property
#guard mutants.all fun (_, m) => allProperties.any fun (_, p) => !p m
-- round 5: each new mutant is caught by a round-5 property, and no round-5 mutant breaks a round-4 property's
-- verdict on the specification's own behaviour (the old matrix is unchanged)
#guard ((mutants.drop 27).take 7).all fun (_, m) => properties5.any fun (_, p) => !p m
-- round 6: the six anchor mutants and the six anchor properties form a diagonal (mutant i is caught by property i
-- and by no other); no anchor mutant is caught by an earlier property and no earlier mutant by an anchor property,
-- so the round-5 matrix is unchanged
#guard (List.range 6).all fun i => (List.range 6).all fun j =>
  match (mutants.drop 34)[i]?, properties6[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j)
  | _, _ => false
#guard ((mutants.drop 34).take 6).all fun (_, m) => (properties ++ properties5).all fun (_, p) => p m
#guard (mutants.take 34).all fun (_, m) => properties6.all fun (_, p) => p m
-- round 7: the thirteen new mutants and the thirteen new properties form a diagonal; no new mutant is caught by an
-- earlier property and no earlier mutant by a new property, so the earlier matrix is unchanged
#guard (List.range 13).all fun i => (List.range 13).all fun j =>
  match (mutants.drop 40)[i]?, properties7[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j)
  | _, _ => false
#guard (mutants.drop 40).all fun (_, m) => (properties ++ properties5 ++ properties6).all fun (_, p) => p m
#guard (mutants.take 40).all fun (_, m) => properties7.all fun (_, p) => p m
-- round 8: the ten new mutants and the ten new properties form a diagonal; no new mutant is caught by an earlier
-- property and no earlier mutant by a new property, so the earlier matrix is unchanged
#guard (List.range 10).all fun i => (List.range 10).all fun j =>
  match (mutants.drop 53)[i]?, properties8[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j)
  | _, _ => false
#guard (mutants.drop 53).all fun (_, m) =>
  (properties ++ properties5 ++ properties6 ++ properties7).all fun (_, p) => p m
#guard (mutants.take 53).all fun (_, m) => properties8.all fun (_, p) => p m
-- round 9: the three zone mutants and the three zone properties form a diagonal; no new mutant is caught by an
-- earlier property and no earlier mutant by a new property, so the earlier matrix is unchanged
#guard (List.range 3).all fun i => (List.range 3).all fun j =>
  match (mutants.drop 63)[i]?, properties9[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j)
  | _, _ => false
#guard (mutants.drop 63).all fun (_, m) =>
  (properties ++ properties5 ++ properties6 ++ properties7 ++ properties8).all fun (_, p) => p m
#guard (mutants.take 63).all fun (_, m) => properties9.all fun (_, p) => p m
-- round 9 batch 2: the eight new mutants and the eight new properties form a diagonal; no new mutant is caught by an
-- earlier property and no earlier mutant by a new property
#guard (List.range 8).all fun i => (List.range 8).all fun j =>
  match (mutants.drop 66)[i]?, properties9b[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j)
  | _, _ => false
#guard (mutants.drop 66).all fun (_, m) =>
  (properties ++ properties5 ++ properties6 ++ properties7 ++ properties8 ++ properties9).all fun (_, p) => p m
#guard (mutants.take 66).all fun (_, m) => properties9b.all fun (_, p) => p m
-- round 10: the five remand mutants and the five remand properties form a diagonal, except that M78 (no tie at all)
-- is also caught by the reason-case property (every tie mutant is weaker than "no tie"); no new mutant is caught by
-- an earlier property and no earlier mutant by a new property
#guard (List.range 5).all fun i => (List.range 5).all fun j =>
  match (mutants.drop 74)[i]?, properties10[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j || (i == 3 && j == 4))
  | _, _ => false
#guard (mutants.drop 74).all fun (_, m) =>
  (properties ++ properties5 ++ properties6 ++ properties7 ++ properties8 ++ properties9 ++ properties9b).all
    fun (_, p) => p m
#guard (mutants.take 74).all fun (_, m) => properties10.all fun (_, p) => p m
-- round 10 §6: the four trial-bridge mutants and the four trial-bridge properties form a diagonal; no new mutant is
-- caught by an earlier property and no earlier mutant by a new property
#guard (List.range 4).all fun i => (List.range 4).all fun j =>
  match (mutants.drop 79)[i]?, properties10b[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j)
  | _, _ => false
#guard (mutants.drop 79).all fun (_, m) =>
  (properties ++ properties5 ++ properties6 ++ properties7 ++ properties8 ++ properties9 ++ properties9b ++
    properties10).all fun (_, p) => p m
#guard (mutants.take 79).all fun (_, m) => properties10b.all fun (_, p) => p m
-- round 11 §5.1: the three tribunal mutants and the three tribunal properties form a diagonal; no new mutant is caught
-- by an earlier property and no earlier mutant by a new property
#guard (List.range 3).all fun i => (List.range 3).all fun j =>
  match (mutants.drop 83)[i]?, properties11[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j)
  | _, _ => false
#guard (mutants.drop 83).all fun (_, m) =>
  (properties ++ properties5 ++ properties6 ++ properties7 ++ properties8 ++ properties9 ++ properties9b ++
    properties10 ++ properties10b).all fun (_, p) => p m
#guard (mutants.take 83).all fun (_, m) => properties11.all fun (_, p) => p m
-- round 11 §5.2: the three identity mutants and the three identity properties form a diagonal; no new mutant is caught
-- by an earlier property and no earlier mutant by a new property
#guard (List.range 3).all fun i => (List.range 3).all fun j =>
  match (mutants.drop 86)[i]?, properties11b[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j)
  | _, _ => false
#guard (mutants.drop 86).all fun (_, m) =>
  (properties ++ properties5 ++ properties6 ++ properties7 ++ properties8 ++ properties9 ++ properties9b ++
    properties10 ++ properties10b ++ properties11).all fun (_, p) => p m
#guard (mutants.take 86).all fun (_, m) => properties11b.all fun (_, p) => p m
#guard (properties.length, properties5.length, properties6.length, properties7.length, properties8.length,
  properties9.length, properties9b.length, properties10.length, properties10b.length, properties11.length,
  properties11b.length, mutants.length) == (27, 8, 6, 13, 10, 3, 8, 5, 4, 3, 3, 89)

end CaseLaw2.Mutants
