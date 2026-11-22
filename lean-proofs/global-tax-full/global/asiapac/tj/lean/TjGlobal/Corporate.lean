import TjGlobal.Pit

/-!
# Tajikistan 2025: profit tax and withholding (1200)

Source: Tax Code as amended to 14.05.2025 (official English text).
* **art. 183 (4)**: legal entities "for activities on production of goods - 13 percent; for the activities of financial and
  credit organizations and mobile companies - 20 percent; … all other types of activity … - 18 percent" (company flags
  `production`, `financial`, `mobile`).
* **art. 197 (1)**: losses carried forward "up to and including 3 years" (year limit not modelled).
* **art. 237 (1)**: dividends "withholding tax at the rate of 12 percent" (Law of 15 April 2025 No. 2159); **art. 238 (1)**:
  interest 12 %; **art. 239 (8)**: non-residents' other income (royalties, services) "at the rate of 15 percent".
-/

namespace TjGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- The rate by the company's flags (sector), else the general rate. -/
def rateOf (co : Company) : Int := if co.flags.contains "production" then 1300 else if co.flags.contains "financial" then 2000 else if co.flags.contains "mobile" then 2000 else 1800

def cit (co : Company) : CorpRegime :=
  { name := "Profit tax (андози фоида)",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "Tax Code art. 183 (4) (13 % production, 20 % financial and mobile, 18 % other); art. 197 (losses, 3 years)"

def wht : Wht :=
  { name := "Withholding tax on non-residents", rules := [
      { kind := .dividend, rateBp := 1200, statute := "art. 237 (1) (12 %, Law No. 2159 of 15.04.2025)" },
      { kind := .interest, rateBp := 1200, statute := "art. 238 (1) (12 %)" },
      { kind := .royalty, rateBp := 1500, statute := "art. 239 (8) 7) (other income 15 %)" },
      { kind := .services, rateBp := 1500, statute := "art. 239 (8) 7) (other income 15 %)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [(cit g.company).citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.lossesForward ≠ 0 then ["the 3-year limit of art. 197 is not checked"] else [])

#guard (cit { profit := 1000000 }).citTax { profit := 1000000 } == 180000
#guard (cit { profit := 1000000, flags := ["production"] }).citTax { profit := 1000000 } == 130000
#guard wht.amount { kind := .dividend, amount := 1000 } == 120

end TjGlobal.Corporate
