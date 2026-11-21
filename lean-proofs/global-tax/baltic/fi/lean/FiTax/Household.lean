import FiTax.Years

/-!
# Finland 2025: the household (individual assessment; what still links spouses) and the contract output

Finland taxes each person separately (no joint filing). What links spouses ("puolisot", TVL 7 §: married, or
cohabiting with a common child) in this model: the child increase of the deficit-credit maximum goes to the spouse
with the larger state tax on earned income (TVL 131 § 1 mom), the unused part of one spouse's maximum raises the
other's (131 § 2 mom), and an unused deficit credit is deducted from the spouse's taxes on request (134 §; assumed
requested). The work-credit child increase is doubled only for a sole guardian who has no spouse (125 § 4 mom).
Investment income of a couple is split half and half (contract); unlisted-company dividends (extension field
`fiUnlistedDividends`, with the shares' net asset value `fiNetAssets`) belong to adult 1.
The lapsilisä (Lapsilisälaki) is a benefit of the family, with the single-parent supplement for one adult.
-/

namespace FiTax
open TaxKernel Lean

/-- A JSON number in cents, half up. -/
def numCents (n : JsonNumber) : Int :=
  let d : Int := (10 : Int) ^ n.exponent
  (2 * n.mantissa * 100 + d) / (2 * d)

/-- A numeric field of a JSON object in cents (`dflt` if absent). -/
def centsField (j : Json) (k : String) (dflt : Int) : Int :=
  match j.getObjVal? k with
  | .ok (.num n) => numCents n
  | _ => dflt

def rawAdults (c : Canon) : List Json :=
  match c.raw.getObjVal? "adults" with
  | .ok (.arr a) => a.toList
  | _ => []

/-- Adult `i`'s field `k` in cents: from the raw line when present (keeps the cents), else 100 × the parsed unit. -/
def adultCents (c : Canon) (i : Nat) (k : String) (dflt : Int) : Int :=
  match (rawAdults c)[i]? with
  | some j => centsField j k (100 * dflt)
  | none => 100 * dflt

def topCents (c : Canon) (k : String) (dflt : Int) : Int := centsField c.raw k (100 * dflt)

/-- Spouses in the sense of TVL 7 §: married, or cohabiting with a (common) child. -/
def spouses (c : Canon) : Bool :=
  c.adults.length == 2 && (c.married || ((c.bool? "cohabiting").getD false && !c.children.isEmpty))

def minors (c : Canon) : Nat := (c.children.filter (fun k => k.age < 18)).length

/-- TVL 33 b §: unlisted dividends `d` on shares with net asset value `na` → (capital-income part, earned part). -/
def unlistedSplit (d na : Int) : Int × Int :=
  let ret := divR .down (unlistedReturnRate * pos na) BP
  let within := min (pos d) ret
  let cap := pctOf unlistedCapitalPart (min within unlistedLimit)
    + pctOf unlistedCapitalPartAbove (pos (within - unlistedLimit))
  (cap, pctOf unlistedEarnedPart (pos (pos d - within)))

/-- Net capital income of the household (cents): interest + 85 % of listed dividends + gains + rent. -/
def householdCapital (c : Canon) : Int :=
  topCents c "interest" c.interest + pctOf listedDividendTaxable (topCents c "dividends" c.dividends)
    + topCents c "capitalGains" c.capitalGains + topCents c "rentalIncome" c.rentalIncome

/-- The persons of a household. -/
def persons (c : Canon) : List Person :=
  let n := c.adults.length
  let cap := householdCapital c
  let (uc, ue) := unlistedSplit (topCents c "fiUnlistedDividends" 0) (topCents c "fiNetAssets" 0)
  let kids := minors c
  let sole := n == 1
  let yel := (c.bool? "fiYel").getD false
  (List.range n).zip c.adults |>.map fun (i, a) =>
    { age := a.age, wages := adultCents c i "wages" a.wages, selfEmp := adultCents c i "selfEmployment" a.selfEmployment,
      pension := adultCents c i "pension" a.pension,
      earnedDiv := if i = 0 then ue else 0,
      capital := (if n = 1 then cap else if i = 0 then half1 cap else half2 cap) + (if i = 0 then uc else 0),
      kids := kids, sole := sole, yel := yel && i = 0 }

/-- One person without a spouse: the deficit credit against their own taxes. -/
def finishAlone (st : Stage) (p : Person) (inc : Int) : Result :=
  let (cr, _) := deficitCredit p inc
  let (t, lost) := applyDeficit st.afterWork cr
  { st, final := t, capitalTax := st.capitalTax, deficitUsed := cr - lost, deficitLost := lost }

/-- Two spouses: 131 § 1 mom (child increase to the larger state tax), 131 § 2 mom (unused maximum), 134 § (transfer
of the unused credit). -/
def finishCouple (sa sb : Stage) (pa pb : Person) (n : Nat) : Result × Result :=
  let inc := deficitChildInc n
  let aGets := sa.afterWork.state ≥ sb.afterWork.state
  let incA := if aGets then inc else 0
  let incB := if aGets then 0 else inc
  let (ca0, shA) := deficitCredit pa incA
  let (cb0, shB) := deficitCredit pb incB
  let roomA := pos (deficitMax + incA - shA)
  let roomB := pos (deficitMax + incB - shB)
  let ca := if shA > deficitMax + incA then min shA (deficitMax + incA + roomB) else ca0
  let cb := if shB > deficitMax + incB then min shB (deficitMax + incB + roomA) else cb0
  let (ta, la) := applyDeficit sa.afterWork ca
  let (tb, lb) := applyDeficit sb.afterWork cb
  let (tb2, la2) := applyDeficit tb la
  let (ta2, lb2) := applyDeficit ta lb
  ({ st := sa, final := ta2, capitalTax := sa.capitalTax, deficitUsed := ca - la2, deficitLost := la2 },
   { st := sb, final := tb2, capitalTax := sb.capitalTax, deficitUsed := cb - lb2, deficitLost := lb2 })

/-- All persons' results. -/
def results (r : Rates) (c : Canon) : List Result :=
  let ps := persons c
  let sts := match ypFor c.year with
    | some q => ps.map (stageY q r)
    | none => ps.map (stage r)
  match ps, sts with
  | [pa, pb], [sa, sb] =>
    if spouses c then
      let (ra, rb) := finishCouple sa sb pa pb (minors c)
      [ra, rb]
    else [finishAlone sa pa (deficitChildInc (minors c)), finishAlone sb pb 0]
  | _, _ => (ps.zip sts).map fun (p, s) => finishAlone s p (deficitChildInc (minors c))

/-- Insertion sort, oldest first (structural, so `decide` can evaluate it). -/
def insertDesc (a : Nat) : List Nat → List Nat
  | [] => [a]
  | b :: t => if a ≥ b then a :: b :: t else b :: insertDesc a t

def sortDesc : List Nat → List Nat
  | [] => []
  | a :: t => insertDesc a (sortDesc t)

/-- Lapsilisä per month (cents): children under 17, the oldest counted first, the under-3 increase and the
single-parent supplement. -/
def childBenefitMonth (ages : List Nat) (single : Bool) : Int :=
  let elig := sortDesc (ages.filter (· < childBenefitAgeLimit))
  let rec go : List Nat → Nat → Int
    | [], _ => 0
    | a :: rest, i =>
      childBenefitBase i + (if a < 3 then childBenefitUnder3 else 0) + (if single then childBenefitSingle else 0)
        + go rest (i + 1)
  go elig 0

def childBenefit (c : Canon) : Int :=
  match ypFor c.year with
  | some q =>
    -- the year's single-parent supplement and the months with the under-3 increase (round 8)
    let elig := sortDesc ((c.children.map (·.age)).filter (· < childBenefitAgeLimit))
    let single := c.adults.length == 1
    let rec go : List Nat → Nat → Int
      | [], _ => 0
      | a :: rest, i =>
        q.cbMonths * childBenefitBase i + (if a < 3 then (q.under3Months : Int) * childBenefitUnder3 else 0)
          + (if single then q.cbMonths * q.cbSingle else 0) + go rest (i + 1)
    go elig 0
  | none => 12 * childBenefitMonth (c.children.map (·.age)) (c.adults.length == 1)

def sumBy (l : List Result) (f : Result → Int) : Int := l.foldl (fun a x => a + f x) 0

/-- Cents → whole euros, half up (the contract's unit). -/
def toEur (x : Int) : Int := divR .halfUp x 100

/-- The rates of a household: Helsinki by default; `municipalRateBp` / `churchRateBp` override. -/
def ratesOf (c : Canon) : Rates :=
  { municipal := (c.int? "municipalRateBp").getD (match ypFor c.year with | some q => q.helsinki | none => helsinkiRate),
    church := (c.int? "churchRateBp").getD 0 }

def personJson (x : Result) : Json :=
  Json.mkObj [("netEarnedCents", toJson x.st.netEarned), ("contributionsCents", toJson x.st.contributions),
    ("pensionDeductionCents", toJson x.st.pensionDed), ("basicDeductionCents", toJson x.st.basicDed),
    ("taxableEarnedCents", toJson x.st.taxable), ("stateTaxBeforeCreditsCents", toJson x.st.stateBefore),
    ("workCreditCents", toJson x.st.workCredit), ("stateTaxCents", toJson x.final.state),
    ("municipalTaxCents", toJson x.final.municipal), ("medicalCents", toJson x.final.medical),
    ("churchTaxCents", toJson x.final.church), ("capitalTaxCents", toJson x.capitalTax),
    ("yleCents", toJson x.st.yle), ("deficitCreditUsedCents", toJson x.deficitUsed),
    ("deficitCreditLostCents", toJson x.deficitLost)]

/-- The four OECD lines at the national average municipal rate (7,54 %, no church tax), in cents. -/
def oecdLines (c : Canon) : List (String × Json) :=
  let avg := match ypFor c.year with | some q => q.average | none => averageMunicipalRate
  let rs := results { municipal := avg, church := 0 } c
  [("oecd754_CGITFP_cents", toJson (sumBy rs Result.stateTotal + sumBy rs (·.st.yle))),
   ("oecd754_SLT_cents", toJson (sumBy rs Result.local)),
   ("oecd754_EECSSC_cents", toJson (sumBy rs Result.employee))]

def out (c : Canon) : Out :=
  let r := ratesOf c
  let rs := results r c
  let cb := childBenefit c
  Out.make c "FI" "EUR" (toEur (sumBy rs Result.stateTotal))
    (surtaxes := [("yleisradiovero", toEur (sumBy rs (·.st.yle)))])
    (localIncomeTax := toEur (sumBy rs Result.local))
    (employeeSocial := toEur (sumBy rs Result.employee))
    (benefits := toEur cb)
    (detail := [Out.d "taxableIncome" (toEur (sumBy rs (·.st.taxable))),
      Out.d "taxBeforeCredits" (toEur (sumBy rs (·.st.stateBefore))),
      Out.d "taxableIncomeCents" (sumBy rs (·.st.taxable)),
      Out.d "taxBeforeCreditsCents" (sumBy rs (·.st.stateBefore)),
      Out.d "workCreditCents" (sumBy rs (·.st.workCredit)),
      Out.d "childBenefitCents" cb,
      Out.d "municipalRateBp" r.municipal, Out.d "churchRateBp" r.church,
      Out.dBool "spouses" (spouses c),
      ("persons", Json.arr (rs.map personJson).toArray)] ++ oecdLines c)
    (unsupported := (if (ypFor c.year).isSome then ["tax years 2022-2024: the eläketulovähennys (TVL 100 §; in 2022 also the separate "
        ++ "state and municipal pension deductions) and the deficit credit's first-home increase (131 §, until 2024) "
        ++ "follow the 2025 rules; capital income tax (124 § 2 mom, 785/2012) and eläketulon lisävero (124 § 4 mom, "
        ++ "1510/2016) are the same wording in all four years"] else []) ++ (if c.adults.any (fun a => a.selfEmployment ≠ 0) then
        ["selfEmployment: taxed as earned income from work; YEL contributions and the business-income split are not modelled"]
      else []) ++
      (if c.charitable ≠ 0 || c.pensionContributions ≠ 0 then
        ["charitable / pensionContributions: not deductible in this model (TVL 98 a § gifts to universities only)"]
      else []))

end FiTax
