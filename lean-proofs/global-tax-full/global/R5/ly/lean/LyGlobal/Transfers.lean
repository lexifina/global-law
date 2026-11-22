import TaxKernel.Global
import R5Common

/-!
# Libya 2025: stamp duty on transfers of real property (4400)

Stamp Duty Law No 12 of 2004 (قانون ضريبة الدمغة), annexed table, part ثانياً (dispositions, transactions and facts),
as amended by Law No 8 of 2010 (table items 21, 22, 24, 28, 33 replaced; the encyclopaedia of 2016, `m2016.pdf`
pp. 139-146, figures checked on the page image of p. 146):
* item 21: dispositions for consideration whose object is a real right in rem over real estate: **3 %**, borne by the
  person who receives the right (the buyer); exempt: dispositions between banks and lenders and persons on limited
  income or basic pensions, and between ascendants and descendants and between spouses.
* item 22: gratuitous dispositions inter vivos of such rights: 2 % on the recipient (exempt in the direct line and
  between spouses); not computed (gifts are not purchases).
The duty is on the value of the disposition (the price). Recurrent property tax: none (Law 2/1986 on the real-estate
tax repealed by Income Tax Law 7/2010 art. 104; see Other.lean). **Grade A** for the text read; currency 2025: grade B, below.
**2025 (pass 3r re-cite, grade B).** The Tax Authority's page of tax laws as served in January 2025 (tax.gov.ly/Law1.aspx,
Wayback 17/01/2025; `law/ly_tax_laws_list_2025.html`) lists "قانون رقم 7 لسنة 2010 لضريبة الدخل", "قانون رقم (8) لسنة
2010", "قانون ضريبة الجهاد رقم (44) لسنة 1970" with no amending law, while it does list amending acts of other laws
(e.g. "قانون رقم (28) لسنة 1423 بتعديل احكام القانون رقم (2) لسنة 1986"); its regulations page (Law2.aspx, Wayback
16/01/2025) lists the executive regulation of Law 7/2010; the 2016 encyclopaedia is still served (assets/m2016.pdf,
Wayback 02/04/2025). Taken as the text in force in 2025; grade B (an official list, not a 2025 consolidation).
-/

namespace LyGlobal
open TaxKernel TaxKernel.Global R5Common

def stamp : TransferDuty := { name := "ضريبة الدمغة على التصرفات العقارية", sched := Schedule.flat 300 }

def transfers : Family :=
  { name := "4400 ضريبة الدمغة (التصرفات العقارية)", covers := [.transactions],
    run := fun _ g _ => stamp.charges g.purchases "Stamp Duty Law 12/2004, table part 2 item 21 as replaced by Law 8/2010 (3 % on the buyer)" }

def transfersUnsupported (g : CanonGlobal) : List String :=
  (if g.purchases.any (fun p => p.kind.isRealEstate) then
    ["stamp duty: exemptions for transfers in the direct line, between spouses and bank financing for low incomes (item 21) not applied"] else [])
  ++ (if g.transfers.any (fun t => t.kind == .gift) then
    ["stamp duty 2 % on gifts of real rights over real estate (item 22) not computed"] else [])

#guard stamp.amount { kind := .home, price := 500000 } == 15000
#guard stamp.amount { kind := .listedShares, price := 500000 } == 0



end LyGlobal
