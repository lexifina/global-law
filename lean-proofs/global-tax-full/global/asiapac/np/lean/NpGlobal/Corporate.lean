import NpGlobal.Pit

/-!
# Nepal FY 2082/83: income tax on entities (1200)

Income Tax Act 2058 as amended by the Finance Act 2082 (`cmp20/world/B11-south-asia/np/law/ita2058_fa2082.pdf`): Schedule 1
rates as read by the registry (B).
* **Schedule 1 s. 2**: entities 25 %; banks, financial institutions, telecom, tobacco and alcohol 30 % (flag `bank`);
  special industries 20 %.

FT review (2026-11-21): **ITA 2058 s. 88** in the consolidation as amended by the Finance Act 2082
(`cmp20/world/B11-south-asia/np/law/ita2058_fa2082.pdf`, sha256 8a1ca760... in that folder's SHA256SUMS; text layer
`ita2058.txt` lines 4645-4800, Devanagari with ligature damage, the rates legible):
* **s. 88 (1)**: a resident person paying "नेपालमा स्रोत भएको ब्याज, ... रोयल्टी, सेवा शुल्क, ... भुक्तानी गर्दा कुल भुक्तानी रकमको
  पन्ध्र प्रतिशतका दरले कर कट्टी गर्नु पर्नेछ" (interest, royalties, service fees with a source in Nepal: 15 % of the gross
  payment); the provisos' lower rates (5 % commission paid by a resident employment company to a non-resident,
  10 % aircraft lease, 5 % interest on foreign-currency loans of banks and of hydropower projects, ...) are not modelled.
* **s. 88 (2) (क)**: "लाभांश भुक्तानी गरेकोमा भुक्तानी रकमको पाँच प्रतिशत" (dividends: 5 %).
Recipient type does not change the rate; tax withheld on a payment to an individual is booked under 1100.
-/

namespace NpGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- The rate by the company's flags (sector), else the general rate. -/
def rateOf (co : Company) : Int := if co.flags.contains "bank" then 3000 else if co.flags.contains "specialIndustry" then 2000 else 2500

def cit (co : Company) : CorpRegime :=
  { name := "Income tax on entities",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "ITA 2058 Schedule 1 s. 2"

def wht : Wht :=
  { name := "Withholding tax on payments (ITA 2058 s. 88)", rules := [
      { kind := .dividend, rateBp := 500, statute := "ITA 2058 s. 88 (2) (क) (5 %)" },
      { kind := .interest, rateBp := 1500, statute := "ITA 2058 s. 88 (1) (15 %)" },
      { kind := .royalty, rateBp := 1500, statute := "ITA 2058 s. 88 (1) (15 %)" },
      { kind := .services, rateBp := 1500, statute := "ITA 2058 s. 88 (1) (सेवा शुल्क, 15 %)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [(cit g.company).citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if !g.company.paymentsAbroad.isEmpty then ["ITA 2058 s. 88 (1) provisos (5 % / 10 % special payments) and treaty rates not modelled"] else [])

#guard (cit { profit := 1000000 }).citTax { profit := 1000000 } == 250000
-- s. 88 (2) (क) 5 %; s. 88 (1) 15 %
#guard wht.amount { kind := .dividend, amount := 1000 } == 50
#guard wht.amount { kind := .interest, amount := 1000 } == 150
#guard wht.amount { kind := .royalty, amount := 1000 } == 150
#guard wht.amount { kind := .services, amount := 1000, toCompany := false } == 150

end NpGlobal.Corporate
