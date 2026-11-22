import GdGlobal.Pit

/-!
# Grenada 2025: employer National Insurance (2200)

Source: National Insurance (Collection of Contributions) Regulations (Cap. 205) Schedule as amended by S.R.O. 43 of 2023
(in force 1 January 2024; the 1.x builder's reading): Part I (the employer's rows) 7 % from 1 January 2025; Part II
(employee) 6 %; Part III maximum insurable earnings "January 1, 2024 | $1,200 per week or $5,200 per month". The Part I
heading of the principal Regulations was not read (the 1.x builder read Part I as the employer's rows from content):
grade B.
-/

namespace GdGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon GdGlobal

def ni : Contribution := Contribution.flatCapped "National Insurance (employer)" 700 (5200 * 12)
def sscF : Family := employerFamily "2200 National Insurance employer" [ni] "NI (Collection of Contributions) Regs Cap. 205 Sched. Part I (S.R.O. 43/2023): 7 % from 1 Jan 2025 to $5,200 a month (Part III)"

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0)) "employer NI 7 % to $5,200 a month; Part I read as the employer's rows from content (heading not read)"

#guard ni.amount 50000 == 3500
#guard ni.amount 100000 == 4368

end GdGlobal.Social
