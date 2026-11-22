import ChTax.Years

/-!
# The assessment: DBG (federal) and StG ZH (canton, City of Zürich, church), one return at a time

A return (`Ret`) is one tax subject: a single person, or a married couple (DBG Art. 9 Abs. 1: "Das Einkommen der
Ehegatten ... wird ohne Rücksicht auf den Güterstand zusammengerechnet"; StG ZH § 7 the same). Unmarried partners
file two returns (no splitting, no joint assessment: concubinage). Income amounts are francs; every deduction and
tax is carried in Rappen (Rp = 1/100 franc) until the taxable income is rounded down to a 100-franc step.
-/

namespace ChTax
open TaxKernel

/-- One person's earnings side on a return. Contributions in Rappen (AHV/IV/EO, ALV, NBU) or francs (BVG). -/
structure Person where
  age : Nat := 40
  wage : Int := 0
  self : Int := 0
  pension : Int := 0
  ahvRp : Int := 0          -- AHV/IV/EO on wages and self-employment (DBG Art. 33 Abs. 1 lit. d/f)
  alvRp : Int := 0          -- ALV (lit. f)
  nbuRp : Int := 0          -- non-occupational accident insurance, if paid by the employee (lit. f)
  bvgRp : Int := 0          -- employee's ordinary pension-fund contribution, Rappen (lit. d)
  buyIn : Int := 0          -- pension-fund buy-in (Einkauf, lit. d)
  p3a : Int := 0            -- Säule 3a (lit. e), already capped
  deriving Repr, Inhabited

/-- A return. `kidHalves`: child deductions in half units (a whole child = 2; separated / unmarried parents with
joint custody each get half, DBG Art. 35 Abs. 1 lit. a, StG ZH § 34 Abs. 1 lit. a). -/
structure Ret where
  persons : List Person
  married : Bool := false
  parent : Bool := false     -- Elterntarif / Verheiratetentarif for a single parent (DBG Art. 36 Abs. 2bis, § 35 Abs. 2)
  kidHalves : Nat := 0
  kidCredits : Nat := 0      -- DBG Art. 36 Abs. 2bis: 263 per child on this return
  interest : Int := 0
  dividends : Int := 0
  qualifying : Bool := false -- dividends from a participation of at least 10 %
  rental : Int := 0
  /-- tax year (round 6) -/
  yr : Nat := 2025
  famAllow : Int := 0        -- family allowances received (taxable as wage, DBG Art. 17 Abs. 1 "Zulagen")
  charitable : Int := 0
  deriving Repr, Inhabited

/-- What differs between the two income taxes. -/
structure Layer where
  insMarried : Int
  insOther : Int
  insPerKid : Int
  kidDed : Int
  marriedDed : Int
  qualDivBp : Int
  /-- the two-earner deduction given the lower earned income (Rp) -/
  twoEarner : Int → Int

/-- DBG Art. 33 Abs. 2: 50 % of the lower earned income, at least 8 600 and at most 14 100; the minimum cannot
exceed the income itself (ESTV practice; the statute's text alone would give 8 600 on 1 franc, see FINDINGS). -/
def fedTwoEarnerRp (lowRp : Int) : Int :=
  min (pos lowRp) (clamp (100 * fedTwoEarnerMin) (100 * fedTwoEarnerMax) (lowRp / 2))

/-- The same for a year's amounts (round 6). -/
def fedTwoEarnerRpY (F : FedYear) (lowRp : Int) : Int :=
  min (pos lowRp) (clamp (100 * F.twoMin) (100 * F.twoMax) (lowRp / 2))

/-- StG ZH § 31 Abs. 2: a flat 6 100, at most the income it is deducted from. -/
def zhTwoEarnerRp (lowRp : Int) : Int := min (pos lowRp) (100 * zhTwoEarner)

def fedLayer : Layer :=
  { insMarried := fedInsMarried, insOther := fedInsOther, insPerKid := fedInsPerKid, kidDed := fedKidDeduction,
    marriedDed := fedMarriedDeduction, qualDivBp := fedQualDivBp, twoEarner := fedTwoEarnerRp }
def fedLayerY (F : FedYear) : Layer :=
  { insMarried := F.insMarried, insOther := F.insOther, insPerKid := F.insPerKid, kidDed := F.kidDed,
    marriedDed := F.marriedDed, qualDivBp := fedQualDivBp, twoEarner := fedTwoEarnerRpY F }
def zhLayerY (F : FedYear) : Layer :=
  { insMarried := F.zhInsMarried, insOther := F.zhInsOther, insPerKid := F.zhInsPerKid, kidDed := F.zhKid,
    marriedDed := 0, qualDivBp := zhQualDivBp, twoEarner := fun lowRp => min (pos lowRp) (100 * F.zhTwo) }
def zhLayer : Layer :=
  { insMarried := zhInsMarried, insOther := zhInsOther, insPerKid := zhInsPerKid, kidDed := zhKidDeduction,
    marriedDed := 0, qualDivBp := zhQualDivBp, twoEarner := zhTwoEarnerRp }

/-- Conventions the statute leaves open or that a referee uses. -/
structure Conv where
  /-- Berufskosten on the wage net of AHV/ALV only (the OECD), instead of the Lohnausweis net wage (after BVG) -/
  berufBeforeBvg : Bool := false
  /-- the insurance increase "ohne Beiträge nach lit. d und e" read literally (AHV contributions count) -/
  insLiteral : Bool := false
  deriving Repr, Inhabited

/-- Net wage (Lohnausweis Ziffer 11): gross minus AHV/IV/EO, ALV, NBU and BVG. The AHV share of a person's wage
is pro rata when they also have self-employment. -/
def netWageRp (cv : Conv) (p : Person) : Int :=
  let earn := p.wage + p.self
  let ahvW := if earn ≤ 0 then 0 else p.ahvRp * p.wage / earn
  100 * p.wage - ahvW - p.alvRp - p.nbuRp - (if cv.berufBeforeBvg then 0 else p.bvgRp)

/-- DBG Art. 26 Abs. 1 lit. c / Abs. 2 and Berufskostenverordnung Anhang: 3 % of the net wage, 2 000 to 4 000;
never more than the net wage. StG ZH § 26 the same (Zürich applies the federal flat rates). -/
def berufRp (cv : Conv) (p : Person) : Int :=
  if p.wage ≤ 0 then 0 else
  let nw := pos (netWageRp cv p)
  min nw (clamp (100 * berufMin) (100 * berufMax) (nw * berufBp / BP))

/-- DBG Art. 33 Abs. 1 lit. d, e, f (StG ZH § 31 Abs. 1 lit. d, e, f): AHV/IV/EO, BVG (incl. buy-ins), Säule 3a,
ALV, NBU. -/
def contribRp (p : Person) : Int := p.ahvRp + p.alvRp + p.nbuRp + p.bvgRp + 100 * (p.buyIn + p.p3a)

/-- DBG Art. 33 Abs. 2 second sentence: earned income "abzüglich der Aufwendungen nach den Artikeln 26–31 und der
allgemeinen Abzüge nach Absatz 1 Buchstaben d–f". -/
def earnedRp (cv : Conv) (p : Person) : Int := 100 * (p.wage + p.self) - berufRp cv p - contribRp p

/-- Gross income of the return in Rp (DBG Art. 16-23): earnings, pensions (Art. 22), interest and dividends (Art. 20;
qualifying dividends partly, Abs. 1bis), rents (Art. 21), family allowances (Art. 17). Private capital gains are
tax-free (Art. 16 Abs. 3). -/
def incomeRp (L : Layer) (r : Ret) : Int :=
  sumInts (r.persons.map fun p => 100 * (p.wage + p.self + p.pension))
  + 100 * (r.interest + r.rental + r.famAllow)
  + (if r.qualifying then r.dividends * L.qualDivBp / 100 else 100 * r.dividends)

/-- DBG Art. 33 Abs. 1 lit. g + Abs. 1bis (StG ZH § 31 Abs. 1 lit. g): the flat cap for insurance premiums and
savings interest (premiums assumed at least the cap: compulsory health insurance), raised by half "für
Steuerpflichtige ohne Beiträge nach Absatz 1 Buchstaben d und e" and by a per-child amount. -/
def insRp (cv : Conv) (L : Layer) (r : Ret) : Int :=
  let base := if r.married then L.insMarried else L.insOther
  let noDE := r.persons.all fun p =>
    decide (p.bvgRp = 0) && decide (p.buyIn = 0) && decide (p.p3a = 0) && (!cv.insLiteral || decide (p.ahvRp = 0))
  let base := if noDE then base + base / 2 else base
  100 * base + 100 * L.insPerKid * r.kidHalves / 2

/-- The two-earner deduction: only for a married couple who both have earned income. -/
def twoEarnerRp (cv : Conv) (L : Layer) (r : Ret) : Int :=
  match r.persons with
  | [a, b] =>
    if r.married && (a.wage + a.self > 0) && (b.wage + b.self > 0) then
      L.twoEarner (min (earnedRp cv a) (earnedRp cv b)) else 0
  | _ => 0

/-- Net income before donations and social deductions: income minus Art. 26-33 (§§ 26-31). -/
def netBeforeGiftsRp (cv : Conv) (L : Layer) (r : Ret) : Int :=
  incomeRp L r - sumInts (r.persons.map (berufRp cv)) - sumInts (r.persons.map contribRp) - insRp cv L r
    - twoEarnerRp cv L r

/-- DBG Art. 33a (StG ZH § 32 lit. b): gifts deductible "wenn diese Leistungen im Steuerjahr 100 Franken erreichen
und insgesamt 20 Prozent der um die Aufwendungen (Art. 26–33) verminderten Einkünfte nicht übersteigen". -/
def giftsRp (cv : Conv) (L : Layer) (r : Ret) : Int :=
  if r.charitable < 100 then 0 else min (100 * r.charitable) (pos (netBeforeGiftsRp cv L r) / 5)

/-- DBG Art. 35 (StG ZH § 34): Sozialabzüge. -/
def socialDedRp (L : Layer) (r : Ret) : Int :=
  100 * L.kidDed * r.kidHalves / 2 + (if r.married then 100 * L.marriedDed else 0)

/-- Taxable income in francs, rounded down to the 100-franc step of the tariffs. -/
def taxable (cv : Conv) (L : Layer) (r : Ret) : Int :=
  let t := pos (netBeforeGiftsRp cv L r - giftsRp cv L r - socialDedRp L r) / 100
  t / 100 * 100

/-! ## Federal tax (DBG Art. 36) -/

/-- The tariff as printed: the last row at or below `x`, its amount, plus its per-100 increment for each further
complete 100 francs ("für je weitere 100 Franken Einkommen ... mehr"). Rappen. -/
def tariffRp (rows : List TRow) (x : Int) : Int :=
  match (rows.reverse.find? fun r => decide (r.lo ≤ x)) with
  | some r => r.baseRp + (x - r.lo) / 100 * r.per100Rp
  | none => 0

def fedRows (r : Ret) : List TRow := if r.married || r.parent then (fedFor r.yr).married else (fedFor r.yr).single
def fedSched (r : Ret) : Schedule :=
  if r.married || r.parent then (fedFor r.yr).marriedSched else (fedFor r.yr).singleSched

/-- Tax before the child reduction (Rp), statute as printed or (`bandsum`) the band sum. -/
def fedBeforeCreditRp (bandsum : Bool) (r : Ret) (ti : Int) : Int :=
  if bandsum then (fedSched r).ticks (ti / 100 * 100) / 100 else tariffRp (fedRows r) ti

/-- DBG Art. 36 Abs. 2bis second sentence (263 per child, not refundable) and Abs. 3 ("Steuerbeträge unter 25
Franken werden nicht erhoben"). -/
def fedFinalRp (beforeRp : Int) (kids : Nat) (creditRp : Int := fedChildCreditRp) : Int :=
  let t := pos (beforeRp - creditRp * kids)
  if t < fedMinTaxRp then 0 else t

/-- DBG Art. 38: capital benefits from pensions, a separate full annual tax at one fifth of the Art. 36 tariff
(Abs. 1, 2 and 2bis first sentence: no child reduction), no social deductions. -/
def fedCapitalRp (married : Bool) (amount : Int) (yr : Nat := 2025) : Int :=
  if amount ≤ 0 then 0 else
  tariffRp (if married then (fedFor yr).married else (fedFor yr).single) (amount / 100 * 100) / fedCapitalDivisor

/-! ## Canton and City of Zürich (StG ZH § 35, Steuerfüsse) -/

def zhSched (r : Ret) : Schedule := if r.married || r.parent then (fedFor r.yr).zhMarried else (fedFor r.yr).zhSingle

/-- Einfache Staatssteuer (Rp) on a taxable income. -/
def zhSimpleRp (r : Ret) (ti : Int) : Int := (zhSched r).ticks ti / 100

/-- StG ZH § 37: capital benefits taxed separately at the rate for one twentieth, simple tax at least 2 %. -/
def zhCapitalSimpleRp (married : Bool) (amount : Int) (yr : Nat := 2025) : Int :=
  if amount ≤ 0 then 0 else
  let a := amount / 100 * 100
  let s := if married then (fedFor yr).zhMarried else (fedFor yr).zhSingle
  let twentieth := a / zhCapitalDivisor
  let rateTicks := if twentieth ≤ 0 then 0 else s.ticks twentieth * a / twentieth
  max rateTicks (zhCapitalMinBp * a) / 100

/-- A multiplier on the simple tax, in Rappen. -/
def multRp (m : Multiplier) (simpleRp : Int) : Int := m.rate * simpleRp / BP

end ChTax
