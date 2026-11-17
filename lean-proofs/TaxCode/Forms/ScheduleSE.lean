import TaxCode.Individual.A.SelfEmployment

/-!
# Schedule SE (2025) Part I and Form 8959 (2025) against §§1401–1402, §3101(b)(2)

Form text: Schedule SE (Form 1040) 2025 (irs.gov/pub/irs-prior/f1040sse--2025.pdf) Part I lines 3–13 (regular
method; no church employee income, no optional method); Form 8959 (2025) Parts I–II lines 1–13 and 18.

Statute: §1401(a), (b)(1); §1402(a)(12), (b)(1), (b)(2); §1401(b)(2) and §3101(b)(2) via
`TaxCode.Individual.A.SelfEmployment`. Amounts in ten-thousandths of a dollar (92.35% exact); the tax in
ten-millionths (12.4% = 124/1000), as the model keeps them; both are rounded once to the dollar at the end.
-/

namespace TaxCode.Forms.ScheduleSE
open TaxCode.Individual TaxCode.Individual.A

/-! ## Schedule SE -/

/-- Line 4a: "If line 3 is more than zero, multiply line 3 by 92.35% (0.9235). Otherwise, enter amount from line 3"
(×10000). -/
def l4a (l3 : Int) : Int := if l3 > 0 then 9235 * l3 else 10000 * l3
/-- Line 4c: "Combine lines 4a and 4b [optional methods: none]. If less than $400, stop; you don't owe
self-employment tax." Line 6: "Add lines 4c and 5b [church income: none]". -/
def l6 (l3 : Int) : Int := if l4a l3 < 400 * 10000 then 0 else l4a l3
/-- Line 7: "Maximum amount of combined wages and self-employment earnings subject to social security tax ... for
2025": $176,100. Lines 8a–8d: social security wages and tips (W-2 boxes 3 and 7, Form 4137, Form 8919). Line 9:
"Subtract line 8d from line 7. If zero or less, enter -0-". -/
def l9 (ssWages : Int) : Int := max 0 (176100 - ssWages)
/-- Lines 10–12 (×10,000,000): "Multiply the smaller of line 6 or line 9 by 12.4%", "Multiply line 6 by 2.9%",
"Add lines 10 and 11". -/
def l12x (l3 ssWages : Int) : Int := 124 * min (l6 l3) (10000 * l9 ssWages) + 29 * l6 l3

/-- **Schedule SE line 12 is §1401(a) + (b)(1) exactly, for every profit and wage amount** (before the single
rounding to dollars that both make). -/
theorem l12_eq_statute (l3 w : Int) :
    l12x l3 w = 124 * oasdiBase10k l3 w + 29 * seIncome10k l3 ∧
      roundDollar (l12x l3 w) 10000000 = seTaxCore l3 w := by
  have h : l12x l3 w = 124 * oasdiBase10k l3 w + 29 * seIncome10k l3 := by
    unfold l12x l6 l4a l9 oasdiBase10k seIncome10k nese10k wageBase2025
    split <;> split <;> omega
  exact ⟨h, by unfold seTaxCore; rw [h]⟩

/-- Line 13: "Deduction for one-half of self-employment tax. Multiply line 12 by 50%" = §164(f). -/
theorem l13_eq_statute (l3 w : Int) : roundDollar (l12x l3 w) 20000000 = halfSeTaxCore l3 w := by
  unfold halfSeTaxCore; rw [(l12_eq_statute l3 w).1]

/-! ## Form 8959 -/

/-- Lines 5, 9: "Married filing jointly $250,000; Married filing separately $125,000; Single, Head of household, or
Qualifying surviving spouse $200,000". -/
def thr8959 : Filing → Int
  | .mfj => 250000
  | .mfs => 125000
  | _ => 200000

/-- Form 8959 lines 4–13 (×10,000,000): line 6 "Subtract line 5 from line 4. If zero or less, enter -0-"; line 7
"Multiply line 6 by 0.9%"; line 8 Schedule SE line 6 ("If you had a loss, enter -0-"); line 11 "Subtract line 10
[= line 4] from line 9. If zero or less, enter -0-"; line 12 "Subtract line 11 from line 8. If zero or less, enter
-0-"; line 13 "Multiply line 12 by 0.9%"; line 18 adds lines 7 and 13 (no RRTA). `seInc10k` is Schedule SE line 6
(×10,000). -/
def l18x (f : Filing) (medicareWages seInc10k : Int) : Int :=
  let l6 := max 0 (medicareWages - thr8959 f)
  let l8 := max 0 seInc10k
  let l11 := max 0 (thr8959 f - medicareWages)
  let l12 := max 0 (l8 - 10000 * l11)
  9 * (10000 * l6) + 9 * l12

/-- **Form 8959 line 18 is §3101(b)(2) + §1401(b)(2) exactly, for all wages and self-employment income** (the model
rounds once; so does the form's total, to whole dollars). -/
theorem l18_eq_statute (f : Filing) (w s : Int) (hs : 0 ≤ s) :
    roundDollar (l18x f w s) 10000000 = additionalMedicareCore f w s := by
  have ht : thr8959 f = amtThreshold f := by cases f <;> rfl
  unfold l18x additionalMedicareCore; rw [ht]; dsimp only
  congr 1; omega

end TaxCode.Forms.ScheduleSE

#print axioms TaxCode.Forms.ScheduleSE.l12_eq_statute
#print axioms TaxCode.Forms.ScheduleSE.l18_eq_statute
