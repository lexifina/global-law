import TaxKernel.Global
import R5Common
import CYTax

/-!
# Cyprus 2025: employer contributions (2200)

* Social Insurance Law 59(Ι)/2010 (cylaw as of 2025-09-12, 1.x `law/si_59_2010_as_of_2025-09-12.txt`) art. 5(1)(στ):
  "23,1%, από το οποίο 8,9% καταβάλλεται από τον μισθωτό, 8,9% από τον εργοδότη" from 2024; the proviso lets the rates
  of the actuarial study apply: the 1.x model applies 8,8 % to the employee (its FINDINGS F1), and the employer's
  share is taken at the same 8,8 % (grade B), on earnings up to the 1.x ceiling `CYTax.siCeiling` (€66.612).
* General Healthcare System Law 89(Ι)/2001 art. 19(1)(β): "κάθε εργοδότης σε ποσοστό 2,90% επί των αποδοχών κάθε
  μισθωτού του", up to the 1.x cap `CYTax.gesyCap` (€180.000).
Not modelled: Social Cohesion Fund, redundancy fund, HRDA levy (other laws, not read).
-/

namespace CyGlobal
open TaxKernel TaxKernel.Global R5Common

def social : Family :=
  { name := "2200 εισφορές εργοδότη", covers := [.sscEmployer],
    run := fun _ g _ =>
      employerOn "Κοινωνικές Ασφαλίσεις (εργοδότης)" "SIL 59(Ι)/2010 art. 5(1)(στ) (8,8 % applied; 8,9 % printed)" 880 (CYTax.siCeiling / 100) g
      ++ employerOn "ΓεΣΥ (εργοδότης)" "GHS Law 89(Ι)/2001 art. 19(1)(β) (2,90 %)" 290 (CYTax.gesyCap / 100) g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.household.adults.any (·.wages > 0) then ["employer: Social Cohesion Fund, redundancy and HRDA levies not modelled"] else []

#guard (employerOn "x" "y" 880 66612 { id := "t", household := { id := "t", adults := [{ wages := 100000 }] } }).map (·.due) == [5861]

end CyGlobal
