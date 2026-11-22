import KgGlobal.Pit

/-!
# Kyrgyzstan 2025: VAT (5111), sales tax (5112) and excises (5121)

Source: Tax Code of the Kyrgyz Republic of 18.01.2022 No. 3, official edition from cbd.minjust.gov.kg
(`GetEdition?editionId=36891`: amended up to Law No. 185 of 31.07.2025, so the text in force in the second half of
2025; `cmp20/world/B05-former-ussr/kg/law/kg_tc_ed36891.txt`, sha256 in `law/SOURCES.tsv`).
* **art. 254 (1)**: "ставка НДС устанавливается в размере 12 процентов от облагаемой поставки и облагаемого импорта";
  (2) zero rate for the supplies of arts. 302-306 (exports). **art. 255 (1)**: every entity on the general regime
  registers for VAT (no turnover threshold in the 2025 text).
* Exempt: **art. 265 (1) 1)** dwellings and the letting of dwellings; **art. 267** water, heat, electricity and gas
  supplied to an individual for domestic use; **art. 268 (2)** medicines and medical devices; **art. 270 (1)**
  financial services.
* **art. 368 (1)** sales tax on revenue without VAT and sales tax (art. 366 (1)): VAT-taxable supplies "1 процента -
  для торговой деятельности и сферы производства товаров", "2 процентов" otherwise; VAT-exempt supplies 2 % / 3 %.
* **art. 336 (1)** base excise rates: 2. vodka "литр 300 сомов"; 5. wines "литр 100 сомов"; 8. beer "литр 30
  сомов"; 12. 1) cigarettes "1000 штук … с 1 января по 31 декабря 2025 года включительно 3000 сомов". Petroleum
  products are taxed per tonne (row 13): not modelled.
-/

namespace KgGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "НДС", standard := 1200,
    classOf := fun gd => match gd with
      | .rent | .water | .electricity | .gas | .medicines | .financial => .exempt
      | _ => .standard }

def excise : Excise :=
  { rates := [
      { good := .spirits, name := "Акциз (водка, ликеро-водочные изделия)", perUnitNum := 300,
        statute := "Налоговый кодекс ст. 336 ч. 1 стр. 2-3 (литр 300 сомов)" },
      { good := .wine, name := "Акциз (вина)", perUnitNum := 100, statute := "ст. 336 ч. 1 стр. 5 (литр 100 сомов)" },
      { good := .beer, name := "Акциз (пиво)", perUnitNum := 30, statute := "ст. 336 ч. 1 стр. 8 (литр 30 сомов)" },
      { good := .cigarettes, name := "Акциз (сигареты)", perUnitNum := 3000, perUnitDen := 1000,
        statute := "ст. 336 ч. 1 стр. 12 1) (1000 штук, 2025: 3000 сомов)" }] }

/-- art. 368 (1) 1): sales tax rate on VAT-taxable revenue (company flag `trade` or `production`: 1 %, else 2 %). -/
def salesTaxBp (co : Company) : Int := if co.flags.contains "trade" || co.flags.contains "production" then 100 else 200

def salesTax (co : Company) : Charge :=
  let rev := isum (co.sales.map (·.net))
  charge .salesTax "Налог с продаж" rev id (fun x => divR .down (salesTaxBp co * pos x) BP) (event := "supplies")
    (bearer := .consumer) (statute := "Налоговый кодекс ст. 366 ч. 1, ст. 368 ч. 1 1) (1 % торговля/производство, 2 % прочие)")

def vatStatute : String := "Налоговый кодекс 2022 ст. 254 (12 %), ст. 255, 265, 267, 268, 270"

def families : List Family :=
  [{ name := "5111 НДС, 5112 налог с продаж, 5121 акцизы", covers := [.vat, .salesTax, .excise],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [vat.businessCharge g.company vatStatute, salesTax g.company] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent := []
def notes : List String := ["KG 5111/5112/5121: Tax Code 2022, official edition 36891 (amended to 31.07.2025)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then
    ["motor-fuel excise (art. 336 row 13) is per tonne: not modelled"] else [])
  ++ (if !g.consumption.isEmpty then ["sales tax inside household prices (art. 368) is not separated in the basket"] else [])
  ++ (if g.consumption.any (fun s => s.good == .health || s.good == .education) then
    ["VAT exemptions for medical and education services beyond art. 268 (2) and 282 not applied"] else [])

#guard vat.embedded { good := .food, amount := 11200 } == 1200
#guard vat.embedded { good := .electricity, amount := 11200 } == 0
#guard excise.duty { good := .spirits, amount := 600, quantity := 500, abvBp := 4000 } == 150
#guard excise.duty { good := .cigarettes, amount := 150, quantity := 20000 } == 60
#guard (salesTax { sales := [{ good := .other, net := 1000000 }], flags := ["trade"] }).due == 10000
#guard (salesTax { sales := [{ good := .other, net := 1000000 }] }).due == 20000

end KgGlobal.Consumption
