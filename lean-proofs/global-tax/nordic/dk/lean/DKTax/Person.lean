import DKTax.Params

/-!
# One person's income measures (PSL §§ 1-4 a, AMBL §§ 1-4, LL §§ 8 A, 9 J, 9 K, 9 L, 13)

The Danish base is built in this order (Skatteministeriet, "Skatteberegningseksempel for en ugift skatteyder i
2023", Tabel 1-2, which this file follows line by line; numbers in brackets are that table's line numbers):

1. AMBL § 2, stk. 1, nr. 1: arbejdsmarkedsbidrag on pay; the employee's ATP and own pension contribution to an
   employer-administered scheme are not part of the base ("[4] Arbejdsmarkedsbidragsgrundlag [1]-[2]-[3]");
   AMBL § 4: self-employed pay it on business profit. `amRate` = 8 pct. Rounded down to whole kroner as in the
   worked example ("8 pct. af [4]": 706.114 → 56.489).
2. PSL § 3: personlig indkomst = pay after the contribution ("[6] = [4]-[5]") + business profit after it +
   pensions + taxable group life premium − private ratepension (PSL § 3, stk. 2, nr. 3; PBL § 18, capped by
   PBL § 16, stk. 2).
3. PSL § 4: kapitalindkomst = interest income − interest expense.
4. PSL § 4 a: aktieindkomst (dividends and gains on listed shares); PSL § 4 a, stk. 5: not in taxable income.
5. Ligningsmæssige fradrag: LL § 9 J beskæftigelsesfradrag (base = AM base + ATP of employee and employer +
   pension contributions of employee and employer, "[31] I alt"), § 9 J, stk. 3 extra for enlige forsørgere,
   § 9 K jobfradrag, § 9 L ekstra pensionsfradrag (base: private ratepension + 92 % of ATP and employer-scheme
   contributions, "[38]"), § 13 union fees (capped) and unemployment insurance, § 8 A gifts (capped), commuting
   (LL § 9 C, taken as given).
6. Skattepligtig indkomst = personlig indkomst + kapitalindkomst − ligningsmæssige fradrag (PSL § 1, "[26]").

`oecd := true` switches to the OECD Taxing Wages conventions for Denmark found in this work (FINDINGS F3):
the employee ATP contribution stays in the AM base and in personal income and is deducted only from taxable
income; no arbejdsmarkedsbidrag on employer pension contributions.
-/

namespace DKTax
open TaxKernel

/-- One taxpayer's inputs (whole kroner a year). -/
structure PIn where
  age : Nat := 40
  /-- gross pay ("Bruttoløn") -/
  wages : Int := 0
  /-- employee's own contribution to an employer-administered pension scheme (PBL § 19), withheld from pay -/
  ownPension : Int := 0
  /-- employer's contribution to that scheme (PBL § 19; not part of pay) -/
  employerPension : Int := 0
  atpOwn : Int := 0
  atpEmployer : Int := 0
  /-- profit of a business outside virksomhedsordningen (PSL § 3, AMBL § 4) -/
  selfEmp : Int := 0
  /-- pension income (personal income, no arbejdsmarkedsbidrag) -/
  pension : Int := 0
  /-- pension fund's group life premium taxed as pay ("[7]") -/
  groupLife : Int := 0
  /-- private ratepension contributions (PBL § 18) -/
  ratepension : Int := 0
  interestIncome : Int := 0
  interestExpense : Int := 0
  /-- aktieindkomst (may be negative) -/
  aktie : Int := 0
  union : Int := 0
  akasse : Int := 0
  /-- befordringsfradrag incl. any tillæg (LL § 9 C), as computed elsewhere -/
  commute : Int := 0
  otherDed : Int := 0
  gifts : Int := 0
  /-- enlig forsørger receiving ekstra børnetilskud (LL § 9 J, stk. 3) -/
  singleParent : Bool := false
  deriving Repr, Inhabited

/-- One taxpayer's income measures (whole kroner). -/
structure PBase where
  amBase : Int
  am : Int
  /-- arbejdsmarkedsbidrag withheld from employer-scheme pension contributions (not in pay; detail only) -/
  amPension : Int
  personal : Int
  ratepenDed : Int
  kapital : Int
  aktie : Int
  bfBase : Int
  bf : Int
  enlig : Int
  job : Int
  pensDed : Int
  union : Int
  gifts : Int
  lmf : Int
  taxable : Int
  deriving Repr, Inhabited

/-- LL § 9 L, stk. 3: 32 pct. "fra og med det 15. indkomstår før det indkomstår, hvor personen når den
folkepensionsalder ... der gælder for den pågældende". Folkepensionsalder by year of birth (lov om social pension
§ 1 a as we read it, refs/PARAMS.md): 67 to 1962, 68 for 1963-66, 69 for 1967-70, 70 from 1971. -/
def pensionAge (birthYear : Int) : Int :=
  if birthYear ≤ 1962 then 67 else if birthYear ≤ 1966 then 68 else if birthYear ≤ 1970 then 69 else 70

def highPensionRate (year : Nat) (age : Nat) : Bool :=
  let by_ : Int := (year : Int) - age
  by_ + pensionAge by_ - 15 ≤ (year : Int)

/-- A percentage of a base, capped: `min cap (rate × base)`, rounded to the nearest krone as in Skatteministeriet's
worked example (ægtepar 2023 "[33] 10,65 pct. af [32]": 391.912 → 41.739; "[40]": 57.839 → 6.941). -/
def pctCapped (rate base cap : Int) : Int := min cap (divR .halfUp (rate * pos base) BP)

def personBase (P : Params) (oecd : Bool) (x : PIn) : PBase :=
  let amBase := if oecd then x.wages else x.wages - x.ownPension - x.atpOwn
  let amWage := P.amRate * amBase / BP
  let amSE := P.amRate * x.selfEmp / BP
  let am := amWage + amSE
  let amPension := if oecd then 0 else P.amRate * (x.ownPension + x.employerPension) / BP
  let ratepenDed := min x.ratepension P.ratepenCap
  let personal := (amBase - amWage) + (x.selfEmp - amSE) + x.pension + x.groupLife - ratepenDed
  let kapital := x.interestIncome - x.interestExpense
  -- LL § 9 J, stk. 1: "grundlaget for arbejdsmarkedsbidrag" + pension contributions with bortseelsesret + ATP
  let bfBase := amBase + x.selfEmp + (x.atpOwn + x.atpEmployer) + (x.ownPension + x.employerPension)
  let bf := pctCapped P.bfRate bfBase P.bfCap
  let enlig := if x.singleParent then pctCapped P.enligRate bfBase P.enligCap else 0
  let job := pctCapped P.jobRate (bfBase - P.jobStart) P.jobCap
  -- LL § 9 L, stk. 1 (Skatteministeriet's example "[38] = [34]+[35]-[36]+[37]")
  let sch := x.atpOwn + x.atpEmployer + x.ownPension + x.employerPension
  let pensBase := min P.pensCap (ratepenDed + sch - P.amRate * sch / BP)
  let pensDed := divR .halfUp ((if highPensionRate P.year x.age then P.pensRateHigh else P.pensRateLow) * pos pensBase) BP
  let union := min x.union P.unionCap
  let gifts := min x.gifts P.giftCap
  let lmf := bf + enlig + job + pensDed + union + x.akasse + x.commute + x.otherDed + gifts
    + (if oecd then x.atpOwn else 0)
  { amBase, am, amPension, personal, ratepenDed, kapital, aktie := x.aktie, bfBase, bf, enlig, job, pensDed,
    union, gifts, lmf, taxable := personal + kapital - lmf }

end DKTax
