/-!
# Partnerships (subchapter K): the rules that move basis, gain and character between partners

Each rule is written from the text of the Code (OLRC release point 119-138) and, where the Code delegates, from the
Treasury regulation that carries it out. Amounts are whole dollars (`Int`); shares are basis points of 10,000.
Tests against the regulations' own examples are in `Entity/Tests.lean`.

What is here:
* §704(c)(1)(A) and Reg. §1.704-3: one contributed property with a built-in gain, depreciated straight line, under the
  traditional method (with the ceiling rule, §1.704-3(b)(1)), the traditional method with curative allocations
  (§1.704-3(c)) and the remedial method (§1.704-3(d)); and the allocation of gain or loss when the partnership sells it.
* §705 / §722 / §733 outside basis; §731(a) gain on a distribution of money; §732(a), (b) basis of distributed
  property; §752(a), (b) liabilities as money.
* §704(c)(1)(B) (contributed property distributed to another partner within 7 years) and §737 (property distributed
  to the contributing partner within 7 years).
* §743(b) with Reg. §1.743-1(d): the transferee's basis adjustment when a §754 election is in effect.
* §751(a) on the sale of an interest: the ordinary part.
* §1061(a): gain on an applicable partnership interest held 3 years or less is short-term.

Not modelled: §704(b) substantial economic effect testing (allocations here follow the partners' shares or §704(c)),
§704(c)(1)(C) built-in losses, §707(a)(2)(B) disguised sales (a two-year presumption in Reg. §1.707-3(c); recorded as a
fact in the drivers, not computed), §734(b), §755 allocation among several assets, and §1245 recapture shares among
partners (the contribution game below treats all gain on the equipment as ordinary, which is the §1245 result when it
sells for no more than its original cost).
-/

namespace Legal.USTax.Entity

/-- `x` times `r` basis points, rounded toward zero (amounts here are non-negative where it matters). -/
def bps (x r : Int) : Int := x * r / 10000

/-! ## §704(c): one contributed property -/

inductive Method where
  | traditional   -- Reg. §1.704-3(b)
  | curative      -- Reg. §1.704-3(c): the traditional method with reasonable curative allocations of other income
  | remedial      -- Reg. §1.704-3(d)
  deriving Repr, DecidableEq, Inhabited

/-- A property contributed with a built-in gain: book value (its fair market value at contribution, Reg.
§1.704-1(b)(2)(iv)(d)(1)), its adjusted tax basis, the years left on its tax recovery schedule (straight line), and
the recovery period a newly purchased property of its kind would have (used for the remedial method's excess,
Reg. §1.704-3(d)(2)). -/
structure Contributed where
  book : Int
  basis : Int
  remaining : Nat
  newLife : Nat
  deriving Repr, Inhabited, DecidableEq

/-- Tax depreciation in year `t` (0-based): the basis over the years left, straight line. -/
def taxDep (c : Contributed) (t : Nat) : Int :=
  if t < c.remaining then c.basis / c.remaining else 0

/-- Book depreciation in year `t`. Traditional and curative: book value recovered at the rate the tax basis is
(Reg. §1.704-1(b)(2)(iv)(g)(3)), i.e. over the same remaining years. Remedial (Reg. §1.704-3(d)(2)): the part of book
value equal to the tax basis over the remaining years, and the excess over a new recovery period starting now. -/
def bookDep (m : Method) (c : Contributed) (t : Nat) : Int :=
  match m with
  | .remedial =>
    (if t < c.remaining then c.basis / c.remaining else 0) +
      (if t < c.newLife then (c.book - c.basis) / c.newLife else 0)
  | _ => if t < c.remaining then c.book / c.remaining else 0

def sumTo (f : Nat → Int) : Nat → Int
  | 0 => 0
  | n + 1 => sumTo f n + f n

/-- Book value and tax basis at the start of year `t` (after `t` years of recovery). -/
def bookValue (m : Method) (c : Contributed) (t : Nat) : Int := c.book - sumTo (bookDep m c) t
def taxBasis (c : Contributed) (t : Nat) : Int := c.basis - sumTo (taxDep c) t

/-- One year's tax and book allocations to the contributing partner `C` and the other partner `N`, as income
(a deduction is negative). -/
structure Alloc where
  cTax : Int
  nTax : Int
  cBook : Int
  nBook : Int
  deriving Repr, Inhabited, DecidableEq

/-- Correcting a ceiling-rule distortion. `over` is how much more income (or less deduction) the tax items give the
non-contributing partner than its book items do. Traditional: nothing (§1.704-3(b)(1), the ceiling rule).
Curative: other income of the same character is shifted from N to C, but no more than N's share of it and no more than
`over` (§1.704-3(c)(3)(i), (ii)). Remedial: a remedial item for N equal to `over` and an offsetting one for C
(§1.704-3(d)(1), (3)). Returns the amount moved from N to C. -/
def cure (m : Method) (over nOther : Int) : Int :=
  match m with
  | .traditional => 0
  | .curative => max 0 (min over nOther)
  | .remedial => over

/-- Year `t` with the contributing partner's share `sC` (basis points) of all items, and `other` ordinary income from
the partnership's other operations (shared the same way). -/
def yearAlloc (m : Method) (c : Contributed) (sC : Int) (other : Int) (t : Nat) : Alloc :=
  let bd := bookDep m c t
  let td := taxDep c t
  let nB := bd - bps bd sC                 -- N's book depreciation
  let nT := min nB td                      -- ceiling rule: no more tax depreciation than there is
  let cT := td - nT
  let cO := bps other sC
  let nO := other - cO
  let over := nB - nT
  let k := cure m over nO
  ⟨cO - cT + k, nO - nT - k, cO - (bd - nB), nO - nB⟩

/-- The allocation of a sale at the start of year `t` for `price`: book gain is shared by the partners' shares; tax
gain follows it for N as far as the tax gain allows, and the contributor takes the rest, which is §704(c)(1)(A)'s
built-in gain first (Reg. §1.704-3(b)(1)). `other` is the partnership's other income that year (for curative
allocations). -/
def saleAlloc (m : Method) (c : Contributed) (sC : Int) (other : Int) (t : Nat) (price : Int) : Alloc :=
  let bg := price - bookValue m c t
  let tg := price - taxBasis c t
  let nB := bg - bps bg sC
  let nT := if 0 ≤ nB then (if 0 ≤ tg then min nB tg else 0) else (if tg ≤ 0 then max nB tg else 0)
  let over := nT - nB
  let cO := bps other sC
  let nO := other - cO
  let k := cure m (max 0 over) nO + (if m = .remedial ∧ over < 0 then over else 0)
  ⟨tg - nT + cO + k, nT + nO - k, bg - nB + cO, nB + nO⟩

/-! ## Outside basis, distributions and liabilities -/

/-- §731(a)(1): gain on a distribution to the extent money (including a §752(b) decrease in liabilities) exceeds the
partner's basis immediately before. -/
def gain731 (outside money : Int) : Int := max 0 (money - outside)

/-- §732(a): a non-liquidating distribution of property takes the partnership's basis, limited to the partner's
basis less money distributed in the same transaction. §732(b): in liquidation, the partner's basis less money. -/
def basis732 (liquidating : Bool) (outside money partnershipBasis : Int) : Int :=
  let room := max 0 (outside - money)
  if liquidating then room else min partnershipBasis room

/-- §733: the partner's basis after a non-liquidating distribution. -/
def basis733 (outside money propertyBasis : Int) : Int := max 0 (outside - money - propertyBasis)

/-- §704(c)(1)(B)(i): contributed property distributed to another partner within 7 years: the contributor recognizes
the gain the property's remaining built-in gain would have given on a sale at fair market value (the §704(c) part
only, i.e. the excess of book value over tax basis, limited by the actual tax gain at that value). -/
def gain704c1B (yearsSinceContribution : Nat) (fmv bookValue taxBasis : Int) : Int :=
  if yearsSinceContribution < 7 then max 0 (min (bookValue - taxBasis) (fmv - taxBasis)) else 0

/-- §737(a): the lesser of (1) the excess of the fair market value of property received (other than money) over the
partner's basis before the distribution less money received, and (2) the partner's net precontribution gain, which
(§737(b)) is the §704(c)(1)(B) gain on property the partner contributed within 7 years and the partnership still
holds. -/
def gain737 (yearsSinceContribution : Nat) (fmvReceived outside money netPrecontribution : Int) : Int :=
  if yearsSinceContribution < 7 then max 0 (min (fmvReceived - max 0 (outside - money)) netPrecontribution) else 0

/-! ## §743(b) and §751(a) -/

/-- Reg. §1.743-1(d): with a §754 election, the transferee's basis adjustment is its basis in the interest less its
share of the partnership's basis, which is its previously taxed capital plus its liability share. Previously taxed
capital is the cash it would get on liquidation after a hypothetical sale of everything at fair market value, less
its share of the tax gain (plus its share of tax loss) from that sale. The share is `num / den`. -/
def adj743 (purchasePrice liabilities num den totalFmv totalBasis : Int) : Int :=
  let sh (x : Int) := x * num / den
  let liab := sh liabilities
  let outside := purchasePrice + liab                       -- §742 cost + §752(d)
  let liquidation := sh (totalFmv - liabilities)
  let ptc := liquidation - sh (totalFmv - totalBasis)
  outside - (ptc + liab)

/-- §751(a): on the sale of an interest, the amount attributable to unrealized receivables and inventory is ordinary;
Reg. §1.751-1(a)(2): it is the ordinary income the partner would be allocated on a sale of those assets at fair
market value. Returns (ordinary, capital) given the partner's total gain and its share of hot-asset gain. -/
def split751 (totalGain hotGainShare : Int) : Int × Int := (hotGainShare, totalGain - hotGainShare)

/-- §1061(a): long-term gain on an applicable partnership interest becomes short-term unless held more than 3 years.
Returns (short-term, long-term). -/
def split1061 (heldYears : Nat) (gain : Int) : Int × Int := if heldYears > 3 then (0, gain) else (gain, 0)

end Legal.USTax.Entity
