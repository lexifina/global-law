import Std
/-!
# Charitable giving: what each provision permits and what it taxes (taxable years 2026-2028)

A married couple filing jointly, both over 73, over three taxable years. They hold cash, publicly traded stock held
more than a year (one lot, fixed basis fraction), a traditional IRA with a required minimum distribution, and in one
profile a wholly owned C corporation. The rules part says what each provision allows and what it costs. It names no
technique.

Figures: 2026 (Rev. Proc. 2025-32) used for all three years, no indexing: joint brackets, standard deduction $32,200
plus 2 x $1,650 (§63(c),(f)), §1(h) breakpoints $98,900 / $613,700, QCD limit $111,000 (§408(d)(8)(G)), §1411
threshold $250,000; trusts: 37% bracket from $16,000, §1(h) breakpoints $3,300 / $16,250; §11 rate 21%. The §7520
rate is taken as 0, to match the no-growth world of the model (at a positive rate a remainder is worth less and
the deduction for it is smaller).

Simplifications: no growth and no yield on any asset; other itemized deductions are a fixed parameter; carryovers
never expire inside the 3-year horizon (§170(d)(1) gives 5 years); a carryover is used up in a year the couple does
not itemize as if they had itemized (Reg. §1.170A-10(a)(2), the conservative reading); the §25F credit is taken as
$1,700 per joint return (conservative: the text says "any taxpayer") plus $1,700 for each other family taxpayer.
-/
namespace Legal.USTax.Hunt.Charity

/-! ## Part 1. Rules -/

structure P where
  ord : Nat        -- ordinary income each year other than IRA distributions
  rmd : Nat        -- §401(a)(9) / §408(a)(6) required distribution each year
  other : Nat      -- itemized deductions other than charity
  basisPct : Nat   -- basis of the stock as a percent of value
  target : Nat     -- total that must reach charity over the three years
  kids : Nat       -- other individual taxpayers in the family with at least $1,700 of tax each
  corpTI : Nat     -- taxable income of a wholly owned C corporation each year (0 = none)
  latPm : Nat      -- per-mille tax the family would pay on gain or dividends when realized (valuation only)
  iraPm : Nat      -- per-mille tax the family would pay on IRA money when withdrawn (valuation only)
  deriving Repr

def stdDed : Nat := 32200 + 3300
def qcdCap : Nat := 111000
def top37 : Nat := 768700

/-- §1(j) as amended, joint return, 2026. -/
def ordTax (ti : Nat) : Nat :=
  let br : List (Nat × Nat × Nat) :=
    [(0, 24800, 10), (24800, 100800, 12), (100800, 211400, 22), (211400, 403550, 24), (403550, 512450, 32),
     (512450, 768700, 35), (768700, 1000000000, 37)]
  br.foldl (fun acc (lo, hi, r) => acc + (min ti hi - min ti lo) * r / 100) 0

/-- §1(h): net capital gain stacked on top of ordinary taxable income, 0 / 15 / 20 percent. -/
def incomeTax (ti gain : Nat) : Nat :=
  let g := min gain ti
  let o := ti - g
  let z := min ti 98900 - min o 98900
  let t20 := ti - max o (min ti 613700)
  ordTax o + (g - z - t20) * 15 / 100 + t20 * 20 / 100

structure S where
  yr : Nat
  cash : Nat
  stock : Nat
  ira : Nat
  gCash : Nat   -- cash this year to §170(b)(1)(A) organizations other than donor advised funds
  gDaf : Nat    -- cash this year to a donor advised fund (§4966(d)(2)) of a public charity sponsor
  bCash : Nat   -- cash this year to a private non-operating foundation (§170(b)(1)(B))
  cStk : Nat    -- stock this year to §170(b)(1)(A) organizations incl. DAF sponsors (§170(b)(1)(C))
  dStk : Nat    -- stock this year to a private non-operating foundation (§170(b)(1)(D), §170(e)(5))
  sgo : Nat     -- cash this year to scholarship granting organizations (§25F)
  qcd : Nat     -- qualified charitable distributions this year (§408(d)(8))
  sold : Nat    -- stock sold this year (value)
  coG : Nat
  coB : Nat
  coC : Nat
  coD : Nat
  given : Nat
  tax : Nat
  tStock : Nat   -- stock held by an irrevocable trust for the children that is not a grantor trust (§§671-677)
  tCash : Nat
  tGain : Nat    -- the trust's gross income this year (gain on sales)
  tPaid : Nat    -- paid this year from that gross income to charity under the instrument (§642(c)(1))
  crtPay : Nat   -- annuity amount of a charitable remainder annuity trust (§664(d)(1))
  crtLeft : Nat  -- annuity payments still to come
  crtGain : Nat  -- that trust's undistributed capital gain (§664(b)(2))
  corp : Nat     -- cash inside the corporation
  corpGift : Nat
  corpCo : Nat
  sgoIra : Nat   -- paid this year by the IRA trustee straight to a scholarship granting organization
  deriving BEq, Hashable, Repr

inductive Mv where
  | cashPC (a : Nat)   -- §170(a), (b)(1)(G)
  | cashDAF (a : Nat)  -- §170(f)(18), (b)(1)(G)
  | cashPF (a : Nat)   -- §170(b)(1)(B)
  | stockPC (a : Nat)  -- §170(e)(1): long-term gain property, no reduction; (b)(1)(C)
  | stockPF (a : Nat)  -- §170(e)(1)(B)(ii), (e)(5): qualified appreciated stock at value; (b)(1)(D)
  | sgo (a : Nat)      -- §25F (taxable years ending after 2026)
  | qcd (a : Nat)      -- §408(d)(8)
  | sell (a : Nat)     -- §1001
  | fundTrust (a : Nat)  -- gift of stock to the children's trust: §2501, within §2505; basis carries over, §1015
  | trustSell (a : Nat)  -- the trust sells: §1001, taxed to the trust, §641
  | trustPay (a : Nat)   -- the trust pays gross income to charity as its instrument directs: §642(c)(1)
  | fundCrat5 (a : Nat)  -- stock to a 2-year annuity trust paying the couple 5% a year, remainder to charity: §664(d)(1)
  | fundCrat45 (a : Nat) -- the same paying 45% a year (remainder 10%, the least §664(d)(1)(D) allows)
  | corpCash (a : Nat)   -- the corporation gives cash: §170(b)(2)
  | iraSgo (a : Nat)     -- the IRA trustee pays a scholarship granting organization direct: §408(d)(8), §25F
  | close              -- end the taxable year: file the returns
  deriving BEq, Hashable, Repr

/-- The couple's return. Returns (tax, carryovers G B C D). -/
def settle (p : P) (s : S) : Nat × Nat × Nat × Nat × Nat :=
  -- An IRA payment to a scholarship granting organization for which the §25F credit is allowed is "not taken into
  -- account as a charitable contribution for purposes of section 170" (§25F(e)); so a §170 deduction "for the entire
  -- distribution" is not allowable and none of it is a QCD (§408(d)(8)(C)): all of it is income. What exceeds the
  -- credit is an ordinary cash gift.
  let cap := if s.yr ≥ 1 then 1700 * (1 + p.kids) else 0
  let sx := s.sgo + s.sgoIra - min cap (s.sgo + s.sgoIra)
  let forced := p.rmd - min p.rmd (s.qcd + s.sgoIra)    -- §408(d)(8): a QCD counts toward the RMD and is excluded
  let gain := s.sold * (100 - p.basisPct) / 100
           + (if s.crtLeft > 0 then min s.crtPay s.crtGain else 0)   -- §664(b)(2): annuity is gain first, then corpus
  let b := p.ord + forced + s.sgoIra + gain                        -- §170(b)(1)(H): contribution base = AGI
  let gT := s.gCash + s.gDaf + sx + s.coG
  let cT := s.cStk + s.coC
  let bT := s.bCash + s.coB
  let dT := s.dStk + s.coD
  let gA := min gT (60 * b / 100)                       -- (G)(i)
  let aLim := 50 * b / 100 - gA                         -- (A), reduced by (G)(iii)(II)
  let aNoC := min cT aLim
  let cA := min (min cT (30 * b / 100)) aLim            -- (C)(i)
  let bLim := min (30 * b / 100) (50 * b / 100 - (aNoC + gA - min gA (10 * b / 100)))  -- (B)(i),(ii)
  let bA := min bT bLim
  let dLim := min (20 * b / 100) (30 * b / 100 - cT)    -- (D)(i)
  let dA := min dT (min dLim (bLim - bA))
  let f := b / 200                                      -- (I): 0.5 percent floor, absorbed D, C, B, (A), G
  let dF := min f dA
  let cF := min (f - dF) cA
  let bF := min (f - dF - cF) bA
  let gF := min (f - dF - cF - bF) gA
  -- §170(d)(1)(C): the floor amount is carried only from a year "from which an excess is carried forward"; read
  -- narrowly: this year's own gifts (used before carryovers) exceed a limit
  let anyX := s.gCash + s.gDaf + sx > gA || s.cStk > cA || s.bCash > bA || s.dStk > dA
  let add (x : Nat) := if anyX then x else 0
  let char := (gA - gF) + (cA - cF) + (bA - bF) + (dA - dF)
  -- itemize (§63(e)), with §68
  let item := p.other + char
  let ti0 := b - item
  let red := 2 * (min item (ti0 + item - top37)) / 37
  let tiI := b - (item - red)
  -- or not: §63(b)(4), §170(p): up to $2,000 of this year's cash to (b)(1)(A) organizations, not DAF
  let pd := min 2000 (min s.gCash (60 * b / 100))
  let tiS := b - stdDed - pd
  let ti := min tiI tiS
  let niit := 38 * (min gain (b - 250000)) / 1000       -- §1411
  let credit := min cap (s.sgo + s.sgoIra)              -- §25F(a),(b)(1): per taxpayer; nonrefundable
  let pre := incomeTax ti gain
  (pre - min pre credit + niit, gT - gA + add gF, bT - bA + add bF, cT - cA + add cF, dT - dA + add dF)

/-- The children's trust's return (§641(b): computed as for an individual). Its income here is long-term gain. The
§642(c) deduction is an itemized deduction (§63(d), §67(b)(4); §67(e) does not move it above the line), so §68 as
rewritten in 2025, which no longer excepts estates and trusts, is applied to it: the conservative reading. -/
def trustTax (s : S) : Nat :=
  let inc := s.tGain - 100                                  -- §642(b)(2)(B)
  let red := 2 * (min s.tPaid (inc - 16000)) / 37           -- §68
  let ti := inc - (s.tPaid - red)
  let z := min ti 3300
  let t20 := ti - min ti 16250
  (ti - z - t20) * 15 / 100 + t20 * 20 / 100
    + 38 * (min (s.tGain - s.tPaid) (inc - 16000)) / 1000    -- §1411(a)(2)

/-- The corporation's return: §170(b)(2)(A) allows what is over 1% and not over 10% of taxable income; §170(d)(2)
carries the part over 10%, and the 1% only from a year that is over 10%. Returns (tax saved at 21%, carryover). -/
def corpSettle (p : P) (s : S) : Nat × Nat :=
  let k := p.corpTI
  let tot := s.corpGift + s.corpCo
  let ded := min tot (k / 10) - min tot (k / 100)
  let over := s.corpGift > k / 10
  (21 * ded / 100, tot - min tot (k / 10) + (if over then min tot (k / 100) else 0))

/-- §664(d)(1): a term-of-years annuity trust, two annual payments of `pct` percent of the initial value, made at
each year end; the trust sells at once and pays no tax (§664(c)(1)). §170(f)(2)(A): the remainder is deductible, as
capital gain property given to a public charity. The remainder is counted as reaching charity when irrevocably set
aside for it. -/
def fundCrat (p : P) (s : S) (a pct : Nat) : Option S :=
  let rem := a - 2 * (pct * a / 100)
  if 0 < a ∧ a ≤ s.stock ∧ s.crtLeft = 0 ∧ s.crtPay = 0 ∧ s.yr ≤ 1 ∧ 5 ≤ pct ∧ pct ≤ 50 ∧ 10 * rem ≥ a then
    some { s with stock := s.stock - a, crtPay := pct * a / 100, crtLeft := 2,
                  crtGain := a * (100 - p.basisPct) / 100, cStk := s.cStk + rem, given := s.given + rem }
  else none

def step (p : P) (s : S) : Mv → Option S
  | .cashPC a => if 0 < a ∧ a ≤ s.cash then some { s with cash := s.cash - a, gCash := s.gCash + a, given := s.given + a } else none
  | .cashDAF a => if 0 < a ∧ a ≤ s.cash then some { s with cash := s.cash - a, gDaf := s.gDaf + a, given := s.given + a } else none
  | .cashPF a => if 0 < a ∧ a ≤ s.cash then some { s with cash := s.cash - a, bCash := s.bCash + a, given := s.given + a } else none
  | .stockPC a => if 0 < a ∧ a ≤ s.stock then some { s with stock := s.stock - a, cStk := s.cStk + a, given := s.given + a } else none
  | .stockPF a => if 0 < a ∧ a ≤ s.stock then some { s with stock := s.stock - a, dStk := s.dStk + a, given := s.given + a } else none
  | .sgo a => if 0 < a ∧ a ≤ s.cash ∧ s.yr ≥ 1 ∧ s.sgo + a ≤ 1700 * (1 + p.kids) then some { s with cash := s.cash - a, sgo := s.sgo + a, given := s.given + a } else none
  | .qcd a => if 0 < a ∧ a ≤ s.ira ∧ s.qcd + a ≤ qcdCap then some { s with ira := s.ira - a, qcd := s.qcd + a, given := s.given + a } else none
  | .sell a => if 0 < a ∧ a ≤ s.stock then some { s with stock := s.stock - a, cash := s.cash + a, sold := s.sold + a } else none
  | .fundTrust a => if 0 < a ∧ a ≤ s.stock then some { s with stock := s.stock - a, tStock := s.tStock + a } else none
  | .trustSell a => if 0 < a ∧ a ≤ s.tStock then
      some { s with tStock := s.tStock - a, tCash := s.tCash + a, tGain := s.tGain + a * (100 - p.basisPct) / 100 } else none
  | .trustPay a => if 0 < a ∧ s.tPaid + a ≤ s.tGain ∧ a ≤ s.tCash then
      some { s with tCash := s.tCash - a, tPaid := s.tPaid + a, given := s.given + a } else none
  | .fundCrat5 a => fundCrat p s a 5
  | .fundCrat45 a => fundCrat p s a 45
  | .corpCash a => if 0 < a ∧ a ≤ s.corp ∧ p.corpTI > 0 then
      some { s with corp := s.corp - a, corpGift := s.corpGift + a, given := s.given + a } else none
  | .iraSgo a => if 0 < a ∧ a ≤ s.ira ∧ s.yr ≥ 1 ∧ s.qcd + s.sgoIra + a ≤ qcdCap then
      some { s with ira := s.ira - a, sgoIra := s.sgoIra + a, given := s.given + a } else none
  | .close =>
    if s.yr ≥ 3 then none else
    let (t, g, b, c, d) := settle p s
    let forced := p.rmd - min p.rmd (s.qcd + s.sgoIra)
    let f := min forced s.ira
    let tt := trustTax s
    let (cSave, cCo) := corpSettle p s
    let pay := if s.crtLeft > 0 then s.crtPay else 0
    if tt > s.tCash then none else
    some { s with yr := s.yr + 1, cash := s.cash + f + pay - t, ira := s.ira - f, tax := s.tax + t + tt,
                  gCash := 0, gDaf := 0, bCash := 0, cStk := 0, dStk := 0, sgo := 0, qcd := 0, sold := 0,
                  coG := g, coB := b, coC := c, coD := d,
                  tCash := s.tCash - tt, tGain := 0, tPaid := 0,
                  crtLeft := s.crtLeft - 1, crtGain := s.crtGain - min pay s.crtGain,
                  crtPay := if s.crtLeft ≤ 1 then 0 else s.crtPay,
                  corp := s.corp + cSave, corpGift := 0, corpCo := cCo, sgoIra := 0 }

/-! ## Part 2. Search -/

def nChan : Nat := 15
def chan : Mv → Nat
  | .cashPC _ => 0 | .cashDAF _ => 1 | .cashPF _ => 2 | .stockPC _ => 3 | .stockPF _ => 4 | .sgo _ => 5 | .qcd _ => 6
  | .sell _ => 7 | .fundTrust _ => 8 | .trustSell _ => 9 | .trustPay _ => 10 | .fundCrat5 _ => 11 | .fundCrat45 _ => 12
  | .corpCash _ => 13 | .iraSgo _ => 14 | .close => 15
def chanName : Nat → String
  | 0 => "cashPC" | 1 => "cashDAF" | 2 => "cashPF" | 3 => "stockPC" | 4 => "stockPF" | 5 => "SGO" | 6 => "QCD"
  | 7 => "sell" | 8 => "fundTrust" | 9 => "trustSell" | 10 => "trustPay" | 11 => "CRAT5" | 12 => "CRAT45"
  | 13 => "corpCash" | 14 => "IRA->SGO" | _ => "close"
def mk (c a : Nat) : Mv := match c with
  | 0 => .cashPC a | 1 => .cashDAF a | 2 => .cashPF a | 3 => .stockPC a | 4 => .stockPF a | 5 => .sgo a | 6 => .qcd a
  | 7 => .sell a | 8 => .fundTrust a | 9 => .trustSell a | 10 => .trustPay a | 11 => .fundCrat5 a | 12 => .fundCrat45 a
  | 13 => .corpCash a | _ => .iraSgo a
def amt : Mv → Nat
  | .cashPC a | .cashDAF a | .cashPF a | .stockPC a | .stockPF a | .sgo a | .qcd a | .sell a => a
  | .fundTrust a | .trustSell a | .trustPay a | .fundCrat5 a | .fundCrat45 a | .corpCash a | .iraSgo a => a
  | .close => 0
def showMv (m : Mv) : String := if m == .close then "|" else s!"{chanName (chan m)} {amt m}"

/-- Natural amounts for a channel: fractions of the target, what is left of the target, each statutory cap, and the
percentage limits applied to the couple's ordinary base. -/
def amounts (p : P) (div : Nat) (s : S) (c : Nat) : List Nat :=
  let u := p.target / div
  let rem := p.target - s.given
  let b0 := p.ord + p.rmd
  let base := [u, 2 * u, 3 * u, p.target, rem, 30 * b0 / 100]
  let g := 100 - p.basisPct
  let free := c == 7 || c == 8 || c == 9 || c == 11 || c == 12
  let l := match c with
    | 0 => 2000 :: base
    | 5 => [1700, 1700 * (1 + p.kids)]
    | 6 => p.rmd :: qcdCap :: base
    | 7 => [u, p.target]
    | 8 => [rem * 100 / g, p.target / 3 * 100 / g]            -- stock whose gain is what is left / a third of the target
    | 9 => [s.tStock]
    | 10 => [min rem (s.tGain - s.tPaid)]
    | 11 => [rem * 100 / 90, u * 100 / 90]                    -- remainder 90%
    | 12 => [rem * 10, u * 10]                                -- remainder 10%
    | 13 => [u, rem, p.corpTI / 10, p.corpTI / 100]
    | 14 => [1700, u]
    | _ => base
  (l.filter (fun a => 0 < a ∧ (free || a ≤ rem))).eraseDups

/-- End wealth of the family (couple, children's trust, corporation) if everything were turned to cash. -/
def wealth (p : P) (s : S) : Nat :=
  let st := s.stock + s.tStock
  s.cash + s.tCash + st - st * (100 - p.basisPct) / 100 * p.latPm / 1000 + s.ira * (1000 - p.iraPm) / 1000
    + s.corp * (1000 - p.latPm) / 1000

abbrev Path := List Mv

/-- Families of plans, by kind of move: results are reported as the best plan in each family. -/
def grp : Nat → Nat
  | 0 | 1 | 2 => 0 | 3 | 4 => 1 | 5 => 2 | 6 => 3 | 7 => 4 | 8 | 9 | 10 => 5 | 11 | 12 => 6 | 13 => 7 | _ => 8
def grpName : Nat → String
  | 0 => "cash gift" | 1 => "stock gift" | 2 => "SGO" | 3 => "QCD" | 4 => "sell" | 5 => "children's trust"
  | 6 => "CRAT" | 7 => "corporate gift" | _ => "IRA->SGO"

/-- All year-end positions reachable from `s` using each channel at most once, in channel order (gifts commute). -/
partial def yearPlans (p : P) (div : Nat) (allowed : Nat → Bool) (c : Nat) (s : S) (path : Path) (fam : Nat)
    (acc : Array (S × Path × Nat)) : Array (S × Path × Nat) :=
  if c ≥ nChan then acc.push (s, path, fam) else
  let acc := yearPlans p div allowed (c + 1) s path fam acc
  if !allowed c then acc else
  (amounts p div s c).foldl (fun acc a =>
    match step p s (mk c a) with
    | some s' => yearPlans p div allowed (c + 1) s' (mk c a :: path) (fam ||| (1 <<< grp c)) acc
    | none => acc) acc

def famName (f : Nat) : String :=
  " + ".intercalate ((List.range 9).filter (fun c => f &&& (1 <<< c) != 0) |>.map grpName)

def run (label : String) (p : P) (s0 : S) (allowed : Nat → Bool) (div : Nat := 3) (topN : Nat := 10) : IO Unit := do
  IO.println s!"== {label} =="
  let t0 ← IO.monoMsNow
  -- baseline: a third of the target in cash to a public charity each year
  let u := p.target / 3
  let mut bs := s0
  for _ in [0:3] do
    bs := ((step p bs (.cashPC u)).bind (step p · .close)).getD bs
  IO.println s!"baseline (cash {u} a year): tax {bs.tax}, end wealth {wealth p bs}"
  -- positions keyed by (position without cash and tax paid, family of moves used); keep the richest
  let key (s : S) (fam : Nat) : S × Nat := ({ s with cash := 0, tax := 0 }, fam)
  let mut frontier : Std.HashMap (S × Nat) (S × Path) := ({} : Std.HashMap (S × Nat) (S × Path)).insert (key s0 0) (s0, [])
  let mut explored := 0
  for y in [0:3] do
    let mut next : Std.HashMap (S × Nat) (S × Path) := {}
    for ((_, fam), (s, path)) in frontier.toList do
      for (s1, path1, fam1) in yearPlans p div allowed 0 s path fam #[] do
        explored := explored + 1
        match step p s1 .close with
        | none => pure ()
        | some s2 =>
          let k := key s2 fam1
          match next[k]? with
          | some (o, _) => if s2.cash > o.cash then next := next.insert k (s2, .close :: path1)
          | none => next := next.insert k (s2, .close :: path1)
    frontier := next
    IO.println s!"year {2026 + y}: {explored} year-plans tried, {frontier.size} positions kept"
  -- best per family among positions that delivered the target exactly and left nothing pending
  let mut fams : Std.HashMap Nat (Nat × S × Path) := {}
  for ((_, fam), (s, path)) in frontier.toList do
    if s.given == p.target ∧ s.crtLeft == 0 then
      let w := wealth p s
      match fams[fam]? with
      | some (w0, _, _) => if w > w0 then fams := fams.insert fam (w, s, path)
      | none => fams := fams.insert fam (w, s, path)
  let sorted := fams.toArray.qsort (fun a b => a.2.1 > b.2.1)
  IO.println s!"{sorted.size} families deliver exactly {p.target} ({(← IO.monoMsNow) - t0} ms); best {topN}:"
  for (fam, (w, s, path)) in sorted.toList.take topN do
    IO.println s!"  {(w : Int) - wealth p bs} vs baseline (tax {s.tax}, carry G{s.coG} B{s.coB} C{s.coC} D{s.coD} corp{s.corpCo}) [{famName fam}]"
    IO.println s!"      {", ".intercalate (path.reverse.map showMv)}"

def s0 (cash stock ira corp : Nat) : S :=
  ⟨0, cash, stock, ira, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, corp, 0, 0, 0⟩

/-- A: AGI about $200k, other itemized $20k (below the standard deduction), $36k to charity over three years. -/
def pA : P := ⟨160000, 40000, 20000, 25, 36000, 0, 0, 150, 220⟩
/-- B: AGI about $1.3M, other itemized $60k, $300k to charity over three years. -/
def pB : P := ⟨1200000, 100000, 60000, 25, 300000, 0, 0, 238, 370⟩
/-- C: AGI about $150k, large stock, $450k to charity over three years (limits bind). -/
def pC : P := ⟨100000, 50000, 20000, 25, 450000, 0, 0, 150, 220⟩

/-- D: as A but under 70 1/2: no IRA distributions, no QCD. -/
def pD : P := ⟨200000, 0, 20000, 25, 36000, 0, 0, 150, 220⟩
/-- E: as B, with two adult children who pay tax and a C corporation earning $2M a year. -/
def pE : P := ⟨1200000, 100000, 60000, 25, 300000, 2, 2000000, 238, 370⟩

/-- F: AGI $500k, gives 30% of it in each year. -/
def pF : P := ⟨450000, 50000, 30000, 25, 450000, 0, 0, 238, 350⟩

def gifts (c : Nat) : Bool := c < 7
def withTrust (c : Nat) : Bool := c < 7 || (8 ≤ c && c ≤ 10)
def withCrat (c : Nat) : Bool := c < 7 || c == 11 || c == 12
def withCorp (c : Nat) : Bool := c < 7 || c == 13
def sel (l : List Nat) (c : Nat) : Bool := l.contains c

-- Round 1: gifts, the credit, IRA distributions
#eval run "A: moderate income; gifts, SGO, QCD" pA (s0 1000000 500000 1000000 0) gifts 6
#eval run "A: + IRA paid straight to an SGO" pA (s0 1000000 500000 1000000 0) (sel [0, 3, 5, 6, 14])
#eval run "D: no IRA; gifts, SGO" pD (s0 1000000 500000 0 0) gifts 6
#eval run "B: high income; gifts, SGO, QCD" pB (s0 3000000 3000000 2500000 0) gifts 6
-- Round 2: trusts and the corporation
#eval run "D: + children's trust" pD (s0 1000000 500000 0 0) (sel [0, 3, 5, 8, 9, 10])
#eval run "B: + annuity trust" pB (s0 3000000 3000000 2500000 0) withCrat
#eval run "E: B + adult children + corporation" pE (s0 3000000 3000000 2500000 5000000) withCorp
-- The two slowest runs:
#eval run "A: + children's trust" pA (s0 1000000 500000 1000000 0) withTrust
#eval run "B: + children's trust" pB (s0 3000000 3000000 2500000 0) withTrust
-- Round 3: gifts larger than the percentage limits
#eval run "C: cash, stock to public charity, SGO, QCD" pC (s0 1000000 3000000 1250000 0) (sel [0, 3, 5, 6])
#eval run "C: stock to either, QCD" pC (s0 1000000 3000000 1250000 0) (sel [3, 4, 6])
#eval run "C: stock, QCD, children's trust" pC (s0 1000000 3000000 1250000 0) (sel [3, 6, 8, 9, 10])
#eval run "F: cash, stock to public charity, SGO, QCD" pF (s0 1000000 3000000 1250000 0) (sel [0, 3, 5, 6])
#eval run "F: stock to either, no QCD" pF (s0 1000000 3000000 1250000 0) (sel [3, 4])
#eval run "F: stock, children's trust" pF (s0 1000000 3000000 1250000 0) (sel [3, 8, 9, 10])

end Legal.USTax.Hunt.Charity
