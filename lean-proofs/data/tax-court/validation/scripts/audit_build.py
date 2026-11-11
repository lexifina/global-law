"""Build validation/audit_matches.json from hand classifications of every verdict.

Classes for matches:
  A computed (sub-flag trivial-arithmetic), B rule-from-judgment-input,
  C echo/tautology, D inferred-from-answer.
Spot-checked items carry flag "spot-checked" (opinion text grepped with audit_grep.py).
"""
import json, glob, os, collections

ENC = r'C:\Users\alany\Documents\tax-formalization-data\taxcourt\encoded'
OUT = r'C:\Users\alany\Documents\tax-formalization-data\taxcourt\validation\audit_matches.json'

T = 'trivial-arithmetic'; S = 'spot-checked'
# (id, issue index): (class, items, flags, inferred_facts, evidence)
M = {
 ('tcmemo-2019-41', 0): ('A', ['premiumTaxCredit', 'excessAdvancePtc', 'householdIncome', 'povertyLine'],
    [S, 'hidden-item-mismatch', 'outcome-stipulated', 'excess-equals-input-APTC'], [],
    'Opinion: "parties have stipulated that $70,065.80 exceeds 400%" of FPL. Lean householdIncome 75,509 vs court 70,066, yet verdict match.'),
 ('tcmemo-2019-41', 2): ('C', ['wages', 'unemployment'], ['concession'], [],
    'Diagnosis: "no court amount to compare, so this is a fact-level check only."'),
 ('tcmemo-2019-83', 0): ('B', ['rolloverIncludible'], [S, 'rule-trivial (days<=60)'], [],
    'Opinion: check received "58 days after petitioner received the IRA distribution"; bookkeeping-error finding encoded as days 58.'),
 ('tcmemo-2020-101', 0): ('B', ['rolloverIncludible'], ['judgment-input (waiverGranted false)', 'output-equals-input'], [],
    'Waiver refusal encoded as waiverGranted false; includible = the 15,000 rolled amount.'),
 ('tcmemo-2020-101', 2): ('A', ['earlyDistributionTax'], [S, T], [],
    'Opinion: "additional tax of $5,051 (10% x $50,507)"; 3,993 exception amount is a judgment input.'),
 ('tcmemo-2022-77', 0): ('C', ['alimonyDeduction'], ['conclusion-encoded-as-fact (childSupport = paid)'], [],
    'childSupport set to the whole 69,888 payment, which forces deduction 0; diagnosis: "legal characterisation, encoded as the childSupport fact, not computed".'),
 ('tcmemo-2022-77', 1): ('C', ['accuracyPenalty'], ['concession'], [],
    'Diagnosis: "Concession, not a computed holding; encoded as expected 0 for completeness."'),
 ('tcmemo-2023-141', 1): ('A', ['earlyDistributionTax'], [S, T], [],
    'Opinion: additional tax of $1,439 under 72(t); 10% x stated 14,386.'),
 ('tcmemo-2023-2', 0): ('A', ['taxableSocialSecurity', 'agi', 'householdIncome'], [S, T, 'reproduces-return-figures'], [],
    'Opinion: AGI $91,274 = pensions $68,750 + taxable SS $22,524; 85% cap of 26,499; MAGI 95,249 a sum.'),
 ('tcmemo-2023-2', 1): ('A', ['premiumTaxCredit', 'excessAdvancePtc', 'povertyLine', 'fplPercent'], [S, 'hidden-item-mismatch (fplPercent 598 vs 401, convention)', 'excess-equals-input-APTC'], [],
    'Opinion: "household income of $95,249 was 598% of the FPL"; Lean prints 401 (Form 8962 convention).'),
 ('tcmemo-2023-2', 3): ('A', ['deficiency'], [S, T, 'duplicate-of-issue-1', 'deficiency-equals-input-APTC'], [],
    'All other facts identical as filed and corrected, so deficiency = APTC input 7,205.'),
 ('tcmemo-2023-37', 0): ('A', ['taxableSocialSecurity'], [S, 'plug: otherIncome residual 6,724 reproduces stated MAGI'], [],
    'Opinion computes "$27,981" uncapped vs "$27,887 ($32,808 x 0.85)"; MAGI 53,456 stated. Lean redoes the court\'s two-tier arithmetic.'),
 ('tcmemo-2023-37', 1): ('C', ['agi'], ['expected-not-stated-by-court', 'derived-from-model-output'], ['otherIncome -1,465 residual (character not stated)'],
    'Diagnosis: "Expected AGI is derived (court\'s MAGI + taxable SS), not stated."'),
 ('tcmemo-2023-37', 2): ('C', ['ordinaryDividends'], ['concession'], [], 'Diagnosis: "Concession encoded as a fact."'),
 ('tcmemo-2023-37', 3): ('C', ['pensions'], ['concession'], [], 'Diagnosis: "IRS concession encoded by leaving taxable pensions as reported."'),
 ('tcmemo-2024-20', 0): ('B', ['qualifyingChild:AV', 'eicChild:AV'], [S, 'assumed-age-17'], [],
    'Opinion: "A.V. lived with petitioner for approximately 60 days during 2020"; abode test 120 <= 366.'),
 ('tcmemo-2024-20', 1): ('B', ['hohQualifyingPerson:AV', 'filingStatus'], ['assumed-fact (paidOverHalfHouseholdCost true, not found)', 'follows-from-issue-0'], [],
    'Note: "paidOverHalfHouseholdCost not found; set true so that the abode finding alone decides".'),
 ('tcmemo-2024-23', 2): ('C', ['taxableInterest', 'ordinaryDividends'], ['concession'], [], 'Diagnosis: "Concession encoded".'),
 ('tcmemo-2024-23', 3): ('C', ['accuracyPenalty'], ['concession', 'nothing-computed'], [], 'Diagnosis: "Concession; nothing to compute."'),
 ('tcmemo-2024-67', 1): ('D', ['taxableIncome', 'regularTax'], [S], ['capital gain 32,227 taxed as ordinary (longTermGain 0): character not stated, chosen to reproduce 60,569'],
    'Note: "IRS taxed the capital gain at ordinary rates (60,569 = ordinary tax on 242,512), so longTermGain 0." Opinion never states gain character.'),
 ('tcmemo-2024-67', 2): ('D', ['regularTax (mfs variant)'], [S], ['longTermGain 0 as above'],
    'Opinion itself states single and MFS rates give the same tax; Lean reruns with the same back-solved inputs.'),
 ('tcmemo-2024-67', 3): ('A', ['earlyDistributionTax'], [T], [], '10% x 2,417 = 241.70.'),
 ('tcmemo-2024-67', 4): ('D', ['deficiency', 'totalTax'], [S], ['longTermGain 0 as above'], 'Deficiency 60,811 = regular tax (inferred character) + 242.'),
 ('tcmemo-2024-67', 5): ('A', ['failureToFile'], [S, T, 'notice-figure-as-input (sfrTax 60,811; stated in opinion)'], [],
    'Opinion: withholding $42,961 "generating a net underpayment of $17,850"; FTF = 22.5% x stated 17,850.'),
 ('tcmemo-2024-67', 6): ('A', ['failureToPay'], [S, T, 'notice-figure-as-input (sfrTax; stated)'], [],
    'Opinion: FTP $3,659 "calculated with reference to petitioner\'s net underpayment of $17,850"; 41 months x 0.5%.'),
 ('tcmemo-2024-67', 7): ('D', ['estimatedTaxAddition', 'estimatedRequiredAnnual'], [S, 'tuned-parameter'], ['due dates set to the 15th because that reproduces 424 (printed dates give 422)', 'no prior-year return assumed (opinion silent)'],
    'Diagnosis: "with the statutory ... dates ... 424 = 423.76, so dueDates is set to the 15th."'),
 ('tcmemo-2025-116', 0): ('B', ['qualifyingChild:AngelaDavis', 'eicChild:AngelaDavis'], ['age-test-real (64, not disabled)'], [],
    'Abode and disability "burden-of-proof findings ... encoded as facts"; Lean adds the age/disability test.'),
 ('tcmemo-2025-23', 0): ('C', ['taxableInterest'], ['concession'], [], 'Diagnosis: "Conceded receipt; encoded as fact and included".'),
 ('tcmemo-2025-23', 1): ('C', ['pensions'], ['concession'], [], 'Diagnosis: "Conceded receipt; encoded as pensions".'),
 ('tcmemo-2025-23', 2): ('A', ['earlyDistributionTax'], [S, T], [], 'Opinion: "10% additional tax of $5,667"; 10% x stated 56,673.'),
 ('tcmemo-2025-23', 3): ('D', ['deficiency'], [S], ['filing status single (not in opinion; only status reproducing 18,064)', 'otherIncome 50,514 backed out from TI 37,964 + assumed single standard deduction'],
    'Diagnosis: "Matches only under an INFERRED single filing status". Opinion text: no "single" or "filing status".'),
 ('tcmemo-2025-23', 4): ('D', ['understatement', 'substantialUnderstatement'], ['depends-on-issue-3'], ['single status as above'],
    'Understatement equals the D-class deficiency; threshold test itself is mechanical.'),
 ('tcmemo-2025-23', 5): ('C', ['6751(b) approval'], ['finding-echo (automaticallyCalculated true)'], [], 'Diagnosis: "Court\'s finding encoded as fact."'),
 ('tcmemo-2025-31', 0): ('B', ['qualifyingChild:JMA', 'dependent:JMA'], ['some-real-logic (QR excluded as QC of another)'], [], '0 days with petitioner; no 152(e) release; father\'s qualifying child.'),
 ('tcmemo-2025-31', 1): ('B', ['ctcChild:JMA'], ['follows-from-issue-0'], [], 'Age 16 passes; residency input fails.'),
 ('tcsumm-2019-23', 0): ('B', ['qualifyingChild:JV/LV'], ['assumed-age-16'], [], 'Foster placement finding encoded as relationship fosterChild.'),
 ('tcsumm-2019-23', 1): ('B', ['tieBreaker:JV', 'tieBreaker:LV'], [S, 'real-logic (152(c)(4) higher-AGI tie-breaker)'], [],
    'Opinion: children "treated as the qualifying children of the taxpayer with the higher adjusted gross income"; AGI $12,893.'),
 ('tcsumm-2019-23', 2): ('B', ['dependent:JV/LV'], ['follows-from-issue-0-1'], [], 'Dependency follows from QC + tie-breaker.'),
 ('tcsumm-2019-23', 4): ('B', ['headOfHousehold', 'filingStatus'], ['follows-from-issue-0-1'], [], 'Unmarried; paid all household expenses (finding).'),
 ('tcsumm-2019-23', 5): ('B', ['eicChild:*'], ['follows-from-issue-0-1', 'EIC amount not compared'], [], 'Flags only; EIC amount 5,150 has no court comparator.'),
 ('tcsumm-2019-23', 6): ('B', ['ctcChild:JV/LV'], ['age<17 test (ages assumed 16)'], [], 'Both under 17.'),
 ('tcsumm-2019-24', 0): ('B', ['aotcEligible:ET', 'aotcEligible:EMT'], ['rule-trivial (4 prior years)', 'EMT half is a concession'], [], 'AOTC claimed 2011-2014 -> 25A(i)(2) bar; EMT conceded.'),
 ('tcsumm-2019-29', 0): ('B', ['qualifyingChild/dependent/ctcChild x3'], ['relationship test'], ['ages 9 assumed'], 'Unrelated children fail 152(c)(1)(A); 9 flags from one fact.'),
 ('tcsumm-2019-29', 2): ('B', ['dependent:Steed'], [S, 'assumed support false (not found)', 'legally doubtful (SSI as gross income)'], [],
    'Opinion: "SSI ... $8,796 for the year, which exceeds the section 151(d) exemption amount of $3,800".'),
 ('tcsumm-2019-33', 1): ('A', ['hsaIncludible', 'hsaAdditionalTax'], [S, T, 'judgment-input (no qualified expenses)'], ['age under 65 assumed'],
    'Opinion: "$634 in HSA distributions"; includible = copy, 20% x 634 = 127.'),
 ('tcsumm-2019-33', 2): ('D', ['deficiency'], [S], ['HOH status (not stated)', 'one under-17 CTC child (not stated)', 'taxShown 0 derived'],
    'Note: "HOH with one under-17 child (CTC) reproduces the notice\'s $10,518 exactly". Opinion: no "head of household", no "child".'),
 ('tcsumm-2019-8', 0): ('C', ['taxableInterest', 'agi'], ['concession', 'agi-derived-not-stated'], [], 'Expected AGI note: "derived ... (not stated by the court)".'),
 ('tcsumm-2019-8', 1): ('B', ['gamblingLossDeduction', 'deduction', 'netTax'], ['judgment-input (losses 0)', 'alt-holding: std vs itemized comparison', 'netTax derived not stated'], ['HOH from the 9,250 standard deduction'],
    'Main: unsubstantiated losses encoded 0; alternative compares 2,994 itemized with 9,250 standard.'),
 ('tcsumm-2019-8', 2): ('C', ['iraDeduction'], ['conclusion-encoded-as-fact (ira.contribution 0)'], [], 'Diagnosis: "The characterization ... is the court\'s legal finding taken as input."'),
 ('tcsumm-2020-14', 0): ('A', ['earlyDistributionTax'], [S, T, 'exception-logic (age-55 separation, SEPP)'], ['separation age 43 (opinion: left Rockwell 1987, Northrop 1999; age not stated)'],
    'Opinion: "10% additional tax of $2,517"; 59 but not 59-1/2; separation long before 55.'),
 ('tcsumm-2020-14', 1): ('A', ['deficiency'], [T, 'duplicate-of-issue-0'], [], 'Deficiency is the 72(t) tax alone.'),
 ('tcsumm-2020-18', 1): ('D', ['accuracyPenalty', 'substantialUnderstatement'], [S, T, 'notice-figure-as-input'], ['taxShown 723 back-solved = notice total tax 8,967 - deficiency 8,244'],
    'Note: "tax shown = required - deficiency (derived) ... consistency checks only"; penalty = 20% x stated deficiency.'),
 ('tcsumm-2020-18', 3): ('D', ['accuracyPenalty', 'substantialUnderstatement'], [S, T, 'notice-figure-as-input'], ['taxShown 4,383 back-solved from notice'],
    'Same construction for 2015: 20% x 18,011 = 3,602.20 (respondent\'s table figure).'),
 ('tcsumm-2020-25', 1): ('B', ['qualifyingChild:ADB/JNB'], ['judgment-input (no common-law marriage -> unrelated)'], [], 'Relationship fails on the credibility finding.'),
 ('tcsumm-2020-25', 2): ('B', ['qualifyingRelative:ADB/JNB'], ['judgment-input (support not shown)'], [], 'livedWithWholeYear false and support false encoded as found.'),
 ('tcsumm-2020-25', 3): ('B', ['dependent:ADB/JNB'], ['follows-from-issue-1-2'], [], 'Follows from QC and QR failing.'),
 ('tcsumm-2020-25', 4): ('B', ['headOfHousehold', 'filingStatus'], ['follows-from-issue-1-2'], [], 'Unmarried, no qualifying person -> single.'),
 ('tcsumm-2020-25', 5): ('B', ['ctcNonrefundable', 'refundableCtc'], ['follows-from-issue-1'], [], 'No 152(c) qualifying child.'),
 ('tcsumm-2020-25', 6): ('A', ['eic', 'earnedIncome'], [S, T, 'court-stated-comparison'], [],
    'Opinion: "Mr. Brzyski earned $16,788 ... This amount is above the cap" of $14,880.'),
 ('tcsumm-2020-5', 0): ('A', ['taxableSocialSecurity'], [S, T, 'cap binds by wide margin'], [],
    'Opinion: "$22,790 (representing 85% of the Social Security benefits of $26,812"; wages 50,248 and IRA 17,410 stated.'),
 ('tcsumm-2020-5', 1): ('D', ['lumpSumElection'], [S], ['2014 priorModifiedIncome 43,138: a lower bound back-solved from the petitioners\' own 8,306 figure'],
    'Note: "requires 2014 modified income >= 43,138 ... that lower bound is encoded as priorModifiedIncome."'),
 ('tcsumm-2020-5', 2): ('A', ['earlyDistributionTax'], [S, T, 'expected-not-stated-by-court'], [],
    'Opinion states the 10% rule but no "1,741"; expected is the encoder\'s 10% x 17,410.'),
 ('tcsumm-2020-9', 0): ('B', ['filingStatus', 'headOfHousehold', 'qualifyingChild x2', 'tieBreaker x2'], ['QCs conceded', 'placeholder AGIs 2 vs 1', 'tie-breaker moot (father did not claim)'], ['ages default 0'],
    'Note: "AGIs not stated; 2 vs 1 used ordinally".'),
 ('tcsumm-2020-9', 1): ('B', ['same 7 items, 2015'], ['duplicate-of-issue-0'], ['ages default 0'], 'Identical facts to the 2016 entry.'),
 ('tcsumm-2021-26', 1): ('B', ['ctcChild x3'], [S, 'age test from birth years', 'same-finding-labelled-judgment-in-issue-0'], [],
    'Opinion: "T.G., born in 2000, S.G, born in 2007, and O.G., born in 2010"; residency is a credibility finding.'),
 ('tcsumm-2021-26', 2): ('B', ['eicChild x3'], ['same-finding-labelled-judgment-in-issue-0', 'EIC amount not computed'], [], 'Residency finding decides; tie-breaker not addressed.'),
 ('tcsumm-2021-41', 0): ('B', ['tieBreaker:IME', 'tieBreaker:PAE'], ['real-logic (parent beats non-parent)'], ['days approximate (290, 75)', 'IME age 5 assumed'], 'Parent claimant wins under 152(c)(4)(A)(i).'),
 ('tcsumm-2021-41', 1): ('B', ['dependent', 'qualifyingRelative'], ['follows-from-issue-0'], [], '152(d)(1)(D): qualifying child of another.'),
 ('tcsumm-2021-41', 2): ('B', ['hohQualifyingPerson', 'filingStatus'], ['follows-from-issue-0'], [], 'No qualifying person -> single.'),
 ('tcsumm-2021-41', 3): ('B', ['ctcChild', 'refundableCtc'], ['follows-from-issue-0'], [], 'No qualifying child.'),
 ('tcsumm-2021-41', 4): ('A', ['eic'], [S, T, 'court-stated-comparison', 'AGI encoded as wages'], [],
    'Opinion: AGI and "earned income both exceeded the phaseout amount of $14,820 for 2015".'),
 ('tcsumm-2021-6', 1): ('A', ['earlyDistributionTax'], [S, T], [], 'Opinion: "additional tax of $10,947 under section 72(t)"; 10% x 109,471.'),
 ('tcsumm-2021-9', 0): ('A', ['taxableSocialSecurity'], [S, T, 'cap binds by wide margin'], ['single assumed (irrelevant here)'], 'Opinion: SS benefits of $13,024 taxable; 85% x 15,322 with 82,395 Schedule C profit.'),
 ('tcsumm-2021-9', 1): ('D', ['deficiency (notice consistency check)'], [S], ['filing status single (opinion silent: no "single", no "joint")'],
    'Note: "Filing status not stated; single assumed"; the 3,992 income-tax figure depends on status.'),
 ('tcsumm-2022-10', 1): ('C', ['qualitative: pension and excess wages taxable'], ['no-court-figure (Rule 155)', 'compared-to-encoder-hand-computation'], ['72(t) on pension kept although opinion never mentions 72(t); age assumed'],
    'Court "states the rule, not the amount"; Lean 6,891 matched only against a hand computation.'),
 ('tcsumm-2022-10', 4): ('D', ['deficiency (notice consistency check)'], [S], ['10% 72(t) on 20,069 pension (opinion has no "72(t)" or "10%"); age not stated'],
    'Diagnosis: "Shows the notice included a 72(t) tax the opinion never mentions."'),
 ('tcsumm-2023-13', 0): ('B', ['rolloverIncludible'], ['assumed rolledOver amount and days (bounds)', 'output-equals-input distribution'], ['rolledOver 71,147 assumed', 'days 366 lower bound'],
    'Diagnosis: "amount not stated; full amount assumed"; court applied no 60-day analysis.'),
 ('tcsumm-2023-13', 2): ('A', ['earlyDistributionTax'], [S, T], [], 'Opinion: "10% additional tax on premature distributions of $11,533"; 10% x 115,325.'),
 ('tcsumm-2023-13', 3): ('D', ['deficiency'], [S], ['otherIncome 139,100 fitted so MFJ schedule reproduces 38,213'],
    'Note: "Base taxable income $115,100 ... is NOT found: it is the value at which ... reproduces the notice".'),
 ('tcsumm-2023-25', 0): ('C', ['lapseIncome', 'agi'], [S, 'inputs-are-court-figures (loanExtinguished = found excess, premiums 0)'], [],
    'Opinion: Forms 1099-R "$13,214 and $5,366"; expected 18,580 is their sum.'),
 ('tcsumm-2023-3', 0): ('B', ['alimonyDeduction'], [S, 'judgment-input (noPostDeathLiability false)', 'rule-trivial', 'total 116,419 = allowed+conceded copy'], [],
    'Opinion: fees payable "until paid in full"; survival-of-liability reading entered as a fact.'),
 ('tcsumm-2023-35', 3): ('C', ['net rent / itemized share'], ['computed-outside-Lean (encoder arithmetic)', 'no-court-total'], [],
    'Diagnosis: "Allocation is arithmetic on found facts, done in the encoding (framework has no Schedule E)".'),
 ('tcsumm-2023-35', 4): ('C', ['net rent'], ['computed-outside-Lean (encoder arithmetic)', 'no-court-total'], [],
    'Diagnosis: "Rental netting done in the encoding (no Schedule E in framework)."'),
 ('tcsumm-2023-35', 5): ('C', ['alimonyIncluded'], ['stipulation-echo'], ['direction (received) and instrument date assumed'],
    'Note: "alimony 3,000 (stipulated; direction not stated) encoded as alimonyReceived".'),
 ('tcsumm-2023-35', 6): ('C', ['filingStatus', 'dependentsCounted', 'exemptions'], ['concession'], ['two placeholder dependents'],
    'Diagnosis: "Concessions; dependents not described in opinion".'),
 ('tcsumm-2023-35', 7): ('B', ['failureToFileApplies'], ['rule-trivial (no return by extended due date)', 'amount unchecked'], [],
    'Applies flag only; "Amount unchecked: court gives none".'),
 ('tcsumm-2024-10', 0): ('A', ['earlyDistributionTax'], [S, T, 'judgment-input (plan not shown to be IRA)'], [],
    'Opinion: deficiency "$13, 702" (spaced in text) = 10% x 137,024; homebuyer exception IRA-only.'),
 ('tcsumm-2024-10', 1): ('A', ['deficiency'], [T, 'duplicate-of-issue-0'], [], 'Deficiency is the 72(t) tax alone.'),
 ('tcsumm-2024-15', 0): ('C', ['iraDeduction'], ['conclusion-encoded-as-fact (contribution 0)'], [],
    'Diagnosis: "\'401(k) deferral is not a sec. 219 contribution\' is the court\'s characterization, taken as input."'),
 ('tcsumm-2024-19', 0): ('C', ['gamblingLossDeduction'], [S, 'answer-encoded-as-input (losses = 61,929)'], [],
    'Opinion: loss "at least equal to her winnings" (Cohan); losses encoded = winnings, so the cap returns the input.'),
 ('tcsumm-2024-22', 0): ('C', ['wages'], [S, 'stipulation-echo', 'court figure 174,995 inconsistency ignored'], [],
    'Opinion: "Petitioners stipulated that they received wages of $206,609"; Lean wages = input.'),
 ('tcsumm-2024-22', 1): ('C', ['withholding excluded'], ['no-output-compared', 'framework-design'], [], 'Diagnosis: "the jurisdictional holding itself is not an output."'),
 ('tcsumm-2024-22', 4): ('C', ['adjustments'], [S, 'stipulation-echo'], [], 'Opinion: "parties stipulated that Mr. Lucas incurred $2,433"; expected adjustments 2,433 = input.'),
 ('tcsumm-2024-22', 6): ('B', ['accuracyPenaltyApplies'], ['court-left-substantiality-to-Rule-155', 'partial-facts', 'judgment-inputs (approval, no reasonable cause)'], ['as-filed standard deduction assumed'],
    'Court: liable "to the extent the understatement ... is substantial"; Lean substantiality computed on partial facts.'),
 ('tcsumm-2024-4', 0): ('A', ['earlyDistributionTax'], [S, T, 'expected-not-stated-by-court', 'date-gated exception logic'], ['age 52 (opinion: "early 50s")'],
    'Opinion gives no "1,034" and no "10%"; expected is the encoder\'s 10% x 10,342.'),
}

# Non-match labels: (id, idx): (fair, comment). Default fair=True with a generic comment.
NM = {
 ('tcmemo-2019-41', 1): (False, 'Labelled court/IRS arithmetic, but 4,084 follows from the IRS worksheet\'s whole-dollar line rounding, which is correct procedure; the 1-dollar gap is a model rounding-convention gap. priorModifiedIncome 0 is itself inferred from 4,084.'),
 ('tcmemo-2023-141', 2): (False, 'Labelled court/IRS arithmetic, but the $2 gap (3,276 vs IRS 3,274) is unexplained; nothing shown proves an IRS error (qualified-dividend share and table rounding are unknowns). Should be "unexplained".'),
 ('tcsumm-2020-18', 5): (False, 'Diagnosis calls 1,860.60 a court error; it is respondent\'s determined penalty in the opinion\'s table. A reduced penalty base (20% x 9,303) is equally consistent; error not demonstrated.'),
 ('tcsumm-2023-25', 4): (False, 'Labelled court/IRS arithmetic, but diagnosis itself says it is a rate-convention difference on a notice reconstruction whose withholding 3,537 was back-solved; not a demonstrated IRS error and not a court holding.'),
 ('tcsumm-2023-25', 1): (False, 'Not-encodable hides a model gap: diagnosis says the sec. 280A facts are mechanical (47 personal days > 14). A computable issue the framework cannot do is excluded from the 110 denominator instead of counted as a model-gap miss.'),
 ('tcsumm-2024-19', 1): (True, 'Fair as judgment, but note negligence=true was supplied by the encoder (court named no ground); on stated facts Lean finds no substantial understatement.'),
 ('tcsumm-2021-26', 0): (True, 'Fair, but inconsistent: the same residency finding drives issues 1-2, which are counted as matches.'),
 ('tcsumm-2020-9', 2): (True, 'Fair; inconsistent with tcsumm-2024-15[0] / tcsumm-2019-8[2], where the same pattern (finding encoded as 0 -> credit/deduction 0) is counted as match.'),
 ('tcsumm-2022-10', 0): (True, 'Conservative: Lean exclusion 101,300 equals the court; qualification rests on judgment inputs.'),
 ('tcsumm-2020-18', 0): (True, 'Fair: deficiency is tautological (taxShown back-solved); rightly not a match.'),
 ('tcsumm-2020-18', 2): (True, 'Fair: tautological deficiency.'),
 ('tcsumm-2020-18', 4): (True, 'Fair: tautological deficiency.'),
 ('tcsumm-2024-12', 2): (True, 'facts-not-stated supported: status/withholding not in opinion; IRS penalty and FTF bases themselves imply different bases (6,910; 3,732).'),
 ('tcsumm-2024-12', 3): (True, 'facts-not-stated supported: only Schedule C items found for 2019.'),
 ('tcsumm-2024-12', 4): (True, 'Supported: 933 = 25% x 3,732 implies unfound timely credits.'),
 ('tcsumm-2024-12', 5): (True, 'Supported: 1,382 = 20% x 6,910, base not in opinion.'),
 ('tcsumm-2024-12', 6): (True, 'Supported: 849 = 20% x 4,244; gap is the deficiency gap.'),
 ('tcmemo-2023-56', 1): (True, 'Supported: opinion gives only the 7,824 item; 3,473 > 39.6% of it, so other return facts are needed.'),
 ('tcmemo-2024-23', 1): (True, 'Supported: needs non-SS MAGI >= 46,874, not in opinion; court adopted the 85% ratio by agreement.'),
 ('tcsumm-2019-8', 3): (True, 'Supported: exemptions/credits on the return not stated; 836 gap.'),
 ('tcsumm-2020-25', 7): (True, 'Supported: fn. 17 says earned income > AGI, implying unstated adjustments (~4,000 reproduces 7,816).'),
 ('tcsumm-2022-23', 1): (True, 'Supported: other MAGI >= 51,255 needed, not stated.'),
 ('tcmemo-2025-23', 7): (True, 'Honest model-gap: unclaimed withholding reduces the underpayment (Reg. 1.6664-2), not modelled.'),
}
CONCESSION_NE = {('tcsumm-2019-33', 3), ('tcsumm-2020-25', 8), ('tcsumm-2020-9', 3), ('tcsumm-2021-41', 5),
                 ('tcsumm-2021-6', 3), ('tcsumm-2021-2', 3), ('tcsumm-2024-11', 2), ('tcmemo-2019-41', 3)}

matches, others = [], []
for f in sorted(glob.glob(os.path.join(ENC, '*.result.json'))):
    r = json.load(open(f, encoding='utf-8'))
    for i, x in enumerate(r['issues']):
        k = (r['id'], i); v = x['verdict']
        if v == 'match':
            c, items, flags, inf, ev = M[k]
            matches.append(dict(id=r['id'], issue_index=i, issue=x['issue'], items=items, **{'class': c},
                                flags=flags, inferred_facts=inf, evidence=ev))
        else:
            fair, com = NM.get(k, (True, None))
            if com is None:
                com = {'judgment': 'Decisive step is a weighing/credibility/substantiation finding; no hidden computable disagreement found.',
                       'not-encodable': 'No computable court figure or outside framework scope; no hidden disagreement found.',
                       'mismatch': 'Diagnosis consistent with the arithmetic shown.'}[v]
                if k in CONCESSION_NE:
                    com = 'Fair, but conceded items are not-encodable here while similar concessions elsewhere are counted as matches (inconsistent counting).'
            others.append(dict(id=r['id'], issue_index=i, issue=x['issue'], label=v,
                               cause=x.get('cause'), fair=fair, comment=com))
assert len(matches) == 95 and len(M) == 95, (len(matches), len(M))

by = collections.Counter(m['class'] for m in matches)
a_nontriv = [m for m in matches if m['class'] == 'A' and T not in m['flags']]
DEN = 110
match_label_concerns = [f"{m['id']}[{m['issue_index']}]" for m in matches if any(
    s.startswith(('hidden-item-mismatch', 'no-court-figure', 'court-left', 'computed-outside-Lean', 'concession', 'nothing-computed', 'no-output-compared'))
    for s in m['flags'])]
unfair = [f"{o['id']}[{o['issue_index']}] ({o['label']})" for o in others if not o['fair']]
spot = sum(1 for m in matches if S in m['flags'])

plugs = [
 dict(case='tcmemo-2023-37', field='facts/asFiled.otherIncome = -1,465', stated=False, note='Schedule E loss -8,189 (stated) + 6,724 unidentified residual back-solved so non-SS MAGI equals the court\'s 53,456; residual character not in opinion.'),
 dict(case='tcmemo-2025-23', field='facts/asFiled.otherIncome = 50,514', stated=False, note='Backed out from stated TI 37,964 + 12,550 single standard deduction; status single inferred because only it reproduces 18,064.'),
 dict(case='tcsumm-2023-13 (entry 2)', field='facts/asFiled.otherIncome = 139,100', stated=False, note='Fitted base: the value at which the 2018 MFJ schedule reproduces the notice deficiency 38,213.'),
 dict(case='tcmemo-2024-67', field='facts.longTermGain = 0', stated=False, note='Capital gain character not stated; set to ordinary because that reproduces 60,569.'),
 dict(case='tcmemo-2024-67', field='estimated.dueDates (statutory 15th, not printed dates)', stated=False, note='Chosen because it gives 424; printed due dates give 422.'),
 dict(case='tcmemo-2024-67', field='sfrTax = 60,811', stated=True, note='Opinion states total tax liability 60,811 (= the notice deficiency, an output figure).'),
 dict(case='tcsumm-2020-18 (3 years)', field='facts.otherTaxes = 8,967 / 22,394 / 15,939 and taxShown = 723 / 4,383 / 5,608', stated='otherTaxes yes (notice total tax quoted); taxShown no', note='Total tax entered as a plug; taxShown back-solved = total - deficiency, so deficiencies are tautological.'),
 dict(case='tcsumm-2019-33', field='taxShown = 0; filing hoh; one CTC child', stated=False, note='Derived/inferred: HOH + one under-17 child chosen because they reproduce 10,518 exactly.'),
 dict(case='tcsumm-2019-33', field='facts.itemizedDeductions = 9,250', stated=True, note='Opinion: itemized deductions of $9,250 (equals the 2015 HOH standard deduction).'),
 dict(case='tcsumm-2023-25', field='sfrTax = 9,910', stated=False, note='Notice deficiency used as SFR tax; opinion never states the SFR tax.'),
 dict(case='tcsumm-2023-25 (entry 2)', field='estimated.withholding = 3,537; currentTax 9,910', stated=False, note='Withholding back-solved so 22.5% x 6,373 = notice FTF 1,434.'),
 dict(case='tcmemo-2019-41', field='ssLumpSums.priorModifiedIncome = 0 (x4)', stated=False, note='Inferred from the stipulated 4,084 itself.'),
 dict(case='tcsumm-2020-5', field='ssLumpSums.priorModifiedIncome = 43,138', stated=False, note='Lower bound back-solved from the petitioners\' 8,306 figure.'),
 dict(case='tcmemo-2023-141', field='otherNonrefundableCredits = 2,278', stated=True, note='Opinion: "tax credits of $2,278"; nature not stated.'),
 dict(case='tcsumm-2022-10 (entry 2)', field='otherIncome = 2,286 (COD); earlyDistributions 72(t) on pension', stated='COD yes; 72(t) no', note='72(t) tax never mentioned in opinion; included because the notice reconstruction needs it.'),
 dict(case='tcsumm-2023-35', field='otherIncome 17,012; itemizedDeductions 25,891; otherTaxes 660', stated='inputs yes, totals encoder-computed', note='Rental netting and itemized allocation done by the encoder; 660 stated as notice 72(t)-type tax.'),
 dict(case='tcsumm-2024-22', field='adjustments 2,433; otherIncome 4,962; itemizedDeductions 32,563', stated=True, note='All stated/stipulated; expected deduction and adjustments equal these inputs (echo).'),
 dict(case='tcsumm-2024-12', field='adjustments 2,500; otherIncome 354', stated=True, note='Student loan interest and NJ refund stated.'),
 dict(case='tcmemo-2022-77', field='asFiled.adjustments 69,880; facts.adjustments 0; alimonyPaid.childSupport = paid', stated='adjustments yes; childSupport is the legal conclusion', note='childSupport = whole payment forces the expected 0.'),
 dict(case='tcsumm-2019-8', field='asFiled.adjustments 6,500; itemizedDeductions 0', stated=True, note='Claimed IRA deduction stated.'),
 dict(case='tcsumm-2024-15', field='adjustments 0; ira.contribution 0', stated='conclusion', note='Contribution 0 forces iraDeduction 0.'),
 dict(case='tcsumm-2020-9', field='tieBreakers agi 2 vs 1', stated=False, note='Ordinal placeholders; AGIs not stated.'),
 dict(case='tcmemo-2024-20', field='status.paidOverHalfHouseholdCost = true', stated=False, note='Not found; set so abode alone decides.'),
]

out = dict(
  method='Hand classification of every verdict from case.json/result.json, with opinion text grepped (validation/scripts/audit_grep.py) for key inputs. Classes: A computed, B rule-from-judgment-input, C echo/tautology, D inferred-from-answer. When in doubt, the weaker class.',
  totals=dict(
    matches=len(matches), by_class=dict(sorted(by.items())),
    A_nontrivial=len(a_nontriv), A_nontrivial_items=[f"{m['id']}[{m['issue_index']}]" for m in a_nontriv],
    spot_checked_matches=spot,
    claimed_rate='95/110 = 86.4%',
    rate_excluding_D=f"{95-by['D']}/{DEN-by['D']} = {100*(95-by['D'])/(DEN-by['D']):.1f}% (D removed from numerator and denominator)",
    rate_A_plus_B_excluding_C_D=f"{by['A']+by['B']}/{DEN-by['C']-by['D']} = {100*(by['A']+by['B'])/(DEN-by['C']-by['D']):.1f}%",
    rate_A_only=f"{by['A']}/{DEN} = {100*by['A']/DEN:.1f}%",
    rate_A_nontrivial_only=f"{len(a_nontriv)}/{DEN} = {100*len(a_nontriv)/DEN:.1f}%",
    unfair_nonmatch_labels=len(unfair), unfair_nonmatch_items=unfair,
    match_label_concerns=len(match_label_concerns), match_label_concern_items=match_label_concerns,
    relabel_concerns_total=len(unfair) + len(match_label_concerns),
    hidden_disagreement_in_judgment_or_not_encodable='None found: no judgment/not-encodable label hides a Lean figure that contradicts a court figure. One not-encodable (tcsumm-2023-25[1]) hides a model gap.',
  ),
  matches=matches, other_labels=others, plugs=plugs,
)
json.dump(out, open(OUT, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
print(json.dumps(out['totals'], indent=1))
