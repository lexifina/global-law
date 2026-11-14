import sys
p = 'LegalProofs/USTax/Hunt/Entity.lean'
t = open(p, encoding='utf-8').read()


def rep(a, b, cnt=1):
    global t
    assert t.count(a) == cnt, (a, t.count(a))
    t = t.replace(a, b)


rep("  rent : Nat        -- fair rent", "  daycare : Nat     -- licensed child-care centre fees for the child, paid in every case\n  rent : Nat        -- fair rent")
rep("  trump : Bool\n  cE : Nat ", "  trump : Bool\n  care : Bool\n  cE : Nat ")
rep("  | trumpAcct               --", "  | childCare               -- business contracts with a licensed centre for its employee's child: §45F(c)(1)(A)(iii)\n  | trumpAcct               --")
rep("  !s.sPS && !s.trump", "  !s.sPS && !s.trump && !s.care")
rep("""  let spF := fica s.spW
""", """  -- §45F(a)(1), (c)(4): 50% credit for an eligible small business on amounts paid under a contract with a qualified
  -- child care facility "to provide child care services to employees of the taxpayer". The value is wages of the
  -- employee: §129 cannot exclude it (§129(d)(4)). §45F(f)(2): no deduction for the amount of the credit.
  let D := if s.care then sc.daycare else 0
  let corpOwnerEmp := (s.ent == .s || s.ent == .c) && s.sal > 0
  let dOwner := if corpOwnerEmp then D else 0     -- wages of the owner-employee
  let dSpouse := D - dOwner                        -- otherwise wages of the spouse-employee
  if s.care && (if corpOwnerEmp then s.sal + D > sc.rcHi else s.spW == 0 || s.spW + D > sc.spouseWork) then none else
  let cr := min (D / 2) 600000
  let spF := fica (s.spW + dSpouse)
""")
rep("  let common := s.spW + spF + s.chW + chF + sPSA", "  let common := s.spW + spF + s.chW + chF + sPSA + (D - cr)")
rep("  let fin (corpTax payroll : Nat) (ordAGI qbi w2 qdiv nii newCE newDefer : Nat) (qOK : Bool) : Option St :=",
    "  let fin (corpTax payroll : Nat) (ordAGI qbi w2 qdiv nii newCE newDefer : Nat) (qOK : Bool) (credit : Nat) : Option St :=")
rep("    let it := ordTax ordTI + capTax ordTI cg\n", "    let it0 := ordTax ordTI + capTax ordTI cg\n    let it := it0 - min credit (it0 - pct (it0 - 25000) 25 100)   -- §38(c)(1); unused credit is ignored\n")
rep("      cE := newCE, qOK := qOK,", "      care := false, cE := newCE, qOK := qOK,")
rep("    let addl := pct (s.spW + nese - addlMedThr) 9 1000             -- §1401(b)(2), §3101(b)(2)", "    let addl := pct (s.spW + dSpouse + nese - addlMedThr) 9 1000   -- §1401(b)(2), §3101(b)(2)")
rep("    let ordAGI := gp + share + (s.spW - sDefA) - ownDed", "    let ordAGI := gp + share + (s.spW + dSpouse - sDefA) - ownDed")
rep("ordAGI qbi (s.spW + s.chW) 0 0 s.cE\n      (oPSA + oDefA + sPSA + sDefA + trSp + trCh) s.qOK", "ordAGI qbi (s.spW + dSpouse + s.chW) 0 0 s.cE\n      (oPSA + oDefA + sPSA + sDefA + trSp + trCh) s.qOK cr")
rep("    let salF := fica s.sal\n", "    let salF := fica (s.sal + dOwner)\n")
rep("    let addl := pct (s.sal + s.spW - addlMedThr) 9 1000", "    let addl := pct (s.sal + s.spW + D - addlMedThr) 9 1000")
rep("      let ordAGI := (s.sal - oDefA) + hInc + inc + (s.spW - sDefA)   -- §1366(a); no §1401 tax on the share",
    "      let ordAGI := (s.sal - oDefA) + D + hInc + inc + (s.spW - sDefA)   -- §1366(a); no §1401 tax on the share")
rep("      fin 0 payroll ordAGI inc (s.sal + s.spW + s.chW) div div (s.cE - div) newDefer false",
    "      fin 0 payroll ordAGI inc (s.sal + s.spW + s.chW + D) div div (s.cE - div) newDefer false cr   -- credit: §1366(a)(1)(A)")
rep("      let ctax := pct inc 21 100                                    -- §11(b)",
    "      let ctax0 := pct inc 21 100                                   -- §11(b)\n      let ctax := ctax0 - min cr (ctax0 - pct (ctax0 - 25000) 25 100) -- §38(c)(1)")
rep("      let ordAGI := (s.sal - oDefA) + (s.spW - sDefA)               -- health: §106(a); rent: §280A(g)(2)",
    "      let ordAGI := (s.sal - oDefA) + D + (s.spW - sDefA)           -- health: §106(a); rent: §280A(g)(2)")
rep("      fin (ctax + aet) payroll ordAGI 0 0 div div newCE newDefer (s.qOK && active)", "      fin (ctax + aet) payroll ordAGI 0 0 div div newCE newDefer (s.qOK && active) 0")
rep("  | .trumpAcct =>\n", "  | .childCare =>\n    if s.done || s.year ≥ sc.years || s.care then none else some { s with care := true }\n  | .trumpAcct =>\n")
rep("acct := false, oDef := false, oPS := false, sDef := false, sPS := false, trump := false, cE := 0, cYear := 0,", "acct := false, oDef := false, oPS := false, sDef := false, sPS := false, trump := false, care := false, cE := 0,\n    cYear := 0,")
rep("  ([deferLimit, sc.spouseWork].filter (· ≤ sc.spouseWork)).eraseDups.map .hireSpouse ++", "  ([deferLimit, sc.spouseWork, sc.spouseWork - sc.daycare].filter (fun a => a > 0 && a ≤ sc.spouseWork)).eraseDups.map .hireSpouse ++")
rep("   .spousePS, .trumpAcct,", "   .spousePS, .trumpAcct, .childCare,")
rep('| .trumpAcct => "Trump account"\n', '| .trumpAcct => "Trump account"\n  | .childCare => "child-care contract"\n')
rep('| .trumpAcct => "trump" |', '| .trumpAcct => "trump" | .childCare => "care" |')
rep("    rent := 11200,", "    daycare := 20000, rent := 11200,")
rep("  | .ownerDefer | .ownerPS | .spouseDefer | .spousePS | .trumpAcct => false\n  | _ => true\n\ndef oneYear", "  | .ownerDefer | .ownerPS | .spouseDefer | .spousePS | .trumpAcct => false\n  | _ => true\n\ndef old : Move → Bool\n  | .trumpAcct | .childCare => false\n  | _ => true\n\ndef oneYear")
rep('"salary"] do', '"salary", "care"] do')
i = t.index('#eval search (scn 400000 false) oneYear')
t = t[:i] + open('tools/hunt/out/Entity/tail3.txt', encoding='utf-8').read()
open(p, 'w', encoding='utf-8', newline='\n').write(t)
