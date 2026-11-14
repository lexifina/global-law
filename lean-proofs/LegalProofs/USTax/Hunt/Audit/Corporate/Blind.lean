import Std
/-!
Blind replication, name = Corporate.
Provisions encoded: §1202 (a),(b),(c),(d),(e)(5),(h)(4),(i); §351(a); §358(a); §368(c); §1223(1)-(2);
§1(h)(4),(7) as rates; §1411(a)(1),(c)(1)(A)(iii) as a rate.
Unit of stock: one fifth of C (worth $8,000,000, basis $0), or the N stock issued for one such fifth.
-/
namespace Legal.USTax.Hunt.Audit.Corporate.Blind

def fifth : Nat := 8000000          -- fair value of one fifth of C; basis is 0, so gain = value
def dollarLimit : Nat := 15000000   -- §1202(b)(4)(B): stock acquired after the applicable date
def basisPerUnit : Nat := 0         -- §358(a)(1): N stock takes the basis of the C stock exchanged (0)

/-- Per-issuer ledger for §1202(b). -/
structure Issuer where
  prior : Nat := 0   -- (b)(4)(B)(i): eligible gain taken into account under (a) in prior years, this issuer
  cur   : Nat := 0   -- eligible gain (b)(2) of the current year from dispositions of this issuer's stock
  curBasis : Nat := 0 -- (b)(1)(B): aggregate adjusted bases of this issuer's QSBS disposed of this year
  hit   : Bool := false -- (b)(5)(B): limit was exceeded in an earlier year, so the limit is zero afterwards
deriving BEq, Hashable, Repr

structure State where
  year : Nat := 1        -- 1, 2; 3 = both years closed
  cA   : Nat := 5        -- fifths of C held by A (QSBS, >5 years, 100% applicable percentage (a)(1)(B),(a)(5))
  nC   : Nat := 0        -- fifths of C held by N
  nQ   : Nat := 0        -- N units held by A treated as QSBS under (h)(4)(A) (basis 0)
  nU   : Nat := 0        -- N units held by A from a §351 exchange failing (h)(4)(D): not QSBS (basis 0)
  nB   : Nat := 0        -- N units held by A received in a taxable exchange (basis = value; §351 failed)
  nOut : Nat := 0        -- N units held by buyers
  isC  : Issuer := {}    -- ledger for stock issued by C
  isN  : Issuer := {}    -- ledger for stock issued by N
  other : Nat := 0       -- current-year gain to which §1202 does not apply
  taxable : Nat := 0     -- gain included in gross income, closed years
deriving BEq, Hashable, Repr

inductive Move where
  | sellC            -- sell one fifth of C (§1202(a)(1)(B))
  | transfer (k : Nat) -- transfer k fifths of C to N for N stock (§351(a))
  | sellNQ | sellNU | sellNB -- sell one unit of N stock of the given kind
  | nextYear
deriving BEq, Hashable, Repr

/-- §1202(b)(1): gain taken into account under (a) for the year is capped at the greater of
(A) the applicable dollar limit and (B) ten times the bases disposed of. -/
def closeIssuer (i : Issuer) : Issuer × Nat :=
  let limA := if i.hit then 0 else dollarLimit - i.prior            -- (b)(4)(B), (b)(5)(B)
  let lim := max limA (10 * i.curBasis)                              -- (b)(1)(A)/(B)
  let taken := min i.cur lim
  ({ prior := i.prior + taken, cur := 0, curBasis := 0, hit := i.hit || i.cur > limA }, i.cur - taken)

def step (s : State) : Move → Option State
  | .sellC =>
    if s.year ≤ 2 ∧ s.cA ≥ 1 then
      some { s with cA := s.cA - 1,
                    isC := { s.isC with cur := s.isC.cur + fifth, curBasis := s.isC.curBasis + basisPerUnit } }
    else none
  | .transfer k =>
    if s.year ≤ 2 ∧ k ≥ 1 ∧ k ≤ s.cA then
      let aN := s.nQ + s.nU + s.nB + k           -- A's N units immediately after
      let tot := aN + s.nOut
      -- §351(a) + §368(c): transferor holds at least 80% of N immediately after the exchange
      if aN * 5 ≥ tot * 4 then
        -- no gain recognised; §358(a)(1) basis 0; §1223(1) tacked holding period.
        -- §1202(h)(4)(D): N must own control (§368(c): at least 80%) of C immediately after.
        if s.nC + k ≥ 4 then
          some { s with cA := s.cA - k, nC := s.nC + k, nQ := s.nQ + k }   -- (h)(4)(A)
        else
          -- (c)(1)(B)(i): stock acquired for stock is not QSBS; (h)(4) does not rescue it
          some { s with cA := s.cA - k, nC := s.nC + k, nU := s.nU + k }
      else
        -- §351 does not apply: taxable exchange of C stock (a "sale or exchange" under §1202(a));
        -- N stock received has basis = value and is not QSBS.
        some { s with cA := s.cA - k, nC := s.nC + k, nB := s.nB + k,
                      isC := { s.isC with cur := s.isC.cur + k * fifth,
                                          curBasis := s.isC.curBasis + k * basisPerUnit } }
    else none
  | .sellNQ =>
    if s.year ≤ 2 ∧ s.nQ ≥ 1 then
      -- (h)(4)(B): §1202 applies only up to the gain built in at the transfer (value - basis = fifth),
      -- unless N was itself a qualified small business then. Value is unchanged, so the cap equals the gain.
      let elig := min fifth (fifth - basisPerUnit)
      some { s with nQ := s.nQ - 1, nOut := s.nOut + 1, other := s.other + (fifth - elig),
                    isN := { s.isN with cur := s.isN.cur + elig, curBasis := s.isN.curBasis + basisPerUnit } }
    else none
  | .sellNU =>
    if s.year ≤ 2 ∧ s.nU ≥ 1 then
      some { s with nU := s.nU - 1, nOut := s.nOut + 1, other := s.other + fifth }
    else none
  | .sellNB =>
    if s.year ≤ 2 ∧ s.nB ≥ 1 then some { s with nB := s.nB - 1, nOut := s.nOut + 1 } else none
  | .nextYear =>
    if s.year ≤ 2 then
      let (c, xc) := closeIssuer s.isC
      let (n, xn) := closeIssuer s.isN
      some { s with year := s.year + 1, isC := c, isN := n, other := 0,
                    taxable := s.taxable + xc + xn + s.other }
    else none

def allMoves : List Move :=
  [.sellC, .transfer 1, .transfer 2, .transfer 3, .transfer 4, .transfer 5, .sellNQ, .sellNU, .sellNB, .nextYear]

/-- §1(h): no "section 1202 gain" ((h)(7)) arises because the percentage limitation is 100%, so the
included gain is taxed at 20%, plus §1411(a)(1) 3.8% on net gain taken into account in taxable income. -/
def tax (taxable : Nat) : Nat := taxable * 238 / 1000

def terminal (s : State) : Bool := s.year == 3 && s.cA == 0 && s.nQ == 0 && s.nU == 0 && s.nB == 0

partial def bfs (frontier : List (State × List Move)) (seen : Std.HashSet State)
    (done : List (State × List Move)) : Nat × List (State × List Move) :=
  match frontier with
  | [] => (seen.size, done)
  | _ =>
    let (next, seen', done') := frontier.foldl (init := ([], seen, done)) fun (nx, sn, dn) (s, p) =>
      allMoves.foldl (init := (nx, sn, dn)) fun (nx, sn, dn) m =>
        match step s m with
        | none => (nx, sn, dn)
        | some t =>
          if sn.contains t then (nx, sn, dn)
          else
            let p' := p ++ [m]
            (((t, p') :: nx), sn.insert t, if terminal t then (t, p') :: dn else dn)
    bfs next seen' done'

def baselinePlan : List Move := [.sellC, .sellC, .sellC, .sellC, .sellC, .nextYear, .nextYear]

def run (p : List Move) : Option State := p.foldlM step ({} : State)

def main : IO Unit := do
  let s0 : State := {}
  let (n, done) := bfs [(s0, [])] ((Std.HashSet.emptyWithCapacity 1024).insert s0) []
  IO.println s!"positions: {n}; terminal positions: {done.length}"
  match run baselinePlan with
  | some b => IO.println s!"baseline: taxable {b.taxable}, tax {tax b.taxable}"
  | none => IO.println "baseline failed"
  match run [.transfer 4, .sellC, .sellNQ, .sellNQ, .sellNQ, .sellNQ, .nextYear, .nextYear] with
  | some b => IO.println s!"simple holding plan (transfer 4, sell 1 C, sell N): taxable {b.taxable}, tax {tax b.taxable}"
  | none => IO.println "simple plan failed"
  match run [.sellC, .sellC, .nextYear, .sellC, .sellC, .sellC, .nextYear] with
  | some b => IO.println s!"split over two years, no corporation: taxable {b.taxable}, tax {tax b.taxable}"
  | none => IO.println "split plan failed"
  let sorted := done.mergeSort (fun a b => a.1.taxable ≤ b.1.taxable)
  let mut last : Option Nat := none
  for (s, p) in sorted do
    if last != some s.taxable then
      let cnt := (sorted.filter (fun x => x.1.taxable == s.taxable)).length
      IO.println s!"tax {tax s.taxable} (taxable {s.taxable}, excluded {5 * fifth - s.taxable}) : {cnt} terminal positions; e.g. {repr p}"
      last := some s.taxable
  IO.println "-- all terminal positions at the minimum:"
  match sorted.head? with
  | some (b, _) =>
    for (s, p) in sorted do
      if s.taxable == b.taxable then IO.println s!"  {repr p}"
  | none => pure ()

#eval main

end Legal.USTax.Hunt.Audit.Corporate.Blind
