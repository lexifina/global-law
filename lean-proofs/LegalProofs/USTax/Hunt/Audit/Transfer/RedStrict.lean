import Std

/-!
# Estate, gift and generation-skipping tax: rules as enacted, then a blind search

Part 1 (`Rules`) writes down what chapters 11, 12, 13 and 14 and §§529, 1014, 1015 permit and tax for one family:
grandparents H and W (generation 1), their child C (generation 2), and `nK` grandchildren K (generation 3).
Nothing in Part 1 names a planning technique. Part 2 searches every sequence of permitted moves.

Text read: OLRC release point through Pub. L. 119-138 (so §2010(c)(3) is the $15,000,000 of Pub. L. 119-21).
Figures: 2026 (basic exclusion $15,000,000 by statute; annual exclusion $19,000).

Time is in 5-year periods. In each period: a planning phase (start of the period), then five years of growth, then,
if someone dies at the end of the period, a "last year" phase (moves made inside the 1-year and 3-year windows of
§§1014(e), 2035(b), 529(c)(4)(C)), then the death and the administration of the estate. Who dies when is a fixed
schedule given to the search, so every plan is compared on the same lives and the same horizon.

Simplifications, stated once:
* Each holding is `v` dollars of which `b` is cash/full-basis and `v - b` is zero-basis appreciation. Growth adds
  appreciation only. Tax is paid from cash first; beyond that, appreciated property is sold and the income tax on the
  sale (23.8%: §1(h) 20% + §1411 3.8%) is counted.
* Lump-sum gifts get no annual exclusion (the exclusion is modelled only through a yearly gift programme and the §529
  five-year election). Gifts in trust are future interests: no exclusion (§2503(b)(1); no withdrawal powers modelled).
* Family trust for C and descendants: no one holds a power that would include it in an estate. It ends at C's death.
* GRAT: 5-year term, annuity valued under §7520 at 5.0% equal to the whole contribution (taxable gift zero is the
  limit §2702(b)(1) allows). Created only at the start of a period, so the grantor outlives the term.
* A "will" is the set of bequests chosen while the estate is open. §2518(a) makes a qualified disclaimer within 9
  months equivalent to the will having said so, so bequest moves stand for both.
* A later spouse (the `remarry` move) brings no property and takes none; he or she only consents under §2513.
* §2032A is an election at each death when `farm` is set (2025 limit $1,420,000). No state death tax, no charity
  (§2055), no §2053 debts, no §6166 deferral (see FINDINGS).

Run: `lake env lean LegalProofs/USTax/Hunt/Transfer.lean` (scenario A, about a minute). Other scenarios:
`lake env lean --run LegalProofs/USTax/Hunt/Transfer.lean <short|Wfirst|Cfirst|farm|late|qtip|nomarry|notrusts|checks>`
(that also re-runs A first).
-/

namespace Legal.USTax.Hunt.Transfer

/-! ## Part 1. Rules -/

/-- §2010(c)(3): basic exclusion amount, $15,000,000 for 2026, indexed after 2026 (assumed 2.5%/yr, rounded to
$10,000 as (c)(3)(B) says). `t` counts 5-year periods. Also the GST exemption (§2631(c)). -/
def exclAt (t : Nat) : Nat := ((15000000 * 113 ^ t / 100 ^ t) + 5000) / 10000 * 10000
/-- §2503(b), 2026. Not indexed in the model. -/
def annualExcl : Nat := 19000
/-- RED: per-mille of the QTIP value that is the income interest (a §2511 gift, not a §2519 transfer). -/
def incFrac : Nat := 0
/-- RED: does §2513 reach the §2519 deemed transfer? -/
def split2519 : Bool := true
/-- RED: may the trust pay the consenting spouse's half of the tax (§2207A(b) read broadly)? -/
def spTaxFromTrust : Bool := false
def nK : Nat := 2
/-- tuition actually charged for the grandchildren, per year, while they are in school (first `schoolPeriods`). -/
def tuitionYr : Nat := 60000 * nK
def schoolPeriods : Nat := 2

/-- §2001(c). -/
def tent (x : Nat) : Nat :=
  if x ≤ 10000 then x * 18 / 100
  else if x ≤ 20000 then 1800 + (x - 10000) * 20 / 100
  else if x ≤ 40000 then 3800 + (x - 20000) * 22 / 100
  else if x ≤ 60000 then 8200 + (x - 40000) * 24 / 100
  else if x ≤ 80000 then 13000 + (x - 60000) * 26 / 100
  else if x ≤ 100000 then 18200 + (x - 80000) * 28 / 100
  else if x ≤ 150000 then 23800 + (x - 100000) * 30 / 100
  else if x ≤ 250000 then 38800 + (x - 150000) * 32 / 100
  else if x ≤ 500000 then 70800 + (x - 250000) * 34 / 100
  else if x ≤ 750000 then 155800 + (x - 500000) * 37 / 100
  else if x ≤ 1000000 then 248300 + (x - 750000) * 39 / 100
  else 345800 + (x - 1000000) * 40 / 100

structure Pot where
  v : Nat := 0
  b : Nat := 0
  deriving BEq, Hashable, Repr, Inhabited

def Pot.add (p q : Pot) : Pot := ⟨p.v + q.v, p.b + q.b⟩
/-- Take `a` out, cash first (`hi`) or appreciated property first. Returns (what is left, what was taken). -/
def Pot.take (p : Pot) (a : Nat) (hi : Bool) : Pot × Pot :=
  let a := min a p.v
  let tb := if hi then min a p.b else a - min a (p.v - p.b)
  (⟨p.v - a, p.b - tb⟩, ⟨a, tb⟩)
/-- Take `a` out pro rata. -/
def Pot.takePro (p : Pot) (a : Nat) : Pot × Pot :=
  let a := min a p.v
  let tb := if p.v = 0 then 0 else a * p.b / p.v
  (⟨p.v - a, p.b - tb⟩, ⟨a, tb⟩)
/-- Pay `x` of tax: cash first, then sell appreciated property (income tax on the sale returned). -/
def Pot.pay (p : Pot) (x : Nat) : Option (Pot × Nat) :=
  let c := min x p.b
  let r := x - c
  let s := (r * 1000 + 761) / 762
  if c + s ≤ p.v then some (⟨p.v - c - s, p.b - c⟩, s - r) else none
/-- Five years at 7%. -/
def Pot.grow (p : Pot) : Pot := ⟨p.v * 1403 / 1000, p.b⟩
/-- Value after the income tax built into it. -/
def Pot.net (p : Pot) : Nat := p.v - (p.v - p.b) * 238 / 1000

inductive Who | H | W | C
  deriving DecidableEq, BEq, Hashable, Repr, Inhabited

def sp : Who → Who | .H => .W | .W => .H | .C => .C

structure Person where
  alive : Bool := true
  own : Pot := {}
  gifts : Nat := 0     -- taxable gifts, all years (§2502(a); adjusted taxable gifts, §2001(b))
  cred : Nat := 0      -- unified credit already allowed against gift tax (§2505(a)(2))
  gtax : Nat := 0      -- gift tax payable on those gifts (§2001(b)(2))
  gtax3 : Nat := 0     -- gift tax paid in the last 3 years of life (§2035(b))
  incl : Nat := 0      -- §529(c)(4)(C) amount
  dsue : Nat := 0      -- §2010(c)(4)
  gst : Nat := 0       -- GST exemption allocated (§2631)
  recvV : Nat := 0     -- appreciated property received by gift from the spouse within a year (§1014(e))
  recvB : Nat := 0
  exC : Bool := false  -- §2503(b) exclusion for this period used for C / for the grandchildren
  exK : Bool := false
  prC : Nat := 0       -- yearly gift programme running this period, dollars per year
  prK : Nat := 0
  pA1 : Nat := 0       -- §2013: estate tax attributable to property received from a decedent, its value, and when
  pX1 : Nat := 0
  pT1 : Nat := 0
  pA2 : Nat := 0
  pX2 : Nat := 0
  pT2 : Nat := 0
  deriving BEq, Hashable, Repr, Inhabited

/-- A trust for C and C's descendants. `af` is the applicable fraction of §2642(a)(2), in millionths. -/
structure Trust where
  v : Nat := 0
  b : Nat := 0
  af : Nat := 0
  deriving BEq, Hashable, Repr, Inhabited

/-- §2642(d): property added to a trust; `e` of GST exemption allocated with it. -/
def Trust.addPot (tr : Trust) (p : Pot) (e : Nat := 0) : Trust :=
  let v := tr.v + p.v
  if v = 0 then tr else
  { v := v, b := tr.b + p.b, af := min 1000000 ((tr.v * tr.af / 1000000 + e) * 1000000 / v) }

structure Grat where
  on : Bool := false
  v : Nat := 0
  b : Nat := 0
  ann : Nat := 0       -- what the annuity returns to the grantor by the end of the term
  toTrust : Bool := false
  deriving BEq, Hashable, Repr, Inhabited

/-- Qualified terminable interest property, §2056(b)(7) / §2523(f). -/
structure Qtip where
  v : Nat := 0
  b : Nat := 0
  doneeW : Bool := false
  rev : Bool := false      -- §2652(a)(3) election
  toTrust : Bool := false  -- remainder to the family trust (else to C outright)
  af : Nat := 0            -- applicable fraction if `rev`
  cWas : Bool := true      -- C alive when the creating spouse's transfer was taxed (§2651(e))
  deriving BEq, Hashable, Repr, Inhabited

inductive Phase | plan | bed | estate (d : Who)
  deriving DecidableEq, BEq, Hashable, Repr, Inhabited

structure St where
  t : Nat := 0
  phase : Phase := .plan
  h : Person := {}
  w : Person := {}
  c : Person := {}
  k : Pot := {}
  k529 : Nat := 0
  tH : Trust := {}
  tW : Trust := {}
  gH : Grat := {}
  gW : Grat := {}
  q : Qtip := {}
  split : Bool := false
  tuit : Bool := false
  eSp : Nat := 0
  eQ : Nat := 0
  eQrev : Bool := false
  eQtt : Bool := false
  eT : Nat := 0
  eC : Nat := 0
  eK : Nat := 0
  newH : Bool := false  -- the H / W slot now holds a later spouse (no property, own exclusion and exemption)
  newW : Bool := false
  farm : Bool := false  -- the appreciated property is a family farm or business real estate meeting §2032A(b)
  xfer : Nat := 0   -- gift, estate and GST tax paid (nominal dollars)
  itax : Nat := 0   -- income tax on property sold to pay them
  deriving BEq, Hashable, Repr, Inhabited

def St.per (s : St) : Who → Person | .H => s.h | .W => s.w | .C => s.c
def St.setPer (s : St) : Who → Person → St
  | .H, p => { s with h := p } | .W, p => { s with w := p } | .C, p => { s with c := p }
def St.trust (s : St) : Who → Trust | .W => s.tW | _ => s.tH
def St.setTrust (s : St) : Who → Trust → St | .W, x => { s with tW := x } | _, x => { s with tH := x }
def St.grat (s : St) : Who → Grat | .W => s.gW | _ => s.gH
def St.setGrat (s : St) : Who → Grat → St | .W, x => { s with gW := x } | _, x => { s with gH := x }
def St.married (s : St) : Bool := s.h.alive && s.w.alive
def St.isNew (s : St) : Who → Bool | .H => s.newH | .W => s.newW | .C => false

inductive Dest | spouse | qtip (rev toTrust : Bool) | child | grand | trust | trustOut
  deriving DecidableEq, BEq, Repr

inductive Move
  | consentSplit                                   -- §2513
  | gift (d : Who) (to : Dest) (a : Nat) (hi : Bool) -- §2501; §2523(a), (f); §1015
  | grat (d : Who) (a : Nat) (toTrust hi : Bool)   -- §2702(a)(2)(B), (b)(1); §7520
  | fund529 (d : Who)                              -- §529(c)(2)
  | program (d : Who) (toK : Bool)                 -- §2503(b), every year of the period
  | tuition (d : Who)                              -- §2503(e)
  | allocGST (d : Who) (a : Nat)                   -- §2632(a), §2642(b)(3)
  | releaseQtip                                    -- §2519
  | distribute (tr : Who) (toK : Bool) (a : Nat)   -- trust distribution; §2612(b)
  | trustTuition (tr : Who)                        -- §2611(b)(1)
  | bequeath (to : Dest) (a : Nat)                 -- will, or §2518 disclaimer
  | electPortability                               -- §2010(c)(5)(A)
  | elect2032A                                     -- §2032A(a)
  | remarry (d : Who)                              -- a surviving spouse marries again
  deriving BEq, Repr

/-- Who dies at the end of each period. -/
abbrev Sched := List (Option Who)
def dying (sc : Sched) (t : Nat) : Option Who := (sc.getD t none)

/-- §2502, §2505: gift tax on a further taxable gift `g`. -/
def chargeGift (t : Nat) (p : Person) (g : Nat) : Person × Nat :=
  let raw := tent (p.gifts + g) - tent p.gifts
  let avail := tent (exclAt t + p.dsue) - p.cred
  let used := min raw avail
  ({ p with gifts := p.gifts + g, cred := p.cred + used, gtax := p.gtax + (raw - used) }, raw - used)

/-- A taxable gift of `a` by `d`. §2513: half each if the spouses consented. If it is a direct skip (§2612(c)):
§2632(b) allocates unused exemption, §2641 taxes the rest at 40%, §2603(a)(3) the transferor pays, §2515 the GST tax
is itself a gift. Returns (state, gift tax, GST tax). -/
def taxGift (s : St) (d : Who) (a : Nat) (skip : Bool) : St × Nat × Nat :=
  let parts : List (Who × Nat) :=
    if s.split && s.married && d != .C then [(d, a - a / 2), (sp d, a / 2)] else [(d, a)]
  parts.foldl (fun (s, gt, gs) (w, amt) =>
    let p := s.per w
    let e := if skip then min (exclAt s.t - p.gst) amt else 0
    let g := if skip then (amt - e) * 40 / 100 else 0
    let (p, tx) := chargeGift s.t { p with gst := p.gst + e } (amt + g)
    (s.setPer w p, gt + tx, gs + g)) (s, 0, 0)

def payFrom (s : St) (d : Who) (gt gs : Nat) : Option St :=
  let p := s.per d
  match p.own.pay (gt + gs) with
  | none => none
  | some (pot, inc) =>
    some { (s.setPer d { p with own := pot, gtax3 := p.gtax3 + (if s.phase == .bed then gt else 0) }) with
           xfer := s.xfer + gt + gs, itax := s.itax + inc }

def lifetime (s : St) : Bool := s.phase == .plan || s.phase == .bed

/-- Property enters the trust of which `w` is the transferor; §2632(c)(1) deemed allocation if `auto`. -/
def putTrust (s : St) (w : Who) (g : Pot) (auto : Bool) : St :=
  let p := s.per w
  let e := if auto then min (exclAt s.t - p.gst) g.v else 0
  (s.setPer w { p with gst := p.gst + e }).setTrust w ((s.trust w).addPot g e)

/-- Gift to the family trust. The trust has a non-skip beneficiary (C), so this is not a direct skip (§2613(a)(2))
but an indirect skip to a GST trust: §2632(c)(1) allocates unused exemption unless the donor elects out
(§2632(c)(5)(A)(i)). §2652(a)(2), §2654(b)(1): a split gift has two transferors, so two trusts. -/
def giftTrust (s s1 : St) (d : Who) (g : Pot) (a : Nat) (auto : Bool) : Option St :=
  if d == .C || !s.c.alive then none else
  let (s2, gt, gs) := taxGift s1 d a false
  (payFrom s2 d gt gs).map fun s3 =>
    if s.split && s.married then
      let g2 : Pot := ⟨g.v / 2, g.b / 2⟩
      putTrust (putTrust s3 d ⟨g.v - g2.v, g.b - g2.b⟩ auto) (sp d) g2 auto
    else putTrust s3 d g auto

def step (sc : Sched) (s : St) : Move → Option St
  | .consentSplit =>
    -- §2513(a): both spouses, all gifts to third parties for the rest of the period
    if lifetime s && s.married && !s.split then some { s with split := true } else none
  | .gift d to a hi =>
    let p := s.per d
    if !lifetime s || !p.alive || a == 0 || a > p.own.v then none else
    let (rest, g) := p.own.take a hi
    let s1 := s.setPer d { p with own := rest }
    match to with
    | .spouse =>
      -- §2523(a): deduction for the whole gift. §1015: basis carries over.
      if d == .C || !s.married || s.isNew (sp d) then none else
      let o := s1.per (sp d)
      let bed := s.phase == .bed
      some (s1.setPer (sp d) { o with own := o.own.add g, recvV := o.recvV + (if bed then g.v else 0),
                                       recvB := o.recvB + (if bed then g.b else 0) })
    | .qtip rev tt =>
      -- §2523(f): income to the spouse for life, election, full deduction. §2652(a)(3): the donor may elect to
      -- stay the transferor for chapter 13, and then allocates exemption to it.
      if d == .C || !s.married || s.q.v > 0 || s.isNew (sp d) then none else
      let e := if rev then min (exclAt s.t - p.gst) a else 0
      let s2 := s1.setPer d { (s1.per d) with gst := p.gst + e }
      some { s2 with q := { v := g.v, b := g.b, doneeW := d == .H, rev := rev, toTrust := tt,
                            af := e * 1000000 / a, cWas := s.c.alive } }
    | .child =>
      if d == .C || !s.c.alive then none else
      let (s2, gt, gs) := taxGift s1 d a false
      (payFrom s2 d gt gs).map fun s3 => s3.setPer .C { s3.c with own := s3.c.own.add g }
    | .grand =>
      -- §2613(a)(1), §2651(e): a grandchild is a skip person only while the child is alive
      let (s2, gt, gs) := taxGift s1 d a (d != .C && s.c.alive)
      (payFrom s2 d gt gs).map fun s3 => { s3 with k := s3.k.add g }
    | .trust => giftTrust s s1 d g a true
    | .trustOut => giftTrust s s1 d g a false
  | .grat d a tt hi =>
    -- §2702(a)(2)(B): the retained annuity is valued under §7520; here it equals the contribution, so the gift is 0.
    -- §2036 would include the trust if the grantor died in the term; the term ends before any scheduled death.
    let p := s.per d
    if s.phase != .plan || d == .C || !p.alive || !s.c.alive || (s.grat d).on || a == 0 || a > p.own.v then none else
    let (rest, g) := p.own.take a hi
    some ((s.setPer d { p with own := rest }).setGrat d { on := true, v := g.v, b := g.b, ann := a * 1276 / 1000, toTrust := tt })
  | .fund529 d =>
    -- §529(c)(2)(A): a completed present-interest gift to the beneficiary; (B): five years of exclusion at once.
    -- §529(c)(4)(A): not in the donor's estate; (C): except the years after death. §2642(c)(1): inclusion ratio 0.
    let p := s.per d
    let dbl := s.split && s.married && d != .C
    let o := s.per (sp d)
    let amt := 5 * annualExcl * nK * (if dbl then 2 else 1)
    if !lifetime s || !p.alive || s.isNew d || p.exK || (dbl && o.exK) || s.t ≥ schoolPeriods || amt > p.own.v then none else
    let (rest, _) := p.own.take amt true
    let incl := if s.phase == .bed && dying sc s.t == some d then 5 * annualExcl * nK * 4 / 5 else 0
    let s1 := s.setPer d { p with own := rest, exK := true, incl := p.incl + incl }
    let s2 := if dbl then s1.setPer (sp d) { (s1.per (sp d)) with exK := true } else s1
    some { s2 with k529 := s2.k529 + amt }
  | .program d toK =>
    -- §2503(b): $19,000 per donee per year, present interests. §2642(c)(1): no GST tax on these.
    let p := s.per d
    let dbl := s.split && s.married && d != .C
    let o := s.per (sp d)
    let used := if toK then p.exK || (dbl && o.exK) else p.exC || (dbl && o.exC)
    if !lifetime s || !p.alive || s.isNew d || used || (!toK && (d == .C || !s.c.alive)) then none else
    let yearly := annualExcl * (if toK then nK else 1) * (if dbl then 2 else 1)
    let mark := fun (x : Person) => if toK then { x with exK := true } else { x with exC := true }
    if s.phase == .plan then
      let p1 := mark (if toK then { p with prK := yearly } else { p with prC := yearly })
      let s1 := s.setPer d p1
      some (if dbl then s1.setPer (sp d) (mark (s1.per (sp d))) else s1)
    else
      if yearly > p.own.v then none else
      let (rest, g) := p.own.take yearly true
      let s1 := s.setPer d (mark { p with own := rest })
      let s2 := if dbl then s1.setPer (sp d) (mark (s1.per (sp d))) else s1
      some (if toK then { s2 with k := s2.k.add g } else s2.setPer .C { s2.c with own := s2.c.own.add g })
  | .tuition d =>
    -- §2503(e): tuition paid to the school is not a gift, without limit; §2611(b)(1): nor a GST.
    let p := s.per d
    let amt := if s.phase == .plan then 5 * tuitionYr else tuitionYr
    if !lifetime s || !p.alive || s.tuit || s.t ≥ schoolPeriods || amt > p.own.v then none else
    let (rest, _) := p.own.take amt true
    some { (s.setPer d { p with own := rest }) with tuit := true, k := s.k.add ⟨amt, amt⟩ }
  | .allocGST d a =>
    -- §2632(a): any time; §2642(b)(3): at the value when made.
    let p := s.per d
    let tr := s.trust d
    -- §2631(a): only to property of which the individual is the transferor (so not by a later spouse to the first
    -- spouse's trust, which shares the slot)
    if !lifetime s || d == .C || !p.alive || s.isNew d || tr.v == 0 || a == 0 || a > exclAt s.t - p.gst
       || a > tr.v * (1000000 - tr.af) / 1000000 + 1 then none else
    some ((s.setPer d { p with gst := p.gst + a }).setTrust d { tr with af := min 1000000 (tr.af + a * 1000000 / tr.v) })
  | .releaseQtip =>
    -- §2519: disposing of the income interest is a transfer of everything else too; with §2511 the whole value is
    -- a gift by the donee spouse. §2207A(b): the gift tax comes out of the property. §1015: basis carries over.
    -- It is a gift by the donee spouse under chapter 12, so §2513 lets a consenting spouse be treated as making
    -- half of it, and §2652(a)(2) then makes that spouse the transferor of half for chapter 13 (unless the first
    -- spouse's estate made the §2652(a)(3) election, which keeps the first spouse as transferor of all of it).
    let d : Who := if s.q.doneeW then .W else .H
    let p := s.per d
    if !lifetime s || s.q.v == 0 || !p.alive || !s.c.alive then none else
    let aInc := s.q.v * incFrac / 1000
    let (sA, gtA, _) := taxGift s d aInc false
    let (sB, gtB, _) := taxGift { sA with split := sA.split && split2519 } d (s.q.v - aInc) false
    let s2 : St := { sB with split := s.split }
    let gt := gtA + gtB
    let gtSp := if s.split && s.married then (s2.per (sp d)).gtax - (s.per (sp d)).gtax else 0
    if !spTaxFromTrust && gtSp > 0 then none else
    match (Pot.mk s.q.v s.q.b).pay gt with
    | none => none
    | some (pot, inc) =>
      let p2 := s2.per d
      let s3 := { (s2.setPer d { p2 with gtax3 := p2.gtax3 + (if s.phase == .bed then gt else 0) }) with
                  xfer := s.xfer + gt, itax := s.itax + inc, q := {} }
      if !s.q.toTrust then some (s3.setPer .C { s3.c with own := s3.c.own.add pot })
      else if s.q.rev then some (s3.setTrust (sp d) ((s3.trust (sp d)).addPot pot (pot.v * s.q.af / 1000000)))
      else if s.split && s.married then
        let sh := if split2519 then 1000 else incFrac
        let g2 : Pot := ⟨pot.v * sh / 2000, pot.b * sh / 2000⟩
        some (putTrust (putTrust s3 d ⟨pot.v - g2.v, pot.b - g2.b⟩ true) (sp d) g2 true)
      else some (putTrust s3 d pot true)
  | .distribute tr toK a =>
    let t := s.trust tr
    if s.phase != .plan || !s.c.alive || a == 0 || a > t.v then none else
    let (rest, g) := (Pot.mk t.v t.b).takePro a
    let s1 := s.setTrust tr { t with v := rest.v, b := rest.b }
    if !toK then some (s1.setPer .C { s1.c with own := s1.c.own.add g })
    else
      -- §2612(b) taxable distribution; §2641 rate = 40% × inclusion ratio; §2603(a)(1) the transferee pays.
      let tx := a * (1000000 - t.af) / 1000000 * 40 / 100
      match g.pay tx with
      | none => none
      | some (pot, inc) => some { s1 with k := s1.k.add pot, xfer := s1.xfer + tx, itax := s1.itax + inc }
  | .trustTuition tr =>
    -- §2611(b)(1): a transfer that would be excluded by §2503(e) if made by an individual is not a GST.
    let t := s.trust tr
    let amt := 5 * tuitionYr
    if s.phase != .plan || s.tuit || s.t ≥ schoolPeriods || amt > t.v then none else
    let (rest, _) := (Pot.mk t.v t.b).take amt true
    some { (s.setTrust tr { t with v := rest.v, b := rest.b }) with tuit := true, k := s.k.add ⟨amt, amt⟩ }
  | .bequeath to a =>
    match s.phase with
    | .estate d =>
      let p := s.per d
      if d == .C || a == 0 || a > p.own.v then none else
      let s1 := s.setPer d { p with own := ⟨p.own.v - a, p.own.b - a⟩ }
      let oAlive := (s.per (sp d)).alive && !s.isNew (sp d)
      match to with
      | .spouse => if oAlive then some { s1 with eSp := s.eSp + a } else none
      | .qtip rev tt =>
        if oAlive && s.q.v == 0 && (s.eQ == 0 || (s.eQrev == rev && s.eQtt == tt)) then
          some { s1 with eQ := s.eQ + a, eQrev := rev, eQtt := tt } else none
      | .child => if s.c.alive then some { s1 with eC := s.eC + a } else none
      | .grand => some { s1 with eK := s.eK + a }
      | .trust => if s.c.alive then some { s1 with eT := s.eT + a } else none
      | .trustOut => none
    | _ => none
  | .electPortability => none   -- applied when the estate is closed (see `advance`)
  | .elect2032A => none
  | .remarry d =>
    -- §2513(a)(1): "married to such individual at the time of the gift"; nothing limits it to a first spouse.
    -- The new spouse brings no property and takes none (no gifts or bequests to him or her are modelled).
    if s.phase != .plan || d == .C || !(s.per d).alive || (s.per (sp d)).alive || s.isNew (sp d) || s.isNew d then none
    else
      let s1 := s.setPer (sp d) {}
      some (if sp d == .H then { s1 with newH := true } else { s1 with newW := true })

/-! ### The end of each phase -/

def taintB (amt rv rb : Nat) : Nat :=
  let t := min amt rv
  amt - t + (if rv = 0 then 0 else t * rb / rv)

/-- Close the estate of a grandparent. `port`: the executor makes the §2010(c)(5)(A) election. -/
def closeG (s : St) (d : Who) (port : Bool) (su : Bool := false) : St :=
  let p := s.per d
  let o := sp d
  let oAlive := (s.per o).alive && !s.isNew o
  let cAlive := s.c.alive
  -- residue: "all to my spouse, or if none to my child, or if none to my grandchildren"
  let r := p.own.v
  let eSp := s.eSp + (if oAlive then r else 0)
  let eC := s.eC + (if !oAlive && cAlive then r else 0)
  let eK := s.eK + (if !oAlive && !cAlive then r else 0)
  let eT := s.eT
  let eQ := s.eQ
  -- §2044: property for which a QTIP deduction was allowed and in which the decedent had the income interest
  let qMine := s.q.v > 0 && (s.q.doneeW == (d == .W))
  let qIn := if qMine then s.q.v else 0
  -- §2056(a), (b)(7): everything passing to the spouse outright or as QTIP is deducted
  let nonMar := eT + eC + eK
  -- §2035(b) gift tax of the last three years; §529(c)(4)(C)
  -- §2032A(a): special-use value, at most $1,420,000 below market (2025 figure); §1014(a)(3): and that is the basis
  let red := if su && s.farm then min 1420000 nonMar else 0
  let base := nonMar - red + p.gtax3 + p.incl
  -- §2001(b), §2010
  let taxOf := fun (te : Nat) => tent (te + p.gifts) - p.gtax - tent (exclAt s.t + p.dsue)
  let tax := taxOf (base + qIn)
  let rest := taxOf base
  -- §2207A(a): the QTIP bears the tax it causes
  let qShare := min qIn (tax - rest)
  let fromNon := min rest nonMar
  let tT := if nonMar = 0 then 0 else fromNon * eT / nonMar
  let tC := if nonMar = 0 then 0 else fromNon * eC / nonMar
  let tK := fromNon - tT - tC
  let eT := eT - tT
  let eC := eC - tC
  let eK := eK - tK
  let eSp := eSp - (rest - fromNon)
  let qRem := qIn - qShare
  let te := base + qIn
  -- chapter 13 at death. §2632(e): unused exemption goes first to direct skips, then to the decedent's trusts.
  let unused := exclAt s.t - p.gst
  let e1 := if cAlive then min unused eK else 0
  -- §2623, §2603(b): the tax is on what the grandchildren receive and comes out of the bequest
  let gst1 := if cAlive then (eK - e1) * 40 / 140 else 0
  let unused := unused - e1
  let tr := s.trust d
  let qToMyTrust := qMine && !s.q.rev && s.q.toTrust && cAlive
  let add := eT + (if qToMyTrust then qRem else 0)
  let neT := tr.v * (1000000 - tr.af) / 1000000 + add
  let neQ := if eQ > 0 && s.eQrev then eQ else 0
  let alloc := min unused (neT + neQ)
  let aT := if neT + neQ = 0 then 0 else alloc * neT / (neT + neQ)
  let aQ := alloc - aT
  -- where the old QTIP goes
  let qRevTrust := qMine && s.q.rev && s.q.toTrust && cAlive
  let qToC := if qMine && cAlive && !s.q.toTrust then qRem else 0
  -- §2651(e): with C dead when the transferor's transfer was taxed, the grandchildren are not skip persons
  let gstQ := if qMine && !cAlive && s.q.rev && s.q.cWas then qRem * (1000000 - s.q.af) / 1000000 * 40 / 100 else 0
  let qToK := if qMine && !cAlive then qRem - gstQ else 0
  -- §1014(a), (b)(1), (b)(10): basis is date-of-death value; §1014(e) for property the spouse gave within a year
  let spB := taintB eSp p.recvV p.recvB
  let rv := p.recvV - min eSp p.recvV
  let rb := if p.recvV = 0 then 0 else p.recvB * rv / p.recvV
  let qB := taintB eQ rv rb
  -- write back
  let s := s.setPer d { p with own := {}, gst := p.gst + e1 + alloc }
  let rT := if nonMar = 0 then 0 else red * s.eT / nonMar
  let rC := if nonMar = 0 then 0 else red * s.eC / nonMar
  let s := s.setTrust d (tr.addPot ⟨add, add - min add rT⟩ aT)
  let s := if qRevTrust then s.setTrust o ((s.trust o).addPot ⟨qRem, qRem⟩ (qRem * s.q.af / 1000000)) else s
  let op := s.per o
  -- §2010(c)(4): the lesser of the basic exclusion amount and what the decedent left unused
  -- (c)(4) speaks of the LAST deceased spouse and (c)(5)(A) needs that spouse's executor to elect: no election, none
  let dsue := if port && oAlive then min (exclAt s.t) (exclAt s.t + p.dsue - (te + p.gifts)) else 0
  let s := if oAlive then s.setPer o { op with own := op.own.add ⟨eSp, spB⟩, dsue := dsue } else s
  let cGets := eC + qToC
  let cp := s.c
  -- §2013(b): estate tax paid × value transferred ÷ (taxable estate − death taxes)
  let a2013 := if te > tax then tax * cGets / (te - tax) else 0
  let cp := { cp with own := cp.own.add ⟨cGets, cGets - min cGets rC⟩ }
  let cp := if cGets = 0 then cp
            else if cp.pX1 = 0 then { cp with pA1 := a2013, pX1 := cGets, pT1 := s.t }
            else { cp with pA2 := a2013, pX2 := cGets, pT2 := s.t }
  let s := s.setPer .C cp
  let kGets := eK - gst1 + qToK
  let newQ : Qtip :=
    if eQ > 0 then { v := eQ, b := qB, doneeW := o == .W, rev := s.eQrev, toTrust := s.eQtt,
                     af := aQ * 1000000 / eQ, cWas := cAlive }
    else if qMine then {} else s.q
  { s with k := s.k.add ⟨kGets, kGets - min kGets (red - rT - rC)⟩, q := newQ, xfer := s.xfer + tax + gst1 + gstQ,
           eSp := 0, eQ := 0, eQrev := false, eQtt := false, eT := 0, eC := 0, eK := 0 }

/-- §2612(a): the child's interest ends and only grandchildren remain: taxable termination. §2622: on the whole
value; §2603(a)(2): the trustee pays. §2654(a)(2): basis steps up, but only by the inclusion ratio. -/
def terminate (s : St) (w : Who) : St :=
  let tr := s.trust w
  if tr.v = 0 then s else
  let ir := 1000000 - tr.af
  let tx := tr.v * ir / 1000000 * 40 / 100
  let b := tr.b + (tr.v - tr.b) * ir / 1000000
  match (Pot.mk tr.v b).pay tx with
  | none => s
  | some (pot, inc) => { (s.setTrust w {}) with k := s.k.add pot, xfer := s.xfer + tx, itax := s.itax + inc }

/-- Close the child's estate: everything to the grandchildren. -/
def closeC (s : St) (su : Bool := false) : St :=
  let p := s.c
  let red := if su && s.farm then min 1420000 p.own.v else 0
  let te := p.own.v - red + p.gtax3 + p.incl
  let taxOf := fun (x : Nat) => tent (x + p.gifts) - p.gtax - tent (exclAt s.t)
  let tax0 := taxOf te
  -- §2013(a), (c): credit for tax on prior transfers, by years since the transferor died
  let x := p.pX1 + p.pX2
  let lim := tax0 - taxOf (te - min te x)
  let pct := fun (t0 : Nat) =>
    let gap := 5 * (s.t - t0)
    if gap ≤ 2 then 100 else if gap ≤ 4 then 80 else if gap ≤ 6 then 60 else if gap ≤ 8 then 40
    else if gap ≤ 10 then 20 else 0
  let cr := fun (a xi t0 : Nat) => if x = 0 then 0 else pct t0 * (min a (lim * xi / x)) / 100
  let tax := tax0 - cr p.pA1 p.pX1 p.pT1 - cr p.pA2 p.pX2 p.pT2
  let left := p.own.v - min p.own.v tax
  let s := { (s.setPer .C { p with own := {} }) with k := s.k.add ⟨left, left - min left red⟩, xfer := s.xfer + tax }
  terminate (terminate s .H) .W

def newPeriod (s : St) : St :=
  let r := fun (p : Person) => { p with gtax3 := 0, incl := 0, recvV := 0, recvB := 0, exC := false, exK := false,
                                        prC := 0, prK := 0 }
  { s with t := s.t + 1, phase := .plan, split := false, tuit := false, h := r s.h, w := r s.w, c := r s.c }

def growAll (s : St) : St :=
  let g := fun (p : Person) => { p with own := p.own.grow }
  let gt := fun (t : Trust) => { t with v := t.v * 1403 / 1000 }
  let gg := fun (t : Grat) => { t with v := t.v * 1403 / 1000 }
  { s with h := g s.h, w := g s.w, c := g s.c, k := s.k.grow, k529 := s.k529 * 1403 / 1000,
           tH := gt s.tH, tW := gt s.tW, gH := gg s.gH, gW := gg s.gW, q := { s.q with v := s.q.v * 1403 / 1000 } }

def endGrat (s : St) (d : Who) : St :=
  let g := s.grat d
  if !g.on then s else
  let (rem, back) := (Pot.mk g.v g.b).takePro g.ann
  let p := s.per d
  let s := (s.setPer d { p with own := p.own.add back }).setGrat d {}
  -- §2642(f): no allocation during the term; §2632(c)(4): deemed made at its close, at the value then
  if g.toTrust then
    let p := s.per d
    let e := min (exclAt s.t - p.gst) rem.v
    (s.setPer d { p with gst := p.gst + e }).setTrust d ((s.trust d).addPot rem e)
  else s.setPer .C { s.c with own := s.c.own.add rem }

def runProgram (s : St) (d : Who) : St :=
  let p := s.per d
  if !p.alive then s else
  let (r1, gC) := p.own.take (p.prC * 5751 / 1000) true
  let (r2, gK) := r1.take (p.prK * 5751 / 1000) true
  let s := s.setPer d { p with own := r2 }
  let s := s.setPer .C { s.c with own := s.c.own.add gC }
  { s with k := s.k.add gK }

/-- End the current phase. -/
def advance (sc : Sched) (s : St) (port : Bool := false) (su : Bool := false) : St :=
  if s.t ≥ sc.length then s else
  match s.phase with
  | .plan =>
    let s := growAll s
    let s := endGrat (endGrat s .H) .W
    let s := runProgram (runProgram (runProgram s .H) .W) .C
    match dying sc s.t with
    | some d => if (s.per d).alive then { s with phase := .bed } else newPeriod s
    | none => newPeriod s
  | .bed =>
    match dying sc s.t with
    | none => newPeriod s
    | some d =>
      let p := s.per d
      let s := s.setPer d { p with alive := false, own := ⟨p.own.v, p.own.v⟩ }
      let s := if d != .C && s.q.v > 0 && (s.q.doneeW == (d == .W)) then { s with q := { s.q with b := s.q.v } } else s
      { s with phase := .estate d }
  | .estate d => newPeriod (if d == .C then closeC s su else closeG s d port su)

/-- What the grandchildren's generation holds at the end, after the income tax built into it. -/
def wealth (s : St) : Nat :=
  let per := fun (p : Person) => p.own.net
  s.k.net + s.k529 + (if s.newH then 0 else per s.h) + (if s.newW then 0 else per s.w) + per s.c + (Pot.mk s.tH.v s.tH.b).net + (Pot.mk s.tW.v s.tW.b).net
    + (Pot.mk s.q.v s.q.b).net

def builtIn (s : St) : Nat := (s.k.v - s.k.b) * 238 / 1000

/-! ## Part 2. Search -/

def amts (s : St) (d : Who) : List Nat :=
  let p := s.per d
  let room := exclAt s.t + p.dsue - p.gifts
  let o := s.per (sp d)
  let room2 := if s.split && s.married && d != .C then room + (exclAt s.t + o.dsue - o.gifts) else room
  let gstU := exclAt s.t - p.gst
  let v := p.own.v
  let net := if v > room2 then room2 + (v - room2) * 10 / 14 else v
  let net2 := if v > room2 then room2 + (v - room2) * 100 / 196 else v
  [v, p.own.b, v - p.own.b, room2, gstU, net, net2].filter (fun a => 0 < a && a ≤ v) |>.eraseDups

def his (p : Person) (a : Nat) : List Bool := if p.own.b = 0 || p.own.b = p.own.v || a = p.own.v then [true] else [true, false]

def moves (_sc : Sched) (s : St) : List Move :=
  match s.phase with
  | .estate d =>
    if d == .C then [] else
    let p := s.per d
    let room := exclAt s.t + p.dsue - p.gifts - (s.eT + s.eC + s.eK)
    let as := [p.own.v, room, exclAt s.t - p.gst].filter (fun a => 0 < a && a ≤ p.own.v) |>.eraseDups
    as.flatMap fun a =>
      [.bequeath .spouse a, .bequeath (.qtip false false) a, .bequeath (.qtip false true) a,
       .bequeath (.qtip true true) a, .bequeath .child a, .bequeath .grand a, .bequeath .trust a]
  | ph =>
    let g1 := [Who.H, Who.W].flatMap fun d =>
      let p := s.per d
      if !p.alive then [] else
      let as := amts s d
      let lump := as.flatMap fun a => (his p a).flatMap fun hi =>
        [.gift d .spouse a hi, .gift d (.qtip false false) a hi, .gift d (.qtip false true) a hi,
         .gift d (.qtip true true) a hi, .gift d .child a hi, .gift d .grand a hi, .gift d .trust a hi, .gift d .trustOut a hi]
        ++ (if ph == .plan then [.grat d a false hi, .grat d a true hi] else [])
      let tr := s.trust d
      let al := min (exclAt s.t - p.gst) (tr.v * (1000000 - tr.af) / 1000000)
      lump ++ [.fund529 d, .program d false, .program d true, .tuition d] ++ (if al > 0 then [.allocGST d al] else [])
    let cc := if !s.c.alive then [] else
      (amts s .C).map (fun a => Move.gift .C .grand a true) ++ [.fund529 .C, .program .C true, .tuition .C]
    let tt := [Who.H, Who.W].flatMap fun w =>
      let t := s.trust w
      if t.v = 0 then [] else
      let cRoom := exclAt s.t - s.c.gifts
      ([t.v, cRoom, t.v * t.af / 1000000].filter (fun a => 0 < a && a ≤ t.v) |>.eraseDups).flatMap (fun a =>
        [Move.distribute w false a, .distribute w true a]) ++ [.trustTuition w]
    [.consentSplit, .releaseQtip, .remarry .H, .remarry .W] ++ g1 ++ cc ++ tt

def kind : Move → Nat
  | .consentSplit => 0
  | .gift .C _ _ _ => 1
  | .gift _ .spouse _ _ => 2
  | .gift _ (.qtip false _) _ _ => 3
  | .gift _ (.qtip true _) _ _ => 4
  | .gift _ .child _ _ => 5
  | .gift _ .grand _ _ => 6
  | .gift _ .trust _ _ => 7
  | .gift _ .trustOut _ _ => 26
  | .grat _ _ false _ => 8
  | .grat _ _ true _ => 9
  | .fund529 _ => 10
  | .program _ false => 11
  | .program _ true => 12
  | .tuition _ => 13
  | .allocGST _ _ => 14
  | .releaseQtip => 15
  | .distribute _ false _ => 16
  | .distribute _ true _ => 17
  | .trustTuition _ => 18
  | .bequeath .spouse _ => 19
  | .bequeath (.qtip false _) _ => 20
  | .bequeath (.qtip true _) _ => 21
  | .bequeath .child _ => 22
  | .bequeath .grand _ => 23
  | .bequeath .trust _ => 24
  | .bequeath .trustOut _ => 24
  | .elect2032A => 27
  | .remarry _ => 28
  | .electPortability => 25

def kindName : Nat → String
  | 0 => "split" | 1 => "C-gift" | 2 => "gift-spouse" | 3 => "lifetime-QTIP" | 4 => "lifetime-QTIP(rev)"
  | 5 => "gift-child" | 6 => "gift-grandchildren" | 7 => "gift-trust" | 8 => "GRAT→child" | 9 => "GRAT→trust"
  | 10 => "529" | 11 => "annual→child" | 12 => "annual→grandchildren" | 13 => "tuition" | 14 => "allocate-GST"
  | 15 => "§2519" | 16 => "trust→child" | 17 => "trust→grandchildren" | 18 => "trust-tuition"
  | 19 => "will:spouse" | 20 => "will:QTIP" | 21 => "will:QTIP(rev)" | 22 => "will:child"
  | 23 => "will:grandchildren" | 24 => "will:trust" | 25 => "portability" | 26 => "gift-trust(no GST alloc)"
  | 27 => "§2032A" | _ => "remarry"

def sig (path : List Move) : Nat := path.foldl (fun m x => m ||| (1 <<< kind x)) 0
def sigNames (m : Nat) : String :=
  ", ".intercalate ((List.range 29).filter (fun i => (m >>> i) % 2 == 1) |>.map kindName)

def fmt (x : Nat) : String :=
  let c := (x % 1000000) / 10000
  s!"${x / 1000000}.{if c < 10 then "0" else ""}{c}M"

def whoS : Who → String | .H => "H" | .W => "W" | .C => "C"
def destS : Dest → String
  | .spouse => "spouse" | .qtip r t => s!"QTIP{if r then " (reverse election)" else ""}, remainder {if t then "family trust" else "child"}"
  | .child => "child" | .grand => "grandchildren" | .trust => "family trust"
  | .trustOut => "family trust (elect out of GST allocation)"
def showMove : Move → String
  | .consentSplit => "consent to split gifts (§2513)"
  | .gift d to a hi => s!"{whoS d} gives {fmt a} to {destS to} ({if hi then "cash first" else "appreciated first"})"
  | .grat d a tt hi => s!"{whoS d} funds GRAT {fmt a} ({if hi then "cash first" else "appreciated first"}), remainder {if tt then "family trust" else "child"}"
  | .fund529 d => s!"{whoS d} funds 529 with five-year election"
  | .program d k => s!"{whoS d} gives the annual exclusion each year to {if k then "grandchildren" else "child"}"
  | .tuition d => s!"{whoS d} pays tuition"
  | .allocGST d a => s!"{whoS d} allocates {fmt a} GST exemption to trust"
  | .releaseQtip => "spouse gives up QTIP income interest (§2519)"
  | .distribute w k a => s!"trust({whoS w}) distributes {fmt a} to {if k then "grandchildren" else "child"}"
  | .trustTuition w => s!"trust({whoS w}) pays tuition"
  | .bequeath to a => s!"will/disclaimer: {fmt a} to {destS to}"
  | .electPortability => "executor elects portability"
  | .elect2032A => "executor elects special-use valuation (§2032A)"
  | .remarry d => s!"{whoS d} marries again"

def finish (sc : Sched) (s : St) : St := Id.run do
  let mut s := s
  for _ in [0:4 * sc.length + 2] do s := advance sc s
  return s

abbrev Node := St × List Move

def isEnabler : Move → Bool | .consentSplit | .remarry _ => true | _ => false

/-- Consenting to split gifts and marrying change no dollar by themselves, so a beam scored on dollars would drop
them. They are therefore free: tried in front of every other move without using up depth. -/
def enablers (sc : Sched) (allowed : St → Move → Bool) (s : St) (path : List Move) : List Node :=
  let try1 := fun (s : St) (p : List Move) (ms : List Move) =>
    ms.filterMap fun m => if allowed s m then (step sc s m).map fun s' => (s', m :: p) else none
  let one := try1 s path [.consentSplit, .remarry .H, .remarry .W]
  let two := one.flatMap fun (s1, p1) => try1 s1 p1 [.consentSplit]
  (s, path) :: one ++ two

/-- Every position reachable from `starts` in at most `m` further moves of the current phase. -/
def expand (sc : Sched) (m : Nat) (allowed : St → Move → Bool) (starts : Array Node) : Array Node := Id.run do
  let mut seen : Std.HashSet St := {}
  let mut all : Array Node := #[]
  let mut layer : Array Node := #[]
  for (s, p) in starts do
    if !seen.contains s then
      seen := seen.insert s
      layer := layer.push (s, p)
  all := layer
  for _ in [0:m] do
    let mut next : Array Node := #[]
    for (s0, path0) in layer do
      for (s, path) in enablers sc allowed s0 path0 do
        for mv in moves sc s do
          if allowed s mv && !isEnabler mv then
            match step sc s mv with
            | some s2 =>
              if !seen.contains s2 then
                seen := seen.insert s2
                next := next.push (s2, mv :: path)
            | none => pure ()
    all := all ++ next
    layer := next
  return all

/-- End the phase from each position; an open estate closes with and without each election. -/
def closeOut (sc : Sched) (xs : Array Node) : Array Node := Id.run do
  let mut out : Std.HashMap St (List Move) := {}
  for (s, path) in xs do
    let mut vs : List (St × List Move) := [(advance sc s, path)]
    match s.phase with
    | .estate d =>
      if d != .C && (s.per (sp d)).alive && !s.isNew (sp d) then vs := vs ++ [(advance sc s true, .electPortability :: path)]
      if s.farm then
        vs := vs ++ [(advance sc s false true, .elect2032A :: path)]
        if d != .C && (s.per (sp d)).alive then
          vs := vs ++ [(advance sc s true true, .elect2032A :: .electPortability :: path)]
    | _ => pure ()
    for (s', p') in vs do
      if !out.contains s' then out := out.insert s' p'
  return out.toArray

/-- small-dollar moves, left out when naming a family -/
def minorMask : Nat := (1 <<< 10) ||| (1 <<< 11) ||| (1 <<< 12) ||| (1 <<< 13) ||| (1 <<< 18)
def major (g : Nat) : Nat := g &&& ((1 <<< 29) - 1 - minorMask)
def nKinds (g : Nat) : Nat := ((List.range 29).filter (fun i => (g >>> i) % 2 == 1)).length

/-- The beam. Positions are scored by finishing with no further move. They are kept in strata by how many kinds of
large move they use (0, 1, …, 6+), `cap / 7` per stratum, at most `perSig` per family, so that plans built from one
or two ideas are never crowded out by variations of the current leader. -/
def score (s : St) : Nat := wealth s

def prune (sc : Sched) (cap perSig : Nat) (xs : Array Node) : Array Node := Id.run do
  let scored := xs.map fun (s, p) => (score (finish sc s), sig p, s, p)
  let sorted := scored.qsort fun a b => a.1 > b.1
  let mut cnt : Std.HashMap Nat Nat := {}
  let mut strata : Std.HashMap Nat Nat := {}
  let mut out : Array Node := #[]
  for (_, g, s, p) in sorted do
    let k := min 6 (nKinds (major g))
    let c := cnt.getD (major g) 0
    let n := strata.getD k 0
    if c < perSig && n < cap / 7 then
      cnt := cnt.insert (major g) (c + 1)
      strata := strata.insert k (n + 1)
      out := out.push (s, p)
  return out

structure Cfg where
  mFirst : Nat := 2     -- exhaustive depth, first planning phase
  mPlan : Nat := 1      -- exhaustive depth, later planning phases
  rounds : Nat := 2     -- then this many further rounds of one move each, pruned between rounds
  mBed : Nat := 1
  mEstate : Nat := 2
  cap : Nat := 350
  perSig : Nat := 2
  allowed : St → Move → Bool := fun _ _ => true

def search (name : String) (sc : Sched) (s0 : St) (cfg : Cfg := {}) (top : Nat := 10) : IO Unit := do
  IO.println s!"==== {name} ===="
  let base := finish sc s0
  let wb := wealth base
  IO.println s!"simple will: grandchildren end with {fmt wb} after tax; transfer tax {fmt base.xfer}, built-in income tax {fmt (builtIn base)}"
  let mut xs : Array Node := #[(s0, [])]
  let mut total := 0
  let mut first := true
  for _ in [0:3 * sc.length] do
    if xs.size > 0 && xs[0]!.1.t < sc.length then
      let ph := xs[0]!.1.phase
      let (m, r) := match ph with
        | .plan => (if first then cfg.mFirst else cfg.mPlan, cfg.rounds)
        | .bed => (cfg.mBed, 1)
        | .estate _ => (cfg.mEstate, 0)
      first := false
      let mut ys := expand sc m cfg.allowed xs
      total := total + ys.size
      for _ in [0:r] do
        ys := prune sc cfg.cap cfg.perSig ys
        ys := expand sc 1 cfg.allowed ys
        total := total + ys.size
      let zs := closeOut sc ys
      xs := prune sc cfg.cap cfg.perSig zs
      IO.println s!"  period {xs[0]!.1.t - (if xs[0]!.1.phase == .plan then 1 else 0)} {repr ph}: {zs.size} positions, kept {xs.size}"
  let scored := xs.map fun (s, p) => (score s, sig p, s, p)
  let sorted := scored.qsort fun a b => a.1 > b.1
  IO.println s!"positions examined: {total}; plans at the end: {sorted.size}"
  -- best plan of each family (families named by their large moves)
  -- a family is shown only if it does not contain all the large moves of a better family already shown
  let mut shown : List Nat := []
  let mut n := 0
  for (wl, g, s, p) in sorted do
    if !shown.any (fun a => a &&& major g == a) && n < top then
      shown := major g :: shown
      n := n + 1
      IO.println s!"#{n}  {fmt wl}  ({if wl ≥ wb then "+" else "-"}{fmt (if wl ≥ wb then wl - wb else wb - wl)} vs simple will)  transfer tax {fmt s.xfer}, income tax paid {fmt s.itax}, built-in {fmt (builtIn s)}"
      IO.println s!"    family: {sigNames (major g)}"
      for m in p.reverse do IO.println s!"      {showMove m}"
  -- plans built from one or two kinds of large move
  IO.println "  one- and two-idea plans (best of each family):"
  let mut seen1 : Std.HashSet Nat := {}
  for (wl, g, _, _) in sorted do
    if nKinds (major g) ≤ 2 && !seen1.contains (major g) then
      seen1 := seen1.insert (major g)
      IO.println s!"    {if wl ≥ wb then "+" else "-"}{fmt (if wl ≥ wb then wl - wb else wb - wl)}  [{sigNames (major g)}]"
  -- what each kind of move is worth: best plan using it against best plan not using it
  IO.println "  kind of move: best plan with it / best plan without it"
  for k in List.range 29 do
    let w := sorted.foldl (fun acc (wl, g, _, _) => if (g >>> k) % 2 == 1 then max acc wl else acc) 0
    let wo := sorted.foldl (fun acc (wl, g, _, _) => if (g >>> k) % 2 == 0 then max acc wl else acc) 0
    if w > 0 then IO.println s!"    {kindName k}: {fmt w} / {fmt wo}"

/-- H owns $100M ($20M cash, $80M appreciation), W and C nothing, two grandchildren in school for ten years. -/
def start : St := { h := { own := ⟨100000000, 20000000⟩ } }

def schedA : Sched := [some .H, some .W, none, none, some .C]
def schedShort : Sched := [some .H, some .W, some .C]
def schedWfirst : Sched := [some .W, some .H, none, none, some .C]
def schedCfirst : Sched := [some .C, some .H, some .W]

/-- Play one written-out plan: `none` ends the phase; `.electPortability` ends it with the election. -/
def play (sc : Sched) (s0 : St) (script : List (Option Move)) : Option St :=
  script.foldl (fun os m => os.bind fun s => match m with
    | none => some (advance sc s)
    | some .electPortability => some (advance sc s true)
    | some mv => step sc s mv) (some s0) |>.map (finish sc)

def showPlay (label : String) (sc : Sched) (s0 : St) (script : List (Option Move)) : IO Unit :=
  match play sc s0 script with
  | none => IO.println s!"  {label}: not allowed"
  | some s => IO.println s!"  {label}: {fmt (wealth s)}  (transfer tax {fmt s.xfer}, income tax paid {fmt s.itax}, built-in {fmt (builtIn s)})"

/-- Head-to-head checks of the specific claims in FINDINGS (same lives as scenario A). -/
def checks : IO Unit := do
  let sc := schedA
  let s0 := start
  IO.println "== 1. second spouse's exclusion and GST exemption applied to the first spouse's QTIP (§2519 + §2513 + §2652(a)(2)) =="
  let q : Option Move := some (.bequeath (.qtip false true) 140300000)
  showPlay "H's will: all to QTIP; W keeps it to death" sc s0 [none, none, q, none]
  showPlay "… with portability" sc s0 [none, none, q, some .electPortability]
  showPlay "… W gives up the income interest in year 5 (§2519), unmarried" sc s0 [none, none, q, none, some .releaseQtip]
  showPlay "… W remarries, both consent (§2513), then §2519" sc s0 [none, none, q, none, some (.remarry .W), some .consentSplit, some .releaseQtip]
  showPlay "… portability, then remarries, consent, §2519" sc s0 [none, none, q, some .electPortability, some (.remarry .W), some .consentSplit, some .releaseQtip]
  IO.println "== 2. second spouse and W's own gifts =="
  showPlay "all to W outright; W gives $80M to family trust in year 5" sc s0 [none, none, none, some (.gift .W .trust 80000000 true)]
  showPlay "… W remarries and both consent first" sc s0 [none, none, none, some (.remarry .W), some .consentSplit, some (.gift .W .trust 80000000 true)]
  IO.println "== 3. direct skip in the last year against the same dollars by will (§2035(b) reaches chapter 12 tax only) =="
  -- H has used his exclusion and exemption on a $15M gift to the grandchildren at the start
  let g0 : Option Move := some (.gift .H .grand 15000000 true)
  showPlay "H gives $20M more to grandchildren in his last year" sc s0 [g0, none, some (.gift .H .grand 20000000 true), none, none]
  -- outlay of that gift: 20M + GST 8M + gift tax 11.2M = 39.2M
  showPlay "H leaves $39.2M (the same outlay) to grandchildren by will" sc s0 [g0, none, none, some (.bequeath .grand 39200000), none]
  showPlay "neither (all to W)" sc s0 [g0, none, none, none]
  IO.println "== 4. §529 five-year election in the last year (§529(c)(4)(C)) against tuition paid directly =="
  showPlay "nothing" sc s0 [none, none, none]
  showPlay "H funds 529s in his last year" sc s0 [none, some (.fund529 .H), none, none]
  showPlay "H funds 529s at the start" sc s0 [some (.fund529 .H), none, none, none]
  showPlay "H pays tuition at the start" sc s0 [some (.tuition .H), none, none, none]
  IO.println "== 5. reverse QTIP election when the child dies between the spouses (§2651(e), §2652(a)(3)) =="
  let sc2 : Sched := [some .H, some .C, some .W]
  showPlay "QTIP, no reverse election" sc2 s0 [none, none, some (.bequeath (.qtip false true) 140300000), none]
  showPlay "QTIP, reverse election" sc2 s0 [none, none, some (.bequeath (.qtip true true) 140300000), none]

def runScenario : String → IO Unit
  | "checks" => checks
  | "A" => search "A: H dies yr 5, W yr 10, C yr 25" schedA start
  | "short" => search "A-short: H dies yr 5, W yr 10, C yr 15 (§2013 credit in range)" schedShort start
  | "Wfirst" => search "B: W (no assets) dies yr 5, H yr 10, C yr 25" schedWfirst start
  | "Cfirst" => search "C: C dies yr 5, H yr 10, W yr 15 (§2651(e))" schedCfirst start
  | "farm" => search "D: as A, the appreciated property is a qualifying farm (§2032A)" schedA { start with farm := true }
  | "nogrant" => search "E: as A, no GRAT" schedA start { allowed := fun _ m => match m with | .grat .. => false | _ => true }
  | "notrusts" => search "F: as A, outright moves only (no GRAT, no trust, no QTIP)" schedA start
      { allowed := fun _ m => match m with
          | .grat .. | .gift _ (.qtip ..) _ _ | .gift _ .trust _ _ | .gift _ .trustOut _ _
          | .bequeath (.qtip ..) _ | .bequeath .trust _ => false | _ => true }
  | "nomarry" => search "A without remarriage" schedA start { allowed := fun _ m => match m with | .remarry _ => false | _ => true }
  | "qtip" => search "I: H has died leaving $100M in a QTIP trust for W (no reverse election), remainder to the family trust; W dies yr 10, C yr 25"
      [none, some .W, none, none, some .C]
      { h := { alive := false }, q := { v := 100000000, b := 100000000, doneeW := true, toTrust := true } }
  | "late" => search "G: as A, but nothing is done until H's last year" schedA start
      { allowed := fun s _ => !(s.t == 0 && s.phase == .plan) }
  | "lateW" => search "H: as B (W dies first), nothing is done until W's last year" schedWfirst start
      { allowed := fun s _ => !(s.t == 0 && s.phase == .plan) }
  | _ => IO.println "scenarios: A short Wfirst Cfirst farm nogrant notrusts nomarry late lateW qtip checks"

/-- `lake env lean --run LegalProofs/USTax/Hunt/Transfer.lean <scenario>` for the others. -/
def runAll (args : List String) : IO Unit := do
  for a in args do runScenario a


/-! ## RED tail (audit code; not in the original) -/

def qStart (v : Nat := 100000000) : St :=
  { h := { alive := false }, q := { v := v, b := v, doneeW := true, toTrust := true } }
def schedQ : Sched := [none, some .W, none, none, some .C]

def showX (label : String) (sc : Sched) (s0 : St) (script : List (Option Move)) : IO Unit :=
  match play sc s0 script with
  | none => IO.println s!"  {label}: NOT ALLOWED"
  | some s => IO.println s!"  {label}: wealth={wealth s} xfer={s.xfer} itax={s.itax} builtin={builtIn s} kv={s.k.v} kb={s.k.b}"

def redDirect (v : Nat) : IO Unit := do
  let s0 := qStart v
  IO.println s!"-- direct plays on the QTIP scenario, trust {v} (incFrac={incFrac}, split2519={split2519}, spTaxFromTrust={spTaxFromTrust})"
  showX "hold to death" schedQ s0 []
  showX "yr0 release unmarried" schedQ s0 [some .releaseQtip]
  showX "yr0 remarry, no consent, release" schedQ s0 [some (.remarry .W), some .releaseQtip]
  showX "yr0 remarry+consent+release" schedQ s0 [some (.remarry .W), some .consentSplit, some .releaseQtip]
  showX "yr5 release unmarried" schedQ s0 [none, some .releaseQtip]
  showX "yr5 remarry+consent+release" schedQ s0 [none, some (.remarry .W), some .consentSplit, some .releaseQtip]

def redChecks1 : IO Unit := do
  let sc := schedA
  let s0 := start
  let q : Option Move := some (.bequeath (.qtip false true) (100000000 * 1403 / 1000))
  IO.println "-- FINDINGS check 1 (scenario A lives)"
  showX "QTIP held to death" sc s0 [none, none, q, none]
  showX "yr5 release unmarried" sc s0 [none, none, q, none, some .releaseQtip]
  showX "yr5 remarry+consent+release" sc s0 [none, none, q, none, some (.remarry .W), some .consentSplit, some .releaseQtip]
  let qr : Option Move := some (.bequeath (.qtip true true) (100000000 * 1403 / 1000))
  showX "reverse-QTIP: yr5 release unmarried" sc s0 [none, none, qr, none, some .releaseQtip]
  showX "reverse-QTIP: yr5 remarry+consent+release" sc s0 [none, none, qr, none, some (.remarry .W), some .consentSplit, some .releaseQtip]

def qName := "QTIP scenario"
def onlyKinds (ks : List Nat) : St → Move → Bool := fun _ m => ks.contains (kind m)
def notKind (k : Nat) : St → Move → Bool := fun _ m => kind m != k

/-- Sum of everything anyone holds (dollars), including what is in an open estate. -/
def tot (s : St) : Nat :=
  s.h.own.v + s.w.own.v + s.c.own.v + s.k.v + s.k529 + s.tH.v + s.tW.v + s.gH.v + s.gW.v + s.q.v
    + s.eSp + s.eQ + s.eT + s.eC + s.eK
def bas (s : St) : Nat :=
  s.h.own.b + s.w.own.b + s.c.own.b + s.k.b + s.k529 + s.tH.b + s.tW.b + s.gH.b + s.gW.b + s.q.b
    + s.eSp + s.eQ + s.eT + s.eC + s.eK
def limitsOk (s : St) : Bool :=
  let ok := fun (p : Person) => p.gst ≤ exclAt s.t && p.cred ≤ tent (exclAt s.t + p.dsue) && p.own.b ≤ p.own.v
  ok s.h && ok s.w && s.c.cred ≤ tent (exclAt s.t) && s.tH.af ≤ 1000000 && s.tW.af ≤ 1000000 && s.q.af ≤ 1000000
    && s.tH.b ≤ s.tH.v && s.tW.b ≤ s.tW.v && s.k.b ≤ s.k.v && s.q.b ≤ s.q.v && s.c.own.b ≤ s.c.own.v

/-- The search of the original, with a conservation check on every step and every phase end it takes. -/
def searchChk (name : String) (sc : Sched) (s0 : St) (cfg : Cfg := {}) : IO Unit := do
  IO.println s!"==== conservation: {name} ===="
  let mut xs : Array Node := #[(s0, [])]
  let mut first := true
  let mut nStep := 0
  let mut badVal : Std.HashMap Nat (Nat × Nat) := {}
  let mut badBas : Std.HashMap Nat (Nat × Nat) := {}
  let mut badLim := 0
  let mut nAdv := 0
  let mut badAdv : Std.HashMap String (Nat × Nat) := {}
  let mut exAdv : List String := []
  for _ in [0:3 * sc.length] do
    if xs.size > 0 && xs[0]!.1.t < sc.length then
      let ph := xs[0]!.1.phase
      let (m, r) := match ph with
        | .plan => (if first then cfg.mFirst else cfg.mPlan, cfg.rounds)
        | .bed => (cfg.mBed, 1)
        | .estate _ => (cfg.mEstate, 0)
      first := false
      let mut ys := expand sc m cfg.allowed xs
      for _ in [0:r] do
        ys := prune sc cfg.cap cfg.perSig ys
        ys := expand sc 1 cfg.allowed ys
      for (s, _) in ys do
        if !limitsOk s then badLim := badLim + 1
        for mv in moves sc s do
          match step sc s mv with
          | none => pure ()
          | some s2 =>
            nStep := nStep + 1
            let a := tot s + s.xfer + s.itax
            let b := tot s2 + s2.xfer + s2.itax
            if a != b then
              let (c, d) := badVal.getD (kind mv) (0, 0)
              badVal := badVal.insert (kind mv) (c + 1, max d (if a > b then a - b else b - a))
            if bas s2 > bas s then
              let (c, d) := badBas.getD (kind mv) (0, 0)
              badBas := badBas.insert (kind mv) (c + 1, max d (bas s2 - bas s))
        for port in [false, true] do
          let s2 := advance sc s port
          nAdv := nAdv + 1
          let a := tot s + s.xfer + s.itax
          let b := tot s2 + s2.xfer + s2.itax
          let bound := (tot s) * 1403 / 1000 + s.xfer + s.itax + 10
          let (lab, bad, dev) := match s.phase with
            | .plan => ("plan(growth): after > before x growth + 10", decide (b > bound), b - bound)
            | .bed => ("last-year: value changed", a != b, if a > b then a - b else b - a)
            | .estate _ => (if b > a then "estate: money created" else "estate: money lost", a != b, if a > b then a - b else b - a)
          if bad then
            let (c, d) := badAdv.getD lab (0, 0)
            badAdv := badAdv.insert lab (c + 1, max d dev)
            if dev > 1000 && exAdv.length < 4 then
              exAdv := s!"{lab}: dev {dev} at t={s.t}, port={port}, eSp={s.eSp} eT={s.eT} eC={s.eC} eK={s.eK} eQ={s.eQ} own={s.h.own.v}/{s.w.own.v}/{s.c.own.v} q={s.q.v} gtax3={s.h.gtax3}/{s.w.gtax3}/{s.c.gtax3} incl={s.h.incl}/{s.w.incl}/{s.c.incl}" :: exAdv
      let zs := closeOut sc ys
      xs := prune sc cfg.cap cfg.perSig zs
  IO.println s!"steps checked: {nStep}; phase ends checked: {nAdv}; positions breaking a limit (exemption, credit, basis>value): {badLim}"
  IO.println s!"value not conserved in a step, by kind (count, max dev $): {badVal.toList.map fun (k, v) => (kindName k, v)}"
  IO.println s!"basis increased in a step, by kind (count, max $): {badBas.toList.map fun (k, v) => (kindName k, v)}"
  IO.println s!"phase ends not conserving: {badAdv.toList}"
  for e in exAdv do IO.println s!"   e.g. {e}"
  let fin := xs.map fun (s, _) => (tot s + s.xfer + s.itax, wealth s, s.xfer)
  let mx := fin.foldl (fun a (g, _, _) => max a g) 0
  let mw := fin.foldl (fun a (_, w, _) => max a w) 0
  let mn := fin.foldl (fun a (_, _, x) => min a x) 1000000000000
  IO.println s!"end plans {fin.size}: max(holdings+tax paid)={mx}; max wealth={mw}; min transfer tax={mn}; untaxed growth bound={tot s0 * 1403 ^ sc.length / 1000 ^ sc.length}"

def wide : Cfg := { mFirst := 3, mPlan := 2, rounds := 3, cap := 1400, perSig := 4 }

/-- Does a later spouse's exclusion or exemption ever get used without a consented split gift by the other spouse?
Counts over every position the search keeps or expands. -/
def searchLeak (name : String) (sc : Sched) (s0 : St) (cfg : Cfg := {}) : IO Unit := do
  IO.println s!"==== later-spouse leak check: {name} ===="
  let mut xs : Array Node := #[(s0, [])]
  let mut first := true
  let mut n := 0
  let mut withNew := 0
  let mut used := 0
  let mut usedNoSplit := 0
  let mut gstOverGifts := 0
  let mut usedNo2519NoOwnGift := 0
  let mut newOwns := 0
  for _ in [0:3 * sc.length] do
    if xs.size > 0 && xs[0]!.1.t < sc.length then
      let ph := xs[0]!.1.phase
      let (m, r) := match ph with
        | .plan => (if first then cfg.mFirst else cfg.mPlan, cfg.rounds)
        | .bed => (cfg.mBed, 1)
        | .estate _ => (cfg.mEstate, 0)
      first := false
      let mut ys := expand sc m cfg.allowed xs
      for _ in [0:r] do
        ys := prune sc cfg.cap cfg.perSig ys
        ys := expand sc 1 cfg.allowed ys
      for (s, p) in ys do
        n := n + 1
        for (isN, per) in [(s.newH, s.h), (s.newW, s.w)] do
          if isN then
            withNew := withNew + 1
            let g := sig p
            if per.own.v > 0 then newOwns := newOwns + 1
            if per.gifts > 0 || per.gst > 0 || per.cred > 0 || per.dsue > 0 then
              used := used + 1
              if (g >>> 0) % 2 == 0 then usedNoSplit := usedNoSplit + 1
              -- no §2519 release and no lump gift by a grandparent anywhere in the path
              if (g >>> 15) % 2 == 0 && (g >>> 5) % 2 == 0 && (g >>> 6) % 2 == 0 && (g >>> 7) % 2 == 0 && (g >>> 26) % 2 == 0 then
                usedNo2519NoOwnGift := usedNo2519NoOwnGift + 1
            if per.gst > per.gifts then gstOverGifts := gstOverGifts + 1
      let zs := closeOut sc ys
      xs := prune sc cfg.cap cfg.perSig zs
  IO.println s!"positions {n}; with a later spouse {withNew}; later spouse's exclusion/exemption used {used}; of those with no consent in the path {usedNoSplit}; with no §2519 and no lump gift in the path {usedNo2519NoOwnGift}; exemption allocated > gifts attributed {gstOverGifts}; later spouse owning property {newOwns}"

def redScenario : String → IO Unit
  | "leak-q" => searchLeak qName schedQ qStart
  | "leak-A" => searchLeak "A" schedA start
  | "checks1" => redChecks1
  | "d100" => redDirect 100000000
  | "d30" => redDirect 30000000
  | "d40" => redDirect 40000000
  | "q" => search qName schedQ qStart {} 6
  | "q-noremarry" => search (qName ++ ", no remarry") schedQ qStart { allowed := notKind 28 } 3
  | "q-nosplit" => search (qName ++ ", no consent") schedQ qStart { allowed := notKind 0 } 3
  | "q-no2519" => search (qName ++ ", no §2519") schedQ qStart { allowed := notKind 15 } 3
  | "q-only" => search (qName ++ ", only the kinds plan #1 uses") schedQ qStart { allowed := onlyKinds [0, 1, 10, 12, 15, 16, 18, 28] } 3
  | "q-only3" => search (qName ++ ", only remarry, consent, §2519") schedQ qStart { allowed := onlyKinds [0, 15, 28] } 3
  | "q-wide" => search (qName ++ ", wide beam") schedQ qStart wide 4
  | "q-wide-noremarry" => search (qName ++ ", wide beam, no remarry") schedQ qStart { wide with allowed := notKind 28 } 3
  | "q30" => search "QTIP 30M" schedQ (qStart 30000000) {} 4
  | "q30-noremarry" => search "QTIP 30M, no remarry" schedQ (qStart 30000000) { allowed := notKind 28 } 3
  | "cons-q" => searchChk qName schedQ qStart
  | "cons-A" => searchChk "A" schedA start { cap := 140 }
  | "A" => search "A" schedA start {} 3
  | x => IO.println s!"unknown {x}"

def redMain (args : List String) : IO Unit := do
  for a in args do redScenario a

end Legal.USTax.Hunt.Transfer

def main (args : List String) : IO Unit := Legal.USTax.Hunt.Transfer.redMain args
