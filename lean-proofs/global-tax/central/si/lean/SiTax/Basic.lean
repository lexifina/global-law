import TaxKernel
import SiTax.Params
import SiTax.Years

/-!
# Slovenia 2025: dohodnina (ZDoh-2), employee contributions, otroški dodatek

Individual assessment (spouses file separately). Per person: annual base (čl. 109) = wages less the employee's
contributions (čl. 41(1)) + pension less the pensioner's contributions (čl. 41(3)) + s.p. profit (actual expenses)
less own contributions; minus the allowances of čl. 111-115 (čl. 119(1)) = net annual base; tax by čl. 122;
pension credit 13,5 % (čl. 112(3), (7)). Capital income, rent and s.p. income on flat-rate expenses are taxed
separately and finally (čl. 131.a, 132, 135.a, 135.č). Dependants' allowances for the same child go to one
parent, the other gets "le morebitna razlika do celotne višine olajšave" (čl. 114(10)); parents choose who claims
(default: the cheapest split, `"siChildClaim": 0 | 1` forces one parent first).

Optional input fields: per adult `siNormRevenue` (s.p. revenue on flat-rate expenses, čl. 48(3), 59) and
`siNormFullTime` (default true); household `siHoldingYears` (capital gains holding period, default 0),
`siChildClaim`, `siLoneParent` (default: one adult with children), `cohabiting` (kernel field; a cohabiting couple
is a couple: FURS guide 8.4 "zunajzakonski partner"), `siChildrenInSchool` (children 18-25 count as dependants).
-/

namespace SiTax
open TaxKernel Lean

/-- `x` times `bp` basis points, rounded half up to the cent. -/
def pct (x bp : Int) : Int := divR .halfUp (x * bp) BP

/-- Cents to whole euros (half up) for the output. -/
def toEur (c : Int) : Int := divR .halfUp c CENT

structure Person where
  age : Nat := 40
  wages : Int := 0
  se : Int := 0
  pension : Int := 0
  normRev : Int := 0
  normFull : Bool := true
  /-- capital income shares (cents): interest, dividends, gains, rent -/
  interest : Int := 0
  dividends : Int := 0
  gains : Int := 0
  rent : Int := 0
  /-- tax year (2022-2025, `Years.yp`) -/
  year : Nat := 2025
  /-- `--eurostat`: contributions at the 1 January parameters (`ypStart2025`) -/
  startOfYear : Bool := false
  /-- `--euromod`: parameters in force on 30 June (`ypJune2025`) -/
  june30 : Bool := false
  deriving Repr, Inhabited

/-- ZDoh-2 čl. 59 (ZDoh-2AB): flat-rate expenses. -/
def normExpenses (full : Bool) (r : Int) : Int :=
  if full then pct (min (pos r) normFullCap) 8000
  else pct (min (pos r) normPartCap1) 8000 + pct (overlap 0 r normPartCap1 normPartCap2) 4000

/-- ZDoh-2 čl. 59 by tax year (round 8, PISRS NPB copies in `improve-central/refs/si/zdoh2/`):
* 2022 (NPB 31, ZDoh-2 incl. ZDoh-2Z, Ur. l. RS 39/22): "normirani odhodki v višini 80 % prihodkov, vendar ne več kot
  40.000 eurov, ali 80.000 eurov, če je bila v davčnem letu ... obvezno zavarovana vsaj ena oseba za polni delovni čas
  neprekinjeno najmanj pet mesecev" (`siNormFullTime` read as that condition);
* 2023-2024 (NPB 32/33, ZDoh-2AA, Ur. l. RS 158/22, čl. 21(1): "Spremenjeni ... 59. ... člen ... se uporabljajo za
  davčna leta, ki se začnejo 1. januarja 2023"): with a person insured full time "najmanj devet mesecev" 80 % up to
  50.000 and 40 % from 50.000 to 100.000 of revenue; otherwise 80 % up to 12.500 and 40 % from 12.500 to 50.000;
* 2025: `normExpenses` (ZDoh-2AB). -/
def normExpensesY (y : Nat) (full : Bool) (r : Int) : Int :=
  if y ≤ 2022 then min (pct (pos r) 8000) (if full then 8000000 else 4000000)
  else if y ≤ 2024 then
    (if full then pct (min (pos r) 5000000) 8000 + pct (overlap 0 r 5000000 10000000) 4000
     else pct (min (pos r) 1250000) 8000 + pct (overlap 0 r 1250000 5000000) 4000)
  else normExpenses full r

theorem normExpensesY_2025 (full : Bool) (r : Int) : normExpensesY 2025 full r = normExpenses full r := by
  simp [normExpensesY]

def normProfit (p : Person) : Int := pos (p.normRev - normExpensesY p.year p.normFull p.normRev)

/-- ZDoh-2 čl. 135.č: rent "po stopnji 15 %" in 2022 (NPB 31) and "po stopnji 25 %" from 2023 (NPB 32/33, ZDoh-2AA
čl. 21(1) lists 135.č among the articles applied from the 2023 tax year); čl. 77(1) (10 % flat costs), čl. 132 (25 %,
20 % after 5 and 15 % after 10 years), čl. 96(1) (exempt after 15 years), čl. 112(3) (13,5 % pension credit) and
čl. 135.a (20 % on flat-rate s.p. profit) read the same in NPB 31 and NPB 33 as in 2025 (round 8 check). -/
def rentRateY (y : Nat) : Int := if y ≤ 2022 then 1500 else rentRate

theorem rentRateY_2025 : rentRateY 2025 = rentRate := by decide

/-- s.p. contributions (both shares) on the base clamped between 60 % and 350 % of PP. -/
def seContrib (p : Person) : Int :=
  if p.se > 0 ∨ (p.normRev > 0 ∧ p.normFull) then pct (clamp seMinBase seMaxBase (pos p.se + normProfit p)) (yp p.year).seRate
  else if p.normRev > 0 then sideContribYear else 0

/-- The part of the s.p. contributions deductible in the annual base (actual-expense s.p. only). -/
def seContribDeductible (p : Person) : Int :=
  if p.se > 0 then (if p.normRev > 0 then pct (clamp seMinBase seMaxBase (pos p.se)) (yp p.year).seRate else seContrib p) else 0

-- Employee contributions at the year's rate (2025: `employeeSSC`; 2022-2024: 22,10 %, `Years.yp`).
/-- `--eurostat` (convention, Eurostat earn_net ESMS 3.4: contribution parameters "refer to the beginning of the fiscal
year, i.e. changes occurring later during the year are ignored"): 2025 with the contributions in force on 1. 1. 2025:
employee 22,10 % (the 1,00 % long-term-care contribution applies "za obdobje od 1. julija 2025 dalje", ZDOsk-1; FURS
brošura 2.2), no pension LTC, OZP 12 x 35,00 (35,00 EUR 1.1.2024-28.2.2025, FURS OZP table). -/
def ypStart2025 : YP := { yp 2025 with eeRate := 2210, ozp := 12 * 3500, pensionLtc := 0 }
/-- `--euromod` (convention, not statute; EUROMOD "Nowcasting prices" note, Feb 2025, s. 1.3-1.4: "Legislative
parameters of the tax system are referred in EM to 30 June"; software/euromod/model/Documentation, sha256 64eb954e…):
2025 with the OZP in force on 30. 6. 2025, 37,17 EUR a month for all 12 months (FURS OZP table; EUROMOD country report
SI 2022-2025 §2.6.4: "As of March 2025, the compulsory health insurance contribution thus amounts to 37.17 EUR"). The
long-term-care contribution keeps its statutory start (1,00 % "za obdobje od 1. julija 2025 dalje", ZDOsk-1): the
country report states this treatment for that policy (§2.2.4 "introduced on 1 July 2025"; §2.6 rate lists "from July
1st 2025"), which governs over the general 30-June rule (tests/convention_policy.json, euromod_convention_mode).
2022-2024: no tax or SSC parameter of an employee changes within the year (OZP 35,00 all of 2024). -/
def ypJune2025 : YP := { yp 2025 with ozp := 12 * 3717 }
def ypP (p : Person) : YP :=
  if p.june30 && p.year = 2025 then ypJune2025
  else if p.startOfYear && p.year = 2025 then ypStart2025 else yp p.year

def wageSSC (p : Person) : Int := { employeeSSC with sched := Schedule.flat (ypP p).eeRate }.amount p.wages
def pensionLTC (p : Person) : Int := pct p.pension (ypP p).pensionLtc
def ozp (p : Person) : Int := if p.age ≥ 18 then (ypP p).ozp else 0

def employeeSocial (p : Person) : Int := wageSSC p + pensionLTC p + seContrib p + ozp p

/-- čl. 111(3)-(4): "skupni dohodek" for the additional general allowance: employment (incl. pension), activity
(profit before contributions; NOT flat-rate-expense income), … (gross, as FURS's monthly table "bruto"). -/
def skupniDohodek (p : Person) : Int := p.wages + p.pension + pos p.se

/-- čl. 109(1), 41: annual base (normirani income excluded). OZP is deducted as an obligatory contribution. -/
def annualBase (p : Person) : Int :=
  pos (p.wages + p.pension + p.se - wageSSC p - pensionLTC p - seContribDeductible p - ozp p)

/-- The pension's share of the annual base (for the čl. 112(7) cap). -/
def pensionBase (p : Person) : Int := pos (p.pension - pensionLTC p)

def generalAllowance (p : Person) : Int := (yp p.year).generalTaper.amount (skupniDohodek p)
def ageAllowance (p : Person) : Int := if p.age ≥ 70 then (yp p.year).age70 else 0
def youngAllowance (p : Person) : Int := if p.age ≤ 29 ∧ p.wages > 0 then (yp p.year).young else 0
def ownAllowances (p : Person) : Int := generalAllowance p + ageAllowance p + youngAllowance p

/-- Base before dependants' allowances. -/
def base0 (p : Person) : Int := annualBase p - ownAllowances p

/-- Net annual base after dependants' allowances `d` (čl. 119(1)). -/
def netBase (p : Person) (d : Int) : Int := pos (base0 p - d)

/-- Tax by čl. 122 on the net base, to the cent (half up). -/
def taxOn (x : Int) : Int := sched.tax Rule.unitHalfUp x

/-- čl. 122 with the year's schedule (2025: `taxOn`). -/
def taxBefore (p : Person) (d : Int) : Int := (yp p.year).sched.tax Rule.unitHalfUp (netBase p d)

/-- čl. 112(3), (7): 13,5 % of the pension, at most the tax on the pension (its proportional share). -/
def pensionCredit (p : Person) (d : Int) : Int :=
  let ab := annualBase p
  if ab ≤ 0 ∨ p.pension ≤ 0 then 0
  else min (pct p.pension pensionCreditRate) (taxBefore p d * pensionBase p / ab)

def personTax (p : Person) (d : Int) : Int := taxBefore p d - pensionCredit p d

/-- Final taxes on capital income and rent (čl. 132, 133, 135.č) and on flat-rate s.p. income (čl. 135.a). -/
def capitalTax (p : Person) (holding : Int) : Int :=
  pct (pos (p.interest - interestExempt)) capitalRate + pct (pos p.dividends) capitalRate
    + pct (pos p.gains) (gainsRate holding) + pct (pos p.rent - pct (pos p.rent) rentCostPct) (rentRateY p.year)

def normTax (p : Person) : Int := pct (normProfit p) normTaxRate

/-- Total of the čl. 114 child allowances for `n` children. -/
def childTotal (n : Nat) : Int := ((List.range n).map childAmount).foldl (· + ·) 0

/-- A person's own income for the dependant test (čl. 115(1): "vsi dohodki po tem zakonu"). -/
def ownIncome (p : Person) : Int :=
  p.wages + p.pension + pos p.se + p.normRev + p.interest + p.dividends + p.gains + p.rent

/-- čl. 115(1): a dependent spouse is not employed, has no activity and own income below 2.838,30. -/
def isDependentSpouse (p : Person) : Bool :=
  p.wages == 0 && p.se == 0 && p.normRev == 0 && decide (ownIncome p < (yp p.year).otherDep)

/-- Tax of a couple when the first takes `dA` of the child allowances `D` and the second the rest (with the
spouse allowances `sA`, `sB` already decided). -/
def coupleTax (a b : Person) (sA sB D dA : Int) : Int :=
  personTax a (sA + dA) + personTax b (sB + (D - dA))

/-- čl. 114(10): one parent claims, the other gets only what the first cannot use. -/
def claimFirst (a b : Person) (sA sB D : Int) (first : Nat) : Int :=
  if first == 0 then min D (pos (base0 a - sA)) else D - min D (pos (base0 b - sB))

/-- The parents' cheapest split (they may agree, čl. 114(10)-(11), and split by months, čl. 114(9)): the tax is
convex and piecewise linear in the split, so the minimum is at 0, D or a bracket edge of either parent. -/
def bestSplit (a b : Person) (sA sB D : Int) : Int :=
  let edges : List Int := (yp a.year).edges
  let cands : List Int := [0, D, claimFirst a b sA sB D 0, claimFirst a b sA sB D 1] ++
    edges.map (fun t => base0 a - sA - t) ++ edges.map (fun t => D - (base0 b - sB - t))
  let cands := cands.map (clamp 0 D)
  cands.foldl (fun best x => if coupleTax a b sA sB D x < coupleTax a b sA sB D best then x else best) D

/-- Monthly otroški dodatek (cents) for a family with yearly net income `famNet` (cents), `members` persons and
children aged `kids` (oldest first): class by income per person per month (ZUPJS čl. 22(2)), amount by rank,
+30 % for a single-parent family (ZSDP-1 čl. 72(1)). -/
def cbMonthlyOf (famNet : Int) (members : Nat) (kids : List Nat) (lone : Bool) : Int :=
  let cls := classTable.lookup (famNet / 12 / (members : Int)) 0
  ((kids.zipIdx).map fun (a, i) =>
    let m := childBenefitMonthly cls i (a ≥ 15)
    if lone then pct m loneParentPct else m).foldl (· + ·) 0

/-! ## Reading the household -/

def eurC (x : Int) : Int := x * CENT

def jInt (j : Json) (k : String) (d : Int := 0) : Int := intField j k d
def jBool (j : Json) (k : String) (d : Bool) : Bool := boolField j k d

def persons (c : Canon) : List Person :=
  let raws := (arrField c.raw "adults").toList
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n == 2 then (if i == 0 then half1 x else half2 x) else x
  (c.adults.zipIdx).map fun (a, i) =>
    let r := raws.getD i Json.null
    { age := a.age, wages := eurC a.wages, se := eurC a.selfEmployment, pension := eurC a.pension,
      normRev := eurC (jInt r "siNormRevenue"), normFull := jBool r "siNormFullTime" true,
      interest := share (eurC c.interest) i, dividends := share (eurC c.dividends) i,
      gains := share (eurC c.capitalGains) i, rent := share (eurC c.rentalIncome) i, year := c.year }

def partners (c : Canon) : Bool := c.isCouple && (c.married || c.bool? "cohabiting" == some true)

/-- Dependent children for the tax allowance: under 18 (čl. 115(2)), or under 26 in school (čl. 115(3)). -/
def taxChildren (c : Canon) : Nat :=
  if c.bool? "siChildrenInSchool" == some true then c.childrenUnder 26 else c.childrenUnder 18

/-! ## Result -/

structure Result where
  ps : List Person
  dep : List Int          -- dependants' allowances per person (cents)
  bases : List Int        -- net annual bases
  before : List Int       -- tax before the pension credit
  credits : List Int
  taxes : List Int        -- personal annual tax
  capital : List Int      -- final capital/rent taxes
  norm : List Int         -- final flat-rate s.p. taxes
  social : List Int
  famNet : Int            -- family net income (cents/year) for the child-benefit test
  members : Nat
  perPerson : Int         -- cents/month
  cls : Int
  cbMonthly : Int
  /-- monthly amount in January-February (the previous Sklep's table; = `cbMonthly` with `--oecd`) -/
  cbJanFeb : Int
  largeFam : Int
  benefits : Int
  deriving Inhabited

def sumL (l : List Int) : Int := l.foldl (· + ·) 0

/-- `oecd`: the OECD convention of the March amounts for all 12 months (flag `--oecd`). Statute (default): ZUTPG
čl. 3 indexes from 1 March (each Sklep: "od 1. marca"), so January-February use the previous Sklep's table
(`Years.cbJanFeb`). 
`janTable` (convention, not statute; `--jan-table`): the child-benefit table in force on 1 January (the previous
Sklep) for all 12 months, as OECD TaxBEN 2024 does; ZUTPG čl. 3 applies each Sklep only "od 1. marca". -/
def compute (c : Canon) (oecd : Bool := false) (janTable : Bool := false) (startOfYear : Bool := false)
    (june30 : Bool := false) : Result :=
  let ps := (persons c).map fun p => { p with startOfYear, june30 }
  let nKids := taxChildren c
  -- `siForgoDependants` (euros): child allowances the parents choose not to claim (they must be claimed, čl. 114)
  let D := pos (childTotalY c.year nKids - eurC ((c.int? "siForgoDependants").getD 0))
  let holding := (c.int? "siHoldingYears").getD 0
  let dep : List Int :=
    match ps with
    | [_] => [D]
    | [a, b] =>
      if partners c then
        let sA := if isDependentSpouse b then (yp c.year).otherDep else 0
        let sB := if isDependentSpouse a then (yp c.year).otherDep else 0
        let dA := match c.int? "siChildClaim", c.str? "siChildClaim" with
          | some 0, _ => claimFirst a b sA sB D 0
          | some 1, _ => claimFirst a b sA sB D 1
          | _, some "half" => D / 2  -- čl. 114(11): no agreement, each a proportional part
          | _, _ => bestSplit a b sA sB D
        [sA + dA, sB + (D - dA)]
      else [D, 0]
    | _ => ps.map fun _ => 0
  let pd := ps.zip dep
  let bases := pd.map fun (p, d) => netBase p d
  let before := pd.map fun (p, d) => taxBefore p d
  let credits := pd.map fun (p, d) => pensionCredit p d
  let taxes := pd.map fun (p, d) => personTax p d
  let capital := ps.map fun p => capitalTax p holding
  let norm := ps.map normTax
  let social := ps.map employeeSocial
  -- otroški dodatek: the family = the applicant, the partner and the children (ZUPJS čl. 10(1))
  let fam : List Nat := if partners c then [0, 1] else [0]
  let netOf (i : Nat) : Int :=
    let p := ps.getD i default
    -- Pravilnik PRAV12104 čl. 2: income less costs, taxes and obligatory contributions; čl. 10(2): flat-rate
    -- s.p. income = profit less the tax (contributions not deducted)
    p.wages + p.pension + p.se + normProfit p + p.interest + p.dividends + p.gains + p.rent
      - (wageSSC p + pensionLTC p + seContribDeductible p + ozp p)
      - taxes.getD i 0 - capital.getD i 0 - norm.getD i 0
  let famNet := pos (sumL (fam.map netOf))
  let kids := ((c.children.filter (·.age < 18)).mergeSort (fun x y => x.age ≥ y.age)).map (·.age)
  let members := fam.length + c.children.length
  let perPerson := famNet / 12 / (members : Int)
  let lone := (c.bool? "siLoneParent").getD (!partners c && kids.length > 0)
  let tM := cbFor c.year
  -- `--euromod`: the table in force on 30 June (the year's Sklep, from 1 March) for all 12 months
  let tJ := if oecd || june30 then tM else cbJanFeb c.year
  -- ZUPJS čl. 22(2)-(3) class and rank, ZSDP-1 čl. 72(1) +30 % for a single-parent family, per table
  let cbm (t : CBT) : Int :=
    let k := t.cls perPerson
    ((kids.zipIdx).map fun (a, i) =>
      let m := t.amount k i (a ≥ 15)
      if lone then pct m loneParentPct else m).foldl (· + ·) 0
  let cls := tM.cls perPerson
  let cbMonthly := cbm tM
  let cbJF := cbm tJ
  let lf := tM.largeFamily (c.childrenUnder 18)
  { ps, dep, bases, before, credits, taxes, capital, norm, social, famNet, members, perPerson, cls, cbMonthly,
    cbJanFeb := cbJF, largeFam := (if janTable then tJ.largeFamily (c.childrenUnder 18) else lf),
    benefits := if janTable then 12 * cbJF + tJ.largeFamily (c.childrenUnder 18) else 10 * cbMonthly + 2 * cbJF + lf }

def outWith (args : List String) (c : Canon) : Out :=
  let oecd := args.contains "--oecd"
  let jan := args.contains "--jan-table" && !oecd
  let euromod := args.contains "--euromod"
  let r := compute c oecd jan (args.contains "--eurostat") euromod
  let it := sumL r.taxes + sumL r.capital + sumL r.norm
  let personJ : List Json := (List.range r.ps.length).map fun i =>
    let p := r.ps.getD i default
    Json.mkObj [("annualBase", toJson (toEur (annualBase p))), ("generalAllowance", toJson (toEur (generalAllowance p))),
      ("ownAllowances", toJson (toEur (ownAllowances p))), ("dependants", toJson (toEur (r.dep.getD i 0))),
      ("netBase", toJson (toEur (r.bases.getD i 0))), ("taxBefore", toJson (toEur (r.before.getD i 0))),
      ("pensionCredit", toJson (toEur (r.credits.getD i 0))), ("tax", toJson (toEur (r.taxes.getD i 0))),
      ("capitalFinalTax", toJson (toEur (r.capital.getD i 0))), ("normFinalTax", toJson (toEur (r.norm.getD i 0))),
      ("social", toJson (toEur (r.social.getD i 0)))]
  Out.make c "SI" "EUR" (toEur it) (employeeSocial := toEur (sumL r.social)) (benefits := toEur r.benefits)
    (detail := [Out.d "taxableIncome" (toEur (sumL r.bases)), Out.d "taxBeforeCredits" (toEur (sumL r.before)),
      Out.d "taxCents" it, Out.d "socialCents" (sumL r.social),
      ("persons", Json.arr personJ.toArray),
      Out.d "childBenefitClass" r.cls, Out.d "incomePerPersonMonthlyCents" r.perPerson,
      Out.d "childBenefitMonthlyCents" r.cbMonthly, Out.d "childBenefitJanFebMonthlyCents" r.cbJanFeb,
      Out.d "largeFamilyAllowance" (toEur r.largeFam),
      Out.dStr "note" (if jan then "--jan-table: child benefit at the table in force on 1 January for all 12 months (TaxBEN convention), tested on the same year's net income" else if euromod && !oecd then "--euromod: parameters in force on 30 June (EUROMOD Nowcasting note s. 1.4): child benefit at the year's Sklep (from 1 March) for all 12 months, 2025 OZP 37,17 EUR for 12 months; LTC from 1 July 2025 (EUROMOD CR SI §2.2.4, §2.6)" else if oecd then "--oecd: child benefit at the amounts from 1 March for all 12 months (OECD convention), tested on the same year's net income"
        else "ZDoh-2 as in force on 1 January of the tax year (čl. 2; 2022-2025); child benefit Jan-Feb at the previous Sklep, Mar-Dec at the year's Sklep (ZUTPG čl. 3), tested on the same year's net income")])
    (unsupported := ["withholding (akontacija) and its settlement", "minimum contribution base for employees (60 % PP)",
      "child benefit: previous-year income (ZUPJS čl. 15(2)), the +20 % for a child under 4 not in kindergarten, assets test",
      "student work, special-needs children, parents as dependants", "OZP paid by the state for low-income persons"] ++
      (if c.year < 2025 then ["tax year " ++ toString c.year ++ ": schedule, general/child/dependant/age/young allowances, employee rate, OZP, s.p. rate and child benefit are year-specific; flat-rate expenses (čl. 59) and the rent rate (čl. 135.č) follow the dated ZDoh-2 versions; pension credit, capital and flat-rate s.p. rates are unchanged from 2025 in those versions; s.p. minimum/maximum bases (60 % / 350 % of the SURS average wage) and the side-occupation lump sums use 2025 values (not cited per year)"] else []) ++
      (if c.year == 2022 && !oecd && !euromod then ["2022: January-February child benefit at the March-2022 amounts (the 2021 table was not fetched)"] else []))

def out (c : Canon) : Out := outWith [] c

def country : Country :=
  { code := "SI", name := "Slovenia", currency := "EUR", year := "2025", compute := out, computeWith := outWith }

end SiTax
