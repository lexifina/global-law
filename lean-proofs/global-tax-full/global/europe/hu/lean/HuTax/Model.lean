import HuTax.Params

/-!
# Hungary 2025: the computation

Annual model of the personal income tax return (Szja tv.) with the 2025 base-reducing allowances in the statutory
order (§ 29/H (1): mothers of four or more / of three, [CSED-GYED, not modelled], under 25, under-30 mothers,
personal (disabled), first marriage, family), the family allowance pooled between spouses or partners
(§ 29/B (1a)-(1b): "közösen" / "megosztás"), the unused family allowance turned into the family contribution allowance
against the 18.5 % TB contribution (Tbj. § 34), separately taxed capital income (Szja tv. §§ 65-67: 15 %) with the
13 % szocho paid by the individual (Szocho tv. § 1 (5), § 2 (2) ceiling), flat-rate (átalány) sole traders
(Szja tv. § 50, 1. sz. melléklet 4.48.) and KATA (Kata tv.) as options, and családi pótlék (Cst. § 11) as benefits.
-/

namespace HuTax
open TaxKernel

/-- Whole forints, half up: NAV 73 examples round 15 % × 20 010 = 3 001.5 to 3 002 and 15 % × 66 670 = 10 000.5
to 10 001. -/
def pct (rate x : Int) : Int := divR .halfUp (rate * x) BP

/-- § 29/A (2): the per-beneficiary monthly amount for `deps` dependants (three or more: the last entry). -/
def famRate (tbl : List Int) (deps : Nat) : Int :=
  if deps = 0 then 0 else tbl.getD (deps - 1) (tbl.getLastD 0)

/-- One month's family allowance: `bens` beneficiaries at the rate for `deps` dependants (§ 29/A (2), (4)-(5)) plus
the § 29/A (2a) supplement for each long-term ill / disabled beneficiary. -/
def famMonth (tbl : List Int) (supp : Int) (deps bens disabled : Nat) : Int :=
  famRate tbl (max deps bens) * bens + supp * disabled

/-- A month of 2025 (1-12) uses the old table before July (2024. évi LV. törvény 4. § (1), in force 2025.VII.1). -/
def famMonth2025 (m : Nat) (deps bens disabled : Nat) : Int :=
  if m ≤ 6 then famMonth famH1 famDisabledH1 deps bens disabled
  else famMonth famH2 famDisabledH2 deps bens disabled

/-- The year's family allowance (the "keret") from a list of months `(month, dependants, beneficiaries, disabled)`. -/
def famFrameMonths : List (Nat × Nat × Nat × Nat) → Int
  | [] => 0
  | (m, d, b, x) :: rest => famMonth2025 m d b x + famFrameMonths rest

/-- The same household all year: 6 months at the old and 6 at the new amounts. -/
def famFrame (deps bens disabled : Nat) : Int :=
  monthsH1 * famMonth famH1 famDisabledH1 deps bens disabled
    + monthsH2 * famMonth famH2 famDisabledH2 deps bens disabled

/-- The same household all year, for tax year `year`: 2025 as `famFrame`; 2022-2024 twelve months at the § 29/A (2)
amounts in force then (`Params.earliestYear`). -/
def famFrameYear (year : Nat) (deps bens disabled : Nat) : Int :=
  (12 - monthsAtNewAmounts year) * famMonth famH1 famDisabledH1 deps bens disabled
    + monthsAtNewAmounts year * famMonth famH2 famDisabledH2 deps bens disabled

theorem famFrameYear_2025 (deps bens disabled : Nat) :
    famFrameYear 2025 deps bens disabled = famFrame deps bens disabled := by
  simp [famFrameYear, famFrame, monthsAtNewAmounts, monthsH1, monthsH2]

/-- Szja tv. § 29/B (6): annual frame less the contribution allowance used during the year × 667 %. -/
def frameAfterInYearCredit (frame inYearCredit : Int) : Int :=
  pos (frame - divR .halfUp (famContribGrossUpBp * inYearCredit) BP)

/-- Szja tv. § 29/F (3): months of the under-25 allowance: every month before the 25th birthday "utoljára a 25.
életéve betöltésének hónapja". `age` is the age reached in 2025; `birthMonth` 1-12. -/
def youthMonths (age birthMonth : Nat) : Nat :=
  if age ≤ 24 then 12 else if age = 25 then min 12 birthMonth else 0

/-- § 29/F (2): the under-25 allowance = qualifying income, at most months × 656 785. -/
def youthAllowance (months : Nat) (qualifying : Int) : Int :=
  min (pos qualifying) ((months : Int) * youthCapMonthly)

/-- The same with the cap of tax year `y` (`youthCapFor`). -/
def youthAllowanceY (y : Nat) (months : Nat) (qualifying : Int) : Int :=
  min (pos qualifying) ((months : Int) * youthCapFor y)

/-- The flat-rate (átalány) income: revenue less the cost ratio (Szja tv. § 53). -/
def atalanyIncome (revenue costBp : Int) : Int := revenue - divR .down (costBp * revenue) BP

/-- Its taxable part: above the tax-free half of the annual minimum wage (1. sz. melléklet 4.48.). -/
def atalanyTaxable (income : Int) : Int := pos (income - atalanyFree)
/-- The same for tax year `y` (`atalanyFreeFor`). -/
def atalanyTaxableY (y : Nat) (income : Int) : Int := pos (income - atalanyFreeFor y)

/-- One adult's inputs. -/
structure Person where
  age : Nat := 40
  wages : Int := 0
  /-- átalány income (after the flat cost ratio, before the tax-free part) -/
  atalany : Int := 0
  skilled : Bool := false
  rental : Int := 0
  disabled : Bool := false
  birthMonth : Nat := 7
  /-- § 29/D: mother of four or more (all year) -/
  mother4 : Bool := false
  /-- 2025. évi XV. tv.: mother of three (income from 1 October 2025) -/
  mother3 : Bool := false
  /-- qualifying income earned after 30 September (default: a quarter of the year's qualifying income) -/
  q4 : Int := -1
  /-- § 29/G: months of the under-30 mothers' allowance -/
  u30Months : Nat := 0
  /-- qualifying income accounted to the under-25 months (§ 29/F (2): "a jogosultsági hónapokban megszerzett ...
  a jogosultsági hónapokra elszámolt"); default: pro rata by months (even monthly pay) -/
  youthIncome : Int := -1
  /-- the same for the under-30 mothers' months (§ 29/G (3)) -/
  u30Income : Int := -1
  /-- a pensioner in their own right: no TB on wages (Tbj. § 6 (1): "kiegészítő tevékenységet folytató") -/
  pensioner : Bool := false
  kata : Bool := false
  kataRevenue : Int := 0
  kataMonths : Nat := 12
  interest : Int := 0
  dividends : Int := 0
  gains : Int := 0
  /-- tax year (minimum-wage-based amounts, `minWageFor`) -/
  year : Nat := 2025
  /-- months of at least 36-hour-a-week employment (`huFullTimeMonths`; -1 = the convention of `notFullTimeShare`) -/
  ftMonths : Int := -1
  deriving Repr, Inhabited

/-- Stage 1 of one person's return: the consolidated base and the allowances that come before the family allowance. -/
structure Stage1 where
  atTaxable : Int
  base : Int
  mothers : Int
  youth : Int
  u30 : Int
  personal : Int
  /-- base left after them -/
  rest : Int
  deriving Repr, Inhabited

def stage1 (p : Person) : Stage1 :=
  let atT := if p.kata then 0 else atalanyTaxableY p.year p.atalany
  let wages := p.wages
  let qual := pos (wages + atT)
  let base := pos (wages + atT + p.rental)
  -- § 29/D / 2025. évi XV. tv. 1. § (2): no ceiling
  let mothers := if p.mother4 then qual
    else if p.mother3 then min qual (if p.q4 < 0 then divR .halfUp qual 4 else p.q4) else 0
  let ym := youthMonths p.age p.birthMonth
  let yq := if p.youthIncome ≥ 0 then min p.youthIncome (qual - mothers) else divR .down ((qual - mothers) * ym) 12
  let youth := youthAllowanceY p.year ym yq
  let uq := if p.u30Income ≥ 0 then min p.u30Income (qual - mothers - youth)
    else min (qual - mothers - youth) (divR .down (qual * p.u30Months) 12)
  let u30 := min (pos uq) ((p.u30Months : Int) * under30CapMonthly)
  let personal := if p.disabled then min (pos (base - mothers - youth - u30)) (12 * personalMonthlyFor p.year) else 0
  { atTaxable := atT, base, mothers, youth, u30, personal,
    rest := pos (base - mothers - youth - u30 - personal) }

/-- Fill the bases in order with an amount; returns what each takes. -/
def fillOrder : List Int → Int → List Int
  | [], _ => []
  | b :: bs, amt => let t := min (pos b) (pos amt); t :: fillOrder bs (amt - t)

/-- The part of a minimum base that applies (Tbj. § 42 (2)-(3) and Szocho tv. § 9 (5), monotonicity fix 2026-11-21).
Tbj. § 42 (2): the sole trader's TB base is the income actually earned (no minimum base) "ha a) az egyéni vállalkozó
... legalább heti 36 órás foglalkoztatással járó munkaviszonyban is áll"; (3) hours of concurrent employments are added.
Szocho tv. § 9 (5): the szocho minimum base leaves out "a hónapnak azt a napját, amelyen ... az egyéni vállalkozó
legalább heti 36 órás foglalkoztatással járó munkaviszonyban áll". So the minimum bases apply for the days without
36-hour employment. The contract has no working hours. **Declared convention**: with `huFullTimeMonths` (0-12) the
minimum bases apply to the other months; without it, the wages are taken to be full-time employment for
wages / minimum wage months (the minimum wage is the monthly pay for full-time work, so a full-time job pays at least that), so wages of 12 x the year's
minimum wage or more give no minimum base (as before) and smaller wages reduce it pro rata. Before this fix any wage
at all (1 forint) removed both minimum bases. -/
def notFullTimeShare (p : Person) (floor : Int) : Int :=
  if p.ftMonths ≥ 0 then divR .halfUp (floor * (12 - min 12 p.ftMonths)) 12
  else
    let w12 := 12 * minWageFor p.year
    divR .halfUp (floor * (w12 - min w12 (pos p.wages))) w12

/-- TB contribution base of a person (wages + the taxable átalány income, at least the minimum wage for a
main-occupation sole trader), and the part the family contribution allowance may reduce (Tbj. § 34 (6) and NAV 73
§ 10: not the part paid only because of a minimum base). -/
def tbBase (p : Person) (s : Stage1) : Int × Int :=
  if p.pensioner then (0, 0)
  else
    let main := p.atalany > 0 && !p.kata
    let floor := if main then notFullTimeShare p (tbMinYearFor p.year p.skilled) else 0
    (p.wages + max s.atTaxable floor, p.wages + s.atTaxable)

/-- Szocho paid by a sole trader on their own átalány income (min. 112.5 % of the minimum wage if main occupation). -/
def szochoSelf (p : Person) (s : Stage1) : Int :=
  if p.pensioner || p.kata || p.atalany ≤ 0 then 0
  else
    let floor := notFullTimeShare p (szochoMinYearFor p.year p.skilled)
    pct szochoRate (max s.atTaxable floor)

/- Hand checks of the convention (2025, minimum wage 290 800, 12 x = 3 489 600): no wages -> the whole TB floor;
wages 1 744 800 (6 months' minimum wage) -> half; 4 000 000 -> none; 3 declared full-time months -> 9/12. The scan's
household (wages 42 277): 3 489 600 x (3 489 600 - 42 277) / 3 489 600 = 3 447 323. -/
private def hp (w : Int) (m : Int := -1) : Person := { (default : Person) with wages := w, ftMonths := m, year := 2025 }
#guard notFullTimeShare (hp 0) 3489600 = 3489600
#guard notFullTimeShare (hp 1744800) 3489600 = 1744800
#guard notFullTimeShare (hp 4000000) 3489600 = 0
#guard notFullTimeShare (hp 4000000 3) 1200 = 900
#guard notFullTimeShare (hp 42277) (tbMinYearFor 2025 false) = 3447323

/-- KATA: 50 000 a month plus 40 % above 1.5 million revenue per month of liability. -/
def kataTax (p : Person) : Int :=
  if p.kata then kataMonthly * p.kataMonths + pct kataExcessRate (pos (p.kataRevenue - kataRevenuePerMonth * p.kataMonths))
  else 0

/-- Szja on separately taxed capital income (§§ 65-67: 15 %) and the individual's szocho: interest uncapped
(Szocho tv. § 1 (5) f)), dividends and gains only until wages + self-employed base + these reach 24 × minimum wage
(§ 2 (2)). -/
def capitalSzja (p : Person) : Int := pct pitRate (p.interest + p.dividends + p.gains)
def capitalSzocho (p : Person) (s : Stage1) : Int :=
  let used := p.wages + (if p.atalany > 0 then s.atTaxable else 0)
  let room := pos (szochoCapitalCeilingFor p.year - used)
  (if interestSzochoFor p.year then pct szochoRate p.interest else 0) + pct szochoRate (min (pos (p.dividends + p.gains)) room)

/-- The household-level inputs. -/
structure House where
  persons : List Person
  /-- the adults are spouses or partners sharing a household (§ 29/B (1a)-(1b)) -/
  couple : Bool
  deps : Nat
  bens : Nat
  disabledKids : Nat
  /-- months of the first-marriage allowance in 2025 (§ 29/C (4)) -/
  firstMarriageMonths : Nat := 0
  /-- frame override (sum of months), e.g. from `famFrameMonths` -/
  frame : Option Int := none
  /-- months of családi pótlék (Cst.) -/
  cspMonths : Nat := 12
  /-- the family contribution allowance already used during the year (§ 29/B (6)) -/
  inYearCredit : Int := 0
  /-- tax year (2022-2025; `famFrameYear`) -/
  year : Nat := 2025
  /-- `--eurostat` (convention, Eurostat earn_net ESMS 3.4: tax parameters "refer to the beginning of the fiscal year,
  i.e. changes occurring later during the year are ignored"): the § 29/A (2) amounts in force on 1 January for all 12
  months -/
  startOfYear : Bool := false
  deriving Repr, Inhabited

structure Result where
  stages : List Stage1
  firstMarriage : List Int
  family : List Int
  frame : Int
  taxable : List Int
  szja : List Int
  tbGross : List Int
  famCredit : List Int
  tb : List Int
  szochoSelf : List Int
  kata : List Int
  capSzja : List Int
  capSzocho : List Int
  csp : Int
  deriving Repr

/-- Családi pótlék per year: per beneficiary child, the Cst. § 11 amount for the number counted, couple or lone parent. -/
def csp (couple : Bool) (deps bens months : Nat) : Int :=
  (months : Int) * famRate (if couple then cspCouple else cspSingle) (max deps bens) * bens

def compute (h : House) : Result :=
  let st := h.persons.map stage1
  let eligible : List Bool := (List.range h.persons.length).map fun i => i = 0 || h.couple
  let rests := st.map (·.rest)
  -- first marriage (§ 29/C (5): shared as the spouses decide; filled in order)
  let fmFrame := if h.couple then (h.firstMarriageMonths : Int) * firstMarriageMonthly else 0
  let fm := fillOrder rests fmFrame
  let rests2 := List.zipWith (· - ·) rests fm
  -- family allowance: only entitled persons (adult 0, and the partner when a couple)
  let frame0 := (h.frame.getD (if h.startOfYear then 12 * famMonth famH1 famDisabledH1 h.deps h.bens h.disabledKids
    else famFrameYear h.year h.deps h.bens h.disabledKids))
  let frame := frameAfterInYearCredit frame0 h.inYearCredit
  let famBases := List.zipWith (fun b e => if e then b else 0) rests2 eligible
  let fam := fillOrder famBases frame
  let unused := pos (frame - sumInts fam)
  let taxable := List.zipWith (· - ·) rests2 fam
  let szja := taxable.map (pct pitRate)
  let bases := List.zipWith tbBase h.persons st
  let tbGross := bases.map (fun b => pct tbRate b.1)
  -- family contribution allowance: 15 % of the unused frame, at most the TB on actual income (Tbj. § 34 (3), (6))
  let caps := List.zipWith (fun b e => if e then pct tbRate b.2 else 0) bases eligible
  let fc := fillOrder caps (pct famContribRate unused)
  let tb := List.zipWith (· - ·) tbGross fc
  { stages := st, firstMarriage := fm, family := fam, frame, taxable, szja, tbGross, famCredit := fc, tb,
    szochoSelf := List.zipWith szochoSelf h.persons st, kata := h.persons.map kataTax,
    capSzja := h.persons.map capitalSzja, capSzocho := List.zipWith capitalSzocho h.persons st,
    csp := csp h.couple h.deps h.bens h.cspMonths }

/-- Net burden of the household (taxes and contributions less benefits). -/
def Result.burden (r : Result) : Int :=
  sumInts r.szja + sumInts r.tb + sumInts r.szochoSelf + sumInts r.kata + sumInts r.capSzja + sumInts r.capSzocho - r.csp

end HuTax
