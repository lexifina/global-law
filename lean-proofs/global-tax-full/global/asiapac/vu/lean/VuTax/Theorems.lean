import VuTax.Basic

/-! # Vanuatu: statements about the model (no `sorry`) -/

namespace VuTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

/-- s. 25(2) is an all-or-nothing floor: reaching VT 3,000 a month costs 6 % of the whole floor at once
(kernel `Contribution.floor_notch`). -/
theorem vnpf_notch : vnpf.ticks vnpf.floor - vnpf.ticks (vnpf.floor - 1) = vnpf.sched.ticks (vnpf.base vnpf.floor) :=
  Contribution.floor_notch vnpf

theorem vnpf_notch_value : vnpf.amount 36000 - vnpf.amount 35999 = 2160 := by decide

#guard vnpf.amount 1200000 = 72000

end VuTax
