import GyGlobal.Pit

/-!
# Guyana 2025: employer National Insurance (2200)

Source: National Insurance Scheme, "Information on contributions" (nis.org.gy, the 1.x builder's copy read 2026-11-20,
`world/B13-caribbean/gy/law/nis_org_gy_information_on_contributions_2026-11-20.html`), official secondary for the
National Insurance and Social Security Act Cap. 36:01 regulations: "The total Contribution for Employed Contributors is
14% of the actual Wage / Salary"; the employee's deduction is 5.6 % (1.x model), so the employer pays 8.4 %; "Monthly
Ceiling ... January 2020 280,000". Grade B.
-/

namespace GyGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon GyGlobal

def nis : Contribution := Contribution.flatCapped "NIS (employer)" 840 (280000 * 12)
def sscF : Family := employerFamily "2200 NIS employer" [nis] "NIS: total 14 % less the employee's 5.6 % = 8.4 % to $280,000 a month (ceiling from January 2020)"

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0)) "employer NIS 8.4 % (14 % total less the 5.6 % employee deduction); ages outside 16-60 not distinguished"

#guard nis.amount 1000000 == 84000
#guard nis.amount 10000000 == 282240

end GyGlobal.Social
