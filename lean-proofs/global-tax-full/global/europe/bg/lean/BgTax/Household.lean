import BgTax.Benefit

/-!
# The canonical household (`cmp/shared/CONTRACT.md`) under Bulgarian law

* Unit: each adult is taxed alone (ЗДДФЛ has no joint assessment); marriage changes nothing except that the child
  relief is shared between the parents (чл. 22в, ал. 4, any two parents, married or not).
* Household totals (rent, dividends, donations, voluntary pension contributions) are split equally (`half1/half2`).
* `interest`: deposits with EU/EEA banks, exempt (чл. 13, ал. 1, т. 8). `capitalGains`: listed shares sold on a
  regulated market, exempt (чл. 13, ал. 1, т. 3). Both enter neither the tax nor the allowance's income test.
* `selfEmployment`: a free profession (25 % statutory expenses, чл. 29, ал. 1, т. 3); input field
  `"bgSelfEmployment": "author"` uses 40 % (т. 2).
* Amounts in stotinki inside; the exe (`Main.lean`) writes leva with two decimals.
-/

namespace BgTax
open TaxKernel Lean

/-- Children counted for the child relief and the allowance: under 18 at the start of 2025 (the relief also applies
"включително за годината, в която детето ... навършило е пълнолетие", чл. 22в, ал. 7). -/
def reliefChildren (c : Canon) : Nat := (c.children.filter (·.age < 18)).length

def toPerson (a : Adult) (rent div vol don : Int) : PersonIn :=
  { age := a.age, wages := a.wages * LEV, selfEmployment := a.selfEmployment * LEV, pension := a.pension * LEV,
    rent := rent * LEV, dividends := div * LEV, volPension := vol * LEV, donations := don * LEV }

/-- The persons of the household with their shares of the household totals. -/
def persons (c : Canon) : List PersonIn :=
  match c.adults with
  | [a] => [toPerson a c.rentalIncome c.dividends c.pensionContributions c.charitable]
  | a :: b :: _ =>
    [toPerson a (half1 c.rentalIncome) (half1 c.dividends) (half1 c.pensionContributions) (half1 c.charitable),
     toPerson b (half2 c.rentalIncome) (half2 c.dividends) (half2 c.pensionContributions) (half2 c.charitable)]
  | [] => []

/-- The free-profession expense rate chosen by the input (default 25 %). -/
def seExpenseOf (c : Canon) : Int :=
  if c.str? "bgSelfEmployment" == some "author" then authorExpenseRate else freelanceExpenseRate

/-- Everything the household owes and receives (stotinki). -/
structure HhResult where
  calcs : List PersonCalc
  childUsed : List Int
  pits : List Int
  incomeTax : Int
  dividendTax : Int
  employeeSocial : Int
  allowance : Int
  grants : Int
  testIncome : Int
  members : Nat
  deriving Repr, Inhabited

def household (c : Canon) (es : Bool := false) (em : Bool := false) : HhResult :=
  let ps := persons c
  let y := c.year
  let cs := ps.map fun p => calcPerson p (seExpenseOf c) y es em
  let r := if em then childReliefJ y (reliefChildren c) else childRelief (reliefChildren c)
  let used := match cs with
    | [a] => [min (pos r) a.room]
    | [a, b] => let (u1, u2) := splitRelief r a.room b.room; [u1, u2]
    | _ => cs.map fun _ => 0
  let pits := (cs.zip used).map fun (k, u) => k.pit u
  let divTax := sumInts (cs.map (·.dividendTax))
  let ss := sumInts (cs.map fun k => k.eeSocial + k.seSocial)
  -- allowance: income per member (ЗСПД § 1, т. 2 ДР: gross taxable incomes and pensions)
  let inc := sumInts (ps.map fun p => pos p.wages + pos p.selfEmployment + pos p.pension + pos p.rent
    + pos p.dividends)
  let n := reliefChildren c
  let members := c.adults.length + n
  let allow := if em then allowanceYearJ y n members inc else allowanceYearY y n members inc
  let grants := schoolGrant * ((if es then schoolGrantChildrenE y (c.children.map (·.age))
    else schoolGrantChildrenY y (c.children.map (·.age))) : Int)
  { calcs := cs, childUsed := used, pits, incomeTax := sumInts pits + divTax, dividendTax := divTax,
    employeeSocial := ss, allowance := allow, grants, testIncome := inc, members }

/-- A detail entry in leva with two decimals. -/
def dLev (k : String) (st : Int) : String × Json := (k, Json.num ⟨st, 2⟩)

/-- `--eurostat`: Eurostat earn_net ESMS 3.4 convention (contribution ceiling and self-insured minimum of 1 January
all year; the most generous school grant for children aged 6-11). Not statute. -/
def outWith (args : List String) (c : Canon) : Out :=
  let es := args.contains "--eurostat"
  let em := args.contains "--euromod"
  let h := household c es em
  let taxable := sumInts (h.calcs.zip h.childUsed |>.map fun (k, u) => pos (k.room - min u k.room))
  Out.make c "BG" "BGN" h.incomeTax (employeeSocial := h.employeeSocial) (benefits := h.allowance + h.grants)
    (detail := [dLev "taxableIncome" taxable, dLev "sumOfAnnualBases" (sumInts (h.calcs.map (·.sumBases))),
      dLev "childRelief" (sumInts h.childUsed), dLev "pitAnnual" (sumInts h.pits),
      dLev "dividendFinalTax" h.dividendTax,
      dLev "employeeContributions" (sumInts (h.calcs.map (·.eeSocial))),
      dLev "selfInsuredContributions" (sumInts (h.calcs.map (·.seSocial))),
      dLev "childAllowance" h.allowance, dLev "schoolGrants" h.grants,
      dLev "allowanceIncomePerMemberMonthly" (if h.members = 0 then 0 else h.testIncome / 12 / (h.members : Int)),
      Out.dStr "units" "BGN with stotinki; the annual balance is rounded to the lev only when paid (ZDDFL art. 48(8))"])
    (unsupported := ["health contributions of residents with no insured activity (ZZO art. 40(1) item 4?)",
      "minimum insurable income by occupation for employees (ZBDOO 2025 annexes 1/1A)",
      "optional sickness/maternity insurance of the self-insured (KSO art. 4(4)) not taken",
      "disability reliefs (ZDDFL arts. 18, 22g), young-family mortgage relief (art. 22a)",
      "one-off birth, pregnancy and first-year allowances (ZSPD arts. 5a, 6, 8)",
      "interest other than on EU/EEA bank deposits or bonds (taxable under art. 35)"] ++
      (if c.year < 2022 then ["tax year before 2022: computed with the 2022 parameters"] else []) ++
      (if es then ["--eurostat: Eurostat earn_net ESMS 3.4 convention, not statute (January ceiling and self-insured minimum all year; school grant for every child aged 6-11)"] else []) ++
      (if em then ["--euromod: EUROMOD 30 June convention, not statute (ceiling, self-insured minimum and child-allowance limits and amounts of June all year; 2022 child relief 4 500 / 9 000 / 13 500 lv. as in force on 30 June 2022)"] else []))

def out (c : Canon) : Out := outWith [] c

def country : Country :=
  { code := "BG", name := "Bulgaria", currency := "BGN", year := "2025", compute := out, computeWith := outWith }

end BgTax
