import PTTax.Household

/-!
# Withholding on wages, mainland 2025 (CIRS art. 99-F; Despachos 236-A/2025 and 8464-A/2025)

The tables (Tabela I: "Não casado sem dependentes ou casado 2 titulares") give, for the monthly pay R,
"(Remuneração mensal x Taxa) - Parcela a abater - (Parcela adicional a abater x nº dependentes)", where in the two
lowest taxed lines the parcela is itself a formula "taxa x 2,60 x (K - R)" / "taxa x 1,35 x (K - R)" (a monthly
copy of the art. 70 mínimo de existência).
Sources (AT): Circular 2/2025 (tables of Despacho 236-A/2025, paid 1 January - 31 July 2025); Circular 4/2025
(Despacho 8464-A/2025 as published 22 July 2025: tables I-A... for 1 August - 30 September, tables I... from
1 October); Circular 7/2025 (the same after Declaração de Retificação n.º 815/2025/2, DR 2.ª série n.º 166,
29 August 2025). Text in `law/Circular_*_2025.txt`, parsed into `refs/withholding_2025.json`.

Money in cents; rates in bp (two decimals of a percent); multipliers ×100 (2,60 → 260).
-/

namespace PTTax
open TaxKernel

/-- The parcela a abater of one line: a value (cents) or `rate × mult/100 × (k − R)`. -/
inductive Parcela where
  | value (p : Int)
  | formula (rate mult k : Int)

/-- One line of a table: pay up to `upTo` (cents; `none` = "Superior a"), marginal rate (bp), parcela, and the
parcela adicional per dependant (cents). -/
structure WLine where
  upTo : Option Int
  rate : Int
  parcela : Parcela
  perDep : Int

def WLine.covers (l : WLine) (r : Int) : Bool :=
  match l.upTo with
  | none => true
  | some u => decide (r ≤ u)

/-- Withholding (cents × 10⁶, exact) on monthly pay `r` (cents) with `n` dependants. -/
def whScaled (t : List WLine) (r n : Int) : Int :=
  match t.find? (fun l => l.covers r) with
  | none => 0
  | some l =>
    let p := match l.parcela with
      | .value p => p * 1000000
      | .formula rate mult k => rate * mult * (k - r)
    pos (r * l.rate * 100 - p - l.perDep * n * 1000000)

/-- Withholding in cents, half up. -/
def wh (t : List WLine) (r n : Int) : Int := divR .halfUp (whScaled t r n) 1000000

/-- Tabela I, Despacho 236-A/2025 (Circular 2/2025), paid 1 Jan - 31 Jul 2025. -/
def tabIJan : List WLine :=
  [⟨some 87000, 0, .value 0, 0⟩, ⟨some 99200, 1300, .formula 1300 260 120832, 2143⟩,
   ⟨some 107000, 1650, .formula 1650 135 147767, 2143⟩, ⟨some 113600, 1650, .value 9081, 2143⟩,
   ⟨some 118700, 2200, .value 15329, 2143⟩, ⟨some 178700, 2500, .value 18890, 2143⟩,
   ⟨some 207800, 3200, .value 31399, 2143⟩, ⟨some 243200, 3550, .value 38672, 2143⟩,
   ⟨some 323300, 3872, .value 46503, 2143⟩, ⟨some 554700, 4005, .value 50803, 2143⟩,
   ⟨some 2022100, 4495, .value 77983, 2143⟩, ⟨none, 4717, .value 122874, 2143⟩]

/-- Tabela I, Despacho 8464-A/2025 as rectified (Circular 7/2025), paid from 1 Oct 2025. -/
def tabIOct : List WLine :=
  [⟨some 87000, 0, .value 0, 0⟩, ⟨some 99200, 1250, .formula 1250 260 120871, 2143⟩,
   ⟨some 107000, 1600, .formula 1600 135 147691, 2143⟩, ⟨some 113600, 1600, .value 8790, 2143⟩,
   ⟨some 118700, 2150, .value 15038, 2143⟩, ⟨some 178700, 2440, .value 18481, 2143⟩,
   ⟨some 207800, 3140, .value 30990, 2143⟩, ⟨some 243200, 3490, .value 38263, 2143⟩,
   ⟨some 323300, 3836, .value 46678, 2143⟩, ⟨some 554700, 3969, .value 50978, 2143⟩,
   ⟨some 2022100, 4495, .value 80156, 2143⟩, ⟨none, 4717, .value 125047, 2143⟩]

/-- The same table as first published on 22 July 2025 (Circular 4/2025): K = 1 205,71 in the second line. -/
def tabIOctOrig : List WLine :=
  match tabIOct with
  | a :: _ :: rest => a :: ⟨some 99200, 1250, .formula 1250 260 120571, 2143⟩ :: rest
  | l => l

/-- Tabela I-A, paid 1 Aug - 30 Sep 2025 (the "compensation" tables, Circular 7/2025). -/
def tabIAug : List WLine :=
  [⟨some 87000, 0, .value 0, 0⟩, ⟨some 99200, 0, .value 0, 2143⟩, ⟨some 107000, 0, .value 0, 2143⟩,
   ⟨some 113600, 0, .value 0, 2143⟩, ⟨some 118700, 108, .value 1227, 2143⟩,
   ⟨some 178700, 244, .value 2842, 2143⟩, ⟨some 207800, 314, .value 4093, 2143⟩,
   ⟨some 243200, 524, .value 8457, 2143⟩, ⟨some 323300, 767, .value 14367, 2143⟩,
   ⟨some 554700, 1389, .value 34477, 2143⟩, ⟨some 2022100, 4495, .value 206767, 2143⟩,
   ⟨none, 4717, .value 251658, 2143⟩]

/-- Spot value printed in the October table's last column ("Taxa efetiva mensal de retenção no limite do
escalão"): 992 € → 5,4 % (53,57 €). -/
theorem tabIOct_992 : wh tabIOct 99200 0 = 5357 := by decide

/-- One cent more pay above 992 € raises the October withholding by 41 cents (rectified table) ... -/
theorem tabIOct_jump_992 : wh tabIOct 99201 0 = wh tabIOct 99200 0 + 41 := by decide
/-- ... and, as first published, lowered it by 56 cents: the rectification moved the jump, it did not remove it.
Continuity at 992 € needs K = 1 207,45 (neither 1 205,71 nor 1 208,71). -/
theorem tabIOctOrig_jump_992 : wh tabIOctOrig 99201 0 + 56 = wh tabIOctOrig 99200 0 := by decide
/-- The January table falls by 34 cents at the same point. -/
theorem tabIJan_jump_992 : wh tabIJan 99201 0 + 34 = wh tabIJan 99200 0 := by decide

/-- Withholding in 2025 for constant monthly pay `r` paid 14 times (CIRS art. 99-C n.º 5: the subsídios "são
sempre objeto de retenção autónoma"): 8 payments on the January table (Jan-Jul and the subsídio de férias),
2 on the August table, 4 on the October table (Oct-Dec and the subsídio de Natal). -/
def withheld2025 (r : Int) : Int := 8 * wh tabIJan r 0 + 2 * wh tabIAug r 0 + 4 * wh tabIOct r 0

/-- The August-September cut is a multiple of what January-July over-withheld (relative to the October table):
at 2 000 €/month, Jan-Jul (8 payments) over-withheld 8 × 7,91 = 63,28 €, and August-September withheld
2 × 296,23 = 592,46 € less than the October table: 9,4 times as much. -/
theorem compensation_2000 :
    8 * (wh tabIJan 200000 0 - wh tabIOct 200000 0) = 6328 ∧
    2 * (wh tabIOct 200000 0 - wh tabIAug 200000 0) = 59246 := by decide

/-- The 2025 total at 2 000 €/month: 3 924,22 € withheld (the statute's IRS for this single employee with the
art. 78-B maximum is 4 128,91 €: `results/withholding_2025.json`). -/
theorem withheld2025_2000 : withheld2025 200000 = 392422 := by decide

end PTTax
