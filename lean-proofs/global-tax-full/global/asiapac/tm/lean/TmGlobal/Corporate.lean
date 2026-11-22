import TmGlobal.Pit

/-!
# Turkmenistan 2025: profit tax and tax on non-residents' income (1200)

Source: Tax Code (mejlis.gov.tm consolidation to 12.04.2025).
* **art. 172 (1)**: "8 процентов - для юридических лиц-резидентов Туркменистана (кроме юридических лиц, в уставном фонде которых
  доля, превышающая 50 процентов, принадлежит государству …)"; 50 % for state credit institutions and insurers and listed
  service providers (not modelled); "20 процентов - для других юридических лиц" (flags `stateMajority`, `nonResident`).
  **(2)** dividends received 15 %.
* **art. 167**: losses carried forward "не более чем на три года" (year limit not modelled).
* **art. 180 (3)**: non-residents' income without a permanent establishment "по ставке 15 процентов" (6 % on bare-boat leases).
-/

namespace TmGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- The rate by the company's flags (sector), else the general rate. -/
def rateOf (co : Company) : Int := if co.flags.contains "stateMajority" then 2000 else if co.flags.contains "nonResident" then 2000 else 800

def cit (co : Company) : CorpRegime :=
  { name := "Налог на прибыль",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "Налоговый кодекс ст. 172 п. 1 (8 % юридические лица-резиденты; 20 % с долей государства > 50 % и другие юридические лица); ст. 167 (убытки, 3 года)"

def wht : Wht :=
  { name := "Налог на доходы нерезидентов (у источника)", rules := [
      { kind := .dividend, rateBp := 1500, statute := "ст. 180 п. 3 (15 %)" },
      { kind := .interest, rateBp := 1500, statute := "ст. 180 п. 3 (15 %)" },
      { kind := .royalty, rateBp := 1500, statute := "ст. 180 п. 3 (15 %)" },
      { kind := .services, rateBp := 1500, statute := "ст. 180 п. 3 (15 %)" }] }

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
  (if true then ["the 50 % rate for state credit institutions, insurers and listed services is not modelled"] else [])

#guard (cit { profit := 1000000 }).citTax { profit := 1000000 } == 80000
#guard (cit { profit := 1000000, flags := ["stateMajority"] }).citTax { profit := 1000000 } == 200000

end TmGlobal.Corporate
