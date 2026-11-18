import UsLoop.Scenarios

/-!
# Headline loopholes, kernel-checked (tax year 2025)

Each theorem evaluates the model (`TaxCode.Individual`, read-only copy) on the households of `UsLoop.Scenarios` with
`decide`, so the kernel itself computes both returns. No `native_decide`, no `sorry`. The catalogue and the scripted
checks for every other item are in `../CATALOGUE.md` and `../scripts/`.
-/

namespace UsLoop
open TaxCode.Individual

/-- K03 carried interest: $1m taken as long-term gain instead of a fee saves $151,955 (37% + SE/Medicare against
20% + 3.8% NIIT; §1(h)(1)(D), §1411, §1401, §1061). -/
theorem carried_interest :
    (form1040F { qbiSstb := true } ciFee).netTax - (form1040F {} ciCarry).netTax = 151955 := by decide

/-- K20 §199A(b)(2)(B): an S-corporation owner with $1m of profit and no employees pays $27,116 less (income tax plus
both FICA halves) with a $280,000 salary than with none, because the W-2 wage limit (50% of wages) otherwise
removes the 20% deduction; $280k is the best salary on a $5k grid (`scripts/catalogue.py`), ~28% of profit. -/
theorem scorp_wage_limit :
    scorpBurden 1000000 0 - scorpBurden 1000000 280000 = 27116 ∧
    scorpBurden 1000000 280000 < scorpBurden 1000000 275000 ∧
    scorpBurden 1000000 280000 < scorpBurden 1000000 285000 := by decide

/-- K22 S corporation vs sole proprietorship at $200k (single, non-SSTB): an $80k salary saves $10,434 of payroll
and income tax (§1401 on all profit vs §§3101, 3111 on the salary only; Rev. Rul. 74-44 requires the salary to be
reasonable). -/
theorem scorp_vs_schedule_c :
    (form1040F {} soleProp).netTax - scorpSingleBurden 200000 80000 = 10434 := by decide

/-- K32 pass-through entity tax (Notice 2020-75): $6,896 saved; the entity-level deduction also takes MAGI from
$550,000 to $522,500, which lifts the §164(b)(7)(B) cap from $25,000 to $33,250. -/
theorem ptet_workaround :
    (form1040F ptetFacts ptetNo).netTax - (form1040F ptetFacts ptetYes).netTax = 6896 := by decide

/-- N1 separate returns for the child tax credit: $365k + $215k with four children on the lower earner's return
pay $6,512 less than the joint return, because §24(b)(2) measures the phase-out on the claiming spouse's MAGI only
($200,000 'any other case' against $400,000 joint) and the brackets below 37% are exactly halved for separate
returns. -/
theorem ctc_separate_returns :
    (form1040F {} ctcJoint).netTax - ((form1040F stdOnly ctcSepA).netTax + (form1040F stdOnly ctcSepB).netTax)
      = 6512 := by decide

/-- K25b marriage penalty: two $25k earners with two children pay $3,665 more married (EIC on $50,000 joint
against EIC on $25,000 with head-of-household status; §32(b), §2(b), §7703). -/
theorem marriage_penalty_eic :
    (form1040F {} mpJoint).netTax - ((form1040F {} mpHoh).netTax + (form1040F {} mpSingle).netTax) = 3665 := by
  decide

/-- T2 a retired couple aged 67 receives $149,400 ($40,000 Social Security + $109,400 long-term gains) with no
federal income tax; $100 more gain costs $15 (§1(h)(1)(B) 0% band, §63(c), §63(f), §151(d)(5)(C), §86). -/
theorem retired_zero_tax :
    (form1040F {} (retired 109400)).netTax = 0 ∧ (form1040F {} (retired 109500)).netTax = 15 := by decide

/-- K27 the EIC investment-income cliff: $1 of interest over $11,950 costs $2,151 (§32(i)(1)). -/
theorem eic_cliff : (form1040F {} (eicAt 11951)).netTax - (form1040F {} (eicAt 11950)).netTax = 2151 := by decide

/-- T1 the §86 torpedo with the senior deduction's phase-out: $1,000 more IRA withdrawal at $46,500 costs $440 (44%)
against $407 (40.7% = 22% × 1.85) without the senior deduction (§86(a)(2), §151(d)(5)(C)(iii): 6% of MAGI over
$75,000, MAGI including the extra taxable benefits). -/
theorem torpedo_senior :
    (form1040F {} (torpedo 47500)).netTax - (form1040F {} (torpedo 46500)).netTax = 440 ∧
    (form1040F noSenior (torpedo 47500)).netTax - (form1040F noSenior (torpedo 46500)).netTax = 407 := by decide

/-- K04 0% gain harvesting: a couple with $80k of wages realizes $48,200 of long-term gain at no tax. -/
theorem gain_harvest :
    (form1040F {} (harvest 48200)).netTax = (form1040F {} (harvest 0)).netTax ∧
    (form1040F {} (harvest 48300)).netTax > (form1040F {} (harvest 0)).netTax := by decide

/-- K21 an SSTB owner at $450k MFJ: a $23,500 401(k) deferral saves $9,024 (38.4%) in the 32% bracket, because it
also restores §199A deduction lost in the §199A(d)(3) phase-in. -/
theorem sstb_deferral :
    (form1040F sstbFacts (sstb 150000)).netTax - (form1040F sstbFacts (sstb 126500)).netTax = 9024 := by decide

end UsLoop
