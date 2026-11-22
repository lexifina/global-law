import TaxKernel.Global2
import R5Common

/-!
# Qatar 2025: income tax on companies (1200) and final withholding on non-residents

Source: Income Tax Law No. 24 of 2018 (MoJ Al Meezan text, as amended; `law/law-2018-24_income_tax.txt`):
* art. 9: "يكون سعر الضريبة (10%) عشرة بالمائة من الدخل الخاضع للضريبة"; art. 9(2): final withholding "بنسبة (5%)" on
  royalties, interest, commissions and services performed in Qatar paid to non-residents without a permanent
  establishment.
* art. 4 exemptions (e.g. 12: income of resident Qatari individuals; Law 17/2014 exempting non-Qatari investors' share
  in listed companies): the exempt share of the profit (Qatari/GCC owners) is the input `exemptShareBp` (default 0).
* losses of a year may be deducted from later years' net income (line 188 of the text; the time limit of the Executive
  Regulations is not read).
-/

namespace QaGlobal
open TaxKernel TaxKernel.Global R5Common

def exemptShareBp (g : CanonGlobal) : Int := max 0 (min BP (intField g.raw "exemptShareBp"))
def incomeTax : CorpRegime := { name := "الضريبة على الدخل", sched := Schedule.flat 1000 }

def wht : Wht :=
  { name := "الاستقطاع من المنبع",
    rules := [.royalty, .interest, .services].map (fun k => { kind := k, rateBp := 500, statute := "ITL 24/2018 art. 9(2) (5 %, final)" })
      ++ [WhtRule.zero .dividend "ITL 24/2018 art. 4(8): dividends paid out of profits taxed under this Law (or exempt) are exempt; art. 9(2) lists no dividends"] }

/-- Kernel 2.1 `CorpRule`: CIT on the share not exempt (`exemptShareBp` read as the complement). -/
def qaRule : CorpRule := { regime := incomeTax, shareKey := "exemptShareBp", shareComplement := true }

def corporate : Family :=
  { name := "1200 الضريبة على الدخل", covers := [.cit, .incomeOther],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [qaRule.citCharge g "ITL 24/2018 art. 9 (10 %), art. 4 (exempt share as input)"] ++ wht.charges g.company }

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g false true false true
  ++ (if g.entity == .company then ["domestic minimum top-up tax (Pillar Two, 2025 amendment) not modelled"] else [])

#guard incomeTax.citTax { profit := 1000000 } == 100000
#guard wht.amount { kind := .royalty, amount := 100000 } == 5000
#guard wht.amount { kind := .dividend, amount := 100000 } == 0

end QaGlobal
