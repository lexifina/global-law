import TaxKernel.Global
import R5Common

/-!
# Yemen 2025: general sales tax (5111)

Law No 19 of 2001 on the General Sales Tax and its amendments, consolidated by the Tax Authority (booklet "قانون رقم
(19) لسنة 2001م بشأن الضريبة العامة على المبيعات وتعديلاته", 41 pp., created 2021-01-26; tax.gov.ye
`images/portfolio/tax/pdf/salestax.pdf`, Wayback 2022-06-25; `law/ye_gst_law19_2001_consolidated.pdf`), read by Arabic OCR
with the figures checked on the page images (pp. 7-8, 25, 39-41):
* art. 3(a): the tax is imposed on the value of sales of taxable goods and services and on all imports; art. 3(b): the
  annexed tables (Law 42/2005) are part of the law: Table 1 exempt services, Table 2 zero rate, Table 3 specific rates.
* art. 4(a): "تحتسب الضريبة بنسبة عامة بواقع (5%) خمسة في المائة من قيمة مبيعات السلع والخدمات"; art. 4(b): petrol,
  diesel (السولار), kerosene, mazout and butane gas "بواقع (5%) من سعر البيع للمستهلك" (on the consumer price, i.e. a
  tax-inclusive base); art. 4(c): Table 2 at zero.
* art. 40(a): Table 1 services exempt: financial and banking, insurance, health, education, non-profit bodies, internal
  land transport of goods and passengers, renting land and buildings for private housing, water (except bottled),
  sewerage and electricity, cleaning, monument restoration, pilgrimage agencies, one-star hotels; art. 40(b) (as replaced
  by Law 7/2020): goods exempt: wheat and wheat flour, rice, medicines, raw gold, personal luggage, ...
* Table 2 (zero): exports, international transport services, children's milk.
* Table 3: cigarettes 90 % of the consumer price; cigars 90 %; qat 20 % of the consumer price; arms 90 %; gold 2 / 3 %;
  mobile telephone services 10 %; international telephone services 10 %.
Basket classes: financial, insurance, health, education, transport, rent, water, electricity, medicines exempt;
petrol, diesel, heating oil, gas 5 % of the amount paid; cigarettes 90 % of the amount paid; other tobacco (cigars)
90 % and communication 10 % on the value before tax; every other good 5 %.
The booklet is the Sana'a Tax Authority's; the Aden government applies the same Law 19/2001 (amendments after 2015 may
differ between the two administrations: not checked). **Grade A** (statute text read).
-/

namespace YeGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "الضريبة العامة على المبيعات", standard := 500, reduced := 9000, reduced2 := 1000,
    classOf := fun g => match g with
      | .financial | .insurance | .health | .education | .transport | .rent | .water | .electricity | .medicines => .exempt
      | .petrol | .diesel | .heatingOil | .gas | .cigarettes => .exempt   -- charged on the consumer price below
      | .tobaccoOther => .reduced
      | .communication => .reduced2
      | _ => .standard }

/-- art. 4(b) and Table 3 item 1: a percentage of the consumer price (the amount paid). -/
def retailBp (g : Good) : Int :=
  if g == .petrol || g == .diesel || g == .heatingOil || g == .gas then 500
  else if g == .cigarettes then 9000 else 0

def retailCharges (xs : List Spend) : List Charge :=
  [(500, "art. 4(b): petrol, diesel, kerosene, mazout, butane 5 % of the consumer price"),
   (9000, "art. 4(a), Table 3 item 1: cigarettes 90 % of the consumer price")].filterMap fun (bp, st) =>
    let amt := isum ((xs.filter fun s => retailBp s.good == bp).map (·.amount))
    if amt == 0 then none else
    some (charge .vat "الضريبة العامة على المبيعات (سعر البيع للمستهلك)" amt id (fun b => divR .down (b * bp) BP)
      (event := "basket") (bearer := .consumer) (statute := "Law 19/2001 " ++ st))

def consumptionPre3q : Family :=
  { name := "5111 الضريبة العامة على المبيعات", covers := [.vat],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [vat.basketCharge g.consumption "Law 19/2001 art. 4(a) (5 %), art. 40 + Table 1 (exempt), Table 3 (cigars 90 %, telephone services 10 %)"]
        ++ retailCharges g.consumption)
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
        [vat.businessCharge g.company "Law 19/2001 art. 4(a) (5 %); input tax deduction art. 14"] else []) }

def consumptionUnsupportedPre3q (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then
    ["sales tax: food taken at 5 %; wheat, flour and rice are exempt (art. 40(b)), children's milk zero-rated (Table 2)"] else [])
  ++ (if g.consumption.any (·.good == .hotels) then ["sales tax: hotels taken at 5 %; one-star hotels are exempt (Table 1 item 12)"] else [])
  ++ (if g.entity == .company then ["sales tax registration threshold (set by the Executive Regulations) not applied"] else [])

#guard vat.embedded { good := .clothing, amount := 10500 } == 500
#guard vat.embedded { good := .communication, amount := 1100 } == 100
#guard vat.embedded { good := .food, amount := 10500 } == 500
#guard (retailCharges [{ good := .petrol, amount := 10000 }, { good := .cigarettes, amount := 1000 }]).map (·.due) == [500, 900]


/-- Pass 3q year-in-force audit: grade C. 5111 general sales tax grade C (year-in-force audit, pass 3q): the GST Law 19/2001 consolidation booklet of 2021 (Wayback 2022) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`consumptionPre3q`) for a later re-cite;
it is not in the model. -/
def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if (consumptionPre3q.run [] g []).isEmpty then [] else ["5111 general sales tax grade C (year-in-force audit, pass 3q): the GST Law 19/2001 consolidation booklet of 2021 (Wayback 2022) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ consumptionUnsupportedPre3q g

end YeGlobal
