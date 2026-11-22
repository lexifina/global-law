import PwGlobal.Pit

/-!
# Palau 2025: employer social security and healthcare fund contributions (2200)

Palau National Code Annotated Title 41 (Social Security), PacLII consolidation `pw/legis/consol_act/sst41226.pdf` (Supp. 18,
Wayback 20241025034041; `pw/law/pw_pnca_t41_paclii_wb20241025.pdf`):
* **41 PNCA § 744 (e)**: an employer contributes 7 % of the remuneration paid "after 1 October 2017" (RPPL 10-12 § 32);
  **§ 742**: "On October 1, 2017, there will no longer be a maximum amount of remuneration" (no ceiling); § 743 (a) (5):
  employees 7 %.
* **41 PNCA § 924 (e)** (National Healthcare Financing Act, RPPL 8-14): every participating employer pays a minimum of 2.5 %
  of its employees' total remuneration (as defined by the Social Security Act) each quarter into the Medical Savings Fund;
  § 924 (a): employees 2.5 %.
-/

namespace PwGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Social security employer contribution (7 %)" a.wages pos (fun b => divR .down (700 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "41 PNCA § 744 (e), § 742 (no maximum from 1 Oct 2017)"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Healthcare fund employer contribution (2.5 %)" a.wages pos (fun b => divR .down (250 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "41 PNCA § 924 (e) (Medical Savings Fund, RPPL 8-14)")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if true then ["employees are taken to be participating employees of a participating employer (§ 924); self-employed deemed remuneration (§ 741, § 924 (d)) not modelled"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 20000 }] } } []).map (·.due) == [1400, 500]

end PwGlobal.Social
