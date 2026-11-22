import NrGlobal.Pit

/-!
# Nauru 2025: business profits tax (1200) and non-resident tax (withholding)

Source: Business Tax Act 2016 (No. 31 of 2016), RONLAW consolidation "Service 6" (as amended to the Constitution
(Amendment) (No 2) Act 2026, which only renames the Republic) and the Business Tax (Amendment of Schedule 1)
Regulations 2024 (SL No. 22 of 2024, in force 1 July 2024), texts from the RONLAW search index
(`ronlaw.gov.nr/api/pdf/search`; `nr/law/nr_bta2016_serv6.txt`, `nr/law/nr_bta_sch1_regs2024.txt`, sha256 in `SHA256SUMS`).
* **s. 11** business profits tax at the Schedule 1 rates on taxable income. **Schedule 1 (1) (d)**: Category A resident
  company with annual gross revenue $0 - $15,000,000: 20 %; Category B above $15,000,000: 25 %; Category C resident
  company controlled by a non-resident associate 25 %; D (RPC business) 30 %; E non-resident company with a PE 25 %;
  F (PE in connection with the Regional Processing Centre) 30 %. Modelled: 20 % at turnover up to $15 m, 25 % above.
* **s. 13 (1)**: non-resident tax "on a non-resident person who has derived interest, a royalty, or insurance premium
  from sources in Naoero"; **Schedule 1 (3)**: "For any other person 20%" (30 % for RPC-related persons);
  **s. 44**: withheld by the payer. Dividends are not in s. 13: explicit 0 % rule (cited). Fees for services paid
  abroad fall under the Employment and Services Tax Act 2014 (services tax, not read): no rule.
-/

namespace NrGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Business profits tax",
    sched := Schedule.flat 2500,
    smallTurnover := 15000000,
    smallSched := Schedule.flat 2000 }

def citStatute : String := "Business Tax Act 2016 s. 11, Schedule 1 (1) (d) Categories A-B (SL 15 of 2018; SL 22 of 2024)"

def wht : Wht :=
  { name := "Non-resident tax (Business Tax Act 2016 s. 13)", rules := [
      { kind := .interest, rateBp := 2000, statute := "Business Tax Act 2016 s. 13 (1), s. 44 (1), Schedule 1 (3) (\"any other person 20%\")" },
      { kind := .royalty, rateBp := 2000, statute := "Business Tax Act 2016 s. 13 (1), s. 44 (1), Schedule 1 (3)" },
      { kind := .dividend, rateBp := 0, statute := "Business Tax Act 2016 s. 13 (1): non-resident tax covers interest, royalties and insurance premiums only" },
      { kind := .services, rateBp := 2000, statute := "Employment and Services Tax Act 2014 s. 9 (1) (b) (i), s. 12 (1), (3), s. 18, Schedule (4) (c): any other non-resident person providing services 20 %" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["Schedule 1 Categories C (resident company controlled by a non-resident associate, 25 %), D and F (Regional Processing Centre business, 30 %) are not distinguished: 20 %/25 % by turnover"] else [])

#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 200000
#guard cit.citTax { profit := 1000000, turnover := 20000000 } == 250000
#guard wht.amount { kind := .interest, amount := 1000 } == 200
#guard wht.amount { kind := .services, amount := 1000 } == 200

end NrGlobal.Corporate
