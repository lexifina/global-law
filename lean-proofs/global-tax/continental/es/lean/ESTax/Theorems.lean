import ESTax.Withholding

/-!
# Theorems about the Spanish model (no `sorry`)

Kernel instances (TaxKernel §5) for the four scales, Spain-specific properties of the statute, and the concrete
households behind FINDINGS (checked by the kernel by evaluation: `decide`).
-/

namespace ESTax
open TaxKernel

/-! ## 1. The scales are progressive; kernel theorems instantiate -/

theorem estatal_progressive : (toSched escalaEstatal).progressive = true := by decide
theorem madrid_progressive : (toSched escalaMadrid).progressive = true := by decide
theorem ahorro_progressive : (toSched escalaAhorroEstatal).progressive = true := by decide
theorem retencion_progressive : (toSched escalaRetencion).progressive = true := by decide

theorem estatal_mono : Monotone' (toSched escalaEstatal).ticks :=
  Schedule.ticks_mono_of_progressive _ estatal_progressive
theorem madrid_mono : Monotone' (toSched escalaMadrid).ticks :=
  Schedule.ticks_mono_of_progressive _ madrid_progressive
theorem estatal_convex : Convex (toSched escalaEstatal).ticks :=
  Schedule.ticks_convex _ estatal_progressive
theorem madrid_convex : Convex (toSched escalaMadrid).ticks :=
  Schedule.ticks_convex _ madrid_progressive
theorem estatal_marginal (x : Int) : (toSched escalaEstatal).ticks (x + 1) - (toSched escalaEstatal).ticks x =
    (toSched escalaEstatal).rate x := Schedule.ticks_succ _ x

/-- The printed "Cuota íntegra" column of each table equals the band sum at the row's start, rounded to the cent:
state, ahorro and withholding tables exactly; Madrid's within rounding (its cuotas are rounded cumulative sums). -/
theorem estatal_cuotas : cuotasConsistent escalaEstatal = true := by decide
theorem madrid_cuotas : cuotasConsistent escalaMadrid = true := by decide
theorem ahorro_cuotas : cuotasConsistent escalaAhorroEstatal = true := by decide
theorem retencion_cuotas : cuotasConsistent escalaRetencion = true := by decide

/-- The withholding scale is the state scale doubled in its first five bands (RIRPF art. 85 vs LIRPF art. 63: the
payer withholds as if the region's scale were the state's) but not in the top band: 47 % = 24,5 % + 22,5 %, not
2 × 24,5 % = 49 %. -/
theorem retencion_doble : (escalaRetencion.take 5).map (fun r => (r.lo, r.cuota, r.rate)) =
    (escalaEstatal.take 5).map (fun r => (r.lo, 2 * r.cuota, 2 * r.rate)) := by decide
theorem retencion_top : (escalaRetencion.getLast!).rate = (escalaEstatal.getLast!).rate + 2250 ∧
    (escalaRetencion.getLast!).rate < 2 * (escalaEstatal.getLast!).rate := by decide

/-! ## 2. The mínimo personal y familiar is a credit at the bottom rate, not a deduction at the top -/

/-- Superadditivity of a progressive schedule with non-negative starts: `s(n) ≤ s(a + n) − s(a)`. -/
theorem superadd (s : Schedule) (hp : s.progressive = true) (hl : s.LosNonneg) (a : Int) (ha : 0 ≤ a) :
    ∀ n : Nat, s.ticks n ≤ s.ticks (a + n) - s.ticks a := by
  intro n
  induction n with
  | zero =>
    have h0 := s.ticks_zero hl
    have e : a + ((0 : Nat) : Int) = a := by omega
    rw [e]
    simp only [Int.ofNat_zero]
    omega
  | succ k ih =>
    have h1 := Schedule.ticks_succ s (k : Int)
    have h2 := Schedule.ticks_succ s (a + k)
    have hk : (0 : Int) ≤ k := Int.natCast_nonneg k
    have h3 : s.rate k ≤ s.rate (a + k) := Schedule.rate_mono s hp (by omega)
    have e2 : a + ((k : Int) + 1) = a + k + 1 := by omega
    show s.ticks ((k : Int) + 1) ≤ s.ticks (a + ((k : Int) + 1)) - s.ticks a
    rw [e2]
    omega

/-- The mínimo is taxed at the bottom of the scale (art. 63.1 2.º): for a mínimo inside the first band its value is
9,5 % of it, whatever the base. -/
theorem minimo_bottom (m : Int) (h1 : m < 1245000) : tableTicks escalaEstatal m = 950 * m := by
  simp [tableTicks, escalaEstatal, h1, BP]

/-- A deduction of the same amount from the base would never be worth less (and is worth more above the first band):
`s(m) ≤ s(b) − s(b − m)` for the state scale. So the Spanish mínimo is a tax credit of `s(m)`, as the OECD books it
(BTC), not an allowance at the marginal rate. -/
theorem minimo_credit_le_deduction (b m : Int) (hm : 0 ≤ m) (hb : m ≤ b) :
    (toSched escalaEstatal).ticks m ≤ (toSched escalaEstatal).ticks b - (toSched escalaEstatal).ticks (b - m) := by
  have hl : (toSched escalaEstatal).LosNonneg := by
    unfold Schedule.LosNonneg; decide
  have h := superadd (toSched escalaEstatal) estatal_progressive hl (b - m) (by omega) m.toNat
  have e : ((m.toNat : Nat) : Int) = m := Int.toNat_of_nonneg hm
  rw [e] at h
  have e2 : b - m + m = b := by omega
  rw [e2] at h
  exact h

/-! ## 3. Art. 20 and DA 61.ª: continuity of the statutory formulas (exact, hundredths of a cent) -/

/-- b) and c) meet exactly at 17.673,52 €: 7.302 − 1,75 × 2.821,52 = 2.364,34. -/
theorem red20_cont_T2 : 100 * r20Max - (r20T2 - r20T1) * r20K1 = 100 * r20Mid := by decide
/-- c) does not reach 0 at 19.747,5 €: 2.364,34 − 1,14 × 2.073,98 = 0,0028 € (0,28 cent). The formula reaches 0 at
19.747,5025 €; the statute's end point is rounded. Harmless after rounding to the cent (1 cent at 19.747,49 €). -/
theorem red20_residual_at_end : 100 * r20Mid - (r20Limite - r20T2) * r20K2 = 28 := by decide
theorem red20_last_cent : red20 (r20Limite - 1) 0 = 1 ∧ red20 r20Limite 0 = 0 := by decide
/-- In band b) one more euro of rendimiento neto removes 1,75 € of reducción (exactly, in hundredths of a cent). -/
theorem red20_slope_b (x : Int) (h1 : r20T1 < x) (h2 : x + 100 ≤ r20T2) :
    red20Exact x 0 - red20Exact (x + 100) 0 = 17500 := by
  unfold red20Exact
  have a : ¬ (r20Limite ≤ x) := by unfold r20Limite r20T2 at *; omega
  have b : ¬ (r20Limite ≤ x + 100) := by unfold r20Limite r20T2 at *; omega
  have c : ¬ (r20Otras < (0 : Int)) := by unfold r20Otras eur; omega
  have d : ¬ (x ≤ r20T1) := by omega
  have e : ¬ (x + 100 ≤ r20T1) := by omega
  have f : x ≤ r20T2 := by omega
  simp only [a, b, c, d, e, f, h2, ite_false, ite_true]
  unfold r20K1; omega
/-- DA 61.ª: the taper ends exactly at 18.276 €: 340 − 0,2 × 1.700 = 0. -/
theorem smi_cont : smiMax - (smiLimite - smiT1) * 2 / 10 = 0 := by decide

/-! ## 4. Concrete households (FINDINGS), evaluated by the kernel -/

def single (w : Int) (sav : Int := 0) : HH :=
  { ages := [40], wages := [w], pensions := [0], selfEmp := [0], savings := sav, rental := 0, pensionContrib := 0,
    charitable := 0, married := false, kids := [], mother := 0 }

def hhTotal (h : HH) : Int := totalOf (assess h).liqs

/-- F7: a worker on the 2025 SMI-level wage (16.576 €) owes no IRPF (DA 61.ª absorbs the 287,12 € of cuota) but the
RIRPF withholding procedure (art. 81 limit 15.876 €, unchanged since RD 142/2024) withholds 300,03 €. -/
theorem smi_owes_nothing : hhTotal (single 1657600) = 0 := by decide
theorem smi_withheld : (withholding (single 1657600).whIn0).importe = 30003 := by decide

/-- F5: the art. 20 and DA 61.ª condition "rentas ... distintas de las del trabajo superiores a 6.500 euros": one
more cent of interest for a 14.000 € worker raises the tax by more than 1.650 €. -/
theorem cliff_6500 : hhTotal (single 1400000 650001) - hhTotal (single 1400000 650000) > 165000 := by decide

def parent (w : Int) (kids : List Nat) : HH :=
  { single w with kids := kids }

def couple (w1 w2 : Int) (kids : List Nat) (married : Bool := true) : HH :=
  { ages := [40, 40], wages := [w1, w2], pensions := [0, 0], selfEmp := [0, 0], savings := 0, rental := 0,
    pensionContrib := 0, charitable := 0, married, kids, mother := 1 }

/-- F3 (Madrid art. 14 notch): a single parent of two (aged 11 and 6) earning 28.600 € instead of 28.590 € pays more
than 120 € more: the family's base imponible passes 24.744 € and the 10 % deduction on the cuota autonómica goes. -/
theorem cliff_madrid_art14 : hhTotal (parent 2860000 [11, 6]) - hhTotal (parent 2859000 [11, 6]) > 12000 := by decide

/-- F4 (Madrid art. 4 + art. 18.1 notch): a single parent of a one-year-old earning 42.050 € instead of 42.040 € pays
more than 700 € more: the base imponible passes 37.322,20 € (joint return) and the 721,70 € birth deduction goes. -/
theorem cliff_madrid_art4 : hhTotal (parent 4205000 [1]) - hhTotal (parent 4204000 [1]) > 70000 := by decide

/-- F4b: in a married couple filing separately, the second earner's own base passing 30.930 € removes their half
(360,85 €) of the birth deduction: 10 € more wages, more than 350 € more tax. -/
theorem cliff_madrid_art4_couple :
    hhTotal (couple 2000000 3522000 [1]) - hhTotal (couple 2000000 3521000 [1]) > 35000 := by decide

/-- F8 (joint filing): for the OECD one-earner couple with two children (average wage), the joint return is cheaper
than two individual returns; married partners can choose it, unmarried partners cannot (art. 82). -/
theorem joint_beats_separate_one_earner :
    (liquidate (couple 3267800 0 [11, 6]).jointBase |>.total) <
      totalOf ((couple 3267800 0 [11, 6]).separateRets.map liquidate) := by decide
theorem married_vs_unmarried_one_earner :
    hhTotal (couple 3267800 0 [11, 6]) < hhTotal (couple 3267800 0 [11, 6] (married := false)) := by decide

end ESTax
