import TaxKernel.World

/-!
# Seychelles: income tax on employment emoluments (Income and Non-Monetary Benefits Tax Act, Cap 273), 2025

Access tier A for the emoluments tax (statute and its amending instruments, all served by the Seychelles Revenue
Commission, src.gov.sc/legislation, fetched 2026-11-20; sha256 in `sc/law/SHA256SUMS`; scanned instruments OCR'd and
the rate table checked on the page image):
* Income and Non-Monetary Benefits Tax (Amendment) Act, 2017 (Act 27 of 2017, Supplement to Official Gazette 29th
  December 2017), s. 2 (f) replacing the First Schedule [Section 4 (1)], para 1: "The income tax payable by an employed
  person who is a citizen of Seychelles in respect of emoluments received from each source of employment in a month
  shall be as follows — Not exceeding SR8555.50 NIL; Exceeding SR 8555.50 but not exceeding SR10,000 15% of the amount
  in excess of SR8555.50; Exceeding SR10,000 but not exceeding SR83,333 SR216.68 plus 20% of the amount in excess of
  SR10,000; Exceeding SR83,333 SR14,883.28 plus 30% of the amount in excess of SR83,333". Para 2 (non-citizens): "Not
  exceeding SR10,000 15% of the amount; ... SR1,500 plus 20% ...; Exceeding SR83,333 SR16,166.60 plus 30%".
* Later instruments touching the First Schedule: S.I. 79 of 2018 (repeals para 3 (b)), S.I. 28 of 2019 (repeals para
  2A and S.I. 24 of 2019), S.I. 26 of 2024 (paras 6-8: bonuses and thirteenth-month pay, from 7 November 2023 / 1
  January 2024); Act 32 of 2022 (Third and Fourth Schedules, s. 5 (6) arrears) does not touch paras 1-2.
Computed in cents per month and per source; the annual tax is 12 months of one source per adult. Optional input field
`"citizen": false` selects para 2. Not modelled: bonuses (paras 6-8), non-monetary benefits (employer tax), business
tax on self-employment.
W5 pattern A (2026-11-20): Seychelles Pension Fund Act 2005 (consolidated version 01/01/2023, pensionfund.sc;
`sc/law/w5/`) s. 17 (1) "Every worker who is a citizen of Seychelles shall be a member of the Fund"; s. 18 (2) "Every
worker shall pay into the Fund for each month ... such sum as may be prescribed". The prescribing regulations were not
reached; the rate is the Fund's notice "Changes to the rates of contribution towards SPF" (08/12/2022, official
secondary): "For employees, the increase in contribution rate will be from 4% to 5%" effective 1 January 2023. No
ceiling is stated (none modelled). Amendment Act 17 of 2025 changes benefits and retirement, not the rate. Citizens
only (non-citizens are not members). Not deducted from the taxable emoluments (the First Schedule taxes emoluments; no
deduction provision read). Input `"w5Contrib": false` drops it.
-/

namespace ScTax
open TaxKernel

/-- First Schedule para 1, monthly, in cents. -/
def citizenSched : Schedule := Schedule.ofList [(0, 0), (855550, 1500), (1000000, 2000), (8333300, 3000)]
/-- para 2 (non-citizens). -/
def nonCitizenSched : Schedule := Schedule.ofList [(0, 1500), (1000000, 2000), (8333300, 3000)]

/- The printed amounts SR216.68, SR14,883.28 and SR1,500, SR16,166.60 (cents; 216.675 printed rounded to 216.68). -/
#guard divR .halfUp (citizenSched.ticks 1000000) BP = 21668
#guard divR .halfUp (citizenSched.ticks 8333300) BP = 1488328
#guard divR .halfUp (nonCitizenSched.ticks 1000000) BP = 150000 ∧ divR .halfUp (nonCitizenSched.ticks 8333300) BP = 1616660

/-- Monthly tax in cents on monthly emoluments in cents from one source. -/
def monthlyCents (citizen : Bool) (m : Int) : Int :=
  divR .halfUp ((if citizen then citizenSched else nonCitizenSched).ticks (pos m)) BP

/-- SPF employee contribution, 5 % of emoluments (Fund notice of 08/12/2022, from 1 January 2023). -/
def spfEmployee (wages : Int) : Int := divR .halfUp (500 * pos wages) BP

#guard spfEmployee 120000 = 6000

def annual (citizen : Bool) (wages : Int) : Int :=
  divR .halfUp (12 * monthlyCents citizen (divR .down (100 * wages) 12)) 100

/- "each source of employment in a month": SR20 000 a month from one employer costs SR2 216.68; the same SR20 000 from
   two employers (10 000 each) costs 2 x 216.68 = SR433.36 (FINDINGS F1). -/
#guard monthlyCents true 2000000 = 221668 ∧ 2 * monthlyCents true 1000000 = 43336

def out (c : Canon) : Out :=
  let citizen := (c.bool? "citizen").getD true
  let it := sumInts (c.adults.map fun a => annual citizen a.wages)
  let w5 := (c.bool? "w5Contrib").getD true
  let spf := if w5 ∧ citizen then sumInts (c.adults.map fun a => spfEmployee a.wages) else 0
  Out.make c "SC" "SCR" it (employeeSocial := spf)
    (detail := [Out.d "taxBeforeCredits" it,
      Out.dStr "note" "INMBT Act First Schedule para 1 (citizens) / 2 (non-citizens) as replaced by Act 27 of 2017; one source per adult, 12 equal months"])
    (unsupported := (if c.interest ≠ 0 ∨ c.dividends ≠ 0 ∨ c.rentalIncome ≠ 0 ∨ c.capitalGains ≠ 0 then ["investment and property income: not under the emoluments tax; not modelled"] else []) ++
      (if (c.adults.any fun a => a.selfEmployment ≠ 0 ∨ a.pension ≠ 0) then ["self-employment (Business Tax Act) and pensions not modelled"] else []) ++
      ["bonuses and thirteenth-month pay (First Schedule paras 6-8) not modelled"])

def country : Country := { code := "SC", name := "Seychelles (emoluments tax, 2025)", currency := "SCR", year := "2025", compute := out }

def sched : Schedule := citizenSched
theorem sched_progressive : sched.progressive = true := by decide

end ScTax
