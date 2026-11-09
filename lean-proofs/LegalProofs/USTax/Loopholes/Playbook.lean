import LegalProofs.USTax.Loopholes.Roth
import LegalProofs.USTax.Loopholes.StepUp
import LegalProofs.USTax.Loopholes.GRAT
import LegalProofs.USTax.Loopholes.QSBS

/-!
# Two ways to make a billion dollars

The same billion, earned twice. Once as pay: wages are taxed as they are earned, at ordinary rates, with payroll tax on
top. Once as the growth of founder's stock, handled with the structures in this folder: never sold (gain untaxed,
`borrow_plan_no_income_tax`), the part that is sold stacked under the §1202 caps (`stacking`), growth moved to the
heirs by zeroed-out GRATs (`zero_gift`), and at death stepped up (`step_up_erases`).
-/

namespace Legal.USTax.Loopholes.Playbook
open Legal.USTax Legal.USTax.Loopholes

/-- Federal tax on wages for a single employee: the rate schedule after the standard deduction, Social Security and
Medicare (`fica`), and the 0.9% additional Medicare tax above $200,000 (§3101(b)(2)). -/
def wageTax (w : Nat) : Nat :=
  scheduleTax .single (w - stdDeduction .single) + fica ⟨.single, 0, w, 0, 0⟩ + bp (w - 200000) 90

/-- **$393,460,310.** The federal tax on $1 billion of pay. -/
theorem salary_billion : wageTax 1000000000 = 393460310 := by decide

/-- The founder's billion of growth: $150 million sold through ten separate taxpayers, the rest never sold and
borrowed against, inherited at a stepped-up basis. -/
def founderIncomeTax : Nat :=
  QSBS.saleTax QSBS.stacked + (live (borrowYear 20000000 700 500) 30 founderStart).incomeTax +
    gainOnSale (inherit ⟨0, 850000000⟩) * ltcgRate / 10000

/-- **$0.** -/
theorem founder_billion : founderIncomeTax = 0 := by decide

end Legal.USTax.Loopholes.Playbook
