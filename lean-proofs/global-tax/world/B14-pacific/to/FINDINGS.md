# Tonga (TO) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Tonga's income tax rates are not in the published revised edition: they sit in a Ministerial Order that the Attorney-General's site does not carry
- kind: gov-error
- ITA s 5(1): 'The Minister shall, with the approval of Cabinet by Order impose ... income tax for each fiscal year'; the AGO point-in-time list for 2025-07-01 shows the Act, the 2020 amendment and the Regulations but no Order; the Income Tax (Amendment) Order 2017 is on the Ministry of Revenue and Customs site only, and refers to a Principal Order ('Order in Council No. 5 of the 21st January 2008') that neither site publishes. The 2025 rates therefore rest on an official secondary publication (access B).
- provisions: ITA s 5(1); Income Tax (Amendment) Order 2017 paras 1-2
- Lean: ToTax.sched
- status: recorded

### F2 The bands have not moved since 1 July 2017
- kind: statute-fault
- Order 2017 para 1(3) 'come into effect on 1 July 2017'; no later Order listed by the Ministry. Info for fiscal drag.
- provisions: Income Tax (Amendment) Order 2017
- Lean: ToTax.sched (#guard)
- status: recorded

### F3 Dividends are exempt (s 21) while salary is taxed up to 25 % plus NRBF 5 %
- kind: loophole-known
- ITA s 21; income-type scanner: dividends +25.3 % at 5 x scale (interest is a model limitation: its withholding is not modelled).
- provisions: ITA s 21
- Lean: ToTax.out
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Pay an owner-manager in exempt dividends | recreated: income-type scanner | ITA s 21 |
| K2 | Split income with a spouse (individual assessment, two 10,000 zero bands) | recreated: filing-unit scanner: 7,000 at 4 x scale | ITA s 5 |
| K3 | Pensions and lump sums from approved funds exempt | not modelled | ITA ss 19(2), 20 |
| K4 | Small businesses under the turnover-based small business tax (s 8, Third Schedule) | not modelled | ITA s 8 |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with the cited scale.json (scale 30,000, start of the 20 % band)
- AGO point-in-time lists (I, N, R) for 2025-07-01 and the Income Tax Act legislation history table
- revenue.gov.to Tax Legislations and New Legislations pages (laptop) for income tax Orders

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and PFTAC (Pacific Financial Technical Assistance Centre) tax-policy diagnostics for each country
- Asian Development Bank Pacific Economic Monitor and country tax-reform reports (Palau 2023 reform, RMI 2025 reform)
- Pacific Islands Tax Administrators Association (PITAA) and Pacific Islands Forum Secretariat papers on PAYE and provident funds
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on Pacific provident funds, final-withholding wage taxes and Compact-state (FSM, RMI, Palau) wage taxes
- OECD Revenue Statistics in Asia and the Pacific (country notes for Fiji, PNG, Samoa, Solomon Islands, Tonga, Nauru, Kiribati, Tuvalu)


Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Order not published (builder). |
| F2 | fact | explained | Unindexed bands. |
| F3 | loophole | confirmed | 0 tax on 150,000 of dividends vs 38,000 on wages. exe and #guard L1TO.F3. Evidence: exe + Lean `L1TO.F3` (`world/loopholes/rest/lean/L1TO.lean`, 2 #guard): tot(a) = 0; tot(b) = 38000; statute re-read: `law/IncomeTaxAct_3.txt`. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/TO.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F3).

### D9M-1 Rates from 1 July 2021: five bands, not the 2017 Order's four; the instrument's text not reached (D9 review, 2026-11-20) - OPEN model gap
- Evidence: the Ministry of Revenue and Customs PAYE page (revenue.gov.to/paye, fetched 2026-11-20 from the laptop by D9
  WP5; copy `law/d9/revenue_gov_to_paye_20261120.html`, sha256 06c61b97...) states "New Tax Rate - 1st July 2021 ...
  $0 - $12,000 0% (Tax Free); $12,001 - $30,000 10%; $30,001 - $50,000 15%; $50,001 - $70,000 20%; $70,001 and over 25%",
  and serves only the "PAYE Worksheet - 1st July 2021". The model applies the Income Tax (Amendment) Order 2017 (0 % to
  10,000, 10 % to 30,000, 20 % to 60,000, 25 % above). The D9 grid `to_official_paye_worksheet_2021_grid` (the 2021
  worksheet, dev 123 / 1,056 exact, every miss with the model above: +200 at low pay = 10 % x 2,000, +1,700 at the top)
  is explained entirely by this change (the worksheet's own formula reproduces all 1,056 dev values; diagnosis only).
- The instrument: ITA s 5(1) sets rates "by Order"; no Order with the 2021 rates was found. The "Income Tax (Amendment)
  Order 2021" listed in Gazette Supplement Extraordinary No 12 of 27 Sep 2022 is the Order of 30 June 2021 (Gazette
  Supplement Extraordinary No. 21, PacLII TOGovGaz 2021/24; `law/d9/TOGovGaz_2021_24_SuppExtra21_20210630.pdf`): it
  revokes income tax on the salaries of local employees of the World Bank (paras (1)-(3)), in force on gazettal and
  expiring 30 June 2026 (paras (4)-(5)); it sets no rates. The other PacLII-archived supplements around 1 July 2021
  (Nos. 14, 18, 20, 22-25 and Gazette Extraordinary Nos. 169-170; copies in `law/d9/`) carry no income tax rate Order;
  supplements Nos. 8-13, 15-17 and 19 of 2021 are not in the PacLII index; revenue.gov.to's legislation pages list the
  2017 Order only; pacliirms.paclii.org answers a challenge (not bypassed); ago.gov.to does not index Orders.
- Status: model out of date for FY 2025/26 (open: the rate Order's text is needed before the schedule is changed;
  the Ministry's notice is cited but not used to change the model). The World Bank Order (expired 30 June 2026, inside
  FY 2025/26) is noted for the unsupported list.
- provisions: ITA (Cap. 11.05) s 5(1); Income Tax (Amendment) Order 2017 para 2; Ministry PAYE notice "New Tax Rate -
  1st July 2021"; Income Tax (Amendment) Order 2021 (30 June 2021, World Bank employees)
