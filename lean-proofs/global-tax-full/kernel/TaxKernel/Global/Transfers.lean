import TaxKernel.Global.Property

/-!
# TaxKernel.Global.Transfers (2.0.0): inheritance and gift (OECD 4300), transfer and stamp duties (4400)

**Whole-amount ("slab") tariffs.** Many inheritance tariffs and stamp duties charge the rate of the bracket the
*whole* amount falls in to the whole amount (DE ErbStG § 19 (1); old UK stamp duty; many land-transfer slabs), unlike
a marginal `Schedule`. `slabRate rows top x` is the rate of the first row whose upper limit is ≥ x (else `top`);
`slabTicks = rate × x`. Each limit is a notch. DE § 19 (3) softens the notches ("Härteausgleich"): above a limit the
tax may exceed the tax at the previous limit only by half (rate ≤ 30 %) or three quarters (rate > 30 %) of the excess:
`slabRelieved rows top relief x = min (slab tax, tax at the previous limit + relief(rate) × excess)`.

**Inheritance and gift tax** (`InheritanceTax`): the recipient's class from the relationship; per class a personal
allowance and a tariff (marginal or slab); extra allowances (DE § 17 by the child's age); exempt relationships
(spouses in UK-style estate taxes, charities); a look-back that adds earlier gifts from the same donor within N years
(DE § 14 (1): ten years; the tax on the total less the tax the earlier gifts would bear today). Estate-based taxes
(UK IHT, US estate tax) are a charge on the sum of the estate's transfers with a nil-rate band: `estateCharge`.

**Transfer duties** (`TransferDuty`): on the price or the higher of price and assessed value; marginal or slab;
a first-home schedule under a price cap; a surcharge for additional homes or non-residents (bp of the base).
Securities transfer taxes are a flat `TransferDuty` on purchases of shares.

Theorems: `slabRelieved_le`, `lookback_split` (two gifts within the window bear the tax on their sum: splitting a gift
inside the look-back gains nothing), `lookback_zero`, `TransferDuty.base_ge_price`.
-/

namespace TaxKernel.Global
open TaxKernel

/-! ## Slab tariffs -/

/-- Rate of the first row `(upper limit, rate)` whose limit is ≥ `x`, else `top`; and the previous row. -/
def slabLookup (rows : List (Int × Int)) (top x : Int) : Int × Option (Int × Int) :=
  go rows none
where
  go : List (Int × Int) → Option (Int × Int) → Int × Option (Int × Int)
    | [], prev => (top, prev)
    | (l, r) :: rest, prev => if x ≤ l then (r, prev) else go rest (some (l, r))

def slabRate (rows : List (Int × Int)) (top x : Int) : Int := (slabLookup rows top x).1

/-- Whole-amount tariff, in ticks. -/
def slabTicks (rows : List (Int × Int)) (top x : Int) : Int := slabRate rows top x * x

/-- Whole-amount tariff with a hardship relief: above a limit `l` (previous row, rate `rl`), the tax is at most
`rl × l + relief(rate) × (x − l)` (ticks; `relief` in bp of the excess). -/
def slabRelieved (rows : List (Int × Int)) (top : Int) (relief : Int → Int) (x : Int) : Int :=
  match slabLookup rows top x with
  | (r, none) => r * x
  | (r, some (l, rl)) => min (r * x) (rl * l + relief r * (x - l))

theorem slabRelieved_le (rows : List (Int × Int)) (top : Int) (relief : Int → Int) (x : Int) :
    slabRelieved rows top relief x ≤ slabTicks rows top x := by
  unfold slabRelieved slabTicks slabRate
  split <;> rename_i h <;> simp [h] <;> omega

/-! ## Inheritance and gift tax -/

structure TaxClass where
  allowance : Int
  /-- marginal tariff (used when `slab` is empty) -/
  sched : Schedule := Schedule.flat 0
  /-- whole-amount tariff rows (upper limit, rate) and the rate above the last -/
  slab : List (Int × Int) := []
  slabTop : Int := 0
  /-- hardship relief on the slab (bp of the excess, by the rate reached), e.g. DE § 19 (3) -/
  relief : Option (Int → Int) := none
  /-- rounding of the taxable acquisition (DE § 10 (1) Satz 6: down to 100 €) and of the tax -/
  baseRound : Rule := {}
  round : Rule := {}

instance : Inhabited TaxClass := ⟨{ allowance := 0 }⟩

def TaxClass.ticks (c : TaxClass) (x : Int) : Int :=
  if c.slab.isEmpty then c.sched.ticks x
  else match c.relief with
    | some f => slabRelieved c.slab c.slabTop f x
    | none => slabTicks c.slab c.slabTop x

def TaxClass.tax (c : TaxClass) (x : Int) : Int := c.round.ofTicks (c.ticks x)

structure InheritanceTax where
  name : String := "inheritance and gift tax"
  classOf : Relation → Nat
  classes : List TaxClass
  exemptRelations : List Relation := []
  /-- earlier gifts from the same donor within this many years are added (0: none) -/
  lookbackYears : Nat := 0
  /-- extra allowance for one transfer (age-dependent, home relief) -/
  extraAllowance : Transfer → Int := fun _ => 0
  /-- exempt part of the value (business relief, home) -/
  exemptValue : Transfer → Int := fun _ => 0

/-- Tax on `current` with `prior` acquisitions inside the look-back: tax on the sum less the tax on the prior ones. -/
def withLookback (f : Int → Int) (prior current : Int) : Int := f (prior + current) - f prior

namespace InheritanceTax
def classFor (it : InheritanceTax) (t : Transfer) : TaxClass := (it.classes[it.classOf t.relation]?).getD default

def priorWithin (it : InheritanceTax) (t : Transfer) : Int :=
  isum ((t.prior.filter fun (_, y) => y < it.lookbackYears).map (·.1))

/-- Taxable acquisition from an amount (before look-back): value less exemptions and allowances, rounded. -/
def taxableOf (it : InheritanceTax) (t : Transfer) (v : Int) : Int :=
  let c := it.classFor t
  c.baseRound.apply (pos (v - it.exemptValue t - c.allowance - it.extraAllowance t))

def taxOn (it : InheritanceTax) (t : Transfer) (v : Int) : Int := (it.classFor t).tax (it.taxableOf t v)

/-- Tax on one transfer, with the look-back. -/
def tax (it : InheritanceTax) (t : Transfer) : Int :=
  if it.exemptRelations.contains t.relation then 0
  else pos (withLookback (it.taxOn t) (it.priorWithin t) t.statutoryValue)

def charges (it : InheritanceTax) (ts : List Transfer) (statute : String) : List Charge :=
  ts.zipIdx.map fun (t, i) =>
    charge .estate it.name t.statutoryValue (fun v => if it.exemptRelations.contains t.relation then 0 else it.taxableOf t (it.priorWithin t + v))
      (fun _ => it.tax t) (event := s!"{if t.kind == .gift then "gift" else "inheritance"} {i + 1}")
      (statute := statute)
end InheritanceTax

/-- Estate-based tax: one charge on the estate (sum of transfers to non-exempt recipients) above a nil-rate band. -/
def estateCharge (name : String) (sched : Schedule) (round : Rule) (nilBand : Int) (exempt : List Relation)
    (ts : List Transfer) (statute : String) : Charge :=
  let estate := isum ((ts.filter fun t => !(exempt.contains t.relation)).map (·.statutoryValue))
  charge .estate name estate (fun e => pos (e - nilBand)) (sched.tax round) (event := "estate") (statute := statute)

/-- Two transfers within the look-back bear exactly the tax on their sum: splitting gains nothing. -/
theorem lookback_split (f : Int → Int) (a b : Int) :
    withLookback f 0 a + withLookback f a b = f (a + b) - f 0 := by
  unfold withLookback; simp only [Int.zero_add]; omega

theorem lookback_zero (f : Int → Int) (x : Int) : withLookback f 0 x = f x - f 0 := by
  unfold withLookback; simp

/-! ## Transfer and stamp duties -/

structure TransferDuty where
  name : String
  sched : Schedule := Schedule.flat 0
  slab : List (Int × Int) := []
  slabTop : Int := 0
  /-- base = max(price, assessed value) where the assessed value is given -/
  higherOfAssessed : Bool := false
  /-- first-home schedule when the price ≤ `firstHomeCap` (−1: no relief) -/
  firstHomeCap : Int := -1
  firstHomeSched : Schedule := Schedule.flat 0
  /-- surcharge for an additional home / a non-resident buyer, bp of the base -/
  additionalBp : Int := 0
  nonResidentBp : Int := 0
  kinds : List AssetKind := [.home, .realEstate, .land]
  round : Rule := {}

namespace TransferDuty
def base (d : TransferDuty) (p : Purchase) : Int :=
  if d.higherOfAssessed ∧ 0 ≤ p.assessed then max p.price p.assessed else p.price

def ticks (d : TransferDuty) (p : Purchase) : Int :=
  let b := d.base p
  let main :=
    if p.firstHome ∧ 0 ≤ d.firstHomeCap ∧ p.price ≤ d.firstHomeCap then d.firstHomeSched.ticks b
    else if d.slab.isEmpty then d.sched.ticks b else slabTicks d.slab d.slabTop b
  main + (if p.additionalHome then d.additionalBp * pos b else 0) + (if p.nonResident then d.nonResidentBp * pos b else 0)

def amount (d : TransferDuty) (p : Purchase) : Int :=
  if d.kinds.contains p.kind then d.round.ofTicks (d.ticks p) else 0

def charges (d : TransferDuty) (ps : List Purchase) (statute : String) (level : Level := .central) : List Charge :=
  (ps.zipIdx.filter fun (p, _) => d.kinds.contains p.kind).map fun (p, i) =>
    charge .transactions d.name p.price (fun _ => d.base p) (fun _ => d.amount p) (event := s!"purchase {i + 1}")
      (level := level) (statute := statute)
end TransferDuty

theorem TransferDuty.base_ge_price (d : TransferDuty) (p : Purchase) : p.price ≤ d.base p := by
  unfold TransferDuty.base; split <;> omega

end TaxKernel.Global
