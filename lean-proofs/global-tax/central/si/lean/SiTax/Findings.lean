import SiTax.Basic

/-!
# Slovenia 2025: the findings, proved on named households (cents; closed by `decide`)
-/

namespace SiTax
open TaxKernel

/-- A wage earner aged 40 (wages in cents). -/
def worker (w : Int) : Person := { wages := w }

/-- Net income (cents) of a single parent earning `w` with children aged `kids` (oldest first), as `compute`. -/
def singleNet (w : Int) (kids : List Nat) : Int :=
  let p := worker w
  let d := childTotal kids.length
  let fam := w - employeeSocial p - personTax p d
  fam + 12 * cbMonthlyOf fam (1 + kids.length) kids true

/-- Net income of a one-earner married couple (the spouse has no income), all child allowances with the earner. -/
def coupleNet1 (w : Int) (kids : List Nat) : Int :=
  let p := worker w
  let q : Person := {}
  let d := otherDependant + childTotal kids.length
  let fam := w - employeeSocial p - personTax p d - employeeSocial q
  fam + 12 * cbMonthlyOf fam (2 + kids.length) kids false

/-- A single parent who claims only `childTotal − f` of the child allowances (forgoes `f` cents). -/
def singleNetF (w : Int) (kids : List Nat) (f : Int) : Int :=
  let p := worker w
  let d := pos (childTotal kids.length - f)
  let fam := w - employeeSocial p - personTax p d
  fam + 12 * cbMonthlyOf fam (1 + kids.length) kids true

/-- A married couple, two children: the first a full-time s.p. on flat-rate expenses with revenue `r` and no real
expenses, the spouse without income. Family income for the child-benefit test (Pravilnik PRAV12104 čl. 10(2):
profit less the tax) and the family's actual cash after taxes and contributions. -/
def normPerson (r : Int) : Person := { normRev := r }
def normFamTest (r : Int) : Int := normProfit (normPerson r) - normTax (normPerson r) - 2 * ozpYear
def normFamCash (r : Int) : Int := r - normTax (normPerson r) - employeeSocial (normPerson r) - ozpYear

/-- Net income (cents) of a single person on wages `w`, no children. -/
def singleNet0 (w : Int) : Int := w - employeeSocial (worker w) - personTax (worker w) 0

/-! ## The theorems (households named in FINDINGS.md) -/

/-- **F7** Child benefit notch: a single parent of two (11, 6) earning 19.519 € gross nets 941,71 € more than at
19.520 € (class 2 → 3, ZUPJS čl. 22 + ZSDP-1 čl. 72). -/
theorem F7_single_notch : singleNet 1951900 [11, 6] - singleNet 1952000 [11, 6] = 94171 := by decide
/-- **F7** The same in a one-earner married couple with two children at 26.734 €: 724,27 €. -/
theorem F7_couple_notch : coupleNet1 2673400 [11, 6] - coupleNet1 2673500 [11, 6] = 72427 := by decide
/-- **F8** The cliff above class 8: a single parent of two at 77.807 € vs 77.808 € loses 929,60 €. -/
theorem F8_cliff : singleNet 7780700 [11, 6] - singleNet 7780800 [11, 6] = 92960 := by decide
/-- **F9** Dependent spouse (čl. 114(1) 3., 115(1)): a spouse with no income is a dependant, one with any wage is
not; for an earner at the average wage (30.135 €) the first euro the spouse earns costs 737,96 € of tax. -/
theorem F9_spouse_notch :
    personTax (worker 3013500) 0 - personTax (worker 3013500) otherDependant = 73796
      ∧ isDependentSpouse {} = true ∧ isDependentSpouse (worker 100) = false := by decide
/-- **F10** Forgoing 400 € of the child allowance: a single parent of two at 19.600 € pays 64 € more tax but keeps
class 2 of the child benefit: 878,36 € a year better off. -/
theorem F10_forgo : singleNetF 1960000 [11, 6] 40000 - singleNetF 1960000 [11, 6] 0 = 87836 := by decide
/-- **F11** A full-time s.p. on flat-rate expenses with 60.000 € revenue and no real expenses: the child-benefit
test sees 8.716,60 € a year for a family of four (class 1, the maximum: 301,99 € a month for two children) while
the family keeps 49.957,19 € after tax and contributions. -/
theorem F11_norm_child_benefit :
    normFamTest 6000000 = 871660 ∧ normFamCash 6000000 = 4995719
      ∧ classTable.lookup (normFamTest 6000000 / 12 / 4) 0 = 1
      ∧ cbMonthlyOf (normFamTest 6000000) 4 [11, 6] false = 30199 := by decide
/-- **F12** The taper band of the additional general allowance (čl. 111(3)): 100 € more gross wages at 15.000 €
leave 46,26 € (METR 53,7 %); at 19.000 € they leave 65,02 € (35,0 %); at 11.000 € 77,40 € (22,6 %). -/
theorem F12_taper_band :
    singleNet0 1510000 - singleNet0 1500000 = 4626 ∧ singleNet0 1910000 - singleNet0 1900000 = 6502
      ∧ singleNet0 1110000 - singleNet0 1100000 = 7740 := by decide

/-- **F13** Who claims the children (čl. 114(10)-(11)): a married couple earning 116.000 € and 29.000 € with two
children pays 1.421,72 € more if the lower earner claims the 5.923,82 € of child allowances, and 710,86 € more if
they do not agree and each gets half. -/
theorem F13_claimant :
    (personTax (worker 2900000) (childTotal 2) + personTax (worker 11600000) 0)
      - (personTax (worker 11600000) (childTotal 2) + personTax (worker 2900000) 0) = 142172
    ∧ (personTax (worker 2900000) (childTotal 2 / 2) + personTax (worker 11600000) (childTotal 2 / 2))
      - (personTax (worker 11600000) (childTotal 2) + personTax (worker 2900000) 0) = 71086 := by decide

end SiTax
