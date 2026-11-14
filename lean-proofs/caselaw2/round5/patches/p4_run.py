"""Round 5 patch 4: Data.lean (treatment_class.tsv) and Run.lean (recognised / operative wiring, classes, oclass)."""
import os
LP = r"~\Documents\global-law-lean\lean-proofs\LegalProofs\CaseLaw2"


def rw(p, pairs):
    p = os.path.join(LP, p)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70], s.count(a))
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="\n").write(s)


rw("Data.lean", [
("""structure CertTextRow where""",
"""/-- `treatment_class.tsv` (round 5, DESIGN5 §1): the treatments row `id` claims a class (`recognised` on a witness
row, `operativeWords` on an explicit row); `fieldLimit` and `doctrine` are display text. The file's presence turns
round-5 output on. -/
structure ClassRow where
  id : String
  claim : String
  fieldLimit : String
  doctrine : String
  src : String
  deriving Repr, Inhabited

def ClassRow.parse (f : Array String) : Option ClassRow :=
  some { id := f[0]!, claim := f[1]!, fieldLimit := f[2]!, doctrine := f[3]!, src := f[4]! }

structure CertTextRow where"""),
("""  witness : Array WitnessRow := #[]
  certText : Array CertTextRow := #[]""",
"""  witness : Array WitnessRow := #[]
  /-- round 5: class claims; `round5` = the file exists (round-5 output mode) -/
  classes : Array ClassRow := #[]
  round5 : Bool := false
  certText : Array CertTextRow := #[]"""),
("""  -- the holdings agent ships its windows separately (D4, 2026-11-12); a missing file loads as empty""",
"""  -- optional (round 5): class claims; absent = round-4 output, byte for byte
  let clsFile := dir / "treatment_class.tsv"
  let mut classes : Array ClassRow := #[]
  let round5 ← clsFile.pathExists
  if round5 then
    let (cs, p) ← loadRows clsFile 5 ClassRow.parse
    classes := cs
    ps := ps.push p
  -- the holdings agent ships its windows separately (D4, 2026-11-12); a missing file loads as empty"""),
("""  return { courts, succession, adoption, rules, history, treatments, witness, certText, issues, holdings, marks, lawchanges,
           supersessions, problems := ps }""",
"""  return { courts, succession, adoption, rules, history, treatments, witness, classes, round5, certText, issues, holdings,
           marks, lawchanges, supersessions, problems := ps }"""),
])

rw("Run.lean", [
# --- class table, per-row class
("""  let textNode (r : Data.TreatmentRow) : Nat := match witOf.get? r.id with | some wr => wr.node | none => r.by_
  let mut treatA : Array TEvent := #[]""",
"""  let textNode (r : Data.TreatmentRow) : Nat := match witOf.get? r.id with | some wr => wr.node | none => r.by_
  -- round 5 (DESIGN5 §1): class claims. The file's presence turns round-5 output on (`r5`); a claim with an unknown
  -- word or an id that is no treatments row is ignored and counted; the first line for an id wins
  let r5 := tables.round5
  let treatIdSet : HashMap String Unit := tables.treatments.foldl (fun m r => m.insert r.id ()) {}
  let mut clsOf : HashMap String Data.ClassRow := {}
  let mut nClsBad := (tables.problems.filter (·.file.endsWith "treatment_class.tsv")).foldl (fun n p => n + p.bad) 0
  for c in tables.classes do
    if (c.claim == "recognised" || c.claim == "operativeWords") && treatIdSet.contains c.id then
      if !clsOf.contains c.id then clsOf := clsOf.insert c.id c else nClsBad := nClsBad + 1
    else nClsBad := nClsBad + 1
  -- the class of each treatments row (index = row number; `none`: not a status-changing kind, or a bad row), and
  -- the rows recognised under the full rule set
  let mut rowCls : Array (Option Cert.OClass) := #[none]
  let mut recRows : HashMap Nat Unit := {}
  let mut classLines : Array String := #[]
  let mut nRecog := 0
  let mut nOper := 0
  let mut treatA : Array TEvent := #[]"""),
("""      let wit (L : Lookups) (wr : WitnessRow) : Cert.Witness :=
        let wd? := decF wr.node
        { known := wd?.isSome, explicit := r.explicit, changes := kind.changesStatus, byEvidence := wr.byEvidence,
          by_ := r.by_,
          witnessOrdered := match wd? with
            | some wd => b.date == 0 || wd.date == 0 || decide (b.date ≤ wd.date)
            | none => false,
          standing := match wd? with
            | some wd => wd.court == x.court || powerAnyDomain L wd x == some true
            | none => false }
      let res (L : Lookups) : String × Bool :=
        let auth := if kind.changesStatus then powerOn L dom else some true
        match witOf.get? r.id with
        | some wr => let v := Cert.checkWitness (inp auth) (wit L wr); (v.toString, v.admitted)
        | none => let v := Cert.check (inp auth); (v.toString, v.admitted)
      let ra := res LA
      let rf := res LF
      let textOk := match witOf.get? r.id with
        | some wr => (Cert.checkWitness (inp (some true)) (wit LA wr)).admitted
        | none => (Cert.check (inp (some true))).admitted
      let ev : TEvent := { id := ri, by_ := r.by_, target := r.target, date := b.date, kind, scope := sc,
                           temporal := tm, explicit := r.explicit }""",
"""      -- round 5: the row's claim. `recognised` counts only on a witness row, `operativeWords` only on another row
      let claim := (clsOf.get? r.id).map (·.claim)
      let claimR := claim == some "recognised" && witOf.contains r.id
      let claimO := claim == some "operativeWords" && !witOf.contains r.id
      let wit (L : Lookups) (wr : WitnessRow) : Cert.Witness :=
        let wd? := decF wr.node
        { known := wd?.isSome, explicit := r.explicit, changes := kind.changesStatus, byEvidence := wr.byEvidence,
          by_ := r.by_,
          witnessOrdered := match wd? with
            | some wd => b.date == 0 || wd.date == 0 || decide (b.date ≤ wd.date)
            | none => false,
          standing := match wd? with
            | some wd => wd.court == x.court || powerAnyDomain L wd x == some true
            | none => false,
          -- round 5: the claim, W's power over X (not mere standing), and the three dates known
          claim := claimR,
          power := match wd? with
            | some wd => powerAnyDomain L wd x == some true
            | none => false,
          datesKnown := match wd? with
            | some wd => x.date != 0 && b.date != 0 && wd.date != 0
            | none => false }
      -- without a claim `checkRecognised` is `checkWitness` (`Cert.checkRecognised_no_claim`)
      let res (L : Lookups) : String × Bool :=
        let auth := if kind.changesStatus then powerOn L dom else some true
        match witOf.get? r.id with
        | some wr => let v := Cert.checkRecognised (inp auth) (wit L wr); (v.toString, v.admitted)
        | none =>
          let v := if claimO then Cert.checkOperative (inp auth) r.explicit else Cert.check (inp auth)
          (v.toString, v.admitted)
      let ra := res LA
      let rf := res LF
      let textOk := match witOf.get? r.id with
        | some wr => (Cert.checkRecognised (inp (some true)) (wit LA wr)).admitted
        | none => if claimO then (Cert.checkOperative (inp (some true)) r.explicit).admitted
                  else (Cert.check (inp (some true))).admitted
      -- recognised under a rule set: the text, the dates, W's standing and W's power (Y's power is decided per issue
      -- below, as for an explicit row)
      let recOk (L : Lookups) : Option Recog :=
        match witOf.get? r.id, (witOf.get? r.id).bind (fun wr => decF wr.node) with
        | some wr, some wd =>
          if (Cert.checkRecognised (inp (some true)) (wit L wr)).isRecognised then
            some { witness := wd.id, date := wd.date, power := true }
          else none
        | _, _ => none
      let ev : TEvent := { id := ri, by_ := r.by_, target := r.target, date := b.date, kind, scope := sc,
                           temporal := tm, explicit := r.explicit }
      -- an operative-words row that does not dispose of the case as a whole: every event's scope is demoted
      let demoteO := claimO && !Cert.wholeCase r.cert.quote"""),
("""      let events (L : Lookups) : List TEvent :=
        if !textOk then []
        else if !kind.changesStatus then [ev]
        else""",
"""      let events (L : Lookups) : List TEvent :=
        let ev := { ev with recog := recOk L }
        (fun (es : List TEvent) => if demoteO then es.map (fun e => { e with scope := demote e.scope }) else es) <|
        if !textOk then []
        else if !kind.changesStatus then [ev]
        else"""),
("""      if textOk then treatInfo := treatInfo.push (r, kind, sc, ri)
      if ri % nShards == k then certLines := certLines.push s!"treatment\\t{r.id}\\t{ra.1}\\t{rf.1}"
    | _, _, _, _ =>
      nRej := nRej + 1
      if ri % nShards == k then certLines := certLines.push s!"treatment\\t{r.id}\\tbadRow\\tbadRow\"""",
"""      if textOk then treatInfo := treatInfo.push (r, kind, sc, ri)
      if ri % nShards == k then certLines := certLines.push s!"treatment\\t{r.id}\\t{ra.1}\\t{rf.1}"
      -- round 5: the row's class (DESIGN5 §5)
      let isRec := (recOk LA).isSome
      let cls := if kind.changesStatus then some (Cert.classOf r.explicit isRec r.cert.quote) else none
      rowCls := rowCls.push cls
      if isRec then
        recRows := recRows.insert ri ()
        nRecog := nRecog + 1
      if claimO && ra.2 then nOper := nOper + 1
      if r5 && ri % nShards == k then
        if let some c := cls then
          let cr := clsOf.get? r.id
          let dash (s : String) := if s.isEmpty then "-" else s
          classLines := classLines.push (s!"{r.id}\\t{c.toString}\\t{optS claim}\\t{ra.1}\\t" ++
            s!"{dash ((cr.map (·.fieldLimit)).getD "-")}\\t{dash ((cr.map (·.doctrine)).getD "-")}\\t" ++
            s!"{optS ((witOf.get? r.id).map (·.node))}")
    | _, _, _, _ =>
      nRej := nRej + 1
      rowCls := rowCls.push none
      if ri % nShards == k then certLines := certLines.push s!"treatment\\t{r.id}\\tbadRow\\tbadRow\""""),
# --- status rows: oclass
("""  let slh ← IO.FS.Handle.mk (out / s!"status_lines-{pad2 k}.tsv") .write""",
"""  -- round 5 (DESIGN5 §5.1): `oclass`, the least class among the treatment effects that make a status
  let effClass (e : Effect) : Option Cert.OClass :=
    match e.rule with
    | .recognised => some .recognised
    | .treatment | .prospective => (rowCls.getD e.src none)
    | _ => none
  let oclassOf (effs : List Effect) (iss : Nat) (t u : Date) : String :=
    let s := status effs iss t u
    if s == .good then "-"
    else
      let cs := effs.filterMap fun e => if e.contrib iss t u == s then effClass e else none
      match cs.foldl (fun (m : Option Cert.OClass) c => match m with
          | none => some c
          | some m => some (if c.idx < m.idx then c else m)) none with
      | some c => c.toString
      | none => "-"
  let slh ← IO.FS.Handle.mk (out / s!"status_lines-{pad2 k}.tsv") .write"""),
("""          let row := s!"{n}\\t{key}\\t{hk}\\t{d}\\t{next}\\t{Status.toString sA}\\t{Status.cls sA}\\t{boolS (if h.issue == 0 then sameVerdict sA sF else sameVerdict (unknownAsOne sA) (unknownAsOne sF))}\\t{optS (wit.map rowId)}\\t{optS (wit.bind (·.actor))}\\t{path}\"""",
"""          let row := s!"{n}\\t{key}\\t{hk}\\t{d}\\t{next}\\t{Status.toString sA}\\t{Status.cls sA}\\t{boolS (if h.issue == 0 then sameVerdict sA sF else sameVerdict (unknownAsOne sA) (unknownAsOne sF))}\\t{optS (wit.map rowId)}\\t{optS (wit.bind (·.actor))}\\t{path}" ++
            (if r5 then "\\t" ++ oclassOf ea h.issue d d else "")"""),
# --- findings: emit with oclass
("""  let emit (kind : String) (i j : Nat) (issue detail : String) (firm : Bool) (path : String) : IO Unit :=
    fh.putStrLn s!"{kind}\\t{i}\\t{j}\\t{issue}\\t{detail}\\t{boolS firm}\\t{path}\"""",
"""  let emit (kind : String) (i j : Nat) (issue detail : String) (firm : Bool) (path : String)
      (oc : String := "-") : IO Unit :=
    fh.putStrLn (s!"{kind}\\t{i}\\t{j}\\t{issue}\\t{detail}\\t{boolS firm}\\t{path}" ++ (if r5 then "\\t" ++ oc else ""))
  let rowOc (rj : Nat) : String := match rowCls.getD rj none with | some c => c.toString | none => "-\""""),
("""        emit "panelDepartsWithoutEnBanc" b.id x.id "-" ((reprStr kind).replace "CaseLaw2.TKind." "")
          (panelDepartsWithoutEnBanc ff && ff.status == .good) path""",
"""        emit "panelDepartsWithoutEnBanc" b.id x.id "-" ((reprStr kind).replace "CaseLaw2.TKind." "")
          (panelDepartsWithoutEnBanc ff && ff.status == .good) path (rowOc rj)"""),
("""        emit "ignoresBindingInUnit" b.id x.id "-" ((reprStr kind).replace "CaseLaw2.TKind." "") (ibu LF EF ff) path""",
"""        emit "ignoresBindingInUnit" b.id x.id "-" ((reprStr kind).replace "CaseLaw2.TKind." "") (ibu LF EF ff) path
          (rowOc rj)"""),
("""        emit "atRisk" b.id x.id "-" ("claim:" ++ kname) (claimRisk (tr LF ff.status)) path; nFind := nFind + 1""",
"""        emit "atRisk" b.id x.id "-" ("claim:" ++ kname) (claimRisk (tr LF ff.status)) path (rowOc rj)
        nFind := nFind + 1"""),
("""      if !r.explicit && kind.changesStatus && powerAnyDomain LA b x != some false && !isNeg fa.status then
        emit "atRisk" x.id b.id "-" "inferredRejection" (powerAnyDomain LF b x != some false && !isNeg ff.status) path""",
"""      -- round 5: a recognised row's status rows carry it; it makes no `inferredRejection`
      if !r.explicit && kind.changesStatus && powerAnyDomain LA b x != some false && !isNeg fa.status &&
          !recRows.contains rj then
        emit "atRisk" x.id b.id "-" "inferredRejection" (powerAnyDomain LF b x != some false && !isNeg ff.status) path
          (rowOc rj)"""),
("""              let rowsOf (L : Lookups) (E : EventLookups) (ej0 : List Effect) : List (String × String × String) :=""",
"""              let rowsOf (L : Lookups) (E : EventLookups) (ej0 : List Effect) :
                  List (String × String × String × String) :="""),
("""                  let mut out : List (String × String × String) := []
                  if !selfCaused 0 then
                    for (name, pr) in [("citesOverruled", citesOverruled), ("citesVacated", citesVacated),
                        ("citesWithdrawn", citesWithdrawn), ("citesNotCitable", citesNotCitable),
                        ("appliesSupersededHolding", appliesSupersededHolding)] do
                      if pr f then out := out ++ [(name, "-", Status.toString f.status)]""",
"""                  let mut out : List (String × String × String × String) := []
                  if !selfCaused 0 then
                    for (name, pr) in [("citesOverruled", citesOverruled), ("citesVacated", citesVacated),
                        ("citesWithdrawn", citesWithdrawn), ("citesNotCitable", citesNotCitable),
                        ("appliesSupersededHolding", appliesSupersededHolding)] do
                      if pr f then out := out ++ [(name, "-", Status.toString f.status, oclassOf ej 0 ci.date ci.date)]
                    -- round 5 (DESIGN5 §2.5): between an unannounced overruling and its recognition
                    if citedRecognisedLater f then out := out ++ [("atRisk", "-", "recognisedLater", "recognised")]"""),
("""                        if pr fh then out := out ++ [(name, is.keys[hd.issue]!, Status.toString fh.status)]
                    if supersededConductUnknown fh then
                      out := out ++ [("atRisk", is.keys[hd.issue]!, "supersededConductUnknown:" ++ is.keys[hd.issue]!)]""",
"""                        if pr fh then out := out ++ [(name, is.keys[hd.issue]!, Status.toString fh.status,
                          oclassOf ej hd.issue ci.date ci.date)]
                    if supersededConductUnknown fh then
                      out := out ++ [("atRisk", is.keys[hd.issue]!, "supersededConductUnknown:" ++ is.keys[hd.issue]!, "-")]"""),
("""              for (name, iss, st) in rA do
                emit name i j iss st (rF.any fun (n', _, s') => n' == name && s' == st) path""",
"""              for (name, iss, st, oc) in rA do
                emit name i j iss st (rF.any fun (n', _, s', _) => n' == name && s' == st) path oc"""),
("""                emit "atRisk" i j "-" ("citesLaterNegated:" ++ Status.toString now)
                  ((lateNeg LF EF (effF.getD j [])).isSome) "-\"""",
"""                emit "atRisk" i j "-" ("citesLaterNegated:" ++ Status.toString now)
                  ((lateNeg LF EF (effF.getD j [])).isSome) "-"
                  (oclassOf (effectsFor LA ci (effA.getD j [])) 0 asOf asOf)"""),
# --- summary + classes file
("""    s!"load_ms\\t{t1 - t0}", s!"run_ms\\t{t2 - t1}"] ++ problems.toList.map (fun p => s!"bad_rows\\t{p.file}\\t{p.bad}")""",
"""    s!"load_ms\\t{t1 - t0}", s!"run_ms\\t{t2 - t1}"] ++ problems.toList.map (fun p => s!"bad_rows\\t{p.file}\\t{p.bad}") ++
    (if r5 then [s!"class_rows\\t{clsOf.size}", s!"class_bad_rows\\t{nClsBad}", s!"recognised_rows\\t{nRecog}",
      s!"operative_rows\\t{nOper}"] else [])
  -- round 5: the class of every status-changing treatments row
  if r5 then
    IO.FS.writeFile (out / s!"classes-{pad2 k}.tsv")
      ("\\n".intercalate classLines.toList ++ (if classLines.isEmpty then "" else "\\n"))"""),
])
print("patched")
