import FmGlobal.Pit

/-!
# Micronesia (Federated States) 2025: Pohnpei State sales tax (5112) and national import duties (5120)

No VAT: the FSM has no national tax on general sales; the states levy sales taxes on the first commercial sale of
goods. Pohnpei (the capital Palikir) is modelled; Chuuk, Kosrae and Yap have their own codes (not modelled).

**Pohnpei sales tax.** Code of the State of Pohnpei, 2012 edition (advance copy, fsmlaw.org
`pohnpei/code/pdf/pohnpei state 2012 code.pdf`; `fm/law/fm_pohnpei_code2012_t12ch2.txt`, sha256 in `SHA256SUMS`),
Title 12 ch. 2 (S.L. No. 4L-35-97 as amended):
* **12 PC 2-102**: "levied on the first commercial sale in Pohnpei State a sale tax … on the sale price": (1) tobacco
  and alcohol products 25 %; (2) fuels (gasoline, diesel, kerosene, LP gas) 2 %; (3) motor vehicles 7 %; (4) food and
  foodstuffs (incl. non-alcoholic beverages, 2-101 (2)) 2 %; (5) all other merchandise 5 %.
* **2-101 (4)**: sale price "exclusive of taxes applicable under this title". Services are not "merchandise"
  (2-101 (3)): not taxed. In the basket the tax is taken inside the household's price (rate / (1 + rate)); the first
  commercial sale is usually the importer's or wholesaler's, so this overstates the tax in a retail price.

**National import duties.** FSM Code (2014 edition, fsmlaw.org `fsm/code/title54/T54_Ch02.htm`;
`fm/law/fm_code2014_t54ch2.txt`), Title 54 **§ 221** (PL 9-139 § 9): cigarettes 25 % ad valorem; other tobacco 50 %;
soft drinks and non-alcoholic beverages 25 %; beer 25 %; distilled spirits $10 per gallon; wine 25 %; foodstuffs 3 %
(fresh citrus 25 %); gasoline and diesel 5 cents per gallon; all other imports 4 %. Booked as 5120 (customs duties,
OECD 5123) on the goods taken as imported: the ad valorem duties on the value before both taxes
(price / ((1 + duty) (1 + sales tax))), the specific ones per litre (1 gallon = 3.785411784 l). The general 3 % and 4 %
duties on all other imports are not modelled.
-/

namespace FmGlobal.Consumption
open TaxKernel TaxKernel.Global

/-- Pohnpei sales tax rate by good, bp (12 PC 2-102). -/
def pnBp (g : Good) : Int :=
  match g with
  | .beer | .wine | .spirits | .cigarettes | .tobaccoOther => 2500
  | .petrol | .diesel | .heatingOil | .gas => 200
  | .food | .nonAlcoholic => 200
  | .clothing | .medicines | .books | .newspapers | .recreation | .other => 500
  | _ => 0

/-- National import duty, ad valorem part, bp (FSMC 54 § 221). -/
def dutyBp (g : Good) : Int :=
  match g with
  | .cigarettes | .beer | .wine | .nonAlcoholic => 2500
  | .tobaccoOther => 5000
  | _ => 0

/-- Specific import duty per litre as a fraction (num, den): spirits $10 per gallon, fuels 5 cents per gallon. -/
def dutySpecific (g : Good) : Int × Int :=
  match g with
  | .spirits => (10000000, 3785412)
  | .petrol | .diesel => (50000, 3785412)
  | _ => (0, 1)

def salesTaxIn (s : Spend) : Int := divR .down (pos s.amount * pnBp s.good) (BP + pnBp s.good)

def dutyIn (s : Spend) : Int :=
  let (n, d) := dutySpecific s.good
  let spec := divR .down (s.quantity * n) (d * 1000)
  let netSt := divR .down (pos s.amount * BP) (BP + pnBp s.good)
  let adv := divR .down (netSt * dutyBp s.good) (BP + dutyBp s.good)
  spec + adv

def basketCharges (xs : List Spend) : List Charge :=
  ((xs.filter fun s => pnBp s.good > 0).map fun s =>
    charge .salesTax "Pohnpei State sales tax" s.amount id (fun _ => salesTaxIn s) (event := s.good.name)
      (level := .state) (bearer := .consumer)
      (statute := s!"Pohnpei Code 2012, 12 PC 2-102 ({pnBp s.good / 100} % of the sale price)"))
  ++ ((xs.filter fun s => dutyBp s.good > 0 || (dutySpecific s.good).1 > 0).map fun s =>
    charge .goodsOther "FSM import duty" s.amount id (fun _ => dutyIn s) (event := s.good.name) (bearer := .consumer)
      (statute := "FSM Code (2014) Title 54 § 221 (1)-(2), (4)-(7), (9)"))

def businessCharges (g : CanonGlobal) : List Charge :=
  let sales := g.company.sales.filter fun s => !s.exported && pnBp s.good > 0
  if g.entity == .company && !sales.isEmpty then
    [charge .salesTax "Pohnpei State sales tax" (isum (sales.map (·.net))) id
      (fun _ => isum (sales.map fun s => divR .down (pos s.net * pnBp s.good) BP)) (event := "supplies") (level := .state)
      (bearer := .consumer) (statute := "Pohnpei Code 2012, 12 PC 2-102 (on the first commercial sale of merchandise in Pohnpei)")]
  else []

/-- Session 11: kept for a re-cite; not run (year-in-force audit, grade C). -/
def familiesPre11 : List Family :=
  [{ name := "5112 Pohnpei sales tax; 5120 national import duties", covers := [.salesTax, .goodsOther],
     run := fun _ g _ => basketCharges g.consumption ++ businessCharges g }]

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .vat, why := "no value added tax: FSM Code Title 54 levies income, gross revenue and import taxes only; sales taxes are state taxes (Pohnpei Code 2012, 12 PC 2-102)" }]

def notes : List String := ["FM 5112, 5120: grade C (session 11 year-in-force audit); sources were Pohnpei Code 2012 Title 12 ch. 2 (Pohnpei taken for the FSM); 5120: FSM Code 2014 Title 54 § 221"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty || g.entity == .company then ["5112 Pohnpei sales tax and 5120 FSM import duties not modelled (session 11 year-in-force audit: Pohnpei Code 2012 edition (advance copy) and FSM Code 2014 codification, later public laws not read; no 2025 version reached: grade C)"] else []) ++
  (if !g.consumption.isEmpty then ["state sales taxes: Pohnpei modelled; Chuuk, Kosrae and Yap codes not read; the tax is due on the first commercial sale (importer or wholesaler) and is taken inside the household's retail price, which overstates it"] else [])
  ++ (if g.consumption.any (fun s => s.good == .recreation || s.good == .electricity || s.good == .water || s.good == .restaurants) then ["recreation taken as merchandise (5 %); electricity, tap water and restaurant meals taken as services (not merchandise under 12 PC 2-101 (3))"] else [])
  ++ (if !g.consumption.isEmpty then ["import duties applied as if every taxed good were imported; the 3 % (foodstuffs) and 4 % (all other imports) duties of FSMC 54 § 221 (8), (11) not modelled; excise-type duties of Chuuk, Kosrae, Yap not modelled"] else [])

#guard salesTaxIn { good := .clothing, amount := 1050 } == 50
#guard salesTaxIn { good := .beer, amount := 1250 } == 250
#guard salesTaxIn { good := .rent, amount := 1000 } == 0
-- 1 562.5 of cigarettes: before the 25 % sales tax 1 250, before the 25 % duty 1 000, duty 250
#guard dutyIn { good := .cigarettes, amount := 1562 } == 249
-- 10 litres of spirits: $10 per gallon = 26.4 dollars
#guard dutyIn { good := .spirits, amount := 400, quantity := 10000 } == 26
#guard absent.length == 1

end FmGlobal.Consumption
