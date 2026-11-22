import TaxKernel.Global2

/-!
# Qatar 2025: no VAT (5111, cited absence); excise tax (5121)

* VAT: Qatar has enacted no value added tax law. The Ministry of Justice legislation database (Al Meezan, the source of
  `law/qa_excise_25_2018.json` and of the 1.x model's Income Tax Law 24/2018 and Social Insurance Law 1/2022) holds the
  Excise Tax Law 25/2018 and the Income Tax Law 24/2018 as Qatar's tax acts; no VAT act (searched by the R5 builder
  and the registry agent, 2026-11-21). The GCC Common VAT Agreement binds only once a member enacts its own law.
* Excise: Law No. 25 of 2018 on Excise Tax as published in the Official Gazette No. 1 of 2019 (17/01/2019, pp. 35-55,
  MoJ scan `law/qa_og_2019_01_law25_2018.pdf`), in force from 2019-01-01:
  - art. 4 (2018 wording, p. 38): "تحدد قيمة السلع الانتقائية الواجب الإقرار عنها ، والتي تفرض عليها الضريبة ، بسعر
    بيع التجزئة المصرح عنه من قبل المنتج أو المستورد لهذه السلع أو وفق قائمة الأسعار المعيارية ... أيهما أعلى";
  - "جدول السلع الانتقائية" (p. 55; same table as Al Meezan attachment 16834): التبغ ومشتقاته 100 %، المشروبات الغازية
    50 %، مشروبات الطاقة 100 %، السلع ذات الطبيعة الخاصة 100 %.
  The MoJ record (API, read 2026-11-21) marks articles 2, 4, 22, 26 and 28 and the tables amended only with effect
  from 2026-07-07 (Law 2/2026: Tables (1)-(2), sugar bands QAR 0.77 / 1.06 per litre), so the 2018 table governs 2025.
  Value: the retail price before the excise (no VAT in Qatar): `beforeTax`, `vatBp` 0; the standard price list floor
  is not applied. Non-carbonated sweetened drinks are not in the 2018 table (not taxed in 2025).
-/

namespace QaGlobal
open TaxKernel TaxKernel.Global

def consumptionAbsent : List Absent :=
  [{ oecd := .vat, why := "5111: no VAT: Permanent Constitution art. 43 (taxes only by a law; the article is unchanged by the 2024 amendments: lexifina/qatar-law, versions of 9/6/2005 and 6/11/2024); no VAT law in force: the Ministry of Justice legislation API title list (all 9 753 records, pass 3p) has no VAT act (its two 'value added' titles are a tax treaty and a telecoms regulation); tax acts in force: Income Tax Law 24/2018, Excise Tax Law 25/2018. The GCC VAT Agreement binds only once a member enacts its own law. convention R5-3k-G; grade A (gap-closing pass, was B)" },
   { oecd := .salesTax, why := "No general sales tax law (as for VAT)" }]

def exciseOf (good : Good) (sub : String) (bp : Int) (what : String) : ExciseRule :=
  { good, sub, name := "الضريبة الانتقائية", adValoremBp := bp, valueBase := .beforeTax, vatBp := 0,
    statute := s!"Law 25/2018 art. 4 and table (OG 1/2019 p. 55): {what}" }

def excise : List ExciseRule :=
  [exciseOf .cigarettes "" 10000 "التبغ ومشتقاته 100 %", exciseOf .tobaccoOther "" 10000 "التبغ ومشتقاته 100 %",
   exciseOf .nonAlcoholic "softDrinks" 5000 "المشروبات الغازية 50 %",
   exciseOf .nonAlcoholic "energyDrinks" 10000 "مشروبات الطاقة 100 %"]

def consumption : Family :=
  { name := "5121 الضريبة الانتقائية", covers := [.excise],
    run := fun _ g _ => exciseRuleCharges excise g }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther) then
    ["tobacco excise: the standard price list floor (Law 25/2018 art. 4) not applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .beer || s.good == .wine) then
    ["alcohol: 'السلع ذات الطبيعة الخاصة' 100 % (Law 25/2018 table) is not itemised in the law; not computed"] else [])
  ++ (if (consumptionX g).any (fun (s, x) => s.good == .nonAlcoholic && x.sub == "") then
    ["nonAlcoholic lines without sub (softDrinks/energyDrinks): no excise applied"] else [])

-- 50 % on the price before excise: 150 paid = 100 + 50; 100 % energy drinks: 200 = 100 + 100
#guard (excise.getD 2 default).dutyOn { good := .nonAlcoholic, amount := 150 } { sub := "softDrinks" } == 50
#guard (excise.getD 3 default).dutyOn { good := .nonAlcoholic, amount := 200 } { sub := "energyDrinks" } == 100
#guard (excise.getD 0 default).dutyOn { good := .cigarettes, amount := 3000 } {} == 1500

end QaGlobal
