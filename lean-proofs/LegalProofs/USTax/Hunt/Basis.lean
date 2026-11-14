import Std

/-!
# Basis and transfers of property inside a family (Hunt: `Basis`)

Part 1 writes down what each provision does when property moves between a taxpayer `T`, the spouse `S` (joint
return), a minor child `K`, an adult child `A`, T's elderly parent `P`, and a charity. Part 2 searches every sequence
of those moves and compares the family's total income tax with "every owner simply sells".

Conventions (each stated once):
* Figures are the 2026 ones (Rev. Proc. 2025-32 as I know them; §1202 and §170(b)(1)(I), §68, §151(d)(5)(C) as
  amended by Pub. L. 119-21), held constant over the years of a scenario. Prices are constant.
* All moves of a year happen at one instant; `nextYear` moves the clock one year and a day. So property acquired in
  year y is long-term from year y+1 (§1222), and a gift in year y is outside "the 1-year period ending on the date of
  the decedent's death" (§1014(e)(1)(A)) for a death in year y+1 and inside it for a death in year y.
* Cash is one family pool: cash gifts are not income (§102(a)). The gift-tax exclusion is tracked for property gifts
  only; gifts above §2503(b) use up unified credit (§2505) and no gift tax is paid, so §1015(d) adds nothing to basis.
* T and S file jointly; their "wages" are net of other itemized deductions, so each charitable dollar is an itemized
  deduction. No §1411 tax, no AMT, no state tax, no estate tax (P's estate is under the §2010 amount).
* §267(d) relief belongs to the original transferee only (conservative; the text says "the taxpayer").
* §1091: only "the taxpayer has acquired" is in the text; nobody here buys on the market, so it never bites.
* Not encoded (read, see FINDINGS): §1014(b)(6) community property, §453 installment sales, §1015(d) (no gift tax
  is ever paid here).

Run: `lake env lean LegalProofs/USTax/Hunt/Basis.lean` runs `small` (about a minute). `wide` (up to 3.4 million
positions) needs a compiled scratch copy; the commands are in `Basis.FINDINGS.md`.
-/

namespace Legal.USTax.Hunt.Basis

/-! ## Part 1. Rules -/

inductive Who where | T | S | K | A | P
  deriving BEq, Hashable, Repr, DecidableEq, Inhabited

inductive Kind where | stock | qsbs | home
  deriving BEq, Hashable, Repr, DecidableEq, Inhabited

def Who.name : Who → String
  | .T => "T" | .S => "S" | .K => "K" | .A => "A" | .P => "P"

def Who.idx : Who → Nat
  | .T => 0 | .S => 1 | .K => 2 | .A => 3 | .P => 4

/-- §1041(a)(1): spouses. -/
def spouses (a b : Who) : Bool := (a == .T && b == .S) || (a == .S && b == .T)

/-- §267(b)(1), (c)(4): brothers and sisters, spouse, ancestors, lineal descendants. P is T's parent, so P is an
ancestor of T, K and A but is **not** in S's family. -/
def related267 (a b : Who) : Bool :=
  match a, b with
  | .T, .S | .S, .T | .T, .K | .K, .T | .T, .A | .A, .T | .T, .P | .P, .T => true
  | .S, .K | .K, .S | .S, .A | .A, .S | .K, .A | .A, .K | .K, .P | .P, .K | .A, .P | .P, .A => true
  | _, _ => false

structure Lot where
  kind : Kind
  owner : Who
  fmv : Nat
  basis : Nat        -- basis for determining gain
  lossBasis : Nat    -- basis for determining loss: §1015(a) lowers it to value at the time of a gift
  held : Nat         -- whole years of holding period, with tacking (§1223(2), §1202(h)(1)(B)); capped at 5
  owned : Nat        -- years owned by the present owner for §121(a) (tacked only by §121(d)(3)(A)); capped at 2
  shield : Nat       -- loss disallowed to the seller by §267(a)(1), usable by this owner under §267(d)
  donor : Option Who -- the person who gave it to the present owner, if it was acquired by gift
  giftAge : Nat      -- years since that gift (0 = inside one year)
  inherited : Bool   -- basis determined under §1014: §1223(9) makes it long-term
  gone : Bool
  deriving BEq, Hashable, Repr, Inhabited

structure Ret where
  st : Int := 0     -- short-term gains less losses this year
  lt : Int := 0     -- long-term
  g28 : Nat := 0    -- section 1202 gain, §1(h)(7): 28-percent rate gain
  cfS : Nat := 0    -- §1212(b) carryovers
  cfL : Nat := 0
  x121 : Nat := 0   -- §121 exclusion used (never reset: §121(b)(3), conservative)
  xQ : Nat := 0     -- §1202(b)(4)(B): eligible gain already taken into account for this issuer
  deriving BEq, Hashable, Repr, Inhabited

structure Cfg where
  wJ : Nat                 -- joint return: ordinary taxable income before charity
  wA : Nat                 -- adult child's wages
  wP : Nat                 -- parent's pension
  death : Option Nat       -- year in which P dies
  horizon : Nat            -- number of tax years
  hold : Bool              -- if set, nothing is sold on the market before the last year
  users : List Who         -- who lives in the home (and has for two years)

structure St where
  lots : List Lot
  year : Nat
  cur : Nat                -- search order only: lots are touched in index order within a year
  pAlive : Bool
  pFinal : Bool            -- P died this year: final return still due
  rJ : Ret
  rK : Ret
  rA : Ret
  rP : Ret
  charCash : Nat           -- this year's contributions, joint return
  charProp : Nat           -- of capital gain property, §170(b)(1)(C)
  cfChar : Nat             -- §170(d)(1) / (b)(1)(C)(ii) carryover
  pledge : Nat             -- what the family gives the charity in any case
  tax : Nat                -- income tax of all four returns, all years
  deriving BEq, Hashable, Repr, Inhabited

inductive Move where
  | sell (i : Nat)                -- sale on the market for cash
  | gift (i : Nat) (to : Who)     -- §102, §1015, §1041
  | sellTo (i : Nat) (to : Who)   -- sale to a family member at value, §267
  | donate (i : Nat)              -- to a public charity, §170
  | donateCash                    -- pay what is left of the pledge in cash
  | die (heir : Who)              -- P dies; the will leaves everything to `heir`
  | nextYear
  deriving BEq, Repr

/-! ### Rates -/

structure Filing where
  brk : List (Nat × Nat)   -- (top of bracket, percent), §1(j)
  z0 : Nat                 -- §1(h)(1)(B): top of the 0-percent band
  z15 : Nat                -- §1(h)(1)(C): top of the 15-percent band

def big : Nat := 1000000000000

def mfj : Filing :=
  ⟨[(24800, 10), (100800, 12), (211400, 22), (403550, 24), (512450, 32), (768700, 35), (big, 37)], 98900, 613700⟩
def single : Filing :=
  ⟨[(12400, 10), (50400, 12), (105700, 22), (201775, 24), (256225, 32), (640600, 35), (big, 37)], 49450, 545500⟩

def ordTax (f : Filing) (x : Nat) : Nat := Id.run do
  let mut prev := 0
  let mut t := 0
  for (top, rate) in f.brk do
    if x > prev then t := t + (min x top - prev) * rate / 100
    prev := top
  return t

/-- §1(h): ordinary income, then 28-percent rate gain (taxed as ordinary but at no more than 28%), then the rest of
net capital gain through the 0 / 15 / 20 bands. -/
def fullTax (f : Filing) (ord g28 lt : Nat) : Nat :=
  let t0 := ordTax f ord
  let tg := min (ordTax f (ord + g28) - t0) (g28 * 28 / 100)
  let base := ord + g28
  let at0 := min lt (f.z0 - min f.z0 base)
  let rem := lt - at0
  let s15 := max base f.z0
  let at15 := min rem (f.z15 - min f.z15 s15)
  let at20 := rem - at15
  t0 + tg + at15 * 15 / 100 + at20 * 20 / 100

structure Net where
  sG : Nat
  lG : Nat
  g28 : Nat
  lossDed : Nat
  cfS : Nat
  cfL : Nat

/-- §1222 netting, §1211(b) ($3,000 against ordinary income), §1212(b) carryover (short-term loss used first),
§1(h)(4)(B) (losses reduce 28-percent rate gain first). -/
def capNet (r : Ret) : Net :=
  let s : Int := r.st - r.cfS
  let l : Int := r.lt - r.cfL
  let g : Int := r.g28
  let u : Int := if s < 0 then min (-s) g else 0
  let s := s + u
  let g := g - u
  let u : Int := if l < 0 then min (-l) g else 0
  let l := l + u
  let g := g - u
  if s ≥ 0 ∧ l ≥ 0 then ⟨s.toNat, l.toNat, g.toNat, 0, 0, 0⟩
  else if s < 0 ∧ l ≥ 0 then
    if l + s ≥ 0 then ⟨0, (l + s).toNat, g.toNat, 0, 0, 0⟩
    else let loss := (-(l + s)).toNat; let d := min 3000 loss; ⟨0, 0, g.toNat, d, loss - d, 0⟩
  else if l < 0 ∧ s ≥ 0 then
    if l + s ≥ 0 then ⟨(l + s).toNat, 0, g.toNat, 0, 0, 0⟩
    else let loss := (-(l + s)).toNat; let d := min 3000 loss; ⟨0, 0, g.toNat, d, 0, loss - d⟩
  else
    let ls := (-s).toNat
    let ll := (-l).toNat
    let d := min 3000 (ls + ll)
    let dS := min d ls
    ⟨0, 0, g.toNat, d, ls - dS, ll - (d - dS)⟩

/-- Taxable income in its three layers, deductions taken from ordinary income first. -/
def tiParts (wages ded : Nat) (n : Net) : Nat × Nat × Nat :=
  let og := wages + n.sG - n.lossDed
  let ord := og - ded
  let spare := ded - og
  let g := n.g28 - spare
  let spare := spare - n.g28
  (ord, g, n.lG - spare)

def retTax (f : Filing) (wages ded : Nat) (n : Net) : Nat :=
  let (o, g, l) := tiParts wages ded n
  fullTax f o g l

def agiOf (wages : Nat) (n : Net) : Nat := wages + n.sG + n.lG + n.g28 - n.lossDed

/-! ### Figures -/

def stdSingle : Nat := 16100      -- §63(c)
def stdAged : Nat := 2050         -- §63(f), unmarried
def seniorDed : Nat := 6000       -- §151(d)(5)(C), less 6% of MAGI over $75,000
def stdDependent : Nat := 1350    -- §63(c)(5)(A)
def giftExcl : Nat := 19000       -- §2503(b)
def qCap : Nat := 15000000        -- §1202(b)(4)(B)
def top37 : Nat := 768700         -- §68(a)(2), joint

/-! ### Helpers -/

def getRet (s : St) : Who → Ret
  | .T | .S => s.rJ | .K => s.rK | .A => s.rA | .P => s.rP

def setRet (s : St) (w : Who) (r : Ret) : St :=
  match w with
  | .T | .S => { s with rJ := r } | .K => { s with rK := r } | .A => { s with rA := r } | .P => { s with rP := r }

def alive (s : St) (w : Who) : Bool := w != .P || s.pAlive

def addGain (r : Ret) (long : Bool) (x : Int) : Ret :=
  if long then { r with lt := r.lt + x } else { r with st := r.st + x }

/-- §121(a), (b)(1), (b)(2): $250,000; $500,000 on a joint return if either spouse meets the ownership test and both
meet the use test. -/
def limit121 (cfg : Cfg) (l : Lot) : Nat :=
  if l.owned < 2 then 0
  else match l.owner with
    | .T | .S =>
      if cfg.users.contains .T && cfg.users.contains .S then 500000
      else if cfg.users.contains l.owner then 250000 else 0
    | w => if cfg.users.contains w then 250000 else 0

/-- Gain or loss on a sale at value, entered on the owner's return. Returns the loss that was **not** allowed. -/
def recognize (cfg : Cfg) (s : St) (l : Lot) (lossAllowed : Bool) : St × Nat :=
  let long := l.held ≥ 1 || l.inherited          -- §1222, §1223(9)
  let r := getRet s l.owner
  if l.fmv > l.basis then
    let gain0 := l.fmv - l.basis
    let gain := gain0 - min gain0 l.shield         -- §267(d)(1)
    match l.kind with
    | .home =>
      let lim := limit121 cfg l
      let ex := min gain (lim - min lim r.x121)
      (setRet s l.owner (addGain { r with x121 := r.x121 + ex } long ((gain - ex : Nat) : Int)), 0)
    | .qsbs =>
      -- §1202(a)(1)(B), (a)(5): 50% at 3 years, 75% at 4, 100% at 5; (b)(1), (b)(4)(B): $15,000,000 of eligible
      -- gain per taxpayer per issuer, counted in full whatever the percentage
      let pct := if l.held ≥ 5 then 100 else if l.held = 4 then 75 else if l.held = 3 then 50 else 0
      if pct = 0 then (setRet s l.owner (addGain r long (gain : Int)), 0)
      else
        let elig := min gain (qCap - min qCap r.xQ)
        let ex := elig * pct / 100
        let r := { r with xQ := r.xQ + elig, g28 := r.g28 + (elig - ex), lt := r.lt + ((gain - elig : Nat) : Int) }
        (setRet s l.owner r, 0)
    | .stock => (setRet s l.owner (addGain r long (gain : Int)), 0)
  else if l.fmv < l.lossBasis then
    let loss := l.lossBasis - l.fmv
    if l.kind == .home then (s, 0)                 -- §165(c): a personal loss
    else if lossAllowed then (setRet s l.owner (addGain r long (-(loss : Int))), 0)
    else (s, loss)
  else (s, 0)                                      -- §1015(a): between the two bases, neither gain nor loss

def zeroYear (r : Ret) (n : Net) : Ret := { r with st := 0, lt := 0, g28 := 0, cfS := n.cfS, cfL := n.cfL }

/-- A lot that has left the family. -/
def deadLot : Lot :=
  { kind := .stock, owner := .T, fmv := 0, basis := 0, lossBasis := 0, held := 0, owned := 0, shield := 0,
    donor := none, giftAge := 1, inherited := false, gone := true }

/-- Forget what can no longer matter, so that equal positions compare equal (search only): who gave a lot matters
only while P, the one person who dies, holds it (§1014(e)); years of ownership only for a home (§121); holding
period beyond one year only for §1202. -/
def norm (cfg : Cfg) (pAlive : Bool) (l : Lot) : Lot :=
  if l.gone then deadLot
  else
    let keep := l.owner == .P && pAlive && cfg.death.isSome
    { l with donor := if keep then l.donor else none, giftAge := if keep then l.giftAge else 1,
             owned := if l.kind == .home then l.owned else 0,
             held := if l.kind == .qsbs then l.held else min 1 l.held }

/-- Close the tax year: four returns. -/
def closeYear (cfg : Cfg) (s : St) : St :=
  -- joint return, with §170
  let nJ := capNet s.rJ
  let agiJ := agiOf cfg.wJ nJ
  let cash := min s.charCash (agiJ * 60 / 100)                       -- §170(b)(1)(G)
  let availP := s.charProp + s.cfChar
  let prop := min availP (min (agiJ * 30 / 100) (agiJ * 50 / 100 - min (agiJ * 50 / 100) cash))  -- (b)(1)(C)
  let cf := (availP - prop) + (s.charCash - cash)
  let total := cash + prop
  let ded0 := total - min total (agiJ / 200)                         -- §170(b)(1)(I): 0.5% floor
  let tiNo := (tiParts cfg.wJ 0 nJ)
  let tiNoSum := tiNo.1 + tiNo.2.1 + tiNo.2.2
  let ded := ded0 - 2 * (min ded0 (tiNoSum - top37)) / 37            -- §68(a)
  let (oJ, gJ, lJ) := tiParts cfg.wJ ded nJ
  let taxJ := fullTax mfj oJ gJ lJ
  -- minor child, §1(g)
  let nK := capNet s.rK
  let u := nK.sG + nK.lG + nK.g28
  let tiK := u - stdDependent
  let nui := min tiK (u - 2 * stdDependent)                          -- §1(g)(4)
  let regK := retTax single 0 stdDependent nK
  let taxK :=
    if nui = 0 then regK
    else
      let aS := nui * nK.sG / u
      let aG := nui * nK.g28 / u
      let aL := nui - aS - aG
      let par := fullTax mfj (oJ + aS) (gJ + aG) (lJ + aL) - taxJ    -- §1(g)(3)
      let rest := tiK - nui
      let own := if nK.sG > 0 then fullTax single rest 0 0 else fullTax single 0 0 rest
      max regK (own + par)                                           -- §1(g)(1)
  -- adult child
  let nA := capNet s.rA
  let taxA := retTax single cfg.wA stdSingle nA
  -- parent (last return in the year of death; carryovers end there)
  let nP := capNet s.rP
  let agiP := agiOf cfg.wP nP
  let sen := seniorDed - min seniorDed (6 * (agiP - 75000) / 100)
  let taxP := if s.pAlive || s.pFinal then retTax single cfg.wP (stdSingle + stdAged + sen) nP else 0
  let rP := if s.pAlive then zeroYear s.rP nP else {}
  { s with
    year := s.year + 1, cur := 0, pFinal := false,
    rJ := zeroYear s.rJ nJ, rK := zeroYear s.rK nK, rA := zeroYear s.rA nA, rP := rP,
    charCash := 0, charProp := 0, cfChar := cf,
    tax := s.tax + taxJ + taxK + taxA + taxP,
    lots := s.lots.map fun l =>
      if l.gone then l
      else norm cfg s.pAlive { l with held := min 5 (l.held + 1), owned := min 2 (l.owned + 1), giftAge := 1 } }

def touch (cfg : Cfg) (s : St) (i : Nat) (l : Lot) : St := { s with lots := s.lots.set i (norm cfg s.pAlive l), cur := i }

/-- One move, if the Code allows it. -/
def step (cfg : Cfg) (s : St) : Move → Option St
  | .sell i =>
    match s.lots[i]? with
    | some l =>
      if l.gone || i < s.cur || !alive s l.owner || (cfg.hold && s.year + 1 != cfg.horizon) then none
      else
        let (s', _) := recognize cfg s l true
        some (touch cfg s' i { l with gone := true })
    | none => none
  | .gift i to =>
    match s.lots[i]? with
    | some l =>
      if l.gone || i < s.cur || l.owner == to || l.owner == .K || !alive s l.owner || !alive s to then none
      else if spouses l.owner to then
        -- §1041(a), (b): no gain or loss, treated as a gift, transferor's adjusted basis; §1015(e) switches the
        -- loss rule of §1015(a) off; §1223(2); §121(d)(3)(A); §2523 (no gift)
        some (touch cfg s i { l with owner := to, shield := 0, donor := some l.owner, giftAge := 0 })
      else
        -- §1015(a): donor's basis, but for loss no more than value at the gift; §1223(2); §1202(h)(1)
        let lb := min l.lossBasis l.fmv
        some (touch cfg s i { l with owner := to, lossBasis := lb, owned := 0, shield := 0, donor := some l.owner, giftAge := 0 })
    | none => none
  | .sellTo i to =>
    match s.lots[i]? with
    | some l =>
      -- search pruning: at constant prices a sale at a gain to a family member taxes the seller exactly as a market
      -- sale does, so only loss property (or any property when market sales are barred) is offered
      if l.gone || i < s.cur || l.owner == to || spouses l.owner to || !alive s l.owner || !alive s to
          || !(l.fmv < l.lossBasis || cfg.hold) then none
      else
        -- §267(a)(1): no deduction for a loss on a sale between related persons; §267(d): the buyer's later gain
        -- is recognized only above that loss. Buyer's basis is cost (§1012), holding period starts again.
        let (s', dis) := recognize cfg s l (!related267 l.owner to)
        some (touch cfg s' i
          { l with owner := to, basis := l.fmv, lossBasis := l.fmv, held := 0, owned := 0, shield := dis,
                   donor := none, giftAge := 0, inherited := false })
    | none => none
  | .donate i =>
    match s.lots[i]? with
    | some l =>
      if l.gone || i < s.cur || !(l.owner == .T || l.owner == .S) || l.kind != .stock || l.fmv > s.pledge then none
      else
        let long := l.held ≥ 1 || l.inherited
        let s := { s with pledge := s.pledge - l.fmv }
        -- §170(e)(1)(A): value less the gain that would not be long-term capital gain
        let s := if l.fmv > l.basis then
                   if long then { s with charProp := s.charProp + l.fmv } else { s with charCash := s.charCash + l.basis }
                 else { s with charCash := s.charCash + l.fmv }
        some (touch cfg s i { l with gone := true })
    | none => none
  | .donateCash =>
    if s.pledge = 0 then none else some { s with charCash := s.charCash + s.pledge, pledge := 0 }
  | .die heir =>
    if !s.pAlive || cfg.death != some s.year || heir == .P || heir == .S then none
    else
      let lots := s.lots.map fun l =>
        if l.gone || l.owner != .P then l
        else
          -- §1014(e): appreciated property given to the decedent within a year and passing back to the donor or
          -- the donor's spouse keeps the decedent's basis
          let back := match l.donor with
            | some d => l.giftAge = 0 && l.fmv > l.basis && (d == heir || spouses d heir)
            | none => false
          if back then { l with owner := heir, owned := 0, shield := 0, donor := none }
          else
            -- §1014(a)(1), (b)(1); §1223(9); §1202(h)(2)(B) keeps the holding period for §1202
            { l with owner := heir, basis := l.fmv, lossBasis := l.fmv, owned := 0, shield := 0, donor := none,
                     inherited := true }
      some { s with lots := lots.map (norm cfg false), pAlive := false, pFinal := true, cur := 0 }
  | .nextYear =>
    if cfg.death == some s.year && s.pAlive then none
    else if s.year + 1 == cfg.horizon && (s.pledge != 0 || s.lots.any fun l => !l.gone) then none
    else if s.year ≥ cfg.horizon then none
    else some (closeYear cfg s)

/-! ## Part 2. Search -/

def people : List Who := [.T, .S, .K, .A, .P]

def moves (s : St) : List Move :=
  let n := s.lots.length
  let per := (List.range n).flatMap fun i =>
    [Move.sell i, Move.donate i] ++ people.flatMap fun w => [Move.gift i w, Move.sellTo i w]
  per ++ [.donateCash, .die .T, .die .A, .die .K, .nextYear]

def kindName : Kind → String
  | .stock => "stock" | .qsbs => "QSBS" | .home => "home"

/-- (description, family tag) -/
def describe (s : St) : Move → String × String
  | .sell i => let l := s.lots[i]!; (s!"y{s.year} {l.owner.name} sells #{i}", s!"{l.owner.name} sells")
  | .gift i to => let l := s.lots[i]!; (s!"y{s.year} {l.owner.name} gives #{i} to {to.name}", s!"{l.owner.name}→{to.name} gift")
  | .sellTo i to => let l := s.lots[i]!; (s!"y{s.year} {l.owner.name} sells #{i} to {to.name}", s!"{l.owner.name}→{to.name} sale")
  | .donate i => (s!"y{s.year} donate #{i}", "donate property")
  | .donateCash => (s!"y{s.year} donate cash", "donate cash")
  | .die h => (s!"y{s.year} P dies, heir {h.name}", s!"heir {h.name}")
  | .nextYear => ("", "")

/-- §2503(b), §2513: the part of a property gift above one annual exclusion ($19,000; $38,000 from T and S together).
Counted per gift, outside the state. -/
def giftOver (s : St) : Move → Nat
  | .gift i to =>
    let l := s.lots[i]!
    if spouses l.owner to then 0
    else l.fmv - (if l.owner == .T || l.owner == .S then 2 * giftExcl else giftExcl)
  | _ => 0

def insertSorted (x : String) : List String → List String
  | [] => [x]
  | y :: ys => if x == y then y :: ys else if x < y then x :: y :: ys else y :: insertSorted x ys

structure Found where
  tax : Nat
  gifts : Nat
  cf : Nat
  path : List String

def runPath (cfg : Cfg) (s : St) (ms : List Move) : Option St :=
  ms.foldlM (fun s m => step cfg s m) s

/-- Every owner sells everything in the first year the scenario allows; the pledge is paid in cash; P's will names T. -/
def baseline (cfg : Cfg) (s0 : St) : Option St := Id.run do
  let mut s := s0
  for y in [0:cfg.horizon] do
    if !cfg.hold || y + 1 == cfg.horizon then
      for i in [0:s.lots.length] do
        match step cfg s (.sell i) with
        | some s' => s := s'
        | none => pure ()
      match step cfg s .donateCash with
      | some s' => s := s'
      | none => pure ()
    match step cfg s (.die .T) with
    | some s' => s := s'
    | none => pure ()
    if y + 1 == cfg.horizon then
      for i in [0:s.lots.length] do
        match step cfg s (.sell i) with
        | some s' => s := s'
        | none => pure ()
    match step cfg s .nextYear with
    | some s' => s := s'
    | none => return none
  return some s

def search (title : String) (cfg : Cfg) (s0 : St) (allowed : Move → Bool) (top : Nat := 14) : IO Unit := do
  IO.println s!"\n===== {title} ====="
  for (l, i) in s0.lots.zipIdx do
    IO.println s!"  #{i} {kindName l.kind} of {l.owner.name}: value {l.fmv}, basis {l.basis}, held {l.held}y"
  let base := match baseline cfg s0 with | some s => s.tax | none => 0
  IO.println s!"baseline (owners sell, will to T): tax {base}"
  let mut frontier : Array (St × List String × List String × Nat) := #[(s0, [], [], 0)]
  let mut seen : Std.HashSet St := {}
  let mut fams : Std.HashMap String Found := {}
  let mut nTerm := 0
  let mut depth := 0
  while frontier.size > 0 do
    depth := depth + 1
    let mut next : Array (St × List String × List String × Nat) := #[]
    for (s, path, tags, gf) in frontier do
      for m in moves s do
        if allowed m then
          match step cfg s m with
          | none => pure ()
          | some s' =>
            let (d, t) := describe s m
            let gf' := gf + giftOver s m
            let path' := if d == "" then path else d :: path
            let tags' := if t == "" then tags else insertSorted t tags
            if s'.year == cfg.horizon then
              nTerm := nTerm + 1
              let key := ", ".intercalate tags'
              let better := match fams[key]? with
                | some f => s'.tax < f.tax || (s'.tax == f.tax && gf' < f.gifts)
                | none => true
              if better then fams := fams.insert key ⟨s'.tax, gf', s'.rJ.cfS + s'.rJ.cfL, path'⟩
            else if !seen.contains s' then
              seen := seen.insert s'
              next := next.push (s', path', tags', gf')
    frontier := next
  IO.println s!"positions {seen.size}, finished plans {nTerm}, families {fams.size}, depth {depth}"
  let arr := fams.toArray.qsort fun a b => a.2.tax < b.2.tax || (a.2.tax == b.2.tax && a.1.length < b.1.length)
  let mut shown := 0
  let mut lastTax := big
  for (k, f) in arr do
    -- one entry per distinct tax level: the shortest family that reaches it, and how many families tie
    if shown < top && f.tax != lastTax then
      shown := shown + 1
      lastTax := f.tax
      let ties := (arr.filter fun x => x.2.tax == f.tax).size
      IO.println s!"tax {f.tax} (saves {(base : Int) - f.tax}; gifts over the exclusion {f.gifts}; joint loss carryover left {f.cf}; {ties} families)  [{k}]"
      IO.println s!"    {"; ".intercalate f.path.reverse}"

/-! ### Scenarios -/

def lot (k : Kind) (o : Who) (fmv basis held : Nat) : Lot :=
  { kind := k, owner := o, fmv := fmv, basis := basis, lossBasis := basis, held := held, owned := if k == .home then 2 else 0, shield := 0,
    donor := none, giftAge := 1, inherited := false, gone := false }

def mk (lots : List Lot) (pledge : Nat) (rP : Ret := {}) : St :=
  { lots := lots, year := 0, cur := 0, pAlive := true, pFinal := false, rJ := {}, rK := {}, rA := {}, rP := rP,
    charCash := 0, charProp := 0, cfChar := 0, pledge := pledge, tax := 0 }

def cfg0 : Cfg := { wJ := 450000, wA := 40000, wP := 30000, death := none, horizon := 2, hold := false, users := [.T, .S, .K, .P] }

/-- 1. No death. T: a long-term winner, a short-term winner, a loser; a $30,000 pledge. -/
def sc1 : St := mk [lot .stock .T 30000 6000 3, lot .stock .T 30000 10000 0, lot .stock .T 20000 50000 3] 30000

/-- 2. P dies. T: a winner. P: a winner and a loser. -/
def sc2 : St := mk [lot .stock .T 60000 10000 3, lot .stock .P 60000 10000 3, lot .stock .P 20000 60000 3] 0

/-- 3. Nothing may be sold on the market before the last year. T: a winner and a loser. -/
def sc3 : St := mk [lot .stock .T 30000 6000 3, lot .stock .T 20000 50000 3] 0

/-- 4. Qualified small business stock issued after July 4, 2025, held two years so far, basis nil. -/
def sc4 (n : Nat) : St := mk (List.replicate n (lot .qsbs .T 12000000 0 2)) 0

/-- 5. The family home, in equal undivided shares, all T's; T, S, K and P live in it. -/
def sc5 (n : Nat) : St := mk (List.replicate n (lot .home .T 500000 100000 3)) 0

/-- 6. Wider: T: long-term winner, short-term winner, loser. P: a winner and a $40,000 loss carryover. Pledge. -/
def sc6 : St := mk [lot .stock .T 60000 10000 3, lot .stock .T 30000 10000 0, lot .stock .T 20000 50000 3,
                    lot .stock .P 60000 10000 3] 30000 { cfL := 40000 }

def all (_ : Move) : Bool := true

/-- The interpreter-sized runs (`lake env lean LegalProofs/USTax/Hunt/Basis.lean`). -/
def small : IO Unit := do
  search "1. no death, two years" cfg0 sc1 all
  search "2a. P dies in year 0 (inside a year of any gift)" { cfg0 with death := some 0 } sc2 all
  search "3. no market sale before the last year" { cfg0 with hold := true } sc3 all
  search "4a. QSBS, two blocks, four years" { cfg0 with horizon := 4 } (sc4 2) all 8
  search "2c. one winner, P dies in year 0, and the will must name T" { cfg0 with death := some 0 }
    (mk [lot .stock .T 60000 10000 3] 0) (fun | .die .A | .die .K => false | _ => true) 6

/-- The wider runs. Too slow for the interpreter; compile a scratch copy (see FINDINGS). -/
def wide : IO Unit := do
  search "2b. P dies in year 1 (more than a year after a year-0 gift)" { cfg0 with death := some 1 } sc2 all
  search "4b. QSBS, three blocks, four years, P dies in year 1" { cfg0 with horizon := 4, death := some 1 } (sc4 3) all 10
  search "5a. home in three shares, three years" { cfg0 with horizon := 3 } (sc5 3) all 10
  search "5b. home in three shares, P dies in year 0" { cfg0 with horizon := 3, death := some 0 } (sc5 3) all 10
  search "6. wider: four lots, pledge, P dies in year 1" { cfg0 with death := some 1 } sc6 all 16

#eval small

end Legal.USTax.Hunt.Basis
