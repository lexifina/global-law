import TaxKernel.Global
import R5Common

/-!
# Lebanon 2025: tax on the profits of industrial, commercial and non-commercial professions (1200)

Decree-Law No 144 of 12/06/1959 (قانون ضريبة الدخل), art. 32 as replaced by **Budget Law No 324 of 12/02/2024 art. 46**
(Official Gazette No 7 of 15/02/2024, pp. 1-238; art. 96: in force on publication). Text from the Lebanese University's
legal informatics centre (legiliban.ul.edu.lb, budget law id 330076, saved `law/legiliban_budget324_2024_art46-50.txt`;
the income-tax law's amended-articles list, law id 185603, shows art. 32 version 7 by Law 324/2024 as the latest, no
2025 amendment; the earlier versions incl. Law 10/2022's, ended 12/02/2024, in `law/legiliban_itl_art32_history.html`):
* "أما أرباح شركات الأموال (الشركات المغفلة- الشركات المحدودة المسؤولية- شركات التوصية بالأسهم بالنسبة للشركاء
  الموصين) فتخضع لضريبة نسبية قدرها 17% (سبعة عشرة بالمئة)": capital companies (SAL, SARL, partnerships limited by
  shares for the limited partners) 17 % flat.
* other taxpayers on real profit (individuals, partnerships: flag `personsCompany`): 4 % to LBP 540 m, 7 % to 1,440 m,
  12 % to 3,240 m, 16 % to 6,240 m, 21 % to 13,500 m, 25 % above. The art. 31 personal allowance (Law 324/2024 art. 49:
  LBP 450 m per natural person, one allowance per de facto company) is deducted first for those (flag `personsCompany`).
* "يترك من الربح الخاضع لها ما كان دون العشرة الاف ليرة": the taxable profit is taken in whole LBP 10,000 (step down).
**Grade A** (dated statute text read). Losses (art. 17), the distribution tax on dividends (art. 72) and withholding on
non-residents (art. 41) are not computed.
-/

namespace LbGlobal
open TaxKernel TaxKernel.Global R5Common

def personsCompany (co : Company) : Bool := co.flags.contains "personsCompany"

/-- art. 32 progressive scale (LBP), Budget Law 324/2024 art. 46. -/
def art32Scale : Schedule :=
  Schedule.ofUpper [(540000000, 400), (1440000000, 700), (3240000000, 1200), (6240000000, 1600),
    (13500000000, 2100)] 2500

/-- art. 31 allowance for persons (Law 324/2024 art. 49): LBP 450 m, one per de facto company. -/
def art31Allowance : Int := 450000000

def stepDown (x : Int) : Int := divR .down (pos x) 10000 * 10000

def profitsTax (co : Company) : Int :=
  let base := pos (co.profit + co.addBacks - co.exemptIncome)
  if personsCompany co then art32Scale.tax {} (stepDown (base - art31Allowance))
  else divR .down (stepDown base * 1700) 10000

/-- Withholding on payments to non-residents (pass 3k; legiliban.ul.edu.lb, law id 185603 sections 273626, 273634-273636,
Budget Law 324/2024 law id 330076; `law/legiliban_itl_art41_72.txt`, `law/legiliban_budget324_2024_sections.html` art. 17, 54):
* DL 144/1959 art. 41: amounts received in Lebanon by persons without a place of business there; art. 42 as replaced by
  Budget Law 324/2024 art. 54 (from the quarter after publication, OG 15/02/2024): the net taxable amount is 20 % of the
  gross for delivered goods and **50 % for compensation for a service**, taxed at **17 %** (8,5 % of the gross); art. 43
  (Law 324/2024 art. 17): the payer withholds and pays quarterly.
* art. 70: movable-capital tax on every capital income not subject to another income tax; art. 72: **10 %** of the gross
  revenue (interest on a loan; bank deposits and bonds of joint-stock companies are art. 69, 7 %).
* art. 72 bis (Law 64/2017, distributions from 27/10/2017): distributions of Lebanese capital companies **10 %** in all cases.
Royalties: art. 42 names only goods and services; not classified here (grade C). -/
def lbWht : Wht :=
  { name := "الضريبة على غير المقيمين ورؤوس الأموال المنقولة",
    rules := [{ kind := .services, rateBp := 850, statute := "DL 144/1959 art. 41, 42 (Budget Law 324/2024 art. 54: 50 % of the gross taxed at 17 %)" },
              { kind := .dividend, rateBp := 1000, statute := "DL 144/1959 art. 72 bis (Law 64/2017: distributions 10 % in all cases)" },
              { kind := .interest, rateBp := 1000, statute := "DL 144/1959 art. 70, 72 (movable-capital income, 10 % of the gross)" }] }

def corporate : Family :=
  { name := "1200 ضريبة الأرباح", covers := [.cit, .incomeOther],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      let base := pos (co.profit + co.addBacks - co.exemptIncome)
      [charge .cit "ضريبة الأرباح (المادة 32)" base (fun b => if personsCompany co then stepDown (b - art31Allowance) else stepDown b)
        (fun _ => profitsTax co)
        (statute := if personsCompany co then "DL 144/1959 art. 31-32 (Budget Law 324/2024 art. 46, 49: scale 4-25 %)"
          else "DL 144/1959 art. 32 (Budget Law 324/2024 art. 46: capital companies 17 %)")] ++ lbWht.charges co }

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true true true true
  ++ (if g.entity == .company && g.company.dividendsPaid ≠ 0 then ["distribution tax on dividends paid (art. 72 bis, 10 %): booked on dividends in paymentsAbroad only; domestic distributions not computed"] else [])
  ++ (if g.entity == .company && !g.company.paymentsAbroad.isEmpty then (if g.company.paymentsAbroad.any (fun p => p.kind == .royalty) then ["royalties paid abroad: art. 42 (Law 324/2024 art. 54) sets the base for goods (20 %) and services (50 %) only; royalties not classified (grade C)"] else [])
       ++ ["interest paid abroad taken as art. 70/72 (10 %); bank-deposit and bond interest (art. 69, 7 %) not distinguished"] else [])

-- capital company: profit 1,000,000,005 -> 1,000,000,000 x 17 % = 170,000,000
#guard profitsTax { profit := 1000000005 } == 170000000
#guard lbWht.amount { kind := .services, amount := 1000000 } == 85000
#guard lbWht.amount { kind := .dividend, amount := 1000000 } == 100000
-- persons company: 1,450 m - 450 m = 1,000 m: 540 m x 4 % + 460 m x 7 % = 21.6 m + 32.2 m = 53.8 m
#guard profitsTax { profit := 1450000000, flags := ["personsCompany"] } == 53800000
#guard profitsTax { profit := 0 } == 0

end LbGlobal
