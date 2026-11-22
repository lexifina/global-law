import VcGlobal.Pit

/-!
# Saint Vincent and the Grenadines 2025: employer National Insurance (2200)

Source: National Insurance Services, "Employers' Guide" (nissvg.org), Wayback capture of 21 April 2025
(`vc/law/nis_employers_guide_wb2025.html`, ARCHIVE_INDEX.tsv), an official secondary source for the National Insurance
Act Cap. 229 regulations (facts paraphrased): contributions total 13 % of insurable earnings, 6 % from the employee and
7 % from the employer; earnings are insurable up to $62,400 a year ($5,200 a month, $1,200 a week). (The live page, fetched 2026-11-21, reads 14 %, employee 6.5 %, employer
7.5 %: a later change.) Grade B.
-/

namespace VcGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon VcGlobal

def nis : Contribution := Contribution.flatCapped "National Insurance (employer)" 700 62400
def sscF : Family := employerFamily "2200 National Insurance employer" [nis] "NIS Employers' Guide (capture 21 April 2025): employer 7 % of insurable earnings up to $62,400 a year"

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "employer NIS 7 % to $62,400 a year (rate of the April 2025 guide; a change later in 2025 would not be seen); the employment-injury-only 0.5 % for employees outside the pension branch not distinguished"

#guard nis.amount 50000 == 3500
#guard nis.amount 100000 == 4368

end VcGlobal.Social
