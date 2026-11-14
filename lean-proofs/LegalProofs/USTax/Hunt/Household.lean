import Std

/-!
# Household: filing status, dependents and credits (rules for 2026, 2025 indexed dollar figures)

Two adults, up to three children, possibly a parent of adult A, with given incomes. The first part says what each
provision allows and what it costs; it names no planning idea. The second part searches every lawful combination of
the choices the Code leaves open (joint or separate return, who claims which child, who keeps up the home, who claims
the grandparent, dependent-care exclusion, pre-tax and Roth retirement contributions, who pays adoption expenses) and
compares the household's total income tax net of credits with the default filing.

    lake env lean LegalProofs/USTax/Hunt/Household.lean

Figures. Statutory amounts are as amended by Pub. L. 119-21: §24(h)(2) $2,200; §21(a)(2) 50/35/20 percent and §129
$7,500 (both from 2026); §151(d)(5)(C) $6,000; §§224, 225; §23(a)(4) $5,000; §36B without the 2021-2025 temporary
rules (so the 400 percent line applies). Indexed amounts are the 2025 ones (Rev. Proc. 2024-40 and Pub. L. 119-21):
brackets, standard deduction, EIC table, §24 refundable $1,700, §25B lines, §23 $17,280 and $259,190. §36B
percentages are the 2026 table (Rev. Proc. 2025-25); the poverty line is the 2025 guideline, which §36B(d)(3)(B)
makes the one for 2026 coverage.

Simplifications, each stated once:
* one year; wages, interest, tips and overtime only; nobody itemizes; no AMT, no state tax, no payroll tax in the
  objective (payroll tax appears only in §24(d)(1)(B)(ii));
* every child is a child of both adults, meets the §152(c)(3) age test and does not provide half of his own support;
* adults living together both live with every child all year; adults living apart lived apart all year;
* the person for whom a child is a §21 qualifying individual is the one who pays that child's care;
* everyone covered through the Exchange is enrolled in the benchmark plan; Medicaid/CHIP eligibility is not modelled;
* the unused nonrefundable adoption credit (carried forward by §23(c)) is counted as lost.
-/

namespace Legal.USTax.Hunt.Household

/-! ## Part 1. Rules -/

inductive Who where | a | b | none
  deriving BEq, Hashable, Repr, DecidableEq, Inhabited

inductive Status where | single | hoh | mfj | mfs
  deriving BEq, Hashable, Repr, DecidableEq, Inhabited

structure Adult where
  wages : Nat       -- includes tips and overtime
  tips : Nat        -- qualified tips, §224(d)
  overtime : Nat    -- qualified overtime compensation, §225(c)
  invest : Nat      -- interest and dividends
  age : Nat
  hasPlan : Bool    -- §401(k) plan at work (else pre-tax saving is a deductible IRA, §219)
  hasFsa : Bool     -- employer dependent care assistance program, §129(d)
  deriving Repr, Inhabited

structure Kid where
  age : Nat
  withA : Bool      -- same principal place of abode as A for more than half the year, §152(c)(1)(B)
  withB : Bool
  care : Nat        -- employment-related care expenses, §21(b)(2)
  tuition : Nat     -- qualified tuition and related expenses, §25A(f)(1)
  earned : Nat
  unearned : Nat
  deriving Repr, Inhabited

structure Elder where
  income : Nat      -- gross income, §152(d)(1)(B)
  inMainHome : Bool -- lives all year in A's home (else in a separate home)
  deriving Repr, Inhabited

structure Facts where
  married : Bool          -- §7703(a): status at the close of the year
  apart : Bool            -- the adults did not share a home in the last six months of the year
  a : Adult
  b : Adult
  kids : List Kid
  elder : Option Elder    -- a parent of A
  aKeepsElderHome : Bool  -- A furnishes over half the cost of the elder's separate home
  marketplace : Bool      -- the adults and children buy coverage through an Exchange
  premAdult : Nat         -- annual benchmark premium per adult
  premKid : Nat
  adoption : Nat          -- qualified adoption expenses, adoption by both adults final this year
  deriving Repr, Inhabited

/-- The choices the Code leaves to the household. -/
structure Plan where
  joint : Bool            -- §6013(a)
  claim : List Who        -- per child: who claims the child as a dependent
  elder : Who
  keeper : Who            -- who furnishes over half the cost of the shared home, §2(b)(1)
  fsaA : Nat
  fsaB : Nat
  preA : Nat              -- elective deferral (§402(g)) if the adult has a plan, else deductible IRA (§219)
  preB : Nat
  rothA : Nat             -- Roth IRA contribution, §408A
  rothB : Nat
  adoptA : Nat            -- percent of the adoption expenses paid by A
  deriving BEq, Hashable, Repr, Inhabited

def Facts.ad (f : Facts) : Who → Adult
  | .b => f.b
  | _ => f.a
def Plan.fsa (p : Plan) : Who → Nat
  | .b => p.fsaB
  | _ => p.fsaA
def Plan.pre (p : Plan) : Who → Nat
  | .b => p.preB
  | _ => p.preA
def Plan.roth (p : Plan) : Who → Nat
  | .b => p.rothB
  | _ => p.rothA
def other : Who → Who
  | .a => .b
  | .b => .a
  | .none => .none

def ceilDiv (x d : Nat) : Nat := (x + d - 1) / d
def sumBy {α} (f : α → Nat) (l : List α) : Nat := l.foldl (fun s x => s + f x) 0

/-! ### §1: rates; §63(c): standard deduction (2025) -/

def brackets : Status → List (Nat × Nat)
  | .single => [(11925, 10), (48475, 12), (103350, 22), (197300, 24), (250525, 32), (626350, 35)]
  | .hoh => [(17000, 10), (64850, 12), (103350, 22), (197300, 24), (250500, 32), (626350, 35)]
  | .mfj => [(23850, 10), (96950, 12), (206700, 22), (394600, 24), (501050, 32), (751600, 35)]
  | .mfs => [(11925, 10), (48475, 12), (103350, 22), (197300, 24), (250525, 32), (375800, 35)]

def taxOn (st : Status) (ti : Nat) : Nat :=
  let rec go (bs : List (Nat × Nat)) (lo acc : Nat) : Nat :=
    match bs with
    | [] => acc + (ti - lo) * 37
    | (hi, r) :: rest => if ti ≤ hi then acc + (ti - lo) * r else go rest hi (acc + (hi - lo) * r)
  go (brackets st) 0 0 / 100

/-- §63(c)(2), (7). -/
def stdDed : Status → Nat
  | .mfj => 31500
  | .hoh => 23625
  | _ => 15750

/-- 2025 poverty guideline, 48 States; §36B(d)(3). -/
def fpl (n : Nat) : Nat := 15650 + 5500 * (n - 1)

/-! ### One return -/

structure Ret where
  st : Status
  sep : Bool          -- married within §7703 and not filing jointly
  eicOk : Bool        -- §32(d): joint return, or not married, or the separated-spouse rule
  wages : Nat         -- includible wages of everyone on the return
  earnedMin : Nat     -- §21(d)(1), §129(b)(1): own earned income, or the lesser of the spouses'
  invest : Nat
  iraDed : Nat
  tips : Nat
  overtime : Nat
  seniors : Nat       -- persons on the return aged 65 or more
  eicAge : Bool       -- §32(c)(1)(A)(ii)(II)
  ctcKids : Nat       -- §24(c): qualifying children under 17 claimed as dependents
  otherDeps : Nat     -- §24(h)(4)
  eicKids : Nat       -- §32(c)(3)
  careKids : Nat      -- §21(b)(1)(A)
  carePaid : Nat
  fsa : Nat           -- excluded under §129
  saver : List Nat    -- §25B(d): contributions of each eligible individual
  tuition : List Nat  -- §25A: per student dependent
  ssTax : Nat         -- §24(d)(2)
  ptcOn : Bool
  famSize : Nat       -- §36B(d)(1)
  benchmark : Nat     -- §36B(b)(3)(B), (C)
  adopt : Nat         -- §23: expenses taken into account (after the §23(b)(1) limit)
  deriving Repr, Inhabited

structure Out where
  agi : Nat
  ti : Nat
  tax : Nat
  parts : List (String × Nat)   -- credits, by provision
  net : Int
  deriving Repr, Inhabited

/-- §25A(b)(1). -/
def aotcOf (t : Nat) : Nat := min t 2000 + (min t 4000 - min t 2000) / 4

/-- §32(a), (b), (j): (credit rate, earned income amount, phaseout start, phaseout rate), rates in basis points. -/
def eicTable (n : Nat) (joint : Bool) : Nat × Nat × Nat × Nat :=
  if n = 0 then (765, 8490, if joint then 17730 else 10620, 765)
  else if n = 1 then (3400, 12730, if joint then 30470 else 23350, 1598)
  else if n = 2 then (4000, 17880, if joint then 30470 else 23350, 2106)
  else (4500, 17880, if joint then 30470 else 23350, 2106)

def eic (r : Ret) (agi : Nat) : Nat :=
  -- §32(d)(1) married must file jointly; §32(i) investment income (2025: $11,600); §32(c)(1)(A)(ii) age if no child
  if !r.eicOk || r.invest > 11600 || (r.eicKids = 0 && !r.eicAge) then 0 else
  let (rate, amt, start, ph) := eicTable r.eicKids (r.st == .mfj)
  let full := rate * amt
  let a1 := rate * min r.wages amt
  let a2 := full - min full (ph * (max agi r.wages - start))
  min a1 a2 / 10000

def interp (lo hi r rlo rhi : Nat) : Nat := lo + (hi - lo) * (r - rlo) / (rhi - rlo)

/-- §36B(b)(2)(B), (b)(3)(A), (c)(1)(A): 2026 percentages, basis points. -/
def ptc (hi fam bench : Nat) : Nat :=
  let line := fpl fam
  if hi < line || hi > 4 * line then 0 else
  let r := hi * 10000 / line
  let bp :=
    if r < 13300 then 210 else if r < 15000 then interp 314 419 r 13300 15000
    else if r < 20000 then interp 419 660 r 15000 20000
    else if r < 25000 then interp 660 844 r 20000 25000
    else if r < 30000 then interp 844 996 r 25000 30000 else 996
  bench - min bench (hi * bp / 10000)

def compute (r : Ret) : Out :=
  let joint := r.st == .mfj
  let agi := r.wages + r.invest - r.iraDed
  -- §63(c)(3), (f): additional amount for the aged (2025: $1,600 married, $2,000 not)
  let aged := r.seniors * (if r.st == .mfj || r.st == .mfs then 1600 else 2000)
  -- §151(d)(5)(C): $6,000 each, less 6% of MAGI over $75,000 ($150,000 joint); joint return if married
  let senior := if r.sep then 0 else r.seniors * (6000 - min 6000 ((agi - (if joint then 150000 else 75000)) * 6 / 100))
  -- §224(b), §225(b): $100 for each $1,000 over $150,000 ($300,000 joint); joint return if married
  let cut := (agi - (if joint then 300000 else 150000)) / 1000 * 100
  let tipCap := min r.tips 25000
  let tipD := if r.sep then 0 else tipCap - min tipCap cut
  let otCap := min r.overtime (if joint then 25000 else 12500)
  let otD := if r.sep then 0 else otCap - min otCap cut
  let ti := agi - (stdDed r.st + aged + senior + tipD + otD)
  let tax := taxOn r.st ti
  -- §21: (c) dollar limit less the §129 exclusion; (d) earned income; (a)(2) percentage; (e)(2) joint if married
  let cap := if r.careKids = 0 then 0 else if r.careKids = 1 then 3000 else 6000
  let exp21 := if r.sep then 0 else min (min (r.carePaid - r.fsa) (cap - r.fsa)) r.earnedMin
  let pct1 := 50 - min 15 (ceilDiv (agi - 15000) 2000)
  let pct := pct1 - min (pct1 - 20) (if joint then ceilDiv (agi - 150000) 4000 else ceilDiv (agi - 75000) 2000)
  let c21 := exp21 * pct / 100
  -- §25A: (d) phaseout $80,000-$90,000 (doubled joint); (g)(6) joint if married; (i) 40% refundable
  let aFull := sumBy aotcOf r.tuition
  let aLo := if joint then 160000 else 80000
  let aRange := if joint then 20000 else 10000
  let aotc := if r.sep then 0 else aFull - min aFull (aFull * min aRange (agi - aLo) / aRange)
  let aRef := aotc * 40 / 100
  -- §25B(b): 50/20/10 percent by AGI (2025 lines), per eligible individual, $2,000 each
  let (t1, t2, t3) := match r.st with
    | .mfj => (47500, 51000, 79000)
    | .hoh => (35625, 38250, 59250)
    | _ => (23750, 25500, 39500)
  let rate := if agi ≤ t1 then 50 else if agi ≤ t2 then 20 else if agi ≤ t3 then 10 else 0
  let saver := sumBy (fun c => min c 2000 * rate / 100) r.saver
  -- nonrefundable credits against the tax, §26(a), in form order
  let u21 := min c21 tax
  let rem := tax - u21
  let uA := min (aotc - aRef) rem
  let rem := rem - uA
  let uS := min saver rem
  let rem := rem - uS
  -- §24: (h)(2) $2,200, (h)(4) $500, (b)(1), (h)(3) phaseout; (d), (h)(5), (h)(6) refundable part
  let ctcFull := r.ctcKids * 2200 + r.otherDeps * 500
  let ctc := ctcFull - min ctcFull (ceilDiv (agi - (if joint then 400000 else 200000)) 1000 * 50)
  let uC := min ctc rem
  let rem := rem - uC
  let e := eic r agi
  let actcB := (r.wages - 2500) * 15 / 100
  let actcAlt := if r.ctcKids ≥ 3 then r.ssTax - e else 0
  let actc := min (min (ctc - uC) (r.ctcKids * 1700)) (max actcB actcAlt)
  -- §23: (b)(2) phaseout over $259,190; (a)(4) $5,000 refundable; (f)(1) joint if married
  let ad := if r.sep then 0 else r.adopt - r.adopt * min 40000 (agi - 259190) / 40000
  let adRef := min 5000 ad
  let adNon := min (ad - adRef) rem
  -- §36B: (c)(1)(C) joint if married
  let p := if r.ptcOn && !r.sep then ptc agi r.famSize r.benchmark else 0
  let credits := u21 + uA + uS + uC + adNon + e + actc + aRef + adRef + p
  { agi := agi, ti := ti, tax := tax,
    parts := [("§21", u21), ("§25A", uA + aRef), ("§25B", uS), ("§24", uC + actc), ("§32", e), ("§23", adNon + adRef),
              ("§36B", p)],
    net := (tax : Int) - credits }

/-! ### From the household and its choices to the returns -/

def isQual (k : Kid) : Bool := k.age < 13 && k.care > 0

/-- The children an adult filing his own return may count, by provision. -/
structure Mine where
  deps : List Kid     -- claimed as dependents (§152(c), or §152(e) on a release by the custodial parent)
  home : List Kid     -- qualifying children for §2(b), §32(c)(3), §21(e)(5): no regard to §152(e)

def mine (f : Facts) (p : Plan) (w : Who) : Mine :=
  let ks := f.kids.zip p.claim
  let deps := (ks.filter (fun kc => kc.2 == w)).map (·.1)
  -- together: the child is the qualifying child of the parent who claims (§152(c)(4)); apart: of the parent the
  -- child lives with, whoever holds the release (§152(e) is disregarded by §§2(b)(1)(A)(i), 32(c)(3)(A), 21(e)(5))
  let home := if f.apart then
      (ks.filter (fun kc => (if w == .a then kc.1.withA else kc.1.withB) && kc.2 != .none)).map (·.1)
    else deps
  { deps := deps, home := home }

def inclWages (f : Facts) (p : Plan) (w : Who) : Nat :=
  let ad := f.ad w
  ad.wages - p.fsa w - (if ad.hasPlan then p.pre w else 0)

def iraDed (f : Facts) (p : Plan) (w : Who) : Nat := if (f.ad w).hasPlan then 0 else p.pre w

/-- §23(b)(1) (2025: $17,280), one limit per adoption, divided between unmarried adopters in proportion to what each
paid (Notice 97-9 lets them divide it as they agree). -/
def adoptShare (f : Facts) (p : Plan) (w : Who) : Nat :=
  let pctW := if w == .a then p.adoptA else 100 - p.adoptA
  min f.adoption 17280 * pctW / 100

def soloRet (f : Facts) (p : Plan) (w : Who) : Ret :=
  let ad := f.ad w
  let m := mine f p w
  let elderMine := f.elder.isSome && p.elder == w
  let kidHome := !m.home.isEmpty && (f.apart || p.keeper == w)
  -- §2(b)(1)(A)(ii) and (B); §2(b)(3)(B)(i): not by reason of a §152(d)(2)(H) dependent, so only A (the child)
  let elderHoh := elderMine && w == .a && (match f.elder with
    | some e => if e.inMainHome then (f.apart || p.keeper == .a) else f.aKeepsElderHome
    | none => false)
  -- §7703(b), §2(c): a married person apart from the spouse, keeping the home of a child, is treated as unmarried
  let unmarried := !f.married || (f.apart && kidHome)
  let st := if !unmarried then Status.mfs else if kidHome || elderHoh then .hoh else .single
  let care := m.home.filter isQual
  let w1 := inclWages f p w
  let cov := if f.marketplace then f.premAdult + m.deps.length * f.premKid else 0
  { st := st, sep := !unmarried,
    eicOk := !f.married || (f.apart && !m.home.isEmpty),   -- §32(d)(2)(B)
    wages := w1,
    earnedMin := if f.married && !unmarried then min w1 (inclWages f p (other w)) else w1,
    invest := ad.invest, iraDed := iraDed f p w, tips := ad.tips, overtime := ad.overtime,
    seniors := if ad.age ≥ 65 then 1 else 0, eicAge := ad.age ≥ 25 && ad.age < 65,
    ctcKids := (m.deps.filter (·.age < 17)).length,
    otherDeps := (m.deps.filter (·.age ≥ 17)).length + (if elderMine then 1 else 0),
    eicKids := m.home.length, careKids := care.length, carePaid := sumBy (·.care) care, fsa := p.fsa w,
    saver := [p.pre w + p.roth w],
    tuition := (m.deps.filter (·.tuition > 0)).map (·.tuition),
    ssTax := (ad.wages - p.fsa w) * 765 / 10000,
    ptcOn := f.marketplace, famSize := 1 + m.deps.length + (if elderMine then 1 else 0), benchmark := cov,
    adopt := adoptShare f p w }

def jointRet (f : Facts) (p : Plan) : Ret :=
  let deps := ((f.kids.zip p.claim).filter (fun kc => kc.2 == .a)).map (·.1)
  let elderMine := f.elder.isSome && p.elder == .a
  let care := deps.filter isQual
  let wa := inclWages f p .a
  let wb := inclWages f p .b
  { st := .mfj, sep := false, eicOk := true, wages := wa + wb, earnedMin := min wa wb,
    invest := f.a.invest + f.b.invest, iraDed := iraDed f p .a + iraDed f p .b,
    tips := f.a.tips + f.b.tips, overtime := f.a.overtime + f.b.overtime,
    seniors := (if f.a.age ≥ 65 then 1 else 0) + (if f.b.age ≥ 65 then 1 else 0),
    eicAge := (f.a.age ≥ 25 && f.a.age < 65) || (f.b.age ≥ 25 && f.b.age < 65),
    ctcKids := (deps.filter (·.age < 17)).length,
    otherDeps := (deps.filter (·.age ≥ 17)).length + (if elderMine then 1 else 0),
    eicKids := deps.length, careKids := care.length, carePaid := sumBy (·.care) care, fsa := p.fsaA + p.fsaB,
    saver := [p.preA + p.rothA, p.preB + p.rothB],
    tuition := (deps.filter (·.tuition > 0)).map (·.tuition),
    ssTax := (f.a.wages + f.b.wages - p.fsaA - p.fsaB) * 765 / 10000,
    ptcOn := f.marketplace, famSize := 2 + deps.length + (if elderMine then 1 else 0),
    benchmark := if f.marketplace then 2 * f.premAdult + deps.length * f.premKid else 0,
    adopt := min f.adoption 17280 }

def returns (f : Facts) (p : Plan) : List (String × Ret) :=
  if p.joint then [("joint", jointRet f p)] else [("A", soloRet f p .a), ("B", soloRet f p .b)]

/-- A child's own return. §63(c)(5) (2025: $1,350, or earned income plus $450); §1(g) with the parent chosen by
§1(g)(5) (joint return, else the parent with the greater taxable income; for unmarried parents the statute says the
custodial parent, and the form instructions use the greater taxable income when they live together); §25A(g)(3):
the student takes the credit only if no one is allowed the §151 deduction, and §25A(i) then denies the refundable part. -/
def kidTax (k : Kid) (claimed : Bool) (parent : Status × Nat) : Nat :=
  let gross := k.earned + k.unearned
  if gross = 0 then 0 else
  let ti := gross - min 15750 (max 1350 (k.earned + 450))
  let nui := min ti (k.unearned - 2700)
  let tax := max (taxOn .single ti) (taxOn .single (ti - nui) + (taxOn parent.1 (parent.2 + nui) - taxOn parent.1 parent.2))
  tax - (if claimed then 0 else min tax (aotcOf k.tuition))

def total (f : Facts) (p : Plan) : Int :=
  let outs : List (Status × Out) := (returns f p).map (fun r => (r.2.st, compute r.2))
  let parent := outs.foldl (fun (best : Status × Nat) o => if o.2.ti ≥ best.2 then (o.1, o.2.ti) else best) (.single, 0)
  let kids := (f.kids.zip p.claim).foldl (fun s kc => s + kidTax kc.1 (kc.2 != .none) parent) 0
  outs.foldl (fun s o => s + o.2.net) (kids : Int)

/-- Is the plan one the Code allows on these facts? -/
def lawful (f : Facts) (p : Plan) : Bool :=
  let claimOk := p.claim.length = f.kids.length && (f.kids.zip p.claim).all (fun kc =>
    match kc.2 with
    | .none => true
    | .a => (kc.1.withA || (f.apart && kc.1.withB)) && true           -- §152(c)(1)(B), or §152(e)(2) release
    | .b => !p.joint && (kc.1.withB || (f.apart && kc.1.withA)))
  let elderOk := match f.elder, p.elder with
    | _, .none => true
    | some e, .a => e.income < 5200                                      -- §152(d)(1)(B), (d)(2)(C)
    -- §152(d)(2)(G) mother/father-in-law if married; else (d)(2)(H): member of B's household all year
    | some e, .b => !p.joint && e.income < 5200 && (f.married || (e.inMainHome && !f.apart))
    | none, _ => false
  let fsaOk := [Who.a, Who.b].all (fun w =>
    p.fsa w = 0 || ((f.ad w).hasFsa &&
      (if p.joint then
        -- §129(a)(2)(A) $7,500 a return; (b)(1)(B) lesser earned income of the spouses
        p.fsaA + p.fsaB ≤ min 7500 (jointRet f { p with fsaA := 0, fsaB := 0 }).carePaid
          && p.fsaA + p.fsaB ≤ min (inclWages f p .a) (inclWages f p .b)
      else
        let r := soloRet f p w
        -- $3,750 on a separate return by a married individual (§129(a)(2)(C) uses §21(e)(3)-(4) status)
        p.fsa w ≤ min (if r.sep then 3750 else 7500) r.carePaid && p.fsa w ≤ r.earnedMin)))
  let retOk := [Who.a, Who.b].all (fun w =>
    let ad := f.ad w
    -- §402(g)(1) (2025: $23,500); §219(b)(5)(A) and §408A(c)(2) (2025: $7,000 for both IRAs together)
    (if ad.hasPlan then p.pre w ≤ 23500 && p.pre w + p.fsa w ≤ ad.wages && p.roth w ≤ 7000
     else p.pre w + p.roth w ≤ 7000) && p.pre w + p.roth w + p.fsa w ≤ ad.wages
    -- §408A(c)(3): no Roth contribution above the income range; none for a married person filing separately who
    -- lived with the spouse (range starts at zero)
    && (p.roth w = 0 || (!(f.married && !p.joint && !f.apart) && f.a.wages + f.b.wages ≤ 150000)))
  let shape :=
    (if p.joint then f.married && p.keeper == .a && p.elder != .b && p.adoptA = 100 else true)
    && p.keeper != .none && (if f.apart then p.keeper == .a else true)
    && p.adoptA ≤ 100 && (if f.adoption = 0 then p.adoptA = 100 else true)
  claimOk && elderOk && fsaOk && retOk && shape

inductive Move where
  | fileJoint | fileSeparate          -- §6013(a)
  | claim (i : Nat) (w : Who)         -- §§151(c), 152(c)(4), 152(e)(2)
  | claimElder (w : Who)              -- §152(d)
  | keep (w : Who)                    -- §2(b)(1): who furnishes over half the cost of the home
  | fsa (w : Who) (amt : Nat)         -- §129
  | pretax (w : Who) (amt : Nat)      -- §402(g) / §219
  | roth (w : Who) (amt : Nat)        -- §408A
  | adopt (pctA : Nat)                -- §23: who pays
  deriving Repr

def apply (p : Plan) : Move → Plan
  | .fileJoint => { p with joint := true }
  | .fileSeparate => { p with joint := false }
  | .claim i w => { p with claim := p.claim.set i w }
  | .claimElder w => { p with elder := w }
  | .keep w => { p with keeper := w }
  | .fsa .b x => { p with fsaB := x }
  | .fsa _ x => { p with fsaA := x }
  | .pretax .b x => { p with preB := x }
  | .pretax _ x => { p with preA := x }
  | .roth .b x => { p with rothB := x }
  | .roth _ x => { p with rothA := x }
  | .adopt x => { p with adoptA := x }

def step (f : Facts) (p : Plan) (m : Move) : Option Plan :=
  let q := apply p m
  if lawful f q then some q else none

/-! ## Part 2. Search -/

/-- The plain filing: married couples file jointly; otherwise the higher earner (or, apart, the parent the child
lives with) claims every child and keeps the home; A claims his parent; nothing else is done. -/
def default (f : Facts) : Plan :=
  let hi : Who := if f.married then .a else if f.a.wages ≥ f.b.wages then .a else .b
  { joint := f.married && !f.apart,
    claim := f.kids.map (fun k => if f.apart then (if k.withA then .a else .b) else hi),
    elder := (match f.elder with
      | some e => if e.income < 5200 then Who.a else Who.none
      | none => Who.none),
    keeper := if f.apart then .a else hi,
    fsaA := 0, fsaB := 0, preA := 0, preB := 0, rothA := 0, rothB := 0, adoptA := 100 }

/-- Every income line that appears in the provisions encoded (§25B, §21, §25A, §24, §151(d)(5)(C), §224, §36B). -/
def lines : List Nat :=
  [23750, 25500, 39500, 35625, 38250, 59250, 47500, 51000, 79000, 15000, 75000, 150000, 80000, 160000, 200000,
   400000] ++ (List.range 7).map (fun n => 4 * fpl (n + 1))

def amountsPre (f : Facts) (p : Plan) (w : Who) : List Nat :=
  let ad := f.ad w
  let mineInc := ad.wages + ad.invest
  let o := other w
  let inc := if p.joint then mineInc + (f.ad o).wages + (f.ad o).invest else mineInc
  let lim := if ad.hasPlan then 23500 else 7000
  ([0, 2000, lim] ++ (lines.filter (· < inc)).map (inc - ·)).filter (· ≤ lim) |>.eraseDups

def moves (f : Facts) (p : Plan) : List Move :=
  let ws := [Who.a, Who.b]
  let care := sumBy (·.care) (f.kids.filter isQual)
  [Move.fileJoint, .fileSeparate, .keep .a, .keep .b, .claimElder .a, .claimElder .b, .claimElder .none,
   .adopt 0, .adopt 50, .adopt 100]
  ++ (List.range f.kids.length).flatMap (fun i => [Move.claim i .a, .claim i .b, .claim i .none])
  ++ ws.flatMap (fun w => (([0, 3750, 7500, min 7500 care]
        ++ (f.kids.filter isQual).map (fun k => min 7500 k.care)).eraseDups).map (Move.fsa w))
  ++ ws.flatMap (fun w => (amountsPre f p w).map (Move.pretax w))
  ++ ws.flatMap (fun w => [Move.roth w 0, .roth w 2000])

def whoS : Who → String
  | .a => "A"
  | .b => "B"
  | .none => "nobody"

/-- What a plan does differently from the default, in words. -/
def describe (f : Facts) (d p : Plan) : List String :=
  (if p.joint != d.joint then [if p.joint then "file jointly" else "file separate returns"] else [])
  ++ ((List.range f.kids.length).filterMap fun i =>
        let c := p.claim.getD i .none
        if c != d.claim.getD i .none then some s!"child {i + 1} claimed by {whoS c}" else none)
  ++ (if p.elder != d.elder then [s!"elder claimed by {whoS p.elder}"] else [])
  ++ (if p.keeper != d.keeper then [s!"{whoS p.keeper} keeps up the home"] else [])
  ++ (if p.fsaA != d.fsaA then [s!"A dependent-care exclusion ${p.fsaA}"] else [])
  ++ (if p.fsaB != d.fsaB then [s!"B dependent-care exclusion ${p.fsaB}"] else [])
  ++ (if p.preA != d.preA then [s!"A pre-tax saving ${p.preA}"] else [])
  ++ (if p.preB != d.preB then [s!"B pre-tax saving ${p.preB}"] else [])
  ++ (if p.rothA != d.rothA then [s!"A Roth IRA ${p.rothA}"] else [])
  ++ (if p.rothB != d.rothB then [s!"B Roth IRA ${p.rothB}"] else [])
  ++ (if p.adoptA != d.adoptA then [s!"A pays {p.adoptA}% of the adoption expenses"] else [])

/-- The family of a plan: which kinds of choice it uses. -/
def family (d p : Plan) : String :=
  let tags :=
    (if p.joint != d.joint then ["status"] else []) ++ (if p.claim != d.claim then ["claims"] else [])
    ++ (if p.elder != d.elder then ["elder"] else []) ++ (if p.keeper != d.keeper then ["keeper"] else [])
    ++ (if p.fsaA != d.fsaA || p.fsaB != d.fsaB then ["fsa"] else [])
    ++ (if p.preA != d.preA || p.preB != d.preB then ["pretax"] else [])
    ++ (if p.rothA != d.rothA || p.rothB != d.rothB then ["roth"] else [])
    ++ (if p.adoptA != d.adoptA then ["adopt"] else [])
  if tags.isEmpty then "default" else "+".intercalate tags

def semi (l : List String) : String := "; ".intercalate l

def showRet (name : String) (r : Ret) : String :=
  let o := compute r
  let st := match r.st with
    | .single => "single"
    | .hoh => "head of household"
    | .mfj => "joint"
    | .mfs => "married separate"
  let cs := (o.parts.filter (·.2 > 0)).map (fun c => s!"{c.1} {c.2}")
  let sep := ", "
  s!"    {name}: {st}, AGI {o.agi}, taxable {o.ti}, tax {o.tax}, credits [{sep.intercalate cs}], net {o.net}"

def showPlan (f : Facts) (p : Plan) : IO Unit := do
  for (n, r) in returns f p do IO.println (showRet n r)

/-- Breadth-first over every lawful plan reachable from the default by changing one choice at a time. -/
def search (name : String) (f : Facts) (maxStates : Nat := 60000) : IO Int := do
  let d := default f
  let base := total f d
  let mut seen : Std.HashSet Plan := Std.HashSet.emptyWithCapacity 1024 |>.insert d
  let mut frontier : Array Plan := #[d]
  let mut fam : Std.HashMap String (Int × Plan) := {}
  let mut depth := 0
  while !frontier.isEmpty && seen.size < maxStates do
    depth := depth + 1
    let mut next : Array Plan := #[]
    for p in frontier do
      for m in moves f p do
        match step f p m with
        | none => pure ()
        | some q =>
          if !seen.contains q then
            seen := seen.insert q
            next := next.push q
            let t := total f q
            let k := family d q
            match fam[k]? with
            | some (bt, _) => if t < bt then fam := fam.insert k (t, q)
            | none => fam := fam.insert k (t, q)
    frontier := next
  IO.println s!"== {name}: default net tax {base}; {seen.size} lawful plans, depth {depth}"
  showPlan f d
  let ranked := (fam.toList.filter (fun e => e.2.1 < base)).toArray.qsort (fun x y => x.2.1 < y.2.1)
  let mut shown := 0
  for (k, (t, q)) in ranked do
    -- a family is listed only if it beats every family that uses a strict subset of its choices
    let tags := k.splitOn "+"
    let dominated := ranked.any (fun e =>
      let ts := e.1.splitOn "+"
      ts.length < tags.length && ts.all tags.contains && e.2.1 ≤ t)
    if !dominated && shown < 12 then
      shown := shown + 1
      IO.println s!"  {base - t} better [{k}]: {semi (describe f d q)}"
      if shown ≤ 1 then showPlan f q
  -- best plan that locks no money away (no retirement contribution)
  let noRet := ranked.filter (fun e => e.2.2.preA = 0 && e.2.2.preB = 0 && e.2.2.rothA = 0 && e.2.2.rothB = 0)
  match noRet[0]? with
  | some (k, (t, q)) =>
    IO.println s!"  best without retirement saving: {base - t} better [{k}]: {semi (describe f d q)}"
    showPlan f q
  | none => IO.println "  nothing beats the default without retirement saving"
  return (ranked[0]?.map (·.2.1)).getD base

/-- Where one more dollar of A's wages raises the household's net tax by more than a dollar, default filing. -/
def cliffs (name : String) (f : Facts) (lo hi : Nat) (tweak : Plan → Plan := id) : IO Unit := do
  let net (w : Nat) : Int :=
    let g := { f with a := { f.a with wages := w } }
    total g (tweak (default g))
  let mut found : Array (Nat × Int × String) := #[]
  let mut w := lo
  while w < hi do
    if net (w + 20) - net w ≥ 16 then
      for x in [w : w + 20] do
        let j := net (x + 1) - net x
        if j ≥ 2 then
          let g0 := { f with a := { f.a with wages := x } }
          let g1 := { f with a := { f.a with wages := x + 1 } }
          let p0 : List (String × Nat) := (returns g0 (tweak (default g0))).flatMap (fun r => (compute r.2).parts)
          let p1 : List (String × Nat) := (returns g1 (tweak (default g1))).flatMap (fun r => (compute r.2).parts)
          let ch := ((p0.zip p1).filter (fun pr => pr.1.2 > pr.2.2 + 1)).map (fun pr => s!"{pr.1.1} -{pr.1.2 - pr.2.2}")
          found := found.push (x + 1, j, if ch.isEmpty then "deduction lost" else semi ch)
    w := w + 20
  IO.println s!"== cliffs, {name}: {found.size} points where $1 more of A's wages costs $2 or more"
  -- grouped by provision and size: count, first and last wage
  let mut groups : Array (String × Int × Nat × Nat × Nat) := #[]
  for (x, j, why) in found do
    match groups.findIdx? (fun g => g.1 == why && g.2.1 == j) with
    | some i => groups := groups.modify i (fun g => (g.1, g.2.1, g.2.2.1 + 1, g.2.2.2.1, x))
    | none => groups := groups.push (why, j, 1, x, x)
  for (why, j, n, first, last) in (groups.qsort (fun x y => x.2.1 > y.2.1)).toList.take 12 do
    IO.println (s!"  +${j} ({why}): {n} point(s), A wages ${first}" ++ (if n > 1 then s!" to ${last}" else ""))

/-! ### Households -/

def adult (wages : Nat) (plan fsa : Bool) : Adult :=
  { wages := wages, tips := 0, overtime := 0, invest := 0, age := 35, hasPlan := plan, hasFsa := fsa }
def kid (age care : Nat) : Kid :=
  { age := age, withA := true, withB := true, care := care, tuition := 0, earned := 0, unearned := 0 }

/-- Two earners, two young children in paid care, both employers offer a dependent-care program. -/
def h1 (married : Bool) : Facts :=
  { married := married, apart := false, a := adult 60000 true true, b := adult 24000 false true,
    kids := [kid 4 9000, kid 8 5000], elder := none, aKeepsElderHome := false, marketplace := false,
    premAdult := 0, premKid := 0, adoption := 0 }

/-- No employer coverage: everyone on the Exchange, three children. -/
def h2 (married : Bool) : Facts :=
  { married := married, apart := false, a := adult 78000 false false, b := adult 30000 false false,
    kids := [kid 3 4000, kid 9 0, kid 15 0], elder := none, aKeepsElderHome := false, marketplace := true,
    premAdult := 6600, premKid := 3900, adoption := 0 }

/-- Tipped and overtime workers, one child, A's parent in a separate home that A pays for. -/
def h3 (married : Bool) : Facts :=
  { married := married, apart := false,
    a := { adult 52000 false false with tips := 24000 },
    b := { adult 46000 false false with tips := 15000, overtime := 6000 },
    kids := [kid 10 0], elder := some { income := 0, inMainHome := false }, aKeepsElderHome := true,
    marketplace := false, premAdult := 0, premKid := 0, adoption := 0 }

/-- The adults live apart; both children live with B; everyone is on the Exchange. -/
def h4 (married : Bool) : Facts :=
  { married := married, apart := true, a := adult 95000 true false, b := adult 40000 false true,
    kids := [{ kid 5 6000 with withA := false }, { kid 11 0 with withA := false }], elder := none,
    aKeepsElderHome := false, marketplace := true, premAdult := 6600, premKid := 3900, adoption := 0 }

/-- A college student with a job, and a younger child with investment income. -/
def h5 (married : Bool) : Facts :=
  { married := married, apart := false, a := adult 98000 true false, b := adult 72000 true false,
    kids := [{ kid 19 0 with tuition := 9000, earned := 14000 }, { kid 15 0 with unearned := 6000 }], elder := none,
    aKeepsElderHome := false, marketplace := false, premAdult := 0, premKid := 0, adoption := 0 }

/-- An adoption by both adults, final this year, $20,000 of expenses. -/
def h6 (married : Bool) : Facts :=
  { married := married, apart := false, a := adult 38000 false false, b := adult 34000 false false,
    kids := [kid 2 0], elder := none, aKeepsElderHome := false, marketplace := false, premAdult := 0, premKid := 0,
    adoption := 20000 }

/-- A's parent lives with them; A earns less; everyone but the parent is on the Exchange. -/
def h7 (married : Bool) : Facts :=
  { married := married, apart := false, a := adult 30000 false false, b := adult 68000 false false,
    kids := [kid 6 0], elder := some { income := 0, inMainHome := true }, aKeepsElderHome := false,
    marketplace := true, premAdult := 6600, premKid := 3900, adoption := 0 }

/-- Two older adults, no children, A's parent lives with them; both adults are on the Exchange. -/
def h8 (married : Bool) : Facts :=
  { married := married, apart := false, a := { adult 20000 false false with age := 62 },
    b := { adult 80000 false false with age := 60 },
    kids := [], elder := some { income := 0, inMainHome := true }, aKeepsElderHome := false,
    marketplace := true, premAdult := 13200, premKid := 0, adoption := 0 }

def pair (name : String) (h : Bool → Facts) : IO Unit := do
  let u ← search (name ++ " unmarried") (h false)
  let m ← search (name ++ " married") (h true)
  IO.println s!"## {name}: best unmarried {u}, best married {m}; marrying costs {m - u}"

#eval show IO Unit from do
  let t0 ← IO.monoMsNow
  pair "H1" h1
  pair "H2" h2
  pair "H3" h3
  pair "H4" h4
  pair "H5" h5
  pair "H6" h6
  pair "H7" h7
  pair "H8" h8
  let t1 ← IO.monoMsNow
  cliffs "H1 married" (h1 true) 0 200000
  cliffs "H2 married" (h2 true) 0 200000
  cliffs "H4 unmarried" (h4 false) 0 200000
  cliffs "H3 unmarried" (h3 false) 0 200000
  cliffs "H1 married, each spouse puts $2,000 in a Roth IRA" (h1 true) 30000 200000
    (fun p => { p with rothA := 2000, rothB := 2000 })
  let t2 ← IO.monoMsNow
  IO.println s!"search {t1 - t0} ms, cliffs {t2 - t1} ms"

end Legal.USTax.Hunt.Household
