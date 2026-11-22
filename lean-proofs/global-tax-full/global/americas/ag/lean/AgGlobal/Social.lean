import AgGlobal.Pit

/-!
# Antigua and Barbuda 2025: employer Social Security and Medical Benefits (2200)

Sources (the 1.x builder's copies, `world/B15-no-pit/ag/law/`): Social Security Act Cap. 408 and the Social Security
(Collection of Contributions) Regulations (S.I. 15 of 2013, S.I. 60 of 2016) Schedule 1 row 2025: private sector
employee 7 %, employer 9 %, total 16 %; ceiling "$6,500.00 per month". Medical Benefits Regulations 2011 (S.I. 27 of
2011): "An employer shall pay contributions to the Scheme at the rate of 3½% of the salary or wages" (no ceiling).
Grade A.
-/

namespace AgGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon AgGlobal

def ss : Contribution := Contribution.flatCapped "Social Security (employer)" 900 (6500 * 12)
def mb : Contribution := { name := "Medical Benefits (employer)", sched := Schedule.flat 350 }
def sscF : Family := employerFamily "2200 Social Security and Medical Benefits (employer)" [ss, mb] "SS (Collection of Contributions) Regs Sched. 1 (S.I. 60/2016) 2025: employer 9 % to $6,500 a month; Medical Benefits Regs 2011: employer 3.5 %"

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0)) "employer Social Security 9 % (private sector) to $6,500 a month and Medical Benefits 3.5 %; public-sector rows and ages 60+ not distinguished"

#guard ss.amount 50000 == 4500
#guard ss.amount 100000 == 7020
#guard mb.amount 100000 == 3500

end AgGlobal.Social
