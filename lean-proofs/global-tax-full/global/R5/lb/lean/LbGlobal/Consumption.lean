import TaxKernel.Global2
import R5Common

/-!
# Lebanon 2025: value added tax (5111)

Law No 379 of 14/12/2001 (الضريبة على القيمة المضافة), article texts with their version dates from the Lebanese
University's legal informatics centre (legiliban.ul.edu.lb, law id 203155; pages saved in `law/legiliban_vat_art*.html`):
* art. 25 as amended by Law 64/2017 (version in force from 20/10/2017, no later version): "إن معدل الضريبة هو أحد عشرة
  بالمئة (11%)" (the surplus over 10 % on water, electricity and telecommunications is Treasury revenue: same rate);
* art. 16 as amended by Law 6/2020 (from 05/03/2020): exempt activities: medical services and hospitalisation (1),
  education (2), insurance (3), banking and financial services (4), shared passenger transport incl. taxis (6),
  sale of built property (9), residential lettings (10), farmers' supplies of crops (11), nurseries (12);
* art. 17 as amended by Law 144/2019 (from 31/07/2019): exempt goods: unprocessed agricultural food products (a),
  bread, flour, meat and fish, milk and dairy, rice, burghul, sugar, salt, vegetable oils, pasta, baby food (b),
  books, periodicals, newspapers (c), household gas (butane) (هـ), medicines and pharmaceutical products (ح), medical
  equipment (ط), precious metals (ي), and diesel (مادة المازوت).
Basket classes: food exempt (art. 17(a)-(b): other processed foods are taxable at 11 %, flagged), medicines, health,
education, insurance, financial, transport (shared passenger transport), rent (residential), books, newspapers, gas
(butane), diesel and heating oil (mazout) exempt; every other good 11 %. **Grade A** (dated article versions read).
The registration threshold (art. 36 as changed by Budget Law 324/2024) is not read: a company's sales are taxed
whatever the turnover.
-/

namespace LbGlobal
open TaxKernel TaxKernel.Global R5Common

def tva : Vat :=
  { name := "الضريبة على القيمة المضافة", standard := 1100,
    classOf := fun g => match g with
      | .food | .medicines | .health | .education | .insurance | .financial | .transport | .rent
      | .books | .newspapers | .gas | .diesel | .heatingOil => .exempt
      | _ => .standard }

/-!
## Internal consumption duty on alcohol and energy drinks (5121), pass 3h

2025 budget, Decree 56/2025 (the 2025 budget draft put in force; OG 11 of 13/03/2025, in force on publication;
legiliban law id 334856, `law/legiliban_budget2025_decree56.txt`):
* art. 44 (amends art. 2 of Legislative Decree 133 of 20/12/1933): internal consumption duty per litre of alcoholic
  liquids **produced in Lebanon**: beer LBP 45,000; arak 60,000; wine 60,000; champagne-type 90,000; cognac-type 390,000;
  whisky under 12 years 300,000, 12 years and over 390,000; other spirits 300,000. Imported products bear the duty in
  the customs tariff tables (not read).
* art. 48: "يفرض رسم استهلاك داخلي على مشروبات الطاقة قيمته 15.000 ل.ل. عن كل ليتر"; imported ones per the tariff tables.
Rules from 13/03/2025 (an undated line bears the window's share of the year); before that date the earlier rates are
not modelled. Lines: beer, wine, spirits (`"sub": "arak"` 60,000, `"whisky12"` 390,000, `"cognac"` 390,000, else
300,000), `nonAlcoholic` with `"sub": "energyDrinks"`; quantity in litres. Domestic origin assumed unless the line is
imported (then not computed). **Grade A** (statute text read).
-/

def perLitre (good : Good) (sub : String) (lbp : Int) (st : String) : ExciseRule :=
  { good, sub, name := "رسم الاستهلاك الداخلي", perUnitNum := lbp, imported := some false, validFrom := "2025-03-13",
    statute := "Decree 56/2025 (2025 budget) " ++ st }

def lbExcise : List ExciseRule :=
  [perLitre .spirits "arak" 60000 "art. 44 (arak LBP 60,000 a litre)",
   perLitre .spirits "whisky12" 390000 "art. 44 (whisky 12 years and over LBP 390,000 a litre)",
   perLitre .spirits "cognac" 390000 "art. 44 (cognac-type LBP 390,000 a litre)",
   perLitre .spirits "" 300000 "art. 44 (other spirits and whisky under 12 years LBP 300,000 a litre)",
   perLitre .beer "" 45000 "art. 44 (beer LBP 45,000 a litre)",
   perLitre .wine "" 60000 "art. 44 (wine LBP 60,000 a litre)",
   perLitre .nonAlcoholic "energyDrinks" 15000 "art. 48 (energy drinks LBP 15,000 a litre)"]

def consumption : Family :=
  { name := "5111 الضريبة على القيمة المضافة, 5121 رسم الاستهلاك الداخلي", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [tva.basketCharge g.consumption "Law 379/2001 art. 25 (11 %, Law 64/2017), 16 (Law 6/2020), 17 (Law 144/2019)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
        [tva.businessCharge g.company "Law 379/2001 art. 25 (11 %); deduction of input tax"] else [])
      ++ exciseRuleCharges lbExcise g (firstOnly := true) }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then
    ["VAT: food taken as exempt (art. 17(a)-(b) basic foods); processed foods outside that list are taxable at 11 %"] else [])
  ++ (if g.consumption.any (·.good == .transport) then
    ["VAT: transport taken as shared passenger transport (art. 16(6)); other transport services are taxable"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic) then
    ["consumption duty: rates of Decree 56/2025 from 13/03/2025 only (earlier 2025 rates not modelled); imported products (customs tariff tables) not computed; lines need quantity in litres"] else [])
  ++ (if g.entity == .company then ["VAT registration threshold (art. 36, Budget Law 324/2024) not read: no threshold applied"] else [])

#guard tva.embedded { good := .clothing, amount := 11100 } == 1100
#guard tva.embedded { good := .electricity, amount := 1110 } == 110
#guard tva.embedded { good := .food, amount := 5000 } == 0
#guard tva.embedded { good := .diesel, amount := 5000 } == 0

#guard (perLitre .beer "" 45000 "").dutyOn { good := .beer, amount := 1000, quantity := 2000 } {} == 90000
#guard (perLitre .nonAlcoholic "energyDrinks" 15000 "").dutyOn { good := .nonAlcoholic, amount := 1000, quantity := 500 } {} == 7500

end LbGlobal
