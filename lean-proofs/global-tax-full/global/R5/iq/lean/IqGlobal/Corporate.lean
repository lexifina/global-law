import TaxKernel.Global
import R5Common

/-!
# Iraq 2025: income tax on companies (1200)

Source: Income Tax Law No. 113 of 1982 as amended, tax.mof.gov.iq consolidated text (`law/itl113.html.txt`):
art. 13(2) ج-هـ: limited liability, private joint-stock and mixed joint-stock companies "بنسبة ثابتة مقدارها 15%".
The page is the General Commission for Taxes' current consolidation (no date printed): grade B.
-/

namespace IqGlobal
open TaxKernel TaxKernel.Global R5Common

def it : CorpRegime := { name := "ضريبة الدخل (الشركات)", sched := Schedule.flat 1500 }

/-- ITL 113/1982 art. 19(1)(a): tax at 15 % on interest due to a person outside Iraq (banks exempt); art. 2(2): a dividend
share is not taxable income where the company has deducted the tax under art. 15 (also art. 21(5)). -/
def iqWht : Wht :=
  { name := "ضريبة الاستقطاع",
    rules := [{ kind := .interest, rateBp := 1500, statute := "ITL 113/1982 art. 19(1)(a) (15 %)" },
              WhtRule.zero .dividend "ITL 113/1982 art. 2(2), 21(5): dividends paid out of taxed income are not taxable"] }

def corporate : Family := corpFamily "1200 ضريبة الدخل" (fun _ => it) (fun _ => "ITL 113/1982 art. 13(2) (15 %)") iqWht

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g true true false true
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .royalty || p.kind == .services) then ["royalties and services paid abroad: the Law assesses the non-resident through an agent (art. 21); direct-withholding instructions not read"] else [])

#guard it.citTax { profit := 1000000 } == 150000
#guard iqWht.amount { kind := .interest, amount := 100000 } == 15000

end IqGlobal
