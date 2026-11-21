import PTTax.Params

/-!
# CIRS art. 68 n.º 2 and art. 69: the statute's own construction of the tax

Art. 68 n.º 2 (Lei 45-A/2024): "O quantitativo do rendimento coletável, quando superior a 8059 €, é dividido em
duas partes ...: uma, igual ao limite do maior dos escalões que nele couber, à qual se aplica a taxa da coluna B
correspondente a esse escalão; outra, igual ao excedente, a que se aplica a taxa da coluna A respeitante ao escalão
imediatamente superior."

Art. 69 n.º 1 and 3 (quociente conjugal, joint taxation only): "as taxas aplicáveis são as correspondentes ao
rendimento coletável dividido por dois", "multiplicando-se por dois o resultado obtido".

`art68Scaled n x` is n × (tax on x / n) computed exactly, in cents × 10⁻⁵ (cents × pcm): for the divisor `n`
(1 = separate/single, 2 = joint) every limit is multiplied by `n` instead of dividing `x`, so nothing is rounded
before the end. Column B is the statute's rounded average rate (three decimals of a percent), so the result is
NOT the exact sum over the bands (`art68Bands`); the difference is a constant inside each escalão (theorem
`art68_minus_bands`), and the statutory tax jumps by a few cents, up or down, at each limit.
-/

namespace PTTax
open TaxKernel

/-- Art. 68 n.º 2 with divisor `n` (art. 69), on rendimento coletável `x` in cents; result in cents × pcm. -/
def art68Scaled (n x : Int) : Int :=
  art68Rows.foldl
    (fun acc (r : Int × Int × Int) =>
      let lim := n * eur r.1
      if lim ≤ x then lim * r.2.2 + (x - lim) * r.2.1 else acc)
    (x * art68FirstRate)

/-- The coleta of art. 68/69 in cents, rounded to the cent (half up; the statute names no rule, the euro
conversion rule of DL 136/2002 art. 5 is to the nearest cent). -/
def art68Coleta (n x : Int) : Int := divR .halfUp (art68Scaled n (pos x)) 100000

/-- The exact band sum, in the same unit (cents × pcm): 10 × kernel ticks (cents × bp). -/
def bandsScaled (n x : Int) : Int := n * 10 * art68Bands.ticks (x / n)

/-! ### The kernel's generic theorems for the band sum -/

theorem art68Bands_progressive : art68Bands.progressive = true := by decide

theorem art68Bands_mono : Monotone' art68Bands.ticks :=
  Schedule.ticks_mono_of_progressive art68Bands art68Bands_progressive

theorem art68Bands_convex : Convex art68Bands.ticks :=
  Schedule.ticks_convex art68Bands art68Bands_progressive

/-- The band sum version of the quociente conjugal never costs more than two separate assessments (kernel
`splitting_le_separate`). The statute's own formula is not convex (see `art68_jump_*`), so this generic theorem
does not carry over to it exactly. -/
theorem quociente_bands_le_separate (a b : Int) :
    splitting art68Bands.ticks a b ≤ separate art68Bands.ticks a b :=
  splitting_le_separate _ art68Bands_convex art68Bands_mono a b

/-! ### Statute vs band sum: a constant per escalão -/

/-- Inside every escalão, the statutory formula equals the exact band sum plus the escalão's constant
(`lim × B − exact tax at lim`, cents × pcm). Proved for every rendimento coletável `x ≥ 0` (single divisor). -/
def art68Err (x : Int) : Int :=
  if x < 1216000 then 0 else if x < 1723300 then -470000 else if x < 2230600 then -519400
  else if x < 2840000 then 628200 else if x < 4162900 then -620000 else if x < 4498700 then 833300
  else if x < 8369600 then -859100 else 1848400

theorem art68_minus_bands (x : Int) (hx : 0 ≤ x) :
    art68Scaled 1 x = 10 * art68Bands.ticks x + art68Err x := by
  simp only [art68Scaled, art68Rows, art68FirstRate, eur, List.foldl, art68Err, art68Bands, Schedule.ticks,
    Schedule.ofList, List.map, bandsTicks, pos]
  repeat' split
  all_goals omega

/-- The statutory tax is never more than 18,484 cents above, nor 8,591 cents below, the exact band sum. -/
theorem art68_close (x : Int) (hx : 0 ≤ x) :
    -859100 ≤ art68Scaled 1 x - 10 * art68Bands.ticks x ∧ art68Scaled 1 x - 10 * art68Bands.ticks x ≤ 1848400 := by
  rw [art68_minus_bands x hx]; unfold art68Err
  repeat' split
  all_goals omega

/-! ### The tax falls when the income rises by one cent (column B rounded down) -/

/-- At 28 400,00 € the coleta is 12 cents LOWER than at 28 399,99 €: one more cent of income, 12 cents less tax. -/
theorem art68_jump_28400 : art68Coleta 1 2840000 + 12 = art68Coleta 1 2839999 := by decide

/-- Same at 44 987,00 €: 17 cents less tax for one more cent. -/
theorem art68_jump_44987 : art68Coleta 1 4498700 + 17 = art68Coleta 1 4498699 := by decide

/-- And at 12 160,00 €: 4 cents less. -/
theorem art68_jump_12160 : art68Coleta 1 1216000 + 4 = art68Coleta 1 1215999 := by decide

/-- Joint taxation doubles the effect: at 56 800,00 € of joint rendimento coletável the coleta falls by 25 cents. -/
theorem art68_jump_joint_56800 : art68Coleta 2 5680000 + 25 = art68Coleta 2 5679999 := by decide

/-- Hence the statutory tax is not monotone (a kernel `Schedule` always is): a finding (FINDINGS F3). -/
theorem art68_not_monotone : ¬ (∀ x y : Int, x ≤ y → art68Coleta 1 x ≤ art68Coleta 1 y) := by
  intro h
  have := h 2839999 2840000 (by decide)
  have h2 := art68_jump_28400
  omega

/-! ### Art. 68-A taxa adicional de solidariedade (n.º 3: joint = twice the amount on half) -/

def solidarityCents (n x : Int) : Int := divR .halfUp (n * solidarity.ticks (pos x / n)) 10000

theorem solidarity_progressive : solidarity.progressive = true := by decide

end PTTax

namespace PTTax
open TaxKernel

/-- The OECD's convention (and the "parcela a abater" form of the AT's withholding tables): the exact band sum,
n × T(x / n) computed by scaling the thresholds, in cents × pcm. Used only with `--bandsum`. -/
def bandsScaledN (n x : Int) : Int := 10 * (art68Bands.mapLo (n * ·)).ticks (pos x)

/-- The art. 68/69 tax in cents × pcm, by the statute (`bands = false`) or by the exact band sum. -/
def art68ScaledBy (bands : Bool) (n x : Int) : Int := if bands then bandsScaledN n x else art68Scaled n (pos x)

end PTTax

namespace PTTax

/-- The statute's quociente conjugal (art. 69) can cost more than two separate assessments (same rendimento
coletável, no other differences): spouses with 83 695,91 € and 83 696,64 € pay 28 cents more jointly, because
column B jumps at 83 696 €. The kernel's `splitting_le_separate` holds for the band sum
(`quociente_bands_le_separate`), not for the statutory formula. -/
theorem quociente_can_cost_more :
    art68Coleta 2 (8369591 + 8369664) = art68Coleta 1 8369591 + art68Coleta 1 8369664 + 28 := by decide

end PTTax
