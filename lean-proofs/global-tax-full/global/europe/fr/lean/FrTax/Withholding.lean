import FrTax.Liquidation

/-!
# Withholding tax rates (prélèvement à la source, CGI art. 204 A to 204 N)

The rate computed on the income of year N applies from September N+1 to August N+2 (art. 204 H, I, 2). Here
`d.year` is the income year N; every rate is in tenths of a per cent (`54` is 5.4 %).

* **Household rate** (art. 204 H, I, 1): the income tax "résultant de l'application des règles prévues aux 1 à 4
  du I de l'article 197" (scale, cap on the quotient familial, décote), times "le rapport entre les montants nets
  imposables des revenus mentionnés au 1 de l'article 204 A, les déficits étant retenus pour une valeur nulle, et
  le revenu net imposable au barème ..., hors déficits, charges et abattements", divided by those same income
  "pour leurs montants déterminés dans les conditions mentionnées à l'article 204 F et à l'article 204 G":
  salaries and pensions before the 10 % allowances (204 F), the other income at its net taxable amount (204 G).
  Rounded "à la décimale la plus proche. La fraction de décimale égale à 0,50 est comptée pour un" (I, 3).
* **Zero rate** (II): nil when the income tax "mis en recouvrement" for the last two years is nil and the RFR
  is under a per-part threshold, "indexé chaque année" (II, last paragraph): 25 705 € for the rates from
  1 September 2021, ... 29 574 € for those from 1 September 2026 (the indexed figures, not the lagging printed ones).
* **Individualised rates** for a couple (art. 204 M): the partner with the lower income gets the rate of I
  computed on their own income plus half the common income, with half the parts and half the deductions; the
  other partner gets what remains of the household numerator, over their own income alone.
* **Default grids** (III, 1, a to c): monthly base -> rate, for mainland France, for Guadeloupe, Martinique and
  La Réunion, and for Guyane and Mayotte, for each rate year 2021 to 2026.

Scope: the income boxes of `Income.lean` except foreign-source salaries and pensions (1AG, 1AF, 1AL, 1AM rows)
and directors' pay of art. 62 (1GB row); `inScope` says so. No foreign tax credit (8VM) is modelled.

Where the statute leaves a computation open (how the pension allowance is split between pensions and alimony,
how a half of the common income is rounded) the model does what the DGFiP's M code does; those are readings,
noted where they occur. Where the statute's words decide, the model follows them, and `PAS.md` lists where M
does otherwise.
-/

namespace FrTax
namespace PAS

/-! ## Rounding of a rate (art. 204 H, I, 3) -/

/-- `num / den` as a rate in tenths of a per cent, rounded half up; 0 for no income. -/
def rateOf (num den : Int) : Int := if den ≤ 0 then 0 else rnd (1000 * num) den

theorem rateOf_nonneg {num den : Int} (h : 0 ≤ num) : 0 ≤ rateOf num den := by
  unfold rateOf
  split
  · exact Int.le_refl 0
  · exact rnd_nonneg (by omega) (by omega)

/-- A rate never exceeds `c` tenths of a per cent when the numerator is at most `c / 1000` of the denominator. -/
theorem rateOf_le {num den c : Int} (hd : 0 < den) (h : 1000 * num ≤ c * den) : rateOf num den ≤ c := by
  unfold rateOf
  rw [if_neg (show ¬ den ≤ 0 by omega)]
  calc rnd (1000 * num) den ≤ rnd (c * den) den := rnd_mono hd h
    _ = c := rnd_exact c den hd

/-- **The household rate is at most 100 %** when the tax is at most the income it is computed on. -/
theorem rateOf_le_full {num den : Int} (hd : 0 < den) (h : num ≤ den) : rateOf num den ≤ 1000 :=
  rateOf_le hd (by omega)

/-- **And at most 45 %** (the top slice of art. 197, I, 1) when the tax is at most 45 % of that income. -/
theorem rateOf_le_45 {num den : Int} (hd : 0 < den) (h : 100 * num ≤ 45 * den) : rateOf num den ≤ 450 :=
  rateOf_le hd (by omega)

/-- **The rate is non-decreasing in the tax**: for the same income, more tax never gives a lower rate. -/
theorem rateOf_mono_num {num num' den : Int} (h : num ≤ num') : rateOf num den ≤ rateOf num' den := by
  unfold rateOf
  split
  · exact Int.le_refl 0
  · exact rnd_mono (by omega) (by omega)

/-! ## Default grids (art. 204 H, III, 1, a to c) -/

inductive Zone | metropole | gmr | gm
  deriving Repr, DecidableEq

def Zone.ofString : String → Option Zone
  | "metropole" => some .metropole | "gmr" => some .gmr | "gm" => some .gm | _ => none

/-- The twenty rates of the grids, in tenths of a per cent (the same in every year and zone). -/
def gridRates : List Int := [0, 5, 13, 21, 29, 35, 41, 53, 75, 99, 119, 138, 158, 179, 200, 240, 280, 330, 380, 430]

/-- The lower bounds of brackets 2 to 20, in euros of monthly base, as art. 204 H, III, 1 prints them in each
rate year: loi n° 2020-1721 (2021), n° 2021-1900 (2022), n° 2022-1726 (2023), n° 2023-1322 (2024),
n° 2025-127 (2025, for income from 1 May 2025), n° 2026-103 (2026, for income from 1 May 2026). -/
def gridLows : Nat → Zone → Option (List Int)
  | 2021, .metropole => some [1420,1475,1570,1676,1791,1887,2012,2381,2725,3104,3494,4077,4888,6116,7640,10604,14362,22545,48292]
  | 2021, .gmr => some [1629,1728,1904,2079,2296,2421,2505,2755,3406,4359,4952,5736,6872,7640,8684,11940,15865,24215,52930]
  | 2021, .gm => some [1745,1887,2104,2371,2463,2547,2630,2922,4033,5219,5887,6830,7515,8325,9661,12997,16533,26496,55926]
  | 2022, .metropole => some [1440,1496,1592,1699,1816,1913,2040,2414,2763,3147,3543,4134,4956,6202,7747,10752,14563,22860,48967]
  | 2022, .gmr => some [1652,1752,1931,2108,2328,2455,2540,2794,3454,4420,5021,5816,6968,7747,8805,12107,16087,24554,53670]
  | 2022, .gm => some [1769,1913,2133,2404,2497,2583,2667,2963,4089,5292,5969,6926,7620,8441,9796,13179,16764,26866,56708]
  | 2023, .metropole => some [1518,1577,1678,1791,1914,2016,2150,2544,2912,3317,3734,4357,5224,6537,8165,11333,15349,24094,51611]
  | 2023, .gmr => some [1741,1847,2035,2222,2454,2588,2677,2945,3641,4659,5292,6130,7344,8165,9280,12761,16956,25880,56568]
  | 2023, .gm => some [1865,2016,2248,2534,2632,2722,2811,3123,4310,5578,6291,7300,8031,8897,10325,13891,17669,28317,59770]
  | 2024, .metropole => some [1591,1653,1759,1877,2006,2113,2253,2666,3052,3476,3913,4566,5475,6851,8557,11877,16086,25251,54088]
  | 2024, .gmr => some [1825,1936,2133,2329,2572,2712,2805,3086,3816,4883,5546,6424,7697,8557,9725,13374,17770,27122,59283]
  | 2024, .gm => some [1955,2113,2356,2656,2758,2853,2946,3273,4517,5846,6593,7650,8416,9324,10821,14558,18517,29676,62639]
  | 2025, .metropole => some [1620,1683,1791,1911,2042,2151,2294,2714,3107,3539,3983,4648,5574,6974,8711,12091,16376,25706,55062]
  | 2025, .gmr => some [1858,1971,2171,2371,2618,2761,2855,3142,3885,4971,5646,6540,7836,8711,9900,13615,18090,27610,60350]
  | 2025, .gm => some [1990,2151,2398,2704,2808,2904,2999,3332,4598,5951,6712,7788,8567,9492,11016,14820,18850,30210,63767]
  | 2026, .metropole => some [1635,1698,1807,1928,2060,2170,2315,2738,3135,3571,4019,4690,5624,7037,8789,12200,16523,25937,55558]
  | 2026, .gmr => some [1875,1989,2191,2392,2642,2786,2881,3170,3920,5016,5697,6599,7907,8789,9989,13738,18253,27858,60893]
  | 2026, .gm => some [2008,2170,2420,2728,2833,2930,3026,3362,4639,6005,6772,7858,8644,9577,11115,14953,19020,30482,64341]
  | _, _ => none

/-- How many lower bounds are at or below the base: the index of the bracket the base falls in ("supérieure ou
égale à ... et inférieure à ..."). -/
def countLe : List Int → Int → Nat
  | [], _ => 0
  | x :: xs, b => (if x ≤ b then 1 else 0) + countLe xs b

/-- The default rate of a monthly base on a grid. -/
def gridRate (lows : List Int) (b : Int) : Int := gridRates.getD (countLe lows b) 0

def defaultRate (rateYear : Nat) (z : Zone) (b : Int) : Option Int := (gridLows rateYear z).map (gridRate · b)

theorem countLe_mono (l : List Int) {b b' : Int} (h : b ≤ b') : countLe l b ≤ countLe l b' := by
  induction l with
  | nil => simp [countLe]
  | cons x xs ih =>
    simp only [countLe]
    split <;> split <;> omega

theorem countLe_le (l : List Int) (b : Int) : countLe l b ≤ l.length := by
  induction l with
  | nil => simp [countLe]
  | cons x xs ih =>
    simp only [countLe, List.length_cons]
    split <;> omega

theorem gridRates_mono : ∀ j, j < 20 → ∀ i, i < j + 1 → gridRates.getD i 0 ≤ gridRates.getD j 0 := by decide

theorem gridRates_le_43 : ∀ i, i < 20 → gridRates.getD i 0 ≤ 430 := by decide

/-- **Every grid is non-decreasing in the base**: earning more never lowers the default rate. -/
theorem gridRate_mono (lows : List Int) (hl : lows.length = 19) {b b' : Int} (h : b ≤ b') :
    gridRate lows b ≤ gridRate lows b' := by
  unfold gridRate
  have h1 := countLe_mono lows h
  have h2 := countLe_le lows b'
  exact gridRates_mono _ (by omega) _ (by omega)

/-- **No default rate exceeds 43 %.** -/
theorem gridRate_le_43 (lows : List Int) (hl : lows.length = 19) (b : Int) : gridRate lows b ≤ 430 := by
  unfold gridRate
  have := countLe_le lows b
  exact gridRates_le_43 _ (by omega)

/-- Below the first bound the default rate is nil. -/
theorem countLe_zero (lows : List Int) (b : Int) (hb : ∀ x ∈ lows, b < x) : countLe lows b = 0 := by
  induction lows with
  | nil => rfl
  | cons x xs ih =>
    simp only [countLe]
    have hx : ¬ x ≤ b := by have := hb x (List.mem_cons_self ..); omega
    rw [if_neg hx, ih (fun y hy => hb y (List.mem_cons_of_mem _ hy))]

theorem gridRate_zero (lows : List Int) (b : Int) (hb : ∀ x ∈ lows, b < x) : gridRate lows b = 0 := by
  unfold gridRate
  rw [countLe_zero lows b hb]; rfl

/-- The eighteen grids as printed: nineteen bounds each, strictly increasing. -/
def wellFormed (l : List Int) : Bool := l.length == 19 && (l.zip l.tail).all fun (a, b) => a < b

theorem grids_wellFormed :
    ([2021, 2022, 2023, 2024, 2025, 2026].all fun y => [Zone.metropole, .gmr, .gm].all fun z =>
      match gridLows y z with | some l => wellFormed l | none => false) = true := by decide

/-- **In every rate year and zone, the default rate is non-decreasing in the base and at most 43 %** (with
`grids_wellFormed`, which gives the nineteen bounds). -/
theorem defaultRate_mono (y : Nat) (z : Zone) (lows : List Int) (hg : gridLows y z = some lows)
    (hl : lows.length = 19) {b b' : Int} (h : b ≤ b') :
    defaultRate y z b = some (gridRate lows b) ∧ defaultRate y z b' = some (gridRate lows b') ∧
      gridRate lows b ≤ gridRate lows b' ∧ gridRate lows b' ≤ 430 := by
  unfold defaultRate; rw [hg]
  exact ⟨rfl, rfl, gridRate_mono lows hl h, gridRate_le_43 lows hl b'⟩

/-! ## The income of art. 204 A, person by person -/

/-- Boxes outside the model's scope for the rate (foreign-source salaries and pensions, art. 62 pay). -/
def outOfScope : List String :=
  ["1GB", "1HB", "1IB", "1JB", "1KB", "1LB"] ++
    (Who.all.map fun w => [row "1" "F" w, row "1" "G" w, row "1" "L" w, row "1" "M" w]).flatten

def inScope (d : Decl) : Bool := outOfScope.all fun b => !d.has b

/-- Each pensioner's 10 % allowance (art. 158, 5, a): 10 % of their pensions, at least `penMin`, at most the
pensions. The household's total is at most `penMax`; the statute does not say how that total is shared between
the pensioners. The reading M uses (ABPRV ... ABPR4): an allowance at its minimum is kept whole, the others share
what is left of `penMax` in proportion (rounded), and the last pensioner in the order 1, 2, dependants takes the
remainder. -/
def penEach (p : Params) (d : Decl) (w : Who) : Int :=
  let g := grossPension d w
  if g ≤ 0 then 0 else min g (max p.penMin (pct 1000 g))

def penAtMin (p : Params) (d : Decl) (w : Who) : Bool :=
  let g := grossPension d w
  min p.penMin g ≥ pct 1000 g

def penAllowanceOf (p : Params) (d : Decl) (w : Who) : Int :=
  let tot := Who.all.foldl (fun a w => a + penEach p d w) 0
  let minSum := Who.all.foldl (fun a w => a + (if penAtMin p d w then penEach p d w else 0)) 0
  let propSum := tot - minSum
  let plpb := p.penMax - minSum
  let share (x : Who) : Int :=
    if penAtMin p d x then penEach p d x
    else if propSum ≤ 0 then 0 else rnd (min (penEach p d x * propSum) (plpb * penEach p d x)) propSum
  -- the persons after `w` in the order of M (declarant 1, declarant 2, dependants 1 to 4)
  let order := Who.all
  let idx := (order.findIdx? (· == w)).getD 0
  let later := (order.drop (idx + 1)).any fun x => grossPension d x > 0
  if w == .v || later then share w
  else pos (min tot p.penMax - (order.take idx).foldl (fun a x => a + share x) 0)

/-- Alimony received (1AO row) net of its share of the allowance: the allowance is spread over the pensions
(1AS), disability pensions (1AZ) and alimony in proportion, the last of them taking what rounding leaves (the
reading M uses, APR1AO). Art. 204 G, 2, 5°: "le montant net imposable". -/
def alimonyNet (p : Params) (d : Decl) (w : Who) : Int :=
  let o := d.get (row "1" "O" w)
  if o ≤ 0 then 0 else
  let e := grossPension d w
  let a := penAllowanceOf p d w
  o - (a - rnd (a * d.get (row "1" "S" w)) e - rnd (a * d.get (row "1" "Z" w)) e)

/-- Salaries, pensions and annuities of a person net of the allowances (art. 79 category, "traitements, salaires,
pensions et rentes viagères"). -/
def tsNet (p : Params) (d : Decl) (w : Who) : Int :=
  netSalary p d w + (grossPension d w - penAllowanceOf p d w)

/-- Micro and real business profits of a person (art. 204 G, 2, 1° to 3°: the taxable result, a deficit counting
for nothing, 204 G, 3). -/
def microNetOf (d : Decl) (w : Who) : Int :=
  (microCategories d w).foldl (fun a (bs, r) =>
    let g := d.sum bs
    a + (if g ≤ 0 then 0 else g - min g (max 305 (pct r g)))) 0

def realOf (d : Decl) : Who → Int
  | .v => d.sum ["5KC", "5QC", "5HC"] | .c => d.sum ["5LC", "5RC", "5IC"]
  | .p1 => d.sum ["5MC", "5SC", "5JC"] | _ => 0

def profits (d : Decl) (w : Who) : Int := pos (microNetOf d w + realOf d w)

/-- A person's income of art. 204 A at its net taxable amount, a deficit counting for nothing (204 H, I, 1). -/
def netOwn (p : Params) (d : Decl) (w : Who) : Int := pos (tsNet p d w) + profits d w

/-- A person's income at the amounts of art. 204 F (salaries and pensions under the retenue, before the 10 %
allowances: "avant application ... du 3° de l'article 83 et des deuxième et dernier alinéas du a du 5 de
l'article 158") and 204 G (alimony, profits: net taxable amount). -/
def denOwn (p : Params) (d : Decl) (w : Who) : Int :=
  pos (grossSalary d w) + d.get (row "1" "S" w) + d.get (row "1" "Z" w) + alimonyNet p d w + profits d w

/-- Common income of the household: annuities bought for value (art. 158, 6) and property income (204 G, 2,
4°), both under the acompte. -/
def common (d : Decl) : Int := annuities d + propertyIncome d

def deps : List Who := [.p1, .p2, .p3, .p4]

def sumW (ws : List Who) (f : Who → Int) : Int := ws.foldl (fun a w => a + f w) 0

/-! ## The household rate (art. 204 H, I and II) -/

/-- Art. 204 H, II, 2°: the RFR per part under which the rate is nil (the only figure of the II test: one amount
per part, no separate half-part or quarter-part increment, no second RFR condition), keyed by income year N
(rates from 1 September N+1).

The statute indexes it: "Le montant des revenus prévu au 2° du présent II est indexé chaque année comme la limite
supérieure de la première tranche du barème de l'impôt sur le revenu". These are the indexed figures, as applied
on 1 September N+1. The figure printed in the consolidated CGI lags one indexation behind, because each
codification decree (n° 2021-744, 2022-782, 2023-422, 2024-496, 2025-547, 2026-562) records the previous year's
indexation; an earlier version of this model used those printed figures (25 654 € for income 2020, ...,
29 310 € for income 2025), which was an error of ours.

Sources: BOFiP BOI-IR-PAS-20-20-10, versions 20220516 (25 705 €, rates from Sept 2021), 20230626 (26 065 €),
20240618 (27 473 €), 20250507 (28 792 €), 20260407 (29 310 €, and 29 574 € for Sept 2026 in its "Remarque"; § 180:
"indexé chaque année, le 1er septembre, comme la limite supérieure de la première tranche du barème"); the same
figures are M's `RFRPARQF` (tgvI.m, sources 2020m_6_5 ... 2025m_3_11) and the DGFiP production simulator's. -/
def zeroRateThreshold : Nat → Int
  | 2020 => 25705 | 2021 => 26065 | 2022 => 27473 | 2023 => 28792 | 2024 => 29310 | 2025 => 29574 | _ => 0

structure Household where
  /-- the income tax of art. 197, I, 1 to 4 (after the cap and the décote) -/
  ir : Int
  /-- income of 204 A at net taxable amounts, deficits nil -/
  pasNet : Int
  /-- the revenu net imposable at the scale, without deficits, charges and allowances -/
  total : Int
  /-- the numerator: `ir * pasNet / total`, rounded to the euro -/
  num : Int
  /-- the denominator: income of 204 A at the amounts of 204 F and 204 G -/
  den : Int
  /-- the rate of I, in tenths of a per cent -/
  rateI : Int
  /-- II applies -/
  zeroII : Bool
  /-- the household rate -/
  rate : Int
  /-- diagnostic: the rate if a tax under 61 € counted as nil (what M does: SEUIL_61 in IRTOTAL) -/
  rate61 : Int
  deriving Repr

def household (p : Params) (d : Decl) : Household :=
  let r := compute p d
  let ir := r.capped.tax - r.decote
  let pasNet := sumW Who.all (netOwn p d) + common d
  let total := pasNet + investmentAtScale d + gainsAtScale d
  let numOf (t : Int) := if total ≤ 0 then 0 else pos (rnd (t * min pasNet total) total)
  let num := numOf ir
  let den := sumW Who.all (denOwn p d) + common d
  let rateI := rateOf num den
  -- II: the tax "mis en recouvrement" nil for the last two years (the year before is an input: box 8OT, or
  -- BTINDIR as M names it) and the RFR under the threshold per part
  let prevNil := d.has "8OT" || d.has "BTINDIR"
  let zeroII := prevNil && r.net ≤ 0 && 4 * r.rfr < r.quarters * zeroRateThreshold d.year
  { ir, pasNet, total, num, den, rateI, zeroII, rate := if zeroII then 0 else rateI,
    rate61 := if zeroII then 0 else rateOf (numOf (if ir < 61 then 0 else ir)) den }

/-! ## Individualised rates (art. 204 M) -/

/-- The scale with `e` eighths of a part (a couple's parts halved: 2.25 parts become 1.125), exactly, then
rounded: `Σ rate% * max(0, min(8r, e*hi) - e*lo) / 800`. -/
def scale8raw (p : Params) (r e : Int) : Int :=
  let s (rate lo : Int) (hi : Option Int) : Int :=
    let top := match hi with | some h => min (8 * r) (e * h) | none => 8 * r
    rate * pos (top - e * lo)
  s 11 p.b1 (some p.b2) + s 30 p.b2 (some p.b3) + s 41 p.b3 (some p.b4) + s 45 p.b4 none

def scale8 (p : Params) (r e : Int) : Int := rnd (scale8raw p r e) 800

/-- Art. 204 M, 2: the tax on `rev` with half the household's parts, by the rules of art. 197, I, 1 to 4: the
scale, the cap on the quotient familial for the half parts above one part, the complementary reduction (halved),
and the décote with the base `decBase`. The cap is an amount of reduction and is rounded on its own (art. 1657, 1,
as for the household: `capped`); a quarter of a half part's cap may end in 0.50. (M rounds it on its own in the
2025 code, IRINDPAS2; with the tax in one rounding in the 2020 to 2024 code.) -/
def taxHalfParts (p : Params) (d : Decl) (rev decBase : Int) : Int :=
  let e := quarters d                       -- half the parts, in eighths of a part
  let full := scale8 p rev e
  -- e - 8 eighths are (e - 8) / 4 half parts, each capped at qfHalf
  let refCapped := scale8 p rev 8 - rnd (p.qfHalf * (e - 8)) 4
  let capped := max full refCapped
  let compl := rnd (art195_other d (family d) * p.qfComplement) 4
  let t := capped - (if capped > full then min compl (capped - full) else 0)
  t - min t (pos (rnd (decBase * 10000 - 4525 * t) 10000))

structure Indiv where
  rate1 : Int
  rate2 : Int
  deriving Repr

def half (x : Int) : Int := rnd x 2

/-- Art. 204 M. `decBase` is the décote base used for the tax with half the parts. -/
def individual (p : Params) (d : Decl) (h : Household) (decBase : Int) : Indiv :=
  let own (w : Who) := netOwn p d w
  if h.rate = 0 then { rate1 := 0, rate2 := 0 } else
  if own .v = own .c then { rate1 := h.rate, rate2 := h.rate } else
  -- 2: the partner who "a personnellement disposé des revenus les plus faibles"
  let lo : Who := if own .v < own .c then .v else .c
  let hi : Who := if own .v < own .c then .c else .v
  let depNet := half (sumW deps (netOwn p d))
  let depDen := half (sumW deps (denOwn p d))
  -- the half of common income and of the deductions, each rounded (the reading M uses)
  let ord := tsNet p d lo + profits d lo + half (sumW deps (fun w => tsNet p d w + profits d w))
    + half (annuities d) + half (investmentAtScale d) + half (gainsAtScale d) + half (propertyIncome d)
  let chg := half (d.get "4BC") + half (d.get "6DE" + csgOnInvestments d)
    + half (charges p d - d.get "6DE" - csgOnInvestments d + retirementDeduction d)
    + half (ageAllowance p d (netGlobal p d)) + half (attachedAllowance p d)
  let rev := pos (ord - chg)
  let irLo := taxHalfParts p d rev decBase
  let pasLo := own lo + depNet + half (common d)
  let totLo := own lo + depNet + half (annuities d) + half (investmentAtScale d) + half (gainsAtScale d)
    + half (propertyIncome d)
  let numLo := if totLo ≤ 0 then 0 else pos (rnd (irLo * min pasLo totLo) totLo)
  let rLo := rateOf numLo (denOwn p d lo + depDen + half (common d))
  -- 3: the other partner: the household numerator less the tax on the first partner's own income at their
  -- rate and on the common income at the household rate, over their own income alone
  let irPremier := rnd (denOwn p d lo * rLo) 1000
  let irCommun := rnd ((sumW deps (denOwn p d) + common d) * h.rate) 1000
  let rHi := rateOf (pos (h.num - irPremier - irCommun)) (denOwn p d hi)
  if lo = .v then { rate1 := rLo, rate2 := rHi } else { rate1 := rHi, rate2 := rLo }

/-- Output fields for the runner (rates in tenths of a per cent). -/
structure Out where
  h : Household
  /-- art. 204 M, the décote of couples ("soumis à imposition commune": the words of art. 197, I, 4) -/
  ind : Option Indiv
  /-- the same with the décote of single people (what M does: SEUIL_DECOTE1) -/
  indSingle : Option Indiv

def out (p : Params) (d : Decl) : Out :=
  let h := household p d
  let indOk := d.couple && flatLevyIncome d = 0
  { h, ind := if indOk then some (individual p d h p.decCouple) else none,
    indSingle := if indOk then some (individual p d h p.decSingle) else none }

/-- `54` ↦ `5.4`. -/
def fmt (t : Int) : String := (if t < 0 then "-" else "") ++ s!"{t.natAbs / 10}.{t.natAbs % 10}"

end PAS
end FrTax
