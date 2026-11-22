import DmGlobal.Pit

/-!
# Dominica 2025: employer Social Security contributions (2200)

Sources: Social Security (Collection of Contributions) (Amendments) Regulations 2008, S.R.O. 8 of 2008 (in force 1 March
2008; the 1.x builder's copy `world/B13-caribbean/dm/law/acts/..._2008_SRO_8_o.pdf`, re-OCR at 400 dpi): Schedule
"Rates of Contributions as a percentage of Insurable Earnings ... (1) Employees excluding those at 2 below 4% 7%; (2)
Categories of employees exempted from the provisions of the Protection of Employment Act ... 4% 6.75%"; S.R.O. 22 of
2019 (in force 1 March 2019; dominica.gov.dm PDF via Wayback, `dm/law/ss_coll_amend_sro22_2019.pdf`) reg. 3: insurable
earnings "$1617" weekly and "$7000" monthly. Grade B: the Schedule is headed "for period commencing on the appointed
date to 31st December, 2008" and no later rate schedule is in the government list of Social Security S.R.O.s (the 2018
and 2019 S.R.O.s change the surcharge and the ceiling only), so the 2008 rates are read as continuing; the 1.x model
reads the employee's 4 % the same way.
-/

namespace DmGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon DmGlobal

def ss : Contribution := Contribution.flatCapped "Social Security (employer)" 700 (7000 * 12)
def sscF : Family := employerFamily "2200 Social Security employer" [ss] "S.R.O. 8 of 2008 Schedule (employer 7 %, row 1); insurable earnings $7,000 a month (S.R.O. 22 of 2019)"

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "employer Social Security 7 % to $7,000 a month (2008 schedule read as continuing); the 6.75 % row for employees outside the Protection of Employment Act not distinguished"

#guard ss.amount 60000 == 4200
#guard ss.amount 100000 == 5880

end DmGlobal.Social
