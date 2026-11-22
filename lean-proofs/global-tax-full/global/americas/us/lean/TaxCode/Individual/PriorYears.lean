import TaxCode.Individual.Form1040

/-!
# Tax years 2022, 2023 and 2024 (harness copy only; round 3 of the 38-model tests)

The Form 1040 model in this folder is the 2025 return (as amended by Pub. L. 119-21). This module adds the **tax
year as a parameter** for the earlier years, for the returns the comparison harness builds most often: **wages
only** (single, head of household, married filing jointly; dependants), the standard deduction, the regular tax (Tax
Table under $100,000, the §1(j) schedule above), the child tax credit and credit for other dependents (§24 as in
force for 2018-2025 before Pub. L. 119-21: $2,000 per child, refundable part indexed), the earned income credit
(§32, Pub. 596 table rule), employee FICA (§3101, the year's contribution and benefit base) and the additional
Medicare tax (§3101(b)(2), unindexed). Pub. L. 119-21 changes (the $2,200 credit, the senior, tips, overtime and
car-loan deductions, the 2025 standard deduction) apply from 2025 only and are not used here.

Round 4 adds, from the same Rev. Procs (§2.03 maximum zero-rate and 15-percent-rate amounts, §3.15(3) aged
amounts) and IRS Notices 2021-61, 2022-55, 2023-75 (§219(b)(5)(A) "$6,000", "$6,500", "$7,000"): interest,
dividends and capital gains (Qualified Dividends and Capital Gain Tax Worksheet), pensions and rents as ordinary
income, the §63(f) aged amounts, cash gifts itemized under §170(b)(1)(A)/(G) (60 % of AGI), the §219 IRA deduction
(not an active participant, as the adapter assumes) and the §1411 net investment income tax (unindexed thresholds).
Round 5 adds self-employment (§§1401-1402 with the year's contribution and benefit base, the §164(f) deduction,
the §199A deduction with the Rev. Proc. §3.27 threshold amounts $170,050 / $340,100, $182,100 / $364,200,
$191,950 / $383,900 and phase-in ranges $50,000 / $100,000, for a non-SSTB business with no W-2 wages or UBIA, as the
adapter assumes) and the §25B saver's credit with the AGI limits of IRS Notices 2021-61, 2022-55, 2023-75, taken
before the child tax credit as Credit Limit Worksheet A orders them.
Round 9 adds the AMT (section below). Not computed: blindness, education,
dependent-care and premium tax credits (no expense, coverage or blindness input in the contract).

Sources (saved with sha256 in `cmp20/improve-anglo/refs/us/`):
* Rev. Proc. 2021-45 (2022), Rev. Proc. 2022-38 (2023), Rev. Proc. 2023-34 (2024) (irs.gov/pub/irs-drop): §2.01
  Tables 1-3 (§1(j)(2)(A)-(C)); §3.05 "the amount used in § 24(d)(1)(A) to determine the amount of credit under § 24
  that may be refundable is $1,500" / "$1,600" / "$1,700"; §3.06(1) earned income credit table and (2) "investment
  income exceeds $10,300" / "$11,000" / "$11,600"; §3.15(1) standard deduction.
* IRC §24(h)(2) ($2,000), (h)(3) ($400,000 joint / $200,000), (h)(4) ($500 other dependants) for 2018-2025 as
  enacted by Pub. L. 115-97 §11022 (unchanged by the Rev. Procs., which index only the refundable amount).
* SSA, "Cost-of-Living Increase and Other Determinations" for 2022 (86 FR 58715), 2023 (87 FR 64296), 2024
  (88 FR 72803): "the OASDI contribution and benefit base is $147,000" / "$160,200" / "$168,600".
-/

namespace TaxCode.Individual.Prior
open TaxCode.Individual

/-- A §1(j) table from its bracket ends; every base is the tax at the end of the previous row (as `C.Sched.Ok`
requires), so the printed bases are checked by the `#guard`s below rather than typed in. -/
def mkSched (e1 e2 e3 e4 e5 e6 : Int) : C.Sched :=
  let b1 := 10 * e1
  let b2 := b1 + 12 * (e2 - e1)
  let b3 := b2 + 22 * (e3 - e2)
  let b4 := b3 + 24 * (e4 - e3)
  let b5 := b4 + 32 * (e5 - e4)
  let b6 := b5 + 35 * (e6 - e5)
  ⟨e1, e2, e3, e4, e5, e6, b1, b2, b3, b4, b5, b6⟩

structure YP where
  year : Nat
  single : C.Sched
  mfj : C.Sched
  hoh : C.Sched
  stdSingle : Int
  stdMfj : Int
  stdHoh : Int
  /-- §24(h)(5) as indexed (Rev. Proc. §3.05) -/
  actcCap : Int
  /-- §32(b) by number of qualifying children (cp, pp, earned income amount, thresholds, max, completed phase-outs) -/
  eic : Nat → D.EicParams
  eicInvestmentLimit : Int
  /-- Social Security Act §230 contribution and benefit base -/
  wageBase : Int
  /-- §63(f) additional standard deduction per aged individual: married / unmarried (Rev. Proc. §3.15(3)) -/
  agedMarried : Int := 0
  agedUnmarried : Int := 0
  /-- §1(h)(1)(B), (C) as modified by §1(j)(5): maximum zero-rate and 15-percent-rate amounts (Rev. Proc. §2.03),
  joint / head of household / other -/
  zeroMfj : Int := 0
  zeroHoh : Int := 0
  zeroOther : Int := 0
  fifteenMfj : Int := 0
  fifteenHoh : Int := 0
  fifteenOther : Int := 0
  /-- §219(b)(5)(A) deductible amount (IRS Notices 2021-61, 2022-55, 2023-75); §219(b)(5)(B) $1,000 at 50+ -/
  iraLimit : Int := 0
  /-- §199A(e)(2) threshold amount: joint / other (phase-in range $100,000 / $50,000, §199A(b)(3)(B)) -/
  qbiThrMfj : Int := 0
  qbiThrOther : Int := 0
  /-- §25B(b)(1)(A), (B), (C)-(D) AGI limits (50 % / 20 % / 10 %): joint, head of household, other -/
  saverMfj : Int × Int × Int := (0, 0, 0)
  saverHoh : Int × Int × Int := (0, 0, 0)
  saverOther : Int × Int × Int := (0, 0, 0)
  /-- §55(d)(1) exemption, §55(d)(2) phase-out threshold (joint / other) and the §55(b)(1)(A) 28 % breakpoint
  (Rev. Proc. §3.11; round 9) -/
  amtExMfj : Int := 0
  amtExOther : Int := 0
  amtThrMfj : Int := 0
  amtThrOther : Int := 0
  amtBreak : Int := 0

/-- 2022: Rev. Proc. 2021-45 §2.01 Tables 1-3, §3.05, §3.06, §3.15; 86 FR 58715. -/
def y2022 : YP :=
  { year := 2022
    single := mkSched 10275 41775 89075 170050 215950 539900
    mfj := mkSched 20550 83550 178150 340100 431900 647850
    hoh := mkSched 14650 55900 89050 170050 215950 539900
    stdSingle := 12950, stdMfj := 25900, stdHoh := 19400, actcCap := 1500
    eic := fun k => match k with
      | 0 => ⟨765, 765, 7320, 9160, 15290, 560, 16480, 22610⟩
      | 1 => ⟨3400, 1598, 10980, 20130, 26260, 3733, 43492, 49622⟩
      | 2 => ⟨4000, 2106, 15410, 20130, 26260, 6164, 49399, 55529⟩
      | _ => ⟨4500, 2106, 15410, 20130, 26260, 6935, 53057, 59187⟩
    eicInvestmentLimit := 10300, wageBase := 147000
    agedMarried := 1400, agedUnmarried := 1750
    zeroMfj := 83350, zeroHoh := 55800, zeroOther := 41675
    fifteenMfj := 517200, fifteenHoh := 488500, fifteenOther := 459750
    iraLimit := 6000
    qbiThrMfj := 340100, qbiThrOther := 170050
    saverMfj := (41000, 44000, 68000), saverHoh := (30750, 33000, 51000), saverOther := (20500, 22000, 34000)
    amtExMfj := 118100, amtExOther := 75900, amtThrMfj := 1079800, amtThrOther := 539900, amtBreak := 206100 }

/-- 2023: Rev. Proc. 2022-38; 87 FR 64296. -/
def y2023 : YP :=
  { year := 2023
    single := mkSched 11000 44725 95375 182100 231250 578125
    mfj := mkSched 22000 89450 190750 364200 462500 693750
    hoh := mkSched 15700 59850 95350 182100 231250 578100
    stdSingle := 13850, stdMfj := 27700, stdHoh := 20800, actcCap := 1600
    eic := fun k => match k with
      | 0 => ⟨765, 765, 7840, 9800, 16370, 600, 17640, 24210⟩
      | 1 => ⟨3400, 1598, 11750, 21560, 28120, 3995, 46560, 53120⟩
      | 2 => ⟨4000, 2106, 16510, 21560, 28120, 6604, 52918, 59478⟩
      | _ => ⟨4500, 2106, 16510, 21560, 28120, 7430, 56838, 63398⟩
    eicInvestmentLimit := 11000, wageBase := 160200
    agedMarried := 1500, agedUnmarried := 1850
    zeroMfj := 89250, zeroHoh := 59750, zeroOther := 44625
    fifteenMfj := 553850, fifteenHoh := 523050, fifteenOther := 492300
    iraLimit := 6500
    qbiThrMfj := 364200, qbiThrOther := 182100
    saverMfj := (43500, 47500, 73000), saverHoh := (32625, 35625, 54750), saverOther := (21750, 23750, 36500)
    amtExMfj := 126500, amtExOther := 81300, amtThrMfj := 1156300, amtThrOther := 578150, amtBreak := 220700 }

/-- 2024: Rev. Proc. 2023-34; 88 FR 72803. -/
def y2024 : YP :=
  { year := 2024
    single := mkSched 11600 47150 100525 191950 243725 609350
    mfj := mkSched 23200 94300 201050 383900 487450 731200
    hoh := mkSched 16550 63100 100500 191950 243700 609350
    stdSingle := 14600, stdMfj := 29200, stdHoh := 21900, actcCap := 1700
    eic := fun k => match k with
      | 0 => ⟨765, 765, 8260, 10330, 17250, 632, 18591, 25511⟩
      | 1 => ⟨3400, 1598, 12390, 22720, 29640, 4213, 49084, 56004⟩
      | 2 => ⟨4000, 2106, 17400, 22720, 29640, 6960, 55768, 62688⟩
      | _ => ⟨4500, 2106, 17400, 22720, 29640, 7830, 59899, 66819⟩
    eicInvestmentLimit := 11600, wageBase := 168600
    agedMarried := 1550, agedUnmarried := 1950
    zeroMfj := 94050, zeroHoh := 63000, zeroOther := 47025
    fifteenMfj := 583750, fifteenHoh := 551350, fifteenOther := 518900
    iraLimit := 7000
    qbiThrMfj := 383900, qbiThrOther := 191950
    saverMfj := (46000, 50000, 76500), saverHoh := (34500, 37500, 57375), saverOther := (23000, 25000, 38250)
    amtExMfj := 133300, amtExOther := 85700, amtThrMfj := 1218700, amtThrOther := 609350, amtBreak := 232600 }

def yearParams? (year : Nat) : Option YP :=
  if year = 2022 then some y2022 else if year = 2023 then some y2023 else if year = 2024 then some y2024 else none

/-! ## Checks against the printed Rev. Proc. tables (bases in cents) -/
-- every printed base of Tables 1-3, 2022-2024 (a typo in the bracket ends or in the Rev. Proc. would fail here)
#guard (y2022.single.b1, y2022.single.b2, y2022.single.b3, y2022.single.b4, y2022.single.b5, y2022.single.b6) =
  (102750, 480750, 1521350, 3464750, 4933550, 16271800)
#guard (y2022.mfj.b2, y2022.mfj.b3, y2022.mfj.b4, y2022.mfj.b5, y2022.mfj.b6) = (961500, 3042700, 6929500, 9867100, 17425350)
#guard (y2022.hoh.b2, y2022.hoh.b3, y2022.hoh.b4, y2022.hoh.b5, y2022.hoh.b6) = (641500, 1370800, 3314800, 4783600, 16121850)
#guard (y2023.single.b2, y2023.single.b3, y2023.single.b4, y2023.single.b5, y2023.single.b6) = (514700, 1629000, 3710400, 5283200, 17423825)
#guard (y2023.mfj.b2, y2023.mfj.b3, y2023.mfj.b4, y2023.mfj.b5, y2023.mfj.b6) = (1029400, 3258000, 7420800, 10566400, 18660150)
#guard (y2023.hoh.b2, y2023.hoh.b3, y2023.hoh.b4, y2023.hoh.b5, y2023.hoh.b6) = (686800, 1467800, 3549800, 5122600, 17262350)
#guard (y2024.single.b2, y2024.single.b3, y2024.single.b4, y2024.single.b5, y2024.single.b6) = (542600, 1716850, 3911050, 5567850, 18364725)
#guard (y2024.mfj.b2, y2024.mfj.b3, y2024.mfj.b4, y2024.mfj.b5, y2024.mfj.b6) = (1085200, 3433700, 7822100, 11135700, 19666950)
#guard (y2024.hoh.b2, y2024.hoh.b3, y2024.hoh.b4, y2024.hoh.b5, y2024.hoh.b6) = (724100, 1546900, 3741700, 5397700, 18195450)
-- the maximum credits are the credit percentage times the earned income amount, rounded (as for 2025)
#guard [y2022, y2023, y2024].all fun y => [0, 1, 2, 3].all fun k =>
  let p := y.eic k; roundDollar (p.cp * p.eia) 10000 = p.maxCredit

/-! ## The return -/

def YP.sched (y : YP) : Filing → C.Sched
  | .mfj => y.mfj
  | .qss => y.mfj
  | .hoh => y.hoh
  | _ => y.single

def YP.std (y : YP) : Filing → Int
  | .mfj => y.stdMfj
  | .qss => y.stdMfj
  | .hoh => y.stdHoh
  | _ => y.stdSingle

/-- Form 1040 line 16: the Tax Table below $100,000 (the same midpoint rule as `C.tableTax`), the schedule above. -/
def YP.line16 (y : YP) (f : Filing) (ti : Int) : Int :=
  if ti < 100000 then roundDollar ((y.sched f).dbl.cents (C.midpoint2 ti)) 200
  else roundDollar ((y.sched f).cents ti) 100

def YP.eicTable (y : YP) (k : Nat) (joint : Bool) (x : Int) : Int :=
  let p := y.eic k
  D.eicTab p.cp p.pp p.eia (p.thr joint) p.maxCredit (p.co joint) x

/-- EIC Worksheet A with the year's table and §32(i) limit. -/
def YP.eicCredit (y : YP) (h : Household) (earned agi : Int) : Int :=
  if !D.eicEligible h ∨ y.eicInvestmentLimit < D.disqualifiedIncome h then 0 else
  let k := D.eicChildren h
  let j := h.filing == .mfj
  if agi < (y.eic k).thr j then y.eicTable k j earned
  else min (y.eicTable k j earned) (y.eicTable k j agi)

/-- Employee FICA with the year's wage base (§3101(a), (b)(1)), as `ficaEmployee` does for 2025. -/
def YP.fica (y : YP) (h : Household) : Int :=
  bp (min (A.headWages h) y.wageBase) 620 + bp (min h.wagesSpouse y.wageBase) 620 + bp h.wages 145

/-- §24 before Pub. L. 119-21: $2,000 per qualifying child, $500 per other dependant, phase-out $50 per $1,000 over
$400,000 / $200,000 (the same thresholds as `D.ctcThreshold`); refundable part per Schedule 8812 Part II-A with the
year's cap. -/
def ctcPerChild : Int := 2000

structure Result where
  agi : Int
  std : Int
  deduction : Int
  ti : Int
  regular : Int
  ctc : Int
  actc : Int
  eic : Int
  fica : Int
  addl : Int
  niit : Int
  ira : Int
  amt : Int
  se : Int
  qbi : Int
  saver : Int
  incomeTax : Int    -- after nonrefundable and refundable credits (negative: a refund); without NIIT and addl Medicare

def YP.zero (y : YP) : Filing → Int
  | .mfj => y.zeroMfj
  | .qss => y.zeroMfj
  | .hoh => y.zeroHoh
  | _ => y.zeroOther

def YP.fifteen (y : YP) : Filing → Int
  | .mfj => y.fifteenMfj
  | .qss => y.fifteenMfj
  | .hoh => y.fifteenHoh
  | _ => y.fifteenOther

/-- Qualified Dividends and Capital Gain Tax Worksheet (Form 1040 line 16; §1(h) as modified by §1(j)(5)) with the
year's amounts; `ti` taxable income, `q` qualified dividends plus net long-term gain (not below zero). Dollars. -/
def YP.qdcgTax (y : YP) (f : Filing) (ti q : Int) : Int :=
  if q ≤ 0 then y.line16 f ti else
  let l4 := min q ti
  let l5 := D.pos (ti - l4)
  let l7 := min ti (y.zero f)
  let l8 := min l5 l7
  let l9 := l7 - l8
  let l10 := min ti l4
  let l12 := l10 - l9
  let l14 := min ti (y.fifteen f)
  let l16 := D.pos (l14 - (l5 + l9))
  let l17 := min l12 l16
  let l20 := l10 - (l9 + l17)
  let tax := roundDollar (15 * l17 + 20 * l20) 100 + y.line16 f l5
  min tax (y.line16 f ti)

/-- §63(f): the additional amount for each spouse (or the individual) aged 65 or over (blindness not modelled). -/
def YP.aged (y : YP) (h : Household) : Int :=
  let one := if h.filing == .mfj || h.filing == .qss || h.filing == .mfs then y.agedMarried else y.agedUnmarried
  (if h.head.age ≥ 65 then one else 0) + (match h.spouse with | some s => if s.age ≥ 65 then one else 0 | none => 0)

/-- §219(b)(1), (b)(5), (c): traditional IRA deduction for individuals who are not active participants (the
adapter's assumption), limited to the deductible amount (+$1,000 at 50+) per spouse and to compensation. -/
def YP.iraDeduction (y : YP) (h : Household) : Int :=
  let lim (p : Person) : Int := y.iraLimit + (if p.age ≥ 50 then 1000 else 0)
  let cap := lim h.head + (match h.spouse with | some s => lim s | none => 0)
  min (D.pos h.iraContributions) (min cap (D.pos (h.wages + h.seIncome)))

/-- §1401(a), (b)(1) on 92.35 % of net earnings (§1402(a)(12)), nil below $400 (§1402(b)(2)), the OASDI part
limited to the year's contribution and benefit base less the head's wages (§1402(b)(1)); whole dollars as
`A.seTaxCore` (`half` = the §164(f) deduction). -/
def YP.seTax (y : YP) (se wages : Int) (half : Bool) : Int :=
  let base := min (A.seIncome10k se) (10000 * max 0 (y.wageBase - wages))
  roundDollar (124 * base + 29 * A.seIncome10k se) (if half then 20000000 else 10000000)

/-- §199A(a), (b)(2)-(3): 20 % of qualified business income, phased out over the range above the threshold for a
business with no W-2 wages and no qualified property (the adapter's case), at most 20 % of taxable income before
the deduction less net capital gain (§199A(a)(2)). -/
def YP.qbiDeduction (y : YP) (f : Filing) (qbi tbq ncg : Int) : Int :=
  if qbi ≤ 0 then 0 else
  let thr := if f == .mfj || f == .qss then y.qbiThrMfj else y.qbiThrOther
  let range := if f == .mfj || f == .qss then 100000 else 50000
  let tent := 20 * qbi    -- cents
  let comp := if tbq ≤ thr then tent else if tbq ≥ thr + range then 0 else tent - tent * (tbq - thr) / range
  D.pos (min (roundDollar comp 100) (roundDollar (20 * D.pos (tbq - ncg)) 100))

/-- §25B(a)-(b): 50 / 20 / 10 % of up to $2,000 of each individual's qualified retirement contributions by AGI. -/
def YP.saverCredit (y : YP) (h : Household) (agi : Int) : Int :=
  let (a, b, c) := if h.filing == .mfj || h.filing == .qss then y.saverMfj
    else if h.filing == .hoh then y.saverHoh else y.saverOther
  let pct := if agi ≤ a then 50 else if agi ≤ b then 20 else if agi ≤ c then 10 else 0
  let rc := D.pos h.retirementContributions
  let people : List (Int × Nat) :=
    if h.filing == .mfj then [(rc / 2, h.head.age), (rc - rc / 2, (h.spouse.map (·.age)).getD 0)] else [(rc, h.head.age)]
  (people.map fun (c, age) => if age ≥ 18 then roundDollar (min c 2000 * pct) 100 else 0).foldl (· + ·) 0

/-! ## Alternative minimum tax (round 9): IRC §55 with Rev. Proc. 2021-45 / 2022-38 / 2023-34 §3.11 amounts

Exemptions $118,100 / $75,900, phase-out from $1,079,800 / $539,900, 28 % above a taxable excess of $206,100 (2022);
$126,500 / $81,300, $1,156,300 / $578,150, $220,700 (2023); $133,300 / $85,700, $1,218,700 / $609,350, $232,600
(2024) (joint / unmarried; the adapter files no separate returns, so the §55(d)(2) MFS add-back is not needed). The
arithmetic is the 2025 module's (`C.taxableExcessQ`, `C.rate2628`, `C.tmtCapGainQ`: sixteenths of a dollar, §55(b)(3)
with the regular-tax (B) and (C)(ii) excesses as Form 6251 Part III lines 43-53 take them). AMTI (§55(b)(2), §56(b)(1)):
taxable income plus the standard deduction when it is claimed; the contract has no other adjustment or preference
(cash gifts are deductible for the AMT; the §199A deduction is not added back, §199A(f)(2)). -/

def YP.amtEx (y : YP) (f : Filing) : Int := if f == .mfj || f == .qss then y.amtExMfj else y.amtExOther
def YP.amtThr (y : YP) (f : Filing) : Int := if f == .mfj || f == .qss then y.amtThrMfj else y.amtThrOther

def YP.rate2628 (y : YP) (xQ : Int) : Int := 26 * min xQ (16 * y.amtBreak) + 28 * max 0 (xQ - 16 * y.amtBreak)

/-- Taxable excess in sixteenths (§55(b)(1)(B), (d)(1)-(2)). -/
def YP.taxableExcessQ (y : YP) (f : Filing) (amti : Int) : Int :=
  let a := 16 * amti
  let ex := max 0 (16 * y.amtEx f - max 0 (a - 16 * y.amtThr f) / 4)
  max 0 (a - ex)

/-- Tentative minimum tax in 1/1600 dollar: §55(b)(1)(A), capped by §55(b)(3) when there is a net capital gain `g`
(qualified dividends + net long-term gain). -/
def YP.tmtQ (y : YP) (f : Filing) (amti ti g : Int) : Int :=
  let te := y.taxableExcessQ f amti
  if 0 < g then
    let ti0 := max 0 ti
    let ord := max 0 (ti0 - max 0 g)
    let gain := min (max 0 g) ti0
    let zeroPart := min gain (max 0 (min ti0 (y.zero f) - ord))
    let gainQ := min (16 * max 0 g) te
    let aQ := te - gainQ
    let bQ := min gainQ (16 * max 0 (min ti0 (y.zero f) - ord))
    let cQ := min (gainQ - bQ) (16 * max 0 (min ti0 (y.fifteen f) - (ord + zeroPart)))
    let dQ := gainQ - bQ - cQ
    min (y.rate2628 te) (y.rate2628 aQ + 15 * cQ + 20 * dQ)
  else y.rate2628 te

/-- §55(a): the excess of the tentative minimum tax (whole dollars, half up) over the regular tax. -/
def YP.amt (y : YP) (f : Filing) (amti ti g regular : Int) : Int :=
  D.pos (roundDollar (y.tmtQ f amti ti g) 1600 - regular)

/-- **IRC §22 credit for the elderly** (round 11; unindexed): for each "qualified individual" (65 or over, §22(b)(1)),
15 % of the initial amount ($5,000 single, head of household, or a joint return with one qualified spouse; $7,500 a
joint return with both, §22(c)(2)(A)) reduced by one-half of AGI over $7,500 (single) / $10,000 (joint) (§22(d));
the contract has no nontaxable pensions or disability (§22(c)(3)). Whole dollars, half up. -/
def elderlyCredit (h : Household) (agi : Int) : Int :=
  let q : Nat := (if h.head.age ≥ 65 then 1 else 0) + (match h.spouse with | some s => if s.age ≥ 65 then 1 else 0 | none => 0)
  if q = 0 || h.filing == .mfs then 0 else
  let joint := h.filing == .mfj || h.filing == .qss
  let initial : Int := if joint && q = 2 then 7500 else 5000
  let red := D.pos (agi - (if joint then 10000 else 7500))   -- one-half of this
  roundDollar (15 * D.pos (2 * initial - red)) 200

def compute (y : YP) (h : Household) : Result :=
  let q := h.qualifiedDividends + D.pos h.longTermGains
  let ordinary := h.wages + h.taxableInterest + (h.ordinaryDividends - h.qualifiedDividends) + h.shortTermGains
    + h.pensions + h.otherIncome
  let ira := y.iraDeduction h
  let hw := A.headWages h
  let se := y.seTax h.seIncome hw false
  let halfSe := y.seTax h.seIncome hw true
  let agi := ordinary + h.seIncome + q - ira - halfSe
  let std := y.std h.filing + y.aged h
  -- §170(b)(1)(A), (G): cash gifts to public charities, at most 60 % of AGI; itemize when larger (§63(e))
  let itemized := min (D.pos h.charitableCash) (D.pos agi * 60 / 100)
  let ded := max std itemized
  let tbq := D.pos (agi - ded)
  let qbi := y.qbiDeduction h.filing (h.seIncome - halfSe) tbq (D.pos h.longTermGains + D.pos h.qualifiedDividends)
  let ti := D.pos (tbq - qbi)
  let regular := y.qdcgTax h.filing ti q
  -- §55: AMTI = taxable income + the standard deduction when claimed (no other item reaches the contract)
  let amtv := y.amt h.filing (ti + (if itemized > std then 0 else std)) ti q regular
  let before := regular + amtv
  let c := D.householdCtcCounts h
  let tentative := ctcPerChild * c.children + D.odcPerDependent * c.others
  let afterPhase := D.pos (tentative - D.ctcReduction h.filing agi)
  -- Credit Limit Worksheet A: the saver's credit (Schedule 3) is taken before the child tax credit
  -- Schedule 3 credits before the child tax credit (Credit Limit Worksheet A): §22, then §25B
  let elderly := min (elderlyCredit h agi) (D.pos before)
  let saver := min (y.saverCredit h agi) (D.pos (before - elderly))
  let nonref := min afterPhase (D.pos (before - elderly - saver))
  let fica := y.fica h + halfSe
  let earned := h.wages + h.seIncome - halfSe
  let eic := y.eicCredit h earned agi
  let earnedAmt := max (D.pctRound (D.pos (earned - D.actcEarnedFloor)) D.actcRateBp)
    (if 3 ≤ c.children then D.pos (fica - eic) else 0)
  let actc := min (min (afterPhase - nonref) (y.actcCap * c.children)) earnedAmt
  let addl := A.additionalMedicare h
  -- §1411: 3.8 % of the lesser of net investment income and MAGI over $250,000 joint / $200,000 (unindexed)
  let nii := h.taxableInterest + h.ordinaryDividends + D.pos (h.shortTermGains + h.longTermGains) + D.pos h.otherIncome
  let thr := if h.filing == .mfj || h.filing == .qss then 250000 else if h.filing == .mfs then 125000 else 200000
  let niit := roundDollar (38 * min (D.pos nii) (D.pos (agi - thr))) 1000
  { agi, std, deduction := ded, ti, regular, ctc := nonref, actc, eic, fica, addl, niit, ira, amt := amtv, se, qbi,
    saver, incomeTax := before - elderly - saver - nonref - actc - eic }

-- 2023, married, $60,000 wages and $20,000 qualified dividends: taxable 52,300, of which 20,000 at 0 %
def exDividends : Household :=
  { filing := .mfj, head := { age := 40 }, spouse := some { age := 40 }, wages := 60000,
    ordinaryDividends := 20000, qualifiedDividends := 20000 }
#guard (compute y2023 exDividends).regular = y2023.line16 .mfj 32300

-- 2024, single, $49,258 wages: taxable $34,658; Tax Table $3,920 (§1(j) schedule $3,920.46 + table midpoint)
#guard (compute y2024 { filing := .single, head := { age := 40 }, wages := 49258 }).ti = 34658


-- AMT checks (round 9): wages-only returns at these points owe no AMT
def amtHousehold (f : Filing) (w qd : Int) : Household :=
  { filing := f
    head := { age := 40 }
    spouse := if f == .mfj then some { age := 40 } else none
    wages := w
    ordinaryDividends := qd
    qualifiedDividends := qd }
-- §22: single, 71, pension $17,168: 15 % x ($5,000 - ($17,168 - $7,500) / 2) = $24.90 -> $25
#guard elderlyCredit { filing := .single, head := { age := 71 } } 17168 = 25
def amtProbe (y : YP) (f : Filing) (w qd : Int) : Int := (compute y (amtHousehold f w qd)).amt
#guard [y2022, y2023, y2024].all fun y => [(Filing.single : Filing), .hoh, .mfj].all fun f =>
  [50000, 200000, 600000, 1000000, 3000000].all fun w => amtProbe y f w 0 = 0

end TaxCode.Individual.Prior
