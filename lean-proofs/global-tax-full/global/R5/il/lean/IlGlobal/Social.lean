import TaxKernel.Global
import R5Common

/-!
# Israel 2025: employer national insurance contributions (2200)

National Insurance Law [consolidated] 1995, Hebrew Wikisource revision 2946268 of 2025-06-29 (`law/il_ni.txt`):
* s. 337(א)(1), 340(א)(1): monthly rates for an employee are the percentages of לוח י׳; its temporary version
  "(הוראת שעה לשנים 2025–2026)", total row, column ג "לעובד": 14.60 on the part above the reduced band (work injury
  2.06 as the 2024-2027 temporary rate) and 5.55 on the part up to it; column ד, the deduction from the employee's
  wage: 7.00 and 1.04. The employer bears the rest: 7.60 % above and 4.51 % up to the band.
* s. 334(א): "מדרגת גבייה מופחתת – סכום של 7,522 שקלים חדשים (נקוב לשנת 2025)".
* לוח י״א item 1: monthly maximum income "הסכום הבסיסי, כפול 5"; s. 1 note: the basic amount for other benefits
  (para. (3)) "בשנת 2025, 10,139 ש״ח": 50,695 a month (the 1.x model's ceiling).
Wages are taken as earned evenly over 12 months.
-/

namespace IlGlobal
open TaxKernel TaxKernel.Global R5Common

def ilBand : Int := 7522 * 12
def ilCeil : Int := 5 * 10139 * 12

/-- Employer NI on a wage band [lo, hi) of annual wages at `rateBp`. -/
def bandOn (name statute : String) (rateBp lo hi : Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter fun (a, _) => a.wages > lo).map fun (a, i) =>
    charge .sscEmployer name a.wages (fun w => min (pos (w - lo)) (hi - lo)) (fun b => divR .down (rateBp * b) BP)
      (event := s!"adult {i + 1}") (level := .social) (bearer := .employer) (statute := statute)

def social : Family :=
  { name := "2200 national insurance (employer)", covers := [.sscEmployer],
    run := fun _ g _ =>
      bandOn "דמי ביטוח לאומי – מעסיק (עד מדרגת הגבייה המופחתת)"
        "NI Law s. 337, 340, לוח י׳ (temporary 2025-2026): 5.55 − 1.04 = 4.51 % up to 7,522 a month (s. 334(a))" 451 0 ilBand g
      ++ bandOn "דמי ביטוח לאומי – מעסיק (מעל מדרגת הגבייה המופחתת)"
        "NI Law לוח י׳ (temporary 2025-2026): 14.60 − 7.00 = 7.60 % above 7,522 a month, to 5 × 10,139 a month (לוח י״א)" 760 ilBand ilCeil g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer NI: wages taken as earned evenly over 12 months; rates for employees past pension age, under 18, or non-residents (maternity and injury only, s. 335) not distinguished; no employer health tax exists (the health tax is the insured's)"]

#guard ilBand == 90264 && ilCeil == 608340
#guard divR .down (451 * ilBand) BP + divR .down (760 * (120000 - ilBand)) BP == 4070 + 2259

end IlGlobal
