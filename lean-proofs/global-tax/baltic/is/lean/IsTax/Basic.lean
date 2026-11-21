import IsTax.Params

/-!
# Iceland (Reykjavík), income year 2025: the assessment (álagning) of a household

Composition (lög nr. 90/2003 um tekjuskatt unless said otherwise):
* earned income less the mandatory 4 % pension contribution, voluntary séreign (≤ 4 %) and gifts to registered
  charities (30. gr. A 4., 5., 7. tölul.) = tekjuskattsstofn (61. gr. 1. og 3. tölul.) = útsvarsstofn;
* state tax: three bands (66. gr. 1. mgr. 1.–3. tölul.; kernel `Schedule`), for joint filers with the transfer of
  top-band income into the middle band (4. tölul.);
* útsvar: Reykjavík 14,97 % of the same base (lög nr. 4/1995, 23. gr.);
* persónuafsláttur (67. gr. A): first against own state tax, then own útsvar, then the spouse's state tax and útsvar,
  then 22/31 of what is left against capital income tax, the rest lapses (a non-refundable, ordered credit: kernel
  `usedCredit`, `applyCreditsOrdered` pattern);
* capital income tax 22 % (66. gr. 3. mgr.) after the 300.000 kr. exemption per person and the 50 % rent exemption;
  spouses' capital income counted with the spouse with the higher net income (62. gr. 1. mgr. 2. tölul.);
* útvarpsgjald and gjald í Framkvæmdasjóð aldraðra: flat levies above an income floor;
* barnabætur (68. gr. A, brbákv. LXXXII): kernel `Taper`-shaped withdrawal, reported as `benefits`.
Rounding: each amount to the nearest whole króna, halves up. The statute states no rule; RSK's own calculators
(reiknivelarws.rsk.is) round this way: barnabætur reductions 9.927,92 → 9.928 and 86.129,76 → 86.130, withholding
148.634,75 → 148.635 (validation/bb_out.jsonl, st_out.jsonl), and the OECD's 2.383.127 for 2.383.126,84 agrees.
-/

namespace IsTax
open TaxKernel

/-- Options: the statute's own choices (Reykjavík, the amounts of income year 2025) by default; the OECD's
conventions (average útsvar, levies at the álagning-2025 amounts) and counterfactuals for the scanners. -/
structure Opts where
  utsvar : Int := utsvarReykjavik
  levies : Levies := levies2025
  bandTransfer : Bool := true
  creditTransfer : Bool := true
  forceSeparate : Bool := false
  /-- apply the 22/31 rule also to a single person's unused credit (Skatturinn's reading; FINDINGS F9) -/
  capCreditSingles : Bool := true
  /-- the income year's parameters (round 5) -/
  yp : YearP := yp2025
  deriving Repr

/-- One adult's earned-income side. -/
structure Person where
  age : Nat
  /-- wages + self-employment (reiknað endurgjald and business profit) + pension income -/
  earned : Int
  /-- iðgjaldsstofn: wages + self-employment -/
  iBase : Int
  /-- voluntary séreign contribution claimed -/
  sereign : Int := 0
  /-- gifts to charities on the almannaheillaskrá -/
  gifts : Int := 0
  deriving Repr

/-- 30. gr. A 4./5. tölul.: the mandatory 4 % (lög nr. 129/1997, 2. gr.: the employee's share of the 15,5 %). -/
def mandPension (p : Person) : Int := divR .halfUp (pensionRate * pos p.iBase) BP
/-- 30. gr. A 4./5. tölul., 2. málsl.: voluntary séreign up to 4 % of the same base. -/
def sereignDed (p : Person) : Int := min (pos p.sereign) (sereignMaxRate * pos p.iBase / BP)
/-- 30. gr. A 7. tölul.: nothing below 10.000 kr. in the year, at most 350.000 kr. -/
def giftDed (g : Int) : Int := if g < giftMin then 0 else min g giftMax
/-- Tekjuskattsstofn of earned income (61. gr. 1. og 3. tölul.); also the útsvarsstofn. -/
def taxable (p : Person) : Int := pos (p.earned - mandPension p - sereignDed p - giftDed p.gifts)

/-- 66. gr. 1. mgr. 1.–3. tölul. -/
def stateTax (ti : Int) : Int := stateSched.tax Rule.unitHalfUp ti

/-- 66. gr. 1. mgr. 4. tölul.: income of the higher spouse above T3 taxed at 23,05 % instead of 31,35 %, up to half
of the lower spouse's distance to T3, never more than the cap. -/
def bandShift (hi lo : Int) : Int := min (pos (hi - T3)) (min (pos (T3 - lo) / 2) bandTransferCap)

/-- The higher spouse's state tax after the transfer. -/
def stateTaxShifted (hi lo : Int) : Int :=
  Rule.unitHalfUp.ofTicks (stateSched.ticks hi - (rate3 - rate2) * bandShift hi lo)

/-- State tax of a jointly taxed couple (first, second). -/
def stateTaxPair (bt : Bool) (a b : Int) : Int × Int :=
  if !bt then (stateTax a, stateTax b)
  else if b ≤ a then (stateTaxShifted a b, stateTax b) else (stateTax a, stateTaxShifted b a)

/-- The levies reported in the `...A25` detail lines (read by the OECD-convention map): for 2025 the álagning-2025
amounts the OECD uses; for 2022-2024 the year's own statutory levies (the OECD's 2022-2024 rows use the following
assessment's amounts, which is the statute). -/
def aLev (o : Opts) : Levies := if o.yp.year < 2025 then o.yp.levies else leviesAssess2025

/-- The same with the year's parameters (`YearP`, round 5). -/
def stateTaxY (q : YearP) (ti : Int) : Int := q.sched.tax Rule.unitHalfUp ti
def bandShiftY (q : YearP) (hi lo : Int) : Int := min (pos (hi - q.t3)) (min (pos (q.t3 - lo) / 2) q.cap)
def stateTaxShiftedY (q : YearP) (hi lo : Int) : Int :=
  Rule.unitHalfUp.ofTicks (q.sched.ticks hi - (q.r3 - q.r2) * bandShiftY q hi lo)
def stateTaxPairY (q : YearP) (bt : Bool) (a b : Int) : Int × Int :=
  if !bt then (stateTaxY q a, stateTaxY q b)
  else if b ≤ a then (stateTaxShiftedY q a b, stateTaxY q b) else (stateTaxY q a, stateTaxShiftedY q b a)

/-- Útsvar on the útsvarsstofn. -/
def utsvarOf (rate ti : Int) : Int := divR .halfUp (rate * pos ti) BP

/-- 67. gr. A 2. mgr.: a credit `c` used first against state tax `st`, then against útsvar `ut`. -/
structure CreditUse where
  state : Int
  utsvar : Int
  left : Int
  deriving Repr

def useCredit (c st ut : Int) : CreditUse :=
  let s := usedCredit st c
  let r := pos c - s
  let u := usedCredit ut r
  ⟨s, u, r - u⟩

/-- Credits of a joint couple: each uses its own; then what one has left is added to the other's credit
("óráðstöfuðum persónuafslætti annars makans bætt við persónuafslátt hins") against the other's remaining state tax
and útsvar. Result: (A, B, left over for capital income tax). -/
def coupleCredits (transfer : Bool) (cA cB stA stB utA utB : Int) : CreditUse × CreditUse × Int :=
  let a := useCredit cA stA utA
  let b := useCredit cB stB utB
  if !transfer then (a, b, a.left + b.left) else
  let a2 := useCredit b.left (stA - a.state) (utA - a.utsvar)
  let b2 := useCredit a.left (stB - b.state) (utB - b.utsvar)
  (⟨a.state + a2.state, a.utsvar + a2.utsvar, 0⟩, ⟨b.state + b2.state, b.utsvar + b2.utsvar, 0⟩, a2.left + b2.left)

/-- Capital income of one taxpayer (a single person or a jointly taxed couple). -/
structure Capital where
  interest : Int := 0
  dividends : Int := 0
  gains : Int := 0
  rent : Int := 0
  divListed : Bool := true
  gainsListed : Bool := true
  deriving Repr

/-- 66. gr. 3. mgr.: the exemption, used on interest first, then listed dividends, then listed gains. -/
def capExemptUsed (k : Capital) (exemption : Int) : Int :=
  min (pos exemption) (pos k.interest + (if k.divListed then pos k.dividends else 0)
    + (if k.gainsListed then pos k.gains else 0))

/-- 50 % of residential rent is exempt; the taxable half (rounded in the taxpayer's favour). -/
def rentTaxable (r : Int) : Int := pos r - rentExemptBp * pos r / BP

/-- The capital income tax base (fjármagnstekjuskattsstofn). -/
def capBase (k : Capital) (exemption : Int) : Int :=
  pos k.interest + pos k.dividends + pos k.gains + rentTaxable k.rent - capExemptUsed k exemption

def capTaxOf (base : Int) : Int := divR .halfUp (capRate * pos base) BP

/-- 67. gr. A 2. mgr.: 22/31 of the credit left over pays capital income tax. -/
def capCredit (left capTax : Int) : Int := min (pos capTax) (capCreditNum * pos left / capCreditDen)

/-- A flat levy due at or above the floor, for ages 16–69 at the end of the income year. -/
def levyDue (amt floor : Int) (age : Nat) (inc : Int) : Int :=
  if 16 ≤ age ∧ age ≤ 69 ∧ floor ≤ inc then amt else 0

/-- Barnabætur: the 4 % reduction of income above the threshold, to the nearest króna (RSK calculator). -/
def bbReduce (excess : Int) : Int := divR .halfUp (bbPct * pos excess) 100
/-- The under-7 supplement's reduction: 4 % per child under 7 of the same excess, rounded once (RSK calculator:
2 × 52.480,52 → 104.961, not 2 × 52.481). -/
def bbReduce7 (m : Nat) (excess : Int) : Int := divR .halfUp (bbPct * m * pos excess) 100

/-- Barnabætur before the 5.000 kr. per-carer rule: n children under 18, m of them under 7. -/
def bbGross (couple : Bool) (n m : Nat) (inc : Int) : Int :=
  let start := if couple then bbStartCouple else bbStartSingle
  let per := if couple then bbCouple else bbSingle
  let red := bbReduce (inc - start)
  if n = 0 then 0 else pos (per * n - red) + pos (bbUnder7 * m - bbReduce7 m (inc - start))

/-- 68. gr. A 7. mgr.: each carer's half (couples, 1. mgr.: "skiptast barnabætur milli þeirra til helminga") below
5.000 kr. lapses. -/
def barnabaetur (couple : Bool) (n m : Nat) (inc : Int) : Int :=
  let g := bbGross couple n m inc
  if couple then
    (if half1 g < bbMinPerCarer then 0 else half1 g) + (if half2 g < bbMinPerCarer then 0 else half2 g)
  else if g < bbMinPerCarer then 0 else g

/-- Barnabætur with the year's amounts (2022-2024, round 6); same structure as `bbGross`/`barnabaetur`, with the
reduction percent by number of children (`bbPct1..3`). -/
def bbGrossY (q : YearP) (couple : Bool) (n m : Nat) (inc : Int) : Int :=
  let start := if couple then q.bbStartCouple else q.bbStartSingle
  let per := if couple then q.bbCouple else q.bbSingle
  let pct := if n ≥ 3 then q.bbPct3 else if n = 2 then q.bbPct2 else q.bbPct1
  let red := divR .halfUp (pct * pos (inc - start)) 100
  if n = 0 then 0 else pos (per * n - red) + pos (q.bbUnder7 * m - bbReduce7 m (inc - start))

def barnabaeturY (q : YearP) (couple : Bool) (n m : Nat) (inc : Int) : Int :=
  let g := bbGrossY q couple n m inc
  if couple then
    (if half1 g < bbMinPerCarer then 0 else half1 g) + (if half2 g < bbMinPerCarer then 0 else half2 g)
  else if g < bbMinPerCarer then 0 else g

/-- Everything computed for one adult. -/
structure PersonResult where
  ti : Int
  stateGross : Int
  stateNoTransfer : Int
  utsvarGross : Int
  utsvarAvg : Int
  credit : CreditUse
  capShare : Int
  utvarp : Int
  aldradra : Int
  utvarpA25 : Int
  aldradraA25 : Int
  deriving Repr

/-- Result of one tax unit (a single person, or a jointly taxed couple). -/
structure UnitResult where
  persons : List PersonResult
  capBase : Int
  capTaxGross : Int
  capCredit : Int
  creditLapsed : Int
  bandShift : Int
  deriving Repr

def personsTotal (f : PersonResult → Int) (l : List PersonResult) : Int := sumInts (l.map f)

/-- A single taxpayer (alone, or one of two separately taxed adults). -/
def singleUnit (o : Opts) (p : Person) (k : Capital) : UnitResult :=
  let ti := taxable p
  let st := stateTaxY o.yp ti
  let ut := utsvarOf o.utsvar ti
  let cr := if 16 ≤ p.age then o.yp.pers else 0
  let u := useCredit cr st ut
  let cb := capBase k capExemption
  let ct := capTaxOf cb
  let cc := if o.capCreditSingles then capCredit u.left ct else 0
  let lev := ti + cb
  let pr : PersonResult :=
    { ti := ti, stateGross := st, stateNoTransfer := st, utsvarGross := ut,
      utsvarAvg := utsvarOf o.yp.utsvarAvg ti, credit := u, capShare := cb,
      utvarp := levyDue o.levies.utvarp o.levies.floor p.age lev,
      aldradra := levyDue o.levies.aldradra o.levies.floor p.age lev,
      utvarpA25 := levyDue (aLev o).utvarp (aLev o).floor p.age lev,
      aldradraA25 := levyDue (aLev o).aldradra (aLev o).floor p.age lev }
  { persons := [pr], capBase := cb, capTaxGross := ct, capCredit := cc,
    creditLapsed := u.left - min u.left (ceilDiv (cc * capCreditDen) capCreditNum),
    bandShift := 0 }

/-- A jointly taxed couple (62. gr.): capital pooled with two exemptions, band transfer, credit transfer. -/
def jointUnit (o : Opts) (pa pb : Person) (k : Capital) : UnitResult :=
  let ta := taxable pa
  let tb := taxable pb
  let (sa, sb) := stateTaxPairY o.yp o.bandTransfer ta tb
  let ua := utsvarOf o.utsvar ta
  let ub := utsvarOf o.utsvar tb
  let ca := if 16 ≤ pa.age then o.yp.pers else 0
  let cb' := if 16 ≤ pb.age then o.yp.pers else 0
  let (cra, crb, left) := coupleCredits o.creditTransfer ca cb' sa sb ua ub
  let cbase := capBase k (2 * capExemption)
  let ct := capTaxOf cbase
  let cc := capCredit left ct
  let levA := ta + half1 cbase
  let levB := tb + half2 cbase
  let mk (p : Person) (ti st ut : Int) (cu : CreditUse) (cs lev : Int) : PersonResult :=
    { ti := ti, stateGross := st, stateNoTransfer := stateTaxY o.yp ti, utsvarGross := ut,
      utsvarAvg := utsvarOf o.yp.utsvarAvg ti, credit := cu, capShare := cs,
      utvarp := levyDue o.levies.utvarp o.levies.floor p.age lev,
      aldradra := levyDue o.levies.aldradra o.levies.floor p.age lev,
      utvarpA25 := levyDue (aLev o).utvarp (aLev o).floor p.age lev,
      aldradraA25 := levyDue (aLev o).aldradra (aLev o).floor p.age lev }
  let shift := if !o.bandTransfer then 0 else if tb ≤ ta then bandShiftY o.yp ta tb else bandShiftY o.yp tb ta
  { persons := [mk pa ta sa ua cra (half1 cbase) levA, mk pb tb sb ub crb (half2 cbase) levB],
    capBase := cbase, capTaxGross := ct, capCredit := cc,
    creditLapsed := left - min left (ceilDiv (cc * capCreditDen) capCreditNum), bandShift := shift }

/-- Read the options from the command line and the household line. -/
def optsOf (args : List String) (c : Canon) : Opts :=
  let avg := args.contains "--average-utsvar" || c.str? "region" == some "average"
  let a25 := args.contains "--levies-assessment-2025" || c.str? "levies" == some "assessment2025"
  let q := yearP c.year
  { utsvar := if avg then q.utsvarAvg else q.utsvarRvk,
    levies := if a25 then leviesAssess2025 else q.levies,
    yp := q,
    bandTransfer := !(args.contains "--no-band-transfer" || c.bool? "noBandTransfer" == some true),
    creditTransfer := !(args.contains "--no-credit-transfer" || c.bool? "noCreditTransfer" == some true),
    forceSeparate := args.contains "--separate" || c.bool? "separate" == some true,
    capCreditSingles := !(args.contains "--literal-67A" || c.bool? "literal67A" == some true) }

def personOf (a : Adult) (sereign gifts : Int) : Person :=
  { age := a.age, earned := a.wages + a.selfEmployment + a.pension, iBase := a.wages + a.selfEmployment,
    sereign, gifts }

/-- Withholding (staðgreiðsla) of one month, for the RSK calculator check: 4 % pension and séreign `serBp` off the
wage, the 2025 withholding bands, less the monthly credit share `pct` % of the person's own and `spct` % of the
spouse's 68.691 kr., rounded once to the nearest króna (as RSK's calculator: 326.425,575 − 34.345,5 → 292.080). -/
def withholdMonth (wage serBp pct spct : Int) : Int × Int × Int :=
  -- RSK's calculator keeps decimals: base in 1/10.000 kr., tax in 1/10^8 kr., one rounding at the end
  let base4 := pos wage * (BP - pensionRate - serBp)
  let sched4 := Schedule.ofList [(0, 3149), (wM1 * BP, 3799), (wM3 * BP, 4629)]
  let tax8 := sched4.ticks base4
  let cr8 := persCreditMonth * (pct + spct) * 1000000
  (base4 / BP, divR .halfUp tax8 (BP * BP), divR .halfUp (pos (tax8 - cr8)) (BP * BP))

def unsupportedList : List String :=
  ["vaxtabætur and sérstakur vaxtastuðningur (housing interest relief; need debts and assets)",
   "children's own income (6 % above 180.000 kr., 66. gr. 2. mgr.)",
   "losses carried forward, business deductions (31. gr.), the 2.000.000 kr. home-stay rule",
   "barnabætur on the birth year and partial-year residence (shared residence: input sharedResidence, one parent per line)",
   "joint taxation chosen by cohabitants is assumed whenever `cohabiting` is set (it never costs: Theorems)"]

/-- The household. -/
def compute (args : List String) (c : Canon) : Out :=
  if c.str? "mode" == some "stadgreidsla" then
    let (base, tax, w) := withholdMonth ((c.int? "monthlyWage").getD 0) ((c.int? "sereignBp").getD 0)
      ((c.int? "creditPct").getD 100) ((c.int? "spouseCreditPct").getD 0)
    Out.make c "IS" "ISK" w (detail := [Out.d "base" base, Out.d "taxBeforeCredit" tax, Out.d "withheld" w])
  else
  let o := optsOf args c
  let cohab := (c.bool? "cohabiting").getD false
  let coupleHH := c.isCouple && (c.married || cohab)
  let joint := coupleHH && !o.forceSeparate
  let unlisted := (c.bool? "closelyHeld").getD false || (c.bool? "dividendsUnlisted").getD false
  let gUnlisted := (c.bool? "gainsUnlisted").getD false
  let a1 := c.adult1
  let ser1 := min (pos c.pensionContributions) (sereignMaxRate * pos a1.earnings / BP)
  let ser2 := pos c.pensionContributions - ser1
  let g1 := if c.isCouple then min (pos c.charitable) giftMax else pos c.charitable
  let g2 := pos c.charitable - g1
  let capAll : Capital :=
    { interest := c.interest, dividends := c.dividends, gains := c.capitalGains,
      rent := c.rentalIncome, divListed := !unlisted, gainsListed := !gUnlisted }
  let half (f : Int → Int) : Capital :=
    { capAll with
      interest := f c.interest, dividends := f c.dividends,
      gains := f c.capitalGains, rent := f c.rentalIncome }
  let units : List UnitResult :=
    match c.adult2? with
    | none => [singleUnit o (personOf a1 ser1 g1) capAll]
    | some a2 =>
      if joint then [jointUnit o (personOf a1 ser1 g1) (personOf a2 ser2 g2) capAll]
      else [singleUnit o (personOf a1 ser1 g1) (half half1), singleUnit o (personOf a2 ser2 g2) (half half2)]
  let ps := units.flatMap (·.persons)
  let stTot := personsTotal (·.stateGross) ps
  let crState := personsTotal (·.credit.state) ps
  let crUt := personsTotal (·.credit.utsvar) ps
  let utTot := personsTotal (·.utsvarGross) ps
  let capTax := sumInts (units.map (·.capTaxGross))
  let capCr := sumInts (units.map (·.capCredit))
  let incomeTax := stTot - crState + capTax - capCr
  let localTax := utTot - crUt
  let utv := personsTotal (·.utvarp) ps
  let ald := personsTotal (·.aldradra) ps
  -- barnabætur (68. gr. A): income = earned base + gross capital income of the carers
  let n := c.childrenUnder 18
  let m := c.childrenUnder 7
  let bbCoupleHH := coupleHH
  let earnBase (p : Person) : Int := pos (p.earned - mandPension p - sereignDed p - giftDed p.gifts)
  let capGross := pos c.interest + pos c.dividends + pos c.capitalGains + pos c.rentalIncome
  let bbInc := match c.adult2? with
    | some a2 => if bbCoupleHH then earnBase (personOf a1 ser1 g1) + earnBase (personOf a2 ser2 g2) + capGross
                 else earnBase (personOf a1 ser1 g1) + half1 capGross
    | none => earnBase (personOf a1 ser1 g1) + capGross
  -- 68. gr. A 1. mgr. (L. 28/2021): with a registered shared residence (skipt búseta) each parent's barnabætur are
  -- computed by his own family status and income "og takmarkast við helming af útreiknuðum barnabótum"
  let shared := (c.bool? "sharedResidence").getD false && !bbCoupleHH
  let bb := if shared then
      (let h := divR .halfUp (bbGross false n m bbInc) 2; if h < bbMinPerCarer then 0 else h)
    else if c.year < 2025 then barnabaeturY o.yp bbCoupleHH n m bbInc else barnabaetur bbCoupleHH n m bbInc
  let pens := sumInts (c.adults.map fun a => pensionRate * pos a.earnings / BP)
  Out.make c "IS" "ISK" incomeTax (surtaxes := [("utvarpsgjald", utv)]) (localIncomeTax := localTax)
    (employeeSocial := ald) (benefits := bb)
    (detail := [Out.d "taxableIncome" (personsTotal (·.ti) ps), Out.d "taxBeforeCredits" stTot,
      Out.d "stateTaxNoBandTransfer" (personsTotal (·.stateNoTransfer) ps),
      Out.d "bandShift" (sumInts (units.map (·.bandShift))),
      Out.d "creditUsedState" crState, Out.d "creditUsedUtsvar" crUt,
      Out.d "creditToCapitalTax" capCr, Out.d "creditLapsed" (sumInts (units.map (·.creditLapsed))),
      Out.d "utsvarGross" utTot, Out.d "utsvarGrossAvg1494" (personsTotal (·.utsvarAvg) ps),
      Out.d "capitalBase" (sumInts (units.map (·.capBase))), Out.d "capitalTaxGross" capTax,
      Out.d "utvarpsgjald" utv, Out.d "framkvaemdasjodurAldradra" ald,
      Out.d "utvarpsgjaldAssess2025" (personsTotal (·.utvarpA25) ps),
      Out.d "aldradraAssess2025" (personsTotal (·.aldradraA25) ps),
      Out.d "pensionMandatory4pct" pens, Out.d "barnabaeturIncome" bbInc,
      Out.d "barnabaeturGross" (bbGross bbCoupleHH n m bbInc),
      Out.dBool "joint" joint, Out.dStr "utsvarRate" (if o.utsvar == utsvarReykjavik then "14.97" else "14.94"),
      Out.dStr "note" "Reykjavik 2025; levies of income year 2025 (assessed 2026); employeeSocial = gjald i Framkvaemdasjod aldradra (as the OECD); the 4 % pension contribution is a deduction, not a tax"])
    (unsupported := unsupportedList ++ (if c.year < 2025 then ["income years 2022-2024: Reykjavík útsvar 2022 (14,52 %) not sourced; "
      ++ "withholding detail and barnabaeturGross detail use 2025"] else []))

def country : Country :=
  { code := "IS", name := "Iceland (Reykjavík)", currency := "ISK", year := "2025",
    compute := compute [], computeWith := compute }

end IsTax
