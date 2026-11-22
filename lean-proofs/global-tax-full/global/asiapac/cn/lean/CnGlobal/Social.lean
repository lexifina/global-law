import CnGlobal.Pit

/-!
# China 2025 (Beijing): employer social insurance (2200)
社会保险法 (2010, amended 2018) and 国办发〔2019〕13号 (B: rates are local rules): employer pension 16 %, unemployment 0.5 %
(Beijing), contribution base capped at 3 × the average wage (Beijing 2025: 35,283 a month: 423,396 a year). Medical
(Beijing employer 9.8 % incl. maternity) and work injury by industry are not modelled.
-/

namespace CnGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "基本养老保险 (employer 16 %)" a.wages (fun w => min (pos w) 423396) (fun b => divR .down (1600 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "社会保险法 art. 12; 国办发〔2019〕13号"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "失业保险 (employer 0.5 %, Beijing)" a.wages (fun w => min (pos w) 423396) (fun b => divR .down (50 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "社会保险法 art. 44; 北京市 rule")) }

def families : List Family := [fam0]

def absent : List Absent :=
  [{ oecd := .payroll, why := "No payroll tax in China (registry: not levied; 社会保险 contributions are 2200); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => a.wages > 0) then ["medical insurance, work injury and housing provident fund (non-tax) not modelled; contribution floor not applied"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000 }] } } []).map (·.due) == [16000, 500]

end CnGlobal.Social
