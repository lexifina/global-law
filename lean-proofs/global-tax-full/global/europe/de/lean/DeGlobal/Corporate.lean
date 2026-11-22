import DeGlobal.Pit

/-!
# DE 2025: withholding on payments abroad (pass 8; the KSt, SolZ and GewSt of the company are the pilot's, `DeGlobal/Basic.lean`)


## 1200 Kapitalertragsteuer / Abzugsteuer (§ 50a): dividend, interest, royalty, services (pass 8, grade A)
Source: EStG §§ 43, 43a, 44a, 49, 50a, gesetze-im-internet.de (`de/law/estg_43.txt` ... `estg_50a.txt`); SolZG § 4 (`de/law/solzg_1995___4.txt`).
* § 43a (1) Nr. 1: "25 Prozent des Kapitalertrags"; § 50a (2): "Der Steuerabzug beträgt 15 Prozent" (30 % for supervisory boards)
* § 49 (1) Nr. 5 c aa: interest is domestic income only where the capital is secured on domestic land, rights or registered ships
* SolZG § 4: "Der Solidaritätszuschlag beträgt 5,5 Prozent der Bemessungsgrundlage"
-/

namespace DeGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- EStG §§ 43, 43a, 49 Abs. 1 Nr. 5, 50a Abs. 1-2; SolZG §§ 3, 4 -/
def p8wht : Wht :=
  { name := "Kapitalertragsteuer / Abzugsteuer (§ 50a)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 2500, statute := "EStG § 43 Abs. 1 Satz 1 Nr. 1, § 43a Abs. 1 Satz 1 Nr. 1: Kapitalertragsteuer 25 %" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "EStG § 49 Abs. 1 Nr. 5 Buchst. c Doppelbuchst. aa: interest of non-residents is German income only when secured on German real estate or ships: none on an unsecured loan" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "EStG § 50a Abs. 1 Nr. 3, Abs. 2 Satz 1: Steuerabzug 15 % on royalties" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "EStG § 50a Abs. 1: the Steuerabzug covers performances (Nr. 1-2), rights (Nr. 3) and supervisory boards (Nr. 4): none on other service fees" }] }
/-- SolZG § 3 (1) Nr. 5-6, § 4: 5,5 % of the Kapitalertragsteuer / Abzugsteuer withheld -/
def p8whtSolZ (co : Company) : List Charge :=
  (co.paymentsAbroad.zipIdx.filter fun (p, _) => p8wht.amount p > 0).map fun (p, i) =>
    charge (if p.toCompany then .cit else .pit) "Solidaritätszuschlag (Abzugsteuern)" (p8wht.amount p) id
      (fun x => divR .down (550 * x) BP) (event := s!"payment {i + 1} ({p.kind.name})") (bearer := .withheld)
      (statute := "SolZG § 3 (1) Nr. 5 und 6, § 4 Satz 1 (5,5 %)")

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Kapitalertragsteuer / Abzugsteuer (§ 50a) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) },
   { name := "1200 Solidaritätszuschlag on withholding (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8whtSolZ g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["DE 1200 withholding pass 8 (dividend, interest, royalty, services): gesetze-im-internet.de, fetched 2026-11-21 (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .dividend) then ["1200 withholding: the refund of two fifths to foreign corporations (§ 44a Abs. 9) and the EU parent-subsidiary exemption (§ 43b) not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .royalty) then ["1200 withholding: the § 50c exemption for EU associated companies not applied"] else [])

#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard (p8whtSolZ { paymentsAbroad := [{ kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 }] }).map (·.due) == [1375]
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 25000
#guard (p8whtSolZ { paymentsAbroad := [{ kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 }] }).map (·.due) == [1375]
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard (p8whtSolZ { paymentsAbroad := [{ kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 }] }).map (·.due) == [825]
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 15000
#guard (p8whtSolZ { paymentsAbroad := [{ kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 }] }).map (·.due) == [825]
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end DeGlobal.Corporate
