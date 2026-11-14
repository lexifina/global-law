import LegalProofs.USTax.Entity.Partnership
import TaxCode.Individual.Form1040

/-!
# A contribution game: a parent's built-in gain in a family partnership

A parent (married, filing jointly, with a wage) contributes depreciable equipment worth `book` with adjusted basis
`basis` and `remaining` years left on its schedule to a partnership; an adult child (single, with a wage of their own)
contributes cash. Shares follow capital. The cash earns `cashBp` a year; the equipment earns the same return on its
market value plus its economic depreciation (its value falls straight line to nothing over its remaining life), so a
dollar of either capital earns the same and pooling them at capital shares moves no economic income between the
partners. All income is ordinary. The partnership sells the equipment at the start of a chosen year for its market
value, and liquidates at the horizon, paying each partner its book capital account in cash (§731(a): gain or loss on
the difference from outside basis, capital). (Distributions of the property itself, §§704(c)(1)(B) and 737, are in
`Partnership.lean` and tested against the regulations, but are not moves here.)

Every year's tax of both people comes from the 2025 household model. The child is a limited partner who does not
materially participate: the child's net partnership loss is suspended (§469(a), (d)(1)) and carried forward
(§469(b)), and freed on the final disposition (§469(g)(1)(A)); the child's partnership income is net investment
income. The parent materially participates. The sale gain on equipment sold for no more than its original cost is
§1245 ordinary income (all of it here).

Against this, the baseline: no partnership; the parent keeps and depreciates the equipment, sells it the same year for
the same price, and the child invests the same cash at the same yield. Score: the family's total tax over the years
(lower is better); the partnership changes nothing economically (each person's cash is its book capital), so a
difference is a tax difference only.
-/

namespace Legal.USTax.Entity.Contrib
open TaxCode.Individual Legal.USTax.Entity

structure Game where
  wageP : Int          -- the parent couple's wages
  wageK : Int          -- the child's wage
  book : Int
  basis : Int
  remaining : Nat
  newLife : Nat
  childCash : Int
  cashBp : Int         -- the yield on every dollar of capital
  horizon : Nat
  deriving Repr, Inhabited

structure Move where
  method : Method
  saleYear : Nat       -- the equipment is sold at the start of this year (1 ≤ saleYear < horizon)
  deriving Repr, Inhabited

/-- The equipment's market value at the start of year `t`: it falls straight line over its remaining tax life. -/
def fmvAt (g : Game) (t : Nat) : Int := if t ≥ g.remaining then 0 else g.book - g.book * t / g.remaining

/-- While held, the equipment earns the yield on its value plus its fall in value (before depreciation); the cash it
has recovered, and the child's cash, earn the yield. After the sale everything is cash. Every dollar of capital earns
the same, so pooling at fixed capital shares moves no economic income between the partners. -/
def opInc (g : Game) (t : Nat) : Int := bps (fmvAt g t) g.cashBp + (fmvAt g t - fmvAt g (t + 1))
def cashInc (g : Game) (held : Bool) (t : Nat) : Int :=
  bps (g.childCash + g.book - (if held then fmvAt g t else 0)) g.cashBp

def parentTax (g : Game) (ord cap : Int) : Int :=
  (form1040 { filing := .mfj, head := { age := 55 }, spouse := some { age := 55 }, wages := g.wageP,
              otherIncome := ord, longTermGains := cap }).netTax
/-- The child's partnership income is passive and net investment income (entered as interest, which the household
model counts in both). -/
def childTax (g : Game) (nii cap : Int) : Int :=
  (form1040 { filing := .single, head := { age := 28 }, wages := g.wageK, taxableInterest := nii,
              longTermGains := cap }).netTax

structure Out where
  family : Int       -- total tax, both, every year (and the liquidation year)
  parent : Int
  child : Int
  deriving Repr, Inhabited

/-- The partnership. Each year's book income is distributed, which lowers book and tax capital alike and so is left
out of both. At the horizon the partnership liquidates in cash equal to book capital (§731(a): capital gain or loss
against outside basis, which is tax capital here, there being no liabilities). -/
def play (g : Game) (mv : Move) : Out :=
  let c : Contributed := ⟨g.book, g.basis, g.remaining, g.newLife⟩
  let sC := g.book * 10000 / (g.book + g.childCash)
  let m := mv.method
  -- returns (parent tax, child tax, child's suspended loss, tax capital P, K, book capital P, K)
  let rec go : Nat → Nat → Int → Int → Int → Int → Int → Int → Int → Int × Int × Int × Int × Int × Int × Int
    | 0, _, pt, kt, susp, tcP, tcK, bcP, bcK => (pt, kt, susp, tcP, tcK, bcP, bcK)
    | k + 1, t, pt, kt, susp, tcP, tcK, bcP, bcK =>
      let held := decide (t < mv.saleYear)
      let sale := if t = mv.saleYear then saleAlloc m c sC 0 t (fmvAt g t) else ⟨0, 0, 0, 0⟩
      let other := cashInc g held t + (if held then opInc g t else 0)
      let a : Alloc := if held then yearAlloc m c sC other t else
          ⟨bps other sC, other - bps other sC, bps other sC, other - bps other sC⟩
      let ordP := a.cTax + sale.cTax
      -- §469: the child's net passive income; a net loss is suspended and carried forward
      let netK := a.nTax + sale.nTax + susp
      let tP := parentTax g ordP 0
      let tK := childTax g (max 0 netK) 0
      go k (t + 1) (pt + tP) (kt + tK) (min 0 netK) (tcP + ordP) (tcK + a.nTax + sale.nTax)
        (bcP + a.cBook + sale.cBook) (bcK + a.nBook + sale.nBook)
  let (pt, kt, susp, tcP, tcK, bcP, bcK) := go g.horizon 0 0 0 0 g.basis g.childCash g.book g.childCash
  -- book income was distributed: what is left of book capital is each partner's original capital
  let tP := parentTax g 0 (bcP - tcP)
  -- §469(g)(1)(A): the suspended loss is freed on the complete disposition (ordinary, against any income)
  let tK := (form1040 { filing := .single, head := { age := 28 }, wages := g.wageK, otherIncome := susp,
                        longTermGains := bcK - tcK }).netTax
  ⟨pt + kt + tP + tK, pt + tP, kt + tK⟩

/-- The baseline: the parent keeps the equipment (and reinvests what it recovers), sells it in the same year for the
same price; the child invests the cash alone. Every dollar earns the same as in the partnership. -/
def baseline (g : Game) (mv : Move) : Out :=
  let c : Contributed := ⟨g.book, g.basis, g.remaining, g.newLife⟩
  let rec go : Nat → Nat → Int → Int → Int × Int
    | 0, _, pt, kt => (pt, kt)
    | k + 1, t, pt, kt =>
      let held := decide (t < mv.saleYear)
      let own := bps (g.book - (if held then fmvAt g t else 0)) g.cashBp + (if held then opInc g t - taxDep c t else 0)
      let saleGain := if t = mv.saleYear then fmvAt g t - taxBasis c t else 0
      let inc := bps g.childCash g.cashBp
      go k (t + 1) (pt + parentTax g (own + saleGain) 0) (kt + childTax g inc 0)
  let (pt, kt) := go g.horizon 0 0 0
  ⟨pt + kt + parentTax g 0 0 + childTax g 0 0, pt + parentTax g 0 0, kt + childTax g 0 0⟩

end Legal.USTax.Entity.Contrib
