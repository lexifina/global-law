import TaxKernel.Global
import R5Common

/-!
# Kuwait 2025: zakat and contribution of shareholding companies, Law 46/2006 (OECD 1200)

Law No 46 of 2006 "في شأن الزكاة ومساهمة الشركات المساهمة العامة والمقفلة في ميزانية الدولة" (MoF copy
`mof.gov.kw/Desicions/Decree/PDF/Q46-2006.pdf`, Wayback 22/04/2026, `law/kw_law46_2006_mof.pdf`, Arabic OCR checked on
the page image):
* art. 1: **1 %** a year of the net profits of Kuwaiti public and closed shareholding companies; the company may state
  what part is zakat on its funds and ask that the amount go to a public service;
* art. 2: collected by the Ministry of Finance for the public treasury; art. 3: executive regulation (not read);
* art. 4: government-owned companies set up by special laws and companies under Decree 3/1955 are outside it.
In force in 2025: Decree-Law 157/2024 (read, KW 1200) cites Law 46/2006 in its preamble (with no amending law) and takes
only the members of groups with EUR 750 m revenue out of it from tax periods beginning 1/1/2025 (art. 1).
Classification: a compulsory payment to the treasury on company profits: OECD 1200 (Guide §85: a tax is classed by its
base; the region's row had it at 6000). Model: a company flagged `shareholding` (a Kuwaiti public or closed
shareholding company), not `foreign` and not `mneGroup750`: 1 % of `profit` (the regulation's deductions not read).
Grade A (statute text read).
-/

namespace KwGlobal
open TaxKernel TaxKernel.Global R5Common

def zakatRegime : CorpRegime := { name := "الزكاة ومساهمة الشركات (القانون 46 لسنة 2006)", sched := Schedule.flat 100 }

def zakatApplies (g : CanonGlobal) : Bool :=
  g.entity == .company && g.company.flags.contains "shareholding" && !g.company.flags.contains "foreign" &&
    !g.company.flags.contains "mneGroup750"

def zakat : Family :=
  { name := "1200 الزكاة ومساهمة الشركات المساهمة", covers := [.cit],
    run := fun _ g _ =>
      if zakatApplies g then
        [zakatRegime.citCharge g.company "Law 46/2006 art. 1 (1 % of net profits of Kuwaiti public and closed shareholding companies), art. 2, 4; DL 157/2024 art. 1"]
      else [] }

def zakatUnsupported (g : CanonGlobal) : List String :=
  if g.entity != .company || g.company.flags.contains "foreign" || g.company.flags.contains "mneGroup750" then [] else
  (if g.company.flags.contains "shareholding" then
    ["zakat (Law 46/2006): base taken as the company's profit (the executive regulation's base and deductions not read); state-owned companies set up by special laws (art. 4) not told apart"]
   else ["zakat (Law 46/2006, 1 %): applies to Kuwaiti public and closed shareholding companies: flag `shareholding` not given, not charged"]) ++
  ["NLST (Law 19/2000, Kuwaiti listed companies): text not reached, not computed (grade C)"]

#guard zakatRegime.citTax { profit := 1000000 } == 10000

end KwGlobal
