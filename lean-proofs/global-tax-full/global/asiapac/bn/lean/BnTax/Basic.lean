import TaxKernel.World

/-!
# Brunei Darussalam 2025: the individuals' rate schedule is empty; National Retirement Scheme (SPK) contribution

Sources (read 2026-11-20; `bn/law/`):
* Income Tax Act, Chapter 35, Revised Edition 2024 (B.L.R.O. 1/2024; agc.gov.bn, `ita_cap35_2024.pdf`): s. 8(1)(b)
  income includes "gains or profits from any employment", but s. 34 "Rate of tax upon individuals": tax "upon the
  chargeable income of every person, other than a company, tax at the rates specified in Schedule 2", and
  Schedule 2 "RATE OF TAX ON CHARGEABLE INCOME" lists no rate (the table is empty). s. 35: companies 18.5 % from
  YA 2015; s. 35(2B): 10 % on remuneration paid by a company to a non-resident director (not modelled).
  Ministry of Finance and Economy, Revenue Division FAQ (official secondary): "Currently, NO tax is levied on:
  ... 2) Personal income – Any earning by an individual from employment, self-employment, dividens, interest etc."
* National Retirement Scheme Act, Chapter 273, Revised Edition 2024 (B.L.R.O. 2/2024; S 21/2023, commencement
  15 July 2023; TAP's copy, `nrs_act_cap273.pdf`): s. 2 "employee" means any person below the minimum retirement
  age being "(a) a citizen of Brunei Darussalam; or (b) a permanent resident"; s. 10(2) "Every employee shall pay
  to the Scheme monthly, in respect of himself, contributions at the rate of 8.5 per cent of his wages" (no
  ceiling; Schedule 2 sets the employer's banded rates).

Not modelled: the minimum retirement age test (Retirement Age Act, Chapter 270, not read). `"nationality"`:
`national` (citizen or permanent resident, default) or `expatriate` (no contribution). Whole dollars.
-/

namespace BnTax
open TaxKernel

def nationality (c : Canon) : String := (c.str? "nationality").getD "national"

def spk : Contribution := { name := "nationalRetirementScheme", sched := Schedule.flat 850 }   -- s. 10(2)

def out (c : Canon) : Out :=
  let nat := nationality c
  let s := if nat = "national" then sumInts (c.adults.map fun a => spk.amount a.wages) else 0
  Out.make c "BN" "BND" 0 (employeeSocial := s)
    (detail := [Out.d "nationalRetirementScheme" s, Out.dStr "nationality" nat,
      Out.dStr "note" "Income Tax Act Cap. 35 s. 34: individuals taxed 'at the rates specified in Schedule 2', which lists none; NRS Act Cap. 273 s. 10(2): 8.5 %"])

def country : Country :=
  { code := "BN", name := "Brunei Darussalam (citizen or PR employee)", currency := "BND", year := "2025", compute := out }

end BnTax
