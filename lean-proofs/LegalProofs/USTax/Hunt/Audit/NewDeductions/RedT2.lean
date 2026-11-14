import Std

/-!
# Individual deductions and caps after Pub. L. 119-21 (2025): rules, then a blind search

A married couple over two taxable years. Both years use the same law and the same figures (taxable year 2026: Rev.
Proc. 2025-32 rate tables and standard deduction; statutory amounts where the statute fixes them), so that what the
search finds is a property of the rules and not of the 2025 -> 2026 change of law.

Part 1 (rules) says what each provision allows and what it taxes. Part 2 searches every sequence of the moves.

Simplifications, each stated once:
* no children, no credits, no AMT, no net investment income tax, no capital gains (all income ordinary);
* contribution base (§170(b)(1)(H)) = adjusted gross income; all gifts are cash to public charities;
* no carryover of gifts cut by the 0.5% floor (§170(d)(1)(C) carries them only when a percentage ceiling is exceeded);
* the self-employed person has no employees and no depreciable property, so above the §199A threshold the W-2/property
  limit is zero and the deduction phases out over the §199A(b)(3)(B) range;
* self-employment tax is below the social security wage base; it is reported next to the income tax, not in it;
* on separate returns a deduction goes to the spouse who paid the item out of their own funds; State income tax
  withheld goes to the earner; car loan interest to the spouse who incurred the debt (§163(h)(4)(B)(i));
* not a community property State.
-/

namespace Legal.USTax.Hunt.NewDeductions

/-! ## Part 1. Rules -/

/-! ### Figures (taxable year 2026) -/

/-- §1(j)(2)(A) as indexed for 2026: upper edge of each bracket and the rate in percent, joint return. -/
def jointBrackets : List (Nat × Nat) :=
  [(24800, 10), (100800, 12), (211400, 22), (403550, 24), (512450, 32), (768700, 35)]
/-- §1(j)(2)(D) as indexed for 2026: married filing separately (each edge is half the joint edge). -/
def sepBrackets : List (Nat × Nat) :=
  [(12400, 10), (50400, 12), (105700, 22), (201775, 24), (256225, 32), (384350, 35)]
def topRate : Nat := 37
/-- §63(c)(2), (7): basic standard deduction, 2026. -/
def stdJoint : Nat := 32200
def stdSep : Nat := 16100
/-- §63(f)(1): additional amount for a married person aged 65, 2026. -/
def stdAged : Nat := 1650
/-- §164(b)(7)(A)(ii), (B)(ii)(II): 2026. -/
def saltCap : Nat := 40400
def saltThreshold : Nat := 505000
def saltFloor : Nat := 10000
/-- §199A(e)(2) threshold as indexed for 2026 (approximate), and the §199A(b)(3)(B) range after the 2025 Act. -/
def qbiThreshJoint : Nat := 403500
def qbiThreshSep : Nat := 201750

/-- Tax on taxable income, in cents-free whole dollars (rounded down). -/
def taxOn (brackets : List (Nat × Nat)) (ti : Nat) : Nat := Id.run do
  let mut lo := 0
  let mut t := 0
  for (hi, r) in brackets do
    if ti > lo then t := t + (min ti hi - lo) * r
    lo := hi
  if ti > lo then t := t + (ti - lo) * topRate
  return t / 100

/-! ### One return -/

/-- What goes on one return for one year. -/
structure Ret where
  joint : Bool          -- §6013 joint return; otherwise a married person's separate return
  aged : Nat            -- persons on the return aged 65 by year end
  wages : Nat           -- wages other than tips (includes the overtime premium)
  overtime : Nat        -- the part of wages that is qualified overtime compensation, §225(c)
  tipsEmp : Nat         -- qualified tips received as an employee
  tipsBiz : Nat         -- qualified tips received in the taxpayer's own trade or business (its only receipts)
  other : Nat           -- other ordinary income
  wagerGain : Nat
  wagerLoss : Nat
  salt : Nat            -- State and local taxes paid
  mortgage : Nat        -- qualified residence interest paid
  gifts : Nat           -- cash gifts to public charities
  carInt : Nat          -- qualified passenger vehicle loan interest paid
  itemize : Bool        -- §63(e) election
  spouseItemizes : Bool -- separate return only: the other spouse elected to itemize
  deriving Repr

/-- §1401: self-employment tax, 15.3% of 92.35% of net earnings (§1402(a)(12)). -/
def seTax (net : Nat) : Nat := net * 9235 / 10000 * 153 / 1000

/-- The pieces of one return's computation. -/
structure Calc where
  agi : Nat
  tips : Nat
  overtime : Nat
  senior : Nat
  car : Nat
  qbi : Nat
  itemized : Nat   -- after §68
  cut68 : Nat
  taxable : Nat
  tax : Nat
  deriving Repr

/-- `tipsCutQbi`: whether the §224 deduction for business tips is an item of deduction of the business under
§199A(c)(3). The statute does not say. `true` is the conservative reading.

`saltLiteral`: how the §164(b)(7)(B) phase-down meets a separate return. Read word for word, (7)(B)(i) reduces the
"applicable limitation amount" ($40,400) by 30% of MAGI over half the threshold, (iii) stops it at $10,000, and only
then (6)(B) gives the separate filer half of it: the reduction is in effect halved. The IRS worksheet instead takes
the 30% off the halved cap ($20,200, floor $5,000). `false` is the IRS computation, the conservative one. -/
def compute (tipsCutQbi saltLiteral : Bool) (r : Ret) : Calc :=
  let halfSe := seTax r.tipsBiz / 2                          -- §164(f)
  let wagerIn := r.wagerGain                                   -- §61: gains are gross income in full
  let agi := r.wages + r.tipsEmp + r.tipsBiz + r.other + wagerIn - halfSe   -- §62(a)(1)
  -- §224: capped at $25,000 on any return (b)(1); less $100 per full $1,000 of MAGI over $150,000 / $300,000 (b)(2);
  -- business tips only up to the business's net income (c), and §164(f)(2) makes half the SE tax a business deduction;
  -- a married person only on a joint return (f)
  let bizTipsOk := min r.tipsBiz (r.tipsBiz - halfSe)
  let tipsPre := min 25000 (r.tipsEmp + bizTipsOk)
  let tips := if r.joint then tipsPre - 100 * ((agi - 300000) / 1000) else 0
  -- §225: $12,500, $25,000 on a joint return (b)(1); same phase-out (b)(2); joint return only if married (e)
  let overtime := if r.joint then min 25000 r.overtime - 100 * ((agi - 300000) / 1000) else 0
  -- §151(d)(5)(C): $6,000 per person aged 65, each cut by 6% of MAGI over $150,000 joint; joint return only (v)
  let senior := if r.joint then r.aged * (6000 - 6 * (agi - 150000) / 100) else 0
  -- §163(h)(4): up to $10,000 (C)(i); less $200 per $1,000 or part of MAGI over $100,000, $200,000 joint (C)(ii).
  -- No joint-return requirement.
  let carThr := if r.joint then 200000 else 100000
  let car := min 10000 r.carInt - 200 * ((agi - carThr + 999) / 1000)
  -- §63(c): standard deduction; zero for a separate return if either spouse itemizes (c)(6)(A)
  let std := if r.joint then stdJoint + stdAged * r.aged
             else if r.spouseItemizes then 0 else stdSep + stdAged * r.aged
  -- §170(p): a non-itemizer's cash gifts up to $1,000, $2,000 joint; no 0.5% floor
  let giftNonItem := min r.gifts (if r.joint then 2000 else 1000)
  -- §164(b)(6)-(7): cap, reduced by 30% of MAGI over the threshold (half for a separate return), not below $10,000;
  -- a separate return gets half of the result
  let thr := if r.joint then saltThreshold else saltThreshold / 2
  let capFull := max saltFloor (saltCap - 30 * (agi - thr) / 100)
  let cap := if r.joint then capFull
             else max (saltFloor / 2) (saltCap / 2 - 30 * (agi - thr) / 100)
  let saltDed := min r.salt cap
  -- §170(b)(1)(G), (I): cash gifts up to 60% of the contribution base, and only the part over 0.5% of it
  let giftItem := min r.gifts (60 * agi / 100) - 5 * agi / 1000
  -- §165(d): 90% of wagering losses, and only up to the gains
  let wagerDed := min (90 * r.wagerLoss / 100) r.wagerGain
  let itemPre := saltDed + r.mortgage + giftItem + wagerDed
  let below := if r.itemize then itemPre else std + giftNonItem   -- §63(a)/(b)
  let tiPre := agi - below - tips - overtime - senior - car
  -- §199A: 20% of qualified business income, at most 20% of taxable income before this deduction (a);
  -- phased out above the threshold for a business with no wages or property (b)(3)(B); minimum $400 when
  -- qualified business income is at least $1,000 (i)
  let tipsDedBiz := tips - min tips r.tipsEmp                -- the part of the §224 deduction that came from business tips
  let qbiBase := r.tipsBiz - halfSe - (if tipsCutQbi then tipsDedBiz else 0)
  let qThr := if r.joint then qbiThreshJoint else qbiThreshSep
  let qRange := if r.joint then 150000 else 75000
  let over := min qRange (tiPre - qThr)
  let q20 := 20 * qbiBase / 100
  let q := min (q20 - q20 * over / qRange) (20 * tiPre / 100)
  let qbi := if qbiBase ≥ 1000 then max q 400 else q
  -- §68: itemized deductions cut by 2/37 of the lesser of themselves or taxable income (before the cut, plus
  -- the itemized deductions) over the start of the 37% bracket; §199A(e)(1) ignores §68
  let thr37 := if r.joint then 768700 else 384350
  let cut68 := if r.itemize then 2 * (min itemPre (tiPre - qbi + itemPre - thr37)) / 37 else 0
  let taxable := tiPre - qbi + cut68
  let tax := taxOn (if r.joint then jointBrackets else sepBrackets) taxable
  ⟨agi, tips, overtime, senior, car, qbi, if r.itemize then itemPre - cut68 else 0, cut68, taxable, tax⟩

/-! ### The household and its choices -/

structure Person where
  wages : Nat
  overtime : Nat
  tips : Nat
  aged : Bool
  stateTax : Nat   -- State income tax withheld each year
  deriving Repr

/-- The facts the couple cannot choose. Amounts are per year unless said otherwise. -/
structure Facts where
  a : Person
  b : Person
  propertyTax : Nat
  instalment : Nat   -- a State/local tax instalment due in January of year 2, payable from December of year 1
  mortgage : Nat
  carInt : Nat       -- interest on a car loan that either spouse could have taken (A in the plain case)
  carIntB : Nat := 0 -- interest on a second car loan, B's
  invest : Nat := 0  -- interest income each year from savings that either spouse may own (A in the plain case)
  gifts : Nat        -- intended cash gifts per year
  lump : Nat         -- an amount of A's ordinary income earned in year 1 that may be received in either year
  wagerGain : Nat    -- A's wagering gains and losses each year
  wagerLoss : Nat
  deriving Repr

/-- The choices made so far. The initial value is the plain filing. -/
structure State where
  tipsBizA : Bool := false   -- A's tipped work is A's own trade or business, not employment
  tipsBizB : Bool := false
  loanB : Bool := false      -- B, not A, incurred the car loan
  ownerB : Bool := false     -- B, not A, owns the savings
  lumpY2 : Nat := 0          -- part of the lump received in year 2
  prepaid : Bool := false    -- the January instalment is paid in December of year 1
  giftShiftEarly : Nat := 0  -- year-2 gifts made in year 1
  giftShiftLate : Nat := 0   -- year-1 gifts made in year 2
  payerB1 : Bool := false    -- B, not A, pays the household's taxes, mortgage interest and gifts in year 1
  payerB2 : Bool := false
  sep1 : Bool := false       -- separate returns in year 1
  sep2 : Bool := false
  itemA1 : Bool := false     -- §63(e) election on the joint return, or on A's separate return
  itemA2 : Bool := false
  itemB1 : Bool := false     -- §63(e) election on B's separate return
  itemB2 : Bool := false
  rank : Nat := 0            -- moves are taken in a fixed order (they commute), to keep the search small
  deriving BEq, Hashable, Repr

inductive Move where
  | tipsAsBusiness (b : Bool)    -- §224(c): tips received in the course of the person's own trade or business
  | spouseBorrows                -- §163(h)(4)(B)(i): "indebtedness incurred by the taxpayer"
  | spouseOwns                   -- §1041(a), §102: a transfer between spouses is not taxed; income follows the owner
  | receiveLater (a : Nat)       -- §451(a): cash-method income is included when received
  | prepayTax                    -- §164(a), §461(a): a tax is deducted when paid
  | giveEarly (a : Nat)          -- §170(a)(1): a gift is deducted when payment is made
  | giveLate (a : Nat)
  | spousePays (year2 : Bool)    -- the deduction belongs to the spouse who pays
  | fileSeparately (year2 : Bool) -- §6013(a) is elective; §1(d)
  | itemize (year2 : Bool) (b : Bool)  -- §63(e)
  deriving BEq, Repr

def Move.rank : Move → Nat
  | .tipsAsBusiness false => 1 | .tipsAsBusiness true => 2 | .spouseBorrows => 3 | .receiveLater _ => 4
  | .spouseOwns => 15
  | .prepayTax => 5 | .giveEarly _ => 6 | .giveLate _ => 6
  | .spousePays false => 7 | .spousePays true => 8
  | .fileSeparately false => 9 | .fileSeparately true => 10
  | .itemize false false => 11 | .itemize false true => 12 | .itemize true false => 13 | .itemize true true => 14

/-- One move, if allowed. -/
def step (f : Facts) (s : State) (m : Move) : Option State :=
  if m.rank ≤ s.rank then none else
  let s' := { s with rank := m.rank }
  match m with
  | .tipsAsBusiness false => if f.a.tips > 0 then some { s' with tipsBizA := true } else none
  | .tipsAsBusiness true => if f.b.tips > 0 then some { s' with tipsBizB := true } else none
  | .spouseBorrows => if f.carInt > 0 then some { s' with loanB := true } else none
  | .spouseOwns => if f.invest > 0 then some { s' with ownerB := true } else none
  | .receiveLater a => if 0 < a ∧ a ≤ f.lump then some { s' with lumpY2 := a } else none
  | .prepayTax => if f.instalment > 0 then some { s' with prepaid := true } else none
  | .giveEarly a => if 0 < a ∧ a ≤ f.gifts then some { s' with giftShiftEarly := a } else none
  | .giveLate a => if 0 < a ∧ a ≤ f.gifts then some { s' with giftShiftLate := a } else none
  | .spousePays false => some { s' with payerB1 := true }
  | .spousePays true => some { s' with payerB2 := true }
  | .fileSeparately false => some { s' with sep1 := true }
  | .fileSeparately true => some { s' with sep2 := true }
  | .itemize false false => some { s' with itemA1 := true }
  | .itemize true false => some { s' with itemA2 := true }
  -- B has a return of their own only when the couple file separately
  | .itemize false true => if s.sep1 then some { s' with itemB1 := true } else none
  | .itemize true true => if s.sep2 then some { s' with itemB2 := true } else none

/-- The returns for one year (one joint, or two separate) and their total tax. -/
def yearReturns (f : Facts) (s : State) (year2 : Bool) : List Ret :=
  let sep := if year2 then s.sep2 else s.sep1
  let payerB := if year2 then s.payerB2 else s.payerB1
  let itemA := if year2 then s.itemA2 else s.itemA1
  let itemB := if year2 then s.itemB2 else s.itemB1
  let lump := if year2 then s.lumpY2 else f.lump - s.lumpY2
  let inst := if year2 then (if s.prepaid then 0 else f.instalment)
              else f.instalment + (if s.prepaid then f.instalment else 0)  -- year 1 also pays the one due that January
  let gifts := if year2 then f.gifts + s.giftShiftLate - s.giftShiftEarly
               else f.gifts + s.giftShiftEarly - s.giftShiftLate
  let house := f.propertyTax + inst
  let person (p : Person) (biz : Bool) (isA : Bool) (pays : Bool) (loan : Nat) (owns : Bool) (itm sp : Bool) : Ret :=
    { joint := false, aged := if p.aged then 1 else 0, wages := p.wages, overtime := p.overtime,
      tipsEmp := if biz then 0 else p.tips, tipsBiz := if biz then p.tips else 0,
      other := (if isA then lump else 0) + (if owns then f.invest else 0),
      wagerGain := if isA then f.wagerGain else 0, wagerLoss := if isA then f.wagerLoss else 0,
      salt := p.stateTax + (if pays then house else 0), mortgage := if pays then f.mortgage else 0,
      gifts := if pays then gifts else 0, carInt := loan,
      itemize := itm, spouseItemizes := sp }
  let ra := person f.a s.tipsBizA true (!payerB) (if s.loanB then 0 else f.carInt) (!s.ownerB) itemA itemB
  let rb := person f.b s.tipsBizB false payerB (f.carIntB + if s.loanB then f.carInt else 0) s.ownerB itemB itemA
  if sep then [ra, rb] else
    [{ joint := true, aged := ra.aged + rb.aged, wages := ra.wages + rb.wages, overtime := ra.overtime + rb.overtime,
       tipsEmp := ra.tipsEmp + rb.tipsEmp, tipsBiz := ra.tipsBiz + rb.tipsBiz, other := ra.other + rb.other,
       wagerGain := ra.wagerGain, wagerLoss := ra.wagerLoss, salt := ra.salt + rb.salt,
       mortgage := f.mortgage, gifts := gifts, carInt := f.carInt + f.carIntB, itemize := itemA, spouseItemizes := false }]

def totalTax (cutQbi lit : Bool) (f : Facts) (s : State) : Nat :=
  ((yearReturns f s false) ++ (yearReturns f s true)).foldl (fun t r => t + (compute cutQbi lit r).tax) 0

/-- Self-employment tax over the two years, less the employee's share of FICA the same tips would have borne
(7.65%). Outside the income tax; shown beside it. -/
def payrollExtra (f : Facts) (s : State) : Nat :=
  let one (p : Person) (biz : Bool) := if biz then 2 * (seTax p.tips - p.tips * 765 / 10000) else 0
  -- §3101(b)(2), §1401(b)(2): 0.9% Additional Medicare Tax over $250,000 joint, $125,000 separate
  let wa := f.a.wages + f.a.tips
  let wb := f.b.wages + f.b.tips
  let jointAmt := 9 * (wa + wb - 250000) / 1000
  let sepAmt := 9 * (wa - 125000) / 1000 + 9 * (wb - 125000) / 1000
  let med (sep : Bool) := if sep then sepAmt - jointAmt else 0
  one f.a s.tipsBizA + one f.b s.tipsBizB + med s.sep1 + med s.sep2

/-! ## Part 2. Search -/

/-- Amounts the position offers: the whole, half, and what brings an income to each statutory edge. -/
def edges : List Nat :=
  [75000, 100000, 150000, 200000, 252500, 300000, 505000, 211400, 403550, 512450, 768700, 384350]

def lumpAmounts (f : Facts) : List Nat :=
  let agiA := f.a.wages + f.a.tips + f.wagerGain + f.lump + f.invest
  let agiJoint := agiA + f.b.wages + f.b.tips
  ([f.lump, f.lump / 2] ++ edges.flatMap (fun e => [agiJoint - e, agiA - e])).filter (fun a => 0 < a ∧ a ≤ f.lump)
    |>.eraseDups

def giftAmounts (f : Facts) : List Nat :=
  [f.gifts, f.gifts - 1000, f.gifts - 2000].filter (· > 0) |>.eraseDups

def moves (f : Facts) : List Move :=
  [.tipsAsBusiness false, .tipsAsBusiness true, .spouseBorrows, .spouseOwns, .prepayTax, .spousePays false, .spousePays true,
   .fileSeparately false, .fileSeparately true, .itemize false false, .itemize false true, .itemize true false,
   .itemize true true]
  ++ (lumpAmounts f).map .receiveLater ++ (giftAmounts f).flatMap (fun a => [.giveEarly a, .giveLate a])

def kind : Move → Nat
  | .tipsAsBusiness _ => 0 | .spouseBorrows => 1 | .spouseOwns => 8 | .receiveLater _ => 2 | .prepayTax => 3 | .giveEarly _ => 4
  | .giveLate _ => 4 | .spousePays _ => 5 | .fileSeparately _ => 6 | .itemize _ _ => 7
def kindNames : List String :=
  ["tips as own business", "spouse takes car loan", "shift income to year 2", "prepay tax instalment",
   "shift gifts between years", "other spouse pays", "separate returns", "", "other spouse owns savings"]

def showMove : Move → String
  | .tipsAsBusiness b => s!"{if b then "B" else "A"}'s tips earned in own trade or business"
  | .spouseBorrows => "B takes the car loan"
  | .spouseOwns => "B owns the savings"
  | .receiveLater a => s!"receive ${a} of the lump in year 2"
  | .prepayTax => "pay the January instalment in December of year 1"
  | .giveEarly a => s!"make ${a} of year-2 gifts in year 1"
  | .giveLate a => s!"make ${a} of year-1 gifts in year 2"
  | .spousePays y => s!"B pays the household items in year {if y then 2 else 1}"
  | .fileSeparately y => s!"separate returns in year {if y then 2 else 1}"
  | .itemize y b => s!"itemize, year {if y then 2 else 1}{if b then " (B's return)" else ""}"

/-- The family of a plan: which kinds of move it uses, ignoring the itemize election (kind 7). -/
def family (path : List Move) : Nat := path.foldl (fun m x => if kind x != 7 then m ||| (1 <<< kind x) else m) 0

def familyName (fam : Nat) : String :=
  let ns := (List.range 9).filterMap fun i => if fam &&& (1 <<< i) != 0 then kindNames[i]? else none
  if ns.isEmpty then "(only the itemize election)" else " + ".intercalate ns

def search (title : String) (cutQbi : Bool) (f : Facts) (lit : Bool := false) (keep : Move → Bool := fun _ => true) : IO Unit := do
  let s0 : State := {}
  -- the plain filing: joint both years, everything in its own year, itemize whenever that is the larger deduction
  let mut frontier : Array (State × List Move) := #[(s0, [])]
  let mut seen : Std.HashSet State := {}
  let mut fams : Std.HashMap Nat (Nat × List Move × State) := {}
  let mut count := 1
  let ms := (moves f).filter keep
  let consider (fams : Std.HashMap Nat (Nat × List Move × State)) (s : State) (path : List Move) :=
    let t := totalTax cutQbi lit f s
    let fam := family path
    match fams[fam]? with
    | some (t0, _, _) => if t < t0 then fams.insert fam (t, path, s) else fams
    | none => fams.insert fam (t, path, s)
  fams := consider fams s0 []
  while !frontier.isEmpty do
    let mut next : Array (State × List Move) := #[]
    for (s, path) in frontier do
      for m in ms do
        match step f s m with
        | none => pure ()
        | some s' =>
          if !seen.contains s' then
            seen := seen.insert s'
            count := count + 1
            let p := path ++ [m]
            fams := consider fams s' p
            next := next.push (s', p)
    frontier := next
  let base := (fams[0]?.map (·.1)).getD 0
  IO.println s!"== {title} =="
  IO.println s!"positions searched: {count}; plain filing (joint, better of standard/itemized each year): ${base} over two years"
  let ranked := fams.toList.filter (fun (k, t, _) => k != 0 ∧ t < base) |>.toArray.qsort (fun x y => x.2.1 < y.2.1)
  -- a family is only reported if it beats every family that uses a strict subset of its moves
  let mut shown := 0
  for (k, t, path, s) in ranked do
    let beatsSubs := fams.toList.all fun (k2, t2, _) => !(k2 != k ∧ k2 &&& k == k2) || t < t2
    if beatsSubs ∧ shown < 8 then
      shown := shown + 1
      let pe := payrollExtra f s
      IO.println s!"  saves ${base - t}{if pe > 0 then s!" (but ${pe} more payroll / Medicare tax)" else ""}: {familyName k}"
      for m in path do IO.println s!"      {showMove m}"
  if shown == 0 then IO.println "  nothing beats the plain filing"

def nobody : Person := ⟨0, 0, 0, false, 0⟩

/-- 1. Two earners in a high-tax State, joint income just inside the SALT phase-down. -/
def highTax : Facts :=
  { a := ⟨400000, 0, 0, false, 26000⟩, b := ⟨150000, 0, 0, false, 9000⟩, propertyTax := 16000, instalment := 6000,
    mortgage := 18000, carInt := 0, gifts := 6000, lump := 50000, wagerGain := 0, wagerLoss := 0 }

/-- 2. A tipped worker and an hourly worker with overtime, a car loan, and a small house. -/
def tipped : Facts :=
  { a := ⟨22000, 0, 30000, false, 1500⟩, b := ⟨78000, 11000, 0, false, 3500⟩, propertyTax := 4000, instalment := 1000,
    mortgage := 7000, carInt := 4500, gifts := 1500, lump := 12000, wagerGain := 0, wagerLoss := 0 }

/-- 3. Retired couple, both over 65; the lump is a retirement-account withdrawal they can time. -/
def retired : Facts :=
  { a := ⟨90000, 0, 0, true, 3000⟩, b := ⟨40000, 0, 0, true, 1500⟩, propertyTax := 8000, instalment := 2000,
    mortgage := 0, carInt := 3000, gifts := 7000, lump := 60000, wagerGain := 0, wagerLoss := 0 }

/-- 4. Both spouses tipped. -/
def bothTipped : Facts :=
  { a := ⟨20000, 0, 28000, false, 1500⟩, b := ⟨18000, 3000, 24000, false, 1300⟩, propertyTax := 3000, instalment := 0,
    mortgage := 0, carInt := 2500, gifts := 800, lump := 0, wagerGain := 0, wagerLoss := 0 }

/-- 5. High earner married to a tipped worker with a car loan; A gambles and breaks even. -/
def mixed : Facts :=
  { a := ⟨260000, 0, 0, false, 15000⟩, b := ⟨15000, 0, 35000, false, 2500⟩, propertyTax := 12000, instalment := 4000,
    mortgage := 15000, carInt := 6000, gifts := 4000, lump := 40000, wagerGain := 30000, wagerLoss := 30000 }

/-- 6. Top bracket: the §68 cut applies. -/
def top : Facts :=
  { a := ⟨900000, 0, 0, false, 70000⟩, b := ⟨120000, 0, 0, false, 8000⟩, propertyTax := 30000, instalment := 15000,
    mortgage := 30000, carInt := 5000, gifts := 40000, lump := 200000, wagerGain := 0, wagerLoss := 0 }

/-- 7. Equal earners in a high-tax State. -/
def equalEarners : Facts :=
  { a := ⟨300000, 0, 0, false, 19000⟩, b := ⟨300000, 0, 0, false, 19000⟩, propertyTax := 16000, instalment := 6000,
    mortgage := 18000, carInt := 0, gifts := 8000, lump := 0, wagerGain := 0, wagerLoss := 0 }

/-- 8. Two middle earners just above the joint car-loan phase-out, two car loans, renters. -/
def carLoans : Facts :=
  { a := ⟨165000, 0, 0, false, 7000⟩, b := ⟨95000, 0, 0, false, 4000⟩, propertyTax := 0, instalment := 0,
    mortgage := 0, carInt := 5000, carIntB := 4000, invest := 6000, gifts := 1500, lump := 15000,
    wagerGain := 0, wagerLoss := 0 }

/-- 9. A break-even gambler married to a wage earner with a car loan. -/
def gambler : Facts :=
  { a := ⟨90000, 0, 0, false, 4000⟩, b := ⟨90000, 0, 0, false, 4000⟩, propertyTax := 6000, instalment := 0,
    mortgage := 9000, carInt := 0, carIntB := 7000, invest := 3000, gifts := 2000, lump := 0,
    wagerGain := 80000, wagerLoss := 80000 }

/-- 10. One earner at $560k, spouse with savings income only. -/
def oneEarner : Facts :=
  { a := ⟨560000, 0, 0, false, 36000⟩, b := ⟨0, 0, 0, false, 0⟩, propertyTax := 20000, instalment := 8000,
    mortgage := 20000, carInt := 6000, invest := 40000, gifts := 10000, lump := 60000,
    wagerGain := 0, wagerLoss := 0 }

/-- 7b, 7c. The same household with the income split unevenly. -/
def unequal (wa wb : Nat) : Facts :=
  { equalEarners with a := ⟨wa, 0, 0, false, wa * 63 / 1000⟩, b := ⟨wb, 0, 0, false, wb * 63 / 1000⟩ }

#eval do
  search "T2 closed gap, flag false: 7 equal earners" true equalEarners false
  search "T2 closed gap, flag TRUE (literal branch deleted): 7L" true equalEarners true
  search "T2 closed gap: 7bL" true (unequal 350000 250000) true

end Legal.USTax.Hunt.NewDeductions
