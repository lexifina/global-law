import KgGlobal.Pit

/-!
# Kyrgyzstan 2025: profit tax and tax on non-residents' income at source (1200)

Source: Tax Code 2022, official edition 36891 (to 31.07.2025).
* **art. 240 (1)**: "ставка налога на прибыль устанавливается в размере 10 процентов" (0 % for the sectors of (2)-(4)).
* **art. 232 (1)**: losses carried forward "на срок не более 5 календарных лет" (the year limit is not modelled).
* **art. 249 (1)-(2)**: base = gross income without deductions; 1) dividends and interest 10 %; 3) "авторские гонорары, роялти
  - 10 процентов"; 4) works and services in the Kyrgyz Republic 10 %.
-/

namespace KgGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Налог на прибыль",
    sched := Schedule.flat 1000 }

def citStatute : String := "Налоговый кодекс 2022 ст. 240 ч. 1 (10 %); ст. 232 (убытки, 5 лет)"

def wht : Wht :=
  { name := "Налог на доход иностранной организации у источника", rules := [
      { kind := .dividend, rateBp := 1000, statute := "ст. 249 ч. 2 п. 1 (дивиденды 10 %)" },
      { kind := .interest, rateBp := 1000, statute := "ст. 249 ч. 2 п. 1 (процентные доходы 10 %)" },
      { kind := .royalty, rateBp := 1000, statute := "ст. 249 ч. 2 п. 3 (роялти 10 %)" },
      { kind := .services, rateBp := 1000, statute := "ст. 249 ч. 2 п. 4 (работы, услуги 10 %)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.lossesForward ≠ 0 then ["the 5-year limit of art. 232 is not checked"] else [])
  ++ (if g.company.dividendsReceived ≠ 0 then ["dividends received treatment not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 100000
#guard wht.amount { kind := .royalty, amount := 1000 } == 100

end KgGlobal.Corporate
