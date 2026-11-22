import TaxKernel.Global
import R5Common

/-!
# Oman 2025: income tax on companies (1200) and withholding on payments to foreign persons

Income Tax Law (Royal Decree 28/2009; Qanoon.om text `law/om_itl.html`) as amended by Royal Decree 9/2017 (Qanoon.om
as archived 2026-04-21, `law/om_rd2017009.html`, ARCHIVE_INDEX.tsv; art. 112 and 159 bis (15) apply from the tax
year beginning 1 January 2017, RD art. 2(3)):
* art. 112 (RD 9/2017): "بتطبيق معدل (١٥٪) خمسة عشر بالمائة من الدخل الخاضع للضريبة لأي مؤسسة أو شركة عمانية أو منشأة
  مستقرة" (no exempt slice since 2017);
* art. 159 bis (15) (Part 5 bis, small establishments meeting the Regulations' criteria: company flag
  `smallEstablishment`): 3 % of taxable income; exempt when the owner manages it full-time or it employs at least two
  Omanis (flag `smallExempt`);
* art. 69-71: losses carried forward up to five years (the input `lossesForward` is taken as within the five years);
* art. 52 (with item 5 added by RD 9/2017: dividends or interest) and art. 113: 10 % of the gross amount paid to a
  foreign person for royalties, research and development, software and management fees. Dividends and interest:
  the suspension decisions in force in 2025 were not read: not computed.
-/

namespace OmGlobal
open TaxKernel TaxKernel.Global R5Common

def omRegime (co : Company) : CorpRegime :=
  { name := "ضريبة الدخل",
    sched := if co.flags.contains "smallEstablishment" then
      (if co.flags.contains "smallExempt" then Schedule.flat 0 else Schedule.flat 300) else Schedule.flat 1500 }

def omWht : Wht :=
  { name := "ضريبة الاستقطاع",
    rules := [{ kind := .royalty, rateBp := 1000, statute := "ITL art. 52(1)-(3), 113 (10 %)" },
              { kind := .services, rateBp := 1000, statute := "ITL art. 52(4) management fees, 113 (10 %)" },
              WhtRule.zero .dividend "ITL art. 52(5) (RD 9/2017) 10 %: collection suspended indefinitely by the Royal directive of 11 Jan 2023 (directive not published; Deloitte Oman highlights 2026, grade B)",
              WhtRule.zero .interest "ITL art. 52(5) (RD 9/2017) 10 %: collection suspended indefinitely by the Royal directive of 11 Jan 2023 (directive not published; Deloitte Oman highlights 2026, grade B)"] }

def corporate : Family :=
  corpFamily "1200 ضريبة الدخل" omRegime
    (fun co => if co.flags.contains "smallEstablishment" then "ITL art. 159 bis (15) (3 %; RD 9/2017)" else "ITL art. 112 (15 %; RD 9/2017), 69-71 (losses)")
    omWht

def corporateUnsupported (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .dividend || p.kind == .interest) then
    ["withholding on dividends and interest: art. 52(5) taken as suspended (Royal directive of 11 Jan 2023, text not read; grade B)"] else [])
  ++ corpInputsUnread g false true true false

#guard (omRegime {}).citTax { profit := 1000000 } == 150000
#guard (omRegime { flags := ["smallEstablishment"] }).citTax { profit := 100000 } == 3000
#guard omWht.amount { kind := .royalty, amount := 50000 } == 5000

end OmGlobal
