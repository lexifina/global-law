import LegalProofs.Basic

/-!
# Real calendar dates

`Date` is a `YYYYMMDD` number, so some numbers between two real dates are not dates at all (`20251299`). That made a
naive "retroactive from 1 January 2026" theorem false (Lean found the counterexample). Here a `ValidDate` carries a real
year, month and day, and theorems can range over real dates only.
-/

namespace Legal

def daysIn (y m : Nat) : Nat :=
  if m = 2 then (if (y % 4 = 0 ∧ y % 100 ≠ 0) ∨ y % 400 = 0 then 29 else 28)
  else if m = 4 ∨ m = 6 ∨ m = 9 ∨ m = 11 then 30 else 31

/-- A real calendar date. -/
structure ValidDate where
  y : Nat
  m : Nat
  d : Nat
  hm : 1 ≤ m ∧ m ≤ 12
  hd : 1 ≤ d ∧ d ≤ daysIn y m

/-- The `YYYYMMDD` number of a real date. -/
def ValidDate.num (v : ValidDate) : Date := v.y * 10000 + v.m * 100 + v.d

theorem daysIn_le (y m : Nat) : daysIn y m ≤ 31 := by
  unfold daysIn; split <;> (try split) <;> (try split) <;> omega

/-- No real date falls strictly between 31 December of one year and 1 January of the next. -/
theorem no_date_between_years (v : ValidDate) (y : Nat) :
    ¬ (y * 10000 + 1231 < v.num ∧ v.num < (y + 1) * 10000 + 101) := by
  have h1 := v.hm; have h2 := v.hd; have h3 := daysIn_le v.y v.m
  unfold ValidDate.num
  omega

/-- **Gap closure, over real dates.** An extension made retroactive from 1 January of the year after the old end date
(31 December) binds on every real date in the combined period. -/
theorem retroactive_jan1_closes_gap (y newUntil : Nat) (v : ValidDate)
    (hv : v.num ≤ newUntil) :
    ({ endsOn := y * 10000 + 1231, extendedFrom := (y + 1) * 10000 + 101, newUntil := newUntil } : Extension).binds
      v.num = true := by
  have := no_date_between_years v y
  by_cases h : v.num ≤ y * 10000 + 1231
  · simp [Extension.binds, h]
  · have : (y + 1) * 10000 + 101 ≤ v.num := by omega
    simp [Extension.binds, h, this, hv]

/-- The Swiss case with the extension the Federal Council suggested: retroactive from 1 January 2026. -/
example (v : ValidDate) (hv : v.num ≤ 20301231) :
    ({ endsOn := 20251231, extendedFrom := 20260101, newUntil := 20301231 } : Extension).binds v.num = true :=
  retroactive_jan1_closes_gap 2025 20301231 v hv

end Legal
