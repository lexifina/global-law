import JmGlobal.Pit

/-!
# Jamaica 2025: employer NIS, NHT (2200), Education Tax and HEART (3000)

Source: Tax Administration Jamaica, "Payroll Taxes and Statutory Contributions (Employee / Employer)" (the 1.x builder's
copy, `world/B13-caribbean/jm/law/TAJ_Payroll_Taxes_and_Statutory_Contributions_Employee_Employer.pdf`), Table #5: an
official secondary source for the rates of the NIS Act, NHT Act, Education Tax Act and HEART Act (grade B).
* NIS employer "3%" on "Gross Emoluments not exceeding $5,000,000"; NHT employer "3%" on gross emoluments; Education
  Tax employer "3.5%" on statutory income (taken as gross emoluments, flagged); HEART "3%" of gross emoluments "if the
  employer's payroll costs exceeds $173,328 per annum".
-/

namespace JmGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon JmGlobal

def nis : Contribution := Contribution.flatCapped "NIS (employer)" 300 5000000
def nht : Contribution := { name := "NHT (employer)", sched := Schedule.flat 300 }
def sscF : Family := employerFamily "2200 NIS and NHT (employer)" [nis, nht] "TAJ Table #5: NIS 3 % to $5,000,000; NHT 3 %"
def edTax : PayrollTax := { name := "Education Tax (employer)", rateBp := 350 }
def heart : PayrollTax := { name := "HEART (employer)", rateBp := 300, threshold := 173328, deduct := false }
def payF : Family :=
  { name := "3000 Education Tax and HEART", covers := [.payroll],
    run := fun args g l => (payrollFamily "Education Tax" edTax "TAJ Table #5: Education Tax employer 3.5 %").run args g l
      ++ (if g.entity == .company then (payrollFamily "HEART" heart "TAJ Table #5: HEART 3 % if payroll > $173,328").run args g l else []) }

def families : List Family := [sscF, payF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0)) "Education Tax base taken as gross emoluments (statute: statutory income); HEART on a household's wages depends on the employer's payroll: not charged"

#guard nis.amount 6000000 == 150000
#guard nht.amount 1000000 == 30000
#guard edTax.amount 1000000 == 35000
#guard heart.amount 173328 == 0
#guard heart.amount 200000 == 6000

end JmGlobal.Social
