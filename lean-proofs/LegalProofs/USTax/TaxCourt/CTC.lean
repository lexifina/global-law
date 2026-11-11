import LegalProofs.USTax.TaxCourt.EIC

/-!
# §24 child tax credit, additional child tax credit, credit for other dependents (2016–2024)

Three regimes:

| | 2016–2017 (pre-TCJA §24) | 2018–2020, 2022–2024 (§24(h), TCJA) | 2021 (§24(i)–(j), ARPA §9611) |
|---|---|---|---|
| per qualifying child | $1,000 | $2,000 (SSN required, §24(h)(7)) | $3,000; $3,600 under 6 |
| child's age (year end) | under 17 | under 17 | under 18 |
| other dependents | — | $500 (§24(h)(4)) | $500 |
| phase-out ($50 per $1,000 or fraction) | over $110,000 joint / $75,000 single, HoH, QSS / $55,000 separate | over $400,000 joint / $200,000 other | the increase over $150,000 joint & QSS / $112,500 HoH / $75,000 other (capped at 5% of the range up to the regular threshold); then the regular reduction |
| refundable part | ACTC: lesser of unused credit and 15% of earned income over $3,000 (3+ children: SS taxes − EIC if greater) | ACTC as before but over $2,500 and capped per child ($1,400; $1,500 in 2022, $1,600 in 2023, $1,700 in 2024) | the whole child credit is refundable if the taxpayer's (either spouse's) principal place of abode was in the U.S. for over half the year; otherwise the TCJA ACTC rule with the $1,400 cap |

2021 advance payments (§7527A) are reconciled under §24(j): the credit is reduced by advance payments; any excess
increases tax, less the safe-harbor amount ($2,000 per child counted for the advance but not on the return, phased
out between 100% and 200% of $60,000 joint / $50,000 HoH / $40,000 other).

The refundable part follows the statute (§24(d)(1) with (h)(5)); where it differs from Schedule 8812 (see
`TaxCode.Individual.D.form_exceeds_statute`) only a taxpayer with both qualifying children and other dependents near
the phase-out, with little tax, is affected.
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual

/-- §24(c)(1) (and §24(i)(2) in 2021): a qualifying child for the credit — a §152(c) qualifying child (a §152(e)
release counts) who is the taxpayer's dependent, under 17 (under 18 in 2021) at year end, and a U.S. citizen, national
or resident (§24(c)(2)). Whether the child has an SSN is applied in `ctcCounts`. -/
def ctcQualifyingChild (p : Params) (taxpayerIsDependent : Bool) (x : PersonFacts) : Bool :=
  qualifyingChild p.year x && isDependent p taxpayerIsDependent x && x.usCitizenOrResident &&
    x.age < (if p.year == 2021 then 18 else 17)

/-- Who counts for what. -/
structure CtcCounts where
  /-- qualifying children allowed the full per-child amount -/
  children : Nat
  /-- of whom under 6 at year end (2021 only) -/
  under6 : Nat
  /-- dependents allowed only the $500 credit for other dependents (2018+) -/
  others : Nat
  deriving Repr, DecidableEq, Inhabited

/-- Counts from the dependents: before 2018 a qualifying child needs a TIN (§24(e)); from 2018 a child without an SSN
and every other U.S. dependent count for the $500 (§24(h)(4), (h)(7)). Without the taxpayer's TIN no credit. -/
def ctcCounts (p : Params) (taxpayerTIN taxpayerIsDependent : Bool) (deps : List PersonFacts) : CtcCounts :=
  if !taxpayerTIN then ⟨0, 0, 0⟩ else
  let isFull := fun x : PersonFacts =>
    ctcQualifyingChild p taxpayerIsDependent x && (if p.ctc.ssnForChild then x.hasSSN else x.hasTIN)
  let full := deps.filter isFull
  let others := deps.filter fun x =>
    isDependent p taxpayerIsDependent x && x.usCitizenOrResident && x.hasTIN && !isFull x
  ⟨full.length, (full.filter (·.age < 6)).length, if p.ctc.perOther > 0 then others.length else 0⟩

/-- What else the credit reads from the return. -/
structure CtcFacts where
  filing : Filing
  /-- §24(b)(1): AGI increased by §§911, 931, 933 exclusions. -/
  magi : Int
  /-- The §26(a) limit left for this credit: tax less the nonrefundable credits taken before it. -/
  taxLeft : Int
  /-- Earned income (§32(c)(2)), for §24(d)(1)(B)(i). -/
  earnedIncome : Int
  /-- Social security taxes (§24(d)(2)): the employee share of FICA plus one-half of SE tax. -/
  ssTaxes : Int := 0
  /-- The earned income credit allowed (§24(d)(1)(B)(ii)). -/
  eic : Int := 0
  /-- 2021: principal place of abode in the U.S. for more than half the year (§24(i)(1)). -/
  usAbode : Bool := true
  /-- 2021: advance child tax credit payments received (§24(j)(1)). -/
  advancePayments : Int := 0
  /-- 2021: qualifying children the IRS counted in setting the advance payments (§24(j)(2)(B)(ii)). -/
  advanceChildren : Nat := 0
  deriving Repr, Inhabited

structure CtcResult where
  /-- nonrefundable part used against tax (CTC and/or ODC) -/
  nonrefundable : Int := 0
  /-- refundable part (ACTC; in 2021 the refundable child credit, after advance payments) -/
  refundable : Int := 0
  /-- the credit after the phase-out(s), before the §26(a) limit -/
  afterPhaseout : Int := 0
  /-- 2021: increase in tax for advance payments over the credit allowed, after the safe harbor (§24(j)(2)) -/
  excessAdvance : Int := 0
  deriving Repr, Inhabited, DecidableEq

/-- §24(b)(2) / (h)(3) threshold amount. -/
def ctcThreshold (p : Params) : Filing → Int
  | .mfj => p.ctc.thrJoint
  | .mfs => p.ctc.thrMfs
  | _ => p.ctc.thrOther

/-- §24(b)(1): "$50 for each $1,000 (or fraction thereof)" of MAGI over the threshold. -/
def ctcReduction (p : Params) (f : Filing) (magi : Int) : Int := 50 * ceilDiv (pos (magi - ctcThreshold p f)) 1000

/-- §24(d)(1)(B): the greater of 15% of earned income over the floor and, with 3 or more qualifying children, social
security taxes less the EIC. Rounded as Schedule 8812 rounds. -/
def actcEarnedAmount (p : Params) (children : Nat) (f : CtcFacts) : Int :=
  max (pctRound (pos (f.earnedIncome - p.ctc.earnedFloor)) 1500)
    (if 3 ≤ children then pos (f.ssTaxes - f.eic) else 0)

/-- 2016–2020, 2022–2024. -/
def ctcStandard (p : Params) (c : CtcCounts) (f : CtcFacts) (perChild : Int := p.ctc.perChild) : CtcResult :=
  let tentative := perChild * c.children + p.ctc.perOther * c.others
  let red := ctcReduction p f.filing f.magi
  let after := pos (tentative - red)
  let nonref := min after (pos f.taxLeft)
  let unused := after - nonref
  -- §24(d)(1)(A) as limited by §24(h)(5): only the qualifying-child credit, at most the cap per child.
  let capA := if p.ctc.refundCap = 0 then unused
    else min (pos (perChild * c.children - red)) (p.ctc.refundCap * c.children)
  let actc := if c.children = 0 then 0 else min capA (min unused (actcEarnedAmount p c.children f))
  { nonrefundable := nonref, refundable := actc, afterPhaseout := after }

/-- 2021, §24(i)(4): the applicable threshold for the reduction of the ARPA increase. -/
def arpaThreshold : Filing → Int
  | .mfj | .qss => 150000
  | .hoh => 112500
  | _ => 75000

/-- 2021, §24(j)(2)(B)(iii): the income threshold for the safe harbor. -/
def safeHarborThreshold : Filing → Int
  | .mfj | .qss => 60000
  | .hoh => 50000
  | _ => 40000

/-- 2021. -/
def ctc2021 (p : Params) (c : CtcCounts) (f : CtcFacts) : CtcResult :=
  let increase : Int := 1000 * (c.children : Int) + 600 * (c.under6 : Int)
  let base : Int := 2000 * (c.children : Int) + 500 * (c.others : Int)
  let range := ctcThreshold p f.filing - arpaThreshold f.filing
  let redA := min (min increase (50 * ceilDiv (pos (f.magi - arpaThreshold f.filing)) 1000)) (range / 20)
  let redB := ctcReduction p f.filing f.magi
  let after := pos (base + increase - redA - redB)
  let r : CtcResult :=
    if f.usAbode then
      -- §24(i)(1): the child credit is refundable; the $500 credits stay nonrefundable (Schedule 8812 (2021) l. 14a)
      let odcPart := min after (500 * c.others)
      let refundable := after - odcPart
      { nonrefundable := min odcPart (pos f.taxLeft), refundable := refundable, afterPhaseout := after }
    else
      -- §24(d) applies with the §24(h)(5) $1,400 cap on the increased child amounts
      let nonref := min after (pos f.taxLeft)
      let unused := after - nonref
      let capA := min (pos (2000 * c.children + increase - redA - redB)) (p.ctc.refundCap * c.children)
      let actc := if c.children = 0 then 0 else min capA (min unused (actcEarnedAmount p c.children f))
      { nonrefundable := nonref, refundable := actc, afterPhaseout := after }
  -- §24(j)(1): the credit is reduced by advance payments, first against the refundable part
  let adv := pos f.advancePayments
  let refAfter := pos (r.refundable - adv)
  let left := pos (adv - r.refundable)
  let nonrefAfter := pos (r.nonrefundable - left)
  let excess := pos (adv - r.refundable - r.nonrefundable)
  -- §24(j)(2)(B): safe harbor $2,000 per child counted for the advance but not on the return, phased out
  let shThr := safeHarborThreshold f.filing
  let missing : Int := pos ((f.advanceChildren : Int) - c.children)
  let sh0 := 2000 * missing
  let over := pos (f.magi - shThr)
  let sh := if over ≥ shThr then 0 else roundDollar (sh0 * (shThr - over)) shThr
  { nonrefundable := nonrefAfter, refundable := refAfter, afterPhaseout := r.afterPhaseout,
    excessAdvance := pos (excess - sh) }

/-- **The credit for the year.** -/
def ctcFor (p : Params) (c : CtcCounts) (f : CtcFacts) : CtcResult :=
  if p.year == 2021 then ctc2021 p c f else ctcStandard p c f

/-! ## Tests: Schedule 8812 / Pub. 972 figures -/

section
private def py (y : Nat) : Params := (params? y).getD default
private def fam (n : Nat) (u6 : Nat := 0) (o : Nat := 0) : CtcCounts := ⟨n, u6, o⟩
private def ff (f : Filing) (magi tax earned : Int) : CtcFacts := { filing := f, magi := magi, taxLeft := tax, earnedIncome := earned }

-- 2017: two children, $1,000 each, enough tax: $2,000 nonrefundable.
#guard ctcFor (py 2017) (fam 2) (ff .mfj 60000 3000 60000) = { nonrefundable := 2000, afterPhaseout := 2000 }
-- 2017 phase-out: joint MAGI $110,001 loses $50 (one fraction of $1,000).
#guard (ctcFor (py 2017) (fam 2) (ff .mfj 110001 9000 110001)).afterPhaseout = 1950
-- 2016, single, $75,000 threshold (not indexed): $76,500 loses $100.
#guard (ctcFor (py 2016) (fam 1) (ff .single 76500 9000 76500)).afterPhaseout = 900
-- 2017 ACTC: one child, no tax, earned income $10,000: 15% × $7,000 = $1,050, capped at the $1,000 unused credit.
#guard ctcFor (py 2017) (fam 1) (ff .single 10000 0 10000) = { refundable := 1000, afterPhaseout := 1000 }
-- 2018 ACTC: one child, no tax, earned $10,000: 15% × $7,500 = $1,125, under the $1,400 cap.
#guard ctcFor (py 2018) (fam 1) (ff .single 10000 0 10000) = { refundable := 1125, afterPhaseout := 2000 }
-- 2024 ACTC cap $1,700: one child, no tax, large earned income.
#guard (ctcFor (py 2024) (fam 1) (ff .hoh 40000 0 40000)).refundable = 1700
-- 2022 cap $1,500; 2023 $1,600.
#guard (ctcFor (py 2022) (fam 1) (ff .hoh 40000 0 40000)).refundable = 1500
#guard (ctcFor (py 2023) (fam 1) (ff .hoh 40000 0 40000)).refundable = 1600
-- 2019: other dependent only: $500 nonrefundable, nothing refundable.
#guard ctcFor (py 2019) (fam 0 0 1) (ff .single 30000 0 30000) = { afterPhaseout := 500 }
-- 2019: threshold $200,000 single, $400,000 joint.
#guard (ctcFor (py 2019) (fam 1) (ff .single 201000 9000 201000)).afterPhaseout = 1950
#guard (ctcFor (py 2019) (fam 1) (ff .mfj 201000 9000 201000)).afterPhaseout = 2000
-- 2021: two children, one under 6, joint MAGI $100,000: $3,600 + $3,000, all refundable.
#guard ctcFor (py 2021) (fam 2 1) (ff .mfj 100000 5000 100000) = { refundable := 6600, afterPhaseout := 6600 }
-- 2021: head of household, one child of 10, MAGI $122,500: the $1,000 increase falls by $50 × 10 = $500.
#guard (ctcFor (py 2021) (fam 1) (ff .hoh 122500 5000 122500)).afterPhaseout = 2500
-- 2021: joint $180,000, one child of 4: the $1,600 increase is gone at $182,000; at $180,000 $1,500 is lost.
#guard (ctcFor (py 2021) (fam 1 1) (ff .mfj 180000 5000 180000)).afterPhaseout = 2100
-- 2021: advance payments $1,800 on a $3,000 credit: $1,200 refundable left.
#guard (ctcFor (py 2021) (fam 1) { ff .single 40000 2000 40000 with advancePayments := 1800, advanceChildren := 1 }).refundable
  = 1200
-- 2021: advance $1,500 for a child the taxpayer cannot claim, AGI $30,000 single: fully protected by the safe harbor.
#guard (ctcFor (py 2021) (fam 0) { ff .single 30000 2000 30000 with advancePayments := 1500, advanceChildren := 1 }).excessAdvance
  = 0
-- ... at AGI $60,000 (150% of $40,000) half of the $2,000 safe harbor remains: $1,500 − $1,000 = $500 repaid.
#guard (ctcFor (py 2021) (fam 0) { ff .single 60000 2000 60000 with advancePayments := 1500, advanceChildren := 1 }).excessAdvance
  = 500
-- ... at $80,000 none: all $1,500.
#guard (ctcFor (py 2021) (fam 0) { ff .single 80000 2000 80000 with advancePayments := 1500, advanceChildren := 1 }).excessAdvance
  = 1500
end

end Legal.USTax.TaxCourt
