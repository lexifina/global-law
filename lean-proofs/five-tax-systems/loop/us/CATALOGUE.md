# US federal individual income tax, TY2025: known loopholes and planning moves, recreated with the model

Model: [`lean-proofs/TaxCode/Individual`](../../../TaxCode/Individual) (TY2025, Pub. L. 119-21), unchanged; the Lake project in `lean/` reads it from there (hashes of the copy used in
`TAXCODE_COPY.sha256`), run through `lean/UsLoop/Core.lean` (`form1040F` = `form1040` with group B's facts passed
through) and the compiled batch exe `lean/.lake/build/bin/usloop`. Scripts: `scripts/model.py` (driver),
`scripts/catalogue.py` (every (a)/(b) row below; output `runs/catalogue.json`). Kernel-checked theorems:
`lean/UsLoop/Theorems.lean` (households in `lean/UsLoop/Scenarios.lean`; `decide`, no `native_decide`, no `sorry`).

**Saving** = federal burden without the move minus with it, one year unless stated, in dollars: the return's
`netTax` (income tax + SE tax + additional Medicare + NIIT − refundable credits) plus, where the move changes payroll
tax on wages, FICA (§§3101/3111, 7.65% each side to the $176,100 base). FICA is the only addition to the model
(triage **b**, 2 lines: `ficaHalf` in `Scenarios.lean`, `fica` in `model.py`).

Triage: **a** expressible as is; **b** with a small statute-faithful addition here; **c** out of scope (reason given).

Counts: **59 catalogued; 43 recreated (38 a, 5 b); 16 out of scope** (one of them, K40, was recreated by the earlier hunt).

| ID | Move | Source | Triage | Scenario (TY2025) | Without → with | Saving | Check |
|---|---|---|---|---|---|---|---|
| K01 | Long-term gain instead of ordinary income | §1(h); IRS Pub. 550 ch. 4; JCT JCX-48-24 (reduced rates on gains) | a | single, $100k wages, $50k extra | 25,067 → 20,955 | **4,112** | catalogue.py |
| K02 | Qualified instead of ordinary dividends | §1(h)(11); Pub. 550 | a | MFJ $200k wages, $40k dividends | 35,734 → 32,898 | 2,836 | catalogue.py |
| K03 | Carried interest: profit share as LTCG, not a fee | §1061, §1(h), §1411; CBO *Options for Reducing the Deficit* (carried interest as ordinary income); TPC Briefing Book | a | MFJ $500k wages, $1m as SE fee (SSTB) vs LTCG | 499,797 → 347,842 | **151,955** | `carried_interest` |
| K04 | 0% LTCG bracket gain harvesting | §1(h)(1)(B); Rev. Proc. 2024-40 §3.03 | a | MFJ $80k wages: $48,200 gain at $0 vs the same gain in a $200k year | 7,230 → 0 | 7,230 | `gain_harvest` |
| K05 | Tax-loss harvesting | §1211(b), §1212(b); Pub. 550 | a | single $150k, $20k gain, $23k loss realised | 28,067 → 24,347 | 3,720 | catalogue.py |
| K06 | Crypto loss harvest with immediate buy-back (no wash sale) | §1091(a) "stock or securities"; Notice 2014-21 (virtual currency is property); Treasury Green Book proposals to extend §1091 to digital assets (not enacted; still law in 2025) | a | as K05 | as K05 | 3,720 | catalogue.py (the model has no §1091: the crypto edge is the rule's absence) |
| K07 | Step-up in basis at death | §1014; JCX-48-24; TPC Briefing Book | a | heir, MFJ $150k, sells $1m asset with $100k basis | 202,221 → 15,898 | 186,323 | catalogue.py |
| K08 | Home sale exclusion | §121; Pub. 523 | a | MFJ $150k, $500k gain | 107,021 → 15,898 | 91,123 | catalogue.py |
| K09 | QSBS 100% exclusion (no AMT preference) | §1202(a)(4), §57(a)(7); Pub. L. 119-21 §70431 for later stock | a | MFJ $300k, $5m gain | 1,253,091 → 50,584 | 1,202,507 | catalogue.py |
| K10 | Municipal bond interest | §103; Pub. 550 | a | MFJ $300k, $50k interest | 64,484 → 50,584 | 13,900 (27.8% = 24% + NIIT; break-even muni yield 72.2% of taxable) | catalogue.py |
| K12 | 401(k) elective deferral (deferral, not exclusion) | §402(g); Notice 2024-80 ($23,500) | a | single $80k | 9,055 → 4,655 | 4,400 | catalogue.py |
| K13 | Deductible IRA stacked with the saver's credit | §219, §25B; Pub. 590-A | a | MFJ $50k, $2k IRA each | 1,853 → 0 | 1,853 (46% of $4k) | catalogue.py |
| K16 | Roth conversion in a low-income year | §408A(d)(3); §63(c), §63(f), §151(d)(5)(C) | a | MFJ 66/66, $20k pension: **$26,700 converts at $0**; vs same in an $80k-pension year | 3,204 → 0 | 3,204 | catalogue.py |
| K17 | HSA through a cafeteria plan (no income tax, no FICA) | §223, §106(d), §125, §3121(a)(2)(B); Pub. 969 | b | MFJ $120k, family $8,550 | — | 2,334 (incl. both FICA halves) | catalogue.py |
| K18 | Dependent-care FSA instead of the credit | §129, §21(c) (limit cut by the exclusion); Pub. 503 | b | MFJ $150k, 2 children, $10k care | 21,774 → 21,290 | 484 | catalogue.py |
| K19 | §199A 20% deduction (non-SSTB, under threshold) | §199A; Form 8995 instr. | a | single, $100k Schedule C | 26,023 → 22,624 | 3,399 | catalogue.py |
| K20 | Salary sized to the §199A W-2 wage limit | §199A(b)(2)(B); Reg. §1.199A-2 | b | MFJ S-corp owner, $1m profit, no employees: best salary **$280k** (28% of profit) vs $0 / $100k | 282,408 → 255,292 | **27,116** (21,085 vs $100k) | `scorp_wage_limit` |
| K21 | Deferral by an SSTB owner in the §199A(d)(3) phase-in | §199A(d)(3); Reg. §1.199A-5 | a | MFJ SSTB, $150k salary + $300k K-1, $23,500 401(k) | 75,176 → 66,152 | 9,024 (38.4% in the 32% bracket) | `sstb_deferral` |
| K22 | S corporation: salary + distribution vs Schedule C | §1401–1402 vs §§3101, 3111, §1366; Rev. Rul. 74-44; GAO-10-195 | b | single, $200k profit, $80k salary | 52,806 → 42,372 | **10,434** | `scorp_vs_schedule_c` |
| K23 | Hiring your under-18 child in a sole proprietorship | §3121(b)(3)(A), §63(c)(5); IRS Pub. 15 (family employees) | a | MFJ $200k SE, child 15 paid $15k | 42,084 → 38,484 | 3,600 (two returns) | catalogue.py |
| K24 | Head of household instead of single | §2(b), §1(b); Pub. 501 | a | $60k, one child | 2,875 → 1,825 | 1,050 | catalogue.py |
| K25a | Marriage bonus (marry by 31 Dec) | §7703(a)(1), §1(a); CBO *For Better or for Worse* (1997) | a | one earner $200k | 37,067 → 26,898 | 10,169 | catalogue.py |
| K25b | Marriage penalty avoided (EIC, HOH) | §32(b), §2(b), §7703 | a | two $25k earners, 2 children | −5,581 → −9,246 | **3,665** | `marriage_penalty_eic` |
| K26 | Unmarried parents: lower earner claims the children | §152(c)(4); Pub. 501; earlier hunt Household plan 6 | a | $60k + $20k, 2 children | 53 → −4,702 | 4,755 | catalogue.py |
| K27 | Keeping investment income under the EIC limit | §32(i); Rev. Proc. 2024-40 ($11,950); Pub. 596 | a | HOH $25k, 1 child: $11,951 vs $11,950 of interest | −867 → −3,018 | **2,151 for $1** | `eic_cliff` |
| K28 | CTC "or fraction thereof" notch | §24(b)(2); Schedule 8812 instr. | a | MFJ $400,001 vs $400,000, 2 children | | 50 for $1 | catalogue.py |
| K29 | Bunching gifts through a donor-advised fund | §170, §63(e); Pub. 526 | a | MFJ $200k, $10k SALT, $12k mortgage, $10k/yr gifts; 2 years | 53,576 → 51,486 | 2,090 | catalogue.py |
| K30 | Giving appreciated stock instead of cash | §170(e)(1), (b)(1)(C); Pub. 526 | a | MFJ $300k, $50k stock, $10k basis | 53,664 → 46,144 | 7,520 | catalogue.py |
| K31 | Qualified charitable distribution | §408(d)(8); Pub. 590-B | a | MFJ 73/73, $50k SS, $100k IRA, $10k gift | 11,022 → 9,822 | 1,200 | catalogue.py |
| K32 | SALT cap workaround: pass-through entity tax | Notice 2020-75; §164(b)(6)–(7) (Pub. L. 119-21 §70120) | a | MFJ $550k K-1, $27.5k state income tax, $15k property tax | 86,862 → 79,966 | **6,896** (MAGI drop lifts the cap 25,000 → 33,250) | `ptet_workaround` |
| K33 | Deferral inside the SALT phase-down band | §164(b)(7)(B) | a | MFJ $510k, $60k SALT, $23,500 401(k) | 107,826 → 99,135 | 8,691 (37.0%; band marginal rate 35.9% at $550k) | catalogue.py |
| K34 | No tax on tips | §224 (Pub. L. 119-21 §70201) | a | single $60k incl. $20k tips | 5,075 → 2,675 | 2,400 | catalogue.py |
| K35 | No tax on overtime | §225 (§70202) | a | MFJ $90k, $8k premium | 6,546 → 5,586 | 960 | catalogue.py |
| K36 | Car loan interest | §163(h)(4) (§70203) | a | single $80k, $5k interest | 9,055 → 7,955 | 1,100 | catalogue.py |
| K37 | Senior deduction kept by drawing from a Roth | §151(d)(5)(C) (§70103) | a | MFJ 66/66 needing $180k: $30k from Roth | 19,946 → 12,554 | 7,392 (band marginal rate 24.6% in the 22% bracket) | catalogue.py |
| K38 | Social Security "tax torpedo" managed by withdrawal order | §86; Pub. 915 | a | single 67, $50k SS: marginal rate 44% at $41k–$53k of IRA withdrawals | | rate 44.0% | catalogue.py, `torpedo_senior` |
| K39 | IRA deduction raises the premium tax credit | §36B(b)(3)(A) as extended through 2025, §219; Pub. 974 | a | single 60, $70k, $13k benchmark, $7k IRA | −195 → −2,210 | 2,015 (28.8%) | catalogue.py |
| K42 | Employer health insurance exclusion | §106, §3121(a)(2); JCX-48-24 (largest exclusion) | b | MFJ, $20k premium vs wages | 28,506 → 23,046 | 5,460 | catalogue.py |
| K43 | Installment sale spreading a gain | §453; Pub. 537 | a | MFJ $60k wages, $400k gain over 4 years vs 1 (2025 law each year) | 69,534 → 30,864 | 38,670 | catalogue.py |
| K52 | Separate returns double the SALT cap | §164(b)(6)–(7) for MFS; §63(c)(6)(A); earlier hunt NewDeductions plan 2 | a | $350k + $250k, lower earner pays property tax and mortgage | 141,220 → 137,710 | 3,510 | catalogue.py |
| K54 | Supporting a parent: HOH + $500 credit | §2(b)(1)(B), §24(h)(4), §152(d); Pub. 501 | a | single $50k | 3,875 → 2,325 | 1,550 | catalogue.py |
| K55 | "Augusta rule" 14-day rental to own business | §280A(g), §162; Sinopoli v. Comm'r, T.C. Memo. 2023-105 (rent must be at market) | a | MFJ $250k SE, $20k rent | 54,305 → 50,296 | 4,009 | catalogue.py |
| K61 | Net unrealised appreciation on employer stock | §402(e)(4); Pub. 575 | a | MFJ 66, $500k stock, $100k basis | 103,022 → 72,152 | 30,870 | catalogue.py |
| K14 | Backdoor Roth | §408A(c)(3), §408(d)(2) pro-rata; Pub. 590-A | c | needs IRA basis and Roth growth over years; the earlier `LegalProofs/USTax/Retirement` search found it unprompted (blog: formalizing-the-us-tax-code) | | | — |
| K15 | Mega backdoor Roth | §415(c), §402A(c)(4); Notice 2014-54 | c | plan-level after-tax contributions, multi-year (also found by the Retirement search) | | | — |
| K40 | Student, not parent, claims the AOTC | §25A(g)(3), (i)(5) | c* | recreated by the earlier hunt (Household plan 7, +$2,500); not redone | | | — |
| K44 | Shifting unearned income to children | §1(g) kiddie tax | c | model has no §1(g)/Form 8615 (needs the parent's return linked; > 60 lines) | | | — |
| K45 | Like-kind exchange | §1031 | c | deferral across years, basis carryover | | | — |
| K46 | Opportunity zones | §1400Z-2 (made permanent by Pub. L. 119-21) | c | multi-year deferral and exclusion | | | — |
| K47 | Buy, borrow, die | §1014 + loans not income | c | multi-generation; estate facts | | | — |
| K48 | 529 plans | §529 | c | no federal deduction; multi-year growth | | | — |
| K49 | ISO exercise and the AMT | §422, §56(b)(3) | c | model's AMT has no ISO preference item | | | — |
| K50 | Real estate professional / NIIT avoidance | §469(c)(7), §1411(c)(2) | c | no passive/active characterisation in `Household` | | | — |
| K51 | Gambling losses | §165(d) (90% from 2026) | c | no gambling fields | | | — |
| K56 | Cost segregation and bonus depreciation | §168(k) (100% restored by Pub. L. 119-21 §70301) | c | asset- and entity-level | | | — |
| K57 | Annual gift exclusion, lifetime exemption | §2503(b), §2010 | c | estate and gift tax (earlier hunt: Transfer) | | | — |
| K58 | Charitable remainder trust | §664 | c | trust-level, multi-year | | | — |
| K59 | Syndicated conservation easements | §170(h), §170(h)(7); Notice 2017-10 | c | partnership-level | | | — |
| K60 | GRAT | §2702 | c | estate and gift tax | | | — |

Notes on the numbers:
- K03 counts the fee as SE income of a specified service business (investment management, §199A(d)(2)), so no §199A
  deduction at that income; the carry bears NIIT, as the model applies §1411 to all gains.
- K20's optimum ($280k of $1m) is the familiar "28.57%" rule: the 20% deduction is capped at 50% of wages, so the
  salary that makes 50% × W = 20% × (profit − W − employer FICA) is about 2/7 of profit.
- K16, K29, K43 compare years at 2025 law; K10 assumes equal yields.
- K31: QCDs matter only with income above the zero-tax room; at $30k of IRA income (first try) both cases owed $0.
- K22, K20: state payroll/unemployment taxes and the reasonable-compensation test are outside the model.
