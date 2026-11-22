import CaTax.Model

/-!
# The canonical household under Canadian (federal + Ontario) law, 2025

Mapping (conventions, stated once):
* Two adults are spouses when `married` is true or when the optional field `cohabiting` is true: ITA s. 248(1)
  "common-law partner" (a person who cohabits with the taxpayer in a conjugal relationship for a continuous
  12 months, or is a parent of the taxpayer's child and cohabits with the taxpayer) is treated as a spouse
  throughout the Act (s. 252(4) family terms; ss. 118, 122.5, 122.6, 122.7 "cohabiting spouse or common-law
  partner"); the Taxation Act, 2007 uses the federal definitions. Otherwise each adult is assessed alone and the first
  adult is the parent of the children.
* Investment income (interest, eligible dividends, capital gains, rent) is split equally between spouses (the
  contract's convention); pension contributions are RRSP contributions, split equally, each spouse deducting up to
  their own limit (earned income of the year stands in for the prior year's).
* `pension` is a life annuity from a registered pension plan: eligible pension income at any age (s. 118(7)) and
  eligible for splitting (s. 60.03, not applied by default: `--split-pension`).
* Gifts are claimed by the spouse with the higher taxable income (CRA allows either spouse to claim both).
* Benefits are those of the payment period whose base taxation year is the household's year (ITA s. 122.6: July of
  the next year to June of the year after; round 7: before, July of the same year was used, which pairs this year's
  income with the amounts of the period based on the previous year's income) with the household's income as the
  base-year income (`benefits` = CCB + Ontario child benefit + GST/HST credit + Ontario
  sales tax credit). The Canada workers benefit is a refundable federal credit for 2025 (in `incomeTax`).
* The Ontario Health Premium is reported as a surtax (`OntarioHealthPremium`); the OECD books it as an employee
  social contribution "payable on taxable income".
-/

namespace CaTax
open TaxKernel Lean

/-- Children under 18 (CCB "qualified dependant", s. 122.6). -/
def kids (c : Canon) : List Nat := (c.children.map (·.age)).filter (· < 18)

/-- ITA s. 122.61(1): CCB for one year of the payment period, on adjusted family net income `afni`. -/
def ccb (ages : List Nat) (afni : Int) (y : YP := y2025) : Int :=
  let n := ages.length
  let e := y.ccbUnder6 * ((ages.filter (· < 6)).length : Int) + y.ccb6to17 * ((ages.filter (6 ≤ ·)).length : Int)
  let q := if afni ≤ y.ccbT1 then 0
    else if afni ≤ y.ccbT2 then pct (ccbRate1 n) (afni - y.ccbT1)
    else y.ccbFixed2 n + pct (ccbRate2 n) (afni - y.ccbT2)
  pos (e - q)

/-- OTA s. 104(5): Ontario child benefit, 12 months. -/
def ocb (n : Nat) (afni : Int) (y : YP := y2025) : Int := pos (12 * y.ocbPerChildMonthly * (n : Int) - pct ocbRate (pos (afni - y.ocbThreshold)))

/-- ITA s. 122.5(3)-shaped formula A − B for the GST/HST credit and its one-off variants, 12 months: adult amount
for the individual and the qualified relation or eligible dependant, `child` for each other dependant, `supp` for a
single parent, and for a single person without dependants the lesser of `supp` and `suppRate` of income over
`phaseIn`; reduced by `outRate` of adjusted income over `thr`. -/
def gstFormula (adult child supp phaseIn suppRate thr outRate : Int) (single : Bool) (n : Nat) (ownIncome afni : Int) : Int :=
  let a := adult
    + (if !single then adult else if n > 0 then adult else 0)
    + child * ((if single && n > 0 then n - 1 else n : Nat) : Int)
    + (if single && n > 0 then supp else 0)
    + (if single && n = 0 then min supp (pct suppRate (pos (ownIncome - phaseIn))) else 0)
  pos (a - pct outRate (pos (afni - thr)))

/-- ITA s. 122.5(3): GST/HST credit, 12 months (`single` = no qualified relation; `ownIncome` for the single
supplement); plus, for base taxation year 2024 (`y.gstTopUp`), the January 2026 one-time amount of s. 122.5(3.004)
(4.4): 0.25 × (A − B) − C with $1,047 / $552, 6 % over $11,337, 15 % over $45,521, C = the regular January payment
(one quarter of the year's s. 122.5(3) amount); a negative result is taken as nil. -/
def gstCredit (single : Bool) (n : Nat) (ownIncome afni : Int) (y : YP := y2025) : Int :=
  let reg := gstFormula y.gstAdult y.gstChild y.gstSingleSupp y.gstSuppPhaseIn gstSuppRate y.gstThreshold gstOutRate
    single n ownIncome afni
  let top := if y.gstTopUp then
      pos (divR .halfUp (gstFormula (dol 1047) (dol 552) (dol 552) (dol 11337) 600 (dol 45521) 1500 single n ownIncome afni) 4
        - divR .halfUp reg 4)
    else 0
  reg + top

/-- OTA s. 104.11: Ontario sales tax credit, 12 months. -/
def ostc (persons : Nat) (singleNoKids : Bool) (afni : Int) (y : YP := y2025) : Int :=
  pos (y.ostcPerPerson * (persons : Int) - pct ostcRate (pos (afni - (if singleNoKids then y.ostcThresholdSingle else y.ostcThresholdFamily))))

/-- ITA s. 122.7(2): Canada workers benefit of a family (`wi` working incomes, `ani` adjusted net incomes). Adults
under 19 at the end of the year are not eligible (s. 122.7(1) "eligible individual"). -/
def cwb (family : Bool) (wi ani : List Int) (y : YP := y2025) : Int :=
  let wTot := sumInts wi
  let aTot := if family && wi.length = 2 then
      -- s. 122.7(1.3): the spouse with the lower working income deducts the lesser of it and $16,386
      let w1 := wi.headD 0
      let w2 := wi.getD 1 0
      let a1 := ani.headD 0
      let a2 := ani.getD 1 0
      if w1 < w2 then pos (a1 - min (pos w1) y.cwbSecondaryExemption) + a2
      else a1 + pos (a2 - min (pos w2) y.cwbSecondaryExemption)
    else sumInts ani
  let a := min (if family then y.cwbMaxFamily else y.cwbMaxSingle) (pct cwbInRate (pos (wTot - cwbWorkThreshold)))
  let b := pct cwbOutRate (pos (aTot - (if family then y.cwbOutFamily else y.cwbOutSingle)))
  pos (a - b)

/-- s. 60.03 pension income splitting: up to half of eligible pension income moved to the spouse. -/
structure Options where
  splitPension : Bool := false
  deriving Repr, Inhabited

structure PersonOut where
  p : Person
  inc : Income
  fed : FedResult
  on : OnResult
  deriving Inhabited

structure HouseholdOut where
  persons : List PersonOut
  fedTax : Int
  cwb : Int
  onTax : Int
  ohp : Int
  social : Int
  ccb : Int
  ocb : Int
  gst : Int
  ostc : Int
  afni : Int
  deriving Inhabited

/-- Optional extra input `wagesCents` (one number per adult): wages in cents, for the OECD check whose average wage
is not a whole number of dollars. -/
def wagesCents (c : Canon) : List (Option Int) :=
  match c.raw.getObjVal? "wagesCents" with
  | .ok (.arr a) => a.toList.map fun j => match j with
    | .num n => some (n.mantissa / ((10 : Int) ^ n.exponent))
    | _ => none
  | _ => []

/-- Optional extra inputs `investmentShare1` / `rrspShare1` (basis points, 0 to 10000): the share of the household's
investment income / RRSP contributions held by the first adult (default: equal split, the contract's convention).
Used by the allocation searches; the law attributes income to whoever owns the capital (ITA s. 74.1). -/
def share1 (c : Canon) (k : String) : Option Int := (c.int? k).map fun v => max 0 (min 10000 v)

/-- Spouses or common-law partners (ITA s. 248(1) "common-law partner"; kernel input field `cohabiting`). -/
def isSpouses (c : Canon) : Bool :=
  c.adults.length = 2 && (c.married || (c.bool? "cohabiting").getD false)

def toPersons (c : Canon) (o : Options) : List Person :=
  let n := c.adults.length
  let wc := wagesCents c
  let si := share1 c "investmentShare1"
  let sr := share1 c "rrspShare1"
  let split (s : Option Int) (x : Int) (i : Nat) : Int :=
    match s with
    | some b => let a := divR .halfUp (x * b) 10000; if i = 0 then a else x - a
    | none => if i = 0 then half1 x else half2 x
  let sh (x : Int) (i : Nat) : Int := if n = 2 then split si x i else x
  let shr (x : Int) (i : Nat) : Int := if n = 2 then split sr x i else x
  let ps := (c.adults.zipIdx).map fun (a, i) =>
    { age := a.age, wages := ((wc.getD i none).getD (dol a.wages)), se := dol a.selfEmployment, pension := dol a.pension,
      interest := dol (sh c.interest i), dividends := dol (sh c.dividends i),
      capitalGains := dol (sh c.capitalGains i), rent := dol (sh c.rentalIncome i),
      rrsp := dol (shr c.pensionContributions i) : Person }
  if o.splitPension && isSpouses c then
    match ps with
    | [a, b] =>
      -- move half of the larger pension to the spouse when it lowers the gap (s. 60.03(1) "split-pension amount")
      if a.pension > b.pension then
        let m := min (a.pension / 2) (pos ((a.pension - b.pension) / 2))
        [{ a with pension := a.pension - m }, { b with pension := b.pension + m }]
      else
        let m := min (b.pension / 2) (pos ((b.pension - a.pension) / 2))
        [{ a with pension := a.pension + m }, { b with pension := b.pension - m }]
    | l => l
  else ps

def household (c : Canon) (o : Options := {}) : HouseholdOut :=
  let y := ypFor c.year
  -- benefits: the payment period whose base taxation year is this income year (ITA s. 122.6)
  let yb := benefitParams c.year
  let ps := toPersons c o
  let incs := ps.map fun p => income p y
  let spouses := isSpouses c
  let ks := kids c
  let nk := ks.length
  let nets := incs.map (·.net)
  let familyNet := if spouses then sumInts nets else nets.headD 0
  -- who claims gifts and the Ontario dependant reduction: the spouse with the higher net income (s. 20(2))
  let hiIdx : Nat := if spouses && (nets.getD 1 0) > (nets.headD 0) then 1 else 0
  let fams : List Family := (List.range ps.length).map fun i =>
    { spouseNet := if spouses then some (nets.getD (1 - i) 0) else none
      eligibleDependant := !spouses && i = 0 && nk > 0
      onDependants := if i = hiIdx then nk else 0
      familyNet := if spouses then familyNet else nets.getD i 0
      gifts := if i = hiIdx then dol c.charitable else 0 }
  let rows := ((ps.zip incs).zip fams).map fun ((p, inc), f) =>
    ({ p, inc, fed := fedTax p inc f y, on := onTax p inc f y } : PersonOut)
  -- family benefits on adjusted family net income (s. 122.6 "adjusted income")
  let afni := if spouses then familyNet else nets.headD 0
  let ccbV := ccb ks afni yb
  let ocbV := if nk > 0 then ocb nk afni yb else 0
  let gstV := if spouses then gstCredit false nk 0 afni yb
    else sumInts ((List.range ps.length).map fun i =>
      gstCredit true (if i = 0 then nk else 0) (nets.getD i 0) (nets.getD i 0) yb)
  let ostcV := if spouses then ostc (2 + nk) false afni yb
    else sumInts ((List.range ps.length).map fun i =>
      let k := if i = 0 then nk else 0
      ostc (1 + k) (k = 0) (nets.getD i 0) yb)
  let wis := ps.map fun p => pos p.wages + p.se
  let elig : List Bool := ps.map fun p => decide (19 ≤ p.age)
  let cwbV := if spouses then cwb true wis nets y
    else sumInts ((List.range ps.length).map fun i =>
      if elig.getD i true then cwb (i = 0 && nk > 0) [wis.getD i 0] [nets.getD i 0] y else 0)
  { persons := rows, fedTax := sumInts (rows.map (·.fed.tax)), cwb := cwbV,
    onTax := sumInts (rows.map (·.on.tax)), ohp := sumInts (rows.map (·.on.ohp)),
    social := sumInts (incs.map (·.social.total)), ccb := ccbV, ocb := ocbV, gst := gstV, ostc := ostcV, afni }

/-- Cents to whole dollars, half up (contract fields are whole units; `detail` keeps cents). -/
def toDollars (x : Int) : Int := divR .halfUp x 100

def personDetail (r : PersonOut) : Json :=
  Json.mkObj [
    ("age", Lean.toJson r.p.age),
    ("totalIncomeCents", Lean.toJson r.inc.total), ("netIncomeCents", Lean.toJson r.inc.net),
    ("taxableIncomeCents", Lean.toJson r.inc.taxable), ("grossUpCents", Lean.toJson r.inc.grossUp),
    ("taxableCapitalGainsCents", Lean.toJson r.inc.taxableGains), ("rrspDeductedCents", Lean.toJson r.inc.rrspDeducted),
    ("cppBaseCents", Lean.toJson r.inc.social.base), ("cppEnhancedCents", Lean.toJson r.inc.social.enhanced),
    ("cppSelfEmployedCents", Lean.toJson r.inc.social.seTotal), ("eiCents", Lean.toJson r.inc.social.ei),
    ("fedBasicTaxCents", Lean.toJson r.fed.basicTax), ("bpaCents", Lean.toJson r.fed.bpa),
    ("fedSpouseOrDependantAmountCents", Lean.toJson r.fed.spouseAmount), ("ceaCents", Lean.toJson r.fed.cea),
    ("fedCreditAmountsCents", Lean.toJson r.fed.creditAmounts), ("fedNrtcCents", Lean.toJson r.fed.nrtc),
    ("fedGiftCreditCents", Lean.toJson r.fed.giftCredit), ("fedDtcCents", Lean.toJson r.fed.dtc),
    ("fedTaxCents", Lean.toJson r.fed.tax),
    ("onBasicTaxCents", Lean.toJson r.on.basicTax), ("onNrtcCents", Lean.toJson r.on.nrtc),
    ("onSurtaxCents", Lean.toJson r.on.surtax), ("onDtcCents", Lean.toJson r.on.dtc),
    ("onTaxReductionCents", Lean.toJson r.on.reduction), ("onLiftCents", Lean.toJson r.on.lift),
    ("onTaxCents", Lean.toJson r.on.tax), ("onHealthPremiumCents", Lean.toJson r.on.ohp)]

def out (o : Options) (c : Canon) : Out :=
  let h := household c o
  let incomeTaxC := h.fedTax - h.cwb
  let benefitsC := h.ccb + h.ocb + h.gst + h.ostc
  let big := (c.capitalGains > 0 || c.dividends > 0) &&
    sumInts (h.persons.map (·.inc.taxable)) > dol 173205
  Out.make c "CA" "CAD" (toDollars incomeTaxC) (surtaxes := [("OntarioHealthPremium", toDollars h.ohp)])
    (localIncomeTax := toDollars h.onTax) (employeeSocial := toDollars h.social) (benefits := toDollars benefitsC)
    (detail := [Out.dStr "taxYear" s!"{(ypFor c.year).year} (calendar); benefits for July {(benefitParams c.year).year} to June {(benefitParams c.year).year + 1} (base taxation year {c.year})",
      Out.dStr "region" "Ontario",
      Out.d "fedTaxCents" h.fedTax, Out.d "cwbCents" h.cwb, Out.d "onTaxCents" h.onTax,
      Out.d "onHealthPremiumCents" h.ohp, Out.d "cppEiCents" h.social,
      Out.d "ccbCents" h.ccb, Out.d "ocbCents" h.ocb, Out.d "gstCreditCents" h.gst, Out.d "ostcCents" h.ostc,
      Out.d "afniCents" h.afni, Out.d "incomeTaxCents" incomeTaxC, Out.d "benefitsCents" benefitsC,
      Out.dBool "pensionSplit" o.splitPension,
      ("persons", Json.arr (h.persons.map personDetail).toArray)])
    (unsupported := ["alternative minimum tax (ITA Division E.1)" ++ (if big then ": may apply to this household" else ""),
      "Ontario energy and property tax credit (rent/property tax not in the household)",
      "Canada child benefit monthly rounding and the $20 lump-sum rule",
      "provinces other than Ontario"]
      ++ (if c.year < 2025 then ["RRSP dollar limit: the 2025 amount ($32,490) is used for this year"] else [])
      ++ (if c.year < 2022 || c.year > 2025 then [s!"tax year {c.year} not modelled: computed with the {(ypFor c.year).year} parameters"] else []))

def country : Country :=
  { code := "CA", name := "Canada (federal + Ontario)", currency := "CAD", year := "2025",
    compute := out {}, computeWith := fun args c => out { splitPension := args.contains "--split-pension" } c }

end CaTax

namespace CaTax
open TaxKernel

/-- Net income of the household in cents (contract: gross − taxes − contributions + benefits), unrounded. -/
def netCents (c : Canon) (o : Options := {}) : Int :=
  let h := household c o
  dol c.gross - (h.fedTax - h.cwb) - h.onTax - h.ohp - h.social + (h.ccb + h.ocb + h.gst + h.ostc)

end CaTax
