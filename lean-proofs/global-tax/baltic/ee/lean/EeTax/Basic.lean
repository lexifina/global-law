import TaxKernel
import EeTax.Params
import EeTax.Model
import EeTax.Withholding

/-!
# Estonia 2025: the household (canonical contract) and the exe's output

Individual assessment (no joint return in 2025: the spouse exemption § 23^4 and the joint declaration of the unused
exemption were repealed from 1.1.2024, TuMS § 61(71) "kuni 2024. aasta 1. jaanuarini kehtinud … §-de 23^1, 23^4
ja 25"). Investment income, gifts and III-pillar payments of a couple are split half/half (`half1`/`half2`).
`dividends` = dividends from Estonian companies, on which the company paid 22/78 (reported in detail, not in
`incomeTax`: the individual owes nothing, § 12(2)). `rentalIncome` = residential rent (§ 39^1 20 % deduction).
Amounts in and out in whole euros; everything inside in cents.
-/

namespace EeTax
open TaxKernel Lean

def cents (e : Int) : Int := e * 100
def euros (c : Int) : Int := divR .halfUp c 100

/-- Family benefits a year (PHS §§ 17, 19, 21), cents. -/
def familyBenefits (y : Nat) (n : Nat) (singleUnrecorded : Bool) : Int :=
  let ca := (List.range n).foldl (fun acc i => acc + (if i < 2 then childAllowance12For y else childAllowance3)) 0
  let lf := if n ≥ 7 then largeFamily7For y else if n ≥ 3 then largeFamily3to6For y else 0
  let sp := if singleUnrecorded then singleParentFor y * n else 0
  12 * (ca + lf + sp)

def adultIns (c : Canon) (p2rate : Int) (paYears : Nat) (board : Bool) : List PIn :=
  let n := c.adults.length
  let sh (x : Int) (i : Nat) : Int := if n ≤ 1 then cents x else if i = 0 then cents (half1 x) else cents (half2 x)
  (c.adults.zipIdx).map fun (a, i) =>
    { pensionAge := a.age ≥ paYears, boardMember := board, wages := cents a.wages, business := cents a.selfEmployment,
      pension := cents a.pension, interest := sh c.interest i, gains := sh c.capitalGains i,
      rent := sh c.rentalIncome i, dividendsEE := sh c.dividends i, gifts := sh c.charitable i,
      pillar3 := sh c.pensionContributions i, p2Rate := p2rate, year2026 := c.year ≥ 2026, year := c.year }

/-- § 23^1 and § 23^4 (2022-2023 only): the extra exemptions, set on each adult. The child exemption (1848 euro for
the second child aged up to 17, 3048 for each further one) goes to one parent: the adult with the larger § 23(3)
income (the first on a tie). The spouse exemption (married couples): 2160 euro less the spouse's income, if the
couple's income is at most 50 400 euro, and not more than 50 400 less the couple's taxable income (§ 23^4(3); the
couple's taxable income before the extra exemptions is used). -/
def withExtras (c : Canon) (ins : List PIn) : List PIn :=
  if !(hasFamilyExemptions c.year) then ins else
  let o := ins.map person
  let tulu := o.map (·.tulu)
  let k := (c.children.filter (·.age ≤ 17)).length
  let kidEx : Int := if k ≥ 2 then childExtra2 + childExtra3 * ((k - 2 : Nat) : Int) else 0
  let t0 := tulu.getD 0 0
  let t1 := tulu.getD 1 0
  let holder : Nat := if ins.length = 2 && t1 > t0 then 1 else 0
  let married := c.married && ins.length = 2
  let tot := t0 + t1
  let taxableTot := (o.map (·.taxable)).foldl (· + ·) 0
  let spouseEx (other : Int) : Int :=
    if married && tot ≤ spouseCap then min (pos (spouseExtra - pos other)) (pos (spouseCap - taxableTot)) else 0
  (ins.zipIdx).map fun (p, i) =>
    let sx := spouseEx (if i = 0 then t1 else t0)
    { p with extraEx := (if i = holder then kidEx else 0) + sx }

def pjson (o : POut) : Json :=
  Json.mkObj [("tulu_c", toJson o.tulu), ("exemption_c", toJson o.exemption), ("ui_c", toJson o.ui),
    ("pillar2_c", toJson o.p2), ("fieSocialTax_c", toJson o.fieSocial), ("deductionsGifts_c", toJson o.dedGifts),
    ("deductionsPillar3_c", toJson o.dedP3), ("taxable_c", toJson o.taxable), ("tax_c", toJson o.tax)]

def sumBy (l : List POut) (f : POut → Int) : Int := l.foldl (fun a o => a + f o) 0

/-- Optional input `monthlyWages`: the first adult's twelve monthly wage payments (euros) from the payer holding
the exemption application (§ 42(1)-(2)); the output then shows the withholding, the annual tax on those wages alone
and the settlement on the return (refund > 0, bill < 0). -/
def monthlyList (c : Canon) : Option (List Int) :=
  match c.raw.getObjVal? "monthlyWages" with
  | .ok (.arr a) => some (a.toList.filterMap fun j => match j.getInt? with | .ok i => some i | _ => none)
  | _ => none

def out (c : Canon) : Out :=
  let p2rate := (c.int? "pillar2Rate").getD pillar2Default
  let paYears := ((c.int? "pensionAgeYears").getD (pensionAgeYears : Int)).toNat
  let board := (c.bool? "boardMember").getD false
  let ins := withExtras c (adultIns c p2rate paYears board)
  let outs := ins.map person
  let oecd := (withExtras c (adultIns c 0 paYears board)).map person      -- the OECD convention: no II-pillar member (F1)
  let tax := sumBy outs (·.tax)
  let soc := sumBy outs POut.social
  let nKids := c.childrenUnder childAgeLimit
  let single := c.adults.length == 1
  let unrec := single && (c.bool? "otherParentUnrecorded").getD false
  let ben := familyBenefits c.year nKids unrec
  let spIfElig := if single then 12 * singleParentFor c.year * nKids else 0
  let cit := citOnDividend (cents c.dividends)
  -- withholding: wages paid evenly over 12 months by one payer holding the exemption application
  let wh := (ins.zip outs).foldl (fun acc (p, _) => acc + (if p.pensionAge then 0 else evenWithheld p.p2Rate p.wages)) 0
  Out.make c "EE" "EUR" (euros tax) (employeeSocial := euros soc) (benefits := euros ben)
    (detail := [Out.d "taxableIncome" (euros (sumBy outs (·.taxable))),
      Out.d "taxBeforeCredits" (euros tax),
      Out.d "basicExemption" (euros (sumBy outs (·.exemption))),
      ("persons", Json.arr (outs.map pjson).toArray),
      Out.d "companyCITonDividends" (euros cit),
      Out.d "singleParentAllowanceIfEligible" (euros spIfElig),
      Out.d "withheldEvenMonthlyWages" (euros wh),
      Out.d "oecdNoPillar2_incomeTax" (euros (sumBy oecd (·.tax))),
      Out.d "oecdNoPillar2_taxable" (euros (sumBy oecd (·.taxable))),
      Out.d "oecdNoPillar2_employeeSocial" (euros (sumBy oecd POut.social)),
      Out.d "monthlySettlement" (match monthlyList c with
        | some ws => euros (yearSettlement p2rate (ws.map cents)) | none => 0),
      Out.d "monthlyWithheld" (match monthlyList c with
        | some ws => euros (yearWithheld true p2rate (ws.map cents)) | none => 0),
      Out.dStr "pillar2" s!"{p2rate} bp of wages (KoPS § 9; input pillar2Rate)",
      Out.dStr "note" "amounts computed in cents; dividends = Estonian dividends after the company's 22/78 CIT (companyCITonDividends), counted in the § 23(3) hump income; rentalIncome = residential rent less 20 % (§ 39^1)"])
    (unsupported := ["single-parent child allowance (PHS § 19) only with otherParentUnrecorded=true",
      "elatis/maintenance, vanemahüvitis (parental benefit), housing and subsistence benefits not modelled",
      "foreign income and credits (§ 45), investment-account deferral (§ 17^2) and capital losses not modelled",
      "pension age taken as age ≥ 65 (RPKS § 7: 64 y 9 m for those born 1961)"]
      ++ (if c.year ≤ 2024 then ["years 2022-2024: the pension-age exemption, the FIE minimum/maximum social-tax "
        ++ "bases and the withholding detail use the 2025 amounts"] else []))

def country : Country := { code := "EE", name := "Estonia", currency := "EUR", year := "2025", compute := out }

end EeTax
