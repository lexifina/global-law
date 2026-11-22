import BsGlobal.Pit

/-!
# The Bahamas 2025: employer National Insurance (2200)

Source: National Insurance (Contributions) (Amendment) Regulations, 2024 (S.I. 37 of 2024, in force 1 July 2024; the 1.x
builder's copy `world/B15-no-pit/bs/law/nic_regs_amend_2024.pdf`): Fifth Schedule "Employed persons ... Basic wages 3.9
[employed person] 5.9 [employer] 9.8 [total]"; reg. 23 (1A): an increase "of one and one half percent ... shared
equally between the employer and employed person commencing the 1st day of July 2024": employer 5.9 + 0.75 = 6.65 %.
Ceiling: the last printed in the Regulations (reg. 52), $2,600 a month, as in the 1.x model; the 2025 administrative
ceiling (RPI + 2 %) is not in an accessible text (flagged). Grade B.
-/

namespace BsGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon BsGlobal

def ni : Contribution := Contribution.flatCapped "National Insurance (employer)" 665 (2600 * 12)
def sscF : Family := employerFamily "2200 National Insurance employer" [ni] "NI (Contributions) Regs Fifth Schedule (S.I. 37/2024) 5.9 % + reg. 23 (1A) 0.75 % = 6.65 %; ceiling $2,600 a month (reg. 52, last printed)"

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0)) "employer NI 6.65 % to the last printed ceiling ($2,600 a month); the 2025 administrative ceiling and the 65+ rate (5.4 %) not modelled"

#guard ni.amount 20000 == 1330
#guard ni.amount 100000 == 2074

end BsGlobal.Social
