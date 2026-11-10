import LegalProofs.USTax.Trusts.Sale

/-!
# What the trust search found, re-checked

`Search.lean` classified 20,100 instruments of one or two powers under the two tests and scored every plan on each.
These are its results, re-checked by the kernel, beside the general theorems in `Sale.lean` that explain them.
-/

set_option maxRecDepth 100000

namespace Legal.USTax.Trusts.Found
open Legal.USTax.Trusts

/-- **The defective trust.** A power held by the grantor, outside any fiduciary capacity, to take back trust property
by substituting property of equal value makes the trust the grantor's for income tax (§675(4)(C)) and leaves it out of
the estate (Rev. Rul. 2008-22), with or without a standard. -/
theorem swap_power_defective (st : Bool) : status [⟨.substitute, .grantor, false, st⟩] = .defective := by
  cases st <;> decide

/-- So does a power in anyone not adverse to apply income to premiums on the grantor's life (§677(a)(3), §2042). -/
theorem premiums_defective (h : Holder) (hh : h ≠ .adverse) (f st : Bool) :
    status [⟨.premiums, h, f, st⟩] = .defective := by
  cases h <;> cases f <;> cases st <;> simp_all <;> decide

/-- **The trap.** A grantor who, as trustee, votes the shares of a company they control: §2036(b) brings the trust into
the estate whatever the capacity, but §675(4)(A) makes the grantor the income-tax owner only outside a fiduciary
capacity. -/
theorem voting_trustee_trap (st : Bool) : status [⟨.voteStock, .grantor, true, st⟩] = .trap := by
  cases st <;> decide

/-- Adding the nonfiduciary swap power to the trap instrument cures it: the trust becomes the grantor's for income
tax, but it stays in the estate. -/
theorem trap_plus_swap : status [⟨.voteStock, .grantor, true, false⟩, ⟨.substitute, .grantor, false, false⟩] = .incomplete := by
  decide

/-! ## The scenario: $50 million, basis $5 million, 8% growth, 3% yield, 20 years -/

def R : Rates := ⟨460, 2380, 4080, 2380, 0⟩
def path : List (Int × Int) := List.replicate 20 (800, 300)
def s0 : St := ⟨50000000, 10000000, 0, 0, 0⟩
def basis : Int := 5000000

/-- Keeping the asset: the heirs receive $177,212,259 after $118,141,505 of estate tax. -/
theorem keep : (outcome R ⟨false, false⟩ false false basis path s0).heirs = 177212259 ∧
    (outcome R ⟨false, false⟩ false false basis path s0).estateTax = 118141505 := by decide

/-- **The search's best plan: $259,488,570.** Sell to a trust with the swap power, swap the asset back just before
death. $82.3 million more for the heirs than keeping it. -/
theorem best : (outcome R ⟨true, true⟩ false true basis path s0).heirs = 259488570 := by decide

/-- Without the swap the heirs keep $205,213,184: the carried-over basis costs them $54.3 million of capital-gains
tax (`no_swap_cost`). -/
theorem without_swap : (outcome R ⟨true, true⟩ false false basis path s0).heirs = 205213184 := by decide

/-- A sale to a trust that is the grantor's for neither tax: $191,701,578, after paying the gain up front. -/
theorem complete_sale : (outcome R ⟨true, false⟩ false false basis path s0).heirs = 191701578 := by decide

/-- **The trap: $159,525,459**, $17.7 million less than doing nothing (`trap_never_better`). -/
theorem trap_sale : (outcome R ⟨true, false⟩ true false basis path s0).heirs = 159525459 := by decide

end Legal.USTax.Trusts.Found
