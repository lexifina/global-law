# Fiji (FJ) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The official Laws of Fiji consolidation is more than two budgets behind: it still prints ss 28A and 125A, which Act 5 of 2024 deleted from 1 August 2024, and its Table of Amendments stops at Act 5 of 2023
- kind: gov-error
- laws.gov.fj (as read by Global law on 2026-10-28) prints s 125A 'Withholding tax not as a final tax' and s 28A 'Pandemic reserve'; the gazetted Income Tax (Budget Amendment) Act 2024 (No 5 of 2024) s 3 'deleting section 28A' and s 6 'deleting section 125A' (in force 1 August 2024). The Act's Table of Amendments ends at Act 5 of 2023 and omits Acts 5 of 2024, 9 of 2025, 1 of 2026 and 14 of 2026; the FNPF Act's table omits Act 21 of 2026 (16 % contributions from 1 August 2026). The same site's 'Laws as published' section has all of them: the consolidation, not the gazette, is stale.
- provisions: ITA 2015 ss 28A, 125A; Act 5 of 2024 ss 1, 3, 6; FNPF Act s 37(4A)
- Lean: FjTax (model built from the gazetted amending texts, not the consolidation)
- status: recorded; draft note to the Office of the Attorney-General below

### F2 Bank interest is exempt only while gross income is at most $30,000: one dollar more makes all of it taxable (10 % final withholding)
- kind: statute-fault
- Exempt Income Schedule Part 4 para (9)(c): 'the interest derived from a licenced Bank, by an individual taxpayer gross income $30,000 or less in a year'. Wages 29,000 + interest 1,000: tax 0; wages 29,001 + interest 1,000: 100 (#guard). The notch equals 10 % of the interest, whatever its size; and 'gross income' (s 14) excludes exempt income (s 14(2)), so the test is circular unless the interest is counted, as the model does.
- provisions: Exempt Income Regs Sch Part 4 (9)(a)-(c); ITA ss 14(2), 112, 125(1)(b); Rates Regs Sch (5A)(a)
- Lean: FjTax.person (#guard 29,000/29,001)
- status: modelled

### F3 Dividends are exempt for individuals while wages bear up to 39 % plus 8 % FNPF: an owner-manager paying profits as dividends from a 25 % company pays far less than on salary
- kind: loophole-known
- Exempt Income Schedule Part 5(1) 'Any dividend received is exempt income'; company rate 25 % (Rates Regs Sch (3)(c)). Income-type scanner: dividends +25.4 % of income better than wages at 5 x scale (250,000); interest +15.6 % (10 % final), capital gains +15.6 % (CGT 10 %).
- provisions: Exempt Income Regs Sch Part 5(1); Rates Regs Sch (3)(c), (5A), (7)
- Lean: FjTax.out (scanner income type)
- status: modelled; scanner reproduces

### F4 The FNPF Act's 'eight-eighteenths or 44.4% (whichever is the greater)' never uses 44.4 %
- kind: statute-fault
- s 39(1): the employer may recover 'eight-eighteenths or 44.4% (whichever is the greater)' of the 18 % contribution; 8/18 = 44.44 % > 44.4 % for every wage (#guard), so the alternative is dead text; the employee pays 8 % of wages, not deductible (ITA s 23 is for employers only).
- provisions: FNPF Act 2011 ss 37(4), 39(1)
- Lean: FjTax.fnpfMonthCents (#guard)
- status: modelled

### F5 Non-residents pay 20 % from the first dollar: $6,400 more than a resident at every income above $270,000
- kind: loophole-known
- Rates Regs Sch para (1) non-resident column ('0-30,000 | 20% of excess over $0') vs resident column; from 270,000 the columns differ by exactly 6,400 (#guard). Residence (s 6: 183 days, domicile) therefore has a fixed value at high incomes.
- provisions: Rates Regs Sch para (1); ITA s 6
- Lean: FjTax.schedNonRes (#guard)
- status: modelled (input resident: false)

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Pay an owner-manager in exempt dividends rather than salary (company 25 %) | recreated: income-type scanner: +25.4 % | Exempt Income Sch Part 5(1); Rates Regs Sch (3)(c) |
| K2 | Hold savings as bank deposits: interest 10 % final (exempt at gross income <= 30,000) instead of marginal rates up to 39 % | recreated: income-type scanner and #guard | ITA ss 112, 125(1)(b); Exempt Income Sch Part 4(9) |
| K3 | Realise gains as capital gains (CGT 10 %) rather than income | recreated: scanner: +15.6 % | ITA s 65; Rates Regs Sch (7) |
| K4 | Split income with a spouse (individual taxation, two 30,000 tax-free bands) | recreated: filing-unit scanner: 6,400 at 2.1 x scale | ITA s 8 (no joint return) |
| K5 | Employer FNPF contributions above the statutory minimum (up to 10 % of salary) are exempt to the employee: salary sacrifice into FNPF | not modelled: needs an input | Exempt Income Sch Part 6(1), (1A) |
| K6 | First home / family home exempt from CGT | not modelled | ITA s 67(1)(b),(f), (4) as substituted by Act 9 of 2025 s 6 |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with the cited scale.json (scale 50,000, start of the 20 % band)
- direct household checks with the exe (interest exemption edge, non-resident column, FNPF rounding)
- every Income Tax and FNPF act and legal notice 2023-2026 in the laws.gov.fj 'Laws as published' listing read for changes to the individual rates, s 8, s 23, s 125, the Exempt Income Schedule and FNPF ss 37-39
- Global law: changes and Tables of Amendments of the ITA, the Rates Regulations, the Exempt Income Regulations and the FNPF Act

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and PFTAC (Pacific Financial Technical Assistance Centre) tax-policy diagnostics for each country
- Asian Development Bank Pacific Economic Monitor and country tax-reform reports (Palau 2023 reform, RMI 2025 reform)
- Pacific Islands Tax Administrators Association (PITAA) and Pacific Islands Forum Secretariat papers on PAYE and provident funds
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on Pacific provident funds, final-withholding wage taxes and Compact-state (FSM, RMI, Palau) wage taxes
- OECD Revenue Statistics in Asia and the Pacific (country notes for Fiji, PNG, Samoa, Solomon Islands, Tonga, Nauru, Kiribati, Tuvalu)

## Draft issue text (not filed)

Draft (not sent) to the Office of the Attorney-General, Laws of Fiji: the consolidated Income Tax Act 2015 still contains sections 28A and 125A, deleted by the Income Tax (Budget Amendment) Act 2024 (No. 5 of 2024) ss 3 and 6 with effect from 1 August 2024, and its Table of Amendments does not list Acts 5 of 2024, 9 of 2025, 1 of 2026 and 14 of 2026; the FNPF Act 2011 consolidation does not show s 37(4A) inserted by Act 21 of 2026.


Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Stale consolidation (builder). |
| F2 | statute-fault | confirmed | 100 FJD (10 % of 1,000 of interest) for one dollar of wages at 29,000. exe and #guard L1FJ.F2. Evidence: exe + Lean `L1FJ.F2` (`world/loopholes/rest/lean/L1FJ.lean`, 1 #guard): tot(b)-tot(a) = 100; statute re-read: `law/gl_exempt_sch.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | loophole | confirmed | 63,601 FJD on 250,000 of wages vs 0 on 250,000 of dividends (company 25 %). exe and #guard L1FJ.F3. Evidence: exe + Lean `L1FJ.F3` (`world/loopholes/rest/lean/L1FJ.lean`, 2 #guard): tot(b) = 0; tot(a) = 63601; statute re-read: `law/gl_exempt_sch.txt`. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |
| F4 | statute-fault | model-proved | FjTax #guard (model build): 8/18 > 44.4 %. |
| F5 | fact | confirmed | 6,400 FJD at 300,000. exe and #guard L1FJ.F5; rates schedule re-read. Evidence: exe + Lean `L1FJ.F5` (`world/loopholes/rest/lean/L1FJ.lean`, 1 #guard): it(b)-it(a) = 6400; statute re-read: `law/gl_rates_regs.txt`. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/FJ.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F3).
