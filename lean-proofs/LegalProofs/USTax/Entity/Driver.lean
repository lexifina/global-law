import LegalProofs.USTax.Entity.Corp
import LegalProofs.USTax.Family.Driver

/-!
# An owner family and its business over many years

Two parents own a business. Their adult children (each with a wage of their own) and, optionally, one non-grantor
trust per child can be given part of it. Each year the business is held in one of three forms, and the forms can
change at year boundaries:

* `u` — unincorporated: a sole proprietorship while the parents own everything, a partnership once anyone else holds
  an interest (§761(a); a family partnership, §704(e));
* `s` — a corporation with an S election (§1362(a));
* `c` — a C corporation.

Every year's income tax of each person is computed by the 2025 household model (`TaxCode/Individual`, Form 1040
with SE tax, §199A with the W-2 wage limit, §1411 and the additional Medicare tax); the trusts by `Family/Trust.lean`'s
§1(e) schedule; the corporation by `Corp.lean`. At the horizon the business is sold, or the parents die holding it,
and the parents die then in either case (so the estate tax is always computed at the same moment).

**Assumptions, stated loudly.**
* 2025 law in every year, in real 2025 dollars, deterministic returns (as in `Family/Driver.lean`). The estate-tax
  exclusion is 2025's $13,990,000 each, with portability, not Pub. L. 119-21's $15,000,000 from 2026.
* The business's profit `P` (before the owner's pay, after staff wages) grows at a fixed real rate; its value is
  `multiple × P` plus whatever profit it has had to reinvest (`needBp` of each year's profit after the owner's wage and
  any corporate tax, for the first `needYears` years; zero in all but the `venture` scenario). Reinvested profit is
  an active operating asset at cost (it adds to value and inside basis one for one and earns nothing beyond the
  profit path); a pass-through's owners are taxed on it without receiving it and their basis rises (§§705, 1367). Its assets are capital or §1231 assets with inside
  basis `assetBasis` (self-created goodwill has none); no depreciation recapture, receivables or inventory, so no
  §751 or §1245 ordinary income on a sale.
* A buyer pays the business's value for its assets, for a partnership interest (it gets a §743(b) step-up) and for S
  stock (with a §338(h)(10) election, so the seller is taxed as on an asset sale). A buyer of C stock gets no step-up
  and pays less by the present value of the §197 amortization forgone on the inside gain (`stepUpPv`); for a C
  corporation's portfolio it deducts the 21 percent tax on the unrealised gain.
* Every income tax (individual, trust, corporate, the accumulated earnings tax) is paid in the year after it accrues;
  payroll taxes in the year. No estimated-tax timing, no state taxes.
* Payroll taxes are counted as taxes, with no credit for the Social Security benefits they buy. The business is the
  head's alone (one SE wage base; not a §761(f) joint venture). A net capital loss is limited to $3,000 a year with
  no carryforward (the household model's).
* The owner's wage: in S years at least the reasonable compensation `rcLo` (Rev. Rul. 74-44; §1366(e)); in C years no
  more than `rcHi` (§162(a)(1): more is a disguised dividend). In `u` years the owner is a general partner or
  proprietor, and all of the parents' share is self-employment income (§1402(a)); a child's or trust's interest is a
  limited partner's (§1402(a)(13)), passive (§469), and so net investment income (§1411(c)(2)).
* §704(e)(1): a donee's share is figured after a reasonable allowance (`rcLo`) for the donor's services; and under
  §761(b) and Reg. §1.704-1(e)(1)(iv) a donee is a partner for income only if capital is a material income-producing
  factor (`capitalMaterial`; false for a services business, whose income then stays with the parents).
* A C corporation's retained earnings are invested in a portfolio. The accumulated earnings tax (§531) applies, with
  `reasonableNeeds` the business's total need for retained earnings (Reg. §1.537-2) and the dividends-received
  deduction added back (§535(b)(3)). §1202's active-business test fails, for the rest of the stock's life, in any
  year in which securities beyond the reasonably required working capital (at most `reasonableNeeds`) exceed 10
  percent of net assets (§1202(e)(5)(B)) or, after 2 years, working capital exceeds half of all assets ((e)(6)). The
  personal holding company tax (§541) is not modelled (the business's income is active). After a `c`→`s` change the
  portfolio stays in the S corporation and its income passes through as investment income; the §1375 tax and the
  §1362(d)(3) termination for passive income with C-year earnings and profits are not modelled.
* Conversions. `u`→`s`, `u`→`c`: §351, no gain; stock basis is the asset basis (§358); a `c` issued this way is
  qualified small business stock if the business is not a §1202(e)(3) field and is worth no more than $75,000,000
  (§1202(d)(1)), with §1202(i) basis equal to fair market value and acquisition at the exchange. `s`→`c`: the
  election is revoked (§1362(d)(1)); the stock, issued while an S corporation, is never QSBS (§1202(c)(1)); a new S
  election waits 5 years (§1362(g)). `c`→`s`: §1374 for 5 years on the built-in gain at the start; the QSBS status is
  lost. To `u` from a corporation: a liquidation (§§331, 336; for `c` the corporate tax on the gain first).
* A gift of equity is valued at its pro rata share of the business (no minority discount), uses unified credit and is
  added back at death (§2001(b)); gift tax at 40 percent is paid in the year on gifts beyond the two exclusions
  (§§2501, 2505), credited at death (§2001(b)(2)) and, if paid within 3 years of death, added to the estate
  (§2035(b)). A liquidation of a C corporation into `u` gets no §1202 exclusion here (a simplification against it).
  The donee takes the donor's basis (§1015) and, for QSBS, its holding period and
  status (§1202(h)(2)(A)). S stock given to a trust makes it an electing small business trust (§1361(e)), taxed on
  its S income at 37 percent (§641(c)).
* The children's own wages are taxed in every plan alike: only the extra tax is the family's. At the horizon each
  trust distributes in kind to its child (§643(e)); a child's unrealised gain is taxed as if sold over ten years on top
  of the child's wage (as in `Family/Driver.lean`).
-/

namespace Legal.USTax.Entity
open TaxCode.Individual Legal.USTax.Family

inductive Form where
  | u | s | c
  deriving Repr, DecidableEq, Inhabited

inductive Exit where
  | sale          -- every holder sells its interest or stock at the horizon
  | assetSale     -- the entity sells its assets and is liquidated
  | death         -- the parents die holding their part; everyone then sells their interest or stock
  deriving Repr, DecidableEq, Inhabited

structure Biz where
  profit : Int
  growthBp : Int
  fastYears : Nat := 0           -- years of `fastBp` growth before `growthBp`
  fastBp : Int := 0
  multipleX10 : Int              -- value = multipleX10 × profit / 10
  staffWages : Int               -- W-2 wages to employees, already deducted from profit (§199A(b)(4))
  ubia : Int := 0
  assetBasis : Int := 0
  sstb : Bool := false           -- §199A(d)(2) and §1202(e)(3)(A)
  rcLo : Int
  rcHi : Int
  reasonableNeeds : Int := 0
  capitalMaterial : Bool := true -- §761(b), Reg. §1.704-1(e)(1)(iv): capital is a material income-producing factor
  needBp : Int := 0              -- share of the year's profit (after the owner's wage and any corporate tax) the
  needYears : Nat := 0           -- business must reinvest in its own operating assets, in the first `needYears` years
  deriving Repr, Inhabited

structure Kid where
  age : Nat
  wage : Int
  deriving Repr, Inhabited

structure ESpec where
  ageH : Nat
  ageS : Nat
  wageS : Int := 0
  spending : Int
  brokerage : Acct
  biz : Biz
  kids : List Kid
  growthBp : Int
  divBp : Int
  intBp : Int
  horizon : Nat
  deriving Repr, Inhabited

/-- A gift at the start of `year` of `bp` basis points of the parents' share, split equally among the children, or
among the children's trusts. -/
structure Gift where
  year : Nat
  bp : Int
  toTrusts : Bool
  deriving Repr, Inhabited

structure EPlan where
  forms : List (Nat × Form)      -- (first year, form); the form before the first entry is `u`
  salary : Int := 0              -- the owner's wage in corporate years (clamped as stated above)
  payoutBp : Int := 10000        -- a C corporation's dividends, as a share of its after-tax income
  gifts : List Gift := []
  exit : Exit := .sale
  deriving Repr, Inhabited

/-! ## Holders -/

def ppm : Int := 1000000

structure Holding where
  share : Int := 0      -- parts per million of the business
  basis : Int := 0      -- basis of the interest or stock
  qBasis : Int := 0     -- §1202(i) basis (C stock issued in a §351 exchange)
  deriving Repr, Inhabited

/-- The entity's own state. -/
structure Ent where
  form : Form := .u
  inside : Int                   -- adjusted basis of the business assets
  port : Acct := ⟨0, 0⟩          -- a C corporation's portfolio
  accEP : Int := 0               -- accumulated earnings and profits (C years)
  sStart : Int := -1             -- first year of the current S election
  nubigLeft : Int := 0           -- §1374(c)(2) room
  sTerm : Int := -100            -- year an S election last ended (§1362(g))
  qYear : Int := -1              -- §1202 acquisition year of the stock (−1: not QSBS)
  qOk : Bool := false
  corpOwe : Int := 0             -- last year's corporate income tax and accumulated earnings tax, paid this year
  opCap : Int := 0               -- profit reinvested in operating assets (active; adds to value and to inside basis)
  deriving Repr, Inhabited

structure ESt where
  ent : Ent
  profit : Int
  hold : List Holding            -- 0: the parents; 1..n: children; n+1..2n: their trusts
  acct : List Acct               -- the same order: each holder's own taxable account
  owe : List Int                 -- each holder's tax for last year, paid this year
  giftsOver : Int := 0
  giftTax : Int := 0             -- gift tax paid (§2501), credited at death (§2001(b)(2))
  giftTaxLate : Int := 0         -- of which paid in the last 3 years before death (§2035(b))
  taxPaid : Int := 0
  corpTaxPaid : Int := 0
  payroll : Int := 0
  deriving Repr, Inhabited

structure EYear where
  form : String
  profit : Int
  parentsTax : Int
  kidsTax : Int
  trustsTax : Int
  corpTax : Int
  payroll : Int
  deriving Repr

def formName : Form → String | .u => "u" | .s => "s" | .c => "c"

/-! ## Small helpers -/

def person (a : Nat) : Person := { age := a }

def ficaEmployee (w : Int) : Int := bps (min w 176100) 620 + bps w 145
def ficaEmployer (w : Int) : Int := bps (min w 176100) 620 + bps w 145
def valueOf (b : Biz) (p : Int) : Int := b.multipleX10 * p / 10
def shareOf (x share : Int) : Int := x * share / ppm
def getH (l : List Holding) (i : Nat) : Holding := l.getD i {}
def getA (l : List Acct) (i : Nat) : Acct := l.getD i ⟨0, 0⟩
def formAt (p : EPlan) (y : Nat) : Form :=
  (p.forms.filter (fun e => e.1 ≤ y)).foldl (fun _ e => e.2) .u

/-- A trust's own return (non-grantor, accumulating; §641, §1(e), §1411(a)(2), §199A at the single threshold):
`ord` ordinary income (a partnership share or interest), `qbi`, `w2` its share of W-2 wages, `cg` qualified dividends
and long-term gain, `nii` its net investment income. -/
def trustTaxOn (ord qbi w2 cg nii : Int) (ubia : Int := 0) : Int :=
  let gross := ord + cg
  let tBefore := max 0 (gross - 100)
  let qd := max 0 (min (B.qbiComponent .single tBefore qbi w2 ubia) (roundDollar (20 * max 0 (tBefore - cg)) 100))
  let ti := max 0 (tBefore - qd)
  trustTax ti cg + roundDollar (38 * min (max 0 nii) (max 0 (gross - 100 - 15650))) 1000

/-- The extra tax on a child of `extra` household items over the child's own wage. -/
def kidExtra (k : Kid) (h : Household) (f : B.Facts) : Int :=
  let base : Household := { filing := .single, head := person (k.age), wages := k.wage }
  (form1040With f { h with filing := .single, head := person (k.age), wages := k.wage }).netTax - (form1040With {} base).netTax

/-- What one holder receives from the business in a year, for its return. -/
structure Flow where
  wage : Int := 0
  se : Int := 0          -- self-employment income (a sole proprietor's or general partner's share)
  active : Int := 0      -- nonpassive pass-through ordinary income (S K-1)
  passive : Int := 0     -- passive pass-through ordinary income
  qbi : Int := 0         -- QBI other than Schedule C / SE income (which the household model adds itself)
  w2 : Int := 0          -- share of W-2 wages for §199A
  qdiv : Int := 0        -- qualified dividends
  intr : Int := 0        -- interest (portfolio income passed through by an S corporation)
  esbt : Int := 0        -- an ESBT's S income
  esbtCg : Int := 0      -- an ESBT's S qualified dividends
  cash : Int := 0        -- money received
  deriving Repr, Inhabited

/-! ## Conversions -/

/-- Changing form at the start of year `y` with business value `v`. Returns the new entity, holdings, and each
holder's (long-term gain, net investment part, money received) from a liquidation, and the corporate tax. -/
def convert (s : ESpec) (y : Nat) (v : Int) (e : Ent) (hs : List Holding) (to : Form) (gPay : Int := 0) :
    Ent × List Holding × List (Int × Int × Int) × Int :=
  let none3 := hs.map fun _ => ((0 : Int), (0 : Int), (0 : Int))
  if e.form = to then (e, hs, none3, 0) else
  match e.form, to with
  | .u, .s => ({ e with form := .s, sStart := y, nubigLeft := 0 }, hs, none3, 0)
  | .u, .c =>
    let q := !s.biz.sstb && v ≤ 75000000
    ({ e with form := .c, qYear := if q then y else -1, qOk := q },
     hs.map fun h => { h with qBasis := shareOf v h.share }, none3, 0)
  | .s, .c => ({ e with form := .c, sTerm := y, qYear := -1, qOk := false }, hs, none3, 0)
  | .c, .s =>
    if (y : Int) - e.sTerm < 5 then (e, hs, none3, 0) else   -- §1362(g): too soon; stays a C corporation
    let nubig := max 0 (v + e.port.value - e.inside - e.port.basis)
    -- the gain realised paying the last C year's tax is taxed as a C corporation's
    ({ e with form := .s, sStart := y, nubigLeft := nubig, qYear := -1, qOk := false }, hs, none3, corpTax gPay)
  | .s, .u =>
    -- §336 gain passes through (§1366), raising stock basis (§1367); §331 on the rest; §1374 if in the period
    let gain := v - e.inside
    let big := if 0 ≤ e.sStart then bigTax (y - e.sStart.toNat) (max 0 gain) (max 0 gain) e.nubigLeft else 0
    let outs := (List.range hs.length).map fun i =>
      let h := getH hs i
      let cash := shareOf (e.port.value - big) h.share
      let g := shareOf (v + e.port.value - big) h.share - h.basis
      -- §1411(c)(4): only the trade or business part of an active owner's gain is outside NII
      (g, (if i = 0 then shareOf (e.port.value - e.port.basis) h.share else g), cash)
    ({ e with form := .u, inside := v, port := ⟨0, 0⟩, sTerm := y, sStart := -1 },
     hs.map fun h => { h with basis := shareOf v h.share }, outs, big)
  | .c, .u =>
    let ct := corpTax (v + e.port.value - e.inside - e.port.basis + gPay)
    let net := v + e.port.value - ct
    let outs := (List.range hs.length).map fun i =>
      let h := getH hs i
      let g := shareOf net h.share - h.basis
      (g, g, shareOf (e.port.value - ct) h.share)
    ({ e with form := .u, inside := v, port := ⟨0, 0⟩, accEP := 0, qYear := -1, qOk := false },
     hs.map fun h => { h with basis := shareOf v h.share }, outs, ct)
  | _, _ => (e, hs, none3, 0)

/-! ## One year -/

def nKids (s : ESpec) : Nat := s.kids.length

def year (s : ESpec) (p : EPlan) (y : Nat) (st : ESt) : ESt × EYear :=
  let n := nKids s
  let b := s.biz
  let P := st.profit
  let v := valueOf b P + st.ent.opCap
  let need := if y < b.needYears then b.needBp else 0
  -- 0. last year's corporate tax, from the corporation's portfolio (a realised gain is taxed with this year's income)
  let (portPaid, gPay) := settle st.ent.port (-st.ent.corpOwe)
  let entPre := { st.ent with port := portPaid, corpOwe := 0 }
  -- 1. form change
  let (ent0, hs0, liq, liqCorp) := convert s y v entPre st.hold (formAt p y) gPay
  -- 2. gifts (no discount), §1015 basis, §1202(h)
  let equity := v + ent0.port.value
  let (hs1, gv) := p.gifts.foldl (fun (acc : List Holding × Int) g =>
      if g.year ≠ y || n = 0 then acc else
      let hs := acc.1
      let par := getH hs 0
      let moved := par.share * g.bp / 10000
      let mb := if par.share = 0 then 0 else par.basis * moved / par.share
      let mq := if par.share = 0 then 0 else par.qBasis * moved / par.share
      let hs := hs.set 0 { share := par.share - moved, basis := par.basis - mb, qBasis := par.qBasis - mq }
      let off := if g.toTrusts then n + 1 else 1
      let hs := (List.range n).foldl (fun hs i =>
        let h := getH hs (off + i)
        hs.set (off + i) { share := h.share + moved / n, basis := h.basis + mb / n, qBasis := h.qBasis + mq / n }) hs
      (hs, acc.2 + shareOf equity moved)) (hs0, 0)
  -- §§2501, 2502, 2505: gift tax on taxable gifts beyond the two unified credits, paid now (40 percent above them)
  let giftTaxNow := (max 0 (st.giftsOver + gv - 2 * estateExclusion) - max 0 (st.giftsOver - 2 * estateExclusion)) * 40 / 100
  let m := hs1.length
  -- 3. operations
  let others := (List.range m).any fun i => i ≠ 0 && (getH hs1 i).share > 0
  let (flows, ent1, corpT, payrollT) : List Flow × Ent × Int × Int :=
    match ent0.form with
    | .u =>
      let allow := if others then min P b.rcLo else 0                   -- §704(e)(1)
      -- §761(b): where capital is not a material income-producing factor a donee is not a partner for income
      let allow := if b.capitalMaterial then allow else P
      let rest := P - allow
      -- reinvested profit is income to the partners all the same (§702), but not paid out
      let reinv := bps (max 0 (P - (if need > 0 then b.rcLo else 0))) need
      let fl := (List.range m).map fun i =>
        let h := getH hs1 i
        let x := shareOf rest h.share + (if i = 0 then allow else 0)
        let c := x - shareOf reinv h.share
        let w2 := shareOf b.staffWages h.share
        if i = 0 then { se := x, w2 := w2, cash := c }
        else if i ≤ n then { passive := x, qbi := x, w2 := w2, cash := c }
        else { passive := x, qbi := x, w2 := w2, cash := c }
      (fl, { ent0 with opCap := ent0.opCap + reinv, inside := ent0.inside + reinv }, 0, 0)
    | .s =>
      -- while the business must reinvest, the owner can be paid no more than the reasonable wage (in every form)
      let w := if need > 0 then min P b.rcLo else min P (max b.rcLo p.salary)
      let er := ficaEmployer w
      let k1 := P - w - er
      -- a portfolio kept from C years: its income passes through (§1366) and is paid out; it is investment income
      let pDiv := bps (max 0 ent0.port.value) s.divBp
      let pInt := bps (max 0 ent0.port.value) s.intBp
      let reinv := bps (max 0 k1) need
      let fl := (List.range m).map fun i =>
        let h := getH hs1 i
        let x := shareOf k1 h.share
        let r := shareOf reinv h.share
        let dv := shareOf pDiv h.share
        let it := shareOf pInt h.share
        let w2 := shareOf (b.staffWages + w) h.share
        if i = 0 then { wage := w, active := x, qbi := x, w2 := w2, qdiv := dv, intr := it, cash := w + x - r + dv + it }
        else if i ≤ n then { passive := x, qbi := x, w2 := w2, qdiv := dv, intr := it, cash := x - r + dv + it }
        else { esbt := x + it, qbi := x, esbtCg := dv, w2 := w2, cash := x - r + dv + it }
      (fl, { ent0 with opCap := ent0.opCap + reinv, inside := ent0.inside + reinv }, 0, er + ficaEmployee w)
    | .c =>
      -- the wage and the employer's tax on it never exceed the profit
      let w := max 0 (min (P * 10000 / 10765) (if need > 0 then min b.rcLo p.salary else min b.rcHi p.salary))
      let er := ficaEmployer w
      let pDiv := bps (max 0 ent0.port.value) s.divBp
      let pInt := bps (max 0 ent0.port.value) s.intBp
      let ti := P - w - er + pInt + pDiv - pDiv / 2 + gPay                -- §243(a)(1)
      let ct := corpTax ti
      let after := P - w - er + pInt + pDiv + gPay - ct
      -- reinvestment comes first (it is a reasonable need of the business, §537(a)(1)); the payout is of the rest
      let reinv := bps (max 0 (P - w - er - corpTax (P - w - er))) need
      let div := bps (max 0 (after - reinv)) p.payoutBp
      let aetT := aet b.sstb ti (pDiv / 2) (div + reinv) b.reasonableNeeds ent0.accEP
      -- this year's taxes are paid next year (as the individuals' are)
      let port1 := (settle ent0.port (P - w - er + pInt + pDiv - div - reinv)).1
      -- §1202(c)(2)(A), (e)(5)(B), (e)(6): securities beyond the reasonably required working capital may be no more
      -- than 10 percent of net assets, and after 2 years working capital no more than half of all assets
      let wc := min (max 0 port1.value) b.reasonableNeeds
      let excess := port1.value - wc
      let tot := v + port1.value
      -- after 2 years working capital beyond half of all assets stops counting as active ((e)(6)); then 80 percent
      -- of assets must be active ((c)(2)(A)); net assets are after the corporate tax owed
      let wcOver := if (y : Int) - ent0.qYear < 2 then 0 else max 0 (wc - tot / 2)
      let ok := ent0.qOk && decide (10 * excess ≤ tot - (ct + aetT)) && decide (5 * (excess + wcOver) ≤ tot)
      let fl := (List.range m).map fun i =>
        let h := getH hs1 i
        let d := shareOf div h.share
        if i = 0 then { wage := w, qdiv := d, cash := w + d } else { qdiv := d, cash := d }
      let entC : Ent := { ent0 with port := port1, accEP := ent0.accEP + after - div - aetT, qOk := ok }
      let entC : Ent := { entC with corpOwe := ct + aetT, opCap := ent0.opCap + reinv, inside := ent0.inside + reinv }
      (fl, entC, ct + aetT, er + ficaEmployee w)
  -- 4. each holder's return
  let fa (i : Nat) : Flow := flows.getD i {}
  let oweOf (i : Nat) : Int := st.owe.getD i 0
  let liqOf (i : Nat) : Int × Int × Int := liq.getD i (0, 0, 0)
  -- the parents
  let pa := getA st.acct 0
  let pDivB := bps (max 0 pa.value) s.divBp
  let pIntB := bps (max 0 pa.value) s.intBp
  let f0 := fa 0
  let (lg0, ln0, lc0) := liqOf 0
  let ageH := s.ageH + y
  let ageS := s.ageS + y
  let preCash := f0.cash + lc0 + s.wageS + pDivB + pIntB - s.spending - ficaEmployee f0.wage - oweOf 0 - giftTaxNow
  let (pa1, gSale) := settle pa preCash
  let hhP : Household :=
    { filing := .mfj, head := person (ageH), spouse := some (person (ageS)),
      wages := f0.wage + s.wageS, wagesSpouse := s.wageS, seIncome := f0.se, otherIncome := f0.active,
      taxableInterest := pIntB + f0.passive + f0.intr, ordinaryDividends := pDivB + f0.qdiv,
      qualifiedDividends := pDivB + f0.qdiv, longTermGains := gSale + lg0, qbi := f0.qbi }
  let factsP : B.Facts := { qbiW2Wages := f0.w2, qbiUbia := shareOf b.ubia (getH hs1 0).share, qbiSstb := b.sstb }
  let lP := form1040With factsP hhP
  -- §1411(c)(4), (c)(6): an S liquidation's pass-through gain of an active owner is not net investment income
  let taxP := lP.netTax - lP.niit + A.niit { hhP with longTermGains := hhP.longTermGains - (lg0 - ln0) } lP.agi
  -- children and trusts
  let kidRes := (List.range n).map fun i =>
    let k := s.kids.getD i default
    let a := getA st.acct (1 + i)
    let f := fa (1 + i)
    let (lg, ln, lc) := liqOf (1 + i)
    let d := bps (max 0 a.value) s.divBp
    let it := bps (max 0 a.value) s.intBp
    let (a1, g) := settle a (f.cash + lc + d + it - oweOf (1 + i))
    let h : Household :=
      { filing := .single, head := person (k.age + y), wages := k.wage,
        taxableInterest := it + f.passive + f.intr, ordinaryDividends := d + f.qdiv, qualifiedDividends := d + f.qdiv,
        longTermGains := g + lg, qbi := f.qbi, otherIncome := 0 }
    let _ := ln
    let t := kidExtra { k with age := k.age + y } h
      { qbiW2Wages := f.w2, qbiUbia := shareOf b.ubia (getH hs1 (1 + i)).share, qbiSstb := b.sstb }
    (a1, t)
  let trustRes := (List.range n).map fun i =>
    let a := getA st.acct (n + 1 + i)
    let f := fa (n + 1 + i)
    let (lg, _, lc) := liqOf (n + 1 + i)
    let d := bps (max 0 a.value) s.divBp
    let it := bps (max 0 a.value) s.intBp
    let (a1, g) := settle a (f.cash + lc + d + it - oweOf (n + 1 + i))
    let es := if f.esbt = 0 ∧ f.esbtCg = 0 then 0 else
      let ub := shareOf b.ubia (getH hs1 (n + 1 + i)).share
      let qd := max 0 (min (B.qbiComponent .single f.esbt f.qbi f.w2 ub) (bps f.esbt 2000))
      esbtTax f.esbt qd f.esbtCg (f.esbt + f.esbtCg)
    let t := es + trustTaxOn (it + f.passive) (if f.esbt = 0 ∧ f.esbtCg = 0 then f.qbi else 0) f.w2
      (d + f.qdiv + g + lg) (it + f.passive + d + f.qdiv + g + lg) (shareOf b.ubia (getH hs1 (n + 1 + i)).share)
    (a1, t)
  let kidsTax := (kidRes.map (·.2)).sum
  let trustsTax := (trustRes.map (·.2)).sum
  -- 5. growth
  let grow (a : Acct) : Acct := { a with value := a.value + bps a.value (if a.value < 0 then s.growthBp + s.divBp + s.intBp else s.growthBp) }
  let ent2 := { ent1 with port := grow ent1.port }
  let g := if y < b.fastYears then b.fastBp else b.growthBp
  let accts := [grow pa1] ++ kidRes.map (fun r => grow r.1) ++ trustRes.map (fun r => grow r.1)
  let total := taxP + kidsTax + trustsTax
  let addB := if ent0.form = .c then 0 else ent1.opCap - ent0.opCap
  let hs2 := hs1.map fun h => { h with basis := h.basis + shareOf addB h.share }
  ({ ent := ent2, profit := P + bps P g, hold := hs2, acct := accts,
     owe := [taxP] ++ kidRes.map (·.2) ++ trustRes.map (·.2),
     giftsOver := st.giftsOver + gv, giftTax := st.giftTax + giftTaxNow,
     giftTaxLate := st.giftTaxLate + (if s.horizon ≤ y + 3 then giftTaxNow else 0), taxPaid := st.taxPaid + total + corpT + liqCorp + payrollT,
     corpTaxPaid := st.corpTaxPaid + corpT + liqCorp, payroll := st.payroll + payrollT },
   ⟨formName ent0.form, P, taxP, kidsTax, trustsTax, corpT + liqCorp, payrollT⟩)

/-! ## The horizon -/

structure EOutcome where
  wealth : Int
  parents : Int          -- the parents' estate after estate tax
  estateTax : Int
  exitTax : Int          -- tax on the exit itself: corporate and every holder's
  kidsHeld : Int
  kidsLatent : Int
  taxPaid : Int          -- income, payroll and corporate tax over the years
  corpTaxPaid : Int
  payroll : Int
  qsbsExcluded : Int
  finalForm : String
  log : List EYear
  deriving Repr

/-- The extra tax on ten equal years of gain `gain` on top of a child's wage. -/
def kidTen (k : Kid) (gain : Int) : Int :=
  let h0 : Household := { filing := .single, head := person (k.age), wages := k.wage }
  if gain ≤ 0 then 0 else
  10 * ((form1040 { h0 with longTermGains := gain / 10 }).netTax - (form1040 h0).netTax)

/-- A holder's sale of its interest or stock for `price`: (tax, QSBS excluded). `kind`: 0 the parents (joint),
1 a child (single, on top of its wage), 2 a trust. `active`: §1411(c)(4) leaves the gain out of NII (a materially
participating owner of a `u` or `s` business). -/
def saleTax (s : ESpec) (e : Ent) (y : Nat) (kind : Nat) (k : Kid) (h : Holding) (price : Int) (active : Bool)
    (other : Int := 0) (niiExtra : Int := 0) : Int × Int :=
  let gain := price - h.basis
  let held : Nat := if e.qYear < 0 then 0 else (y - e.qYear.toNat)
  let q := if e.form = .c ∧ e.qOk ∧ 0 ≤ e.qYear then
      qsbsSplit { gain := max 0 (price - h.qBasis), heldYears := held, basisSold := h.qBasis }
    else ⟨0, 0, 0, 0⟩
  -- §1202(i): gain before the exchange is taxed, but never more than the gain
  let pre := if e.form = .c ∧ e.qOk ∧ 0 ≤ e.qYear then min (h.qBasis - h.basis) (max 0 gain) else 0
  let ltcg := if e.form = .c ∧ e.qOk ∧ 0 ≤ e.qYear then q.ltcg + pre else gain
  let nii := if active then niiExtra else ltcg + q.g28
  match kind with
  | 0 =>
    -- the parents' sale in the year of their death, on top of that year's other income (the spouse's wage and the
    -- portfolio's yield, `other`): the extra tax
    let h0 : Household :=
      { filing := .mfj, head := person (s.ageH + y), spouse := some (person (s.ageS + y)),
        wages := s.wageS, wagesSpouse := s.wageS, qualifiedDividends := other * s.divBp / max 1 (s.divBp + s.intBp),
        ordinaryDividends := other * s.divBp / max 1 (s.divBp + s.intBp),
        taxableInterest := other - other * s.divBp / max 1 (s.divBp + s.intBp) }
    let l0 := form1040With {} h0
    let hh := { h0 with longTermGains := ltcg + q.g28 }
    let l := form1040With {} hh
    let ti := l.taxableIncome
    let reg := taxWith28 .mfj ti (min ti (ltcg + other * s.divBp / max 1 (s.divBp + s.intBp))) q.g28
    let niit := roundDollar (38 * min (max 0 (nii + other)) (max 0 (l.agi - 250000))) 1000
    (reg + niit + l.amt - (l0.regularTax + l0.niit + l0.amt), q.excluded)
  | 1 =>
    let h0 : Household := { filing := .single, head := person (k.age), wages := k.wage }
    let hh := { h0 with longTermGains := ltcg + q.g28, taxableInterest := 0 }
    let l := form1040With {} hh
    let ti := l.taxableIncome
    let reg := taxWith28 .single ti (min ti ltcg) q.g28
    let niit := roundDollar (38 * min (max 0 nii) (max 0 (l.agi - 200000))) 1000
    let base := (form1040With {} h0).regularTax
    (reg + niit + l.amt - base, q.excluded)
  | _ =>
    let g := ltcg + q.g28
    let ti := max 0 (g - 100)
    if e.form = .s then
      -- an ESBT's sale of S stock is in its S portion (§641(c)(2)(C)(ii)): §1(h) rates, no lower brackets
      (bps (max 0 g) 2000 + roundDollar (38 * max 0 (nii - 15650)) 1000, 0)
    else
    -- §1(h) for a trust: 28-percent gain at no more than 28 percent; never more than the ordinary schedule
    let t := min (trustTax ti (max 0 (min ti (ltcg + q.g28))) + bps (max 0 (min q.g28 ti)) 800) (trustTax ti 0)
    (t + roundDollar (38 * min (max 0 nii) (max 0 (g - 100 - 15650))) 1000, q.excluded)

/-- The present value of 15 years of straight-line §197 amortization, per dollar, at 5 percent: 0.692 (in
thousandths). -/
def stepUpPv : Int := 692

def finish (s : ESpec) (p : EPlan) (st : ESt) (log : List EYear) : EOutcome :=
  let n := nKids s
  let y := s.horizon
  let b := s.biz
  let e := st.ent
  let v := valueOf b st.profit + e.opCap
  let hs := st.hold
  -- last year's tax, paid by selling: the gain realised is taxed with the rest (the children's and trusts' with their
  -- latent gain, the parents' at 23.8 percent unless they die holding, when §1014 erases it)
  let paid := (List.range st.acct.length).map fun i => sell (getA st.acct i) (st.owe.getD i 0)
  let realised (i : Nat) : Int := (paid.getD i (⟨0, 0⟩, 0)).2
  let st := { st with acct := paid.map (fun (x : Acct × Int) => x.1) }
  -- last year's corporate tax
  let (portF, gF) := settle e.port (-e.corpOwe)
  let e := { e with port := portF, corpOwe := 0 }
  -- the entity-level part of the exit; the gain realised paying last year's tax is taxed with it
  let portNet := e.port.value - corpTax (e.port.value - e.port.basis + gF)    -- buyer deducts the latent tax
  -- a buyer of C stock gets no step-up in the business's assets: it pays less by the present value of the §197
  -- amortization it forgoes on the inside gain (21 percent over 15 years, discounted at 5 percent: factor 0.692)
  let vStock := v - corpTax (max 0 (v - e.inside)) * stepUpPv / 1000
  let (prices, entTax, hs2) : List Int × Int × List Holding :=
    match e.form with
    | .c =>
      if p.exit = .assetSale then
        let ct := corpTax (v + e.port.value - e.inside - e.port.basis + gF)
        ((List.range hs.length).map (fun i => shareOf (v + e.port.value - ct) (getH hs i).share), ct, hs)
      else ((List.range hs.length).map (fun i => shareOf (vStock + portNet) (getH hs i).share), 0, hs)
    | .s =>
      -- a buyer of S stock takes a §338(h)(10) election, so stock, assets and an heirs' sale are taxed alike: the
      -- inside gain passes through, raising basis, and the liquidation gives the rest; §1374 in the period
      let gain := v + e.port.value - e.inside - e.port.basis
      let big := if 0 ≤ e.sStart then bigTax (y - e.sStart.toNat) (max 0 gain) (max 0 gain) e.nubigLeft else 0
      ((List.range hs.length).map (fun i => shareOf (v + e.port.value - big) (getH hs i).share), big, hs)
    | .u => ((List.range hs.length).map (fun i => shareOf v (getH hs i).share), 0, hs)
  -- holders' taxes on the exit
  let par := getH hs2 0
  let parentsSale : Int × Int :=
    if p.exit = .death then (0, 0)                                   -- §1014: basis = value at death
    else
      -- the active owner's gain is outside NII except a C corporation's (stock) or a kept portfolio's
      let portGain := if e.form = .s then shareOf (e.port.value - e.port.basis) par.share else 0
      saleTax s e y 0 default par (prices.getD 0 0) (e.form ≠ .c)
        (bps (max 0 (getA st.acct 0).value) (s.divBp + s.intBp)) portGain
  let kidSales := (List.range n).map fun i =>
    let k := s.kids.getD i default
    let k := { k with age := k.age + y }
    let a := saleTax s e y 1 k (getH hs2 (1 + i)) (prices.getD (1 + i) 0) false
    let t := saleTax s e y 2 k (getH hs2 (n + 1 + i)) (prices.getD (n + 1 + i) 0) false
    (a, t)
  let parentsSale := (parentsSale.1 + (if p.exit = .death then 0 else realised 0 * 238 / 1000), parentsSale.2)
  let exitTax := entTax + parentsSale.1 + (kidSales.map (fun x => x.1.1 + x.2.1)).sum
  let excluded := parentsSale.2 + (kidSales.map (fun x => x.1.2 + x.2.2)).sum
  -- the parents' estate
  let pa := getA st.acct 0
  let estate := pa.value + prices.getD 0 0 - parentsSale.1
  -- §2001(b): 40 percent of the taxable estate (with §2035(b)'s gross-up for gift tax paid in the last 3 years) plus
  -- adjusted taxable gifts above the two exclusions, less the gift tax payable on those gifts (§2001(b)(2))
  let estTax := max 0 (max 0 (estate + st.giftTaxLate + st.giftsOver - 2 * estateExclusion) * 40 / 100 - st.giftTax)
  -- the children: own account + trust account + sale proceeds after tax
  let kidsHeld := (List.range n).foldl (fun t i =>
    let x := kidSales.getD i ((0, 0), (0, 0))
    t + (getA st.acct (1 + i)).value + (getA st.acct (n + 1 + i)).value + prices.getD (1 + i) 0 + prices.getD (n + 1 + i) 0
      - x.1.1 - x.2.1) 0
  let latent := (List.range n).foldl (fun t i =>
    let k := s.kids.getD i default
    let a := getA st.acct (1 + i)
    let tr := getA st.acct (n + 1 + i)
    t + kidTen { k with age := k.age + y } (unrealised a + unrealised tr + realised (1 + i) + realised (n + 1 + i))) 0
  let wealth := estate - estTax + kidsHeld - latent
  ⟨wealth, estate - estTax, estTax, exitTax, kidsHeld, latent, st.taxPaid, st.corpTaxPaid, st.payroll, excluded,
    formName e.form, log⟩

def init (s : ESpec) : ESt :=
  let n := nKids s
  { ent := { inside := s.biz.assetBasis }, profit := s.biz.profit,
    hold := [{ share := ppm, basis := s.biz.assetBasis }] ++ List.replicate (2 * n) {},
    acct := [s.brokerage] ++ List.replicate (2 * n) ⟨0, 0⟩, owe := List.replicate (2 * n + 1) 0 }

def simulate (s : ESpec) (p : EPlan) : EOutcome :=
  let rec go : Nat → ESt → List EYear → ESt × List EYear
    | 0, st, log => (st, log)
    | k + 1, st, log =>
      let y := s.horizon - (k + 1)
      let (st', l) := year s p y st
      go k st' (log ++ [l])
  let (st, log) := go s.horizon (init s) []
  finish s p st log

end Legal.USTax.Entity
