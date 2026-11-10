/-!
# The wash-sale rule (§1091), as written

A loss on selling property is deductible (§165). §1091(a) takes it away in one case: a loss on a sale of **stock or
securities** (including contracts or options to acquire them) where, within 30 days before or after the sale, the
taxpayer acquired substantially identical stock or securities. The loss is not lost: §1091(d) adds it to the basis of
the replacement, so it comes back when the replacement is sold.

This file executes a sequence of trades under those rules. Each trade buys or sells one unit of an asset on a day; a
sale disposes of the oldest unit held (first in, first out, the default identification rule). For each sale at a loss
of a stock or security, the executor looks through the whole sequence for an acquisition of a substantially identical
asset within the 61-day window, other than the unit sold and not already used to match another sale, and if it finds
one it disallows the loss and adds it to that unit's basis. Which assets are stock or securities, and which are
substantially identical to which, is data: nothing here mentions any planning technique.
-/

namespace Legal.USTax.WashSale

structure Asset where
  security : Bool  -- stock or securities, §1091(a)
  cls : Nat        -- assets with the same `cls` are substantially identical
  deriving DecidableEq, Repr

structure Trade where
  day : Nat
  asset : Nat
  buy : Bool
  deriving DecidableEq, Repr

structure Lot where
  asset : Nat
  idx : Nat        -- the trade that bought it (or an id for a lot held at the start)
  day : Nat
  basis : Int
  deriving DecidableEq, Repr

structure Book where
  lots : List Lot
  pending : List (Nat × Int)  -- disallowed losses waiting for a replacement still to be bought: (trade, amount)
  used : List Nat             -- replacements already matched to a sale
  recognized : Int            -- gain recognized (negative: deductible loss)
  disallowed : Int            -- losses disallowed so far
  proceeds : Int
  costs : Int
  deriving DecidableEq, Repr

structure Market where
  assets : Nat → Asset
  price : Nat → Nat → Int     -- asset, day

/-! ## Bookkeeping, with the facts the proofs need -/

def sumB : List Lot → Int
  | [] => 0
  | l :: ls => l.basis + sumB ls

def sumP : List (Nat × Int) → Int
  | [] => 0
  | p :: ps => p.2 + sumP ps

/-- Take the oldest unit of an asset. -/
def takeFirst (a : Nat) : List Lot → Option (Lot × List Lot)
  | [] => none
  | l :: ls => if l.asset = a then some (l, ls) else (takeFirst a ls).map fun (x, r) => (x, l :: r)

theorem takeFirst_sum (a : Nat) : ∀ (ls : List Lot) (x : Lot) (r : List Lot), takeFirst a ls = some (x, r) → sumB ls = x.basis + sumB r
  | [], _, _, h => by simp [takeFirst] at h
  | l :: ls, x, r, h => by
    simp only [takeFirst] at h
    split at h
    · simp at h; obtain ⟨rfl, rfl⟩ := h; simp [sumB]
    · cases hq : takeFirst a ls with
      | none => simp [hq] at h
      | some p =>
        simp [hq] at h; obtain ⟨rfl, rfl⟩ := h
        have := takeFirst_sum a ls p.1 p.2 (by rw [hq])
        simp [sumB]; omega

/-- Add `d` to the basis of the held unit bought by trade `j`. -/
def bump (j : Nat) (d : Int) : List Lot → Option (List Lot)
  | [] => none
  | l :: ls => if l.idx = j then some ({ l with basis := l.basis + d } :: ls) else (bump j d ls).map (l :: ·)

theorem bump_sum (j : Nat) (d : Int) : ∀ (ls r : List Lot), bump j d ls = some r → sumB r = sumB ls + d
  | [], _, h => by simp [bump] at h
  | l :: ls, r, h => by
    simp only [bump] at h
    split at h
    · simp at h; subst h; simp [sumB]; omega
    · cases hq : bump j d ls with
      | none => simp [hq] at h
      | some p => simp [hq] at h; subst h; have := bump_sum j d ls p hq; simp [sumB]; omega

/-- Collect the disallowed losses waiting for trade `i`. -/
def takePending (i : Nat) : List (Nat × Int) → Int × List (Nat × Int)
  | [] => (0, [])
  | p :: ps => let (t, r) := takePending i ps; if p.1 = i then (p.2 + t, r) else (t, p :: r)

theorem takePending_sum (i : Nat) : ∀ ps : List (Nat × Int), sumP ps = (takePending i ps).1 + sumP (takePending i ps).2
  | [] => by simp [takePending, sumP]
  | p :: ps => by
    have := takePending_sum i ps
    simp only [takePending]; split <;> simp [sumP] <;> omega

def heldIdx (ls : List Lot) (j : Nat) : Bool := ls.any (·.idx = j)

/-- §1091(a): a replacement for a sale on day `d` of a unit bought by trade `own`: an acquisition of a substantially
identical asset within 30 days either side, not the unit sold, not already used, and (if already bought) still held. -/
def replacement (M : Market) (plan : List (Nat × Trade)) (b : Book) (i : Nat) (cls d own : Nat) : Option Nat :=
  (plan.find? fun (j, t) => t.buy && (M.assets t.asset).cls == cls && t.day + 30 ≥ d && d + 30 ≥ t.day && j != own &&
    !b.used.contains j && (decide (j > i) || heldIdx b.lots j)).map (·.1)

/-- One trade. -/
def step (M : Market) (plan : List (Nat × Trade)) (b : Book) : Nat × Trade → Option Book
  | (i, t) =>
    let p := M.price t.asset t.day
    if t.buy then
      let (adj, rest) := takePending i b.pending
      some { b with lots := b.lots ++ [⟨t.asset, i, t.day, p + adj⟩], pending := rest, costs := b.costs + p }
    else
      match takeFirst t.asset b.lots with
      | none => none
      | some (lot, others) =>
        let g := p - lot.basis
        let b' := { b with lots := others, proceeds := b.proceeds + p }
        let plain := some { b' with recognized := b.recognized + g }
        if g < 0 && (M.assets t.asset).security then
          match replacement M plan b i (M.assets t.asset).cls t.day lot.idx with
          | none => plain
          | some j =>
            if j > i then
              some { b' with pending := (j, -g) :: b.pending, used := j :: b.used, disallowed := b.disallowed - g }
            else match bump j (-g) others with
              | none => plain
              | some ls => some { b' with lots := ls, used := j :: b.used, disallowed := b.disallowed - g }
        else plain

def runFrom (M : Market) (plan : List (Nat × Trade)) : List (Nat × Trade) → Book → Option Book
  | [], b => some b
  | x :: xs, b => (step M plan b x).bind (runFrom M plan xs)

/-- Execute a plan, numbering its trades. -/
def execute (M : Market) (trades : List Trade) (b0 : Book) : Option Book :=
  let plan := (List.range trades.length).zip trades
  runFrom M plan plan b0

end Legal.USTax.WashSale
