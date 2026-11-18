# Novel search, US TY2025: candidates and verdicts

Total CPU: about 5 minutes. The exe computes ~25,000 returns a second per core.

## What was scanned

| Scan | Script | Size | Output |
|---|---|---|---|
| S1 marginal rates (net tax + employee FICA), 28 archetypes, $0–700k on a $250 grid, +$1,000 steps | `scripts/scan.py` | 157,000 returns | `runs/scan_mtr.json` |
| S2 random households (seeded; every field family incl. tips, overtime, car loan, SALT, seniors, SS, PTC, credits), +$1,000 of each of 6 income types | `scripts/random_scan.py` | 60,000 households, 360,000 perturbations | `runs/random_scan.json` |
| T1 §86 torpedo × senior deduction (senior switched off through its SSN condition) | `scripts/scan2.py` | 5,600 | `runs/scan2.json` |
| T2 most cash a retired household receives at zero tax | `scripts/scan2.py` | 48,000 | `runs/scan2.json` |
| T3 joint vs separate returns, 9 expense/child allocations, couples $0–600k on a $25k grid (same §63(e) choice for both spouses) | `scripts/scan2.py` | 3,000 couples × 5 returns | `runs/scan2.json` |
| T3b separate returns for the child tax credit, 1–4 children, $5k grid to $800k | `scripts/ctc_mfs.py` | 51,000 couples | `runs/ctc_mfs.json` |
| T9 §63(e): smaller deduction cheaper (AMT), wages to $2m, SALT to the $40k cap | `scripts/scan2.py` | 2,600 | `runs/scan2.json` |

## Result in one line

No marginal rate above 100% except the known cliffs (EIC investment income, saver's credit tiers); every saving the
scans found has a statutory cause and is already documented somewhere. What is new is quantification under 2025 law.

## Candidates

| # | Candidate | Numbers (model) | Statutory cause | Verdict |
|---|---|---|---|---|
| N1 | **Separate returns to escape the child-credit phase-out.** Put the children on the lower earner's separate return; the other spouse's income then reduces no credit. | 7,620 of 51,000 couples gain; best $6,512 (4 children, $365k + $215k), $4,312 (3), $3,388 (2), $1,456 (1). Theorem `ctc_separate_returns`. | §24(b)(2) with §24(h)(3): $400,000 joint, $200,000 "any other case", measured on the claiming taxpayer's MAGI; brackets below 37% are exactly halved for separate returns (§1(d)), so separate filing costs nothing in rate until 37%; CTC is not among the credits barred on separate returns. §152(c)(4) lets either parent claim. | **Known** (instead.com, catalyst-cpa.com, filetax.com articles on MFS and the CTC). Not found by the earlier Household hunt (its couples were below the threshold). |
| N2 | **Torpedo plus senior phase-out.** | Single 67 with $40–50k of SS: IRA withdrawals face 44.0% (theorem `torpedo_senior`: $440 per $1,000 vs $407 without the senior deduction) = 22% × 1.85 × 1.06 + rounding. But the senior deduction also *removes* the torpedo for many: single with $30k SS 40.7% → 32.0%; MFJ with $80k SS 40.7% → 35.4%; for single $40k SS the ≥40% band shrinks from about $8,000 to $5,000 of withdrawals. | §86(a)(2) 85% inclusion; §151(d)(5)(C)(iii) 6% of MAGI (which includes the extra taxable benefits) over $75k/$150k. | **Known** qualitatively (247wallst.com, themadisonpartners.com, levyio.com on stacking); the exact peak and the band shift are our quantification. |
| N3 | **Zero-tax retirement income.** | MFJ 67/67: $143,400 of long-term gain alone, or $40k SS + $109,400 gain = **$149,400 cash at $0 federal income tax** (theorem `retired_zero_tax`); single 67: $86,600 ($60k SS + $26,600 gain). With IRA withdrawals instead: $46,700 (MFJ, no SS). | §1(h)(1)(B) 0% band to $96,700 TI; §63(c) $31,500 + §63(f) $3,200 + §151(d)(5)(C) $12,000; §86 base amounts. | **Known** mechanism (0% band for retirees); the 2025 senior deduction adds $12,000 of room. |
| N4 | Separate returns win with SALT or charity at $300k + $300k. | Up to $3,938 (SALT split), $3,485 (charity with SALT). | The model reads §164(b)(7)(B) for separate filers as a 15% reduction ending at $350,000 (group B FINDINGS §3, "high"). | **Earlier hunt** (NewDeductions plans 1–2, CANDIDATE: a reading of the text). Depends on that reading: possibly an **artefact of the model's reading**, not of the IRS worksheet. |
| N5 | Separate returns with the car loan in the lower earner's name. | $1,147 at $100k + $100–200k. | §163(h)(4) has no joint-return condition. | **Earlier hunt** (NewDeductions plan 4). |
| N6 | §199A phase-in marginal rates 68–69%. | Single Schedule C $252k–277k: 68.1%; MFJ SSTB $447k–454k and $480k–500k: 69.2%; MFJ non-SSTB, no W-2 wages $492k–544k: 68.3%. | §199A(b)(3)(B), (d)(3): the deduction is withdrawn over $50k/$100k of taxable income. | **Known** (§199A phase-in "cliffs" discussed since 2018; Form 8995-A). |
| N7 | Saver's credit tier cliff, 97.9% over $1,000. | MFJ $50,750–51,500 with $4k contributed. | §25B(b) tiers. | **Known** (earlier hunt Household cliffs; the comparison's cliffs). |
| N8 | EIC investment-income cliff — the only source of >100% rates in 360,000 random perturbations (all 164 hits; one was attributed to taxable SS by the largest-moving line, but its EIC also fell to zero). | $2,151 for $1 (theorem `eic_cliff`). | §32(i). | **Known**. |
| N9 | §63(e): electing the smaller deduction is cheaper. | 99 of 2,600 high-gain households (MFJ $775k+ with $1m gain), up to $1,750. | AMT (§55) with the 2025 $40k cap; standard deduction and SALT both added back. | **Known** (Form 1040 instructions; the model already takes the cheaper election). |
| N10 | PTET also restores the SALT cap by lowering MAGI. | K32: MAGI $550k → $522.5k lifts the cap $25,000 → $33,250; $6,896 saved. | §164(b)(7)(B) measured on MAGI; entity-level tax reduces the K-1. | **Known** (Thomson Reuters, Cooley, The Tax Adviser 2026 on PTET after Pub. L. 119-21). |

## Nothing found where looked

- No interaction among the 2025 Act deductions (tips, overtime, car loan, senior) produces a rate over 50% outside
  the bands above: they sit below the line (§63(b)), so they move neither AGI nor any credit; their own phase-outs are
  10% ($100 per $1,000), 20% (car, $200 per $1,000) and 6% × the bracket.
- The 2025 premium tax credit has no 400% cliff (the enhanced table runs through 2025): highest marketplace rate
  40.2% (single 60).
- Over 157,000 smooth-scan points, the highest rates outside §199A are 54.7% (HOH with a college student: AOTC
  phase-out 25% + 22% + FICA) and 47.9% (SALT phase-down band: 35% × 1.3 + 2.4% Medicare).

## Sources checked (3 searches)

instead.com/resources/blog/child-tax-credit-for-married-filing-separately; catalyst-cpa.com/married-filing-separately-the-2026-child-tax-credit;
247wallst.com (2026-06-15, 2026-08-21) and themadisonpartners.com on the senior deduction; tax.thomsonreuters.com
"OB3 SALT cap increase: why PTET elections still make sense"; cooley.com 2025-07-15; thetaxadviser.com 2026 Mar.
