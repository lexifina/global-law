import KzGlobal.Pit

/-!
# Kazakhstan 2025: VAT (5111) and excises (5121)

Source: Tax Code of the Republic of Kazakhstan (Кодекс от 25.12.2017 № 120-VI, adilet K1700000120) as archived on
2025-06-11 (`cmp20/world/B05-former-ussr/kz/law/tc_wb20250611.txt`, sha256 in `law/SOURCES.tsv`); the 2017 Code
governs 2025 (the new Code of 18.07.2025 applies from 2026-01-01).
* **art. 422 (1)**: "Ставка налога на добавленную стоимость составляет 12 процентов"; (2) exports at the zero rate.
* **art. 82 (4)**: "Минимум оборота составляет 20 000-кратный размер месячного расчетного показателя"; МРП 2025 =
  3 932 тенге (Law on the republican budget 2025-2027 art. 9; the 1.x model's `mrp`).
* Exemptions: **art. 394** 33) medicines, 35) medical care, 28)-30) education; **art. 396 (1) 2)** letting of
  dwellings; **art. 397 (2)** financial operations (deposits, loans) and 6) insurance.
* **art. 463 (4) 1)** table (tenge per unit): 7. alcoholic products other than cognac, wine, beer "2550 тенге/литр
  100 % спирта"; 9. wines "35 тенге/литр"; 12. beer products "90 тенге/литр"; 14. filter cigarettes "15 900 тенге/1 000
  штук". Motor fuels (art. 463 (4) 2)) are taxed per tonne by seller type: not modelled (the basket is in litres).
-/

namespace KzGlobal.Consumption
open TaxKernel TaxKernel.Global

def mrp : Int := 3932

def vat : Vat :=
  { name := "Налог на добавленную стоимость", standard := 1200, threshold := 20000 * mrp,
    classOf := fun gd => match gd with
      | .medicines | .health | .education | .rent | .financial | .insurance => .exempt
      | _ => .standard }

def excise : Excise :=
  { rates := [
      { good := .spirits, name := "Акциз (алкогольная продукция)", perUnitNum := 2550, onPureAlcohol := true,
        statute := "Налоговый кодекс ст. 463 п. 4 пп. 1) стр. 7 (2 550 тенге/литр 100 % спирта)" },
      { good := .wine, name := "Акциз (вина)", perUnitNum := 35, statute := "ст. 463 п. 4 пп. 1) стр. 9 (35 тенге/литр)" },
      { good := .beer, name := "Акциз (пивоваренная продукция)", perUnitNum := 90,
        statute := "ст. 463 п. 4 пп. 1) стр. 12 (90 тенге/литр)" },
      { good := .cigarettes, name := "Акциз (сигареты)", perUnitNum := 15900, perUnitDen := 1000,
        statute := "ст. 463 п. 4 пп. 1) стр. 14 (15 900 тенге/1 000 штук)" }] }

def vatStatute : String := "Налоговый кодекс 2017 ст. 422 (12 %), ст. 394, 396, 397 (освобождения), ст. 82 п. 4 (минимум оборота 20 000 МРП)"

def families : List Family :=
  [{ name := "5111 НДС, 5121 акцизы", covers := [.vat, .excise],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent := []
def notes : List String := ["KZ 5111/5121: Tax Code 2017 as in force 2025 (adilet, archived 2025-06-11)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then
    ["motor-fuel excise (Tax Code art. 463 (4) 2)) is per tonne by seller type: not modelled"] else [])
  ++ (if g.consumption.any (·.good == .tobaccoOther) then ["excise on other tobacco (art. 463 row 18, per kg) not modelled"] else [])

-- art. 422: 12 % inside a tax-inclusive 11 200
#guard vat.embedded { good := .food, amount := 11200 } == 1200
#guard vat.embedded { good := .rent, amount := 11200 } == 0
-- art. 82 (4): the minimum turnover 78 640 000 tenge; at it no VAT is due
#guard vat.threshold == 78640000
#guard vat.net { turnover := 78640000, sales := [{ good := .other, net := 78640000 }] } == 0
-- 1 litre of 40 % vodka: 0.4 l of pure alcohol × 2 550
#guard excise.duty { good := .spirits, amount := 5000, quantity := 1000, abvBp := 4000 } == 1020
-- a pack of 20 cigarettes: 20 × 15.9
#guard excise.duty { good := .cigarettes, amount := 1000, quantity := 20000 } == 318

end KzGlobal.Consumption
