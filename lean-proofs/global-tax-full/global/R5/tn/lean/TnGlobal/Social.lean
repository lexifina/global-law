import TaxKernel.Global
import R5Common

/-!
# Tunisia 2025: employer CNSS contributions (2200), TFP and FOPROLOS (3000)

* CNSS, private non-agricultural scheme (Law 60-30 of 14 Dec 1960 art. 40-47; rates by decree, not read): the fund's
  employer page as archived on 2025-04-21 (`law/wb_cnss_nonagr_20250421.html`): total rate 25,75 %, of which
  16,57 % on the employer and 9,18 % on the employee (no wage ceiling); work-injury rate 0.4-4 %
  by activity (Decree 95-538): not computed.
* Taxe de formation professionnelle: LF 1989 (Loi 88-145) art. 29-30 in the DGELF recueil "mis à jour au 1er janvier
  2023" (`law/recueil2023.pdf`): monthly on all wages, "2% pour tous les secteurs à l'exception des entreprises
  exerçant dans le secteur des industries manufacturières … 1%" (2 % applied).
* FOPROLOS: Loi 77-54 art. 1-2 (same recueil): every public or private employer except private farmers, "fixée au
  taux de 1 %".
LF 2024 (Loi 2023-13) and LF 2025 (Loi 2024-48) do not amend either (searched).
-/

namespace TnGlobal
open TaxKernel TaxKernel.Global R5Common

/-- A payroll tax (OECD 3000) of `rateBp` on each adult's wages, borne by the employer. -/
def payrollOn (name statute : String) (rateBp : Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
    charge .payroll name a.wages (fun w => pos w) (fun b => divR .down (rateBp * b) BP)
      (event := s!"adult {i + 1}") (level := .social) (bearer := .employer) (statute := statute)

def social : Family :=
  { name := "2200/3000 CNSS employer, TFP, FOPROLOS", covers := [.sscEmployer, .payroll],
    run := fun _ g _ =>
      employerOn "اشتراكات الضمان الاجتماعي (المؤجر)" "Law 60-30 art. 40-47; CNSS rate 16,57 % employer (fund page, archived 2025-04-21)" 1657 (-1) g
      ++ payrollOn "Taxe de formation professionnelle" "Loi 88-145 (LF 1989) art. 29-30: 2 % (1 % manufacturing)" 200 g
      ++ payrollOn "Contribution au FOPROLOS" "Loi 77-54 art. 1-2: 1 %" 100 g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer: work-injury rate (0.4-4 % by activity, Decree 95-538) not computed; TFP at 2 % (manufacturing 1 %); agricultural, fishing and domestic-worker schemes, total exporters and regional-development firms (exempt from TFP/FOPROLOS) not distinguished"]

#guard divR .down (1657 * 1000000) BP == 165700

end TnGlobal
