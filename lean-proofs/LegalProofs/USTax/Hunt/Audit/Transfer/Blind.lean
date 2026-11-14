import Std
/-!
Blind replication `Transfer`: estate / gift / GST position of a widow W holding a QTIP income interest.
Self-contained. Dollars are `Nat`. Rate 40% flat (task figure); exclusion and GST exemption $15,000,000 each.
One calendar year of lifetime moves, then W dies.
-/
namespace Legal.USTax.Hunt.Audit.Transfer.Blind

def M : Nat := 1000000
def exclusion : Nat := 15 * M          -- §2010(c)(3), §2631(c) (task figure)
def trustValue : Nat := 100 * M        -- QTIP trust; §2056(b)(7) deduction taken by H's estate
def wOwn : Nat := 10 * M

/-- §2001(c) at the task rate: tentative tax. -/
def tent (x : Nat) : Nat := x * 2 / 5
/-- §2010(c)(1) / §2505(a)(1): applicable credit amount = tentative tax on the exclusion.
    W has no DSUE (§2010(c)(4): H's exclusion was used up; N does not die). -/
def credit : Nat := tent exclusion
/-- §2502(a) + §2505(a),(c): gift tax payable on total taxable gifts `g` (Nat subtraction floors at 0). -/
def giftTax (g : Nat) : Nat := tent g - credit

/-- Parameters that the text does not fix. -/
structure Cfg where
  /-- value of W's qualifying income interest (the position gives no age; 0 = worthless at once) -/
  incomeVal : Nat
  /-- reading of §2207A(b): does recovery reach the tax on the half that §2513 attributes to N? -/
  broadRecovery : Bool
  deriving Repr

inductive Recip | C | G | TrustG deriving BEq, Hashable, Repr
/-- §2613(a)(1), (a)(2)(A): a grandchild, or a trust all interests in which are held by grandchildren. -/
def Recip.skip : Recip → Bool
  | .C => false
  | _ => true
def Recip.name : Recip → String
  | .C => "C"
  | .G => "G"
  | .TrustG => "a trust for G"

/-- A disposition of the income interest, §2519(a) ("all or part"). `pct` = percent of the interest given. -/
structure Disp where
  pct : Nat
  to : Recip
  whileMarried : Bool
  deriving BEq, Hashable, Repr

structure State where
  married : Bool := false
  wConsent : Bool := false          -- §2513(a)(2)
  nConsent : Bool := false          -- §2513(a)(2)
  cash : Nat := wOwn                -- W's own property not yet given
  preC : Nat := 0                   -- own gifts before marriage, to C
  preSkip : Nat := 0                -- own gifts before marriage, to G / trust for G
  postC : Nat := 0                  -- own gifts while married to N
  postSkip : Nat := 0
  disp : Option Disp := none
  wOptOut : Bool := false           -- §2632(b)(3): W elects out of deemed allocation
  nOptOut : Bool := false           -- same for N (transferor of half under §2652(a)(2))
  recoverFull : Bool := false       -- §2207A(b): recover all she is entitled to (else only the shortfall)
  dead : Bool := false
  toHeirs : Nat := 0                -- objective: reaching C and G after all tax
  taxes : Nat := 0
  deriving BEq, Hashable, Repr

inductive Move
  | marry                                   -- W marries N
  | giftOwn (to : Recip) (amt : Nat)        -- §2501, §2511
  | dispose (pct : Nat) (to : Recip)        -- §2511 (interest given) + §2519 (all other interests)
  | consentW | consentN                     -- §2513(a)(2)
  | optOutW | optOutN                       -- §2632(b)(3)
  | recoverFull                             -- §2207A(b)
  | die (bequestTo : Recip)                 -- §2001, §2044, §2207A(a); last step
  deriving Repr

def Move.name : Move → String
  | .marry => "W marries N"
  | .giftOwn r a => s!"W gives ${a} of her own property to {r.name}"
  | .dispose p r => s!"W gives {p}% of her income interest to {r.name} (s.2519 applies)"
  | .consentW => "W consents to s.2513 splitting"
  | .consentN => "N consents to s.2513 splitting"
  | .optOutW => "W elects out of deemed GST allocation"
  | .optOutN => "N elects out of deemed GST allocation"
  | .recoverFull => "W recovers all the gift tax she may from the trust (s.2207A(b))"
  | .die r => s!"W dies; own property to {r.name}"

/-- Everything is settled when W dies (one calendar year of gifts, then death). -/
def settle (cfg : Cfg) (s : State) (bequest : Recip) : Option State :=
  -- §2513(a): split only with both consents, and only gifts made while married to each other
  let split := s.married && s.wConsent && s.nConsent
  -- §2519(a): disposition of all OR PART of the income interest = transfer of all interests other than it
  let remGift := match s.disp with
    | some _ => trustValue - cfg.incomeVal
    | none => 0
  -- §2511: the part of the income interest actually given
  let incGift := match s.disp with
    | some d => cfg.incomeVal * d.pct / 100
    | none => 0
  let incSkip := match s.disp with
    | some d => d.to.skip
    | none => false
  let dMarried := match s.disp with
    | some d => d.whileMarried
    | none => false
  let pre  := s.preC + s.preSkip + (if dMarried then 0 else remGift + incGift)
  let post := s.postC + s.postSkip + (if dMarried then remGift + incGift else 0)
  let preNo  := s.preC + s.preSkip + (if dMarried then 0 else incGift)   -- without the §2519 property
  let postNo := s.postC + s.postSkip + (if dMarried then incGift else 0)
  let gW := pre + (if split then post / 2 else post)
  let gN := if split then post / 2 else 0
  let gWNo := preNo + (if split then postNo / 2 else postNo)
  let gNNo := if split then postNo / 2 else 0
  let tW := giftTax gW
  let tN := giftTax gN
  -- §2207A(b): tax for the year over the tax "if the value of such property had not been taken into account"
  let entW := tW - giftTax gWNo
  let entN := if cfg.broadRecovery then tN - giftTax gNNo else 0
  -- chapter 13: direct skips (§2612(c)); transferor = donor (§2652(a)(1)(B)), halves under §2652(a)(2)
  let skipPre  := s.preSkip + (if !dMarried && incSkip then incGift else 0)
  let skipPost := s.postSkip + (if dMarried && incSkip then incGift else 0)
  let skW := skipPre + (if split then skipPost / 2 else skipPost)
  let skN := if split then skipPost / 2 else 0
  let allocW := if s.wOptOut then 0 else min skW exclusion        -- §2632(b)(1)
  let allocN := if s.nOptOut then 0 else min skN exclusion
  let gstW := tent (skW - allocW)                                 -- §2641, §2642(a): 40% × inclusion ratio
  let gstN := tent (skN - allocN)
  -- N has no assets. §2513(d) makes W liable for N's gift tax; nothing listed makes her liable for N's GST tax.
  if gstN > 0 then none else
  let need := tW + tN + gstW
  let entitled := entW + entN
  let shortfall := need - min need s.cash
  let recov := if s.recoverFull then entitled else min entitled shortfall
  if s.cash + recov < need then none else
  let cashLeft := s.cash + recov - need
  -- death. §2044(b)(2): no inclusion once §2519 applied to a disposition of part or all.
  let trustInEstate := match s.disp with
    | some _ => 0
    | none => trustValue
  let estate := cashLeft + trustInEstate
  -- §2001(b): tentative on estate + adjusted taxable gifts, less gift tax payable, less §2010 credit
  let estTax := tent (estate + gW) - tW - credit
  -- bequest of own property to G at death: direct skip; §2632(e)(1)(A) allocates what exemption is left
  let deathSkip := if bequest.skip then cashLeft else 0
  let gstDeath := tent (deathSkip - min deathSkip (exclusion - allocW))
  let taxes := need + estTax + gstDeath
  if wOwn + trustValue < taxes then none else
  some { s with dead := true, cash := 0, taxes := taxes, toHeirs := wOwn + trustValue - taxes }

def step (cfg : Cfg) (s : State) (m : Move) : Option State :=
  if s.dead then none else
  match m with
  | .marry => if s.married then none else some { s with married := true }
  | .giftOwn r a =>
      if a == 0 || a > s.cash then none else
      let s := { s with cash := s.cash - a }
      some (match s.married, r.skip with
        | false, false => { s with preC := s.preC + a }
        | false, true  => { s with preSkip := s.preSkip + a }
        | true,  false => { s with postC := s.postC + a }
        | true,  true  => { s with postSkip := s.postSkip + a })
  | .dispose p r =>
      if s.disp.isSome || p == 0 || p > 100 then none
      else some { s with disp := some ⟨p, r, s.married⟩ }
  | .consentW => if s.married && !s.wConsent then some { s with wConsent := true } else none
  | .consentN => if s.married && !s.nConsent then some { s with nConsent := true } else none
  | .optOutW => if s.wOptOut then none else some { s with wOptOut := true }
  | .optOutN => if s.married && !s.nOptOut then some { s with nOptOut := true } else none
  | .recoverFull => if s.recoverFull then none else some { s with recoverFull := true }
  | .die r => settle cfg s r

def recips : List Recip := [.C, .G, .TrustG]

def moves : List Move :=
  [.marry, .consentW, .consentN, .optOutW, .optOutN, .recoverFull]
  ++ recips.flatMap (fun r => [Move.giftOwn r (5 * M), Move.giftOwn r (10 * M)])
  ++ recips.flatMap (fun r => [Move.dispose 100 r, Move.dispose 50 r, Move.dispose 1 r])
  ++ recips.map Move.die

/-- Breadth-first search to exhaustion, deduplicating states. Returns (positions seen, finished states with plans). -/
partial def search (cfg : Cfg) : Nat × List (State × List String) := Id.run do
  let mut seen : Std.HashSet State := {}
  let s0 : State := {}
  seen := seen.insert s0
  let mut frontier : List (State × List String) := [(s0, [])]
  let mut finished : List (State × List String) := []
  while !frontier.isEmpty do
    let mut next : List (State × List String) := []
    for (s, path) in frontier do
      for m in moves do
        match step cfg s m with
        | none => pure ()
        | some s' =>
          if !seen.contains s' then
            seen := seen.insert s'
            let p := path ++ [m.name]
            if s'.dead then finished := (s', p) :: finished else next := (s', p) :: next
    frontier := next.reverse
  return (seen.size, finished)

def baseline (cfg : Cfg) : Nat :=
  match step cfg {} (.die .C) with
  | some s => s.toHeirs
  | none => 0

/-- A coarse family label for a finished plan. -/
def family (s : State) : String :=
  let split := s.married && s.wConsent && s.nConsent
  let d := match s.disp with
    | some d => s!"dispose {d.pct}% ({if d.whileMarried then "while married" else "unmarried"})"
    | none => "no disposition"
  let g := if s.preC + s.preSkip + s.postC + s.postSkip > 0 then "own gifts" else "no own gifts"
  s!"{if split then "split" else "no split"} | {d} | {g} | {if s.recoverFull then "full recovery" else "minimal recovery"}"

def report (cfg : Cfg) : IO Unit := do
  let (n, fin) := search cfg
  let base := baseline cfg
  IO.println s!"=== incomeVal={cfg.incomeVal} broadRecovery={cfg.broadRecovery}"
  IO.println s!"positions={n} finished={fin.length} baseline={base}"
  let sorted := fin.toArray.qsort (fun a b => a.1.toHeirs > b.1.toHeirs || (a.1.toHeirs == b.1.toHeirs && a.2.length < b.2.length))
  match sorted[0]? with
  | none => IO.println "no finished plan"
  | some (s, p) =>
    IO.println s!"BEST value={s.toHeirs} gain={s.toHeirs - base} taxes={s.taxes}"
    for l in p do IO.println s!"   - {l}"
  -- best per family
  let mut famSeen : Std.HashSet String := {}
  let mut k := 0
  for (s, p) in sorted do
    let f := family s
    if !famSeen.contains f && k < 14 then
      famSeen := famSeen.insert f
      k := k + 1
      IO.println s!"  family [{f}] value={s.toHeirs} gain={(s.toHeirs : Int) - base} moves={p}"

#eval do
  for broad in [false, true] do
    for iv in [0, 20 * M, 40 * M] do
      report { incomeVal := iv, broadRecovery := broad }

end Legal.USTax.Hunt.Audit.Transfer.Blind
