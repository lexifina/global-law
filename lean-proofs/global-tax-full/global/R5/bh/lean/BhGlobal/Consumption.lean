import TaxKernel.Global2
import R5Common

/-!
# Bahrain 2025: VAT (5111); excise tax (5121)

Source: VAT Law promulgated by Decree-Law No. 48 of 2018, LLOC consolidated text with Law No. 33 of 2021
(`law/L4818.docx`, https://www.lloc.gov.bh/FullAr/L4818.docx; current consolidation, no later amending act appended).
* art. 3 as replaced by Law 33/2021 art. 3: "تُفرَض الضريبة بنسبة أساسية مقدارها (10%) من قيمة التوريد أو الاستيراد".
* art. 53 zero rate: 4 preventive and basic health care; 5 medicines and medical equipment; 12 nursery, pre-basic,
  basic, secondary and higher education; 13 the local transport sector; 14 oil, oil derivatives and gas; 15 the basic
  foods listed in item (first) of art. 31 of the GCC Agreement (the list is not in the Law: all food zero-rated here
  and flagged).
* art. 54 financial services exempt; art. 55 supplies of bare land and buildings (sale and lease) exempt.
* The mandatory registration threshold is in the Executive Regulation (not read): not applied.
Excise: Law No. 40 of 2017 regarding the Excise Tax, LLOC English text "including amendments thereto", published May
2024 (`law/FullEn_K4017.docx`), art. 3: "1-Tobacco (100%) 2-Soft Drinks (50%) 3-Energy Drinks (100%)"; base per the
GCC Unified Excise Tax Agreement (Law 39/2017) and Executive Regulation (Minister of Finance Decision 17/2017, OG 3346
of 28/12/2017, `law/og3346_20171228_excise_reg17_2017.pdf`) art. 4(d): the value is the retail price (or the standard
price, if higher) "مخصوماً منه الضرائب المشمولة فيها": the price before excise and VAT (`beforeTax`).
Sweetened drinks: Bahrain taxes none outside art. 3. The Regulation's art. 1 defines only التبغ, المشروبات الغازية
("أية مشروبات تحتوي على الغاز باستثناء المياه الغازية غير المنكهة") and مشروبات الطاقة; the 2024 consolidation of the Law
keeps three items; NBR's executive summary (June 2020, `law/nbr_excise_summary_202006.pdf`) lists the same three, and its
decisions page (archived 2023-07-02) lists only tax-stamp decisions. Non-carbonated sweetened drinks bear no excise.
**2025 (pass 3r re-cite).** NBR excise FAQ as served on 16/02/2025 (nbr.gov.bh/excise_faqs, Wayback;
`law/bh_nbr_excise_faq_2025.html`), q. 1.3 "ما هي السلع التي تشملها الانتقائية وكم تبلغ نسبة كل منها؟": "المشروبات الغازية –
بنسبة 50% / مشروبات الطاقة – بنسبة 100% / التبغ ومشتقاته – بنسبة 100%"; q. 1.6 lists as the legislation Law 39/2017, Law
40/2017 and Decision 17/2017 only (no amending law): the three rates applied all of 2025. Grade B.
-/

namespace BhGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "ضريبة القيمة المضافة", standard := 1000,
    classOf := fun g => match g with
      | .health | .medicines | .education | .transport | .petrol | .diesel | .gas | .food => .zero
      | .financial | .rent => .exempt
      | _ => .standard }

def exciseOf (good : Good) (sub : String) (bp : Int) (what : String) : ExciseRule :=
  { good, sub, name := "الضريبة الانتقائية", adValoremBp := bp, valueBase := .beforeTax, vatBp := 1000,
    statute := s!"Law 40/2017 art. 3: {what}" }

def excise : List ExciseRule :=
  [exciseOf .nonAlcoholic "softDrinks" 5000 "soft drinks 50 %", exciseOf .nonAlcoholic "energyDrinks" 10000 "energy drinks 100 %",
   exciseOf .cigarettes "" 10000 "tobacco 100 %", exciseOf .tobaccoOther "" 10000 "tobacco 100 %"]


def consumption : Family :=
  { name := "5111 ضريبة القيمة المضافة, 5121 الضريبة الانتقائية", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [vat.basketCharge g.consumption "DL 48/2018 art. 3 as amended by Law 33/2021 (10 %); art. 53 (zero), 54, 55 (exempt)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company "DL 48/2018 art. 3, 53-55"] else [])
      ++ exciseRuleCharges excise g }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then ["VAT: only the basic foods of the GCC Agreement art. 31 list are zero-rated; all food taken as zero-rated"] else [])
  ++ (if g.entity == .company then ["VAT registration threshold (Executive Regulation) not applied"] else [])
  ++ (if (consumptionX g).any (fun (s, x) => s.good == .nonAlcoholic && x.sub == "") then
    ["excise: nonAlcoholic lines without sub (softDrinks/energyDrinks): no excise applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther) then
    ["tobacco excise: the published retail price floor not applied"] else [])

#guard vat.embedded { good := .clothing, amount := 11000 } == 1000
#guard vat.embedded { good := .medicines, amount := 11000 } == 0

-- 100 % on the price before excise and VAT: 210 = 100 + 100 + 10 % VAT
-- non-carbonated sweetened drinks: no rule in the list (Law 40/2017 art. 3)
#guard (excise.filter (·.sub == "sweetenedDrinks")).isEmpty
#guard (excise.getD 1 default).dutyOn { good := .nonAlcoholic, amount := 220 } { sub := "energyDrinks" } == 100

end BhGlobal
