import TaxKernel.World

/-!
# Saint Kitts and Nevis 2025: no tax on individuals' income since 1980; social security and the Housing and Social
# Development Levy (HSDL)

Sources (Law Commission, lawcommission.gov.kn, read 2026-11-20; `kn/law/`):
* Income Tax Act, Cap. 20.22, Revised Edition at 31 December 2017 (`ita_ch20_22_2017.pdf`), s. 3(3) (inserted by
  Act 14 of 1980): "This section shall not apply to income which accrues on or after 1st May, 1980 to any person
  (other than a company) liable under this section." Act 12 of 2021 adds s. 3A on companies only.
* Housing and Social Development Levy Act, Cap. 20.21, Revised Edition at 31 December 2017 (`hsdl_ch20_21_2017.pdf`):
  s. 3(1) "a Levy upon the wages of every person employed in Saint Christopher and Nevis"; s. 3(2):
  (a) wages up to the threshold: 0 % by the employee; (b) "in the case of an employee whose wages range between
  [the threshold] and $78,000.00, 3.5% by the employee"; (c) $78,000 to $96,000: "3.5% by the employee on the portion
  of the wages up to $78,000.00" and "10% ... between $78,000.01 and $96,000.01"; (d) above $96,000: in addition
  "12% by the employee on the portion of the wages which exceed $96,000.00".
  The threshold: $18,720 (2017 text); "$23,400.00 (450.00 per week)" by Act No. 1 of 2024 (published 29 February
  2024); "$27,040.00 (520.00) per week)" by Act No. 14 of 2025 (published 11 July 2025, Extra-Ordinary Gazette 39;
  no commencement clause read: taken as in force from July 2025 wages).
* Social Security Act, Cap. 22.10 and Regulations, Revised Edition at 31 December 2017 (`ssa_ch22_10_2017.pdf`):
  Schedule 1 to the Regulations, Part I: "Persons between 16 and 62 years: 5% of wages subject to the ceiling";
  under 16 and from 62: Nil; Schedule 2: ceiling "January 1, 1998: $6,500 Per Month" (no later instrument found in
  the annual laws 2021-2025 index search; S.R.O. 3 of 2024 amends benefits only).

Reading of s. 3(2)(b): below $78,000 the 3.5 % falls on the whole wage once the wage exceeds the threshold, so the
levy has a notch at the threshold (FINDINGS F1). 2025 is weighted 6/12 at $23,400 and 6/12 at $27,040.
-/

namespace KnTax
open TaxKernel

def ssCeiling : Int := 6500 * 12
def ss : Contribution := Contribution.flatCapped "socialSecurity" 500 ssCeiling      -- Regs Sch. 1 Part I, Sch. 2

def ssPerson (a : Adult) : Int := if a.age < 16 ∨ a.age ≥ 62 then 0 else ss.amount a.wages

def thresholdH1 : Int := 23400   -- Act 1 of 2024
def thresholdH2 : Int := 27040   -- Act 14 of 2025

/-- HSDL employee levy in ticks (units × basis points) for an annual wage `w` and threshold `t` (s. 3(2)). -/
def hsdlTicks (t w : Int) : Int :=
  if w ≤ t then 0
  else 350 * min w 78000 + 1000 * (min w 96000 - min w 78000) + 1200 * pos (w - 96000)

/-- One year under one threshold, whole dollars rounded down. -/
def hsdlYear (t w : Int) : Int := divR .down (hsdlTicks t w) 10000

/-- 2025: six months under each threshold. -/
def hsdl2025 (w : Int) : Int := divR .down (6 * hsdlTicks thresholdH1 w + 6 * hsdlTicks thresholdH2 w) (12 * 10000)

def hsdlPerson (a : Adult) : Int := if a.age < 16 then 0 else hsdl2025 a.wages

def out (c : Canon) : Out :=
  let s := sumInts (c.adults.map ssPerson)
  let h := sumInts (c.adults.map hsdlPerson)
  let uns := if c.adults.any (fun a => a.selfEmployment > 0) then ["self-employed social security contributions not modelled"] else []
  Out.make c "KN" "XCD" 0 (employeeSocial := s + h)
    (detail := [Out.d "socialSecurity" s, Out.d "housingSocialDevelopmentLevy" h,
      Out.dStr "note" "Income Tax Act Cap. 20.22 s. 3(3): no tax on non-company income since 1 May 1980; HSDL Act s. 3(2) (Acts 1/2024, 14/2025); SS Regs 5 % up to $6,500 a month"])
    (unsupported := uns)

def country : Country :=
  { code := "KN", name := "Saint Kitts and Nevis (employee)", currency := "XCD", year := "2025", compute := out }

end KnTax
