import PTTax.Art68

/-!
# CIRS art. 70: mínimo de existência (2025)

Art. 70 n.º 2 (Lei 24-D/2022, Lei 82/2023, Lei 34/2024): for a titular whose gross income is predominantly from
categoria A, the professional activities of categoria B (Portaria 1011/2001 table, except code 15) or pensions,
"é abatido um montante por mínimo de existência, por titular":
* a) RB ≤ VR: "a diferença positiva entre o valor de referência e a soma das deduções específicas com Limite
  despesas gerais/Taxa 1.º escalão";
* b) VR < RB ≤ L: "a diferença positiva entre o valor de referência - 2,60 x (rendimentos brutos - valor de
  referência) e a soma das deduções específicas com Limite despesas gerais/taxa 1.º escalão";
* c) RB > L: "a diferença positiva entre L – limite do 1.º escalão – 1,35 × (rendimentos brutos – L) e a soma das
  deduções específicas";
* d) "tem como valor mínimo zero e não pode ser superior à diferença entre os rendimentos brutos e as deduções
  específicas".
n.º 3: "L = valor de referência - (Limite despesas gerais/Taxa 1.º escalão x 3,60) + (Limite 1.º escalão/3,60)",
read (as the AT's simplified formulas and continuity require) as VR − G/3,60 + Lim1/3,60 with
G = Limite despesas gerais / Taxa 1.º escalão (a fraction whose denominator is "Taxa 1.º escalão x 3,60").
With 2025 values VR = 12 180 €, G = 250 / 12,5 % = 2 000 €, Lim1 = 8 059 €: L = 13 863,0555… €.

L is not a whole number of cents, so the model never rounds it: all comparisons are made on 36 × amounts.
The abatimento itself is rounded to the cent (half up) — the statute names no rounding.
-/

namespace PTTax
open TaxKernel

/-- 36 × L, in cents: 36·VR + 10·(Lim1 − G). -/
def meL36 : Int := 36 * meRef + 10 * (lim1 - meG)

theorem meL36_val : meL36 = 49907000 := by decide

/-- 10 × the segment-b amount: 36·VR − 26·RB − 10·DE − 10·G (before the positive part). -/
def meB10 (rb de : Int) : Int := 36 * meRef - 26 * rb - 10 * de - 10 * meG

/-- 3600 × the segment-c amount: 235·(36 L) − 3600·Lim1 − 4860·RB − 3600·DE. -/
def meC3600 (rb de : Int) : Int := 235 * meL36 - 3600 * lim1 - 4860 * rb - 3600 * de

/-- The abatimento of art. 70 n.º 2 for one titular with gross income `rb` and deduções específicas `de` (cents),
before the clamp d). -/
def meRaw (rb de : Int) : Int :=
  if rb ≤ meRef then pos (meRef - de - meG)
  else if 36 * rb ≤ meL36 then divR .halfUp (pos (meB10 rb de)) 10
  else divR .halfUp (pos (meC3600 rb de)) 3600

/-- Art. 70 n.º 2 d): between 0 and RB − DE. -/
def meAbate (rb de : Int) : Int := min (meRaw rb de) (pos (rb - de))

/-! ### What the construction does to the marginal rate (2025) -/

/-- Segment b: each extra 10 cents of gross income (deduções específicas fixed) adds 36 cents to the income left
after the abatimento — 3,6 € of rendimento coletável per euro earned (an effective 45 % at the 12,5 % rate,
56 % with the 11 % employee contribution). Stated for amounts that keep the abatimento positive. -/
theorem me_segment_b_step (rb de : Int) (h1 : meRef < rb) (h2 : 36 * (rb + 10) ≤ meL36)
    (hp : 0 ≤ meB10 (rb + 10) de) :
    meRaw (rb + 10) de = meRaw rb de - 26 := by
  have hp' : 0 ≤ meB10 rb de := by unfold meB10 at *; omega
  have e1 : meRaw (rb + 10) de = divR .halfUp (pos (meB10 (rb + 10) de)) 10 := by
    unfold meRaw; rw [if_neg (show ¬ (rb + 10 ≤ meRef) by omega), if_pos h2]
  have e2 : meRaw rb de = divR .halfUp (pos (meB10 rb de)) 10 := by
    unfold meRaw; rw [if_neg (show ¬ (rb ≤ meRef) by omega), if_pos (show 36 * rb ≤ meL36 by omega)]
  rw [e1, e2, pos_of_nonneg hp, pos_of_nonneg hp']
  simp only [divR, meB10] at *
  omega

/-- Segment c: each extra 200 cents of gross income removes 270 cents of abatimento (1,35 per euro): 2,35 € of
rendimento coletável per euro earned, an effective 37,6 % at the 16 % rate of the 2nd escalão (48,6 % with the
employee contribution). -/
theorem me_segment_c_step (rb de : Int) (h2 : meL36 < 36 * rb) (hp : 0 ≤ meC3600 (rb + 200) de) :
    meRaw (rb + 200) de = meRaw rb de - 270 := by
  have hp' : 0 ≤ meC3600 rb de := by unfold meC3600 at *; omega
  have hr : meRef < rb := by have := meL36_val; have := meRef_val; omega
  have e1 : meRaw (rb + 200) de = divR .halfUp (pos (meC3600 (rb + 200) de)) 3600 := by
    unfold meRaw
    rw [if_neg (show ¬ (rb + 200 ≤ meRef) by omega), if_neg (show ¬ (36 * (rb + 200) ≤ meL36) by omega)]
  have e2 : meRaw rb de = divR .halfUp (pos (meC3600 rb de)) 3600 := by
    unfold meRaw; rw [if_neg (show ¬ (rb ≤ meRef) by omega), if_neg (show ¬ (36 * rb ≤ meL36) by omega)]
  rw [e1, e2, pos_of_nonneg hp, pos_of_nonneg hp']
  simp only [divR, meC3600] at *
  omega

/-- Continuity at RB = VR: segment a and segment b agree. -/
theorem me_continuous_at_ref (de : Int) : meRaw meRef de = pos (meRef - de - meG) := by
  simp [meRaw]

end PTTax
