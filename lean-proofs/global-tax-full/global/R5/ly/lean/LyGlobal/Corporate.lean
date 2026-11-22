import TaxKernel.Global
import R5Common

/-!
# Libya 2025: income tax on companies and the Jihad tax (1200)

Source: "موسوعة التشريعات الضريبية الحديثة" (tax legislation encyclopaedia, part 1, 2016; the 1.x folder's
`world/B06-mena/ly/law/m2016.pdf`), Arabic OCR with the figures checked on the page images (pp. 28-29, 104):
* Income Tax Law No 7 of 2010 (قانون ضرائب الدخل), art. 63: the tax is imposed on the income of national companies
  (arising in Libya and abroad) and of branches of foreign companies; art. 64: also other juristic persons with a
  commercial, industrial, craft or real-estate investment activity; art. 66: annual tax on net income;
  art. 70: "يكون سعر الضريبة سنوياً (20%)". Art. 104 repeals Law 11/1372 (2004), Law 2/1986 (real-estate tax) and
  Law 28/1369 (livestock tax).
* Law No 44 of 1970 imposing the Jihad tax (ضريبة الجهاد), art. 1 (additional tax on profits and income), art. 2
  ثانياً: on all profits and other incomes defined in the tax law except agriculture: 2 % of profit exempt from tax,
  "4% من الربح أو الدخل الخاضع للضريبة فيما زاد على حد الإعفاء". A company has no exemption limit: 4 % of the
  taxable profit. The encyclopaedia (2016) prints the law as in force; no later repeal was found.
Taxable profit = profit + add-backs − exempt income − losses brought forward (losses offset in full: the
carry-forward rule of the individual business-income chapter is applied to companies by art. 71 and not limited here).
**Grade A** for the text read (2016 encyclopaedia); currency 2025: grade B, below.
**2025 (pass 3r re-cite, grade B).** The Tax Authority's page of tax laws as served in January 2025 (tax.gov.ly/Law1.aspx,
Wayback 17/01/2025; `law/ly_tax_laws_list_2025.html`) lists "قانون رقم 7 لسنة 2010 لضريبة الدخل", "قانون رقم (8) لسنة
2010", "قانون ضريبة الجهاد رقم (44) لسنة 1970" with no amending law, while it does list amending acts of other laws
(e.g. "قانون رقم (28) لسنة 1423 بتعديل احكام القانون رقم (2) لسنة 1986"); its regulations page (Law2.aspx, Wayback
16/01/2025) lists the executive regulation of Law 7/2010; the 2016 encyclopaedia is still served (assets/m2016.pdf,
Wayback 02/04/2025). Taken as the text in force in 2025; grade B (an official list, not a 2025 consolidation).
-/

namespace LyGlobal
open TaxKernel TaxKernel.Global R5Common

def it : CorpRegime := { name := "ضريبة الدخل على الشركات", sched := Schedule.flat 2000 }
def jihad : CorpRegime := { name := "ضريبة الجهاد", sched := Schedule.flat 400 }

def corporate : Family :=
  { name := "1200 ضريبة الدخل على الشركات وضريبة الجهاد", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [it.citCharge g.company "Income Tax Law 7/2010 art. 63, 66, 70 (20 %)",
       jihad.citCharge g.company "Law 44/1970 art. 1, 2 ثانياً (Jihad tax 4 % of taxable profit)"] }

def corporateUnsupported (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["income tax: exempt income and branch expense limits (art. 66: head-office charges ≤ 5 % of administrative expenses) taken as given",
   "Jihad tax on wages and pensions (Law 44/1970 art. 2 أولاً: 1/2/3 %) not computed here (the 1.x PIT line is unchanged)"]
  ++ (if g.company.lossesForward ≠ 0 then ["losses: offset in full (no time limit applied)"] else [])

#guard (it.citTax { profit := 1000000 }) == 200000
#guard (jihad.citTax { profit := 1000000 }) == 40000



end LyGlobal
