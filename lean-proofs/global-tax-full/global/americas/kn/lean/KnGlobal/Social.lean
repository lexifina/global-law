import KnGlobal.Pit

/-!
# Saint Kitts and Nevis 2025: employer Social Security (2200) and Housing and Social Development Levy (3000)

Sources (the 1.x builder's copies, `world/B15-no-pit/kn/law/`): Social Security Act Cap. 22.10 and Regulations, Revised
Edition 31 Dec 2017: Schedule 1 to the Regulations, Part II "EMPLOYER'S CONTRIBUTION ... Persons between 16 and 62
years 5% of wages subject to the ceiling" (1 % under 16 and from 62); Schedule 2 ceiling $6,500 a month. Housing and
Social Development Levy Act Cap. 20.21 s. 3 (2) (a)-(d): "3% by the employer in respect of the wages the employer pays
to the employee" at every wage level (Acts 1 of 2024 and 14 of 2025 change the employee thresholds only). Grade A.
-/

namespace KnGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon KnGlobal

def ss : Contribution := Contribution.flatCapped "Social Security (employer)" 500 (6500 * 12)
def sscF : Family := employerFamily "2200 Social Security employer" [ss] "SS Regs Sched. 1 Part II: 5 % (ages 16-61) to $6,500 a month (Sched. 2)"
def hsdl : PayrollTax := { name := "Housing and Social Development Levy (employer)", rateBp := 300 }
def payF : Family := payrollFamily "3000 Housing and Social Development Levy (employer 3 %)" hsdl "HSDL Act Cap. 20.21 s. 3 (2): 3 % by the employer on the wages paid"

def families : List Family := [sscF, payF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0)) "Social Security employer 5 % read for every employee (1 % for those under 16 or 62 and over: not distinguished)"

#guard ss.amount 50000 == 2500
#guard ss.amount 100000 == 3900
#guard hsdl.amount 50000 == 1500

end KnGlobal.Social
