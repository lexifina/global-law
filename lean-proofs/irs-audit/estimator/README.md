# The IRS Tax Withholding Estimator checked against the statute

Three places where the IRS's [Tax Withholding Estimator](https://apps.irs.gov/app/tax-withholding-estimator/) (2026
rules) departs from the Internal Revenue Code. Each was found by running the estimator's published code
([IRS-Public/tax-withholding-estimator](https://github.com/IRS-Public/tax-withholding-estimator), commit
[31e040b](https://github.com/IRS-Public/tax-withholding-estimator/tree/31e040b58d57c68d17309f8c1942969d2dae93b4)) on
1,000 generated households against an independent model of the law, then confirmed by entering one household for each
into the live estimator on irs.gov on 18 November 2026.

| | What the estimator does | The statute | Household (live irs.gov) | Estimator | Law |
|---|---|---|---|---|---|
| 1 | Leaves qualified dividends out of net investment income and out of the EITC investment-income test | [§1411(c)(1)(A)(i)](https://uscode.house.gov/us/usc/t26/s1411#c-1-A-i), [§32(i)(2)(A)](https://uscode.house.gov/us/usc/t26/s32#i-2-A) | Single, salary $192,000, qualified dividends $68,000 | NIIT $0 | NIIT $2,280 |
| | | | Head of household, one child, salary $24,000, qualified dividends $13,000 | EITC $2,328 | No EITC |
| 2 | Counts employer pensions as net investment income | [§1411(c)(5)](https://uscode.house.gov/us/usc/t26/s1411#c-5) | Single, 65+, employer pension $264,000 | NIIT $2,432 | NIIT $0 |
| 3 | Counts the 0.9% Additional Medicare Tax but never credits what the employer withheld | [§3102(f)](https://uscode.house.gov/us/usc/t26/s3102#f-1) | Single, one job, salary $420,000 | $1,980 more owed | Nothing more owed |

## Files

- [TweLive.lean](TweLive.lean): the households above, with the figures the live estimator showed, each pinned next to
  the statute's answer and checked by `decide`; and a theorem that for a single filer with one employer the estimator
  overstates the bill by exactly what the employer withheld.
- [TweNiit.lean](TweNiit.lean): the net investment income tax and EITC test, the households from the headless runs,
  and a bound on the dividend understatement (at most 3.8% of qualified dividends when no pension is involved).
- [TweAddlMedicare.lean](TweAddlMedicare.lean): the Additional Medicare Tax cases from the headless runs, including a
  married couple with one $500,000 earner (estimator: $2,250 owed; law: $450 back).

Each file stands alone. Check one with `lean TweLive.lean` (Lean 4).

## Reproducing on irs.gov

Paycheck withholding in each household is set to the income tax the law says is due, so the correct result is a balance
of about $0 and anything else is the estimator's departure. For household 1: About you: Single, no dependents. Income:
one salary job, all year, paid monthly, last pay period ended and paid 31 October 2026, $16,000 per period ($160,000 so
far), federal income tax withheld $3,751 per period ($37,510 so far); Investment income: qualified dividends $68,000.
Standard deduction; no adjustments or credits. The estimator shows "Estimated federal tax owed $2"; in the browser
console, `factGraph.get('/netInvestmentIncomeTax')` is `0.00`. Entered as ordinary dividends instead, the same $68,000
gives `2280.00`. The other households follow the same pattern with the figures in the table (the pension: $22,000 a
month, $4,594 withheld; the $420,000 job: $35,000 a month, $9,178 withheld; the EITC household: $2,000 a month, no
withholding, one child for the child tax credit and the EITC).

The fact dictionary the live site loads
([fact-dictionary.xml](https://apps.irs.gov/app/tax-withholding-estimator/resources/fact-dictionary.xml)) matches the
repository at 31e040b for every fact involved, and its scripts and compiled rules engine are byte for byte the
repository's files.
