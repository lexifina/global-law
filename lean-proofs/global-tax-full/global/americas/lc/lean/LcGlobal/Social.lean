import LcGlobal.Pit

/-!
# Saint Lucia 2025: employer National Insurance (2200)

Source: National Insurance Corporation Act Cap. 16.01 (Revised Laws, the 1.x builder's copy `world/B13-caribbean/lc/law/
nic/`): s. 28 (2), Schedule 2: "the employer's and employee's contribution shall each be 5% of the total salary or
wages"; s. 29, Schedule 3 para. 1: earnings "in excess of $60,000 per annum ... are exempted in respect of that portion
in excess of $60,000". Grade A.
-/

namespace LcGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon LcGlobal

def nic : Contribution := Contribution.flatCapped "National Insurance (employer)" 500 60000
def sscF : Family := employerFamily "2200 National Insurance employer" [nic] "NIC Act Cap. 16.01 s. 28 (2), Sched. 2: 5 %; Sched. 3 para. 1: earnings above $60,000 a year exempt"

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0)) "employer NIC 5 % to $60,000 a year; persons under 16 or over 60 (insured only by regulations) not distinguished"

#guard nic.amount 40000 == 2000
#guard nic.amount 100000 == 3000

end LcGlobal.Social
