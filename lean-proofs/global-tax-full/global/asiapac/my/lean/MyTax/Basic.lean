import TaxKernel.World

/-!
# Malaysia: income tax of resident individuals, Year of Assessment 2025

Access tier B. The Income Tax Act 1967 (Act 53) is not in Global law (its Malaysia corpus holds the Constitution, the
Employment Act and the PDPA) and the Laws of Malaysia portal (lom.agc.gov.my) serves its act lists as encrypted JSON
behind signed tokens (not bypassed). The amounts are IRBM's (LHDN, hasil.gov.my) own published tables (official
secondary; pages saved in `my/law/`, fetched 2026-11-20, sha256 in `SHA256SUMS`):
* "Tax Rate", "Year of Assessment 2023, 2024 & 2025" (hasil_rates.html): A 0-5,000 0; B 5,001-20,000 1 %; C 3 %;
  D 6 %; E 50,001-70,000 11 %; F 70,001-100,000 19 %; G 100,001-400,000 25 %; H 400,001-600,000 26 %;
  I 600,001-2,000,000 28 %; J exceeding 2,000,000 30 %; printed tax at each limit 150 / 600 / 1,500 / 3,700 / 9,400 /
  84,400 / 136,400 / 528,400 (checked by `#guard`). This is ITA Schedule 1 Part I.
* "Tax Relief", "Year of Assessment 2025" (hasil_relief.html): 1 "Individual and dependent relatives 9,000";
  14 "Husband / wife / payment of alimony to former wife 4,000 (Restricted)"; 16a "Each unmarried child and under the
  age of 18 years old 2,000"; 17 EPF and life insurance (restricted to 4,000 for EPF); 20 SOCSO 350 (restricted).
* "Rebates" (hasil_rebate.html), s. 6A: "Income Tax Rebates For Resident Individual With Chargeable Income Less Than
  RM35,000", YA 2009 onwards RM400 for the individual, and RM400 more where the husband or wife "does not have any
  total income" (total 800).
Not reached: the EPF Act Third Schedule and the SOCSO/EIS contribution tables (kwsp.gov.my answers 403, perkeso.gov.my
timed out); employee contributions and their reliefs (items 17 and 20) are therefore `unsupported`.
W5 pattern A (2026-11-20): EPF, SOCSO and EIS employee contributions and their reliefs added (input `"w5Contrib": false`
drops them and restores the earlier outputs). Texts in `my/law/w5/` (Wayback captures of the agencies' own copies):
* EPF Act 1991 Third Schedule (KWSP's copy, PDF dated 2022-06-29, captured 2024-07-28): Part A (citizens and PRs until
  60): bands of RM20 to RM5,000 and RM100 to RM20,000, employee amounts = 11 % of the band's upper limit rounded up to
  the ringgit (e.g. "4,900.01 to 4,920.00 ... 542.00", "19,900.01 to 20,000.00 ... 2,200.00"); "for the months where
  the wages exceed RM20,000.00, the contribution by the employee shall be calculated at the rate of 11% ... rounded to
  the next ringgit"; Part E: citizens aged 60 or more, employee 0.00. (The 9 % schedule of 2021 is not in force.)
* Employees' Social Security Act 1969 (Act 4, PERKESO copy as at 1 September 2022) Third Schedule para 2 (first
  category, invalidity and employment injury): employee 10 sen to 2.75 for wages to RM600, then RM3.25 for RM600-700
  rising 50 sen per RM100; Act A1724 (2024; royal assent 11 Sep 2024, s. 3) extends it to items 64-65: "exceed RM5,900
  but not exceed RM6,000 ... RM29.75" and above RM6,000 RM29.75. First Schedule para (12)(ii): invalidity does not
  cover employees aged 60 (second category: employer only).
* Employment Insurance System Act 2017 (Act 800) Second Schedule para 2: employee 5 sen to 50 sen for wages to RM300,
  then 0.2 % of the band's mid-wage (RM0.70 for RM300-400 ...); Act A1725 (2024) s. 3 items 55-65: "exceed RM5,900 but
  not exceed RM6,000 RM11.90", above RM6,000 RM11.90. Items 41-54 (A1657 of 2022) not read: the same rule applied.
  First Schedule para 8: not for employees under 18 or aged 60 or more.
* Both 2024 Acts commence on a date appointed by the Minister (not read); PERKESO's notice "011024 - Pindaan Had
  Maksimum Siling Gaji" (1 Oct 2024, on its contribution page captured 2024-10-16) dates the RM6,000 ceiling; all of
  2025 is after it.
* Reliefs (LHDN YA 2025 table, already in `my/law/`): item 17 EPF "Restricted to RM4,000", item 20 SOCSO 350 (EIS
  counted in it: reading, both are paid to PERKESO).
Monthly wage = annual wages / 12 (whole ringgit), twelve months.
Unit: separate assessment (s. 45 joint election not modelled: never cheaper for two earners under a progressive scale
with per-person reliefs, and the one-earner case is covered by the spouse relief and the double rebate).
-/

namespace MyTax
open TaxKernel

def sched : Schedule := Schedule.ofList [(0, 0), (5000, 100), (20000, 300), (35000, 600), (50000, 1100),
  (70000, 1900), (100000, 2500), (400000, 2600), (600000, 2800), (2000000, 3000)]

/- LHDN's printed tax at each band limit equals the band sums. -/
#guard [(20000, 150), (35000, 600), (50000, 1500), (70000, 3700), (100000, 9400), (400000, 84400),
  (600000, 136400), (2000000, 528400)].all fun (t, base) => sched.ticks t = base * BP

def individualRelief : Int := 9000
def spouseRelief : Int := 4000
def childRelief : Int := 2000
def rebateLimit : Int := 35000
def rebate : Int := 400

/-! ### W5 pattern A: EPF, SOCSO, EIS (monthly, employee share) -/

/-- EPF Third Schedule Part A, employee, ringgit; Part E (aged 60 or more): nil. -/
def epfMonthly (w : Int) (age : Nat) : Int :=
  if age ≥ 60 ∨ w ≤ 10 then 0
  else if w ≤ 5000 then ceilDiv (11 * (ceilDiv w 20 * 20)) 100
  else if w ≤ 20000 then ceilDiv (11 * (ceilDiv w 100 * 100)) 100
  else ceilDiv (11 * w) 100

/-- SOCSO Third Schedule para 2 (first category), employee, sen; ceiling RM6,000 (Act A1724). -/
def socsoSen (w : Int) (age : Nat) : Int :=
  if age ≥ 60 ∨ w ≤ 0 then 0
  else if w ≤ 30 then 10 else if w ≤ 50 then 20 else if w ≤ 70 then 30 else if w ≤ 100 then 40
  else if w ≤ 140 then 60 else if w ≤ 200 then 85
  else (min (ceilDiv w 100 * 100) 6000 - 50) / 2

/-- EIS Second Schedule para 2, employee, sen; ceiling RM6,000 (Act A1725); ages 18 to 59. -/
def eisSen (w : Int) (age : Nat) : Int :=
  if age < 18 ∨ age ≥ 60 ∨ w ≤ 0 then 0
  else if w ≤ 30 then 5 else if w ≤ 50 then 10 else if w ≤ 70 then 15 else if w ≤ 100 then 20
  else if w ≤ 140 then 25 else if w ≤ 200 then 35
  else (min (ceilDiv w 100 * 100) 6000 - 50) / 5

#guard epfMonthly 20 40 = 3 ∧ epfMonthly 4910 40 = 542 ∧ epfMonthly 5150 40 = 572 ∧ epfMonthly 20000 40 = 2200
#guard epfMonthly 30000 40 = 3300 ∧ epfMonthly 5000 60 = 0
#guard socsoSen 650 40 = 325 ∧ socsoSen 5050 40 = 2525 ∧ socsoSen 5950 40 = 2975 ∧ socsoSen 9000 40 = 2975 ∧ socsoSen 150 40 = 85
#guard eisSen 350 40 = 70 ∧ eisSen 5050 40 = 1010 ∧ eisSen 5950 40 = 1190 ∧ eisSen 9000 40 = 1190 ∧ eisSen 5000 60 = 0

/-- Annual employee contributions of one adult: (EPF, SOCSO + EIS), ringgit. -/
def contributions (a : Adult) : Int × Int :=
  if a.wages ≤ 0 then (0, 0) else
  let w := a.wages / 12
  (12 * epfMonthly w a.age, divR .halfUp (12 * (socsoSen w a.age + eisSen w a.age)) 100)

/-- One resident: (tax after the s. 6A rebate(s), chargeable income). `relief`: items 17 and 20 (W5). -/
def person (statutory : Int) (spouseNoIncome : Bool) (nChildren : Nat) (relief : Int := 0) : Int × Int :=
  let ci := pos (statutory - individualRelief - (if spouseNoIncome then spouseRelief else 0) - childRelief * nChildren - relief)
  let t := sched.tax Rule.unitDown ci
  let rb := if ci ≤ rebateLimit then rebate + (if spouseNoIncome then rebate else 0) else 0
  (pos (t - rb), ci)

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let idx := List.range c.adults.length
  let stat (a : Adult) (i : Nat) : Int := pos a.wages + pos a.selfEmployment + pos (share c.rentalIncome i)
  let stats := (c.adults.zip idx).map fun (a, i) => stat a i
  let top : Nat := match stats with
    | [x0, x1] => if x1 > x0 then 1 else 0
    | _ => 0
  let kids : Nat := c.childrenUnder 18
  let w5 := (c.bool? "w5Contrib").getD true
  let ctb := c.adults.map fun a => if w5 then contributions a else (0, 0)
  let reliefOf (i : Nat) : Int := match ctb[i]? with
    | some (e, s) => min e 4000 + min s 350
    | none => 0
  let rs := (stats.zip idx).map fun (x, i) =>
    let spNo := c.isCouple ∧ (stats.zip idx).all (fun (y, j) => j = i ∨ y ≤ 0) ∧ x > 0
    person x spNo (if i = top then kids else 0) (reliefOf i)
  let epf := sumInts (ctb.map (·.1))
  let socso := sumInts (ctb.map (·.2))
  Out.make c "MY" "MYR" (sumInts (rs.map (·.1))) (employeeSocial := epf + socso)
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.2))), Out.d "epf" epf, Out.d "socsoEis" socso,
      Out.dStr "note" "child relief claimed by the higher earner; rental income taken as statutory (net) income"])
    (unsupported := (if c.adults.any (fun a => a.wages > 0) ∧ !w5 then ["EPF, SOCSO and EIS employee contributions and their reliefs (items 17, 20): contribution schedules not reached"] else []) ++
      (if c.interest ≠ 0 ∨ c.dividends ≠ 0 then ["interest and dividends: Schedule 6 exemptions and the dividend tax not read (ITA text not reached)"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: RPGT / CGT regimes not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: exemption conditions not read"] else []))

def country : Country := { code := "MY", name := "Malaysia (YA 2025)", currency := "MYR", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- The s. 6A rebate ends at RM35,000 of chargeable income: one ringgit more costs RM400 (a notch). -/
#guard (person (35000 + 9000 + 1) false 0).1 - (person (35000 + 9000) false 0).1 = 400

end MyTax
