import CaTax.Params

/-!
# Canada (federal) and Ontario personal income tax, CPP/EI and benefits, 2025

One return per adult (Canada has no joint return; spouses interact through the spouse amount, the CCB and other
family benefits, the CWB and LIFT family tests, and the Ontario tax reduction). Amounts in cents.

Order of the federal computation (ITA Part I): income (Division B: wages s. 5, pension s. 56(1)(a), interest s. 12,
dividends s. 82, taxable capital gains s. 38, rent s. 9) → net income (deductions s. 60(e), (e.1), s. 146(5)) →
taxable income (s. 2(2)) → tax s. 117(2) → non-refundable credits s. 118 (BPA, spouse/eligible dependant, age,
pension, s. 118(10) CEA), s. 118.7 (CPP/EI), s. 118.1 (gifts), s. 121 (dividends) → refundable CWB s. 122.7.
Ontario (Taxation Act, 2007): s. 6 tax → s. 9 credits → s. 16 surtax → s. 19.1 dividend credit → s. 20 tax
reduction → s. 21.1 LIFT → s. 24 Ontario Health Premium. Order as in ON428-2025 Part C.
-/

namespace CaTax
open TaxKernel

/-- `x × r` (r in bp) to the cent, half up (the return's rounding to the cent). -/
def pct (r x : Int) : Int := divR .halfUp (r * x) BP

/-! ## CPP and EI (CPP Act ss. 8, 10; EI Act s. 67) -/

structure Social where
  /-- employee base contribution (s. 8(1)): credit under ITA s. 118.7(b) -/
  base : Int
  /-- employee first + second additional (s. 8(1.1), (1.2)): deduction under ITA s. 60(e.1) -/
  enhanced : Int
  /-- self-employed contributions (both shares, CPP Act s. 10) -/
  seTotal : Int
  /-- of which: base, employee-equivalent half (credit s. 118.7(c) = what s. 60(e) leaves) -/
  seCreditPart : Int
  ei : Int
  deriving Repr, Inhabited

def Social.total (s : Social) : Int := s.base + s.enhanced + s.seTotal + s.ei
/-- Deduction in computing income: ITA s. 60(e) (self-employed: all but the employee-equivalent base half) and
s. 60(e.1) (employee enhanced contributions). -/
def Social.deduction (s : Social) : Int := s.enhanced + (s.seTotal - s.seCreditPart)
/-- Amounts carrying the 118.7 credit. -/
def Social.creditBase (s : Social) : Int := s.base + s.seCreditPart + s.ei

/-- Contributions of a person aged 18 to 69 (CPP Act s. 12: contributory period; contributions stop at 70 and
do not start before 18) with wages `w` and self-employed earnings `se` (cents). Wages fill the earnings ceilings
first; self-employed earnings above them pay both shares (s. 10). -/
def social (age : Nat) (w se : Int) (y : YP := y2025) : Social :=
  let w := pos w
  let se := pos se
  let cppOn := 18 ≤ age ∧ age < 70
  let baseE (x : Int) : Int := pos (min x y.cppYmpe - cppYbe)
  let cpp2E (x : Int) : Int := pos (min x y.cppYampe - y.cppYmpe)
  let bW := baseE w
  let bAll := baseE (w + se)
  let c2W := cpp2E w
  let c2All := cpp2E (w + se)
  let base := if cppOn then pct cppBaseRate bW else 0
  let enh := if cppOn then pct y.cppFirstAddRate bW + pct y.cpp2Rate c2W else 0
  let seBaseHalf := if cppOn then pct cppBaseRate (bAll - bW) else 0
  let seEnhHalf := if cppOn then pct y.cppFirstAddRate (bAll - bW) + pct y.cpp2Rate (c2All - c2W) else 0
  { base, enhanced := enh, seTotal := 2 * (seBaseHalf + seEnhHalf), seCreditPart := seBaseHalf,
    ei := pct y.eiRate (min w y.eiMie) }

/-! ## One person's income -/

/-- What one adult has (cents). Dividends are eligible dividends from listed Canadian shares (contract). -/
structure Person where
  age : Nat
  wages : Int
  se : Int
  pension : Int
  interest : Int
  dividends : Int
  capitalGains : Int
  rent : Int
  rrsp : Int
  deriving Repr, Inhabited

structure Income where
  social : Social
  grossUp : Int
  taxableGains : Int
  total : Int
  rrspDeducted : Int
  net : Int
  taxable : Int
  deriving Repr, Inhabited

def Person.employment (p : Person) : Int := pos p.wages

def income (p : Person) (y : YP := y2025) : Income :=
  let s := social p.age p.wages p.se y
  let gu := pct eligibleGrossUp (pos p.dividends)
  let tg := divR .down (cgInclusionNum * pos p.capitalGains) cgInclusionDen
  let total := pos p.wages + p.se + pos p.pension + pos p.interest + pos p.dividends + gu + tg + p.rent
  let earned := pos p.wages + p.se + p.rent
  let rrspLim := min rrspDollarLimit (pct rrspPct (pos earned))
  let rr := min (pos p.rrsp) rrspLim
  let net := pos (total - s.deduction - rr)
  { social := s, grossUp := gu, taxableGains := tg, total, rrspDeducted := rr, net, taxable := net }

/-! ## Federal tax (ITA Division E) -/

/-- ITA s. 118(1.1): basic personal amount; the enhancement is withdrawn in proportion to income between the
first dollar amounts of s. 117(2)(d) and (e) (kernel `Taper`; withdrawal rounded down to the cent, so the amount
is never below the statute's). -/
def bpaTaper : Taper :=
  { full := bpaMax, start := bpaTaperStart, num := bpaMax - bpaMin, den := bpaTaperEnd - bpaTaperStart,
    floor := bpaMin, round := .down }
def bpa (netIncome : Int) : Int := bpaTaper.amount netIncome

/-- ITA s. 118(2): age amount, withdrawn at 15 % above the threshold (kernel `Taper`). -/
def ageTaper : Taper := { full := ageAmount, start := ageThreshold, num := 15, den := 100, round := .down }

/-- The year's basic personal amount, age amount (federal and Ontario) as kernel `Taper`s (the 2025 ones above are
`bpaTaper`, `ageTaper`, `onAgeTaper`, about which `Theorems` proves the bounds). -/
def bpaTaperY (y : YP) : Taper :=
  { full := y.bpaMax, start := y.bpaTaperStart, num := y.bpaMax - y.bpaMin, den := y.bpaTaperEnd - y.bpaTaperStart,
    floor := y.bpaMin, round := .down }
def bpaY (y : YP) (netIncome : Int) : Int := (bpaTaperY y).amount netIncome
def ageTaperY (y : YP) : Taper := { full := y.ageAmount, start := y.ageThreshold, num := 15, den := 100, round := .down }

structure Family where
  /-- the other spouse's net income, if married -/
  spouseNet : Option Int
  /-- the person claims the eligible dependant amount (single parent, child under 18) -/
  eligibleDependant : Bool
  /-- children under 18 for whom this person claims the Ontario tax reduction (higher-income spouse) -/
  onDependants : Nat
  /-- family adjusted income for LIFT (own net income if single) -/
  familyNet : Int
  /-- gifts claimed on this return -/
  gifts : Int
  deriving Repr, Inhabited

structure FedResult where
  basicTax : Int
  bpa : Int
  spouseAmount : Int
  ageAmount : Int
  cea : Int
  pensionAmount : Int
  cppEiBase : Int
  creditAmounts : Int
  nrtc : Int
  giftCredit : Int
  dtc : Int
  tax : Int
  deriving Repr, Inhabited

def fedGiftCredit (gifts taxable : Int) (y : YP := y2025) : Int :=
  let g := pos gifts
  let low := min g giftLowTier
  let top := min (pos (g - giftLowTier)) (pos (taxable - y.topThreshold))
  let mid := pos (g - giftLowTier - top)
  pct y.lowRate low + pct giftTopRate top + pct giftMidRate mid

def fedTax (p : Person) (inc : Income) (f : Family) (y : YP := y2025) : FedResult :=
  let basic := y.fedSchedule.tax { mode := .halfUp } inc.taxable
  let b := bpaY y inc.net
  -- s. 118(1)(a)(ii) / (b)(iv): C.01 − C.1 (s. 257: a negative result is nil)
  let sp := match f.spouseNet with
    | some sn => pos (b - sn)
    | none => if f.eligibleDependant then b else 0
  let age := if 65 ≤ p.age then (ageTaperY y).amount inc.net else 0
  let cea := min y.ceaMax p.employment
  let pen := min pensionAmountMax (pos p.pension)
  let cppEi := inc.social.creditBase
  let amounts := b + sp + age + cea + pen + cppEi
  let nrtc := pct y.lowRate amounts
  let gc := fedGiftCredit f.gifts inc.taxable y
  let dtc := divR .halfUp (fedDtcNum * inc.grossUp) fedDtcDen
  let tax := pos (pos (basic - nrtc - gc) - dtc)
  { basicTax := basic, bpa := b, spouseAmount := sp, ageAmount := age, cea, pensionAmount := pen,
    cppEiBase := cppEi, creditAmounts := amounts, nrtc, giftCredit := gc, dtc, tax }

/-! ## Ontario tax (Taxation Act, 2007, Part II Division B; Division C) -/

structure OnResult where
  basicTax : Int
  nrtc : Int
  afterCredits : Int
  surtax : Int
  dtc : Int
  beforeReduction : Int
  reduction : Int
  lift : Int
  tax : Int
  ohp : Int
  deriving Repr, Inhabited

def onAgeTaper : Taper := { full := onAgeAmount, start := onAgeThreshold, num := 15, den := 100, round := .down }

def onAgeTaperY (y : YP) : Taper :=
  { full := y.onAgeAmount, start := y.onAgeThreshold, num := 15, den := 100, round := .down }

def onTax (p : Person) (inc : Income) (f : Family) (y : YP := y2025) : OnResult :=
  let basic := y.onSchedule.tax { mode := .halfUp } inc.taxable
  -- s. 9(3), (4): A × [$10,823 − (B − $1,082)], B ≥ $1,082
  let sp := match f.spouseNet with
    | some sn => pos (y.onSpouseMax - (max y.onSpouseFloor sn - y.onSpouseFloor))
    | none => if f.eligibleDependant then y.onSpouseMax else 0
  let age := if 65 ≤ p.age then (onAgeTaperY y).amount inc.net else 0
  let pen := min y.onPensionMax (pos p.pension)
  let amounts := y.onBpa + sp + age + pen + inc.social.creditBase
  let g := pos f.gifts
  let gift := pct onLowRate (min g giftLowTier) + pct onGiftHighRate (pos (g - giftLowTier))
  let nrtc := pct onLowRate amounts + gift
  let t53 := pos (basic - nrtc)
  -- s. 16(1): surtax on the gross tax amount (no split income or subdivision d credits here)
  let surtax := pct onSurtaxR1 (pos (t53 - y.onSurtaxT1)) + pct onSurtaxR2 (pos (t53 - y.onSurtaxT2))
  -- s. 19.1(b): 36.3158 % of the s. 82(1)(b)(ii) gross-up
  let dtc := divR .halfUp (onDtcPpm * inc.grossUp) 1000000
  let t73 := pos (t53 + surtax - dtc)
  -- s. 20(1): twice the personal amount less tax otherwise payable
  let pa := y.onReductionBasic + y.onReductionPerDependant * (f.onDependants : Int)
  let red := min t73 (pos (2 * pa - t73))
  let t81 := t73 - red
  -- s. 21.1(3.1): LIFT
  let d := min liftMax (pct onLowRate p.employment)
  let e := pct liftRate (max (pos (inc.net - liftPersonal)) (pos (f.familyNet - liftFamily)))
  let lift := min t81 (pos (d - e))
  { basicTax := basic, nrtc, afterCredits := t53, surtax, dtc, beforeReduction := t73, reduction := red, lift,
    tax := t81 - lift, ohp := ohp inc.taxable }

end CaTax
