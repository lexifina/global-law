import Std

/-!
# Partnerships and their partners: what subchapter K permits and what it taxes

Part 1 (`Rules`) writes down, provision by provision, what a partner and a partnership may do with property, money,
debt and interests, and the tax effect of each act. Nothing in Part 1 names a planning technique. Part 2 (`Search`)
runs a blind breadth-first search over every allowed sequence of acts and compares the tax bill with a plain sale.

Text used: OLRC release point through Pub. L. 119-138 (`tools/hunt/sec.py`). Dollar figures are in thousands;
the only statutory dollar figure used is the $250,000 of §§734(d) and 743(d), which is not indexed.

Simplifications, each stated once here:
* fair market values do not change (so every built-in gain or loss is a §704(c) amount of the contributor, or is
  the result of a basis adjustment); no depreciation, no operating income;
* a partner's interest is worth his book capital (contributed value less distributed value); gain or loss not
  governed by §704(c) is shared in proportion to book capital (§704(b): partner's interest in the partnership);
* liabilities: a borrowing is borne by one named partner (§752(a), assumption/guarantee). How a nonrecourse liability
  is shared is in the regulations and is left out;
* §704(c)(1)(A) is applied by the traditional method (the contributor takes the built-in amount first);
* §707(a)(2)(B) is read conservatively with the two-year presumption of Reg. §1.707-3(c): money distributed to a
  partner within two years of his contributing property is a sale of that property; a distribution of *other*
  property inside the same two years is not offered as a move at all. The debt-financed exception of
  Reg. §1.707-5(b) is a switch (`debtFin`), off unless stated;
* §751(b) is applied by the "hypothetical sale" method: a partner whose share of the gain in substantially
  appreciated inventory falls in a distribution has ordinary income equal to the fall; whoever takes the share over
  has a cost basis in it and gain on what he gave for it (taken in full, the conservative figure);
* §704(c)(1)(B) losses: §707(b)(1) is applied to the deemed sale to the distributee (T.D. 8642), with §267(c)
  family attribution; §267(a)(1) on a sale of an interest between related persons;
* a disguised sale of part of a property is taxed in proportion to the whole property each time (two part-sales
  of one property recognise slightly less than the whole gain; the remainder is still taxed under §731);
* §732(d), §736(a), §708(b)(2), §724, §735, §1061, §707(c), §1402(a)(13), §199A, §163(j)(4), §461(l), §7704 and
  the audit regime (§6221 ff.) were read but are not in the search: they change character, timing or procedure,
  not the amounts tracked here. Death of a partner (§1014, §743(b)) is not a move.

The search conserves gain: in none of the positions run does any plan lower the tax due once everything is sold
and the partnership wound up. Every plan it finds defers gain, moves it to another asset or person, or brings a
loss forward.
-/

namespace Legal.USTax.Hunt.Partnership

/-! ## Part 1. Rules -/

inductive Kind where
  | capital     -- capital asset or §1231(b) property, not actively traded
  | security    -- marketable security, §731(c)(2)
  | inventory   -- inventory item, §751(d)
  deriving BEq, Hashable, Repr, DecidableEq, Inhabited

inductive Holder where
  | person (p : Nat)
  | pship
  | sold
  deriving BEq, Hashable, Repr, DecidableEq, Inhabited

structure Asset where
  id : Nat
  kind : Kind
  fmv : Int
  basis : Int               -- adjusted basis to whoever holds it (common basis if the partnership)
  holder : Holder
  contrib : Option Nat      -- the partner who contributed it (§§731(c)(3)(A)(i), 737(d)(1), 751(b)(2)(A))
  succ : Option Nat         -- that partner or his successor in interest (§704(c)(3))
  yr : Nat                  -- year of contribution
  big : Int                 -- §704(c) built-in gain (+) or loss (−) not yet recognised
  adj : Array Int           -- §743(b) adjustment for each person (transferee only)
  deriving BEq, Hashable, Repr, Inhabited

structure Person where
  cash : Int
  outside : Int             -- adjusted basis of the partnership interest, §705
  cap : Int                 -- book capital = value of the interest net of liabilities
  liab : Int                -- share of partnership liabilities, §752
  capGain : Int             -- capital gain (loss negative) recognised so far
  ordInc : Int              -- ordinary income recognised so far
  susp : Int                -- loss suspended by §704(d)
  cashYr : Option Nat       -- year of the last contribution of money
  propYr : Option Nat       -- year of the last contribution of property
  nonInv : Bool             -- has contributed something other than §731(c)(3)(C)(i) assets
  deriving BEq, Hashable, Repr, Inhabited

structure State where
  year : Nat
  pcash : Int
  elect : Bool              -- §754 election in effect
  everNonInv : Bool         -- partnership has held assets outside §731(c)(3)(C)(i)
  carry : Int               -- §755(b) last sentence: adjustment waiting for property of like character
  assets : Array Asset
  persons : Array Person
  deriving BEq, Hashable, Repr, Inhabited

structure Cfg where
  unit : Int                -- the natural amount for cash moves (value of the appreciated property)
  debtFin : Bool            -- Reg. §1.707-5(b) debt-financed distribution exception on/off
  related : Nat → Nat → Bool
  fam : Nat → Bool := fun p => p < 2   -- the related group whose tax is being minimised

inductive Move where
  | contribute (p a : Nat)            -- §721, §722, §723
  | contribCash (p : Nat) (amt : Int) -- §721, §722
  | borrow (g : Nat) (amt : Int)      -- §752(a)
  | repay (g : Nat)                   -- §752(b)
  | dist (p : Nat) (a : Option Nat) (cash : Int)  -- §§731–737, 751(b), 704(c)(1)(B), 707(a)(2)(B)
  | sellInt (p q : Nat)               -- §§741, 742, 743, 751(a), 752(d)
  | pSell (a : Nat)                   -- partnership sells an asset: §§702, 704, 705
  | ownSell (a : Nat)                 -- a person sells an asset he holds: §1001
  | buy (amt : Int)                   -- partnership buys a capital asset for cash: §1012
  | elect                             -- §754
  | wait (toYear : Nat)               -- let a clock run (2 years, 7 years)
  deriving BEq, Repr

def modP (s : State) (i : Nat) (f : Person → Person) : State := { s with persons := s.persons.modify i f }
def modA (s : State) (i : Nat) (f : Asset → Asset) : State := { s with assets := s.assets.modify i f }

/-- Record recognised gain or loss with its character: ordinary for inventory items (§§702(b), 751), capital
otherwise (§§731(a), 741, 1221). -/
def recG (k : Kind) (g : Int) (p : Person) : Person :=
  if k == .inventory then { p with ordInc := p.ordInc + g } else { p with capGain := p.capGain + g }

/-- Split `amt` in proportion to `w`, the rounding remainder going to the last positive weight. -/
def spread (w : Array Int) (amt : Int) : Array Int := Id.run do
  let tot := w.foldl (· + ·) 0
  let mut out := Array.replicate w.size (0 : Int)
  if tot ≤ 0 then return out
  let mut left := amt
  let mut last := 0
  for i in [0:w.size] do
    if w[i]! > 0 then
      let x := amt * w[i]! / tot
      out := out.set! i x
      left := left - x
      last := i
  return out.modify last (· + left)

def caps (s : State) : Array Int := s.persons.map (fun p => if p.cap > 0 then p.cap else 0)

/-- How the gain or loss on a sale of a partnership asset at value is shared. §704(c)(1)(A): the contributor (or
successor, §704(c)(3)) takes the built-in gain first. §704(c)(1)(C): a built-in loss is taken into account only for
the contributor; for the others the basis is the value at contribution. The rest follows book capital (§704(b)).
Each partner's §743(b) adjustment then reduces (or increases) his own share. -/
def allocSale (s : State) (a : Asset) : Array Int := Id.run do
  let g := a.fmv - a.basis
  let (who, first) : Option Nat × Int :=
    match a.succ with
    | some q =>
      if a.big > 0 ∧ g > 0 then (some q, min a.big g)
      else if a.big < 0 then (some q, a.big)
      else (none, 0)
    | none => (none, 0)
  let mut out := spread (caps s) (g - first)
  if let some q := who then out := out.modify q (· + first)
  for i in [0:out.size] do
    out := out.modify i (· - a.adj[i]!)
  return out

/-- A partner's distributive share of a partnership gain or loss: basis up for gain (§705(a)(1)); loss allowed only
up to the basis of the interest (§704(d)(1)), the excess suspended (§704(d)(2)). -/
def takeShare (k : Kind) (g : Int) (p : Person) : Person :=
  if g ≥ 0 then recG k g { p with outside := p.outside + g }
  else
    let allowed := min (-g) (max 0 p.outside)
    recG k (-allowed) { p with outside := p.outside - allowed, susp := p.susp + (-g - allowed) }

def zeroAdj (n : Nat) : Array Int := Array.replicate n 0

/-- §351(e)(1), applied by §721(b): would the partnership, counting the new asset, be an investment company —
more than 80 percent of its assets money, stock or securities (Reg. §1.351-1(c)(1)(ii)) — and are there other
contributors (the regulation's "diversification")? Conservative: any other partner counts. -/
def investmentCo (s : State) (p : Nat) (a : Asset) : Bool := Id.run do
  let mut sec := s.pcash + (if a.kind == .security then a.fmv else 0)
  let mut tot := s.pcash + a.fmv
  for b in s.assets do
    if b.holder == .pship then
      tot := tot + b.fmv
      if b.kind == .security then sec := sec + b.fmv
  let others := (List.range s.persons.size).any (fun i => i != p ∧ s.persons[i]!.cap > 0)
  return others ∧ sec * 100 > tot * 80

/-- §721(a): no gain or loss on a contribution of property for an interest. §721(b): gain (not loss) is recognised
if the partnership would be an investment company. §722, §723: bases carry over, increased by that gain.
§704(c)(1)(A): the difference between value and basis is the contributor's. -/
def contribute (s : State) (p i : Nat) : Option State := do
  let a ← s.assets[i]?
  guard (a.holder == .person p)
  let g := a.fmv - a.basis
  let rec721b := if g > 0 ∧ investmentCo s p a then g else 0
  let nb := a.basis + rec721b
  let s := modP s p (fun P => recG a.kind rec721b
    { P with outside := P.outside + nb, cap := P.cap + a.fmv, nonInv := P.nonInv || a.kind != .security,
             propYr := some s.year })
  let s := modA s i (fun a => { a with basis := nb, holder := .pship, contrib := some p, succ := some p,
                                         yr := s.year, big := a.fmv - nb, adj := zeroAdj s.persons.size })
  pure { s with everNonInv := s.everNonInv || a.kind != .security }

/-- §721(a), §722: money contributed is basis. -/
def contribCash (s : State) (p : Nat) (amt : Int) : Option State := do
  let P ← s.persons[p]?
  guard (amt > 0 ∧ amt ≤ P.cash)
  let s := modP s p (fun P => { P with cash := P.cash - amt, outside := P.outside + amt, cap := P.cap + amt,
                                       cashYr := some s.year })
  pure { s with pcash := s.pcash + amt }

def totalDebt (s : State) : Int := s.persons.foldl (fun acc p => acc + p.liab) 0
def totalAssets (s : State) : Int :=
  s.assets.foldl (fun acc a => if a.holder == .pship then acc + a.fmv else acc) s.pcash

/-- §752(a): a partner's increased share of partnership liabilities is a contribution of money by him (§722:
basis). The partnership borrows from a lender; partner `g` bears the liability. -/
def borrow (s : State) (g : Nat) (amt : Int) : Option State := do
  let G ← s.persons[g]?
  guard (G.cap > 0 ∧ amt > 0 ∧ totalDebt s + amt ≤ totalAssets s)
  let s := modP s g (fun P => { P with liab := P.liab + amt, outside := P.outside + amt })
  pure { s with pcash := s.pcash + amt }

/-- §752(b): a decrease in a partner's share of liabilities is a distribution of money to him; §733 basis down;
§731(a)(1) gain if the money exceeds basis. -/
def relieve (amt : Int) (P : Person) : Person :=
  let gain := max 0 (amt - P.outside)
  { P with liab := P.liab - amt, outside := max 0 (P.outside - amt), capGain := P.capGain + gain }

def repay (s : State) (g : Nat) : Option State := do
  let G ← s.persons[g]?
  let amt := min s.pcash G.liab
  guard (amt > 0)
  let s := modP s g (relieve amt)
  pure { s with pcash := s.pcash - amt }

/-- §755: allocate a §734(b) adjustment among remaining partnership property of like character (§755(b)):
an increase first to appreciated property in proportion to appreciation, then by value; a decrease first to
depreciated property in proportion to depreciation, then by basis, never below zero; what cannot be placed waits
(§755(b), last sentence). -/
def adjust734 (s : State) (delta : Int) (inv : Bool) : State := Id.run do
  if delta == 0 then return s
  let ok (a : Asset) : Bool := a.holder == .pship ∧ (a.kind == .inventory) == inv
  if !(s.assets.any ok) then return { s with carry := s.carry + delta }
  let mut s := s
  if delta > 0 then
    let app := s.assets.map (fun a => if ok a then max 0 (a.fmv - a.basis) else 0)
    let totApp := app.foldl (· + ·) 0
    let d1 := min delta totApp
    let x1 := spread app d1
    let x2 := spread (s.assets.map (fun a => if ok a then a.fmv else 0)) (delta - d1)
    for i in [0:s.assets.size] do
      s := modA s i (fun a => { a with basis := a.basis + x1[i]! + x2[i]! })
    return s
  else
    let m := -delta
    let dep := s.assets.map (fun a => if ok a then max 0 (a.basis - a.fmv) else 0)
    let totDep := dep.foldl (· + ·) 0
    let d1 := min m totDep
    let x1 := spread dep d1
    for i in [0:s.assets.size] do
      s := modA s i (fun a => { a with basis := a.basis - x1[i]! })
    let bases := s.assets.map (fun a => if ok a then a.basis else 0)
    let totB := bases.foldl (· + ·) 0
    let d2 := min (m - d1) totB
    let x2 := spread bases d2
    for i in [0:s.assets.size] do
      s := modA s i (fun a => { a with basis := a.basis - x2[i]! })
    return { s with carry := s.carry - (m - d1 - d2) }

/-- Each partner's share of the gain in substantially appreciated inventory (§751(b)(1)(A)(ii), (b)(3): value
over 120 percent of basis, taken in aggregate), counting inventory he holds directly after a distribution. -/
def hotShares (s : State) (extra : Option (Nat × Int)) : Array Int := Id.run do
  let mut out := Array.replicate s.persons.size (0 : Int)
  let mut f : Int := 0
  let mut b : Int := 0
  for a in s.assets do
    if a.holder == .pship ∧ a.kind == .inventory then
      f := f + a.fmv; b := b + a.basis
  if f * 100 > b * 120 then
    for a in s.assets do
      if a.holder == .pship ∧ a.kind == .inventory then
        let al := allocSale s a
        for i in [0:out.size] do out := out.modify i (· + al[i]!)
  if let some (p, g) := extra then out := out.modify p (· + g)
  return out

/-- A distribution of one asset and/or money to partner `p`. In liquidation of his interest if it is the whole
value of the interest. Applied in this order:
1. §707(a)(2)(B) (with Reg. §1.707-3(c)): money within two years of his contribution of property is a sale of it.
2. §704(c)(1)(B): property contributed by another partner, distributed within 7 years: that partner recognises the
   built-in gain or loss; his interest basis and the property basis are adjusted.
3. §737: the distributee recognises the lesser of (value of property received − (interest basis − money)) and his
   net precontribution gain on property he contributed within 7 years; §737(c) basis adjustments; §737(d)(1)
   excludes his own contributed property. §731(c)(1): marketable securities are money for this.
4. §731(c): marketable securities are money at value, unless §731(c)(3)(A)(i) (he contributed them) or (iii)
   (investment partnership, eligible partner); reduced by §731(c)(3)(B) (his share of the gain in them).
5. §731(a)(1): gain to the extent money exceeds interest basis. §731(a)(2): loss only in liquidation and only if
   nothing but money and inventory/receivables is received.
6. §732(a)(1),(2): carryover basis limited to interest basis less money; §732(b): in liquidation, interest basis
   less money; §732(c)(1)(A): inventory never above the partnership's basis. §731(c)(4): plus §731(c) gain.
7. §733: interest basis down.
8. §734(b), if §754 election or (§734(d)) a basis reduction over $250,000: common basis of what remains goes up by
   §731(a)(1) gain and by basis lost under §732(a)(2)/(b), down by §731(a)(2) loss and by basis gained under
   §732(b); §731(c)(5): §731(c) gain ignored here.
9. §751(b): see `hotShares`; §751(b)(2)(A) excludes property the distributee contributed. -/
def distribute (cfg : Cfg) (s0 : State) (p : Nat) (ai : Option Nat) (cash : Int) : Option State := do
  let P0 ← s0.persons[p]?
  guard (P0.cap > 0 ∧ cash ≥ 0 ∧ cash ≤ s0.pcash)
  let a0? : Option Asset ← match ai with
    | none => pure none
    | some i => (s0.assets[i]?).map some
  if let some a := a0? then guard (a.holder == .pship)
  let fmvA : Int := match a0? with | some a => a.fmv | none => 0
  let total := fmvA + cash
  guard (total > 0 ∧ total ≤ P0.cap)
  let liq := total == P0.cap
  guard (!(liq ∧ P0.liab > 0))
  let own := match a0? with | some a => a.contrib == some p | none => false
  let recentProp := s0.assets.any (fun b => b.holder == .pship ∧ b.contrib == some p ∧ s0.year < b.yr + 2)
  let recentCash := match P0.cashYr with | some y => s0.year < y + 2 | none => false
  let recentAny := match P0.propYr with | some y => s0.year < y + 2 | none => false
  guard (!(a0?.isSome && !own && (recentAny || recentCash)))
  let mut s := s0
  -- 1. §707(a)(2)(B)
  if cash > 0 ∧ recentProp then
    let t := cash - (if cfg.debtFin then min cash P0.liab else 0)
    if t > 0 then
      for j in [0:s.assets.size] do
        let z := s.assets[j]!
        if z.holder == .pship ∧ z.contrib == some p ∧ s.year < z.yr + 2 ∧ z.fmv > 0 then
          let t' := min t z.fmv
          let gain := t' * (z.fmv - z.basis) / z.fmv
          -- §707(b)(1)(A), (b)(3): a loss on a sale to the partnership is not allowed to a person who owns,
          -- directly or through family (§267(c)), more than half of it
          let tot := (caps s).foldl (· + ·) 0
          let mine := (List.range s.persons.size).foldl (fun acc i =>
            if i == p ∨ cfg.related p i then acc + s.persons[i]!.cap else acc) (0 : Int)
          let allowed := gain > 0 ∨ mine * 2 ≤ tot
          if gain != 0 then
            s := modP s p (fun P => (if allowed then recG z.kind gain else id)
              { P with outside := max 0 (P.outside + gain) })
            s := modA s j (fun z => { z with basis := z.basis + gain, big := z.big - gain })
          break
  -- 2. §704(c)(1)(B)
  if let some i := ai then
    let a := s.assets[i]!
    if let some q := a.succ then
      if q != p ∧ s.year < a.yr + 7 ∧ a.big != 0 then
        -- the amount he would have been allocated on a sale, so net of his own §743(b) adjustment
        let amt := a.big - a.adj[q]!
        -- §704(c)(1)(B)(ii) treats it as a sale by the partnership to the distributee, so §707(b)(1)(A), (b)(3)
        -- denies a loss when the distributee owns, directly or through family, more than half (T.D. 8642)
        let tot := (caps s).foldl (· + ·) 0
        let his := (List.range s.persons.size).foldl (fun acc i =>
          if i == p ∨ cfg.related p i then acc + s.persons[i]!.cap else acc) (0 : Int)
        let allowed := amt > 0 ∨ his * 2 ≤ tot
        s := modP s q (fun Q => (if allowed then recG a.kind amt else id) { Q with outside := max 0 (Q.outside + amt) })
        s := modA s i (fun a => { a with basis := a.basis + a.big, big := 0, adj := a.adj.set! q 0 })
  let hotBefore := hotShares s none
  let a? : Option Asset := ai.map (fun i => s.assets[i]!)
  -- 4 (computed early because §737 uses it). §731(c)
  let secMoney : Int := match a? with
    | some a =>
      if a.kind == .security ∧ !own ∧ !(!s.everNonInv ∧ !P0.nonInv) then
        a.fmv - max 0 (min a.fmv ((allocSale s a)[p]!))
      else 0
    | none => 0
  let isMoneyAsset := match a? with
    | some a => a.kind == .security ∧ !own ∧ !(!s.everNonInv ∧ !P0.nonInv)
    | none => false
  -- 3. §737
  let net737 : Int := max 0 (s.assets.foldl (fun (acc : Int) b =>
    if b.holder == .pship ∧ b.succ == some p ∧ s.year < b.yr + 7 ∧ some b.id != ai then acc + b.big - b.adj[p]! else acc) 0)
  let propFmv : Int := if a?.isSome ∧ !own ∧ !isMoneyAsset then fmvA else 0
  let out0 := s.persons[p]!.outside
  let g737 := min net737 (max 0 (propFmv - max 0 (out0 - cash - secMoney)))
  if g737 > 0 then
    let mut left := g737
    for j in [0:s.assets.size] do
      let b := s.assets[j]!
      if left > 0 ∧ b.holder == .pship ∧ b.succ == some p ∧ s.year < b.yr + 7 ∧ some b.id != ai ∧ b.big - b.adj[p]! > 0 then
        let x := min left (b.big - b.adj[p]!)
        s := modP s p (fun P => recG b.kind x { P with outside := P.outside + x })
        s := modA s j (fun b => { b with basis := b.basis + x, big := b.big - x })
        left := left - x
  -- 5. §731(a)
  let out1 := s.persons[p]!.outside
  let gCash := max 0 (cash - out1)
  let gAll := max 0 (cash + secMoney - out1)
  let gSec := gAll - gCash
  let afterMoney := max 0 (out1 - cash)
  -- 6. §732
  let (b732, inside, loss) : Int × Int × Int := match a? with
    | some a =>
      let inside := a.basis + a.adj[p]!
      if liq then
        if a.kind == .inventory then (min inside afterMoney, inside, max 0 (afterMoney - inside))
        else (afterMoney, inside, 0)
      else (min inside afterMoney, inside, 0)
    | none => (0, 0, if liq then max 0 (out1 - cash) else 0)
  s := modP s p (fun P => { P with capGain := P.capGain + gAll - loss,
                                   outside := if liq then 0 else max 0 (afterMoney - b732),   -- §733
                                   cap := P.cap - total, cash := P.cash + cash })
  s := { s with pcash := s.pcash - cash }
  if let some i := ai then
    s := modA s i (fun a => { a with basis := b732 + gSec, holder := .person p, contrib := none, succ := none,
                                     big := 0, adj := zeroAdj s.persons.size })
  -- 8. §734(b)
  let up := gCash + (if a?.isSome ∧ b732 < inside then inside - b732 else 0)
  let down := loss + (if a?.isSome ∧ liq ∧ b732 > inside then b732 - inside else 0)
  if s.elect ∨ down > 250 then
    let inv := match a? with | some a => a.kind == .inventory | none => false
    s := adjust734 s (up - down) inv
  -- a partner who has left: his §704(c)(1)(C) built-in loss is no longer anyone's (the others' basis is the value
  -- at contribution); his built-in gain is shared by those who remain
  if liq then
    for j in [0:s.assets.size] do
      let b := s.assets[j]!
      if b.holder == .pship ∧ b.succ == some p then
        let cut := if b.big < 0 then min (-b.big) (max 0 (b.basis - b.fmv)) else 0
        s := modA s j (fun b => { b with succ := none, basis := b.basis - cut, big := 0 })
      s := modA s j (fun b => { b with adj := b.adj.set! p 0 })
  -- 9. §751(b)
  if !own then
    let recvHot : Option (Nat × Int) := match ai with
      | some i => let a := s.assets[i]!
                  if a.kind == .inventory then some (p, a.fmv - a.basis) else none
      | none => none
    let hotAfter := hotShares s recvHot
    for j in [0:s.persons.size] do
      let d := hotBefore[j]! - hotAfter[j]!
      if hotBefore[j]! > 0 ∧ d > 0 then
        s := modP s j (fun Q => { Q with ordInc := Q.ordInc + d, capGain := Q.capGain - (if j == p ∧ liq ∧ ai.isNone then d else 0),
                                         outside := if Q.cap > 0 then Q.outside + d else Q.outside })
        -- the purchaser of the hot share takes a cost basis in it
        if j == p then
          s := adjust734 s d true
          -- if they paid with appreciated property rather than money, they sold that much of it: gain to those
          -- who remain, and a cost basis for the distributee in that part
          if let some i := ai then
            let a := s.assets[i]!
            if a.kind != .inventory ∧ a.fmv > 0 ∧ inside < a.fmv then
              let g := d * (a.fmv - inside) / a.fmv
              let sh := spread (caps s) g
              for k in [0:s.persons.size] do
                if sh[k]! != 0 then
                  s := modP s k (fun Q => { Q with capGain := Q.capGain + sh[k]!, outside := Q.outside + sh[k]! })
              if !liq then s := modA s i (fun a => { a with basis := a.basis + g })
          -- in liquidation his ordinary income is basis in his interest, and so in the property he takes
          if liq then
            if let some i := ai then s := modA s i (fun a => { a with basis := a.basis + d })
        else if let some i := ai then
          if s.assets[i]!.kind == .inventory then
            -- the distributee bought that share with his interest in other property: gain on what he gave up
            -- (taken in full, the conservative figure) and a cost basis in the share
            s := modA s i (fun a => { a with basis := a.basis + d })
            s := modP s p (fun P => { P with capGain := P.capGain + d })
  pure s

/-- Make a list of bases add up to `target`: §732(c)(2) for an increase (first to appreciated property in
proportion to appreciation, then by value), §732(c)(3) for a decrease (first to depreciated property in proportion
to depreciation, then by basis). Items are (basis, value). -/
def fitBasis (items : Array (Int × Int)) (target : Int) : Array Int := Id.run do
  let bases := items.map (·.1)
  let diff := target - bases.foldl (· + ·) 0
  if diff ≥ 0 then
    let app := items.map (fun (b, f) => max 0 (f - b))
    let d1 := min diff (app.foldl (· + ·) 0)
    let x1 := spread app d1
    let x2 := spread (items.map (·.2)) (diff - d1)
    return (List.range items.size).toArray.map (fun i => bases[i]! + x1[i]! + x2[i]!)
  else
    let m := -diff
    let dep := items.map (fun (b, f) => max 0 (b - f))
    let d1 := min m (dep.foldl (· + ·) 0)
    let x1 := spread dep d1
    let b1 := (List.range items.size).toArray.map (fun i => bases[i]! - x1[i]!)
    let x2 := spread b1 (min (m - d1) (b1.foldl (· + ·) 0))
    return (List.range items.size).toArray.map (fun i => b1[i]! - x2[i]!)

def partners (s : State) : List Nat := (List.range s.persons.size).filter (fun i => s.persons[i]!.cap > 0)

/-- §708(b)(1): when only one partner is left, nothing is carried on "in a partnership"; it has terminated and he
holds the property. §731(a): gain if the money exceeds his interest basis; loss only if he receives nothing but
money and inventory. §732(b), (c): his interest basis less money becomes the basis of the property, inventory
first and never above the partnership's basis. He takes over the liabilities (§752(a) and (b) offset). -/
def terminate (s : State) : State := Id.run do
  match partners s with
  | [p] =>
    let P := s.persons[p]!
    let gain := max 0 (s.pcash - P.outside)
    let rem := max 0 (P.outside - s.pcash)
    let held (inv : Bool) (a : Asset) : Bool := a.holder == .pship ∧ (a.kind == .inventory) == inv
    let item (a : Asset) : Int × Int := (a.basis + a.adj[p]!, a.fmv)
    let invIdx := (List.range s.assets.size).filter (fun i => held true s.assets[i]!)
    let capIdx := (List.range s.assets.size).filter (fun i => held false s.assets[i]!)
    let invItems := invIdx.toArray.map (fun i => item s.assets[i]!)
    let invTot := invItems.foldl (fun acc x => acc + x.1) 0
    let invB := if rem < invTot then fitBasis invItems rem else invItems.map (·.1)
    let rem2 := max 0 (rem - invTot)
    let capItems := capIdx.toArray.map (fun i => item s.assets[i]!)
    let capB := fitBasis capItems rem2
    let loss := if capIdx.isEmpty then rem2 else 0
    let mut s := s
    let setB (s : State) (i : Nat) (b : Int) : State :=
      modA s i (fun a => { a with basis := b, holder := .person p, contrib := none, succ := none, big := 0,
                                  adj := zeroAdj s.persons.size })
    for k in [0:invIdx.length] do s := setB s invIdx[k]! invB[k]!
    for k in [0:capIdx.length] do s := setB s capIdx[k]! capB[k]!
    s := modP s p (fun P => { P with cash := P.cash + s.pcash - P.liab, outside := 0, cap := 0, liab := 0, susp := 0,
                                     capGain := P.capGain + gain - loss, cashYr := none, propYr := none,
                                     nonInv := false })
    return { s with pcash := 0, elect := false, everNonInv := false, carry := 0 }
  | _ => return s

/-- Sale of a whole interest for its value. §741: capital gain or loss, except §751(a): the part attributable to
inventory is ordinary. §752(d): liabilities assumed are amount realised. §267(a)(1): no loss on a sale to a related
person. Buyer: cost basis (§742, §1012) including liabilities. §743(b), if a §754 election is in effect or
(§743(d)) the partnership has a substantial built-in loss (inside basis over value by more than $250,000, or the
transferee would be allocated a loss over $250,000): the buyer's own basis in each asset is adjusted by the
seller's share of its gain or loss (§755). §704(c)(3): the buyer succeeds to the seller's §704(c) position. -/
def sellInt (cfg : Cfg) (s : State) (p q : Nat) : Option State := do
  let P ← s.persons[p]?
  let Q ← s.persons[q]?
  guard (p != q ∧ P.cap > 0 ∧ Q.cash ≥ P.cap)
  let shares : Array Int := s.assets.map (fun a => if a.holder == .pship then (allocSale s a)[p]! else 0)
  let hotAll : Int := Id.run do
    let mut h : Int := 0
    for a in s.assets do
      if a.holder == .pship ∧ a.kind == .inventory then h := h + (allocSale s a)[p]!
    return h
  let total := P.cap + P.liab - P.outside
  let disallowed := total < 0 ∧ cfg.related p q
  let ordPart := hotAll
  let capPart := total - ordPart
  let inB := s.assets.foldl (fun acc a => if a.holder == .pship then acc + a.basis else acc) 0
  let inV := s.assets.foldl (fun acc a => if a.holder == .pship then acc + a.fmv else acc) 0
  let lossToBuyer := shares.foldl (· + ·) 0
  let mandatory : Bool := inB - inV > 250 ∨ lossToBuyer < -250
  let mut s := s
  s := modP s p (fun P => { P with cash := P.cash + P.cap, outside := 0, cap := 0, liab := 0, susp := 0,
                                   capGain := if disallowed then P.capGain else P.capGain + capPart,
                                   ordInc := if disallowed then P.ordInc else P.ordInc + ordPart })
  s := modP s q (fun Q => { Q with cash := Q.cash - P.cap, outside := Q.outside + P.cap + P.liab,
                                   cap := Q.cap + P.cap, liab := Q.liab + P.liab })
  for j in [0:s.assets.size] do
    let a := s.assets[j]!
    if a.holder == .pship then
      let adj := (a.adj.set! p 0)
      let adj := if s.elect || mandatory then adj.modify q (· + shares[j]!) else adj
      s := modA s j (fun a => { a with adj := adj, succ := if a.succ == some p then some q else a.succ })
  pure s

/-- The partnership sells an asset for its value; each partner takes his share (§702, §704, §705). -/
def pSell (s : State) (i : Nat) : Option State := do
  let a ← s.assets[i]?
  guard (a.holder == .pship)
  let al := allocSale s a
  let mut s := s
  for j in [0:s.persons.size] do
    if al[j]! != 0 then s := modP s j (takeShare a.kind al[j]!)
  s := modA s i (fun a => { a with holder := .sold, big := 0, succ := none })
  pure { s with pcash := s.pcash + a.fmv }

/-- §1001: a person sells an asset he holds. -/
def ownSell (s : State) (i : Nat) : Option State := do
  let a ← s.assets[i]?
  match a.holder with
  | .person p =>
    let s := modP s p (fun P => recG a.kind (a.fmv - a.basis) { P with cash := P.cash + a.fmv })
    pure (modA s i (fun a => { a with holder := .sold }))
  | _ => none

/-- §1012: the partnership buys a capital asset for cash; basis is cost. Any §755(b) adjustment waiting for
property of like character attaches to it. -/
def buy (s : State) (amt : Int) : Option State := do
  guard (amt > 0 ∧ amt ≤ s.pcash ∧ s.assets.all (fun a => a.id != 9))
  let b := max 0 (amt + s.carry)
  let a : Asset := { id := 9, kind := .capital, fmv := amt, basis := b, holder := .pship, contrib := none,
                     succ := none, yr := s.year, big := 0, adj := zeroAdj s.persons.size }
  pure { s with pcash := s.pcash - amt, assets := s.assets.push a, carry := s.carry - (b - amt), everNonInv := true }

/-- The clocks that are running: 2 years (Reg. §1.707-3(c)) and 7 years (§§704(c)(1)(B), 737(b)) from each
contribution. -/
def clocks (s : State) : List Nat := Id.run do
  let mut out : List Nat := []
  for a in s.assets do
    if a.holder == .pship ∧ a.contrib.isSome then
      for d in [2, 7] do
        if a.yr + d > s.year ∧ !out.contains (a.yr + d) then out := (a.yr + d) :: out
  for P in s.persons do
    if let some y := P.cashYr then
      if P.cap > 0 ∧ y + 2 > s.year ∧ !out.contains (y + 2) then out := (y + 2) :: out
  return out

def step (cfg : Cfg) (s : State) : Move → Option State
  | .contribute p a => contribute s p a
  | .contribCash p amt => contribCash s p amt
  | .borrow g amt => if (partners s).length < 2 then none else borrow s g amt
  | .repay g => repay s g
  | .dist p a cash => (distribute cfg s p a cash).map terminate
  | .sellInt p q => (sellInt cfg s p q).map terminate
  | .pSell a => if (partners s).length < 2 then none else pSell s a
  | .ownSell a => ownSell s a
  | .buy amt => if (partners s).length < 2 then none else buy s amt
  | .elect => if s.elect ∨ (partners s).length < 2 then none else some { s with elect := true }
  | .wait y => if (clocks s).contains y then some { s with year := y } else none

/-! ## Part 2. Search -/

/-- Everything sold and the partnership wound up: the partnership sells each asset, pays its debts, distributes
the cash in liquidation (§731(a)); each person sells what he holds directly. -/
def windup (s : State) : State := Id.run do
  let mut s := s
  for i in [0:s.assets.size] do
    if let some s' := pSell s i then s := s'
  for j in [0:s.persons.size] do
    let P := s.persons[j]!
    if P.cap > 0 ∨ P.liab > 0 then
      s := modP s j (fun P => { P with capGain := P.capGain + (P.cap + P.liab - P.outside), cash := P.cash + P.cap,
                                       outside := 0, cap := 0, liab := 0 })
  for i in [0:s.assets.size] do
    if let some s' := ownSell s i then s := s'
  return s

/-- Tax in dollars (amounts are thousands): 23.8% on net capital gain (20% + §1411), 40.8% on ordinary income
(37% + 3.8%), losses taken at the same rates. -/
def taxOf (P : Person) : Int := P.capGain * 238 + P.ordInc * 408
def totalTax (s : State) : Int := s.persons.foldl (fun acc P => acc + taxOf P) 0
def famTax (cfg : Cfg) (s : State) : Int :=
  (List.range s.persons.size).foldl (fun acc i => if cfg.fam i then acc + taxOf s.persons[i]! else acc) 0
def famCash (cfg : Cfg) (s : State) : Int :=
  (List.range s.persons.size).foldl (fun acc i => if cfg.fam i then acc + s.persons[i]!.cash else acc) 0

def pname : Nat → String
  | 0 => "A" | 1 => "B" | 2 => "C" | 3 => "D" | n => s!"P{n}"
def aname : Nat → String
  | 0 => "X" | 1 => "Y" | 2 => "Z" | 9 => "N" | n => s!"asset{n}"

def showMove (aname : Nat → String) : Move → String
  | .contribute p a => s!"{pname p} contributes {aname a}"
  | .contribCash p amt => s!"{pname p} contributes cash {amt}"
  | .borrow g amt => s!"partnership borrows {amt}, borne by {pname g}"
  | .repay g => s!"partnership repays {pname g}'s debt"
  | .dist p a cash =>
    let what := match a with | some i => aname i | none => ""
    s!"distribute to {pname p}: {what}{if a.isSome ∧ cash > 0 then " + " else ""}{if cash > 0 then s!"cash {cash}" else ""}"
  | .sellInt p q => s!"{pname p} sells interest to {pname q}"
  | .pSell a => s!"partnership sells {aname a}"
  | .ownSell a => s!"holder sells {aname a}"
  | .buy amt => s!"partnership buys asset N for {amt}"
  | .elect => "§754 election"
  | .wait y => s!"wait to year {y}"

def moveCode : Move → Nat
  | .contribute .. => 0 | .contribCash .. => 1 | .borrow .. => 2 | .repay .. => 3 | .dist _ (some _) 0 => 4
  | .dist _ none _ => 5 | .dist .. => 6 | .sellInt .. => 7 | .pSell .. => 8 | .ownSell .. => 9 | .buy .. => 10
  | .elect => 11 | .wait .. => 12

def codeName : Nat → String
  | 0 => "contribute" | 1 => "cash-in" | 2 => "borrow" | 3 => "repay" | 4 => "dist-property" | 5 => "dist-cash"
  | 6 => "dist-property+cash" | 7 => "sell-interest" | 8 => "pship-sale" | 9 => "own-sale" | 10 => "buy"
  | 11 => "754" | _ => "wait"

def sigOf (path : List Move) : Nat := path.foldl (fun acc m => acc ||| (1 <<< moveCode m)) 0
def sigName (sig : Nat) : String :=
  " + ".intercalate ((List.range 13).filter (fun c => sig &&& (1 <<< c) != 0) |>.map codeName)

/-- Moves offered in a position, amounts taken from the position itself. -/
def moves (cfg : Cfg) (s : State) : List Move := Id.run do
  let n := s.persons.size
  let mut out : List Move := []
  for i in [0:s.assets.size] do
    match s.assets[i]!.holder with
    | .person p => out := .contribute p i :: .ownSell i :: out
    | .pship => out := .pSell i :: out
    | .sold => pure ()
  for p in [0:n] do
    let P := s.persons[p]!
    if P.cash ≥ cfg.unit then out := .contribCash p cfg.unit :: out
    if P.cap > 0 then
      if totalDebt s == 0 then out := .borrow p cfg.unit :: out
      if P.liab > 0 then out := .repay p :: out
      for q in [0:n] do
        if q != p then out := .sellInt p q :: out
      -- cash only
      for c in [min s.pcash P.cap, min s.pcash P.outside, min s.pcash cfg.unit, min s.pcash (P.cap * 9 / 10)].eraseDups do
        if c > 0 ∧ c ≤ P.cap then out := .dist p none c :: out
      for i in [0:s.assets.size] do
        let a := s.assets[i]!
        if a.holder == .pship ∧ a.fmv ≤ P.cap then
          out := .dist p (some i) 0 :: out
          let c := min s.pcash (P.cap - a.fmv)
          if c > 0 then out := .dist p (some i) c :: out
  if s.pcash ≥ cfg.unit then out := .buy cfg.unit :: out
  if !s.elect ∧ s.persons.any (fun P => P.cap > 0) then out := .elect :: out
  for y in clocks s do out := .wait y :: out
  return out

structure Hit where
  taxNow : Int      -- the family's tax so far, plus any tax so far of the unrelated partners (their losses not credited)
  others : Int      -- the unrelated partners' tax so far (negative: losses)
  taxAll : Int
  year : Nat
  len : Nat
  path : List Move
  st : State

def better (a b : Hit) : Bool :=
  a.taxNow < b.taxNow ∨ (a.taxNow == b.taxNow ∧ (a.taxAll < b.taxAll ∨ (a.taxAll == b.taxAll ∧
    (a.year < b.year ∨ (a.year == b.year ∧ a.len < b.len)))))

def isFamHolder (cfg : Cfg) (s : State) : Holder → Bool
  | .person p => cfg.fam p
  | .pship => (partners s).all cfg.fam
  | .sold => false

def famHolds (cfg : Cfg) (s : State) (id : Nat) : Bool := s.assets.any (fun a => a.id == id ∧ isFamHolder cfg s a.holder)

/-- Goal 1: X has left the family for cash — sold, or held by an unrelated person — the family (A and B, related)
has at least X's value in new cash in hand, owes nothing through the partnership, and still has Y. -/
def goalOut (cfg : Cfg) (s0 s : State) : Bool :=
  s.assets.any (fun a => a.id == 0 && a.holder != .pship && !isFamHolder cfg s a.holder) ∧
  famCash cfg s ≥ famCash cfg s0 + cfg.unit ∧ famHolds cfg s 1 ∧
  (List.range s.persons.size).all (fun i => !cfg.fam i ∨ s.persons[i]!.liab == 0)

/-- Goal 2: the family has nine tenths of X's value in new cash in hand while it still holds both X and Y, directly
or through a partnership in which no unrelated person has capital. -/
def goalCash (cfg : Cfg) (s0 s : State) : Bool :=
  famCash cfg s ≥ famCash cfg s0 + cfg.unit * 9 / 10 ∧ famHolds cfg s 0 ∧ famHolds cfg s 1

/-- Goal 4: nothing has been sold and the family holds, directly or through an all-family partnership, every asset
it held or had contributed at the start. -/
def goalKeep (cfg : Cfg) (s0 s : State) : Bool :=
  s.assets.size == s0.assets.size ∧ (List.range s0.assets.size).all (fun i =>
    let a0 := s0.assets[i]!
    let a := s.assets[i]!
    let mine := match a0.holder with
      | .person p => cfg.fam p
      | .pship => (a0.contrib.map cfg.fam).getD false
      | .sold => false
    !mine || (match a.holder with | .person p => cfg.fam p | _ => false))

/-- Goal 3: every asset has been sold for cash (the cash may still be inside a continuing partnership). -/
def goalSold (s : State) : Bool := s.assets.all (fun a => a.holder == .sold)

def showPerson (i : Nat) (P : Person) : String :=
  s!"{pname i}[cash {P.cash} cap {P.cap} out {P.outside} liab {P.liab} cg {P.capGain} oi {P.ordInc}]"

def describe (h : Hit) : IO Unit := do
  IO.println s!"  family tax now ${h.taxNow}  (unrelated partners now ${h.others})  everyone, once all is sold and wound up ${h.taxAll}  year {h.year}  [{sigName (sigOf h.path)}]"
  IO.println s!"    {"; ".intercalate (h.path.map (showMove (fun i => aname ((h.st.assets[i]?.map (·.id)).getD i))))}"
  let ps := (List.range h.st.persons.size).map (fun i => showPerson i h.st.persons[i]!)
  IO.println s!"    {" ".intercalate ps}"
  let as := h.st.assets.toList.map (fun a =>
    let w := match a.holder with | .person p => pname p | .pship => "pship" | .sold => "sold"
    s!"{aname a.id}:{w} basis {a.basis}/{a.fmv}")
  IO.println s!"    {" ".intercalate as}  carry {h.st.carry}"

def search (label : String) (cfg : Cfg) (depth : Nat) (s0 : State) (allowed : Move → Bool) (top : Nat := 8) :
    IO Unit := do
  let mut frontier : Array (State × List Move) := #[(s0, [])]
  let mut seen : Std.HashSet State := {}
  seen := seen.insert s0
  let mut hits : Array (Std.HashMap Nat Hit) := #[{}, {}, {}, {}]
  for d in [1:depth + 1] do
    let mut next : Array (State × List Move) := #[]
    for (s, path) in frontier do
      for m in moves cfg s do
        if allowed m then
          match step cfg s m with
          | none => pure ()
          | some s' =>
            if !seen.contains s' then
              seen := seen.insert s'
              let path' := path ++ [m]
              let gs := [goalOut cfg s0 s', goalCash cfg s0 s', goalSold s', goalKeep cfg s0 s' && famTax cfg s' < 0]
              if gs.any id then
                let oth := totalTax s' - famTax cfg s'
                let h : Hit := ⟨famTax cfg s' + max 0 oth, oth, totalTax (windup s'), s'.year, d, path', s'⟩
                let sig := sigOf path'
                for k in [0:4] do
                  if gs[k]! then
                    if (hits[k]!.get? sig).all (fun o => better h o) then hits := hits.modify k (·.insert sig h)
              if !gs[0]! ∨ !gs[2]! then next := next.push (s', path')
    frontier := next
    IO.println s!"[{label}] depth {d}: {frontier.size} new positions, {seen.size} in all"
  let w0 := windup s0
  let base := totalTax w0
  IO.println s!"[{label}] plain sale of everything: everyone ${base}, family ${famTax cfg w0}"
  let names := ["X sold out of the family for cash, Y kept", "cash in hand, X and Y kept", "every asset sold",
                "a loss taken while the family keeps every asset"]
  for k in [0:4] do
    let all := hits[k]!.toArray
    -- keep a family only if no family using a strict subset of its kinds of move does at least as well
    let minimal := all.filter (fun (sig, h) => !all.any (fun (sig2, o) =>
      sig2 != sig ∧ sig2 &&& sig == sig2 ∧ o.taxNow ≤ h.taxNow ∧ o.taxAll ≤ h.taxAll))
    let arr := (minimal.map (·.2)).qsort better
    IO.println s!"[{label}] == {names[k]!}: {all.size} families of plans, {arr.size} not dominated; best {top} by tax now =="
    for h in arr.toList.take top do describe h
    let arr2 := arr.qsort (fun a b => a.taxAll < b.taxAll ∨ (a.taxAll == b.taxAll ∧ better a b))
    match arr2.toList.head? with
    | some h => if h.taxAll < base then
                  IO.println s!"[{label}] -- lowest tax after everything is sold and wound up --"
                  for h in (arr2.toList.filter (fun h => h.taxAll < base)).take 3 do describe h
    | none => pure ()

/-! ### Positions -/

def person0 (cash : Int) : Person := ⟨cash, 0, 0, 0, 0, 0, 0, none, none, false⟩
def asset0 (id : Nat) (k : Kind) (fmv basis : Int) (p : Nat) : Asset :=
  ⟨id, k, fmv, basis, .person p, none, none, 0, 0, zeroAdj 4⟩

def rel (p q : Nat) : Bool := (p == 0 ∧ q == 1) ∨ (p == 1 ∧ q == 0)

/-- A holds X (value 1,000, basis 100). B, related to A, holds Y (value 1,000, basis 1,000). C and D are unrelated
and hold cash. -/
def start1 : State :=
  { year := 0, pcash := 0, elect := false, everNonInv := false, carry := 0,
    assets := #[asset0 0 .capital 1000 100 0, asset0 1 .capital 1000 1000 1],
    persons := #[person0 0, person0 0, person0 2000, person0 2000] }

def cfg1 : Cfg := { unit := 1000, debtFin := false, related := rel }

def noD : Move → Bool
  | .sellInt _ 3 => false | .contribCash 3 _ => false | _ => true

/-- The same at a quarter of the size: X (300, basis 60), Y (300, basis 300). Every basis difference is under
$250,000. -/
def start1s : State :=
  { start1 with assets := #[asset0 0 .capital 300 60 0, asset0 1 .capital 300 300 1],
                persons := #[person0 0, person0 0, person0 600, person0 600] }
def cfg1s : Cfg := { cfg1 with unit := 300 }

/-- B's asset has a built-in loss: Y (1,000, basis 1,600). -/
def start2 : State := { start1 with assets := #[asset0 0 .capital 1000 100 0, asset0 1 .capital 1000 1600 1] }

/-- C also holds marketable securities Z (1,000, basis 400). -/
def start3 : State :=
  { start1 with assets := #[asset0 0 .capital 1000 100 0, asset0 1 .capital 1000 1000 1, asset0 2 .security 1000 400 2],
                persons := #[person0 0, person0 0, person0 1000, person0 1000] }

/-- B's asset is inventory: Y (1,000, basis 400). -/
def start4 : State := { start1 with assets := #[asset0 0 .capital 1000 100 0, asset0 1 .inventory 1000 400 1] }

/-- An existing partnership, contributions made long ago (year 0; it is now year 8, so the 2- and 7-year clocks
have run). `mk` puts an asset in the partnership as contributed by `p`. -/
def held (id : Nat) (k : Kind) (fmv basis : Int) (p : Nat) : Asset :=
  ⟨id, k, fmv, basis, .pship, some p, some p, 0, fmv - basis, zeroAdj 4⟩
def partner0 (cash outside cap : Int) (nonInv : Bool := true) : Person :=
  ⟨cash, outside, cap, 0, 0, 0, 0, none, none, nonInv⟩

/-- S6. A, B and C are related; D is not. The partnership holds two parcels contributed by A (each 200, basis 20),
Y contributed by B (200, basis 200), Y' contributed by C (200, basis 200) and 200 of cash contributed by D. No basis
difference on any one parcel reaches $250,000; on the two together it does (360). -/
def start6 : State :=
  { year := 8, pcash := 200, elect := false, everNonInv := true, carry := 0,
    assets := #[held 0 .capital 200 20 0, held 1 .capital 200 200 1, held 2 .capital 200 20 0, held 3 .capital 200 200 2],
    persons := #[partner0 0 40 400, partner0 0 200 200, partner0 0 200 200, partner0 0 200 200] }
def cfg6 : Cfg := { unit := 200, debtFin := false, related := fun p q => p < 3 ∧ q < 3 ∧ p != q, fam := fun p => p < 3 }

/-- S6b. The same value in single pieces: A's parcel (400, basis 40), B's Y (400, basis 400), D's cash 200. -/
def start6b : State :=
  { start6 with assets := #[held 0 .capital 400 40 0, held 1 .capital 400 400 1],
                persons := #[partner0 0 40 400, partner0 0 400 400, partner0 0 0 0, partner0 0 200 200] }

/-- S7. An existing partnership of A (X: 1,000, basis 100), B, related to A (Y: 1,000, basis 1,600) and C,
unrelated (marketable securities Z: 1,000, basis 400). D is an outsider with cash. -/
def start7 : State :=
  { year := 8, pcash := 0, elect := false, everNonInv := true, carry := 0,
    assets := #[held 0 .capital 1000 100 0, held 1 .capital 1000 1600 1, held 2 .security 1000 400 2],
    persons := #[partner0 0 100 1000, partner0 0 1600 1000, partner0 0 400 1000 false, person0 2000] }

/-- S8. A partnership formed three years ago: A put in 1,000 of cash, B (related to A) put in Y (1,000, basis
1,600), C (unrelated) put in 2,000 of cash. The family holds exactly half. -/
def start8 : State :=
  { year := 3, pcash := 3000, elect := false, everNonInv := true, carry := 0,
    assets := #[held 1 .capital 1000 1600 1],
    persons := #[{ partner0 0 1000 1000 with cashYr := some 0 }, partner0 0 1600 1000,
                 { partner0 0 2000 2000 with cashYr := some 0 }, person0 2000] }

/-- S8b. The same, but C put in 1,000, so the family holds two thirds. -/
def start8b : State :=
  { start8 with pcash := 2000,
                persons := #[{ partner0 0 1000 1000 with cashYr := some 0 }, partner0 0 1600 1000,
                             { partner0 0 1000 1000 with cashYr := some 0 }, person0 2000] }

def simple : Move → Bool
  | .borrow .. => false | .repay .. => false | .buy .. => false | .contribCash .. => false | .sellInt .. => false
  | .contribute .. => false | _ => true

def propOnly : Move → Bool
  | .dist _ none _ => false | .dist _ (some _) c => c == 0 | m => simple m

#eval search "S1 X 1000/100, Y 1000/1000" cfg1 6 start1 (fun _ => true) 4
#eval search "S1s X 300/60, Y 300/300" cfg1s 5 start1s (fun _ => true) 2
#eval search "S2 Y built-in loss 1000/1600" cfg1 6 start2 (fun _ => true) 8
#eval search "S3 C holds securities Z 1000/400" cfg1 5 start3 (fun _ => true) 3
#eval search "S4 Y inventory 1000/400" cfg1 6 start4 noD 4
#eval search "S5 as S1, debt-financed exception on" { cfg1 with debtFin := true } 5 start1 noD 3
#eval search "S6 existing partnership, parcels under $250k" cfg6 6 start6 propOnly 4
#eval search "S6b same, single pieces over $250k" cfg6 4 start6b propOnly 4
#eval search "S7 existing partnership with loss asset and securities" cfg1 4 start7 (fun _ => true) 6
#eval search "S8 loss asset, family holds half" cfg1 3 start8 simple 4
#eval search "S8b loss asset, family holds two thirds" cfg1 3 start8b simple 4

end Legal.USTax.Hunt.Partnership
