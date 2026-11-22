import LkGlobal.Pit

/-!
# Sri Lanka 2025-26: income tax on companies and withholding on non-residents (1200)

Inland Revenue Act No. 24 of 2017 as amended by Act No. 45 of 2022 (B: First and Fifth Schedules as read by the registry;
the build server copies `sched1_20251001.txt`, `sched5_s52.txt` not re-read).
* **First Schedule para. 4 (1) (d)**: companies 30 % "with effect from April 1, 2023" (para. 2 is partnerships).


FT review (2026-11-21). The withholding rates are in the **First Schedule para. 10**, not the Fifth Schedule (which
lists qualifying payments and reliefs). Read: the Act as enacted (parliament.lk `6054.pdf`, `lk/law/ira2017_6054.pdf`)
and the amending sections (copies in `cmp20/world/B11-south-asia/lk/law/act45_2022_sel.txt`, `act2_2025.txt`):
* **s. 84 (1) (a) (i)**: withholding "at the rate provided for in paragraph 10 of the First Schedule" where a person
  "pays a dividend, interest, discount, charge, natural resource payment, rent, royalty ..."; **s. 85 (1) (b)**: where a
  person "pays a service fee or an insurance premium with a source in Sri Lanka to a non-resident person".
* **para. 10 (1) (c) (ii)**: "service fees referred to in section 85(1)(b) - 14%".
* **para. 10 (1) (d)** (added by Act No. 45 of 2022 s. 33 (6) (c), for payments to which s. 84A (1A) applies):
  "(iv) all other payments except dividend - 14%; and (v) dividend paid-15%"; **(d) (ii)** as replaced by Act No. 2 of
  2025 s. 3 (3): "interest or discount paid ... (b) with effect from April 1, 2025 - 10%".
Grade B: s. 84A (1A) (its scope) and Act No. 10 of 2021 were not read; para. 10 (1) (b) (s. 84 (1) (a): interest 5 %,
other 14 %) would give 5 % on interest. Dividends 15 % and royalties 14 % under (d).

**Session 12 (year in force), 1200 grade A.** IRD consolidated text of the Inland Revenue Act "incorporating amendments up to
31st March 2025" (dated 30 June 2025; Acts No. 10 of 2021, 45 of 2022, 4 of 2023, 14 of 2023, 2 of 2025, each with its
effective date; ird.gov.lk, Internet Archive 2026-03-08, `lk/law/lk_ira_cons2025_ird_wb20260308.pdf`) and Act No. 2 of 2025
(`lk/law/lk_ira_act02_2025_ird_wb20250709.pdf`): First Schedule para. 4 (1) "(d) with effect from April 1, 2023 shall be
taxed at the rate of 30%" (Act No. 45 of 2022 s. 33 (3)); Act No. 2 of 2025 s. 3 (2) only adds (2C) from 1 April 2025
(foreign-currency service and foreign-source gains 15 %; betting, gaming, liquor and tobacco 45 %) and closes (2B) (40 %)
at 31 March 2025. The general 30 % is the same in Y/A 2024/25 (1 Jan - 31 Mar 2025) and 2025/26: no split. The sector
rates (para. 4 (2A)-(2C)) are not modelled (flagged).
-/

namespace LkGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat 3000 }

def citStatute : String := "IRA 2017 First Schedule para. 4 (1) (d) (30 % from 1 April 2023; Act No. 45 of 2022 s. 33 (3))"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 1500, statute := "IRA 2017 First Schedule para. 10 (1) (d) (v) (Act No. 45 of 2022)" },
      { kind := .interest, rateBp := 1000, statute := "First Schedule para. 10 (1) (d) (ii) (b) (Act No. 2 of 2025: 10 % from 2025-04-01)" },
      { kind := .royalty, rateBp := 1400, statute := "First Schedule para. 10 (1) (d) (iv) (14 %)" },
      { kind := .services, rateBp := 1400, statute := "s. 85 (1) (b); First Schedule para. 10 (1) (c) (ii) (14 %)" }] }

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
  (if true then ["concessionary and sector rates (First Schedule para. 4 (2A) 14 %, (2B) 40 % to 31 March 2025, (2C) 15 % / 45 % from 1 April 2025) and gains on investment assets (para. 4 (4): 30 %) not modelled"] else [])
  ++ (if !g.company.paymentsAbroad.isEmpty then ["withholding rates: s. 84A (1A) scope not read (para. 10 (1) (b) would give 5 % on interest); treaty rates not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 300000
-- First Schedule para. 10 (1) (d) (v), (d) (ii) (b), (d) (iv), (c) (ii)
#guard wht.amount { kind := .dividend, amount := 1000 } == 150
#guard wht.amount { kind := .interest, amount := 1000 } == 100
#guard wht.amount { kind := .royalty, amount := 1000 } == 140
#guard wht.amount { kind := .services, amount := 1000 } == 140

end LkGlobal.Corporate
