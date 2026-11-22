import TaxKernel.Global
import R5Common

/-!
# Kuwait 2025: income tax on bodies corporate (1200) (pass 3r: re-cited to Decree-Law 157/2024)

Kuwait Income Tax Decree No 3 of 1955, art. 1, 3 and 7 as replaced by **Law No 2 of 2008** (Kuwait Al-Youm No 856 of
3/2/2008; MoF scan `mof.gov.kw/Desicions/Decree/PDF/Q2-2008.pdf`, Wayback 2011-10-16, `law/kw_law2_2008_gazette.pdf`,
read on the page image): art. 1 "تفرض ضريبة دخل سنوية على دخل كل هيئة مؤسسة تزاول العمل أو التجارة في دولة الكويت
أينما كان تأسيسها ... ويحدد مقدار الضريبة وفقاً لهذا القانون بنسبة 15% من الدخل الصافي الخاضع للضريبة", with profits
from trading on the Kuwait stock exchange exempt; art. 3: net income after all expenses incurred to earn it; art. 7:
a loss is carried to the following years, at most three. Executive Regulations (`la2-2008.pdf`, Wayback) define the
body corporate. The tax is in practice borne by foreign bodies corporate (Kuwaiti and GCC ownership outside it: the
regulation's scope article not read), so it is computed only for a company flagged `foreign`.

**2025 (pass 3r).** **Decree-Law 157/2024** issuing the law on the tax on multinational groups (MoF copy
`mof.gov.kw/MOFServices/PDF/TaxMultinationalLegislation.pdf`, scan of 30/12/2024, Wayback 30/01/2025; Arabic OCR,
`law/kw_dl157_2024_mof.pdf`, `kw_dl157_2024.ocr.txt`) cites in its preamble "المرسوم رقم (3) لسنة 1955 بشأن ضريبة الدخل
الكويتية والقوانين المعدلة له" as in force and, art. 1 (أولى): from tax periods beginning on or after 1/1/2025 the
groups subject to the new law are no longer subject to Decree 3/1955, Law 23/1961, Law 19/2000 art. 12(1) and 14(2)
(NLST) and Law 46/2006 (zakat); art. 5 (خامسة): in force from 1/1/2025. A group is subject when its consolidated
revenue reached EUR 750 million in at least two of the four preceding tax periods (law art. 1, "حد الإيرادات").
So in 2025 the 15 % applies to a foreign body corporate outside such a group; for a member (flag `mneGroup750`) the
heading is the domestic minimum top-up tax, not computed (listed). The MoF form for non-Kuwaiti taxpayers served in
2025 (`TaxFormNotKuwaiti.aspx`, Wayback 06/02/2025) still applies "القانون 2 لسنة 2008 المعدل لمرسوم ضريبة الدخل رقم 3
لسنة 1955". **Grade A** for the rate and base. Not computed: the DL 157/2024 tax, NLST, KFAS (zakat, Law 46/2006: `Zakat.lean`, gap-closing pass);
the three-year limit on losses (aggregate `lossesForward` offset).
-/

namespace KwGlobal
open TaxKernel TaxKernel.Global R5Common

def it : CorpRegime := { name := "ضريبة الدخل", sched := Schedule.flat 1500 }

/-- a constituent of a multinational group with consolidated revenue of EUR 750 million (DL 157/2024) -/
def mneGroup (g : CanonGlobal) : Bool := g.company.flags.contains "mneGroup750"

def corporate : Family :=
  { name := "1200 ضريبة الدخل على الهيئات المؤسسة", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company || !g.company.flags.contains "foreign" || mneGroup g then [] else
      [it.citCharge g.company "Income Tax Decree 3/1955 art. 1, 3, 7 as replaced by Law 2/2008 (15 %); DL 157/2024 art. 1 (groups below EUR 750 m stay under it in 2025)"] }

def corporateUnsupported (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if mneGroup g then
    ["1200: member of a multinational group with revenue of EUR 750 m: from 1/1/2025 the tax of Decree-Law 157/2024 (15 % top-up) replaces Decree 3/1955, NLST and zakat (DL 157/2024 art. 1): not computed"]
  else if g.company.flags.contains "foreign" then [] else
    ["income tax: a company not flagged `foreign` taken as Kuwaiti/GCC-owned and outside Law 2/2008 (Executive Regulations scope not read)"])
  ++ (if g.company.lossesForward ≠ 0 && !mneGroup g then ["losses: offset in full; art. 7 limits the carry-forward to three years"] else [])

#guard (it.citTax { profit := 1000000 }) == 150000

end KwGlobal
