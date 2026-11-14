import Std
/-!
Blind replication `Residence`: §877A, §877(a)(2),(e), §7701(b)(1)-(3),(6),(10), §2801, §871(a)(2), §897(a) (outline),
§1(h) as flat 20% + §1411 3.8% for residents.  Self-contained; amounts in whole dollars.
-/
namespace Legal.USTax.Hunt.Audit.Residence.Blind

/-! ## Figures (task-given unless marked) -/
def value : Nat := 1100000          -- stock FMV
def basis0 : Nat := 100000          -- stock basis
def netWorth : Nat := 1500000
def avgTax : Nat := 60000
def exclusion877A : Nat := 890000   -- §877A(a)(3), 2025
def avgTaxLimit : Nat := 206000     -- §877(a)(2)(A), 2025
def netWorthLimit : Nat := 2000000  -- §877(a)(2)(B)
def lprYears : Nat := 12
def annualExcl2503b : Nat := 19000  -- JUDGMENT: §2503(b) 2025 figure, not in task
def nChildren : Nat := 2            -- JUDGMENT: "children" = 2 recipients
def horizon : Nat := 3

/-- per-mille of an amount -/
def pm (rate amt : Nat) : Nat := amt * rate / 1000
def residentRate : Nat := 238       -- §1(h) flat 20% + §1411 3.8%
def rate877b : Nat := 200           -- §7701(b)(10) -> §877(b): §1 rates, flat 20% (JUDGMENT: no §1411 on a nonresident)
def rate871a2 : Nat := 300          -- §871(a)(2)
def rate2801 : Nat := 400           -- §2801(a)(1): highest §2001(c) rate (JUDGMENT: 40%, not in list)

/-- §2801(a),(c): tax on the recipients for a covered gift or bequest of value `v`. -/
def tax2801 (v : Nat) : Nat := pm rate2801 (v - min v (annualExcl2503b * nChildren))

/-- §877(e)(2): long-term resident = LPR in at least 8 of the 15 taxable years ending with the year of the event. -/
def longTermResident (yearsSoFar : Nat) : Bool := decide (min 15 yearsSoFar ≥ 8)

/-- §877A(g)(1)(A) with §877(a)(2)(A),(B),(C).  The (g)(1)(B) exceptions are for dual citizens at birth / minors
    relinquishing citizenship; P is neither. -/
def coveredTest (certifies : Bool) : Bool :=
  decide (avgTax > avgTaxLimit) || decide (netWorth ≥ netWorthLimit) || !certifies

structure S where
  year : Nat := 1
  opened : Bool := false
  inUS : Bool := true
  hasCard : Bool := true
  surrYear : Nat := 0        -- 0 = never
  covered : Bool := false
  stock : Nat := 0           -- 0 P holds, 1 children hold, 2 sold
  cash : Nat := 0            -- 0 none, 1 P holds, 2 children hold
  basis : Nat := basis0      -- P's basis incl. the §877A(a)(2) "proper adjustment"
  kidsBasis : Nat := 0
  tax : Nat := 0
  tailGain : Nat := 0        -- gain realised in the post-surrender part of the surrender year while abroad (§7701(b)(2)(B) pending)
  tailGift : Nat := 0        -- gift made in that same pending portion by a covered expatriate
  nra : Nat := 0             -- gain realised while nonresident, exposed to §7701(b)(10)
  unlisted : Bool := false   -- plan relies on a basis rule outside the listed provisions (§1014/§1015)
  done : Bool := false
  deriving BEq, Hashable, Repr

inductive Move where
  | open (inUS : Bool)       -- presence for the year: all year in the US / all year abroad
  | giveUp (certify : Bool)  -- cease to be LPR (§7701(b)(6)); make or decline the §877(a)(2)(C) certification
  | sell
  | giftStock
  | giftCash
  | kidsSell
  | endYear
  | die
  deriving BEq, Hashable, Repr

/-- Residence at this moment. 0 resident, 1 pending (last-year rule), 2 nonresident alien.
  §7701(b)(1)(A)(i): LPR at any time in the calendar year -> resident for the year.
  §7701(b)(1)(A)(ii)+(3): present all year (>=183 days) -> resident, card or no card.
  §7701(b)(2)(B): in the surrender year, the part after the last LPR day is nonresident iff closer connection abroad
  (JUDGMENT: abroad all year = closer connection) AND not resident at any time in the next calendar year (pending).
  Otherwise no card + abroad all year (0 days < 31, (3)(A)(i)) -> nonresident alien. -/
def status (s : S) : Nat :=
  if s.hasCard then 0 else if s.inUS then 0 else if s.surrYear == s.year then 1 else 2

/-- Resolve the pending tail: `resNext` = resident at any time in the next calendar year. -/
def resolveTail (s : S) (resNext : Bool) : S :=
  if resNext then
    -- §877A(g)(1)(C): not covered for §2801 while taxed as resident
    { s with tax := s.tax + pm residentRate s.tailGain, tailGain := 0, tailGift := 0 }
  else
    { s with nra := s.nra + s.tailGain,
             tax := s.tax + (if s.covered then tax2801 s.tailGift else 0),
             tailGain := 0, tailGift := 0 }

/-- §2801(e)(1) with §877A(g)(1)(C): is a transfer made now a covered gift/bequest?  returns (tax now, pending value) -/
def giftTax (s : S) (v : Nat) : Nat × Nat :=
  if !s.covered then (0, 0)
  else match status s with
    | 0 => (0, 0)
    | 1 => (0, v)
    | _ => (tax2801 v, 0)

def finish (s : S) : S := { resolveTail s false with done := true }

def step (s : S) : Move → Option S
  | .open us =>
    if s.opened || s.done then none else
      let s1 := resolveTail s (us || s.hasCard)
      -- §7701(b)(10): resident >=3 consecutive years, ceased, resident again before close of 3rd following year:
      -- intervening period taxed as in §877(b).
      let s2 := if us && !s1.hasCard && s1.nra > 0 then { s1 with tax := s1.tax + pm rate877b s1.nra, nra := 0 } else s1
      some { s2 with opened := true, inUS := us }
  | .giveUp cert =>
    if !s.opened || s.done || !s.hasCard then none else
      -- §877A(g)(2)(B),(3)(B): expatriate only if a long-term resident
      let ltr := longTermResident (lprYears + s.year)
      let cov := ltr && coveredTest cert
      let s1 := { s with hasCard := false, surrYear := s.year, covered := cov }
      if cov && s.stock == 0 then
        -- §877A(a)(1) deemed sale the day before (P is resident that day); (a)(3) exclusion;
        -- (a)(2) flush: later gain adjusted by the gain taken into account "without regard to paragraph (3)".
        let gain := value - s.basis
        let incl := gain - min gain exclusion877A
        some { s1 with tax := s1.tax + pm residentRate incl, basis := value }
      else some s1
  | .sell =>
    if !s.opened || s.done || s.stock != 0 then none else
      let gain := value - s.basis
      let s1 := { s with stock := 2, cash := 1 }
      match status s with
      | 0 => some { s1 with tax := s1.tax + pm residentRate gain }
      | 1 => some { s1 with tailGain := s1.tailGain + gain }
      | _ => -- §871(a)(2) only if present >=183 days; §897(a): stock assumed not a US real property interest
        some { s1 with tax := s1.tax + (if s.inUS then pm rate871a2 gain else 0), nra := s1.nra + gain }
  | .giftStock =>
    if !s.opened || s.done || s.stock != 0 then none else
      let (t, p) := giftTax s value
      some { s with stock := 1, kidsBasis := s.basis, unlisted := true, tax := s.tax + t, tailGift := s.tailGift + p }
  | .giftCash =>
    if !s.opened || s.done || s.cash != 1 then none else
      let (t, p) := giftTax s value
      some (finish { s with cash := 2, tax := s.tax + t, tailGift := s.tailGift + p })
  | .kidsSell =>
    if !s.opened || s.done || s.stock != 1 then none else
      some (finish { s with stock := 2, cash := 2, tax := s.tax + pm residentRate (value - s.kidsBasis) })
  | .endYear =>
    if !s.opened || s.done || s.year ≥ horizon then none else
      some { s with year := s.year + 1, opened := false }
  | .die =>
    if !s.opened || s.done then none else
      if s.cash == 1 then
        -- §2801(e)(1)(B): covered expatriate "immediately before such death"; pending tail resolves nonresident (no next year)
        let st := status s
        let s1 := resolveTail s false
        let t := if s.covered && st != 0 then tax2801 value else 0
        some { s1 with cash := 2, tax := s1.tax + t, done := true }
      else if s.stock == 0 then
        let st := status s
        let s1 := resolveTail s false
        let t := if s.covered && st != 0 then tax2801 value else 0
        -- children then sell; basis at death = FMV is §1014, OUTSIDE the listed provisions
        some { s1 with stock := 2, cash := 2, tax := s1.tax + t, unlisted := true, done := true }
      else none

def allMoves : List Move :=
  [.open true, .open false, .giveUp true, .giveUp false, .sell, .giftStock, .giftCash, .kidsSell, .endYear, .die]

partial def search (s : S) (path : List Move) (seen : Std.HashSet S) (acc : Array (List Move × S)) :
    Std.HashSet S × Array (List Move × S) := Id.run do
  let mut seen := seen.insert s
  let mut acc := acc
  if s.done then return (seen, acc.push (path.reverse, s))
  for m in allMoves do
    match step s m with
    | some s' =>
      let (se, ac) := search s' (m :: path) seen acc
      seen := se; acc := ac
    | none => pure ()
  return (seen, acc)

def mv : Move → String
  | .open true => "inUS" | .open false => "abroad" | .giveUp true => "giveUp+certify" | .giveUp false => "giveUp+noCert"
  | .sell => "sell" | .giftStock => "giftStock" | .giftCash => "giftCash" | .kidsSell => "kidsSell"
  | .endYear => "|" | .die => "die"

def showPlan (p : List Move) : String := " ".intercalate (p.map mv)

def report (title : String) (plans : Array (List Move × S)) : IO Unit := do
  IO.println s!"--- {title}: {plans.size} complete plans"
  let sorted := plans.qsort (fun a b => a.2.tax < b.2.tax || (a.2.tax == b.2.tax && a.1.length < b.1.length))
  let mut last : Option Nat := none
  let mut shown := 0
  for (p, s) in sorted do
    if last != some s.tax then
      last := some s.tax; shown := 0
      IO.println s!"tax {s.tax}  (count {(sorted.filter (fun q => q.2.tax == s.tax)).size})"
    if shown < 3 then
      IO.println s!"    {showPlan p}"
      shown := shown + 1

def baselinePlan : List Move := [.open true, .sell, .die]
def run (p : List Move) : Option S := p.foldlM step ({} : S)

#eval do
  let (seen, plans) := search {} [] {} #[]
  IO.println s!"positions (distinct states) {seen.size}, complete plans {plans.size}"
  IO.println s!"baseline {showPlan baselinePlan} -> {(run baselinePlan).map S.tax}"
  report "TIER 1 (listed provisions only: P sells, cash passes)" (plans.filter (fun q => !q.2.unlisted))
  report "TIER 1, in the US all year every year" (plans.filter (fun q => !q.2.unlisted && !q.1.contains (.open false)))
  report "TIER 2 (uses §1014/§1015 basis, outside the list)" (plans.filter (fun q => q.2.unlisted))

end Legal.USTax.Hunt.Audit.Residence.Blind
