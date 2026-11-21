# Barbados (BB) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The reverse tax credit has no amount for any year after 2016
- kind: statute-fault
- s. 65D(1)(e) (Act 2020-10) makes employees earning under $25,000 eligible 'for income year 2018 and subsequent income years', but s. 65D(2) as last replaced (Act 2015-16) fixes the credit only 'for the income year 2013 to the income year 2016, the amount of $650'. No Act on BRA's list sets an amount for 2017 onwards. The model gives 0 and flags it.
- provisions: ITA s. 65D(1)(e), (2) (Acts 2013-18, 2015-16, 2020-10)
- Lean: BbTax.out (unsupported flag)
- status: recorded

### F2 The compensatory income credit depends on a 'prescribed rate' that was not found, and stops dead at $35,000
- kind: statute-fault
- s. 65G: employees earning more than $25,000 and not more than $35,000 get 'up to $1 250 calculated at the prescribed rate of their taxable income'. One dollar above 35,000 loses the whole credit (up to 1,250): a notch whose size depends on a rate outside the Act (input bbCicRateBp).
- provisions: ITA s. 65G (Act 2020-10 s. 11)
- Lean: BbTax.person
- status: modelled with an input

### F3 Barbados employees pay NIS on income-tax-taxed pay: the employee share is not deductible
- kind: loophole-known
- s. 30(1)(a) (employee contributions) 'Repealed by 1992-28'; only the employer's contributions are deductible (s. 30(1)(b)). Combined marginal rate above 50,000 of taxable income: 28.5 % + 11 % = 39.5 % up to the NIS ceiling.
- provisions: ITA s. 30
- Lean: BbTax.person
- status: modelled

### F4 The Resilience Fund (from April 2025) is levied on gross earnings without the NIS ceiling
- kind: model-fix
- nis.gov.bb: 0.25 % 'calculated on gross earnings' from 1 April 2025, replacing the 0.1 % Catastrophe Fund on insurable earnings; the model applies the old rate January-March (official secondary).
- provisions: NIS contribution rates page (official secondary)
- Lean: BbTax.nisMonthCents
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Pensioners aged 60+ get a 40,000 allowance instead of 25,000 | recreated | ITA s. 38B(1)(b) |
| K2 | Spouse with no income: extra 3,000 allowance | recreated: filing-unit scanner | ITA s. 38B(1)(c) |
| K3 | Registered retirement savings plan contributions deductible | not modelled | ITA ss. 24A, 24F |
| K4 | Foreign income remitted through the banking system earns a credit (Sixth Schedule) | not modelled | ITA s. 12I (Act 2020-10) |
| K5 | Stay at or below 35,000 to keep the compensatory income credit | recreated: F2 (input) | ITA s. 65G |

## Step 5: what was searched

- kernel scanners with scale 50,000 (s. 42 threshold)
- every Income Tax (Amendment) Act on the BRA 'Income Tax Act' page (2009-2025), text layers
- s. 65D amount chain (2007 consolidation, 2013-18, 2015-16, 2020-10)

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | explained | No amount for the credit after 2016 (builder). |
| F2 | statute-fault | confirmed | up to 1,250 BBD at 35,001 (500 at an assumed 5 % rate: the prescribed rate is not found). exe and #guard L1BB.F2 with input bbCicRateBp = 500 (assumption, not law). Evidence: exe + Lean `L1BB.F2` (`world/loopholes/rest/lean/L1BB.lean`, 1 #guard): tot(b)-tot(a) = 500; statute re-read: `law/acts/Income_Tax__Amendment___Act_2c_2020-10.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | fact | explained | Employee NIS not deductible (fact). |
| F4 | record | explained | Model fix. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BB.json`): timing 1,284-1,615 = the NIS ceiling; marriage bonus 855 = the spouse allowance (catalogue K2); METR 161 % at 0 is the first-dollar NIS line (no money at 1 BBD); income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
