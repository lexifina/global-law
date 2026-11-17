import TaxCode.Individual.C.AMT

/-!
# Form 6251 (2025) Part II, lines 4–11, against §55 (what the model covers)

Form text: Form 6251 (2025) lines 4–11; 2025 Instructions for Form 6251, line 4 (married filing separately over
$900,350: "include 25% of the excess of the amount on line 4 over $900,350" up to "$68,500"), "Exemption Worksheet—
Line 5" (lines 1–6 and the Note: AMTI at or above $978,750 / $1,800,700 / $900,350: exemption zero), line 7 ("If line
6 is $239,100 or less ($119,550 ... separately), multiply line 6 by 26%. Otherwise, multiply line 6 by 28% and
subtract $4,782 ($2,391 ...)"), lines 8–11 (no AMT foreign tax credit).

Statute: §55(b)(1)(A), (d)(1)–(2) (2025 amounts, Rev. Proc. 2024-40 §2.11) via `TaxCode.Individual.C.AMT`
(sixteenths of a dollar for AMTI; 1/1600 dollar for tax). Domain: no capital gain (Part III not used), no AMTFTC.
Part I (line 1b = taxable income + the Schedule 1-A line 37 senior deduction; line 2a taxes or the standard
deduction) is the model's `amtiBase`.
-/

namespace TaxCode.Forms.Form6251
open TaxCode.Individual TaxCode.Individual.C

/-- Line 4 for a separate filer (instructions): 25% of the excess over $900,350, at most $68,500; in sixteenths. -/
def l4Q (f : Filing) (amti : Int) : Int :=
  16 * amti + (if f = .mfs then min (4 * max 0 (amti - 900350)) (16 * 68500) else 0)

/-- Exemption Worksheet lines 1–6 in sixteenths: line 1 $88,100 / $137,000 / $68,500; line 3 $626,350 / $1,252,700 /
$626,350; line 4 "Subtract line 3 from line 2. If zero or less, enter -0-"; line 5 "Multiply line 4 by 25%"; line 6
"Subtract line 5 from line 1. If zero or less, enter -0-". -/
def l5Q (f : Filing) (aQ : Int) : Int :=
  let w1 := match f with | .single | .hoh => 88100 | .mfj | .qss => 137000 | .mfs => 68500
  let w3 := match f with | .mfj | .qss => 1252700 | _ => 626350
  max 0 (16 * w1 - max 0 (aQ - 16 * w3) / 4)

/-- Line 6: "Subtract line 5 from line 4. If ... zero or less, enter -0-". -/
def l6Q (f : Filing) (amti : Int) : Int := max 0 (l4Q f amti - l5Q f (l4Q f amti))

/-- Line 7 (1/1600 dollar). -/
def l7 (f : Filing) (x : Int) : Int :=
  let brk := if f = .mfs then 119550 else 239100
  let sub := if f = .mfs then 2391 else 4782
  if x ≤ 16 * brk then 26 * x else 28 * x - 1600 * sub

/-- Line 11: "Subtract line 10 from line 9. If zero or less, enter -0-" (line 9 = line 7; line 10 the regular tax,
here in 1/1600 dollar). -/
def l11 (f : Filing) (amti reg1600 : Int) : Int := max 0 (l7 f (l6Q f amti) - reg1600)

/-- **Form 6251 lines 4–7 are §55(b)(1)(A) and (d) exactly for every AMTI ≥ 0 and filing status** (no gains). -/
theorem l7_eq_statute (f : Filing) (amti : Int) (h : 0 ≤ amti) : l7 f (l6Q f amti) = tmtOrdQ f amti := by
  have e4 : l4Q f amti = amtiQ f amti := by
    unfold l4Q amtiQ mfsAddBackQ amtZeroPoint amtThreshold amtExemption; cases f <;> simp
  have e5 : ∀ a, l5Q f a = exemptionQ f a := by
    intro a; unfold l5Q exemptionQ amtExemption amtThreshold; cases f <;> rfl
  unfold tmtOrdQ taxableExcessQ l6Q; rw [e4, e5]
  have : 0 ≤ max 0 (amtiQ f amti - exemptionQ f (amtiQ f amti)) := by omega
  generalize max 0 (amtiQ f amti - exemptionQ f (amtiQ f amti)) = x at *
  unfold l7 rate2628 amtBreak; cases f <;> simp <;> split <;> omega

/-- The worksheet's Note: at or above the zero point the exemption is zero (so skipping the worksheet is right). -/
theorem note_ok (f : Filing) (amti : Int) (h : amtZeroPoint f ≤ amti) : l5Q f (l4Q f amti) = 0 := by
  unfold l5Q l4Q amtZeroPoint amtThreshold amtExemption at *; cases f <;> simp at * <;> omega

end TaxCode.Forms.Form6251

#print axioms TaxCode.Forms.Form6251.l7_eq_statute
