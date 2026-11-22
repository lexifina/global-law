import UzGlobal.Pit

/-!
# Uzbekistan 2025: VAT (5111) and excises (5121)

Source: Tax Code of the Republic of Uzbekistan of 30.12.2019 No. ЗРУ-599, lex.uz text as in force on 2025-01-01
(`cmp20/world/B05-former-ussr/uz/law/lex_tc_ru_on20250101.txt`; amendments by ЗРУ-1014 of 24.12.2024 included;
sha256 in `law/SOURCES.tsv`).
* **art. 258**: "налоговая ставка устанавливается в размере 12 процентов"; 0 % in the cases of chapter 36.
* **art. 461 (1) 1)**: legal entities "совокупный доход которых за налоговый период не превышает один миллиард сумов"
  pay the turnover tax instead of VAT: VAT threshold 1 000 000 000 sum.
* Exempt: **art. 243** 10) education, 27) financial services (art. 244), 28) insurance (art. 245).
* **art. 289-1** (ЗРУ-1014): cigarettes "на производимые … с 1 января 2025 года: 300 000 сум/1 000 штук" (imports
  330 000, and 340 000 from 1 July 2025); **art. 289-2** (per litre): vodka and other alcohol, per litre of
  anhydrous alcohol, imports 76 000 / produced 44 000; natural wine 14 000 / 5 000; beer 6 000 / 2 000.
  **art. 289-3**: petroleum products per tonne (not modelled). The basket uses the rates on domestic production
  unless the line sets `"uzImported": true`.
-/

namespace UzGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Налог на добавленную стоимость", standard := 1200, threshold := 1000000000,
    classOf := fun gd => match gd with
      | .education | .financial | .insurance => .exempt
      | _ => .standard }

def excise (imported : Bool) : Excise :=
  { rates := [
      { good := .spirits, name := "Акцизный налог (алкогольная продукция)", perUnitNum := if imported then 76000 else 44000,
        onPureAlcohol := true, statute := "Налоговый кодекс ст. 289-2 п. 2 (76 000 / 44 000 сум за литр безводного спирта)" },
      { good := .wine, name := "Акцизный налог (вино натуральное)", perUnitNum := if imported then 14000 else 5000,
        statute := "ст. 289-2 п. 3 (14 000 / 5 000 сум за литр)" },
      { good := .beer, name := "Акцизный налог (пиво)", perUnitNum := if imported then 6000 else 2000,
        statute := "ст. 289-2 п. 4 (6 000 / 2 000 сум за литр)" },
      { good := .cigarettes, name := "Акцизный налог (сигареты)", perUnitNum := if imported then 330000 else 300000,
        perUnitDen := 1000, statute := "ст. 289-1 п. 1 (на производимые 300 000 сум/1 000 штук; импорт 330 000)" }] }

def imported (g : CanonGlobal) : Bool := match g.raw.getObjVal? "uzImported" with | .ok (.bool b) => b | _ => false

def vatStatute : String := "Налоговый кодекс ст. 258 (12 %), ст. 461 (1 млрд сумов), ст. 243-245"

def families : List Family :=
  [{ name := "5111 НДС, 5121 акцизный налог", covers := [.vat, .excise],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ (excise (imported g)).charges g.consumption }]

def absent : List Absent := []
def notes : List String := ["UZ 5111/5121: Tax Code as in force 2025-01-01 (lex.uz), ЗРУ-1014 rates"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then
    ["petroleum excise (art. 289-3) is per tonne: not modelled"] else [])
  ++ (if imported g && g.consumption.any (·.good == .cigarettes) then
    ["imported cigarettes: 330 000 sum/1 000 used; the 340 000 rate from 1 July 2025 is not applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .rent || s.good == .health || s.good == .medicines) then
    ["VAT on rent, health and medicines taken at the standard rate: their exemptions were not read"] else [])

#guard vat.embedded { good := .food, amount := 11200 } == 1200
#guard vat.embedded { good := .education, amount := 11200 } == 0
#guard (excise false).duty { good := .spirits, amount := 50000, quantity := 500, abvBp := 4000 } == 8800
#guard (excise true).duty { good := .cigarettes, amount := 20000, quantity := 20000 } == 6600
#guard (excise false).duty { good := .cigarettes, amount := 20000, quantity := 20000 } == 6000

end UzGlobal.Consumption
