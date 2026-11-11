import LegalProofs.USTax.TaxCourt.FilingStatus

/-!
# §32 earned income credit, tax years 2012–2024

Amounts: the year's §32(b) figures (`Params.eic`), applied through the IRS EIC Table (§32(f)(1)) with the same
reconstruction as the 2025 model (`TaxCode.Individual.D.eicTab`: each $50 line is the credit at its midpoint, a line
straddling a kink shows the maximum), and EIC Worksheet A's rule (look up earned income; if AGI is at or above the
threshold, also AGI, and take the smaller). `eicStatuteAmount` gives the exact statutory formula for comparison.

Eligibility by year (§32(c)(1), (c)(3), (d), (i), (m), and for 2021 §32(n) as added by ARPA §§9621–9624):

| rule | 2012–2020 | 2021 | 2022–2024 |
|---|---|---|---|
| childless age (at year end) | 25–64 | 19+ (24+ for a specified student, 18+ former foster or homeless youth), no upper limit | 25–64 |
| childless phase-in/out | 7.65% | 15.3% (§32(n)) | 7.65% |
| married filing separately | barred (§32(d)) | allowed for a separated spouse with a qualifying child (§32(d)(2), ARPA §9623) | same as 2021 |
| qualifying children without SSNs | they block the childless credit | childless credit allowed (§32(c)(1)(F), ARPA §9622) | same as 2021 |
| investment-income limit | indexed $3,400–$3,650 | $10,000 (§9624) | indexed from $10,000 |

Not modelled: §32(k) disallowance periods (an input flag), nontaxable combat pay election, the §32(c)(2)(B) exclusions
from earned income other than as found, and U.S. possessions.
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual TaxCode.Individual.D

/-- §32(c)(3): a qualifying child for the EIC — §152(c) "determined without regard to paragraph (1)(D) thereof and
section 152(e)" (no support test; a release to the other parent does not move the child), whose principal place of
abode is in the United States; a married child only if the taxpayer may claim him as a dependent (§32(c)(3)(B)). The
SSN requirement (§32(c)(3)(D)) is applied separately in `eicChildCounts`. -/
def eicQualifyingChild (p : Params) (x : PersonFacts) : Bool :=
  qualifyingChild p.year x { supportTest := false, use152e := false } && x.abodeInUS &&
    (!x.married || isDependent p false { x with releasedToOtherParent := false })

/-- (children with a valid SSN, qualifying children without one). -/
def eicChildCounts (p : Params) (deps : List PersonFacts) : Nat × Nat :=
  let qcs := deps.filter (eicQualifyingChild p)
  ((qcs.filter (·.hasSSN)).length, (qcs.filter (!·.hasSSN)).length)

/-- What the EIC reads about the taxpayer beyond the dependents. -/
structure EicFacts where
  filing : Filing
  earnedIncome : Int
  agi : Int
  /-- §32(i)(2) disqualified income: interest (taxable and exempt), dividends, net rents and royalties, capital gain
  net income, net passive income. -/
  disqualifiedIncome : Int := 0
  taxpayerAge : Nat := 30
  spouseAge : Option Nat := none
  /-- Taxpayer (and, on a joint return, spouse) has an SSN valid for employment (§32(m)). -/
  taxpayerSSN : Bool := true
  /-- The taxpayer is the qualifying child of another taxpayer (§32(c)(1)(B)). -/
  qualifyingChildOfAnother : Bool := false
  /-- The taxpayer can be claimed as a dependent (§32(c)(1)(A)(ii)(III)). -/
  canBeClaimedAsDependent : Bool := false
  /-- Principal place of abode in the U.S. for more than half the year (§32(c)(1)(A)(ii)(I)). -/
  abodeInUS : Bool := true
  /-- 2021: a "specified student" (§32(n)(1)(B)(ii)): needs age 24. -/
  specifiedStudent : Bool := false
  /-- 2021: a qualified former foster youth or qualified homeless youth (§32(n)(1)(C)): age 18 suffices. -/
  fosterOrHomelessYouth : Bool := false
  /-- 2021+: §32(d)(2) separated spouse (lived apart the last six months, or legally separated under a written
  agreement or decree and not in the same household at year end), with a qualifying child living with the taxpayer
  more than half the year. -/
  separatedSpouse : Bool := false
  /-- Barred by §32(k) (two- or ten-year disallowance after reckless or fraudulent claims). -/
  disallowed32k : Bool := false
  deriving Repr, Inhabited

/-- §32(c)(1)(A)(ii)(II) and, for 2021, §32(n)(1): the age window for a taxpayer with no qualifying child. -/
def childlessAgeOk (p : Params) (f : EicFacts) (age : Nat) : Bool :=
  if p.year == 2021 then
    let minAge := if f.fosterOrHomelessYouth then 18 else if f.specifiedStudent then 24 else 19
    minAge ≤ age
  else 25 ≤ age && age < 65

/-- The IRS EIC Table rule (Pub. 596), generalising `TaxCode.Individual.D.eicTab`: zero at or past the completed
phase-out; a $50 line with a kink strictly inside shows the (rounded) maximum; otherwise the credit at the line's
midpoint, rounded to the dollar. `mx10k` is the maximum used in the phase-out, in 1/10,000 dollars: the 2016–2023
tables use the unrounded credit percentage × earned income amount, the 2024 (and 2025) tables the rounded maximum
(see the findings in `LegalProofs/USTax/TaxCourt.lean`; e.g. 2016, three children, $27,350–27,400: $4,334 printed, $4,335 with the rounded $6,269). -/
def eicTabY (cp pp eia thr mx mx10k co : Int) (x : Int) : Int :=
  if x ≤ 0 ∨ co ≤ x then 0 else
  let a := x / 50 * 50
  let b := min (a + 50) co
  if (a < eia ∧ eia < b) ∨ (a < thr ∧ thr < b) then mx else
  let m := a + b
  let v := max 0 (min (cp * m) (2 * mx10k - pp * max 0 (m - 2 * thr)))
  (v + 10000) / 20000

/-- Whether the year's EIC Table phases out from the unrounded maximum (2016–2023) or the rounded one (2024). -/
def Params.eicUnroundedMax (p : Params) : Bool := p.year ≤ 2023

/-- The EIC Table amount for column `k` (0–3 children), joint or not, at amount `x`. -/
def eicTableAmount (p : Params) (k : Nat) (joint : Bool) (x : Int) : Int :=
  let e := p.eic k
  eicTabY e.cp e.pp e.eia (e.thr joint) e.maxCredit
    (if p.eicUnroundedMax then e.cp * e.eia else 10000 * e.maxCredit) (e.co joint) x

/-- With the rounded maximum, `eicTabY` is exactly the 2025 model's `eicTab`. -/
theorem eicTabY_rounded (cp pp eia thr mx co x : Int) :
    eicTabY cp pp eia thr mx (10000 * mx) co x = eicTab cp pp eia thr mx co x := by
  unfold eicTabY eicTab
  simp only
  split
  · rfl
  · split
    · rfl
    · congr 2; omega

/-- EIC Worksheet A, lines 1–6. -/
def eicWorksheetAmount (p : Params) (k : Nat) (joint : Bool) (earned agi : Int) : Int :=
  if agi < (p.eic k).thr joint then eicTableAmount p k joint earned
  else min (eicTableAmount p k joint earned) (eicTableAmount p k joint agi)

/-- §32(a)–(b) exactly (no table), rounded to the dollar. -/
def eicStatuteAmount (p : Params) (k : Nat) (joint : Bool) (earned agi : Int) : Int :=
  let e := p.eic k
  roundDollar (eicScaled e.cp e.pp e.eia (e.thr joint) earned agi) 10000

/-- **The credit**, with the reasons for any denial. `kids` = (qualifying children with SSNs, without). -/
def eicAmount (p : Params) (f : EicFacts) (kids : Nat × Nat) : Int × List String :=
  let withSSN := kids.1
  let withoutSSN := kids.2
  let joint := f.filing == .mfj
  let failures : List String :=
    (if f.disallowed32k then ["§32(k) disallowance period"] else []) ++
    (if f.taxpayerSSN then [] else ["§32(m) taxpayer identification (SSN)"]) ++
    (if f.qualifyingChildOfAnother then ["§32(c)(1)(B) taxpayer is a qualifying child of another"] else []) ++
    (if f.filing == .mfs && !(p.year ≥ 2021 && f.separatedSpouse && withSSN + withoutSSN > 0)
      then ["§32(d) married filing separately"] else []) ++
    (if f.disqualifiedIncome > p.eicInvLimit then [s!"§32(i) disqualified income over ${p.eicInvLimit}"] else []) ++
    (if withSSN > 0 then []
     else
      (if withoutSSN > 0 && p.year < 2021 then ["§32(c)(1)(A)(ii): has a qualifying child without an SSN"] else []) ++
      (if childlessAgeOk p f f.taxpayerAge || (joint && (f.spouseAge.map (childlessAgeOk p f)).getD false) then []
       else ["§32(c)(1)(A)(ii)(II) age (no qualifying child)"]) ++
      (if f.abodeInUS then [] else ["§32(c)(1)(A)(ii)(I) U.S. abode"]) ++
      (if f.canBeClaimedAsDependent then ["§32(c)(1)(A)(ii)(III) dependent of another"] else []))
  if failures.isEmpty then (eicWorksheetAmount p (min 3 withSSN) joint f.earnedIncome f.agi, [])
  else (0, failures)

/-! ## Tests: Pub. 596 and EIC Table figures for each year -/

section
private def py (y : Nat) : Params := (params? y).getD default

-- Every year: the maximum credit is reached exactly at the earned income amount (Rev. Proc. tables), and the table
-- gives $0 at the completed phase-out amount.
#guard years.all fun y => [0, 1, 2, 3].all fun k =>
  let e := (py y).eic k
  eicTableAmount (py y) k false e.eia == e.maxCredit && eicTableAmount (py y) k true (e.co true) == 0 &&
  eicTableAmount (py y) k false (e.co false) == 0

-- EIC Tables as printed (Pub. 596; columns: no child, 1, 2, 3 — single/HoH, then MFJ):
-- 2016, $9,800–9,850: 387 / 3,341 / 3,930 / 4,421 ; MFJ 506 / 3,341 / 3,930 / 4,421
#guard [0, 1, 2, 3].map (eicTableAmount (py 2016) · false 9800) = [387, 3341, 3930, 4421]
#guard [0, 1, 2, 3].map (eicTableAmount (py 2016) · true 9800) = [506, 3341, 3930, 4421]
-- 2016, $27,350–27,400: 0 / 1,905 / 3,638 / 4,334 ; MFJ 0 / 2,792 / 4,806 / 5,503
#guard [0, 1, 2, 3].map (eicTableAmount (py 2016) · false 27350) = [0, 1905, 3638, 4334]
#guard [0, 1, 2, 3].map (eicTableAmount (py 2016) · true 27350) = [0, 2792, 4806, 5503]
-- 2021 (ARPA childless column), $9,800–9,850: 1,502 ; $15,000–15,050: 980 single, 1,502 joint
#guard eicTableAmount (py 2021) 0 false 9800 = 1502 ∧ eicTableAmount (py 2021) 0 false 15000 = 980
#guard eicTableAmount (py 2021) 0 true 15000 = 1502
-- 2024, $15,000–15,050: 273 / 4,213 / 6,010 / 6,761 ; MFJ 632 / 4,213 / 6,010 / 6,761
#guard [0, 1, 2, 3].map (eicTableAmount (py 2024) · false 15000) = [273, 4213, 6010, 6761]
#guard [0, 1, 2, 3].map (eicTableAmount (py 2024) · true 15000) = [632, 4213, 6010, 6761]
-- 2024, $27,350–27,400: 0 / 3,469 / 5,980 / 6,850 ; MFJ 0 / 4,213 / 6,960 / 7,830
#guard [0, 1, 2, 3].map (eicTableAmount (py 2024) · false 27350) = [0, 3469, 5980, 6850]
#guard [0, 1, 2, 3].map (eicTableAmount (py 2024) · true 27350) = [0, 4213, 6960, 7830]

-- Eligibility by year: a 22-year-old with no child gets nothing in 2020 or 2022, but the credit in 2021 (§32(n)).
#guard (eicAmount (py 2020) { filing := .single, earnedIncome := 9000, agi := 9000, taxpayerAge := 22 } (0, 0)).1 = 0
#guard (eicAmount (py 2021) { filing := .single, earnedIncome := 9800, agi := 9800, taxpayerAge := 22 } (0, 0)).1 = 1502
#guard (eicAmount (py 2022) { filing := .single, earnedIncome := 9000, agi := 9000, taxpayerAge := 22 } (0, 0)).1 = 0
-- A 66-year-old: barred except in 2021.
#guard (eicAmount (py 2021) { filing := .single, earnedIncome := 9800, agi := 9800, taxpayerAge := 66 } (0, 0)).1 = 1502
#guard (eicAmount (py 2019) { filing := .single, earnedIncome := 6920, agi := 6920, taxpayerAge := 66 } (0, 0)).1 = 0
-- Married filing separately with a qualifying child, living apart: barred in 2020, allowed in 2022.
#guard (eicAmount (py 2020) { filing := .mfs, earnedIncome := 15000, agi := 15000, separatedSpouse := true } (1, 0)).1 = 0
#guard (eicAmount (py 2022) { filing := .mfs, earnedIncome := 15000, agi := 15000, separatedSpouse := true } (1, 0)).1
  = eicTableAmount (py 2022) 1 false 15000
-- Investment income one dollar over the limit removes the whole credit (2019: $3,600).
#guard (eicAmount (py 2019) { filing := .single, earnedIncome := 15000, agi := 15000, disqualifiedIncome := 3600 } (2, 0)).1
  = eicTableAmount (py 2019) 2 false 15000
#guard (eicAmount (py 2019) { filing := .single, earnedIncome := 15000, agi := 15000, disqualifiedIncome := 3601 } (2, 0)).1
  = 0
end

end Legal.USTax.TaxCourt
