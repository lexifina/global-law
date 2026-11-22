import TaxKernel.Global
import R5Common

/-!
# Algeria 2025: taxe sur la valeur ajoutée (5111)

Code des taxes sur le chiffre d'affaires (قانون الرسوم على رقم الأعمال), DGI 2025 Arabic edition (mfdgi.gov.dz dropfiles
category 776, file 2521, Wayback 2025-02-22; saved `law/dgi_ctca_2025_ar.pdf`). The text layer's digits are font-shifted,
so the rates and item numbers were read on the page images (pp. 7-9, 13-16). Footnotes give each article's amending
finance laws (art. 21 last LF 2017 art. 26; art. 23 last LF 2024 art. 35; art. 9 last LF 2024 art. 34):
* art. 21: "يحصل الرسم على القيمة المضافة بالمعدل العادي 19%".
* art. 23: reduced rate 9 % on (1) the listed goods (live animals, fresh vegetables, pulses, cereals, rice, pasta,
  couscous, olive oil, durum flour products, pharmaceutical materials of ch. 30 fixed by regulation, books and printed
  matter 49.01, newspaper paper ...), (2) "عمليات البيع المتعلقة بتوزيع الكهرباء والغاز الطبيعي فيما يخص استهلاكا يقل
  عن 250 كيلواط/ساعي بالنسبة للكهرباء و 2500 وحدة حرارية لكل ثلاثة أشهر بالنسبة للغاز الطبيعي", (4) newspapers and
  periodicals, (8) social-housing rents, (9) medical professions, (16) shows, (17) heavy fuel oil, butane, propane and
  LPG fuel, (19) education services of State-approved establishments, (21) rail passenger transport, (27) digital
  books, (33) supply of drinking water to households.
* art. 9 exemptions: (1) cereals for flour, ordinary and superior flour, semolina, bread; (2) milk, cream, infant milk;
  (3) pharmaceutical products in the national nomenclature of medicines; (15) personal insurance contracts; (16) bank
  loans to households for a dwelling; (19)-(20) reinsurance, natural-catastrophe insurance.
Basket classes: medicines exempt (9-3); insurance exempt (9-15, personal insurance); food 9 % (art. 23 list; bread,
flour, milk exempt and other foods 19 %: flagged); water, gas, heating oil, health, education, books, newspapers 9 %;
electricity 9 % on the first 1,000 kWh a year (250 kWh a quarter, an even consumption assumed) and 19 % beyond when a
quantity is given; rent outside VAT (flagged: a private dwelling let is not taken as a taxable operation; social-housing
rents 9 %); every other good 19 % (incl. petrol, diesel, transport other than rail, banking, communication).
**Grade A** (official 2025 code edition read on the page images).
-/

namespace DzGlobal
open TaxKernel TaxKernel.Global R5Common

def tva : Vat :=
  { name := "الرسم على القيمة المضافة", standard := 1900, reduced := 900,
    classOf := fun g => match g with
      | .medicines | .insurance | .rent => .exempt
      | .food | .water | .gas | .heatingOil | .health | .education | .books | .newspapers | .electricity => .reduced
      | _ => .standard }

/-- 250 kWh a quarter = 1,000 kWh a year, in thousandths of a kWh (`Spend.quantity`). -/
def elecCap : Int := 1000 * 1000

/-- Split an electricity spend with a quantity above the yearly 1,000 kWh into the 9 % part and the rest, the rest
carried as `.other` (19 %); every other spend unchanged. -/
def splitElec (s : Spend) : List Spend :=
  if s.good == .electricity && s.quantity > elecCap then
    let low := divR .down (s.amount * elecCap) s.quantity
    [{ s with amount := low, quantity := elecCap }, { good := .other, amount := s.amount - low }]
  else [s]

def basket (xs : List Spend) : List Spend := xs.flatMap splitElec

def consumption : Family :=
  { name := "5111 الرسم على القيمة المضافة", covers := [.vat],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [tva.basketCharge (basket g.consumption) "CTCA art. 21 (19 %), 23 (9 %: list, electricity to 250 kWh/quarter), 9 (exemptions); DGI edition 2025"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
        [tva.businessCharge g.company "CTCA art. 21 (19 %); deduction art. 29 ff."] else []) }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then
    ["TVA: food taken at 9 % (art. 23 list); bread, flour, semolina and milk are exempt (art. 9), foods outside the list 19 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity && s.quantity == 0) then
    ["TVA on electricity: no kWh given, all taken within 250 kWh a quarter (9 %)"] else [])
  ++ (if g.consumption.any (·.good == .gas) then
    ["TVA on gas: taken at 9 % (art. 23-2 natural gas to 2,500 thermies a quarter, 23-17 butane/propane); natural gas above that is 19 %"] else [])
  ++ (if g.consumption.any (·.good == .rent) then
    ["TVA on rent: a private dwelling let taken as outside VAT; social-housing rents are 9 % (art. 23-8)"] else [])
  ++ (if g.consumption.any (·.good == .transport) then
    ["TVA on transport taken at 19 %; rail passenger transport is 9 % (art. 23-21)"] else [])
  ++ (if g.consumption.any (·.good == .insurance) then
    ["TVA: insurance taken as exempt personal insurance (art. 9-15); other insurance is taxable"] else [])

#guard tva.embedded { good := .clothing, amount := 11900 } == 1900
#guard tva.embedded { good := .food, amount := 10900 } == 900
#guard tva.embedded { good := .medicines, amount := 5000 } == 0
-- 2,000 kWh for 2,000: half (1,000 kWh) at 9 %, the other half at 19 %
#guard tva.basket (basket [{ good := .electricity, amount := 2000, quantity := 2000000 }]) == 82 + 159
#guard tva.basket (basket [{ good := .electricity, amount := 1090, quantity := 1000000 }]) == 90

end DzGlobal
