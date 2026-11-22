import TwGlobal.Pit

/-!
# Taiwan 2025: employer social insurance (2200)
(B, official 2025 tables.) 勞工保險條例 art. 13 + 就業保險法: 12.5 % (incl. 1 % employment insurance), employer 70 %: 8.75 %,
insured salary capped at 45,800 a month (549,600 a year); 全民健康保險法 art. 18, 27: 5.17 % × 60 % × (1 + 0.56 average
dependants) = 4.839 %, capped at 219,500 a month; 勞工退休金條例 art. 14: employer 6 %, capped at 150,000 a month.
-/

namespace TwGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "勞工保險 + 就業保險 (employer 8.75 %)" a.wages (fun w => min (pos w) 549600) (fun b => divR .down (875 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "勞工保險條例 arts. 13, 15; 就業保險法 art. 40"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "全民健康保險 (employer 4.839 %)" a.wages (fun w => min (pos w) 2634000) (fun b => divR .down (4839 * b) 100000) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "全民健康保險法 arts. 18, 27"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "勞工退休金 (employer 6 %)" a.wages (fun w => min (pos w) 1800000) (fun b => divR .down (600 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "勞工退休金條例 art. 14")) }

def families : List Family := [fam0]

def absent : List Absent :=
  [{ oecd := .payroll, why := "No payroll tax in Taiwan; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 600000 }] } } []).map (·.due) == [48090, 29034, 36000]

end TwGlobal.Social
