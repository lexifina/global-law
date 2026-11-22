import FrTax.Liquidation
import Compare.Canon

/-!
# France, income 2025: the canonical household on the existing FrTax model, plus contributions on pay and
# the allocations familiales

The income tax, the flat tax on investment income (art. 200 A), the CEHR (art. 223 sexies), the CDHR (art. 224) and
the prélèvements sociaux on investment and property income are `FrTax.compute` and `FrTax.socialLevies`, the model in
`fr/lean` (copied here unchanged; hashes in `refs/fr_sources.sha256`).

This file adds what the model leaves out because it starts from the boxes of form 2042, which hold the *taxable*
salary:
* the employee's compulsory contributions on a gross salary (pension insurance, AGIRC-ARRCO complementary pensions),
  the CSG and the CRDS on pay, and from them the taxable salary of box 1AJ;
* the allocations familiales (the one universal cash child benefit), with their income tiers and the complement that
  smooths each tier boundary.

Simplifications (stated once, applying to every household): an ordinary private-sector employee outside
Alsace-Moselle, one employer, pay spread evenly over the year; contributions computed on the annual pay and rounded
to the euro per line (payroll rounds each month to the cent); no APEC (executives, 0.024 %), no employer-paid
complementary health or provident cover added to the CSG base or the taxable salary; the allocations familiales take
the same year's income as their resources (the law reads the income of year N-2).

How the household is put on returns: a married couple files one return (art. 6, 1); a single adult files alone,
with the single-parent half part (art. 194, II, box T) when there are children; two unmarried adults file two
returns, the children on the first (no box T: they do not live alone), investment, rental income, gifts and pension
contributions split equally. Investment income is French and paid by a French bank: interest 2TR, dividends 2DC
(eligible for the 40 % allowance under the option), gains 3VG; the household takes the cheaper of the flat tax and
the option for the scale (art. 200 A, 2), as the US model takes the cheaper of itemizing and the standard deduction.
-/

namespace Compare.Fr
open FrTax Lean

/-! ## Contributions on pay (employee share, 2025) -/

/-- Plafond annuel de la sécurité sociale for 2025 (CSS art. L241-3; arrêté du 19 décembre 2024): 47 100 €. -/
def pass : Int := 47100

/-- PASS for 2024 (arrêté du 19 décembre 2023): 46 368 €; sets the PER deduction ceilings of art. 163 quatervicies
for contributions paid in 2025. -/
def pass2024 : Int := 46368

/-- The PASS of year `y` (CSS art. L241-3, D242-17; one arrêté a year): 2021 and 2022 41 136 € (arrêté du 22
décembre 2020; arrêté du 15 décembre 2021 portant fixation du plafond de la sécurité sociale pour 2022); 2023
43 992 € (arrêté du 9 décembre 2022); 2024 46 368 € (arrêté du 19 décembre 2023); 2025 47 100 € (arrêté du 19
décembre 2024). Round 1 (improve-continental): the contributions of 2022-2024 used the 2025 PASS before. -/
def passFor : Nat → Int
  | 2021 => 41136 | 2022 => 41136 | 2023 => 43992 | 2024 => 46368 | _ => pass

/-- `rate` basis points of `x` euros, rounded half up to the euro. -/
def bpOf (rate x : Int) : Int := rnd (rate * x) 10000

/-- `rate` basis points of `x` euros, in cents, rounded half up to the cent. -/
def bpCents (rate x : Int) : Int := rnd (rate * x) 100

/-- The employee's contributions on an annual gross salary, each line in cents (computed on the year's pay, not
month by month). -/
structure Contrib where
  /-- CSS art. D242-4: assurance vieillesse, salarié, 6,90 % "sur la part de la rémunération dans la limite du
  plafond", from 1 January 2024. -/
  vieillessePlaf : Int
  /-- CSS art. D242-4: 0,40 % "sur la totalité de la rémunération". -/
  vieillesseDeplaf : Int
  /-- AGIRC-ARRCO complementary pensions (CSS art. L921-1; ANI du 17 novembre 2017), employee share: 3,15 % on
  tranche 1 (pay up to the PASS), 8,64 % on tranche 2 (from 1 to 8 PASS). -/
  agircT1 : Int
  agircT2 : Int
  /-- Contribution d'équilibre général, employee share: 0,86 % on tranche 1, 1,08 % on tranche 2. -/
  cegT1 : Int
  cegT2 : Int
  /-- Contribution d'équilibre technique, employee share: 0,14 % on tranches 1 and 2, due only when pay exceeds the
  PASS (so it starts with a jump at the PASS). -/
  cet : Int
  /-- CSS art. L136-2, I: the CSG and CRDS base on pay is reduced by 1,75 % "pour leur montant inférieur à quatre
  fois la valeur du plafond" (in cents). -/
  csgBase : Int
  /-- CSS art. L136-8, I, 1°: CSG 9,2 %, of which 6,8 points deductible from taxable income (CGI art. 154 quinquies,
  I) and 2,4 points not deductible. -/
  csgDeductible : Int
  csgNonDeductible : Int
  /-- CRDS 0,5 % on the same base (ordonnance n° 96-50 du 24 janvier 1996, art. 14 and 19). -/
  crds : Int
  deriving Repr

def contribP (pass : Int) (g0 : Int) : Contrib :=
  let g := max 0 g0
  let t1 := min g pass
  let t2 := max 0 (min g (8 * pass) - pass)
  let base := 100 * g - rnd (175 * min g (4 * pass)) 100
  { vieillessePlaf := bpCents 690 t1, vieillesseDeplaf := bpCents 40 g,
    agircT1 := bpCents 315 t1, agircT2 := bpCents 864 t2, cegT1 := bpCents 86 t1, cegT2 := bpCents 108 t2,
    cet := if g > pass then bpCents 14 (t1 + t2) else 0,
    csgBase := base, csgDeductible := rnd (680 * base) 10000, csgNonDeductible := rnd (240 * base) 10000,
    crds := rnd (50 * base) 10000 }

/-- 2025. The rates (D242-4, the AGIRC-ARRCO ANI, L136-2 / L136-8, the CRDS) did not change from 2022 to 2025;
only the PASS did. -/
def contrib (g0 : Int) : Contrib := contribP pass g0

/-- The contributions of year `y`: the same rates on that year's PASS. -/
def contribY (y : Nat) (g0 : Int) : Contrib := contribP (passFor y) g0

/-- The social security and complementary-pension contributions (not the CSG/CRDS), in euros. -/
def Contrib.ssc (c : Contrib) : Int :=
  rnd (c.vieillessePlaf + c.vieillesseDeplaf + c.agircT1 + c.agircT2 + c.cegT1 + c.cegT2 + c.cet) 100

/-- The CSG and CRDS on pay, in euros. -/
def Contrib.csgCrds (c : Contrib) : Int := rnd (c.csgDeductible + c.csgNonDeductible + c.crds) 100

/-- The deductible CSG, in euros. -/
def Contrib.csgDed (c : Contrib) : Int := rnd c.csgDeductible 100

def Contrib.total (c : Contrib) : Int := c.ssc + c.csgCrds

/-- **CGI art. 83, 1° and art. 154 quinquies, I.** The salary declared in box 1AJ: gross pay less the compulsory
contributions and the deductible 6,8 points of CSG (the 2,4 points and the CRDS stay taxable). -/
def taxableSalaryY (y : Nat) (g : Int) : Int :=
  let c := contribY y g
  max 0 g - c.ssc - c.csgDed

def taxableSalary (g : Int) : Int := taxableSalaryY 2025 g

/-! ## Allocations familiales (CSS art. L521-1, D521-1, D521-3), 2025 -/

/-- Base mensuelle de calcul des allocations familiales (CSS art. L551-1), in cents: 474,37 € from 1 April 2025
(DSS-DGCS press release of 31 March 2025: "revalorisée de 1,7 % ... son montant est de 474,37 €"); 466,44 € before
(the same release: 2 children "de 149,26 € à 151,8 €", and 149,26 € = 32 % of 466,44 €). -/
def bmafJanMar : Int := 46644
def bmafAprDec : Int := 47437

/-- D521-1, I: rates in basis points of the BMAF for tier 1, 2, 3: for the second child, for the third and each
further child, and the age supplement. -/
def rateSecond : Nat → Int | 1 => 3200 | 2 => 1600 | _ => 800
def rateThird : Nat → Int | 1 => 4100 | 2 => 2050 | _ => 1025
def rateAge : Nat → Int | 1 => 1600 | 2 => 800 | _ => 400

/-- D521-3, I and II: the ceilings for `n` children, revalued each 1 January in line with consumer prices excluding
tobacco (CSS art. D521-3, III; L551-1). 2022: arrêté du 16 décembre 2021 (58 396 € / 81 721 €, 5 839 € per
child); 2023: arrêté du 21 décembre 2022 (59 330 € / 83 029 €, 5 932 €); 2024: instruction interministérielle
DSS/2B/2023/205 du 21 décembre 2023 (62 474 € / 87 430 €, 6 246 €: 74 966 € and 99 922 € for two children); 2025:
BO Santé-Protection sociale-Solidarité n° 2024/34 du 31 décembre 2024 (65 473 € / 91 627 €, 6 546 €: 78 565 € and
104 719 € for two children, the 2024 values x 1,048). Round 1 (improve-continental): the model used the 2024
ceilings for 2025 (it cited a service-public page for "2025" whose figures are the 2024 ones). -/
def ceil1For : Nat → Int → Int
  | 2022, n => 58396 + 5839 * n | 2023, n => 59330 + 5932 * n | 2024, n => 62474 + 6246 * n
  | _, n => 65473 + 6546 * n
def ceil2For : Nat → Int → Int
  | 2022, n => 81721 + 5839 * n | 2023, n => 83029 + 5932 * n | 2024, n => 87430 + 6246 * n
  | _, n => 91627 + 6546 * n
def ceiling1 (n : Int) : Int := ceil1For 2025 n
def ceiling2 (n : Int) : Int := ceil2For 2025 n

/-- The BMAF of each month of year `y`, in cents (CSS art. L551-1): 414,81 € from 1 April 2021 (circulaire
DSS/2B/2021/65 du 19 mars 2021); 422,28 € from 1 April 2022 (circulaire DSS/2B/2022/82 du 28 mars 2022); 439,17 €
from 1 July 2022 (loi n° 2022-1158 du 16 août 2022, art. 9: 4 % anticipated revaluation); 445,93 € from 1 April
2023 (instruction interministérielle DSS/2B/2023/41 du 24 mars 2023); 466,44 € from 1 April 2024 (instruction
interministérielle DSS/2B/2024/43 du 20 mars 2024); 474,37 € from 1 April 2025 (above). Round 1: the allocations
of 2022-2024 used the 2025 bases before. -/
def bmafMonths : Nat → List Int
  | 2022 => List.replicate 3 41481 ++ List.replicate 3 42228 ++ List.replicate 6 43917
  | 2023 => List.replicate 3 43917 ++ List.replicate 9 44593
  | 2024 => List.replicate 3 44593 ++ List.replicate 9 46644
  | _ => List.replicate 3 bmafJanMar ++ List.replicate 9 bmafAprDec

/-- `--june30` (EUROMOD convention, round 15): the months before July take the BMAF in force on 30 June; from July the
months keep their own base. EUROMOD "usually simulates policies as of June 30th of the respective year" and, for
France 2022-2025, the full-year adjustment for later changes "is switched on by default ... weighted by the number of
months the amounts are in application" (EUROMOD Country Report France 2022-2025, JRC 2026, policy extensions: Full
Year Adjustments; EUROMOD nowcasting note, JRC 2025, sections 1.3-1.4). Statute (no flag): each month's own base. -/
def bmafMonthsJune30 (y : Nat) : List Int :=
  let l := bmafMonths y
  List.replicate 6 (l.getD 5 0) ++ l.drop 6

/-- The monthly amount in cents for `n` children under 20, `k` of them taking the age supplement. -/
def monthly (bmaf : Int) (tier : Nat) (n k : Int) : Int :=
  if n < 2 then 0 else
  rnd (rateSecond tier * bmaf) 10000 + (n - 2) * rnd (rateThird tier * bmaf) 10000 + k * rnd (rateAge tier * bmaf) 10000

/-- **D521-1, II.** One month's allocation for resources `r`: the tier's amount, plus, just above a ceiling `c`, the
complement "égal, pour chaque mois, au douzième de la différence entre ... ce plafond de ressources majoré de [douze
fois le montant mensuel] et ... le montant des ressources". In cents. -/
def monthC (c1 c2 : Int) (bmaf : Int) (r n k : Int) : Int :=
  let tier : Nat := if r ≤ c1 then 1 else if r ≤ c2 then 2 else 3
  let m := monthly bmaf tier n k
  let comp (c : Int) : Int := max 0 ((100 * c + 12 * m - 100 * r) / 12)
  m + (if tier = 2 then comp c1 else if tier = 3 then comp c2 else 0)

def month (bmaf : Int) (r n k : Int) : Int := monthC (ceiling1 n) (ceiling2 n) bmaf r n k

/-- The allocations familiales of 2025 in euros: three months at the old base, nine at the new one. The age
supplement goes to each child of 14 or more, except the eldest of exactly two children (CSS art. L521-3). -/
def allocationsY (y : Nat) (r : Int) (ages : List Nat) (june30 : Bool := false) : Int :=
  let kids := ages.filter (· < 20)
  let n : Int := kids.length
  let k0 : Int := (kids.filter (· ≥ 14)).length
  let k : Int := if n = 2 && k0 > 0 then k0 - 1 else k0
  let cents := (if june30 then bmafMonthsJune30 y else bmafMonths y).foldl (fun a b => a + monthC (ceil1For y n) (ceil2For y n) b r n k) 0
  rnd cents 100

def allocations (r : Int) (ages : List Nat) : Int := allocationsY 2025 r ages

/-- CRDS of 0,5 % on family benefits (ordonnance n° 96-50, art. 14; the OECD's tables deduct it too). -/
def crdsOnBenefits (af : Int) : Int := bpOf 50 af

/-! ## Returns -/

structure Foyer where
  people : List Adult
  couple : Bool
  kids : List Child
  livesAlone : Bool
  interest : Int
  dividends : Int
  gains : Int
  rents : Int
  gifts : Int
  pc : Int

def boxes (y : Nat) (f : Foyer) (opt : Bool) : List (String × Int) :=
  let yi : Int := y
  let p1 := f.people.headD {}
  let p2 := f.people.tail.head?
  let minors := f.kids.filter (·.age < 18)
  let adultsKids := f.kids.filter (·.age ≥ 18)
  let status := if f.couple then [("0AM", 1)] else [("0AC", 1)]
  let t := if !f.couple && f.livesAlone && !f.kids.isEmpty then [("0BT", 1)] else []
  let births := [("0DA", yi - p1.age)] ++ (match p2 with | some q => [("0DB", yi - q.age)] | none => [])
  let kidBoxes := (if minors.isEmpty then [] else [("0CF", (minors.length : Int))])
    ++ (minors.zipIdx.map fun (c, i) => (s!"0F{i}", yi - c.age))
    ++ (if adultsKids.isEmpty then [] else [("0DJ", (adultsKids.length : Int))])
    ++ (adultsKids.zipIdx.map fun (c, i) => (s!"0J{i}", yi - c.age))
  let person (p : Adult) (sal pen se : String) : List (String × Int) :=
    (if p.wages > 0 then [(sal, taxableSalaryY y p.wages)] else [])
      ++ (if p.pension > 0 then [(pen, p.pension)] else [])
      ++ (if p.selfEmployment ≠ 0 then [(se, p.selfEmployment)] else [])
  let pay := person p1 "1AJ" "1AS" "5QC" ++ (match p2 with | some q => person q "1BJ" "1BS" "5RC" | none => [])
  let inv := (if f.interest > 0 then [("2TR", f.interest)] else [])
    ++ (if f.dividends > 0 then [("2DC", f.dividends)] else [])
    ++ (if f.gains > 0 then [("3VG", f.gains)] else [])
    ++ (if opt then [("2OP", 1)] else [])
    -- the paying bank withheld the social levies on interest and dividends at source (box 2BH)
    ++ (if f.interest + f.dividends > 0 then [("2BH", f.interest + f.dividends)] else [])
  let rent := if f.rents ≠ 0 then [("4BA", f.rents)] else []
  let gift := if f.gifts > 0 then [("7UF", f.gifts)] else []
  -- art. 163 quatervicies, I, 2: the ceiling is 10 % of the previous year's professional income (here the same
  -- year's taxable salaries after the 10 % allowance), at least 10 % of the PASS, at most 10 % of 8 PASS (2024)
  let ceil (p : Adult) : Int :=
    let pp := passFor (y - 1)
    max (bpOf 1000 pp) (min (bpOf 1000 (8 * pp)) (bpOf 900 (taxableSalaryY y p.wages)))
  let per := if f.pc > 0 then
      [("6NS", f.pc), ("APS", ceil p1)] ++ (match p2 with
        | some q => [("APT", ceil q), ("6QR", 1)] | none => [])
    else []
  status ++ t ++ births ++ kidBoxes ++ pay ++ inv ++ rent ++ gift ++ per

def decl (y : Nat) (f : Foyer) (opt : Bool) : Decl :=
  { year := y, boxes := (boxes y f opt).foldl (fun m (kv : String × Int) => m.insert kv.1 kv.2) {} }

/-- **CSS art. L136-7 and L136-8, I, 2°; ordonnance n° 96-50, art. 16 and 19; CGI art. 235 ter.** The social levies
the paying bank withholds on interest and dividends paid in 2025: CSG 9,2 %, CRDS 0,5 %, prélèvement de solidarité
7,5 %, 17,2 % in all. The LFSS 2026 rate of 10,6 % for the CSG applies to these "produits de placement" only from
1 January 2026 (loi n° 2025-1403, art. 12, II, 2°, as noted under L136-8), while it applies to the "revenus du
patrimoine" of L136-6, which include gains on securities, from income 2025: those the model assesses on the
return (box 3VG) at 18,6 %. Rounded to the euro once (the bank rounds each payment to the cent). -/
def psAtSource (f : Foyer) : Int := bpOf 1720 (f.interest + f.dividends)

structure FoyerRes where
  r : Result
  opt : Bool
  ps : Int
  resources : Int

def foyer (p : Params) (y : Nat) (f : Foyer) : FoyerRes :=
  let d0 := decl y f false
  let r0 := compute p d0
  let ps := socialLevies d0 + psAtSource f
  let res0 := grossGlobal p d0 + flatBase d0
  if f.interest + f.dividends + f.gains ≤ 0 then { r := r0, opt := false, ps, resources := res0 } else
  let d1 := decl y f true
  let r1 := compute p d1
  if r1.net + r1.cehr + r1.cdhr < r0.net + r0.cehr + r0.cdhr then
    { r := r1, opt := true, ps, resources := grossGlobal p d1 + flatBase d1 }
  else { r := r0, opt := false, ps, resources := res0 }

def foyers (c : Canon) : List Foyer :=
  match c.adults with
  | [a] => [{ people := [a], couple := false, kids := c.children, livesAlone := true, interest := c.interest,
              dividends := c.dividends, gains := c.capitalGains, rents := c.rentalIncome, gifts := c.charitable,
              pc := c.pensionContributions }]
  | [a, b] =>
    if c.married then
      [{ people := [a, b], couple := true, kids := c.children, livesAlone := false, interest := c.interest,
         dividends := c.dividends, gains := c.capitalGains, rents := c.rentalIncome, gifts := c.charitable,
         pc := c.pensionContributions }]
    else
      [{ people := [a], couple := false, kids := c.children, livesAlone := false, interest := half1 c.interest,
         dividends := half1 c.dividends, gains := half1 c.capitalGains, rents := half1 c.rentalIncome,
         gifts := half1 c.charitable, pc := half1 c.pensionContributions },
       { people := [b], couple := false, kids := [], livesAlone := false, interest := half2 c.interest,
         dividends := half2 c.dividends, gains := half2 c.capitalGains, rents := half2 c.rentalIncome,
         gifts := half2 c.charitable, pc := half2 c.pensionContributions }]
  | _ => []

def fmtParts (q : Int) : String :=
  let w := q / 4
  match q % 4 with
  | 0 => s!"{w}" | 1 => s!"{w}.25" | 2 => s!"{w}.5" | _ => s!"{w}.75"

/-- `--euromod-schedule-year` (EUROMOD convention, round 15): the income-tax amounts (art. 197 schedule and caps, art. 83
and 158 allowances, décote, ...) enacted for the income of year `y - 1` are applied to the income of year `y`, as
EUROMOD's system `y` does: EUROMOD Country Report France 2022-2025 (Bouvard and Trannoy, JRC 2026), section 2.7.5,
Table 2.77 "IRPP, marginal income rates", labels the schedules 0-10 225 / 10 777 / 11 294 / 11 496 as "Taxation 2022,
income 2022" ... "Taxation 2025, income 2025", and Table 2.78 the caps 1 592 / 1 678 / 1 759 / 1 791 the same way; by
statute those are the schedules of incomes 2021-2024 (lois de finances 2022-2025). Contributions, CSG, CRDS and the
allocations familiales stay those of year `y`; the rules that depend on the year itself (`year := y`) are unchanged.
Statute mode (no flag): the amounts of income year `y`. -/
def taxParams (y : Nat) (args : List String) : Params :=
  if args.contains "--euromod-schedule-year" then { ((paramsFor (y - 1)).getD p2025) with year := y }
  else (paramsFor y).getD p2025

def out (c : Canon) (args : List String := []) : Out :=
  let y := c.year
  let p := taxParams y args
  let fs := foyers c
  let rs := fs.map (foyer p y)
  let sum (g : FoyerRes → Int) : Int := rs.foldl (fun a x => a + g x) 0
  let cs := c.adults.map fun a => contribY y a.wages
  let ssc := cs.foldl (fun a x => a + x.ssc) 0
  let csg := cs.foldl (fun a x => a + x.csgCrds) 0
  let resources := sum (·.resources)
  let af := allocationsY y resources (c.children.map (·.age)) (args.contains "--june30")
  let afCrds := crdsOnBenefits af
  let i (x : Int) : Json := Lean.toJson x
  let unsup : List String :=
    (if c.adults.any (fun a => a.selfEmployment ≠ 0) then
        ["contributions and CSG/CRDS of the self-employed (profit taxed as declared, box 5QC)"] else [])
      ++ (if c.adults.any (fun a => a.pension ≠ 0) then ["CSG, CRDS and CASA on pensions"] else [])
  { id := c.id, country := "FR", currency := "EUR", incomeTax := sum (·.r.net),
    surtaxes := [("CEHR", sum (·.r.cehr)), ("CDHR", sum (·.r.cdhr)), ("PrelevementsSociauxCapital", sum (·.ps))],
    localIncomeTax := 0, employeeSocial := ssc + csg, benefits := af - afCrds,
    detail := [("foyers", i fs.length), ("parts", Json.arr (rs.map fun x => Json.str (fmtParts x.r.quarters)).toArray),
      ("rni", i (sum (·.r.rni))), ("rfr", i (sum (·.r.rfr))), ("decote", i (sum (·.r.decote))),
      ("flatTax", i (sum (·.r.flat))), ("option2OP", Json.bool (rs.any (·.opt))),
      ("sscWages", i ssc), ("csgCrdsWages", i csg),
      ("csgDeductibleWages", i (cs.foldl (fun a x => a + x.csgDed) 0)),
      ("taxableSalaries", i (c.adults.foldl (fun a x => a + taxableSalaryY y x.wages) 0)),
      ("afResources", i resources), ("allocationsFamiliales", i af), ("crdsOnAllocations", i afCrds)],
    unsupported := unsup }

/-! ## Checks against the OECD Taxing Wages 2026 country table for France, 2025 -/

-- Average wage 45 964 €: employee SSC 5 198,39 € in the OECD table (11,31 % gives 5 198,53 € here); CSG + CRDS
-- 4 380,52 € (the OECD's income tax of the one-earner couple, whose impôt sur le revenu is nil, is exactly this).
#guard (contrib 45964).ssc = 5199
#guard (contrib 45964).csgCrds = 4380
-- 167 % of the average wage, 76 761 €: OECD 8 434,74 €.
#guard (contrib 76761).ssc = 8436
-- The CET starts with a jump at the PASS: one euro of pay above 47 100 € costs 65,94 € of CET.
#guard (contrib 47100).cet = 0 && (contrib 47101).cet = 6594
-- The allocations familiales of a couple on the average wage with two children: OECD 1 813,97 €, CRDS 9,07 €.
#guard allocations 40000 [6, 11] = 1814 && crdsOnBenefits 1814 = 9
-- Earlier years (round 1): 32 % of each month's BMAF before the 0,5 % CRDS.
#guard allocationsY 2022 40000 [6, 11] = 1647 && allocationsY 2023 40000 [6, 11] = 1706
#guard allocationsY 2024 40000 [6, 11] = 1771
#guard (contribY 2022 41136).cet = 0 && (contribY 2022 41137).cet > 0
-- `--june30`: 2022 = six months at 422,28 € and six at 439,17 €; 2024 = twelve months at 466,44 €.
#guard bmafMonthsJune30 2022 = List.replicate 6 42228 ++ List.replicate 6 43917
#guard bmafMonthsJune30 2024 = List.replicate 12 46644

end Compare.Fr
