import Std
/-!
# C corporations and their shareholders: what each provision permits and what it taxes

A closely held corporation **C** (cash = retained earnings, one appreciated asset), an individual **A**, A's adult
child **K**, A's sibling **S**, and a second corporation **P** wholly owned by A (the "corporate shareholder").
Amounts are in thousands of dollars. Rates: 2025/2026 top rates, 21% corporate (§11(b)), 20% on net capital gain and
qualified dividends (§1(h)(1)(D), (11)) + 3.8% net investment income tax (§1411) = 23.8%; 28% + 3.8% on "section 1202
gain" (§1(h)(4), (7)); 37% + 3.8% on short-term gain.

Part 1 (rules) says only what each provision does. Part 2 searches every sequence of moves.

Simplifications, each stated once:
* C has no operating income during the plan (the question is how to take out what is already there);
* one class of stock; value per share = (cash + asset value) / shares, no discount for latent corporate tax;
* years are whole; "more than n years" is read as n whole years and a day;
* gift tax is not charged (a gift uses unified credit, $15,000,000 per donor from 2026, §2010(c)(3) as amended 2025);
* capital losses give no benefit; top-bracket individuals throughout;
* left out (read, not encoded): §305/§306 second class of stock, §304 sales to P for cash, §332/§337 liquidation of C
  into P, §1045 rollover, §357/§362(e), §382, §163(j), §267, §1244, §165(g), §7872 loans (a loan is not an extraction);
  §4501 applies only to a corporation whose stock is traded on an established securities market (§4501(b)), §55(b)(2)
  only above $1 billion of income (§59(k)): neither reaches C.
-/

namespace Legal.USTax.Hunt.Corporate

/-! ## Part 1. Rules -/

structure Cfg where
  post2025 : Bool      -- stock acquired after July 4, 2025 (§1202(a)(6)): tiers and $15,000,000
  pPHC : Bool          -- P meets the §542(a)(1) income test (60% of adjusted ordinary gross income is dividends etc.)
  c3Qsbs : Bool        -- read §301(c)(3)(A) gain as "gain from the sale or exchange of" the stock for §1202
  aetLiteral : Bool    -- §535(c)(2): "$250,000 exceeds the accumulated earnings and profits" counts a deficit
  maxYears : Nat
  deriving Repr

def bp (x rate : Nat) : Nat := x * rate / 10000
def rDiv : Nat := 2380
def rLT : Nat := 2380
def rST : Nat := 4080
def r1202 : Nat := 3180
def rCorp : Nat := 2100

/-- §1202(a)(1), (4), (5): the excluded share of gain, by years held. -/
def qPct (cfg : Cfg) (age : Nat) : Nat :=
  if cfg.post2025 then (if age ≥ 5 then 100 else if age ≥ 4 then 75 else if age ≥ 3 then 50 else 0)
  else (if age ≥ 5 then 100 else 0)
/-- §1202(b)(4): the dollar limit per taxpayer per issuer. -/
def qCap (cfg : Cfg) : Nat := if cfg.post2025 then 15000 else 10000

structure Ind where
  sh : Nat
  basis : Nat
  cash : Int        -- money received, net of the individual's own tax
  q : Bool          -- the stock is qualified small business stock in this holder's hands
  usedPrior : Nat   -- §1202(b)(4): eligible gain taken into account in prior years
  gainYr : Nat      -- eligible gain this year
  basisYr : Nat     -- §1202(b)(1)(B): basis of stock disposed of this year
  takenYr : Nat     -- eligible gain taken into account this year
  pend : Nat        -- §301 distributions received this year, character settled at year end (§316(a)(2))
  deriving BEq, Hashable, Repr

structure St where
  alive : Bool
  cash : Nat
  aFmv : Nat
  aBasis : Nat
  accEP : Int
  curEP : Int
  isS : Bool
  sPending : Bool
  sYears : Nat
  nubig : Nat
  aaa : Int
  age : Nat          -- years since the stock was issued; every transfer here tacks (§1223(1), (2), §1202(h))
  year : Nat
  a : Ind
  k : Ind
  s : Ind
  oSh : Nat          -- shares held by unrelated buyers
  gaveK : Bool       -- K holds stock acquired from A within 10 years (§302(c)(2)(B))
  pSh : Nat
  pBasisC : Nat      -- P's basis in its C stock (§362(a))
  pPend : Nat
  pAffil : Bool      -- P and C were members of one affiliated group on each day of this year (§243(b)(1)(B))
  pAlive : Bool
  pCash : Nat
  pAccEP : Int
  pCurEP : Int
  pDivYr : Nat       -- dividends P received this year
  pRegTaxYr : Nat    -- P's regular tax this year
  pDist : Nat        -- P's distributions to A this year
  pBasisA : Nat      -- A's basis in P stock
  tax : Nat          -- all tax paid by anyone
  deriving BEq, Hashable, Repr

inductive Who where | A | K | S deriving BEq, Hashable, Repr, DecidableEq

inductive Move where
  | dividend (amt : Nat)       -- C distributes cash pro rata, §301
  | sellAsset                  -- C sells its asset, §1001/§11; S corporation: §1366, §1374
  | liquidate                  -- complete liquidation, §336 and §331
  | redeem (h : Who) (f : Nat) -- C buys 1/f of h's shares for cash, §302/§317(b)
  | sellOut (h : Who) (f : Nat)-- h sells 1/f of h's shares to an unrelated buyer, §1001, §1202
  | pSellOut                   -- P sells its C shares to an unrelated buyer
  | gift (to : Who) (f : Nat)  -- A gives 1/f of A's shares, §1015, §1223(2), §1202(h)(2)(A)
  | contribP (f : Nat)         -- A transfers 1/f of A's C shares to P for P stock, §351, §358, §362(a)
  | pDistribute (amt : Nat)    -- P distributes cash to A, §301
  | pLiquidate                 -- P liquidates, §331
  | electS                     -- §1362(a), effective for the following year (§1362(b)(3))
  | wait (n : Nat)             -- the taxable year ends; n years pass
  deriving BEq, Hashable, Repr

def getI (s : St) : Who → Ind | .A => s.a | .K => s.k | .S => s.s
def setI (s : St) (h : Who) (i : Ind) : St :=
  match h with | .A => { s with a := i } | .K => { s with k := i } | .S => { s with s := i }
def outSh (s : St) : Nat := s.a.sh + s.k.sh + s.s.sh + s.oSh + s.pSh

/-- Gain of an individual on a sale or exchange of `basisPart` of stock for `amount`: §1001; the §1202 exclusion with
the per-issuer limit (greater of the dollar limit less prior years' eligible gain, or ten times the basis disposed of
in the year, §1202(b)(1)); the part of eligible gain not excluded because of the percentage is "section 1202 gain"
taxed at 28% (§1(h)(7)). Returns the holder and the tax. -/
def exchGain (cfg : Cfg) (age : Nat) (i : Ind) (amount basisPart : Nat) (eligible : Bool := true) : Ind × Nat :=
  let gain := amount - basisPart
  let pct := qPct cfg age
  if i.q && pct > 0 && eligible then
    let gainYr := i.gainYr + gain
    let basisYr := i.basisYr + basisPart
    let lim := max (qCap cfg - min (qCap cfg) i.usedPrior) (10 * basisYr)
    let allowed := max i.takenYr (min gainYr lim)
    let inc := allowed - i.takenYr
    let t := bp (inc * (100 - pct) / 100) r1202 + bp (gain - inc) rLT
    ({ i with cash := i.cash + amount - t, gainYr := gainYr, basisYr := basisYr, takenYr := allowed }, t)
  else
    let t := bp gain (if age ≥ 1 then rLT else rST)
    ({ i with cash := i.cash + amount - t }, t)

/-- §301(c) for an individual at year end: `dv` of the year's distributions is dividend (taxed, §1(h)(11)), the rest
reduces basis (§301(c)(2)) and the excess is gain (§301(c)(3)). The cash was received when distributed. -/
def settleInd (cfg : Cfg) (age : Nat) (i : Ind) (dv nd : Nat) : Ind × Nat :=
  let t1 := bp dv rDiv
  let red := min nd i.basis
  let g := nd - red
  let i1 := { i with basis := i.basis - red, cash := i.cash - t1, pend := 0 }
  if cfg.c3Qsbs then
    let (i2, t2) := exchGain cfg age { i1 with cash := i1.cash - g } g 0
    (i2, t1 + t2)
  else
    let t2 := bp g rLT
    ({ i1 with cash := i1.cash - t2 }, t1 + t2)

/-- Year end for C. C corporation: §316(a): dividends come first from the year's earnings and profits computed at year
end, then from accumulated earnings and profits (a deficit for the year is not netted against accumulated earnings for
distributions made during it: the conservative reading). P's dividend: §243(a)(1) 50%, §243(c) 65% at 20% ownership,
§243(a)(3)/(b) 100% for the part out of earnings of a year throughout which P and C were affiliated; §1059(a) if P has
held (with tacking) not more than 2 years and the dividend is at least 10% of basis (§1059(c)), except qualifying
dividends (§1059(e)(2)). S corporation: §1368(c): accumulated adjustments account first, then dividend out of
accumulated earnings and profits, then basis. -/
def settleC (cfg : Cfg) (s : St) : Option St :=
  let d := s.a.pend + s.k.pend + s.s.pend + s.pPend
  if d = 0 then
    some (if s.isS then s else { s with accEP := s.accEP + s.curEP, curEP := 0 })
  else if s.isS then
    let fromA := min d s.aaa.toNat
    let dv := min (d - fromA) s.accEP.toNat
    let one (i : Ind) : Ind × Nat :=
      let dvI := i.pend * dv / d
      settleInd { cfg with c3Qsbs := false } s.age i dvI (i.pend - dvI)
    let (a, ta) := one s.a
    let (k, tk) := one s.k
    let (ss, ts) := one s.s
    some { s with a := a, k := k, s := ss, aaa := s.aaa - fromA, accEP := s.accEP - dv, tax := s.tax + ta + tk + ts }
  else
    let fromCur := min d s.curEP.toNat
    let fromAcc := min (d - fromCur) s.accEP.toNat
    let dv := fromCur + fromAcc
    let one (i : Ind) : Ind × Nat :=
      let dvI := i.pend * dv / d
      settleInd cfg s.age i dvI (i.pend - dvI)
    let (a, ta) := one s.a
    let (k, tk) := one s.k
    let (ss, ts) := one s.s
    -- P
    let dP := s.pPend * dv / d
    let curP := s.pPend * fromCur / d
    let frac := if outSh s = 0 then 0 else s.pSh * 100 / outSh s
    let full := if s.pAffil && frac ≥ 80 then curP else 0
    let rest := dP - full
    let drdRest := rest * (if frac ≥ 20 then 65 else 50) / 100
    let extraordinary := s.age ≤ 2 && dP > 0 && dP * 10 ≥ s.pBasisC
    let red1059 := if extraordinary then min s.pBasisC drdRest else 0
    let gain1059 := if extraordinary then drdRest - red1059 else 0
    let basis1 := s.pBasisC - red1059
    let ndP := s.pPend - dP
    let red2 := min ndP basis1
    let gainP := gain1059 + (ndP - red2)
    let pTax := bp (rest - drdRest + gainP) rCorp
    if s.pCash < pTax then none else
    some { s with a := a, k := k, s := ss, accEP := s.accEP + s.curEP - fromCur - fromAcc, curEP := 0,
                  pPend := 0, pBasisC := basis1 - red2, pCash := s.pCash - pTax,
                  pCurEP := s.pCurEP + dP + gainP - pTax, pDivYr := s.pDivYr + dP, pRegTaxYr := s.pRegTaxYr + pTax,
                  tax := s.tax + ta + tk + ts + pTax }

/-- Year end for P. §316(a) for its distributions to A; if P is a personal holding company, §316(b)(2)(A) makes any
distribution a dividend up to the undistributed personal holding company income, and §541 taxes what is left of that
income (taxable income without the dividends-received deduction, less tax, less dividends paid: §545(a), (b)(1), (3),
§561) at 20%. Otherwise §531 taxes accumulated taxable income (§535(a), (b)(1), (3)) at 20%, with the minimum credit
of §535(c)(2); the purpose in §532(a) is presumed and no reasonable business need is assumed. -/
def settleP (cfg : Cfg) (s : St) : Option St :=
  if !s.pAlive then some s else
  let income := s.pDivYr - s.pRegTaxYr
  let d1 := min s.pDist s.pCurEP.toNat
  let d2 := min (s.pDist - d1) s.pAccEP.toNat
  let dvA := if cfg.pPHC then max (d1 + d2) (min s.pDist income) else d1 + d2
  let credit := if cfg.pPHC then 0
    else if cfg.aetLiteral then ((250 : Int) - s.pAccEP).toNat else 250 - min 250 s.pAccEP.toNat
  let pen := bp (income - min income (dvA + credit)) 2000
  if s.pCash < pen then none else
  let (a, ta) := settleInd { cfg with c3Qsbs := false } s.age { s.a with basis := s.pBasisA, pend := 0 } dvA (s.pDist - dvA)
  some { s with a := { a with basis := s.a.basis }, pBasisA := a.basis, pCash := s.pCash - pen,
                pAccEP := s.pAccEP + s.pCurEP - dvA - pen, pCurEP := 0, pDivYr := 0, pRegTaxYr := 0, pDist := 0,
                tax := s.tax + ta + pen }

def settle (cfg : Cfg) (s : St) : Option St := (settleC cfg s).bind (settleP cfg)

/-- C disposes of its asset at value. C corporation: §11 on the gain, which adds to the year's earnings and profits.
S corporation: §1374 at 21% on built-in gain recognized within 5 years of the first S year (§1374(d)(7)); the gain,
less that tax (§1366(f)(2)), is taxed to the shareholders (§1366(a)) and raises their basis (§1367(a)(1)) and the
accumulated adjustments account (§1368(e)(1)). -/
def sellAssetStep (s : St) : St :=
  let gain := s.aFmv - s.aBasis
  if !s.isS then
    let t := bp gain rCorp
    { s with cash := s.cash + s.aFmv - t, aFmv := 0, aBasis := 0, curEP := s.curEP + gain - t, tax := s.tax + t }
  else
    let big := if s.sYears < 5 then bp (min gain s.nubig) rCorp else 0
    let pass := gain - big
    let o := outSh s
    let one (i : Ind) : Ind × Nat :=
      let share := pass * i.sh / o
      let t := bp share rLT
      ({ i with basis := i.basis + share, cash := i.cash - t }, t)
    let (a, ta) := one s.a
    let (k, tk) := one s.k
    let (ss, ts) := one s.s
    { s with cash := s.cash + s.aFmv - big, aFmv := 0, aBasis := 0, nubig := s.nubig - min gain s.nubig,
             aaa := s.aaa + pass, a := a, k := k, s := ss, tax := s.tax + big + ta + tk + ts }

/-- §318(a): stock a holder is treated as owning. Parent and child (§318(a)(1)(A)(ii)); A owns all of P, so P's
shares are A's (§318(a)(2)(C)) and, being treated as actually owned (§318(a)(5)(A)), K's too. Siblings are not in
§318(a)(1). -/
def constructive (s : St) : Who → Nat
  | .A => s.a.sh + s.k.sh + s.pSh
  | .K => s.k.sh + s.a.sh + s.pSh
  | .S => s.s.sh

def step (cfg : Cfg) (s : St) : Move → Option St
  | .dividend amt =>
    let o := outSh s
    if s.alive ∧ 0 < amt ∧ amt ≤ s.cash ∧ o > 0 then
      let give (i : Ind) : Ind := let x := amt * i.sh / o; { i with cash := i.cash + x, pend := i.pend + x }
      let xp := amt * s.pSh / o
      some { s with cash := s.cash - amt, a := give s.a, k := give s.k, s := give s.s,
                    pCash := s.pCash + xp, pPend := s.pPend + xp }
    else none
  | .sellAsset => if s.alive ∧ s.aFmv > 0 then some (sellAssetStep s) else none
  | .liquidate =>
    -- §336(a): gain as if the asset were sold at value; the year's other distributions are settled against the
    -- year's earnings including that gain (§316(a)(2)); §331(a): what each shareholder receives is payment for the stock
    let o := outSh s
    if s.alive ∧ o > 0 ∧ (s.pSh = 0 ∨ s.pSh * 100 / o < 80) then
      let s1 := if s.aFmv > 0 then sellAssetStep s else s
      (settleC cfg s1).bind fun s2 =>
        let one (i : Ind) : Ind × Nat :=
          let (j, t) := exchGain cfg s2.age i (s2.cash * i.sh / o) i.basis
          ({ j with sh := 0, basis := 0 }, t)
        let (a, ta) := one s2.a
        let (k, tk) := one s2.k
        let (ss, ts) := one s2.s
        let xp := s2.cash * s2.pSh / o
        let gp := xp - s2.pBasisC
        let tp := bp gp rCorp
        some { s2 with alive := false, cash := 0, a := a, k := k, s := ss, oSh := 0, pSh := 0, pBasisC := 0,
                       pCash := s2.pCash + xp - tp, pCurEP := s2.pCurEP + gp - tp, tax := s2.tax + ta + tk + ts + tp }
    else none
  | .redeem h f =>
    let i := getI s h
    let o := outSh s
    let n := i.sh / f
    if s.alive ∧ f > 0 ∧ n > 0 ∧ i.sh % f = 0 ∧ n < o then
      let price := n * (s.cash + s.aFmv) / o
      if price > s.cash ∨ price = 0 then none else
      -- §1202(c)(3)(A): a purchase by the corporation from the taxpayer or a related person (§267(b): family includes
      -- siblings, §267(c)(4)) within 2 years after issue disqualifies the stock; all holders here are related
      let s := if s.age < 2 then { s with a := { s.a with q := false }, k := { s.k with q := false }, s := { s.s with q := false } } else s
      let i := getI s h
      let before := constructive s h
      let after := before - n
      let oAfter := o - n
      -- §302(c)(2): family attribution waived on a complete termination, unless stock moved between the related
      -- persons within 10 years (§302(c)(2)(B)); attribution from P (§318(a)(2)(C)) cannot be waived
      let waiver := match h with
        | .A => s.pSh == 0 && !s.gaveK
        | .K => !s.gaveK
        | .S => true
      let complete := i.sh == n && (after == 0 || waiver)                                  -- §302(b)(3)
      let disprop := decide (after * 2 < oAfter) && decide (after * o * 5 < before * oAfter * 4)          -- §302(b)(2)(B), (C)
      if complete || disprop then
        let bPart := i.basis * n / i.sh
        let (j, t) := exchGain cfg s.age i price bPart
        let j := { j with sh := i.sh - n, basis := i.basis - bPart }
        -- §312(n)(7): earnings and profits fall by no more than the redeemed stock's ratable share; §1368(e)(1)(B)
        let ep := min (price : Int) (s.accEP.toNat * n / o : Nat)
        let aa := if s.isS then (s.aaa.toNat * n / o : Nat) else 0
        some (setI { s with cash := s.cash - price, accEP := s.accEP - ep, aaa := s.aaa - aa, tax := s.tax + t } h j)
      else
        -- §302(d): a §301 distribution; the basis of the redeemed shares stays with the holder's other shares
        let j := { i with sh := i.sh - n, cash := i.cash + price, pend := i.pend + price,
                          basis := if i.sh = n then 0 else i.basis }
        some (setI { s with cash := s.cash - price } h j)
    else none
  | .sellOut h f =>
    let i := getI s h
    let o := outSh s
    let n := i.sh / f
    if s.alive ∧ f > 0 ∧ n > 0 ∧ i.sh % f = 0 then
      let price := n * (s.cash + s.aFmv) / o
      let bPart := i.basis * n / i.sh
      -- an S corporation's stock is not qualified small business stock (§1202(c)(1), (2)(A)): `q` is already false
      let (j, t) := exchGain cfg s.age i price bPart
      some (setI { s with oSh := s.oSh + n, tax := s.tax + t } h { j with sh := i.sh - n, basis := i.basis - bPart })
    else none
  | .pSellOut =>
    let o := outSh s
    if s.alive ∧ s.pAlive ∧ s.pSh > 0 then
      let price := s.pSh * (s.cash + s.aFmv) / o
      let g := price - s.pBasisC
      let t := bp g rCorp           -- §1202(a)(1): "a taxpayer other than a corporation"
      some { s with oSh := s.oSh + s.pSh, pSh := 0, pBasisC := 0, pCash := s.pCash + price - t,
                    pCurEP := s.pCurEP + g - t, tax := s.tax + t }
    else none
  | .gift to f =>
    let n := s.a.sh / f
    if s.alive ∧ to != .A ∧ f > 0 ∧ n > 0 ∧ s.a.sh % f = 0 then
      let bPart := s.a.basis * n / s.a.sh
      let d := getI s to
      let d := { d with sh := d.sh + n, basis := d.basis + bPart, q := if d.sh = 0 then s.a.q else d.q && s.a.q }
      let s1 := setI s to d
      some { s1 with a := { s.a with sh := s.a.sh - n, basis := s.a.basis - bPart },
                     gaveK := s.gaveK || to == .K }
    else none
  | .contribP f =>
    let n := s.a.sh / f
    -- §351(a): A controls P; §358(a)(1): A's P stock takes the basis of the C stock; §362(a): so does P's C stock.
    -- §1361(b)(1)(B): a corporation may not hold S corporation stock
    if s.alive ∧ s.pAlive ∧ !s.isS ∧ !s.sPending ∧ f > 0 ∧ n > 0 ∧ s.a.sh % f = 0 then
      let bPart := s.a.basis * n / s.a.sh
      some { s with a := { s.a with sh := s.a.sh - n, basis := s.a.basis - bPart },
                    pSh := s.pSh + n, pBasisC := s.pBasisC + bPart, pBasisA := s.pBasisA + bPart, pAffil := false }
    else none
  | .pDistribute amt =>
    if s.pAlive ∧ 0 < amt ∧ amt ≤ s.pCash then
      some { s with pCash := s.pCash - amt, pDist := s.pDist + amt, a := { s.a with cash := s.a.cash + amt } }
    else none
  | .pLiquidate =>
    if s.pAlive ∧ s.pSh = 0 ∧ s.pPend = 0 ∧ s.pDivYr = 0 ∧ s.pDist = 0 ∧ s.pCurEP = 0 then
      let g := s.pCash - s.pBasisA
      let t := bp g rLT
      some { s with pAlive := false, pCash := 0, pBasisA := 0, a := { s.a with cash := s.a.cash + s.pCash - t },
                    tax := s.tax + t }
    else none
  | .electS =>
    if s.alive ∧ !s.isS ∧ !s.sPending ∧ s.pSh = 0 then some { s with sPending := true } else none
  | .wait n =>
    if n > 0 ∧ s.year + n ≤ cfg.maxYears then
      (settle cfg s).map fun s =>
        let roll (i : Ind) : Ind := { i with usedPrior := i.usedPrior + i.takenYr, gainYr := 0, basisYr := 0, takenYr := 0 }
        let s := { s with a := roll s.a, k := roll s.k, s := roll s.s, age := s.age + n, year := s.year + n,
                          sYears := if s.isS then s.sYears + n else 0,
                          pAffil := s.alive && outSh s > 0 && s.pSh * 100 / outSh s ≥ 80 }
        if s.sPending then
          -- §1374(d)(1): net unrealized built-in gain at the start of the first S year; §1202(c)(2)(A): the stock
          -- stops being qualified small business stock once the corporation is not a C corporation
          { s with isS := true, sPending := false, sYears := n - 1, nubig := s.aFmv - s.aBasis, aaa := 0,
                   accEP := s.accEP, a := { s.a with q := false }, k := { s.k with q := false }, s := { s.s with q := false } }
        else s
    else none

/-! ## Part 2. Search -/

def nm : Who → String | .A => "A" | .K => "K" | .S => "S"

def kind : Move → String
  | .dividend _ => "dividend" | .sellAsset => "sellAsset" | .liquidate => "liquidate"
  | .redeem h _ => s!"redeem-{nm h}" | .sellOut _ _ => "sellStock" | .pSellOut => "P-sellStock"
  | .gift t _ => s!"gift-{nm t}" | .contribP _ => "contribP" | .pDistribute _ => "P-distribute"
  | .pLiquidate => "P-liquidate" | .electS => "electS" | .wait _ => "wait"

def showMove : Move → String
  | .dividend a => s!"C pays dividend {a}"
  | .sellAsset => "C sells asset"
  | .liquidate => "C liquidates"
  | .redeem h f => s!"C redeems 1/{f} of {nm h}'s shares"
  | .sellOut h f => s!"{nm h} sells 1/{f} of shares to outsider"
  | .pSellOut => "P sells its C shares to outsider"
  | .gift t f => s!"A gives 1/{f} of shares to {nm t}"
  | .contribP f => s!"A contributes 1/{f} of C shares to P (§351)"
  | .pDistribute a => s!"P distributes {a} to A"
  | .pLiquidate => "P liquidates"
  | .electS => "C elects S"
  | .wait n => s!"wait {n}y"

def moves (s : St) : List Move :=
  let divs := ([s.cash, s.accEP.toNat].filter (fun x => x > 0 ∧ x ≤ s.cash)).eraseDups.map Move.dividend
  let pd := ([s.pCash, 250].filter (fun x => x > 0 ∧ x ≤ s.pCash)).eraseDups.map Move.pDistribute
  let fr := [1, 2, 4]
  divs ++ pd ++ [.sellAsset, .liquidate, .pSellOut, .pLiquidate, .electS, .wait 1, .wait 2, .wait 5]
    ++ fr.flatMap (fun f => [Move.redeem .A f, .redeem .K f, .redeem .S f, .sellOut .A f, .sellOut .K f, .sellOut .S f,
                             .gift .K f, .gift .S f, .contribP f])

structure Result where
  fam : Int
  aOnly : Int
  tax : Nat
  path : List Move

/-- Money in the family's hands after every tax, once the year is closed. `full`: only positions where nothing is left
in C for the family (liquidated or sold) and nothing is left in P. -/
def evaluate (cfg : Cfg) (full : Bool) (s : St) : Option (Int × Int × Nat) :=
  match settle cfg s with
  | none => none
  | some e =>
    let exited := !e.alive ∨ (e.a.sh + e.k.sh + e.s.sh + e.pSh = 0) ∨ (e.cash = 0 ∧ e.aFmv = 0)
    if full ∧ !(exited ∧ (e.pCash = 0 ∨ !e.pAlive)) then none
    else some (e.a.cash + e.k.cash + e.s.cash, e.a.cash, e.tax)

def insertSorted (x : String) : List String → List String
  | [] => [x]
  | y :: ys => if x < y then x :: y :: ys else if x == y then y :: ys else y :: insertSorted x ys

def signature (p : List Move) : String :=
  " + ".intercalate ((p.map kind).filter (· != "wait") |>.foldl (fun acc x => insertSorted x acc) [])

def search (label : String) (cfg : Cfg) (depth : Nat) (s0 : St) (full : Bool) (allowed : Move → Bool)
    (baseline : List Move) (top : Nat := 8) (famGoal : Bool := true) : IO Unit := do
  let mut frontier : Array (St × List Move) := #[(s0, [])]
  let mut seen : Std.HashSet St := {}
  seen := seen.insert s0
  let mut best : Std.HashMap String Result := {}
  let mut steps := 0
  for _ in [0:depth] do
    let mut next : Array (St × List Move) := #[]
    for (s, path) in frontier do
      -- nothing further to do once the family holds nothing in C and P is empty
      let finished := (!s.alive || s.a.sh + s.k.sh + s.s.sh + s.pSh == 0) && (s.pCash == 0 || !s.pAlive)
      for m in (if finished then [] else moves s) do
        if allowed m then
          match step cfg s m with
          | none => pure ()
          | some s' =>
            steps := steps + 1
            if !seen.contains s' then
              seen := seen.insert s'
              let p := m :: path
              next := next.push (s', p)
              match evaluate cfg full s' with
              | none => pure ()
              | some (fam, ao, tx) =>
                let sig := signature p
                let sc := if famGoal then fam else ao
                let better := match best[sig]? with
                  | none => true
                  | some r => sc > (if famGoal then r.fam else r.aOnly)
                if better then best := best.insert sig ⟨fam, ao, tx, p.reverse⟩
    frontier := next
  let bl := baseline.foldl (fun (o : Option St) m => o.bind (fun s => step cfg s m)) (some s0)
  let blv := (bl.bind (evaluate cfg full)).getD (0, 0, 0)
  let blScore := if famGoal then blv.1 else blv.2.1
  IO.println s!"== {label}: {seen.size} positions, {steps} moves tried, {best.size} move families"
  IO.println s!"   baseline (plain): family {blv.1}, A {blv.2.1}, total tax {blv.2.2}"
  let sorted := best.toArray.qsort (fun x y => (if famGoal then x.2.fam > y.2.fam else x.2.aOnly > y.2.aOnly))
  let mut shown := 0
  for (sig, r) in sorted do
    let sc := if famGoal then r.fam else r.aOnly
    -- show a family only if no family using a subset of its moves does at least as well
    let ks := sig.splitOn " + "
    let dominated := sorted.any fun (sig2, r2) =>
      sig2 != sig && (sig2.splitOn " + ").all (ks.contains ·) && (sig2.splitOn " + ").length < ks.length &&
        (if famGoal then r2.fam else r2.aOnly) ≥ sc
    if shown < top ∧ sc > blScore + 5 ∧ !dominated then
      shown := shown + 1
      IO.println s!"   +{sc - blScore}  family {r.fam}, A {r.aOnly}, tax {r.tax}  [{sig}]"
      IO.println s!"        {"; ".intercalate (r.path.map showMove)}"
  if shown = 0 then IO.println "   nothing beats the baseline"

def ind0 : Ind := ⟨0, 0, 0, false, 0, 0, 0, 0, 0⟩

/-- C: 10,000 cash from retained earnings, an asset worth 30,000 with no basis; A holds all 400 shares, basis 1,000.
P: no assets; `pEP` its accumulated earnings and profits and `pBasis` A's basis in it. -/
def start (q : Bool) (age : Nat) (accEP : Int) (pEP : Int) (pBasis : Nat) : St :=
  { alive := true, cash := 10000, aFmv := 30000, aBasis := 0, accEP := accEP, curEP := 0, isS := false,
    sPending := false, sYears := 0, nubig := 0, aaa := 0, age := age, year := 0,
    a := { ind0 with sh := 400, basis := 1000, q := q }, k := ind0, s := ind0, oSh := 0, gaveK := false,
    pSh := 0, pBasisC := 0, pPend := 0, pAffil := false, pAlive := true, pCash := 0, pAccEP := pEP, pCurEP := 0,
    pDivYr := 0, pRegTaxYr := 0, pDist := 0, pBasisA := pBasis, tax := 0 }

def cfg0 : Cfg := { post2025 := false, pPHC := false, c3Qsbs := false, aetLiteral := false, maxYears := 6 }

def keepBusiness : Move → Bool
  | .sellAsset | .liquidate | .sellOut _ _ | .pSellOut => false
  | _ => true

end Legal.USTax.Hunt.Corporate

namespace Legal.USTax.Hunt.Corporate
def plain : List Move := [.sellAsset, .dividend 33700]
def all : Move → Bool := fun _ => true
#eval do
  let s := start false 10 10000 (-8000) 8000
  search "D1 P deficit 8000, not PHC, AET min credit 250, keep business" cfg0 5 s false keepBusiness [.dividend 10000]
  search "D2 same, AET credit counts deficit (literal)" { cfg0 with aetLiteral := true } 5 s false keepBusiness [.dividend 10000]
  search "D3 same, P is a PHC" { cfg0 with pPHC := true } 5 s false keepBusiness [.dividend 10000]
  search "D4 P no deficit (E&P 0, basis 8000), literal" { cfg0 with aetLiteral := true } 5 (start false 10 10000 0 8000) false keepBusiness [.dividend 10000]
  search "D5 deficit, stock 1 year old (§1059), literal" { cfg0 with aetLiteral := true } 5 (start false 1 10000 (-8000) 8000) false keepBusiness [.dividend 10000]
end Legal.USTax.Hunt.Corporate
