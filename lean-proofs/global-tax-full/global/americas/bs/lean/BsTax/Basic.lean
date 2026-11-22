import TaxKernel.World

/-!
# The Bahamas 2025: no income tax; National Insurance contribution of an employed person

Sources (Bahamas Laws On-line, laws.bahamas.gov.bs, point-in-time indexes at 2025-07-01; `bs/law/`):
* No income tax: the alphabetical index of Acts in force on 2025-07-01 (letter I) lists no income tax act, only the
  International Tax Cooperation Act and its orders (`lawsbs_index_bs_acts_I.html`); the Department of Inland
  Revenue's site lists VAT, real property tax, business licence and condo hotel taxes (official secondary).
* National Insurance (Contributions) Regulations (S.I. 68/1984 as revised to LRO 1/2017, `nic_regs_1984.pdf`):
  reg. 2 "basic wages" (wages for a normal period without overtime) and "insurable wage or income" = "the basic
  wage ... up to the wage ceiling set out in regulation 52"; reg. 52: "With effect from the 3rd day of January, 2011,
  the ceiling on insurable wages or income shall be $500 per week or $2,166 per month", "July 2nd, 2012: $600 per
  week or $2,600 per month", and from "July 2014 and every second year thereafter: To be determined based on the
  change in the Retail Price Index ... plus 2%".
* National Insurance (Contributions) (Amendment) Regulations, 2024 (S.I. No. 37 of 2024, in force 1 July 2024,
  `nic_regs_amend_2024.pdf`): Fifth Schedule: "Employed persons other than those in categories listed below: Basic
  wages 3.9 [employed person] 5.9 [employer] 9.8 [total]"; persons 65 and over not receiving retirement benefit
  3.4 / 5.4; reg. 23(1A): "a rate of contribution increase of one and one half percent on the rate of contribution
  set out in column 5 of the Fifth Schedule which shall be shared equally between the employer and employed person
  commencing the 1st day of July 2024". Employee rate in 2025: 3.9 % + 0.75 % = 4.65 %.

The 2025 ceiling is fixed administratively under reg. 52 (RPI + 2 % every second year since July 2014) and is not in
an accessible text: contributions are computed up to the last ceiling printed in the regulations ($2,600 a month);
for higher wages the output is flagged `unsupported` (the true contribution is higher). Ages 65 and over:
`unsupported` (the rate depends on receipt of retirement benefit). Whole dollars; contributions are weekly or monthly.
-/

namespace BsTax
open TaxKernel

def rate : Int := 465                 -- Fifth Schedule 3.9 % + reg. 23(1A) 0.75 %
def lastPrintedCeiling : Int := 2600 * 12   -- reg. 52, from 2 July 2012

def ni : Contribution := Contribution.flatCapped "nationalInsurance" rate lastPrintedCeiling

def out (c : Canon) : Out :=
  let s := sumInts (c.adults.map fun a => if a.age < 65 then ni.amount a.wages else 0)
  let uns :=
    (if c.adults.any (fun a => a.wages > lastPrintedCeiling) then
      ["2025 ceiling on insurable wages (reg. 52: RPI + 2 % every second year since July 2014) not in an accessible text: contributions capped at the last printed ceiling ($2,600 a month), so they are understated above it"] else [])
    ++ (if c.adults.any (fun a => a.age ≥ 65 ∧ a.wages > 0) then
      ["employed persons 65 and over: rate depends on receipt of retirement benefit (Fifth Schedule), not modelled"] else [])
    ++ (if c.adults.any (fun a => a.selfEmployment > 0) then
      ["self-employed persons' contributions (Fifth Schedule, income-based) not modelled"] else [])
  Out.make c "BS" "BSD" 0 (employeeSocial := s)
    (detail := [Out.d "nationalInsurance" s,
      Out.dStr "note" "no income tax act in force (Bahamas Laws index at 2025-07-01); NI (Contributions) Regs Fifth Schedule (S.I. 37/2024) 3.9 % + reg. 23(1A) 0.75 %"])
    (unsupported := uns)

def country : Country :=
  { code := "BS", name := "The Bahamas (employed person)", currency := "BSD", year := "2025", compute := out }

end BsTax
