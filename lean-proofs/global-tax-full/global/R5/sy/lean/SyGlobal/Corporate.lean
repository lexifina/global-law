import TaxKernel.Global
import R5Common

/-!
# Syria 2025: real profits tax on companies (1200)

Income Tax Law No. 24 of 2003, art. 16 as replaced by Legislative Decree No. 30 of 2023 (Damascus, 28 August 2023;
full text as published by the Ministry of Agriculture and Agrarian Reform, 1.x `law/rescue3/ld30_2023_moaar.pdf`;
art. 29(a): the new rates apply to business from 1 January 2024). The rates include the national defence, schools,
municipal and sustainable-development additions, but not the local administration addition nor the national
reconstruction contribution (other laws, not read: not computed):
* art. 16(b), capital companies: 15 % for joint-stock companies with more than 40 % of their shares publicly
  subscribed (flag `publicOver40`); 20 % for other joint-stock companies, limited liability companies and public and
  mixed-sector companies; 25 % for banks, insurance and reinsurance and financial brokerage (flag `financial`);
  35 % for oil and gas investment companies (flag `oilGas`);
* art. 16(a), partnerships and other persons (flag `partnership`): 10 % up to 10,000,000 SYP, 14 % to 30,000,000,
  18 % to 100,000,000, 22 % to 500,000,000, 25 % above (the exempt minimum of art. 20 not read: taxed from the first
  pound).
Changes after December 2024 were not checked.
-/

namespace SyGlobal
open TaxKernel TaxKernel.Global R5Common

def partnershipSched : Schedule :=
  Schedule.ofUpper [(10000000, 1000), (30000000, 1400), (100000000, 1800), (500000000, 2200)] 2500

def syRate (co : Company) : Int :=
  if co.flags.contains "oilGas" then 3500 else if co.flags.contains "financial" then 2500
  else if co.flags.contains "publicOver40" then 1500 else 2000

def syRegime (co : Company) : CorpRegime :=
  { name := "ضريبة الأرباح الحقيقية",
    sched := if co.flags.contains "partnership" then partnershipSched else Schedule.flat (syRate co) }

def corporate : Family :=
  corpFamily "1200 ضريبة الأرباح الحقيقية" syRegime
    (fun co => if co.flags.contains "partnership" then "ITL 24/2003 art. 16(a) as replaced by LD 30/2023 (10-25 %)"
      else s!"ITL 24/2003 art. 16(b) as replaced by LD 30/2023 ({syRate co / 100} %)")
    { rules := [] }

def corporateUnsupported (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["local administration addition and national reconstruction contribution (other laws) not computed; post-2024 changes not checked"]
  ++ (if g.company.flags.contains "partnership" then ["partnership scale: exempt minimum (art. 20) not applied"] else [])
  ++ (if g.company.lossesForward ≠ 0 then ["losses brought forward: carry-forward rule not read; offset in full"] else [])
  ++ corpInputsUnread g false true true false

#guard (syRegime {}).citTax { profit := 1000000 } == 200000
#guard partnershipSched.tax {} 30000000 == 3800000

end SyGlobal
