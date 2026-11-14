import LegalProofs.USTax.Entity.Partnership
import TaxCode.Individual.Form1040

/-!
# Corporations: subchapters C and S, and the corporate stock rules at the owner boundary

Written from the Code's text (OLRC release point 119-138, which includes Pub. L. 119-21). Whole dollars; 2025 law.

* §11(b): 21 percent of taxable income.
* §§531, 535(a), (b)(1), (c)(1)-(2): the accumulated earnings tax.
* §243(a)(1): the 50 percent dividends-received deduction (a corporation owning less than 20 percent of the payer).
* §1367(a) with Reg. §1.1367-1(f) ordering, and §1368(b), (c): S corporation basis and distributions.
* §1374: the built-in gains tax on a former C corporation in its 5-year recognition period.
* §641(c)(2)(A): an electing small business trust's S portion pays the top §1(e) rate (capital gain under §1(h)).
* §1202 as amended by Pub. L. 119-21 §70431: the exclusion (50/75/100 percent at 3/4/5 years for stock acquired after
  4 July 2025; 100 percent after 5 years for stock acquired from 28 Sep 2010 to 4 July 2025), the per-issuer limit
  ((b)(1): the greater of the applicable dollar limit and 10 times the basis of the stock sold in the year; (b)(4):
  $15,000,000 / $10,000,000 less prior use), the §1202(i) basis rule (no less than fair market value of property
  exchanged), the $75,000,000 gross-assets test (§1202(d)(1)), and §1(h)(4), (7): the non-excluded part of eligible
  gain is 28-percent rate gain.
* §302(b)(2), (3) and §318(a)(1): redemptions of a family's stock.
-/

namespace Legal.USTax.Entity
open TaxCode.Individual

/-! ## C corporations -/

/-- §11(b). A loss gives no tax (net operating losses are not carried in the drivers). -/
def corpTax (ti : Int) : Int := max 0 ti * 21 / 100

/-- §535(c)(2): the minimum accumulated earnings credit — $250,000 ($150,000 for the service fields named there)
less accumulated earnings and profits at the close of the preceding year. -/
def aetMinimumCredit (service : Bool) (accumulatedEP : Int) : Int :=
  max 0 ((if service then 150000 else 250000) - accumulatedEP)

/-- §§531, 535: 20 percent of accumulated taxable income: taxable income, plus the dividends-received deduction
(§535(b)(3)), less the federal income tax (§535(b)(1)) and dividends paid (§561), less the accumulated earnings credit.
The credit is the year's retained earnings that are for the reasonable needs of the business (§535(c)(1)) —
`reasonableNeeds` is the business's total need, which earnings and profits already accumulated count against
(Reg. §1.537-2(b)) — or, if more, the minimum credit (§535(c)(2)). Retained earnings for the year are after-tax taxable
income less dividends (the drivers have no other E&P adjustments). -/
def aet (service : Bool) (ti drd dividends reasonableNeeds accumulatedEP : Int) : Int :=
  let afterTax := ti - corpTax ti
  let retained := max 0 (afterTax + drd - dividends)
  let credit := max (min retained (max 0 (reasonableNeeds - accumulatedEP))) (aetMinimumCredit service accumulatedEP)
  max 0 (afterTax + drd - dividends - credit) * 20 / 100

/-! ## S corporations -/

/-- One year's S corporation items for a shareholder, in the §1367 order of Reg. §1.1367-1(f) (after 1996): basis is
increased by income, then reduced by distributions (§1368(d)(1)), then by nondeductible expenses, then by losses,
never below zero; losses beyond basis are suspended (§1366(d)(2)). `pre1997` applies the old order (losses before
distributions), which Reg. §1.1368-3 Example 1 uses. -/
structure SYear where
  income : Int
  losses : Int           -- §1367(a)(2)(B), (C)
  nondeductible : Int    -- §1367(a)(2)(D)
  distribution : Int
  deriving Repr, Inhabited

structure SResult where
  taxFree : Int
  gain : Int             -- §1368(b)(2)
  dividend : Int         -- §1368(c)(2)
  basisAfter : Int
  suspended : Int
  aaaAfter : Int
  deriving Repr, Inhabited, DecidableEq

/-- §1368(b), (c) for one shareholder of a corporation with accumulated adjustments account `aaa` and accumulated
earnings and profits `ep` (from C years). -/
def sYear (pre1997 : Bool) (basis aaa ep : Int) (y : SYear) : SResult :=
  let b1 := basis + y.income
  let aaa1 := aaa + y.income
  if pre1997 then
    let b2 := max 0 (b1 - y.nondeductible)
    let lossAllowed := min y.losses b2
    let b3 := b2 - lossAllowed
    let viaAaa := min y.distribution (max 0 (aaa1 - y.losses))
    let free1 := min viaAaa b3
    let div := min (y.distribution - viaAaa) ep
    let rest := y.distribution - viaAaa - div
    let free2 := min rest (b3 - free1)
    ⟨free1 + free2, (viaAaa - free1) + (rest - free2), div, b3 - free1 - free2, y.losses - lossAllowed,
      aaa1 - y.losses - viaAaa⟩
  else
    -- §1368(c)(1): the part not over AAA is treated under (b); (2) then dividend to E&P; (3) the rest under (b)
    let viaAaa := min y.distribution (max 0 aaa1)
    let free1 := min viaAaa b1
    let div := min (y.distribution - viaAaa) ep
    let rest := y.distribution - viaAaa - div
    let free2 := min rest (b1 - free1)
    let b2 := b1 - free1 - free2
    let b3 := max 0 (b2 - y.nondeductible)
    let lossAllowed := min y.losses b3
    ⟨free1 + free2, (viaAaa - free1) + (rest - free2), div, b3 - lossAllowed, y.losses - lossAllowed,
      aaa1 - viaAaa - y.losses⟩

/-- §1374: in the recognition period (the 5 years from the first S year, (d)(7)(A)) the tax is the highest §11(b)
rate on the net recognized built-in gain: the lesser of the recognized built-in gain and the corporation's taxable
income ((d)(2)(A)), and no more than the net unrealized built-in gain not yet recognized ((c)(2)). The gain recognized
is limited to each asset's built-in gain at the start ((d)(3)(B)); the drivers pass that limit in. -/
def bigTax (yearsSinceElection : Nat) (recognizedBig taxableIncome nubigLeft : Int) : Int :=
  if yearsSinceElection < 5 then corpTax (min (min recognizedBig taxableIncome) nubigLeft) else 0

/-- §641(c)(2)(A): an ESBT's S portion pays 37 percent on ordinary income (the highest §1(e) rate) and §1(h) rates on
net capital gain (20 percent in the drivers, the S portion having no lower brackets); the §199A deduction is allowed
to the ESBT (Reg. §1.641(c)-1(d)(2)(ii)) and is passed in; §1411 at 3.8 percent on what is not active (the trust's
own material participation is not assumed). -/
def esbtTax (ordinary qbiDeduction capGain : Int) (nii : Int) : Int :=
  max 0 (ordinary - qbiDeduction) * 37 / 100 + max 0 capGain * 20 / 100 + max 0 (nii - 15650) * 38 / 1000

/-! ## §1202 -/

/-- The facts of one sale of qualified small business stock by one taxpayer. -/
structure QsbsSale where
  gain : Int                 -- gain on the stock sold this year
  heldYears : Nat           -- whole years held (with §1223 tacking and §1202(h) carryover for gifts and inheritance)
  newStock : Bool := true    -- acquired after 4 July 2025 (§1202(a)(6)(A))
  basisSold : Int            -- §1202(i) basis of the stock sold this year
  priorUsed : Int := 0       -- eligible gain taken into account in earlier years for this issuer ((b)(4))
  separate : Bool := false   -- a married individual filing separately ((b)(3)(A))
  deriving Repr, Inhabited

/-- (excluded, section 1202 gain taxed at 28%, other long-term gain). -/
structure QsbsSplit where
  excluded : Int
  g28 : Int
  ltcg : Int
  eligibleUsed : Int         -- eligible gain taken into account (counts against the (b)(4) limit later)
  deriving Repr, Inhabited, DecidableEq

/-- §1202(a)(1)(B), (a)(5): the applicable percentage for new stock: 50 at 3 years, 75 at 4, 100 at 5 or more.
§1202(a)(1)(A), (a)(4): old stock (acquired after 27 Sep 2010) 100 percent if held more than 5 years. -/
def qsbsPct (newStock : Bool) (held : Nat) : Int :=
  if newStock then (if held ≥ 5 then 100 else if held ≥ 4 then 75 else if held ≥ 3 then 50 else 0)
  else (if held > 5 then 100 else 0)

def qsbsSplit (s : QsbsSale) : QsbsSplit :=
  let pct := qsbsPct s.newStock s.heldYears
  if pct = 0 ∨ s.gain ≤ 0 then ⟨0, 0, max 0 s.gain, 0⟩ else
  let dollar := (if s.newStock then 15000000 else 10000000) / (if s.separate then 2 else 1)
  let limit := max (max 0 (dollar - s.priorUsed)) (10 * s.basisSold)       -- (b)(1)(A), (B)
  let eligible := min s.gain limit
  let excl := eligible * pct / 100
  -- §1(h)(7): section 1202 gain is what would be excluded but for the percentage, less what is excluded
  ⟨excl, eligible - excl, s.gain - eligible, eligible⟩

/-- §1(h)(1) with 28-percent rate gain `g28` (§1(h)(4)): the ordinary-rate amount is the greater of taxable income
less net capital gain and the lesser of the income taxed below 28 percent and taxable income less adjusted net capital
gain ((A)); 28-percent gain above it is taxed at 28 percent ((E)); adjusted net capital gain `ancg` at 0/15/20 as in
the worksheet; and the total never exceeds the ordinary-rate tax on all of it (the opening words of §1(h)(1)).
`below28` is the top of the 24 percent row (§1(j)(2) as made permanent by Pub. L. 119-21). -/
def below28 : Filing → Int
  | .mfj | .qss => 394600
  | .mfs => 197300
  | .hoh => 197300
  | .single => 197300

def taxWith28 (f : Filing) (ti ancg g28 : Int) : Int :=
  if g28 ≤ 0 then C.regularTax f ti ancg else
  let ancg := max 0 (min ancg ti)
  let g28 := max 0 (min g28 (ti - ancg))
  let ordA := max (ti - ancg - g28) (min (below28 f) (ti - ancg))
  let onAncg := C.regularTax f ti ancg - C.line16Tax f (ti - ancg)
  let total := C.line16Tax f ordA + (ti - ancg - ordA) * 28 / 100 + onAncg
  min total (C.line16Tax f ti)

/-! ## §302 and §318 -/

/-- A shareholder: shares owned directly, and the family members (indices) whose stock §318(a)(1) attributes to it
(spouse, children, grandchildren, parents; not siblings, and stock attributed under (a)(1) is not attributed again,
§318(a)(5)(B)). -/
structure Holder where
  shares : Int
  family : List Nat := []
  deriving Repr, Inhabited

def owned (hs : List Holder) (i : Nat) (waiveFamily : Bool := false) : Int :=
  let h := hs.getD i default
  h.shares + (if waiveFamily then 0 else (h.family.map fun j => (hs.getD j default).shares).sum)

def totalShares (hs : List Holder) : Int := (hs.map (·.shares)).sum

def redeem (hs : List Holder) (i : Nat) (n : Int) : List Holder :=
  hs.set i { hs.getD i default with shares := (hs.getD i default).shares - n }

/-- §302(b)(2): after the redemption the shareholder owns (with attribution) less than 50 percent of the voting stock,
and its percentage is less than 80 percent of its percentage before (one class of voting common stock). -/
def substantiallyDisproportionate (hs : List Holder) (i : Nat) (n : Int) : Bool :=
  let before := owned hs i
  let tb := totalShares hs
  let hs' := redeem hs i n
  let after := owned hs' i
  let ta := totalShares hs'
  decide (2 * after < ta) && decide (10 * after * tb < 8 * before * ta)

/-- §302(b)(3) with (c)(2): a complete termination; family attribution is waived when the (c)(2)(A) conditions are
met (no interest other than as a creditor for 10 years, the agreement filed), passed in as `waiver`. -/
def completeTermination (hs : List Holder) (i : Nat) (waiver : Bool) : Bool :=
  let hs' := redeem hs i (hs.getD i default).shares
  decide (owned hs' i waiver = 0)

/-- §302(a), (d): a redemption meeting (b)(2) or (b)(3) is an exchange; otherwise a §301 distribution (a dividend to
the extent of earnings and profits). -/
def redemptionIsExchange (hs : List Holder) (i : Nat) (n : Int) (waiver : Bool) : Bool :=
  substantiallyDisproportionate hs i n || (n = (hs.getD i default).shares && completeTermination hs i waiver)

end Legal.USTax.Entity
