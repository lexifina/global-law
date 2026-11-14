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
  ("M53 setAside on any kind", { checkHistory7 := m53 })
]

/-! ## The kill matrix -/

def killers (p : Impl → Bool) : List String := (mutants.filter fun (_, m) => !p m).map (·.1)

def allProperties : List (String × (Impl → Bool)) := properties ++ properties5 ++ properties6 ++ properties7

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
#guard (properties.length, properties5.length, properties6.length, properties7.length, mutants.length) ==
  (27, 8, 6, 13, 53)

end CaseLaw2.Mutants
