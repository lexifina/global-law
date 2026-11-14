import Std

/-!
# How an owner-worker takes money out of a business (tax year 2026 figures)

Part 1 (Rules) writes down what each provision permits and what it taxes. Part 2 (Search) tries every allowed sequence.
No rule names a planning technique.

The household: married couple filing jointly (owner + spouse with no other income), one child under 18, standard
deduction, no other income. The business earns `profit` a year before anything paid to or for the family.
2026 figures (Rev. Proc. 2025-32 / Notice 2025-67 / SSA, from memory): standard deduction $32,200; joint brackets;
wage base $184,500; §199A threshold $403,500 joint with the $150,000 phase-in range that Pub. L. 119-21 starts in 2026;
§402(g) $24,500; §415(c) $72,000; §401(a)(17) $360,000.

Simplifications, each stated once:
* no investment return on retained cash (so no personal-holding-company income, §§541-543, and no §1411 income on it);
* §543(a)(7) personal-service-contract income is not modelled (a one-person service C corporation can be a PHC);
* the accumulated earnings tax (§§531-535) is applied automatically to accumulations past the credit (§533 presumption);
* S-corporation income is distributed each year (basis and AAA always cover it, §§1367-1368);
* child tax credit, AMT, itemized deductions, state tax, Social Security benefit accrual are ignored;
* §§127, 129 are left out: §127(b)(3) and §129(d)(4) cap the share going to >5% owners and their families at 5% / 25%,
  which a family-only workforce cannot meet. §119 and §132 are left out (no tax difference from a business expense).
* §461(l): no losses arise with a positive profit, so it never binds here.
-/

namespace Legal.USTax.Hunt.Entity

/-! ## Part 1. Rules -/

def wageBase : Nat := 184500      -- §3121(a)(1), §1402(b)(1): contribution and benefit base, 2026
def stdDed : Nat := 32200         -- §63(c), joint, 2026
def stdDedChild : Nat := 16100    -- §63(c)(5): a dependent's earned income up to the basic standard deduction
def addlMedThr : Nat := 250000    -- §3101(b)(2)(A), §1401(b)(2)(A)(i)
def niitThr : Nat := 250000       -- §1411(b)(1)
def qbiThr : Nat := 403500        -- §199A(e)(2), joint, 2026
def qbiRange : Nat := 150000      -- §199A(b)(3)(B), (d)(3): $150,000 joint for years after 2025 (Pub. L. 119-21)
def deferLimit : Nat := 24500     -- §402(g)(1), 2026
def addLimit : Nat := 72000       -- §415(c)(1)(A), 2026
def compCap : Nat := 360000       -- §401(a)(17), 2026
def trumpPerEmployee : Nat := 2500 -- §128(b)(1)
def trumpPerAccount : Nat := 5000  -- §530A: aggregate contributions to one account for a year

def pct (x n d : Nat) : Nat := x * n / d

/-- §1(j) as amended, joint return, 2026 brackets. -/
def ordTax (ti : Nat) : Nat :=
  let b : List (Nat × Nat × Nat) :=
    [(0, 24800, 10), (24800, 100800, 12), (100800, 211400, 22), (211400, 403550, 24), (403550, 512450, 32),
     (512450, 768700, 35)]
  let t := b.foldl (fun acc (lo, hi, r) => acc + (min ti hi - min ti lo) * r) 0
  (t + (ti - min ti 768700) * 37) / 100

/-- §1(h): net capital gain and qualified dividends (§1(h)(11)) stacked on ordinary taxable income; joint 2026. -/
def capTax (ordTI g : Nat) : Nat :=
  let z := min g (98900 - min 98900 ordTI)
  let f := min (g - z) (613700 - min 613700 (ordTI + z))
  pct f 15 100 + pct (g - z - f) 20 100

/-- §1(h)(4), (7): the part of §1202 gain not excluded is 28-percent rate gain. -/
def gain28Tax (ordTI g : Nat) : Nat := min (ordTax (ordTI + g) - ordTax ordTI) (pct g 28 100)

/-- §199A(a), (b)(2), (b)(3), (d)(3). No qualified property (the 2.5% alternative is zero). -/
def qbiDed (qbi w2 : Nat) (sstb : Bool) (ti ordTI : Nat) : Nat :=
  let d :=
    if ti ≤ qbiThr then qbi / 5
    else if ti ≥ qbiThr + qbiRange then (if sstb then 0 else min (qbi / 5) (w2 / 2))
    else
      let ex := ti - qbiThr
      let q := if sstb then qbi * (qbiRange - ex) / qbiRange else qbi
      let w := if sstb then w2 * (qbiRange - ex) / qbiRange else w2
      let a := q / 5
      let b := w / 2
      if b < a then a - (a - b) * ex / qbiRange else a
  min d (ordTI / 5)   -- §199A(a)(2): 20% of taxable income less net capital gain

/-- One half (employee or employer) of FICA on a wage, §§3101(a), (b)(1), 3111(a), (b). -/
def fica (w : Nat) : Nat := pct (min w wageBase) 62 1000 + pct w 145 10000

structure Scn where
  profit : Nat      -- yearly profit before anything paid to or for the family
  svc : Bool        -- a field named in §1202(e)(3)(A) and §535(c)(2)(B) (health, law, accounting, consulting …): so also an SSTB
  rcLo : Nat        -- value of the owner's own services (used only where `rcFloor` asks for it)
  rcHi : Nat        -- most that is a "reasonable allowance for salaries", §162(a)(1)
  health : Nat      -- family health insurance premiums, paid in every case
  homeOff : Nat     -- home-office costs, paid in every case
  rent : Nat        -- fair rent for 14 days' use of the home by the business
  childWork : Nat   -- value of services the child actually renders
  spouseWork : Nat  -- value of services the spouse actually renders
  gYear : Nat       -- goodwill the business builds each year (what a buyer pays above cash)
  years : Nat
  rcFloor : Bool    -- true: a corporation must pay the owner at least `rcLo` (Rev. Rul. 74-44, case law; not in the Code)
  lpLiteral : Bool  -- true: "limited partner" in §1402(a)(13) means a state-law limited partner even if he works
  deferRate : Nat   -- percent: assumed later tax on pre-tax retirement / Trump-account money

inductive Ent where | sp | lp | s | c
  deriving BEq, Hashable, Repr, DecidableEq

inductive Keep where
  | out      -- distribute the year's earnings
  | retain   -- distribute nothing
  | credit   -- retain only up to the §535(c) credit, distribute the rest
  | sweep    -- distribute the year's earnings and everything retained before
  deriving BEq, Hashable, Repr, DecidableEq

structure St where
  year : Nat          -- completed years
  ent : Ent
  entSet : Bool       -- an entity choice was made for the current year
  sal : Nat           -- owner's salary (corporation) or §707(c) guaranteed payment (limited partnership)
  spW : Nat
  chW : Nat
  health : Bool
  rent : Bool
  acct : Bool
  oDef : Bool
  oPS : Bool
  sDef : Bool
  sPS : Bool
  trump : Bool
  cE : Nat            -- C-corporation earnings retained (cash inside the corporation)
  cYear : Nat         -- first year (1-based) for which the stock was C-corporation stock issued by a QSB; 0 = none
  qOK : Bool          -- §1202 requirements met so far
  g0 : Nat            -- value of the business when it was put into the corporation, §1202(i)(1)(B)
  revoked : Bool      -- an S election was terminated, §1362(g)
  lastTI : Nat        -- final year's taxable income (ordinary, then capital), for stacking the sale
  lastCap : Nat
  lastMAGI : Nat
  tax : Nat           -- every federal tax paid so far by the corporation and the family
  defer : Nat         -- pre-tax money in retirement plans and Trump accounts
  done : Bool
  deriving BEq, Hashable, Repr

inductive Move where
  | choose (e : Ent)        -- §351 incorporation / §1362(a) election / §1362(d) revocation / form a limited partnership
  | salary (a : Nat)        -- §162(a)(1) salary, or §707(c) guaranteed payment
  | hireSpouse (a : Nat)    -- §162(a)(1); FICA applies (§3121(b)(3)(B) exempts only non-business service)
  | hireChild (a : Nat)     -- §162(a)(1); §3121(b)(3)(A)
  | healthPlan              -- business pays the family premiums: §§105(b), 106(a), 162(l), 1372
  | rentHome                -- business rents the home for 14 days: §162(a)(3), §280A(g)
  | acctPlan                -- reimburse home-office costs under an accountable plan: §62(a)(2)(A), (c)
  | ownerDefer              -- §401(k) elective deferral, §402(g)
  | ownerPS                 -- employer profit-sharing contribution, §404(a)(3), (a)(8), §415(c)
  | spouseDefer
  | spousePS
  | trumpAcct               -- employer contribution to the child's Trump account, §128, §530A
  | endYear (k : Keep)      -- close the year: §11, §§301/316, §§531-535, §§1366-1368
  | sell                    -- sell the business (stock, or assets of a proprietorship) after the last year
  deriving BEq, Repr

def pendingClear (s : St) : Bool :=
  s.sal == 0 && s.spW == 0 && s.chW == 0 && !s.health && !s.rent && !s.acct && !s.oDef && !s.oPS && !s.sDef &&
  !s.sPS && !s.trump

/-- Close a year. Returns `none` when the settings are not allowed. -/
def closeYear (sc : Scn) (s : St) (k : Keep) : Option St :=
  let H := sc.health
  let spF := fica s.spW
  -- §3121(b)(3)(A): service by a child under 18 "in the employ of his father or mother" is not employment. A
  -- corporation or a partnership with a non-parent partner is not the father or mother.
  let chF := if s.ent == .sp then 0 else fica s.chW
  -- spouse's plan: §402(g), §404(a)(3)(A)(i)(I) 25% of compensation, §415(c)(1)(B) 100% of compensation
  let sPSA := if s.sPS then s.spW / 4 else 0
  let sDefA := if s.sDef then min deferLimit (if s.sPS then s.spW * 3 / 4 else pct s.spW 9235 10000) else 0
  let childTax := pct (s.chW - stdDedChild) 10 100
  let common := s.spW + spF + s.chW + chF + sPSA
  let fin (corpTax payroll : Nat) (ordAGI qbi w2 qdiv nii newCE newDefer : Nat) (qOK : Bool) : Option St :=
    let ordTI0 := ordAGI - stdDed
    let cg := qdiv - (stdDed - min stdDed ordAGI)
    let q := qbiDed qbi w2 sc.svc (ordTI0 + cg) ordTI0
    let ordTI := ordTI0 - q
    let it := ordTax ordTI + capTax ordTI cg
    let magi := ordAGI + qdiv
    let niit := pct (min nii (magi - niitThr)) 38 1000          -- §1411(a)(1)
    let last := s.year + 1 == sc.years
    some { s with
      year := s.year + 1, entSet := false, sal := 0, spW := 0, chW := 0, health := false, rent := false,
      acct := false, oDef := false, oPS := false, sDef := false, sPS := false, trump := false,
      cE := newCE, qOK := qOK,
      lastTI := if last then ordTI else 0, lastCap := if last then cg else 0, lastMAGI := if last then magi else 0,
      tax := s.tax + corpTax + payroll + childTax + it + niit, defer := s.defer + newDefer }
  match s.ent with
  | .sp | .lp =>
    if k != .out || s.rent || s.acct then none else
    -- spouse-employee's family coverage is a business expense excluded from the employee's income, §§105(b), 106(a)
    -- §128(a): contribution to the Trump account "of such employee or of any dependent of such employee"; the
    -- proprietor is not an employee, the spouse-employee and the child-employee are. FICA as for a corporation,
    -- except that the child's service for a parent is not employment at all (§3121(b)(3)(A)).
    let trSp := if s.trump && s.spW > 0 then trumpPerEmployee else 0
    let trCh := if s.trump && s.chW > 0 then trumpPerEmployee else 0
    let trF := pct (trSp + (if s.ent == .sp then 0 else trCh)) 765 10000
    let ded := sc.homeOff + common + (if s.health then H else 0) + trSp + trCh + trF   -- home office: §280A(c)(1)
    if ded > sc.profit then none else
    let net := sc.profit - ded
    let gp := if s.ent == .lp then s.sal else net
    if gp > net then none else
    let share := net - gp     -- §1402(a)(13): a limited partner's distributive share is excluded
    let nese := pct gp 9235 10000                                  -- §1402(a)(12)
    let ss := pct (min nese wageBase) 124 1000                     -- §1401(a), §1402(b)(1)
    let med := pct nese 29 1000                                    -- §1401(b)(1)
    let halfSE := (ss + med) / 2                                   -- §164(f)
    let earned := gp - halfSE                                      -- §401(c)(2)(A)(vi)
    let h162 := if s.health then 0 else min H earned               -- §162(l)(1), (2)(A); not for SE tax, (l)(4)
    let oPSA := if s.oPS then min (earned / 5) addLimit else 0     -- §404(a)(8)(D): 25% of earned income net of itself
    let oDefA := if s.oDef then min deferLimit (min (earned - oPSA) (addLimit - oPSA)) else 0
    let ownDed := halfSE + h162 + oPSA + oDefA
    let addl := pct (s.spW + nese - addlMedThr) 9 1000             -- §1401(b)(2), §3101(b)(2)
    let ordAGI := gp + share + (s.spW - sDefA) - ownDed
    let qbi := (if s.ent == .lp then share else net) - ownDed      -- §199A(c)(4)(B): guaranteed payment is not QBI
    -- §1411(c)(2)(A): the owner materially participates, so the share is not net investment income
    fin 0 (ss + med + addl + 2 * spF + 2 * chF + 2 * trF) ordAGI qbi (s.spW + s.chW) 0 0 s.cE
      (oPSA + oDefA + sPSA + sDefA + trSp + trCh) s.qOK
  | .s | .c =>
    if s.sal > sc.rcHi then none else
    -- remuneration for an officer's services is wages whatever it is called (§3121(a), (d)(1)); read conservatively,
    -- any corporation must pay the owner-worker at least the value of his services
    if sc.rcFloor && s.sal < sc.rcLo then none else
    let salF := fica s.sal
    let oPSA := if s.oPS then min (min s.sal compCap / 4) addLimit else 0
    let oDefA := if s.oDef then min deferLimit (min (if s.oPS then s.sal * 3 / 4 else pct s.sal 9235 10000) (addLimit - oPSA)) else 0
    -- §128: only for an "employee"; §1372 treats a 2-percent S shareholder as a partner for fringe benefits, and
    -- §1372(b) counts stock owned under §318, so the owner's spouse and child are 2-percent shareholders too.
    -- §3121(a)(18) does not list §128, so the contribution is treated here as FICA wages.
    let trumpA := if s.trump && s.ent == .c then
        min trumpPerAccount ((if s.sal > 0 then trumpPerEmployee else 0) + (if s.spW > 0 then trumpPerEmployee else 0) +
          (if s.chW > 0 then trumpPerEmployee else 0))
      else 0
    let trumpF := pct trumpA 765 10000
    let ded := s.sal + salF + common + (if s.health then H else 0) + (if s.acct then sc.homeOff else 0) +
      (if s.rent then sc.rent else 0) + oPSA + trumpA + trumpF
    if ded > sc.profit then none else
    let inc := sc.profit - ded
    let addl := pct (s.sal + s.spW - addlMedThr) 9 1000
    let payroll := 2 * salF + 2 * spF + 2 * chF + 2 * trumpF + addl
    let newDefer := oPSA + oDefA + sPSA + sDefA + trumpA
    if s.ent == .s then
      if s.trump then none else
      if k != .out && k != .sweep then none else
      -- §1372 + §162(l)(5): premiums are wages to the 2% shareholder (not FICA wages, §3121(a)(2)(B)), deductible
      -- under §162(l) up to the wages from the corporation
      let hInc := if s.health then H - min H s.sal else 0
      let ordAGI := (s.sal - oDefA) + hInc + inc + (s.spW - sDefA)   -- §1366(a); no §1401 tax on the share
      -- §1368(c): distributions beyond the AAA are dividends out of C-year earnings and profits
      let div := if k == .sweep then s.cE else 0
      if k == .sweep && s.cE == 0 then none else
      fin 0 payroll ordAGI inc (s.sal + s.spW + s.chW) div div (s.cE - div) newDefer false
    else
      let ctax := pct inc 21 100                                    -- §11(b)
      let earn := inc - ctax
      -- §535(c)(1), (2): credit = what is kept for reasonable needs, at least $250,000 ($150,000 for the listed
      -- service fields) less earnings already accumulated
      let allow := max (sc.profit / 4) (if sc.svc then 150000 else 250000)
      let room := allow - s.cE
      let div := match k with
        | .out => earn | .retain => 0 | .credit => earn - min earn room | .sweep => earn + s.cE
      if k == .sweep && s.cE == 0 then none else
      if k == .credit && (earn ≤ room) then none else
      let kept := earn - min earn div
      let aet := pct (kept - room) 20 100                           -- §531
      let newCE := s.cE + earn - div - aet
      -- §1202(e)(1)(A), (e)(6): 80% of assets by value in the active business; working capital counts, but for at
      -- most half of the assets once the corporation is 2 years old
      let gw := (s.year + 1) * sc.gYear
      let total := gw + newCE
      let wc := min newCE (min (sc.profit / 4) (if s.year + 1 > 2 then total / 2 else total))
      let active := (newCE - wc) * 5 ≤ total
      let ordAGI := (s.sal - oDefA) + (s.spW - sDefA)               -- health: §106(a); rent: §280A(g)(2)
      fin (ctax + aet) payroll ordAGI 0 0 div div newCE newDefer (s.qOK && active)

def step (sc : Scn) (s : St) : Move → Option St
  | .choose e =>
    if s.done || s.entSet || !pendingClear s || e == s.ent || s.year ≥ sc.years then none else
    match s.ent, e with
    | .sp, .lp => if sc.lpLiteral then some { s with ent := .lp, entSet := true } else none
    | .sp, .s => some { s with ent := .s, entSet := true }
    -- §351; §1202(c)(1): stock issued by a C corporation that is a qualified small business; (e)(3)(A) excludes
    -- the listed service fields; (i)(1)(B): value already there at the exchange is not eligible gain
    | .sp, .c => some { s with ent := .c, entSet := true, cYear := s.year + 1, qOK := !sc.svc, g0 := s.year * sc.gYear }
    -- §1362(a); §1202(c)(2)(A): must be a C corporation for substantially all the holding period
    | .c, .s => if s.revoked then none else some { s with ent := .s, entSet := true, qOK := false }
    -- §1362(d)(1); the stock was not issued by a C corporation, §1202(c)(1)
    | .s, .c => some { s with ent := .c, entSet := true, revoked := true, qOK := false }
    | _, _ => none
  | .salary a =>
    if s.done || s.year ≥ sc.years || s.ent == .sp || s.sal != 0 || a == 0 || a > sc.rcHi then none
    else some { s with sal := a }
  | .hireSpouse a =>
    if s.done || s.year ≥ sc.years || s.spW != 0 || a == 0 || a > sc.spouseWork then none else some { s with spW := a }
  | .hireChild a =>
    if s.done || s.year ≥ sc.years || s.chW != 0 || a == 0 || a > sc.childWork then none else some { s with chW := a }
  | .healthPlan =>
    if s.done || s.year ≥ sc.years || s.health then none
    -- a proprietor or partner is not an employee (§105(g)); the plan can cover him only as the spouse of an employee
    else if (s.ent == .sp || s.ent == .lp) && s.spW == 0 then none
    else some { s with health := true }
  | .rentHome =>
    if s.done || s.year ≥ sc.years || s.rent || !(s.ent == .s || s.ent == .c) then none else some { s with rent := true }
  | .acctPlan =>
    if s.done || s.year ≥ sc.years || s.acct || !(s.ent == .s || s.ent == .c) then none else some { s with acct := true }
  | .ownerDefer =>
    if s.done || s.year ≥ sc.years || s.oDef || (s.ent != .sp && s.sal == 0) then none else some { s with oDef := true }
  | .ownerPS =>
    if s.done || s.year ≥ sc.years || s.oPS || (s.ent != .sp && s.sal == 0) then none else some { s with oPS := true }
  | .spouseDefer =>
    if s.done || s.year ≥ sc.years || s.sDef || s.spW == 0 then none else some { s with sDef := true }
  | .spousePS =>
    if s.done || s.year ≥ sc.years || s.sPS || s.spW == 0 then none else some { s with sPS := true }
  | .trumpAcct =>
    if s.done || s.year ≥ sc.years || s.trump || s.ent == .s then none
    else if s.spW == 0 && s.chW == 0 && (s.ent != .c || s.sal == 0) then none
    else some { s with trump := true }
  | .endYear k => if s.done || s.year ≥ sc.years then none else closeYear sc s k
  | .sell =>
    if s.done || s.year != sc.years then none else
    let G := sc.years * sc.gYear
    let base := s.lastTI + s.lastCap
    let niitRoom := s.lastMAGI - niitThr
    let over (g : Nat) : Nat := (s.lastMAGI + g) - niitThr - niitRoom   -- part of g above the §1411 threshold
    let t :=
      match s.ent with
      -- goodwill of a proprietorship / partnership / S stock held by a material participant: §1(h); not net
      -- investment income, §1411(c)(1)(A)(iii), (c)(4). Cash left in an S corporation from C years is part of the gain.
      | .sp | .lp => capTax base G
      | .s => capTax base (G + s.cE)
      | .c =>
        let gain := G + s.cE
        let held := if s.cYear == 0 then 0 else sc.years + 1 - s.cYear
        let long := sc.years ≥ 2
        if !long then ordTax (s.lastTI + gain) - ordTax s.lastTI + pct (min gain (over gain)) 38 1000
        else if s.qOK && s.cYear != 0 && held ≥ 3 then
          -- §1202(a)(1)(B), (a)(5): 50% at 3 years, 75% at 4, 100% at 5; (b)(4)(B) $15,000,000 per issuer
          let elig := min (gain - s.g0) 15000000
          let ex := if held ≥ 5 then elig else if held == 4 then elig * 3 / 4 else elig / 2
          let g28 := elig - ex
          let other := gain - elig
          gain28Tax s.lastTI g28 + capTax (base + g28) other + pct (min (g28 + other) (over (g28 + other))) 38 1000
        else capTax base gain + pct (min gain (over gain)) 38 1000   -- §1411(c)(1)(A)(iii)
    some { s with done := true, tax := s.tax + t }

/-! ## Part 2. Search -/

def start : St :=
  { year := 0, ent := .sp, entSet := false, sal := 0, spW := 0, chW := 0, health := false, rent := false,
    acct := false, oDef := false, oPS := false, sDef := false, sPS := false, trump := false, cE := 0, cYear := 0,
    qOK := false, g0 := 0, revoked := false, lastTI := 0, lastCap := 0, lastMAGI := 0, tax := 0, defer := 0,
    done := false }

/-- Amounts the position itself offers: each limit, each threshold, the profit split the §199A wage limit names. -/
def salaryAmounts (sc : Scn) : List Nat :=
  ([deferLimit, 2 * deferLimit, sc.rcLo, sc.profit * 2 / 7, wageBase, 190000, addlMedThr, sc.rcHi].filter
    (fun a => a > 0 && a ≤ sc.rcHi)).eraseDups

def moves (sc : Scn) (s : St) : List Move :=
  if s.done then [] else if s.year == sc.years then [.sell] else
  [.choose .lp, .choose .s, .choose .c] ++ (salaryAmounts sc).map .salary ++
  ([deferLimit, sc.spouseWork].filter (· ≤ sc.spouseWork)).eraseDups.map .hireSpouse ++
  [.hireChild (min sc.childWork stdDedChild), .healthPlan, .rentHome, .acctPlan, .ownerDefer, .ownerPS, .spouseDefer,
   .spousePS, .trumpAcct, .endYear .out, .endYear .retain, .endYear .credit, .endYear .sweep]

def showEnt : Ent → String | .sp => "sole prop" | .lp => "limited partnership" | .s => "S corp" | .c => "C corp"

def showMove : Move → String
  | .choose e => s!"-> {showEnt e}"
  | .salary a => s!"salary/GP {a}"
  | .hireSpouse a => s!"spouse wage {a}"
  | .hireChild a => s!"child wage {a}"
  | .healthPlan => "health plan" | .rentHome => "rent home 14d" | .acctPlan => "accountable plan"
  | .ownerDefer => "owner 401(k) deferral" | .ownerPS => "owner profit-sharing"
  | .spouseDefer => "spouse 401(k) deferral" | .spousePS => "spouse profit-sharing" | .trumpAcct => "Trump account"
  | .endYear .out => "| distribute" | .endYear .retain => "| retain" | .endYear .credit => "| retain to credit"
  | .endYear .sweep => "| distribute all incl. prior"
  | .sell => "SELL"

/-- Family of a plan: which kinds of move it uses (amounts and order dropped). -/
def kind : Move → String
  | .choose e => s!"->{showEnt e}"
  | .salary _ => "salary" | .hireSpouse _ => "spouse" | .hireChild _ => "child" | .healthPlan => "health"
  | .rentHome => "rent" | .acctPlan => "acct" | .ownerDefer => "oDef" | .ownerPS => "oPS" | .spouseDefer => "sDef"
  | .spousePS => "sPS" | .trumpAcct => "trump" | .endYear .out => "" | .endYear .retain => "retain"
  | .endYear .credit => "retain-credit" | .endYear .sweep => "sweep" | .sell => ""

def family (p : List Move) : String :=
  let ks := (p.map kind).filter (· != "") |>.eraseDups
  " ".intercalate (ks.toArray.qsort (· < ·)).toList

def cost (sc : Scn) (s : St) : Nat := s.tax + pct s.defer sc.deferRate 100

/-- Breadth-first over every allowed sequence. Within a year positions are deduplicated exactly. At a year end, of the
positions that agree on everything carried forward (retained cash compared in `bucket`-dollar bands), the cheapest
so far is kept. Every reported plan is a real sequence replayed through `step`. -/
def search (sc : Scn) (allowed : Move → Bool) (bucket : Nat) (top : Nat) (label : String) : IO Unit := do
  let mut frontier : Array (St × List Move) := #[(start, [])]
  let mut seen : Std.HashSet St := {}
  let mut carried : Std.HashMap St Nat := {}
  let mut fams : Std.HashMap String (Nat × St × List Move) := {}
  let mut n := 0
  let mut finals := 0
  while !frontier.isEmpty do
    let mut next : Array (St × List Move) := #[]
    for (s, path) in frontier do
      for m in moves sc s do
        if allowed m then
          match step sc s m with
          | none => pure ()
          | some s' =>
            n := n + 1
            if s'.done then
              finals := finals + 1
              let p := (m :: path).reverse
              let f := family p
              let c := cost sc s'
              match fams[f]? with
              | some (c0, _, _) => if c < c0 then fams := fams.insert f (c, s', p)
              | none => fams := fams.insert f (c, s', p)
            else
              match m with
              | .endYear _ =>
                -- the family is part of the key so that runner-up families survive
                let key := { s' with tax := (family (m :: path)).hash.toNat, defer := 0, cE := s'.cE / bucket }
                let c := cost sc s'
                match carried[key]? with
                | some c0 => if c < c0 then carried := carried.insert key c; next := next.push (s', m :: path)
                | none => carried := carried.insert key c; next := next.push (s', m :: path)
              | _ =>
                if !seen.contains s' then
                  seen := seen.insert s'
                  next := next.push (s', m :: path)
    frontier := next
  let base := match fams[""]? with | some (c, _, _) => c | none => 0
  let arr := fams.toArray.qsort (fun a b => a.2.1 < b.2.1)
  IO.println s!"== {label}: profit {sc.profit}/yr x {sc.years}, service field {sc.svc}, S floor {sc.rcFloor}, LP literal {sc.lpLiteral}"
  IO.println s!"   {n} positions, {finals} complete plans, {arr.size} families. Baseline (sole prop, nothing else): total tax {base}"
  let mut i := 0
  for (f, (c, s, p)) in arr do
    if i < top then
      IO.println s!" {i+1}. saves {(base : Int) - c}  [tax {s.tax}, deferred {s.defer}]  {f}"
      IO.println s!"      {"; ".intercalate (p.map showMove)}"
    i := i + 1
  -- what each kind of move is worth: over every family that has it and whose twin without it also exists
  for k in ["acct", "child", "health", "rent", "spouse", "oDef", "oPS", "sDef", "sPS", "trump", "salary"] do
    let mut lo : Int := 1000000000
    let mut hi : Int := -1000000000
    let mut hiF := ""
    let mut loF := ""
    for (f, (c, _, _)) in arr do
      let ws := f.splitOn " "
      if ws.contains k then
        match fams[" ".intercalate (ws.filter (· != k))]? with
        | some (c0, _, _) =>
          let d : Int := (c0 : Int) - c
          if d > hi then hi := d; hiF := f
          if d < lo then lo := d; loF := f
        | none => pure ()
    if hi > -1000000000 then IO.println s!"   adding '{k}': from {lo} ({loF}) to +{hi} ({hiF})"

def scn (profit : Nat) (svc : Bool) : Scn :=
  { profit, svc, rcLo := min 120000 (profit / 2), rcHi := max 250000 (profit / 2), health := 24000, homeOff := 6000,
    rent := 11200, childWork := 12000, spouseWork := 30000, gYear := 0, years := 1, rcFloor := true,
    lpLiteral := false, deferRate := 22 }

def noRetire : Move → Bool
  | .ownerDefer | .ownerPS | .spouseDefer | .spousePS | .trumpAcct => false
  | _ => true

def oneYear : Move → Bool
  | .endYear .retain | .endYear .credit | .endYear .sweep => false
  | _ => true

def fringeFree : Move → Bool
  | .choose _ | .salary _ | .endYear _ | .sell => true
  | _ => false

def run (sc : Scn) (p : List Move) : String :=
  match p.foldl (fun o m => o.bind (fun s => step sc s m)) (some start) with
  | some s => s!"tax {s.tax} defer {s.defer} cost {cost sc s}"
  | none => "not allowed"
#eval (salaryAmounts (scn 400000 false)).flatMap fun a => [24500, 30000].map fun w => (a, w,
  run (scn 400000 false) [.choose .c, .salary a, .hireSpouse w, .healthPlan, .rentHome, .acctPlan, .ownerPS, .endYear .out, .sell],
  run (scn 400000 false) [.choose .c, .salary a, .hireSpouse w, .healthPlan, .rentHome, .acctPlan, .ownerPS, .trumpAcct, .endYear .out, .sell])
end Legal.USTax.Hunt.Entity
