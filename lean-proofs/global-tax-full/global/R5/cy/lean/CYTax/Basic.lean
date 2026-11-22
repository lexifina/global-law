import TaxKernel
import CYTax.Params

/-!
# Cyprus 2025: income tax (ITL 118(I)/2002), Special Contribution for Defence (SDC 117(I)/2002), GESY (89(I)/2001),
# social insurance (SIL 59(I)/2010), child benefit and single-parent benefit (CBL 167(I)/2002)

Money in euro cents throughout (the Tax Department computes to the cent); the exe writes euros with two decimals.
Individual taxation: each adult is a separate taxpayer (ITL art. 5: "φόρος … επί του φορολογητέου εισοδήματος
οποιουδήποτε προσώπου"; there is no joint return). Household investment income, donations and pension
contributions are split equally between two adults (contract; `half1`/`half2` on cents).

Order of computation for one person (ITL):
1. income = wages − art. 8(21Α)/(23Α) exemption + self-employment + pension + 80 % of gross rent (art. 9(2));
   interest (art. 8(19)), dividends (art. 8(20)) and gains on securities (art. 8(22)) are exempt from income tax;
2. − donations (art. 9(1)(στ)) = taxable income before art. 14;
3. − art. 14 deductions (social insurance, GESY, provident/pension fund), at most one fifth of step 2 (art. 14
   proviso (ii));
4. Second Schedule para 1(β) scale, rounded half up to the cent.
SDC and GESY on investment income are separate levies (reported under `surtaxes`).
-/

namespace CYTax
open TaxKernel Lean

/-- `x × r / 10000` rounded half up to the cent (x in cents, r in basis points). -/
def mulBp (x r : Int) : Int := divR .halfUp (x * r) 10000

/-- A money field of a JSON object in cents (exact for amounts given to the cent; half up beyond). -/
def centsOf (j : Json) (k : String) : Int :=
  match j.getObjVal? k with
  | .ok (.num n) =>
    let d : Int := (10 : Int) ^ n.exponent
    (2 * n.mantissa * 100 + d) / (2 * d)
  | _ => 0

def strOf (j : Json) (k : String) : String :=
  match j.getObjVal? k with
  | .ok (.str s) => s
  | _ => ""

def boolOf (j : Json) (k : String) : Bool :=
  match j.getObjVal? k with
  | .ok (.bool b) => b
  | _ => false

/-- One taxpayer's inputs (cents). `ex` = "21A" | "23A" | "" (ITL art. 8 first-employment exemptions; a status the
input states, not an election). -/
structure Person where
  w : Int := 0
  s : Int := 0
  p : Int := 0
  i : Int := 0
  d : Int := 0
  r : Int := 0
  g : Int := 0
  c : Int := 0
  pc : Int := 0
  ex : String := ""
  deriving Repr, Inhabited

/-- Options: the printed statutory SI rates instead of the applied ones; non-domiciled (SDC Law art. 2: "κάτοικος της
Δημοκρατίας" for SDC means resident AND domiciled). -/
structure Opts where
  statuteSI : Bool := false
  nonDom : Bool := false
  year : Nat := 2025
  deriving Repr, Inhabited

/-- ITL art. 8(21Α) and 8(23Α). -/
def exemption (ex : String) (w : Int) : Int :=
  if ex == "21A" then min (mulBp w ex21ARate) ex21ACap
  else if ex == "23A" then (if w > ex23AThreshold then mulBp w ex23ARate else 0)
  else 0

/-- SIL art. 5(1): employee contribution on insurable earnings up to the ceiling. -/
def siEmployee (o : Opts) (w : Int) : Int :=
  mulBp (min (pos w) (siCeilingFor o.year)) (siEmployeeRateFor o.year o.statuteSI)

/-- SIL art. 12: self-employed contribution; base = profit up to what is left of the ceiling (simplification:
the statute's notional minimum income per occupation is not modelled). -/
def siSelf (o : Opts) (w s : Int) : Int :=
  mulBp (min (pos s) (pos (siCeilingFor o.year - pos w))) (siSelfRateFor o.year o.statuteSI)

/-- GESY art. 19(4): the €180.000 cap, filled in the order emoluments (employment, self-employment), pensions,
income. Returns the four bases. -/
def gesyBases (w s p inc : Int) : Int × Int × Int × Int :=
  let bw := min (pos w) gesyCap
  let bs := min (pos s) (pos (gesyCap - bw))
  let bp := min (pos p) (pos (gesyCap - bw - bs))
  let bi := min (pos inc) (pos (gesyCap - bw - bs - bp))
  (bw, bs, bp, bi)

/-- GESY contributions of one person: (on earnings and pension, on income). Income = gross interest + dividends +
gross rent (EUROMOD CR §2.7.5.2 "Gross incomes"; gains on securities not counted). -/
def gesy (w s p i d r : Int) : Int × Int :=
  let (bw, bs, bp, bi) := gesyBases w s p (i + d + r)
  (mulBp bw gesyEmployee + mulBp bs gesySelf + mulBp bp gesyPension, mulBp bi gesyIncome)

/-- SDC on one person's investment income: (dividends, interest, rent). -/
def sdc (o : Opts) (x : Person) : Int × Int × Int :=
  if o.nonDom then (0, 0, 0) else
  let total := x.w + x.s + x.p + x.i + x.d + x.r
  let ir := if total ≤ sdcInterestLowLimit then sdcInterestLow else sdcInterest
  (mulBp (pos x.d) sdcDividend, mulBp (pos x.i) ir, divR .halfUp (pos x.r * sdcRentBase * sdcRent) 100000000)

/-- Income tax on taxable income `ti` (cents), Second Schedule 1(β). -/
def scaleTax (ti : Int) : Int := divR .halfUp (scale2025.ticks ti) 10000

structure PersonOut where
  exempt : Int
  si : Int
  gesyEarn : Int
  gesyInc : Int
  ti0 : Int
  art14Claim : Int
  art14Cap : Int
  art14 : Int
  taxable : Int
  tax : Int
  sdcD : Int
  sdcI : Int
  sdcR : Int
  deriving Repr, Inhabited

def person (o : Opts) (x : Person) : PersonOut :=
  let ex := exemption x.ex x.w
  let si := siEmployee o x.w + siSelf o x.w x.s
  let (ge, gi) := gesy x.w x.s x.p x.i x.d x.r
  let rentNet := x.r - mulBp x.r rentDeduction
  let inc := (x.w - ex) + x.s + x.p + rentNet
  let ti0 := pos (inc - pos x.c)
  let claim := si + ge + gi + pos x.pc
  let cap := ti0 * art14CapNum / art14CapDen
  let a14 := min claim cap
  let ti := ti0 - a14
  let (sd, sint, sr) := sdc o x
  { exempt := ex, si, gesyEarn := ge, gesyInc := gi, ti0, art14Claim := claim, art14Cap := cap, art14 := a14,
    taxable := ti, tax := scaleTax ti, sdcD := sd, sdcI := sint, sdcR := sr }

/-- Child benefit per year (cents) for `n` dependent children and gross family income `fam` (CBL Schedule
para 2, 4; 2025 indexed amounts). -/
def childBenefit (n : Nat) (fam : Int) (year : Nat := 2025) : Int :=
  if n = 0 then 0 else
  let row := ((cbTableFor year).getD (min n 4 - 1) [])
  let col : Option Nat :=
    if fam ≤ cbCol1 then some 0 else if fam ≤ cbCol2 then some 1 else if fam ≤ cbCol3 then some 2
    else if fam ≤ cbLimitFor year n then some 3 else none
  match col with
  | none => 0
  | some k => (n : Int) * row.getD k 0

/-- Single-parent benefit per year (cents): CBL Schedule para 8, Table B, monthly per child × 12. -/
def singleParent (single : Bool) (n : Nat) (fam : Int) (year : Nat := 2025) : Int :=
  if !single || n = 0 then 0
  else if fam ≤ spLimitLow then 12 * (n : Int) * (spMonthlyFor year).1
  else if fam ≤ spLimitHigh then 12 * (n : Int) * (spMonthlyFor year).2
  else 0

/-- The household's taxpayers, in cents, from the raw input line. -/
def people (c : Canon) : List Person :=
  let adults : List Json := match c.raw.getObjVal? "adults" with
    | .ok (.arr a) => a.toList
    | _ => []
  let tot (k : String) := centsOf c.raw k
  let n := adults.length
  let share (k : String) (idx : Nat) : Int :=
    if n ≤ 1 then tot k else if idx = 0 then half1 (tot k) else half2 (tot k)
  (adults.zipIdx).map fun (a, idx) =>
    { w := centsOf a "wages", s := centsOf a "selfEmployment", p := centsOf a "pension",
      i := share "interest" idx, d := share "dividends" idx, r := share "rentalIncome" idx,
      g := share "capitalGains" idx, c := share "charitable" idx, pc := share "pensionContributions" idx,
      ex := strOf a "cyFirstEmployment" }

def optsOf (args : List String) (c : Canon) : Opts :=
  { statuteSI := args.contains "--statute-si", nonDom := args.contains "--non-dom" || boolOf c.raw "cyNonDom",
    year := if c.year ≥ 2022 && c.year ≤ 2024 then c.year else 2025 }

/-- Gross family income for the child benefit (CBL Schedule para 2: "ετήσιο ακαθάριστο οικογενειακό εισόδημα";
EUROMOD CR §2.6.2.3: wages, pensions, capital income, rents). Same-year income stands in for the previous year's. -/
def familyIncome (ps : List Person) : Int :=
  ps.foldl (fun a x => a + x.w + x.s + x.p + x.i + x.d + x.r) 0

def sumBy (l : List PersonOut) (f : PersonOut → Int) : Int := l.foldl (fun a x => a + f x) 0

def outWith (args : List String) (c : Canon) : Out :=
  let o := optsOf args c
  let ps := people c
  let rs := ps.map (person o)
  let n := c.childrenUnder childAgeLimit
  let fam := familyIncome ps
  let cb := childBenefit n fam o.year
  let sp := singleParent (ps.length == 1) n fam o.year
  let it := sumBy rs (·.tax)
  let pd (k : String) (f : PersonOut → Int) : List (String × Json) :=
    (rs.zipIdx).map fun (r, idx) => Out.d s!"p{idx + 1}_{k}_cents" (f r)
  Out.make c "CY" "EUR" it
    (surtaxes := [("SDC_dividends", sumBy rs (·.sdcD)), ("SDC_interest", sumBy rs (·.sdcI)),
                  ("SDC_rent", sumBy rs (·.sdcR)), ("GESY_income", sumBy rs (·.gesyInc))])
    (employeeSocial := sumBy rs (·.si) + sumBy rs (·.gesyEarn))
    (benefits := cb + sp)
    (detail := [Out.d "taxableIncome_cents" (sumBy rs (·.taxable)), Out.d "SI_cents" (sumBy rs (·.si)),
                Out.d "GESY_earnings_cents" (sumBy rs (·.gesyEarn)), Out.d "childBenefit_cents" cb,
                Out.d "singleParent_cents" sp, Out.d "familyIncome_cents" fam]
      ++ pd "taxable" (·.taxable) ++ pd "tax" (·.tax) ++ pd "art14" (·.art14) ++ pd "art14Cap" (·.art14Cap)
      ++ pd "art14Claim" (·.art14Claim) ++ pd "exempt" (·.exempt) ++ pd "ti0" (·.ti0))
    (unsupported := ["life-insurance premiums (art. 14(1))", "art. 20 foreign-pension option, art. 20A widow's pension",
      "self-employed SI notional minimum incomes", "child benefit: asset test, residence test, previous-year income",
      "children 18-20 in education / National Guard", "SDC deemed dividend distribution (company side)",
      "monthly SI ceiling with a 13th salary (annual cap used)"] ++
      (if o.year < 2025 then ["tax year " ++ toString o.year ++ ": SI rates and ceiling, child and single-parent benefit amounts and limits are year-specific; SDC rates and the art. 8(21Α)/(23Α) statuses use the 2025 text (the 23Α threshold changed in 2022)"] else []))

def out (c : Canon) : Out := outWith [] c

def country : Country :=
  { code := "CY", name := "Cyprus", currency := "EUR", year := "2025", compute := out, computeWith := outWith }

end CYTax
