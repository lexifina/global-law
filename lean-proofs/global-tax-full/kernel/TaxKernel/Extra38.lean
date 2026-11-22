import TaxKernel.Theorems.Parts
import TaxKernel.Family
import TaxKernel.Table

/-!
# TaxKernel.Extra38 (1.2.1): the kernel gaps the 18 countries reported (INBOX 2026-11-19), added only

* **A taper whose withdrawal is rounded half-up (or up)** (SK ZDP § 47 rounds the NČZD withdrawal half-up; `Taper.WellFormed`
  asks for `.down`): `Taper.WellFormedM` allows any monotone mode, and `Taper.amount_antitoneM` proves that more income
  still never raises the allowance.
* **A spill capped at the receiving levy** (HU Tbj. § 34 (3): the contribution allowance is at most the TB due):
  `spillAllowanceCapped allowance income rate cap`.
* **An exempt amount valued on its own tariff** (BE CIR 92 art. 134: the tax-free sum is valued on the pre-2017 tariff,
  not on the current one): `lowBandReductionOn sExempt exempt`, `taxAfterLowBandOn s sExempt exempt income`.
* **Per-period rules whose parameters change mid-year** (BG maximum insurable income from April, HU per-child table
  July-December, RO pensions from August, SI parameters from March and July): `perPeriodIdx n f annual` gives `f` the
  period index (0 = first month) as well as the period's amount.
* **A contribution rate chosen by the size of the whole base** (AT AMPFG § 2a: unemployment-insurance rate 0/1/2/2.95 % by
  monthly pay): use a `Table` of rates and `rateOfBase t base` (= `Table.lookup t base 0 * base`, ticks); the
  jump at each row edge is the notch (`Table.valuesMono` decides whether the rates rise).
-/

namespace TaxKernel

namespace Taper
/-- Well formed with any monotone rounding of the withdrawal. -/
def WellFormedM (t : Taper) : Prop := 0 < t.den ∧ 0 ≤ t.num ∧ t.floor ≤ t.full ∧ t.round.isMonotoneMode

theorem reduction_monoM (t : Taper) (hw : t.WellFormedM) {x y : Int} (h : x ≤ y) :
    t.reduction x ≤ t.reduction y := by
  obtain ⟨hd, hn, _, hr⟩ := hw
  unfold reduction
  exact divR_mono t.round t.den hd hr (mul_le_mul_rate hn (pos_mono (by omega)))

/-- More income never raises a tapered allowance, whatever monotone rounding the statute uses. -/
theorem amount_antitoneM (t : Taper) (hw : t.WellFormedM) {x y : Int} (h : x ≤ y) : t.amount y ≤ t.amount x := by
  have := t.reduction_monoM hw h
  unfold amount; omega
end Taper

/-- `spillAllowance` with the spill limited to `cap` (the levy it is set against). -/
def spillAllowanceCapped (allowance income rate cap : Int) : Int × Int :=
  let s := spillAllowance allowance income rate
  (s.1, min (pos cap) s.2)

theorem spillAllowanceCapped_le (allowance income rate cap : Int) :
    (spillAllowanceCapped allowance income rate cap).2 ≤ pos cap := by
  unfold spillAllowanceCapped; simp only; omega

/-- The reduction for an exempt amount valued on its own tariff `sExempt` (ticks). -/
def lowBandReductionOn (sExempt : Schedule) (exempt : Int) : Int := sExempt.ticks (pos exempt)

/-- Tax (ticks) on `income` by `s`, less the exempt amount valued on `sExempt`, never below 0. -/
def taxAfterLowBandOn (s sExempt : Schedule) (exempt income : Int) : Int :=
  pos (s.ticks income - lowBandReductionOn sExempt exempt)

/-- With one tariff for both, it is `taxAfterLowBand`. -/
theorem taxAfterLowBandOn_same (s : Schedule) (exempt income : Int) :
    taxAfterLowBandOn s s exempt income = taxAfterLowBand s exempt income := rfl

/-- A per-period rule that also sees the period's index (parameters that change during the year). -/
def perPeriodIdx (n : Nat) (f : Nat → Int → Int) (annual : Int) : Int :=
  let q := annual / n
  let r := (annual % n).toNat
  (List.range n).foldl (fun acc i => acc + f i (q + if i < r then 1 else 0)) 0

/-- With a rule that ignores the index, it is `perPeriod`. -/
theorem perPeriodIdx_const (n : Nat) (g : Int → Int) (annual : Int) :
    perPeriodIdx n (fun _ x => g x) annual = perPeriod n g annual := rfl

/-- A rate (bp) looked up by the size of the whole base, charged on the whole base (ticks). -/
def rateOfBase (t : Table) (base : Int) : Int := Table.lookup t base 0 * base

end TaxKernel
