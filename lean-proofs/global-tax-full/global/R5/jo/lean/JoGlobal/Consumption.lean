import TaxKernel.Global
import R5Common

/-!
# Jordan 2025: general sales tax (5111)

General Sales Tax Law No 6 of 1994 and its amendments, ISTD official English text "The General Sales Tax Law and its
Amendments 2023" (istd.gov.jo, Wayback 2025-08-05; `law/jo_gst_law_en_2023.txt`):
* art. 6(a): "A general tax shall be charged under this Law at the rate of 16 per cent on the supply or importation of
  goods or services"; art. 6(b): Table (1) goods also bear the special tax (art. 4(c): "without prejudice to" the
  general tax), rates by regulation (5121, not modelled here).
* art. 7(a): zero rate for Table (2) goods; art. 7(b): Table (3) goods and services exempt; art. 3(b)-(c): the Council
  of Ministers issues and amends Tables (2) and (3).
Tables as published by the ISTD in English ("salestax_tables_8-2020", Wayback 2024-05-02; `law/jo_gst_tables_en_2020.txt`):
* Table (2) zero rate: fresh meat and fish, petroleum oils and petroleum gases (petrol, diesel, heating oil, LPG),
  printed books, newspapers and periodicals.
* Table (3) exempt goods: poultry, milk, eggs, pulses, tea, wheat, rice, flour, olive oil, sugar, bread, water (except
  bottles of 5 l or less), electricity, fresh vegetables; exempt services: electricity and water supply, land, water and
  air transport, financial intermediation, life, medical and accident insurance and reinsurance, real estate
  activities and dwellings, education, health, meals of popular (unclassified) restaurants.
* Rate tables: medicines (chapter 30) 4 %; other foods at 2, 4, 5 or 10 % by item.
* Council of Ministers decision 9366 of 31/5/2020: hotels and tourist restaurants 8 %.
Basket classes: food, water, electricity, rent, financial, insurance, education, health, transport exempt (staple-food
reading: see unsupported); petrol, diesel, heating oil, gas, books, newspapers zero; medicines 4 %; hotels and
restaurants 8 %; every other good 16 %.
**Grade B**: the 16 % is the law's own text (A); the zero, exempt and reduced lists are the ISTD's 2020 tables and a
2020 Cabinet decision, not checked against later decisions.
-/

namespace JoGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "الضريبة العامة على المبيعات", standard := 1600, reduced := 800, superReduced := 400,
    classOf := fun g => match g with
      | .food | .water | .electricity | .rent | .financial | .insurance | .education | .health | .transport => .exempt
      | .petrol | .diesel | .heatingOil | .gas | .books | .newspapers => .zero
      | .medicines => .superReduced
      | .hotels | .restaurants => .reduced
      | _ => .standard }

def consumption : Family :=
  { name := "5111 الضريبة العامة على المبيعات", covers := [.vat],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [vat.basketCharge g.consumption "General Sales Tax Law 6/1994 art. 6(a) (16 %), art. 7 + Tables (2)/(3) (ISTD 2020); medicines 4 %, hotels and tourist restaurants 8 % (CoM decision 9366/2020)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
        [vat.businessCharge g.company "General Sales Tax Law 6/1994 art. 6(a) (16 %); input tax deduction"] else []) }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then
    ["sales tax: food taken as exempt or zero-rated staples (Table 3 / Table 2); other foods are 2, 4, 5 or 10 % by tariff item"] else [])
  ++ (if g.consumption.any (·.good == .restaurants) then
    ["sales tax: restaurants taken at 8 % (tourist restaurants); popular restaurants are exempt (Table 3 services item 26)"] else [])
  ++ (if g.consumption.any (·.good == .insurance) then
    ["sales tax: insurance taken as exempt (life, medical, accident, reinsurance); other insurance bears 16 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .heatingOil || s.good == .cigarettes
        || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic || s.good == .communication) then
    ["special sales tax (Table 1: fuels, tobacco, alcohol, soft drinks, mobile services; art. 6(b)) not modelled"] else [])
  ++ (if g.entity == .company then ["sales tax registration threshold (Regulation 81/2000) not applied"] else [])

#guard vat.embedded { good := .clothing, amount := 11600 } == 1600
#guard vat.embedded { good := .medicines, amount := 10400 } == 400
#guard vat.embedded { good := .restaurants, amount := 10800 } == 800
#guard vat.embedded { good := .food, amount := 5000 } == 0

end JoGlobal
