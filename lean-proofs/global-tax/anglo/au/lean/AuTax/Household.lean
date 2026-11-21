import AuTax.Person

/-!
# The household: family tax benefit, the Medicare levy's family reduction and surcharge

Australia assesses individuals; the family enters through the Medicare levy (family income threshold, MLA s. 8),
the surcharge's family thresholds (ss. 8C, 8D) and family tax benefit (FA Act 1999 Sch 1, on the family's adjusted
taxable income, Sch 3 cl 3). Children's ages decide FTB categories: under 13 / 13 and over for Part A (cl 7);
youngest under 5 / 5 and over for Part B (cl 30); a couple gets no Part B once the youngest has turned 13 (cl 28D).
Children aged 16-19 are taken to be full-time secondary students (FTB children; `unsupported` note); 20 and over
are not FTB children.
-/

namespace AuTax

structure Household where
  id : String
  year : Nat := 2025
  persons : List Person
  married : Bool := false
  children : List Nat := []
  /-- Grandfathered energy supplement (FA Act Sch 1 cll 6A, 25C, 29AA: only for recipients before 20 Sept 2016).
  Off by default (a new claimant); the OECD includes it. -/
  energySupplement : Bool := false
  /-- Claim Parenting Payment (Single) where entitled (Social Security Act 1991; annualised as in the OECD
  country chapter). Off by default: the contract's `benefits` are universal child benefits; the OECD includes it. -/
  incomeSupport : Bool := false
  /-- The two adults live together as a couple without being married (input `"cohabiting": true`, kernel API
  1.0.2; `"deFacto": true` is read the same). -/
  cohabiting : Bool := false
  deriving Repr, Inhabited

def sumBy {α : Type} (l : List α) (f : α → Int) : Int := l.foldl (fun a x => a + f x) 0

def ftbChildren (h : Household) : List Nat := h.children.filter (· ≤ 19)

/-- Members of a couple: married, or cohabiting as a couple. Australian law treats a de facto partner exactly as a
spouse: ITAA 1997 s. 995-1 "spouse" includes "another individual (whether of the same sex or a different sex) who
... although not legally married to the individual, lives with the individual on a genuine domestic basis in a
relationship as a couple" (applied to the Medicare levy and surcharge through MLA s. 3(4) and ITAA 1936 s. 6(1)
"spouse"), and the family assistance law's "member of a couple" (FA Act s. 3(1), adopting Social Security Act 1991
s. 4) covers a de facto relationship. Two adults who are neither are two unrelated adults; the children belong to
the first. -/
def coupled (h : Household) : Bool := h.persons.length = 2 && (h.married || h.cohabiting)

/-! ## Family tax benefit -/

structure Ftb where
  partA : Int
  partB : Int
  ati : Int
  method : String
  deriving Repr

/-! ## Parenting Payment (Single): the income-support passport

Parameters for 2024-25 as annualised in OECD, Taxing Wages 2026, country chapter "Australia (2024-2025 income tax
year)", Other transfers: maximum PP(S) AUD 26,104.20; reduced by AUD 0.40 per AUD 1 of income above AUD 5,735.60
plus AUD 639.60 for each child other than the first; Pharmaceutical Allowance AUD 176.80 "added to the maximum
basic rate ... Anyone with a PP(S) entitlement, after PA has been added, receives the full amount of PA";
Energy Supplement AUD 312; Telephone Allowance AUD 146.71; sole parents with a child under 14. (Parameters, not
the statute: the Social Security Act 1991 rate calculator is fortnightly; these are the OECD's annual sums.) -/

structure Pps where
  payment : Int
  telephone : Int
  deriving Repr

def ppsCalc (p : Params) (h : Household) (income : Int) : Pps :=
  let kids := h.children.filter (· < 14)
  if !h.incomeSupport || coupled h || kids.isEmpty || p.label ≠ "2024-25" then { payment := 0, telephone := 0 } else
  let free := 573560 + 63960 * ((kids.length : Int) - 1)
  let mx := 2610420 + 17680 + (if h.energySupplement then 31200 else 0)
  let rate := mx - pct (pos (income - free)) 4000
  if rate ≤ 0 then { payment := 0, telephone := 0 }
  else { payment := max rate 17680, telephone := 14671 }

def ftbCalc (p : Params) (h : Household) (atis : List Int) (onIncomeSupport : Bool := false) : Ftb :=
  let kids := ftbChildren h
  let n : Int := kids.length
  if kids.isEmpty then { partA := 0, partB := 0, ati := 0, method := "no FTB child" } else
  -- Sch 3 cl 3: a member of a couple's ATI includes the partner's.
  let fam := if coupled h then sumBy atis id else (atis.headD 0)
  let es := h.energySupplement
  let supp := if fam > aud p.ftbASuppLimit then 0 else n * p.ftbASuppC
  let stdA := sumBy kids fun a => if a < 13 then p.ftbAUnder13C else p.ftbA13plusC
  let esMax := if es then sumBy kids fun a => if a < 13 then p.esAUnder13C else p.esA13plusC else 0
  let maxRate := stdA + supp + esMax
  let base := n * p.ftbABaseC + supp + (if es then n * p.esABaseC else 0)
  -- cl 3 step 2 / cl 38M: 20 % of ATI above the lower income free area (cl 38N).
  -- cl 38L: a recipient of a social security pension or benefit has a nil income excess.
  -- Method 1 is a kernel `Taper`: the maximum rate withdrawn at 20 % above the lower income free area, never
  -- below the base rate (cl 3 step 4). Method 2: the base rate withdrawn at 30 % above the higher income free area.
  let m1T : TaxKernel.Taper := { full := maxRate, start := aud p.ftbALIFA, num := p.ftbATaper1, den := 10000,
                                 floor := base }
  let m1raw : TaxKernel.Taper := { m1T with floor := -1000000000 }
  let m2T : TaxKernel.Taper := { full := base, start := aud p.ftbAHIFA, num := p.ftbATaper2, den := 10000 }
  let fam' := if onIncomeSupport then 0 else fam
  let (a, meth) :=
    if fam ≤ aud p.ftbAHIFA || onIncomeSupport then (m1T.amount fam', "Method 1 (cl 3)")   -- cl 1(2)(a)
    else (pos (max (m2T.amount fam) (m1raw.amount fam)), "Method 2 (cl 25)")             -- cl 25 steps 2-4
  -- Part B (cl 29): youngest FTB child; 16-18 counted (senior secondary); couple with youngest 13+ nil (cl 28D).
  let kidsB := kids.filter (· ≤ 18)
  let youngest := kidsB.foldl min 99
  let b :=
    if kidsB.isEmpty then 0
    else if coupled h && youngest ≥ 13 then 0
    else
      let primary := if coupled h then atis.foldl max 0 else atis.headD 0
      if primary > aud p.ftbBPrimaryLimit && !onIncomeSupport then 0   -- cl 28B(1) (indexed), (2)
      else
        let mx := (if youngest < 5 then p.ftbBUnder5C else p.ftbB5plusC) + p.ftbBSuppC +
          (if es then (if youngest < 5 then p.esBUnder5C else p.esB5plusC) else 0)
        if coupled h then
          let lower := atis.foldl min (atis.headD 0)
          -- cl 29(2), cll 32-33: a kernel `Taper` on the lower earner's ATI
          ({ full := mx, start := aud p.ftbBFreeArea, num := p.ftbBTaper, den := 10000 } : TaxKernel.Taper).amount lower
        else mx
  { partA := a, partB := b, ati := fam, method := meth }

/-! ## Medicare levy (s. 8 family reduction) and surcharge (ss. 8B-8D) -/

/-- Dependent children for the levy (ITAA 1997 s. 961-5(1)(c): a child under 21, or a student under 25; here
under 21). -/
def levyChildren (h : Household) : Int := (h.children.filter (· < 21)).length

/-- The levy of every person after MLA ss. 7 and 8 (in cents), given taxable incomes `tis` and whether FTB is
payable (s. 8(6): a single person's threshold rises for a child only if FTB was payable for that child). -/
def familyLevies (p : Params) (h : Household) (tis : List Int) (ftbPayable : Bool) : List Int :=
  let base := tis.map (levyS7C p)
  let kids := levyChildren h
  let family := coupled h || (kids > 0)
  if !family then base else
  let fi := if coupled h then sumBy tis id else tis.headD 0
  let kidsCounted := if coupled h || ftbPayable then kids else 0
  let fit := aud (p.mlFamily + p.mlFamilyChild * kidsCounted)
  -- s. 8(1): the family exemption is the family's: both spouses, or, for a parent who is not coupled, the parent alone
  -- (an unrelated second adult keeps the s. 7 levy; round 12 fix: it used to be zeroed too)
  if fi ≤ fit then (if coupled h then tis.map fun _ => 0 else 0 :: base.drop 1)
  else
    -- s. 8(2): reduce by 2 % of the threshold less 8 % of the excess (in ticks, cents x bp)
    let red := pos (fit * p.mlRate - (fi - fit) * p.mlFamilyTaper)
    if red = 0 then base else
    if coupled h then
      match tis, base with
      | [t1, t2], [l1, l2] =>
        if l1 > 0 && l2 > 0 then
          -- s. 8(3): each spouse's reduction is the share of family income that is not the spouse's
          let r1 := ticksToCents (red * t1 / fi)
          let r2 := ticksToCents (red * t2 / fi)
          -- s. 8(4): an excess over one's own levy reduces the spouse's levy
          let e1 := pos (r1 - l1)
          let e2 := pos (r2 - l2)
          [pos (l1 - r1 - e2), pos (l2 - r2 - e1)]
        else if l1 > 0 then [pos (l1 - ticksToCents red), l2]
        else if l2 > 0 then [l1, pos (l2 - ticksToCents red)]
        else base
      | _, _ => base
    else
      match base with
      | l1 :: rest => pos (l1 - ticksToCents red) :: rest
      | [] => base

/-- Surcharge rate (bp) for income `isp` against tier thresholds `t1 < t2 < t3` (MLA ss. 8B(2)-(4); PHI Act
s. 22-30: a tier 2 earner's income exceeds the tier 2 threshold, ...). -/
def mlsRate (p : Params) (isp t1 t2 t3 : Int) : Int :=
  if isp > aud t3 then p.mlsRate3 else if isp > aud t2 then p.mlsRate2 else if isp > aud t1 then p.mlsRate1 else 0

/-- The tier-1 surcharge on its own is a kernel `Surcharge` with an exemption limit and no glide zone (charged on
the whole income once it exceeds the threshold): the kernel's `exempt_notch` applies (`Theorems`). -/
def mlsTier1 (p : Params) : TaxKernel.Surcharge := { rate := p.mlsRate1, exempt := p.mlsT1 }

/-- MLS of each person (cents): 8B single without dependants, 8C single with dependants (family thresholds),
8D married (combined income against family thresholds; own income above the s. 8D(3)(c) floor). Charged on
taxable income (no reportable fringe benefits here). -/
def surcharges (p : Params) (h : Household) (tis isps : List Int) : List Int :=
  let kids := levyChildren h
  let step := p.mlsChildStep * pos (kids - 1)
  let fam (t : Int) := 2 * t + step
  if coupled h then
    let comb := sumBy isps id
    let r := mlsRate p comb (fam p.mlsT1) (fam p.mlsT2) (fam p.mlsT3)
    let anyUncovered := h.persons.any (!·.privateCover)
    (tis.zip isps).map fun (t, i) =>
      if anyUncovered && i > aud p.mlsMarriedFloor then pct t r else 0
  else
    ((List.range h.persons.length).zip (h.persons.zip (tis.zip isps))).map fun (k, x, t, i) =>
      if x.privateCover then 0
      else if k = 0 && kids > 0 then pct t (mlsRate p i (fam p.mlsT1) (fam p.mlsT2) (fam p.mlsT3))
      else pct t (mlsRate p i p.mlsT1 p.mlsT2 p.mlsT3)

/-! ## Everything -/

structure PersonResult where
  taxable : Int
  frankingCredit : Int
  basicTax : Int
  lito : Int
  incomeTax : Int
  levy : Int
  surcharge : Int
  div293 : Int
  contribTax : Int
  help : Int
  broadIncome : Int
  deriving Repr

structure Result where
  persons : List PersonResult
  ftb : Ftb
  incomeTax : Int
  medicareLevy : Int
  mls : Int
  div293 : Int
  contribTax : Int
  help : Int
  benefits : Int
  pps : Pps
  deriving Repr

def compute (h : Household) : Result :=
  let p := paramsFor h.year
  let tis := h.persons.map (taxableIncomeC p)
  let broad := h.persons.map (broadIncomeC p)
  -- PP(S) income test on the parent's ordinary income (here: assessable income before deductions, in cents)
  let pps := ppsCalc p h (assessableC p (h.persons.headD default))
  let ftb := ftbCalc p h broad (pps.payment > 0)
  let levies := familyLevies p h tis (ftb.partA + ftb.partB > 0)
  let mls := surcharges p h tis broad
  let rs := (h.persons.zip (tis.zip (levies.zip (mls.zip broad)))).map fun (x, ti, lv, ms, bi) =>
    let bt := basicTaxC p ti
    let lo := litoC p ti + lmitoC p ti
    let fc := frankingCreditC (pos x.dividends) x.frankingRate
    -- ITAA 1997 s. 63-10: LITO (non-refundable) first; franking offset refundable (s. 67-25), applied last.
    let it := pos (bt - lo) - fc
    { taxable := ti, frankingCredit := fc, basicTax := bt, lito := min lo bt, incomeTax := it, levy := lv,
      surcharge := ms, div293 := div293C p x, contribTax := contribTaxC p x,
      help := if x.helpDebt then helpRepaymentC p bi else 0, broadIncome := bi : PersonResult }
  { persons := rs, ftb := ftb,
    incomeTax := sumBy rs (·.incomeTax), medicareLevy := sumBy rs (·.levy), mls := sumBy rs (·.surcharge),
    div293 := sumBy rs (·.div293), contribTax := sumBy rs (·.contribTax), help := sumBy rs (·.help),
    benefits := ftb.partA + ftb.partB + pps.payment + pps.telephone, pps := pps }

/-- The household's burden used by the searches: income tax (after refundable offsets) + Medicare levy + MLS +
Division 293 + the fund's contributions tax + HELP repayment (if any) - FTB. -/
def burden (r : Result) : Int := r.incomeTax + r.medicareLevy + r.mls + r.div293 + r.contribTax + r.help - r.benefits

end AuTax
