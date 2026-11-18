import JpTax.Basic

/-!
# 児童手当 (児童手当法, as amended by 令和6年法律第47号 from October 2024)

Monthly amounts (第6条第3項): "三歳未満児童算定額は一万五千円とし、三歳以上児童算定額は一万円とし、第三子以降算定額は
三万円とする". No income limit (the 所得制限 was abolished from October 2024). A 児童 is one "十八歳に達する日以後の最初の
三月三十一日までの間にある者" (第3条第1項); for the birth order, children up to "二十二歳に達する日以後の最初の三月三十一日"
whom the parent supports also count (第6条第2項第2号, 第三子以降算定額算定対象者).

Convention: a child's age is its age on 31 December 2025 and is taken as its age all year; children aged 0–18 are
支給対象児童, those aged 19–22 count for the order only (they are taken to be supported by the parents). The yearly
amount is 12 months of the monthly amount.
-/

namespace JpTax

/-- **第6条第1項第1号, the table**, by the counts `a` (第三子以降算定額算定対象者: 19–22), `b` (三歳以上支給対象児童) and
`c` (三歳未満支給対象児童). Each row copied from the statute. -/
def teateTable (a b c : Nat) : Int :=
  let u : Int := 15000   -- 三歳未満児童算定額
  let o : Int := 10000   -- 三歳以上児童算定額
  let t : Int := 30000   -- 第三子以降算定額
  if a = 0 then
    if b = 0 then
      (if c = 0 then 0 else if c = 1 then u else u * 2 + t * ((c : Int) - 2))
    else if b = 1 then
      (if c = 0 then o else o + u + t * ((c : Int) - 1))
    else o * 2 + t * ((b : Int) - 2) + t * c
  else if a = 1 then
    if b = 0 then (if c = 0 then 0 else u + t * ((c : Int) - 1))
    else o + t * ((b : Int) - 1) + t * c
  else t * ((b : Int) + c)

/-- The same rule written as birth order: rank the counted children from the oldest; the first two ranks get 10,000
yen (aged 3–18) or 15,000 yen (under 3), the third and later 30,000 yen; ranks held by 19–22-year-olds pay nothing. -/
def teateRank (a b c : Nat) : Int :=
  let bLow : Int := max 0 (min (b : Int) (2 - (a : Int)))
  let cLow : Int := max 0 (min (c : Int) (2 - (a : Int) - (b : Int)))
  10000 * bLow + 30000 * ((b : Int) - bLow) + 15000 * cLow + 30000 * ((c : Int) - cLow)

/-- **The statute's table is the birth-order rule**, for every family. -/
theorem teateTable_eq_rank (a b c : Nat) : teateTable a b c = teateRank a b c := by
  unfold teateTable teateRank
  by_cases ha0 : a = 0
  · subst ha0
    by_cases hb0 : b = 0
    · subst hb0
      by_cases hc0 : c = 0
      · subst hc0; decide
      · by_cases hc1 : c = 1
        · subst hc1; decide
        · simp only [hc0, hc1, ite_false, ite_true]; omega
    · by_cases hb1 : b = 1
      · subst hb1
        by_cases hc0 : c = 0
        · subst hc0; decide
        · simp only [hc0, ite_false, ite_true]; omega
      · simp only [hb0, hb1, ite_false, ite_true]; omega
  · by_cases ha1 : a = 1
    · subst ha1
      by_cases hb0 : b = 0
      · subst hb0
        by_cases hc0 : c = 0
        · subst hc0; decide
        · simp only [hc0, ite_false, ite_true]; omega
      · simp only [hb0, ite_false, ite_true]; omega
    · simp only [ha0, ha1, ite_false]; omega

/-- Monthly amount for children of the given ages (31 December 2025). -/
def teateMonthly (ages : List Int) : Int :=
  let a := (ages.filter (fun x => decide (19 ≤ x ∧ x ≤ 22))).length
  let b := (ages.filter (fun x => decide (3 ≤ x ∧ x ≤ 18))).length
  let c := (ages.filter (fun x => decide (0 ≤ x ∧ x < 3))).length
  teateTable a b c

/-- 児童手当 for 2025: twelve months (第8条第4項 pays them in six instalments). -/
def teateYear (ages : List Int) : Int := 12 * teateMonthly ages

end JpTax
