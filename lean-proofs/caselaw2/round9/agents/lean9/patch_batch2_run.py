"""lean9, round 9 batch 2: the runner (Run.lean) for the joinedFar (DESIGN9 section 5) and implicitReject (section 7)
claims. Run once (refuses to run twice)."""
import os
import sys

p = os.path.join(sys.argv[1], "LegalProofs", "CaseLaw2", "Run.lean")
s = open(p, encoding="utf-8", newline="").read()
assert "claimF" not in s


def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)


rep('''    -- round 7: `doctrine` is a claim (DESIGN7 §2.4)
    if (c.claim == "recognised" || c.claim == "operativeWords" || c.claim == "doctrine") && treatIdSet.contains c.id then''',
    '''    -- round 7: `doctrine` is a claim (DESIGN7 §2.4); round 9: `joinedFar` (DESIGN9 §5), `implicitReject` (§7)
    if (c.claim == "recognised" || c.claim == "operativeWords" || c.claim == "doctrine" || c.claim == "joinedFar" ||
        c.claim == "implicitReject") && treatIdSet.contains c.id then''')
rep('''  let ambLabels := doctrineAmbiguousLabels dRows
''', '''  let ambLabels := doctrineAmbiguousLabels dRows
  -- round 9 (DESIGN9 §5): the key lengths of the index for the far-antecedent key test (only when a row claims
  -- `joinedFar`; without the claim the step is round 7's, `Cert.joinedFar_no_claim`)
  let lensF : List Nat := if !(clsOf.fold (fun b _ c => b || c.claim == "joinedFar") false) then [] else
    match cx.citeIndex with
    | some m => keyLengths m
    | none => []
''')
rep('''      let claimD := claim == some "doctrine"
''', '''      let claimD := claim == some "doctrine"
      -- round 9: the far-antecedent (§5) and implicit-rejection (§7) claims (without them: round 8's step,
      -- `Cert.joinedFar_no_claim`, `Cert.implicitReject_no_claim`)
      let claimF := claim == some "joinedFar"
      let claimI := claim == some "implicitReject"
''')
rep('''          let v := Cert.zoneThen zs (inp auth) js (fin (Cert.checkTreatment (inp auth) r.explicit .doctrine js))
          (v.toString, v.admitted)
        else match witOf.get? r.id with
        | some wr => let v := Cert.checkRecognised9 zs (inp auth) (wit L wr); (v.toString, v.admitted)
        | none =>
          let v := Cert.checkTreatment9 zs (inp auth) r.explicit tcl js
          (v.toString, v.admitted)''', '''          let v := Cert.zoneThen zs (inp auth) js (fin (Cert.checkTreatment (inp auth) r.explicit .doctrine js))
          (v.toString, v.admitted)
        else if claimI then
          let v := Cert.zoneThen zs (inp auth) js (Cert.checkTreatmentI true (inp auth) r.explicit tcl js)
          (v.toString, v.admitted)
        else match witOf.get? r.id with
        | some wr => let v := Cert.checkRecognised9 zs (inp auth) (wit L wr); (v.toString, v.admitted)
        | none =>
          let v := Cert.zoneThen zs (inp auth) js (Cert.checkTreatmentF claimF lensF (inp auth) r.explicit tcl js)
          (v.toString, v.admitted)''')
rep('''        else match witOf.get? r.id with
        | some wr => (Cert.checkRecognised9 zs (inp (some true)) (wit LA wr)).admitted
        | none => (Cert.checkTreatment9 zs (inp (some true)) r.explicit tcl js).admitted''', '''        else if claimI then
          (Cert.zoneThen zs (inp (some true)) js (Cert.checkTreatmentI true (inp (some true)) r.explicit tcl js)).admitted
        else match witOf.get? r.id with
        | some wr => (Cert.checkRecognised9 zs (inp (some true)) (wit LA wr)).admitted
        | none =>
          (Cert.zoneThen zs (inp (some true)) js (Cert.checkTreatmentF claimF lensF (inp (some true)) r.explicit tcl js)).admitted''')
open(p, "w", encoding="utf-8", newline="").write(s)
print("Run.lean patched")
