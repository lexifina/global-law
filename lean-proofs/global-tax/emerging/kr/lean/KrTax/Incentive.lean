import KrTax.Basic
import KrTax.IncentiveData
import KrTax.IncentiveData2023

/-!
# 근로장려금 and 자녀장려금 (조세특례제한법 §100의2–§100의13, §100의27–§100의31)

Refundable: a decided 장려금 "is deemed tax already paid" (STA §100의7④) and is paid out. The statute gives each a
formula (§100의5①, §100의29①) and then says the amount is read from a banded 산정표 (§100의5⑤ "근로장려금은
총급여액 등의 구간별로 작성한 대통령령으로 정하는 근로장려금산정표를 적용하여 산정한다", §100의29②): the tables in
`IncentiveData` are the law; `eitcFormula`/`ctcFormula` are the formulas they are checked against
(`Theorems.lean`, FINDINGS F3–F4). Asset tests (§100의3①4: 재산 < 2억4천만원; ≥ 1억7천만원 halves) are assumed met.
-/

namespace KrTax
open TaxKernel

/-- Household type (STA §100의3⑤): 0 = 단독가구, 1 = 홑벌이 가구, 2 = 맞벌이 가구. -/
abbrev Kind := Nat

/-- §100의5① formula, exact as a fraction `num / den` of won: 단독 "총급여액등 × 400분의165" below 400만원, 165만원
to 900만원, "165만원 − (총급여액등 − 900만원) × 1천300분의165" to 2천200만원; 홑벌이 700분의285 / 285만원 /
1천800분의285 (700만, 1천400만, 3천200만원); 맞벌이 800분의330 / 330만원 / 2천700분의330 (800만, 1천700만,
4천400만원). Returned as (numerator, denominator). -/
def eitcFormula (k : Kind) (x : Int) : Int × Int :=
  let (a, b, mx, pn, pd, sd, e) : Int × Int × Int × Int × Int × Int × Int :=
    if k = 0 then (4000000, 9000000, 1650000, 165, 400, 13000000, 22000000)
    else if k = 1 then (7000000, 14000000, 2850000, 285, 700, 18000000, 32000000)
    else (8000000, 17000000, 3300000, 330, 800, 27000000, 44000000)
  if x < 0 then (0, 1)
  else if x < a then (x * pn, pd)
  else if x < b then (mx, 1)
  else if x < e then (mx * sd - (x - b) * mx, sd)
  else (0, 1)

/-- §100의29① formula (per child): 홑벌이 "100만원 − (총급여액등 − 2천100만원) × 4천900분의50" from 2천100만원,
맞벌이 "… − (총급여액등 − 2천500만원) × 4천500분의50" from 2천500만원, below 7천만원. -/
def ctcFormula (k : Kind) (x : Int) : Int × Int :=
  let (st, den) : Int × Int := if k = 1 then (21000000, 49000000) else (25000000, 45000000)
  if x < st then (1000000, 1)
  else if x < 70000000 then (1000000 * den - (x - st) * 500000, den)
  else (0, 1)

/-- The 산정표 entry for `x` (총급여액 등) in column `k`: the row with 이상 ≤ x < 미만; 0 when no row ("-", outside the
table) or "해당 없음". -/
def eitcTable (k : Kind) (x : Int) : Int :=
  match eitcRows.find? (fun r => decide (r.1 ≤ x ∧ x < r.2.1)) with
  | some (_, _, a, b, c) => max 0 (if k = 0 then a else if k = 1 then b else c)
  | none => 0

def ctcTable (k : Kind) (x : Int) : Int :=
  match ctcRows.find? (fun r => decide (r.1 ≤ x ∧ x < r.2.1)) with
  | some (_, _, a, b) => max 0 (if k = 1 then a else if k = 2 then b else 0)
  | none => 0

/-- End of the phase-in (가목) segment. -/
def eitcPhaseInEnd (k : Kind) : Int := if k = 0 then 4000000 else if k = 1 then 7000000 else 8000000

/-- STA §100의7③ (결정): an amount under 1만5천원 is nil; in the phase-in (§100의5① 가목) an amount of 1만5천원 to
10만원 is raised to 10만원; in the phase-out (다목) 1만5천원 to 3만원 is raised to 3만원. -/
def eitcDecide (k : Kind) (x v : Int) : Int :=
  if v < 15000 then 0
  else if x < eitcPhaseInEnd k ∧ v < 100000 then 100000
  else if x ≥ eitcPhaseInEnd k ∧ v < 30000 then 30000
  else v

/-- 근로장려금 of a household of kind `k` with 총급여액 등 `x` and 연간 총소득 `tot` (§100의3①2: total income below
the 총소득기준금액). -/
def eitcTableY (y : Int) (k : Kind) (x : Int) : Int :=
  if y = 2022 ∨ y = 2023 then
    match eitcRows2023.find? (fun r => decide (r.1 ≤ x ∧ x < r.2.1)) with
    | some (_, _, a, b, c) => max 0 (if k = 0 then a else if k = 1 then b else c)
    | none => 0
  else eitcTable k x

def ctcTableY (y : Int) (k : Kind) (x : Int) : Int :=
  if y = 2022 then
    match ctcRows2023.find? (fun r => decide (r.1 ≤ x ∧ x < r.2.1)) with
    | some (_, _, a, b) => max 0 (if k = 1 then a else if k = 2 then b else 0)
    | none => 0
  else ctcTable k x

def eitc (k : Kind) (x tot : Int) (y : Int := 2025) : Int :=
  if tot < eitcLimitY y k then eitcDecide k x (eitcTableY y k x) else 0

/-- 자녀장려금 for `n` 부양자녀 (§100의28: 총소득 < 7천만원; 단독가구 has no child): the table amount per child × n, less
the 자녀세액공제 the claimant or spouse received (STAD §100의31②, from §100의30② "중복하여 적용할 수 없다"); a
remainder under 3만원 but above 0 is raised to 3만원 (STA §100의31②). -/
def ctc (k : Kind) (n : Nat) (x tot childCreditTaken : Int) (y : Int := 2025) : Int :=
  if n = 0 ∨ k = 0 ∨ tot ≥ ctcLimitY y then 0
  else
    let gross := ctcTableY y k x * n
    let net := gross - childCreditTaken
    if net ≤ 0 then 0 else if net < 30000 then 30000 else net

end KrTax
