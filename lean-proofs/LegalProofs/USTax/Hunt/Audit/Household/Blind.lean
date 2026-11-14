import Std
/-!
Blind replication `Household`: adoption credit (§23) for two adults who jointly adopt one child.
Money is in cents. Self-contained; `import Std` only.
-/
namespace Legal.USTax.Hunt.Audit.Household.Blind

/-- §23(b)(1) dollar limit as indexed for 2025 (given). -/
def limit23 : Int := 1728000
/-- §23(a)(4) refundable amount, as in the text. -/
def refundable23 : Int := 500000
def wagesA : Int := 3800000
def wagesB : Int := 3400000
def totalQAE : Nat := 20   -- thousands

inductive Status | unset | single | hoh | joint | separate
  deriving BEq, Hashable, Repr, DecidableEq
inductive Who | nobody | a | b
  deriving BEq, Hashable, Repr, DecidableEq

/-- §63 standard deduction, 2025 figures (given). -/
def stdDed : Status → Int
  | .single => 1575000 | .separate => 1575000 | .hoh => 2362500 | .joint => 3150000 | .unset => 0

/-- §1(j) brackets 2025: upper bounds of the 10%, 12% and 22% bands. -/
def bands : Status → Int × Int × Int
  | .joint => (2385000, 9695000, 20670000)
  | .hoh   => (1700000, 6485000, 10335000)
  | _      => (1192500, 4847500, 10335000)

def taxOn (s : Status) (wages : Int) : Int :=
  let ti := max 0 (wages - stdDed s)
  let (b1, b2, b3) := bands s
  let p1 := min ti b1
  let p2 := max 0 (min ti b2 - b1)
  let p3 := max 0 (min ti b3 - b2)
  (p1 * 10 + p2 * 12 + p3 * 22) / 100   -- incomes here never pass the 22% band

structure State where
  married     : Bool
  /-- variant: §23(i) regulations treat unmarried co-adopters as 1 taxpayer for the (b)(1) amount -/
  sharedLimit : Bool
  stage       : Nat := 0
  paidA       : Nat := 0          -- thousands paid by A; B pays the rest
  dep         : Who := .nobody
  statA       : Status := .unset
  statB       : Status := .unset
  allocA      : Int := 0          -- A's share of a shared (b)(1) limit, cents
  deriving BEq, Hashable, Repr

inductive Move
  | split (aThousands : Nat)     -- who pays: §23(a)(1) "paid or incurred by the taxpayer"
  | claim (w : Who)              -- who claims the child as dependent
  | fileJoint                    -- §6013(a)
  | fileSeparate                 -- §6013(a) "may"; §21(e)(2) via §23(f)(1) then denies the credit
  | fileA (s : Status)           -- unmarried: single, or head of household if A claims the child
  | fileB (s : Status)
  | alloc (aCents : Int)         -- shared-limit variant only: division of the one (b)(1) amount
  deriving BEq, Hashable, Repr

def step (s : State) (m : Move) : Option State :=
  match s.stage, m with
  | 0, .split k => if k ≤ totalQAE then some { s with paidA := k, stage := 1 } else none
  | 1, .claim w => some { s with dep := w, stage := 2 }
  | 2, .fileJoint =>
      -- §6013(a): only a husband and wife may make a joint return
      if s.married then some { s with statA := .joint, statB := .joint, stage := 9 } else none
  | 2, .fileSeparate =>
      -- §7703(b)/§21(e)(4) cannot apply: the spouse is a member of the household all year, so no HoH
      if s.married then some { s with statA := .separate, statB := .separate, stage := 9 } else none
  | 2, .fileA st =>
      if s.married then none
      else if st == .single || (st == .hoh && s.dep == .a) then some { s with statA := st, stage := 3 } else none
  | 3, .fileB st =>
      if st == .single || (st == .hoh && s.dep == .b) then
        some { s with statB := st, stage := if s.sharedLimit then 4 else 9 }
      else none
  | 4, .alloc a => if 0 ≤ a && a ≤ limit23 then some { s with allocA := a, stage := 9 } else none
  | _, _ => none

def allMoves : List Move :=
  (List.range (totalQAE + 1)).map .split ++
  [.claim .nobody, .claim .a, .claim .b, .fileJoint, .fileSeparate,
   .fileA .single, .fileA .hoh, .fileB .single, .fileB .hoh] ++
  ((List.range 18).map fun (k : Nat) => Move.alloc (Int.ofNat k * 100000)) ++ [.alloc limit23]

structure Outcome where
  net   : Int   -- combined income tax, less nonrefundable credit used, less refundable credit (cash)
  carry : Int   -- §23(c) carryforward, reported separately
  taxBefore : Int
  refund : Int
  deriving BEq, Hashable, Repr

/-- One taxpayer's §23 computation: (nonrefundable used, refundable, carryforward). -/
def credit (qae lim tax : Int) : Int × Int × Int :=
  let c := min qae lim                 -- §23(a)(1), (b)(1); (b)(2) phase-out not reached
  let r := min c refundable23          -- §23(a)(4): "so much ... as does not exceed $5,000" → subpart C
  let nr := c - r                      -- remains a subpart A credit
  let used := min nr tax               -- §26(a): limited to regular tax liability (no §27, no §55 here)
  (used, r, nr - used)                 -- §23(c)(1): excess carried to the succeeding year

def eval (s : State) : Outcome :=
  let pa : Int := (s.paidA : Int) * 100000
  let pb : Int := ((totalQAE - s.paidA : Nat) : Int) * 100000
  if s.statA == .joint then
    let tax := taxOn .joint (wagesA + wagesB)
    let (u, r, cf) := credit (pa + pb) limit23 tax     -- joint return: one taxpayer, one limit, one $5,000
    { net := tax - u - r, carry := cf, taxBefore := tax, refund := r }
  else if s.statA == .separate then
    let tax := taxOn .separate wagesA + taxOn .separate wagesB
    { net := tax, carry := 0, taxBefore := tax, refund := 0 }  -- §21(e)(2): credit "only if" joint return
  else
    let ta := taxOn s.statA wagesA
    let tb := taxOn s.statB wagesB
    let la := if s.sharedLimit then s.allocA else limit23
    let lb := if s.sharedLimit then limit23 - s.allocA else limit23
    let (ua, ra, ca) := credit pa la ta
    let (ub, rb, cb) := credit pb lb tb
    { net := ta + tb - ua - ub - ra - rb, carry := ca + cb, taxBefore := ta + tb, refund := ra + rb }

/-- Exhaustive search over move sequences; returns terminal (plan, state). -/
partial def search (s : State) (plan : List Move) : List (List Move × State) :=
  if s.stage == 9 then [(plan.reverse, s)]
  else allMoves.foldl (fun acc m => match step s m with
    | some t => acc ++ search t (m :: plan)
    | none => acc) []

def better (x y : Outcome) : Bool := x.net < y.net || (x.net == y.net && x.carry > y.carry)

def fmt (c : Int) : String :=
  let sign := if c < 0 then "-" else ""
  let n := c.natAbs
  let cents := n % 100
  s!"{sign}${n / 100}.{if cents < 10 then "0" else ""}{cents}"

def isBaseline (s : State) : Bool := s.paidA == 0 || s.paidA == totalQAE

def report (name : String) (init : State) : IO Unit := do
  let terms := search init []
  let mut seen : Std.HashSet State := {}
  let mut uniq : Array (List Move × State) := #[]
  for (p, s) in terms do
    if !seen.contains s then
      seen := seen.insert s
      uniq := uniq.push (p, s)
  IO.println s!"== {name}: {uniq.size} distinct terminal positions"
  let sorted := uniq.qsort (fun x y => better (eval x.2) (eval y.2))
  let base := sorted.filter (fun x => isBaseline x.2)
  match base[0]? with
  | some (p, s) =>
      let o := eval s
      IO.println s!"  baseline (one adult pays all, best other choices): net {fmt o.net} carry {fmt o.carry}  {repr p}"
  | none => pure ()
  match (base.filter (fun x => x.2.statA != .hoh && x.2.statB != .hoh && x.2.statA != .separate))[0]? with
  | some (_, s) =>
      let o := eval s
      IO.println s!"  baseline (one adult pays all, no head-of-household): net {fmt o.net} carry {fmt o.carry}"
  | none => pure ()
  let mut fams : Array (Outcome × Nat × List Move) := #[]
  for (p, s) in sorted do
    let o := eval s
    match fams.findIdx? (fun f => f.1 == o) with
    | some i => fams := fams.modify i (fun f => (f.1, f.2.1 + 1, f.2.2))
    | none => fams := fams.push (o, 1, p)
  IO.println s!"  {fams.size} distinct outcomes; top 8:"
  for (o, n, p) in fams.toList.take 8 do
    IO.println s!"   net {fmt o.net} carry {fmt o.carry} (tax before credit {fmt o.taxBefore}, refundable {fmt o.refund}) x{n}  e.g. {repr p}"
  IO.println "  best by A's share (thousands): "
  for k in List.range (totalQAE + 1) do
    match (sorted.filter (fun x => x.2.paidA == k))[0]? with
    | some (_, s) => let o := eval s; IO.println s!"    A={k}k: net {fmt o.net} carry {fmt o.carry}"
    | none => pure ()

#eval report "MARRIED" { married := true, sharedLimit := false }
#eval report "UNMARRIED, statute text only (each individual a taxpayer)" { married := false, sharedLimit := false }
#eval report "UNMARRIED, variant: §23(i) regulation shares the (b)(1) amount" { married := false, sharedLimit := true }

end Legal.USTax.Hunt.Audit.Household.Blind
