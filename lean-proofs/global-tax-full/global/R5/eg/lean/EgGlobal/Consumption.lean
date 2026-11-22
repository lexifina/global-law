import TaxKernel.Global2
import R5Common

/-!
# Egypt 2025: value added tax (5111) and table tax on cigarettes and soft drinks (5121)

Law No 67 of 2016 (قانون الضريبة على القيمة المضافة), Official Gazette 35 bis (ج) of 7/9/2016, with the amending laws
the Egyptian Tax Authority lists for it: Law 13/2020, Law 3/2022 (OG 3 bis (هـ) of 27/1/2022), Law 177/2023 (OG 44 bis
(أ) of 4/11/2023), Law 157/2025 (OG 29 (cont.) of 17/7/2025, in force 18/7/2025). Gazette scans from eta.gov.eg
(`sites/default/files/2024-03/vat-law_no.*.pdf`, `2025-07/vat-law_no.157.of_.2025.pdf`, Wayback 2024-10-15 and
2025-12-12), read by Arabic OCR (tesseract `ara`, user install) with the key digits checked on the page images
(`law/eg_vat-law_no.*.ocr.txt`):
* art. 2: VAT on goods and services incl. those in the annexed Table, at every stage, "إلا ما استثنى بنص خاص".
* art. 3: "يكون السعر العام للضريبة على السلع والخدمات (13%) عن العام المالى 2016/2017 و(14%) اعتباراً من العام
  المالى 2017/2018"; machinery and equipment for production 5 % (not in the household basket); exports 0 %.
* art. 12: the Table tax (ضريبة الجدول) is due in addition to art. 3 VAT "unless the Table states otherwise": Table
  section أولاً ("table tax only") holds tobacco products, petroleum products (petrol, kerosene, solar/diesel, fuel oil),
  edible oils, crackers and pastry, crisps, fertilisers, AC inter-governorate transport, media production (and from
  18/7/2025 crude oil 10 %, item 16, Law 157/2025 art. 5; item 9 construction contracting cancelled by its art. 6, so
  contracting bears 14 % VAT from that day); section ثانياً (table tax + VAT) holds soft drinks, beer, alcohol,
  cosmetics, large appliances, cars, mobile telecommunications. So petrol, diesel, heating oil and tobacco carry no VAT.
* Annexed list of exempt goods and services (items as replaced by Law 3/2022 art. 3 and Law 157/2025 art. 4; items
  18 crude oil and 48 news agencies cancelled by Law 157/2025 art. 6): dairy and baby food (1-2), eggs (3), tea, sugar,
  coffee (4), milling products (5), bread (6), pasta (7), meat, poultry, fish (8-11), agricultural produce (12), local
  processed vegetables and fruit (14), pulses, grains, salt, spices (15), food sold directly by non-tourist restaurants
  and shops meeting the Minister's conditions (16), sewerage and water except bottled water (17), natural gas and butane
  (19), electricity (22), newspapers, books, periodicals (26), sale and lease of land and buildings (28), banking,
  exchange, non-bank financial services (33-36), insurance and reinsurance (37), education, training and research (38),
  health services except cosmetic (39), land passenger transport incl. taxis except tourist, AC inter-governorate and
  private-car hire (40), non-tourist water and air passenger transport (41), medicines (55(a), Law 3/2022).
Basket classes: food, water, electricity, gas, rent, financial, insurance, education, health, transport, medicines,
books, newspapers exempt; petrol, diesel, heating oil, cigarettes, other tobacco outside VAT (table tax only); every
other good 14 %. **Grade A** (Gazette text read, amendment chain from the ETA's list of VAT laws).

## Table tax (5121), pass 3h
* Cigarettes, Table أولاً item 1/ب/3 (per 20 cigarettes and other packs pro rata), page images checked:
  - Law 177/2023 art. 1 (to 17/7/2025): "(50%) من سعر بيع المستهلك النهائى بالإضافة إلى": 450 piastres a pack (local
    factories, consumer price ≤ EGP 31); 700 pt (local over 31 to 45, or imported ≤ 45); 750 pt (local or imported over
    45). Note (3): both price limits rise 12 % a year for five years from the law's start (4/11/2023): from 5/11/2024
    the limits are 34.72 and 50.40.
  - Law 157/2025 art. 1 (from 18/7/2025): 50 % plus 500 pt (local ≤ 48), 750 pt (local over 48 to 69, or imported ≤ 69),
    800 pt (local or imported over 69); note (3): limits rise 12 % a year for three years "تبدأ من 5 نوفمبر 2025":
    read as the next yearly step of the same cycle, so from 5/11/2025 the limits are 53.76 and 77.28.
  - Notes (1)-(2): the base is the final consumer price including all taxes (the amount paid); the declared or
    ministerial price, if higher, is the minimum base (not modelled).
  Pack price = amount / (quantity / 20); a line without `quantity` bears the 50 % only (unsupported note). An undated
  line is split by days: 198 days at the 2023 table, 110 days at the 2025 table with the 2025 limits, 57 days with
  the raised limits. `imported` from the line (`"imported": true` or `importedGoods`).
* Soft drinks, Table ثانياً item 1 (table tax and VAT): "مياه غازية صودا أو مياه غازية معطرة ومحلاة ... القيمة (8%)",
  note (1): value = final consumer price; non-alcoholic beer item 2 the same. Lines with `"sub": "softDrinks"`.
Not modelled: petroleum products (per-litre amounts; the 2016 OCR digits are unreadable and later amounts not read),
other tobacco (honey tobacco 190 % / 225 %, pipe tobacco per kg), alcohol (Law 157/2025 per hectolitre), cosmetics,
appliances, cars, mobile services.
-/

namespace EgGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "الضريبة على القيمة المضافة", standard := 1400,
    classOf := fun g => match g with
      | .food | .water | .electricity | .gas | .rent | .financial | .insurance | .education | .health | .transport
      | .medicines | .books | .newspapers => .exempt
      | .petrol | .diesel | .heatingOil | .cigarettes | .tobaccoOther => .exempt
      | _ => .standard }

/-! ### Table tax on cigarettes -/

/-- Period of the 2025 year by days before the date: 0 = Law 177/2023 (to 17/7), 1 = Law 157/2025 (18/7-4/11),
2 = Law 157/2025 with the limits raised on 5/11/2025. -/
def cigPeriod (d : Nat) : Nat := if d < 198 then 0 else if d < 308 then 1 else 2

/-- (lower limit, upper limit) of the consumer price of a pack, piastres. -/
def cigLimits : Nat → Int × Int
  | 0 => (3472, 5040) | 1 => (4800, 6900) | _ => (5376, 7728)

/-- (local ≤ lower, middle band, over the upper limit) amounts a pack, piastres. -/
def cigAmounts : Nat → Int × Int × Int
  | 0 => (450, 700, 750) | _ => (500, 750, 800)

/-- Amount per pack (piastres) for a pack price (piastres) in a period. -/
def cigPerPack (p : Nat) (packPt : Int) (imported : Bool) : Int :=
  let (lo, hi) := cigLimits p
  let (a1, a2, a3) := cigAmounts p
  if !imported && packPt ≤ lo then a1 else if packPt ≤ hi then a2 else a3

/-- Table tax on one line: 50 % of the amount paid + packs × the amount per pack (piastres → pounds, down). -/
def cigTax (amount quantity : Int) (imported : Bool) (day : Option Nat) : Int :=
  let adv := divR .down (pos amount * 5000) BP
  if quantity ≤ 0 then adv else
  let packPt := divR .down (pos amount * 100 * 20000) quantity
  let specPt := match day with
    | some d => divR .down (quantity * cigPerPack (cigPeriod d) packPt imported) 20000
    | none => divR .down (quantity * (cigPerPack 0 packPt imported * 198 + cigPerPack 1 packPt imported * 110
        + cigPerPack 2 packPt imported * 57)) (20000 * 365)
  adv + divR .down specPt 100

def cigStatute : String :=
  "VAT Law 67/2016 art. 12, Table أولاً 1/ب/3 as replaced by Law 177/2023 art. 1 (to 17/7/2025) and Law 157/2025 art. 1 (from 18/7/2025): 50 % of the consumer price + 450-800 piastres a pack by price band"

def cigCharges (g : CanonGlobal) : List Charge :=
  ((consumptionX g).zipIdx.filter fun ((s, _), _) => s.good == .cigarettes).map fun ((s, x), i) =>
    charge .excise "ضريبة الجدول (السجائر)" s.amount id (fun _ => cigTax s.amount s.quantity x.imported (dayOfYear? g.year x.date))
      (event := s!"cigarettes {i + 1}") (bearer := .consumer) (statute := cigStatute)

/-! ### Table tax on soft drinks -/

def softDrinks : ExciseRule :=
  { good := .nonAlcoholic, sub := "softDrinks", name := "ضريبة الجدول (المياه الغازية)", adValoremBp := 800,
    valueBase := .retail, statute := "VAT Law 67/2016 art. 12, Table ثانياً item 1 (8 % of the final consumer price, notes (1)-(2))" }

def consumption : Family :=
  { name := "5111 الضريبة على القيمة المضافة, 5121 ضريبة الجدول", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [vat.basketCharge g.consumption "Law 67/2016 art. 2-3 (14 %), art. 12 + Table (table-tax-only goods), exempt list (Law 3/2022, 157/2025)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
        [vat.businessCharge g.company "Law 67/2016 art. 3 (14 %); input tax deduction"] else [])
      ++ cigCharges g
      ++ exciseRuleCharges [softDrinks] g }

def isTableOnly (g : Good) : Bool :=
  g == .petrol || g == .diesel || g == .heatingOil || g == .cigarettes || g == .tobaccoOther

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then
    ["VAT: food taken as exempt (exempt-list items 1-16); other processed foods are 14 %, edible oils and pastry are table-tax-only"] else [])
  ++ (if g.consumption.any (·.good == .restaurants) then
    ["VAT: restaurants taken at 14 %; non-tourist eateries meeting the Minister's conditions are exempt (item 16)"] else [])
  ++ (if g.consumption.any (·.good == .transport) then
    ["VAT: transport taken as exempt land/water/air passenger transport (items 40-41); tourist and AC inter-governorate transport are not"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .heatingOil || s.good == .tobaccoOther) then
    ["table tax (5121) on petroleum products and tobacco other than cigarettes not modelled; those goods carry no VAT (Table section أولاً)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes && s.quantity ≤ 0) then
    ["cigarette table tax: a line without quantity (sticks) bears the 50 % only; the amount per pack needs the pack price"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes) then
    ["cigarette table tax: the declared or ministerial minimum base and the band-limit step on 5/11/2025 (read as the next yearly 12 % step) taken as stated"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .communication) then
    ["table tax (Table section ثانياً: alcohol, mobile telecoms) not modelled; VAT taken on the amount paid"] else [])
  ++ (if g.consumption.any (fun s => s.good == .nonAlcoholic) then
    ["soft-drinks table tax (8 %) only on lines with sub softDrinks"] else [])
  ++ (if g.entity == .company then ["VAT registration threshold (art. 16) not applied"] else [])

#guard vat.embedded { good := .clothing, amount := 11400 } == 1400
#guard vat.embedded { good := .food, amount := 5000 } == 0
#guard vat.embedded { good := .petrol, amount := 5000 } == 0
#guard vat.embedded { good := .communication, amount := 1140 } == 140
-- 10 packs at EGP 40 (local): 2023 table middle band 7.00, 2025 table lower band 5.00
#guard cigTax 400 200000 false (some 10) == 200 + 70
#guard cigTax 400 200000 false (some 200) == 200 + 50
-- undated: (700 × 198 + 500 × 110 + 500 × 57) / 365 = 608.4 pt a pack → 10 packs EGP 60
#guard cigTax 400 200000 false none == 260
-- 10 imported packs at EGP 60: 2023 upper band 7.50, 2025 middle band 7.50
#guard cigTax 600 200000 true (some 250) == 300 + 75

end EgGlobal
