import KzGlobal.Pit

/-!
# Kazakhstan 2025: corporate income tax and withholding on non-residents (1200)

Source: Tax Code 2017 (adilet, archived 2025-06-11; `law/SOURCES.tsv`).
* **art. 313 (1)**: taxable income less the art. 288 items and the losses carried forward under art. 300 "подлежит
  обложению налогом по ставке 20 процентов".
* **art. 300 (1)**: business losses carried forward (ten years; the year limit is not modelled: `lossesForward` is offset in
  full).
* **art. 646 (1)**: non-residents' income at source: 1) other income "20 процентов"; 5) "доходы от прироста стоимости,
  дивиденды, вознаграждения, роялти – 15 процентов"; (4) the dividend exemption for holdings over three years is not
  modelled.
-/

namespace KzGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Корпоративный подоходный налог",
    sched := Schedule.flat 2000 }

def citStatute : String := "Налоговый кодекс 2017 ст. 313 п. 1 (20 %); ст. 300 (перенос убытков)"

def wht : Wht :=
  { name := "Подоходный налог у источника выплаты (нерезиденты)", rules := [
      { kind := .dividend, rateBp := 1500, statute := "ст. 646 п. 1 пп. 5) (дивиденды 15 %)" },
      { kind := .interest, rateBp := 1500, statute := "ст. 646 п. 1 пп. 5) (вознаграждения 15 %)" },
      { kind := .royalty, rateBp := 1500, statute := "ст. 646 п. 1 пп. 5) (роялти 15 %)" },
      { kind := .services, rateBp := 2000, statute := "ст. 646 п. 1 пп. 1) (прочие доходы 20 %)" },
      { kind := .other, rateBp := 2000, statute := "ст. 646 п. 1 пп. 1) (20 %)" }] }

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
  (if g.company.dividendsReceived ≠ 0 then ["dividends received: art. 288 exemption not modelled (they stay in the profit)"] else [])
  ++ (if g.company.debt ≠ 0 then ["thin capitalisation (art. 246) not modelled"] else [])
  ++ (if !g.company.paymentsAbroad.isEmpty then ["art. 646 (2) tax-haven rate 20 % and (4) the three-year dividend exemption not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 200000
#guard cit.citTax { profit := 1000000, lossesForward := 300000 } == 140000
#guard wht.amount { kind := .dividend, amount := 1000 } == 150
#guard wht.amount { kind := .services, amount := 1000 } == 200

end KzGlobal.Corporate
