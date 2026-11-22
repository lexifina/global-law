import BbGlobal.Pit

/-!
# Barbados 2025: employer National Insurance and levies (2200)

Source: National Insurance and Social Security Service, "Contribution Rates & Earnings Ceilings" (nis.gov.bb, the 1.x
builder's copy read 2026-11-20, `world/B13-caribbean/bb/law/nis_gov_bb_contribution-rates_2026-11-20.html`), an
official secondary source for the rates under the National Insurance and Social Security Act Cap. 47 and its
Regulations: grade B. Private Sector Employees "R", Employer %: National Insurance 6.75, Non-Contributory 2.00,
Unemployment 0.75, Employment Injury 0.75, Severance 0.50, Training Levy 0.50, Health Service Contribution 1.50 (total
12.75); "Resilience & Regeneration" employer 0.25 % "from April 1, 2025". Ceiling 2025 (1.x model): $5,280 a month.
-/

namespace BbGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon BbGlobal

def nis : Contribution := Contribution.flatCapped "NIS, levies and Health Service Contribution (employer)" 1275 (5280 * 12)
def sscF : Family := employerFamily "2200 NIS employer (private sector R)" [nis] "NIS rate table: employer 12.75 % (NI 6.75, NC 2, UE 0.75, EI 0.75, severance 0.5, training 0.5, HSC 1.5) to $5,280 a month"

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0)) "employer contributions at the private-sector R rates to the $5,280 monthly ceiling (Health Service Contribution and levies assumed under the same ceiling); Resilience & Regeneration 0.25 % from 1 April 2025 not charged (lower bound); public-sector rows not modelled"

#guard nis.amount 100000 == 8078
#guard nis.amount 50000 == 6375

end BbGlobal.Social
