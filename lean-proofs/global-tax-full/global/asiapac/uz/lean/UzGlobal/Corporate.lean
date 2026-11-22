import UzGlobal.Pit

/-!
# Uzbekistan 2025: profit tax and tax on non-residents' income (1200)

Source: Tax Code, lex.uz text in force 2025-01-01 (ЗРУ-1014 of 24.12.2024 in force 1 January 2025).
* **art. 337**: 1 banks 20; 2 mobile communication (and polyethylene granules) 20; 8 e-commerce 10; 11 dividends received 5;
  12 "Остальные налогоплательщики … 15" (company flags `bank`, `mobile`, `ecommerce`).
* **art. 333**: losses may reduce the profit of the current period "на всю сумму полученного им убытка или на часть" (no cap).
* **art. 353**: 1 "Дивиденды и проценты 10"; 6 "Иные доходы … 20" (royalties and services).
-/

namespace UzGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- The rate by the company's flags (sector), else the general rate. -/
def rateOf (co : Company) : Int := if co.flags.contains "bank" then 2000 else if co.flags.contains "mobile" then 2000 else if co.flags.contains "ecommerce" then 1000 else 1500

def cit (co : Company) : CorpRegime :=
  { name := "Налог на прибыль",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "Налоговый кодекс ст. 337 (ЗРУ-1014: банки 20 %, мобильная связь 20 %, электронная торговля 10 %, остальные 15 %); ст. 333"

def wht : Wht :=
  { name := "Налог на доходы нерезидентов", rules := [
      { kind := .dividend, rateBp := 1000, statute := "ст. 353 п. 1 (дивиденды и проценты 10 %)" },
      { kind := .interest, rateBp := 1000, statute := "ст. 353 п. 1 (10 %)" },
      { kind := .royalty, rateBp := 2000, statute := "ст. 353 п. 6 (иные доходы 20 %)" },
      { kind := .services, rateBp := 2000, statute := "ст. 353 п. 6 (иные доходы 20 %)" }] }

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
  (if g.company.dividendsReceived ≠ 0 then ["dividends received are taxed at 5 % (art. 337 row 11) apart from the profit: not modelled"] else [])

#guard (cit { profit := 1000000 }).citTax { profit := 1000000 } == 150000
#guard (cit { profit := 1000000, flags := ["bank"] }).citTax { profit := 1000000 } == 200000
#guard wht.amount { kind := .royalty, amount := 1000 } == 200

end UzGlobal.Corporate
