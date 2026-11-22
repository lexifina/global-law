import NOTax.Params

/-!
# NOTax.Person: one taxpayer's 2025 assessment

Norway taxes each spouse separately (sktl. § 2-11 (1): "Ektefeller skattlegges særskilt for inntekt"). The tax is
built from two bases:

* **personinntekt** (sktl. § 12-2): wages, pensions and business income, gross. It carries the progressive
  trinnskatt (SV 2025 § 3-1) and the trygdeavgift (ftrl. § 23-3).
* **alminnelig inntekt** (net income: all income less all deductions, sktl. § 5-1 and ch. 6), less the
  personfradrag (§ 15-4), taxed flat at 22 % (municipal 12.75 + county 2.65 + fellesskatt 6.6).

Kernel parts: `Schedule` (trinnskatt, the three flat taxes, the pension-credit taper), `Rounding` (`Rule.unitDown`,
skattebetalingsforskriften § 10-4-4), `Allowance` (`cappedDeduction` for the minstefradrag, `taxableAfter` for the
personfradrag), `Credit` (`usedCredit`). Local (kernel gaps): the trygdeavgift phase-in cap (a contribution never
above 25 % of income over the floor), the two-step pension-credit taper, the § 17-1 low-income limit.
-/

namespace NOTax
open TaxKernel

/-- One taxpayer's inputs (whole kroner; this person's share of household capital income). -/
structure PersonIn where
  age : Nat := 40
  wages : Int := 0
  pension : Int := 0
  /-- business income of an enkeltpersonforetak (no business capital: no skjermingsfradrag, § 12-12) -/
  business : Int := 0
  interest : Int := 0
  dividends : Int := 0
  /-- skjermingsfradrag available against the dividends (§ 10-12) -/
  skjerming : Int := 0
  gains : Int := 0
  rental : Int := 0
  debtInterest : Int := 0
  ips : Int := 0
  gifts : Int := 0
  /-- foreldrefradrag claimed by this person (already within the household cap) -/
  foreldre : Int := 0
  bsu : Int := 0
  netWealth : Int := 0
  /-- receives alderspensjon/AFP (sktl. § 16-1 (1) a-b) -/
  alderspensjon : Bool := false
  /-- married or registered cohabitant (§ 17-1 limit "for hver ektefelle") -/
  spouse : Bool := false
  deriving Repr, Inhabited

/-! ## Bases -/

/-- sktl. § 12-2: personinntekt = wages (a), pensions (b) and calculated business income (g); never negative. -/
def personinntekt (p : PersonIn) : Int := pos p.wages + pos p.pension + pos p.business

/-- sktl. § 6-32 (1): 46 % of wages up to 92 000, 40 % of pensions up to 73 150, "Summen av minstefradrag skal
ikke overstige øvre grense for minstefradrag i lønnsinntekt". Whole kroner, rounded down (no rule is stated). -/
def minstefradrag (wages pension : Int) : Int :=
  min minstWageMax (cappedDeduction wages minstWageMax minstWageRate wages
    + cappedDeduction pension minstPensionMax minstPensionRate pension)

/-- sktl. § 10-11 (1), § 10-31 (1)-(2): the owner income after skjerming, "oppjusteres med 1,72"
(a loss likewise; rounded towards zero to the krone). -/
def oppjuster (x : Int) : Int := if 0 ≤ x then oppNum * x / oppDen else -(oppNum * (-x) / oppDen)

/-- The dividend after skjerming (§ 10-12 (1): "Fradraget kan ikke overstige aksjonærens utbytte"). -/
def dividendNet (p : PersonIn) : Int := pos (p.dividends - min (pos p.skjerming) (pos p.dividends))

/-- sktl. § 6-47 (1) c-d: IPS deduction, at most 15 000 (2025). -/
def ipsDeduction (p : PersonIn) : Int := min (pos p.ips) ipsMax

/-- sktl. § 6-50 (5): gifts of at least 500, at most 25 000. -/
def giftDeduction (p : PersonIn) : Int := if p.gifts < giftMin then 0 else min p.gifts giftMax

/-- Alminnelig inntekt before the oppjustering of owner income (sktl. § 17-1 (6) uses this measure). -/
def alminneligBeforeOpp (p : PersonIn) : Int :=
  p.wages + p.pension + p.business + p.interest + dividendNet p + p.gains + p.rental
    - minstefradrag p.wages p.pension - pos p.debtInterest - ipsDeduction p - giftDeduction p - pos p.foreldre

/-- The oppjustering itself (the 0.72 added on top of dividends and gains). -/
def oppTillegg (p : PersonIn) : Int := oppjuster (dividendNet p) - dividendNet p + (oppjuster p.gains - p.gains)

/-- Alminnelig inntekt (sktl. § 5-1, ch. 6, § 10-11, § 10-31). -/
def alminnelig (p : PersonIn) : Int := alminneligBeforeOpp p + oppTillegg p

/-- The base of the three flat taxes: alminnelig inntekt less the personfradrag (§ 15-4), never negative. -/
def grunnlag (p : PersonIn) : Int := taxableAfter personfradrag (alminnelig p)

/-! ## Taxes -/

def flatTax (rate base : Int) : Int := (Schedule.flat rate).tax Rule.unitDown base

def kommuneskatt (p : PersonIn) : Int := flatTax kommuneRate (grunnlag p)
def fylkesskatt (p : PersonIn) : Int := flatTax fylkeRate (grunnlag p)
def fellesskatt (p : PersonIn) : Int := flatTax fellesRate (grunnlag p)
def trinnskattOf (p : PersonIn) : Int := trinnskatt.tax Rule.unitDown (personinntekt p)

/-- ftrl. § 23-3 (2) nr. 1 c: "personinntekt for personer under 17 år eller over 69 år" pays the low rate. -/
def lowRateAge (age : Nat) : Bool := age < 17 || age > 69

/-- Trygdeavgift at the rates of TA 2025, before the phase-in cap (ticks). -/
def taRateTicks (p : PersonIn) : Int :=
  if lowRateAge p.age then taLow * personinntekt p
  else taMid * pos p.wages + taLow * pos p.pension + taHigh * pos p.business

/-- The phase-in cap of ftrl. § 23-3 (4) for personinntekt `pi` (ticks): 25 % of the excess over 99 650. -/
def taCapTicks (pi : Int) : Int := taCapRate * pos (pi - taFloor)

/-- Trygdeavgift (ticks): the rates, never more than the cap; nothing up to the floor. -/
def taTicks (p : PersonIn) : Int :=
  if personinntekt p ≤ taFloor then 0 else min (taRateTicks p) (taCapTicks (personinntekt p))

def trygdeavgift (p : PersonIn) : Int := Rule.unitDown.ofTicks (taTicks p)

/-- The listed taxes before credits: municipal, county, fellesskatt, trinnskatt, trygdeavgift. -/
def ordinaryTax (p : PersonIn) : Int :=
  kommuneskatt p + fylkesskatt p + fellesskatt p + trinnskattOf p + trygdeavgift p

/-! ## Credits and the low-income limit -/

/-- sktl. § 16-1: 36 000, tapered by 16.7 % of pension above 276 400 and 6 % above 422 950 (2025); limited to the
income taxes and trygdeavgift (§ 16-1 (6)). -/
def pensionCreditGross (p : PersonIn) : Int :=
  if p.alderspensjon then pos (pensionCreditFull - Rule.unitDown.ofTicks (pensionCreditTaper.ticks (pos p.pension)))
  else 0

def pensionCredit (p : PersonIn) : Int := usedCredit (ordinaryTax p) (pensionCreditGross p)

/-- sktl. § 17-1 (1)-(3), (6): the income measure (no oppjustering, plus 1.5 % of net wealth above the free
amount) and the limit. -/
def sbIncome (p : PersonIn) : Int :=
  alminneligBeforeOpp p
    + sbWealthRate * pos (p.netWealth - (if p.spouse then sbWealthFreeSpouse else sbWealthFreeSingle)) / BP
def sbLimit (p : PersonIn) : Int := if p.spouse then sbSpouse else sbSingle

/-- The taxes § 17-1 (2) limits (trinnskatt only at the two lowest rates). -/
def sbListed (p : PersonIn) : Int :=
  kommuneskatt p + fylkesskatt p + fellesskatt p + trinnskattLow2.tax Rule.unitDown (personinntekt p)
    + trygdeavgift p

/-- Tax under § 17-1 for a pension recipient: nothing up to the limit; above it the listed taxes are at most 55 %
of the excess, the rest of the trinnskatt is due in full. -/
def sbTax (p : PersonIn) : Int :=
  if sbIncome p ≤ sbLimit p then 0
  else min (sbListed p) (Rule.unitDown.ofTicks (sbRate * (sbIncome p - sbLimit p))) + (ordinaryTax p - sbListed p)

def sbApplies (p : PersonIn) : Bool := decide (0 < p.pension)

/-- Tax after § 16-1 and § 17-1 ("får skatten fastsatt etter den bestemmelsen som gir lavest skatt", § 16-1 (4)). -/
def taxAfterPensionRules (p : PersonIn) : Int :=
  let viaCredit := ordinaryTax p - pensionCredit p
  if sbApplies p then min viaCredit (sbTax p) else viaCredit

/-- sktl. § 16-10: BSU credit, 10 % of up to 27 500 saved, through the year of turning 33, limited to the taxes
("ikke med høyere beløp enn summen av fastsatte inntektsskatter og trygdeavgift"). -/
def bsuCreditGross (p : PersonIn) : Int :=
  if p.age ≤ bsuLastAge then bsuRate * min (pos p.bsu) bsuMax / BP else 0

def bsuCredit (p : PersonIn) : Int := usedCredit (taxAfterPensionRules p) (bsuCreditGross p)

/-- Total tax and trygdeavgift of the person. -/
def totalTax (p : PersonIn) : Int := taxAfterPensionRules p - bsuCredit p

/-- The reduction of the ordinary taxes by credits and § 17-1, booked against central tax first, then local
tax, then trygdeavgift (the statute grants it "i inntektsskatt og trygdeavgift" without an order). -/
def reduction (p : PersonIn) : Int := ordinaryTax p - totalTax p

structure Lines where
  central : Int
  local_ : Int
  social : Int
  deriving Repr

def lines (p : PersonIn) : Lines :=
  let c0 := fellesskatt p + trinnskattOf p
  let l0 := kommuneskatt p + fylkesskatt p
  let s0 := trygdeavgift p
  let r := reduction p
  let rc := min r c0
  let rl := min (r - rc) l0
  let rs := r - rc - rl
  { central := c0 - rc, local_ := l0 - rl, social := s0 - rs }

/-- OECD Taxing Wages convention (`notax --oecd`, round 1, 2026-11-19): the OECD's Norwegian lines are the taxes
before any rounding (S100 2025: SLT 92 576,33 = 15,40 % × 601 145; CGITFP 71 149,28). The statute rounds each
assessed tax down to the krone (`Rule.unitDown`, kept as the default); this convention computes each line from
the unrounded ticks and rounds the line once, half up. Credits and § 17-1 are those of the statute model. -/
def linesOecd (p : PersonIn) : Lines :=
  let g := grunnlag p
  let c0 := Rule.unitHalfUp.ofTicks ((Schedule.flat fellesRate).ticks g + trinnskatt.ticks (personinntekt p))
  let l0 := Rule.unitHalfUp.ofTicks ((Schedule.flat kommuneRate).ticks g + (Schedule.flat fylkeRate).ticks g)
  let s0 := Rule.unitHalfUp.ofTicks (taTicks p)
  let r := reduction p
  let rc := min r c0
  let rl := min (r - rc) l0
  let rs := r - rc - rl
  { central := c0 - rc, local_ := l0 - rl, social := s0 - rs }

end NOTax
