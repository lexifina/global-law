# Jamaica (JM) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The tax authority's 2025 payroll guide misprints the 2026 and 2027 threshold computations
- kind: gov-error
- TAJ 'Payroll Taxes and Statutory Contributions' Table # 3 computes Jan-Mar 2026 as '($1,799,360 x 3)/12' although the text says the threshold is 1,799,376; Table # 4 uses '$1,907,360' for Jan-Mar 2027 although April 2026 moves it to 1,902,360, and prints 1,426,770 (the 2026 figure) for April-December 2027 where 2,003,496 x 9/12 = 1,502,622; the 'Effective Threshold - 2027' 1,978,212 is right only with the correct cells. Table # 2 (2025) adds up (#guard).
- provisions: TAJ Payroll guide (2025-04-29) Tables # 2-4
- Lean: JmTax (#guard on Table # 2)
- status: recorded (official secondary)

### F2 The 30 % rate applies to statutory income above J$6 million, not to income above the threshold plus 6 million
- kind: model-fix
- TAJ: 'SI above the Threshold up to $6M is taxed at 25%. SI in excess of ... $6M yearly ... is taxed at 30%'. The 25 % band is therefore 6 M less the threshold wide.
- provisions: TAJ rates note
- Lean: JmTax.taxOf
- status: modelled

### F3 Four payroll charges with four different bases
- kind: loophole-known
- NIS 3 % of gross up to 5 M; NHT 2 % of all gross; Education Tax 2.25 % of statutory income (gross less NIS and pension); income tax on statutory income. Approved pension contributions reduce income tax and Education Tax but not NIS or NHT (pension not modelled).
- provisions: TAJ Table #5
- Lean: JmTax.person
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Approved pension contributions reduce statutory income (income tax and Education Tax) | not modelled | TAJ definitions (allowable deductions) |
| K2 | Age relief and pension relief (250,040 each in 2025) | recreated: age 65+; pension | TAJ thresholds table |
| K3 | Employee share ownership plan purchases deductible | not modelled | TAJ definitions (ESOP Act) |

## Step 5: what was searched

- kernel scanners with scale 6,000,000 (start of the 30 % band, official secondary)
- TAJ rates-and-fees pages; Internet Archive CDX of laws.moj.gov.jm for the ITA

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Round D2 (improvement agent, 2026-11-20): D1 dev failures settled from the statute

### D2-1 Approved pension contributions deducted (model fix); the TAJ case residual is the dataset's threshold
- kind: model-fix
- Income Tax Act s. 44A (1) (approved retirement scheme contributions "allowed to be deducted"); TAJ "Payroll Taxes and
  Statutory Contributions" (updated April 2025, law/payroll.txt l. 45): "Allowable deductions may include contributions to
  NIS, an approved pension fund, an approved retirement scheme"; its Illustration 2: "Statutory Income ($480,000 -
  ($19,200 + $12,500))", Education Tax "2.25% of Statutory Income". The model now deducts `pensionContributions` (first
  adult) from statutory income and the Education Tax base; the Fourth Schedule limit was not read (none applied).
  #guard on Illustration 2 annualised.
- Dev: 1 / 1 -> 1 / 2 within 1 % (of 3). The two remaining differences are the reference values' threshold: the
  converted cases annualise one month's threshold (141,674, January-March 2025) x 12, while YA 2025's effective
  threshold is 1,774,554 (TAJ: 1,700,088 for 3 months and 1,799,376 for 9; the model's) and the TAJ guide's April 2025
  illustration itself uses 149,948 (tax 74,588). Reported to the test agent (software/ISSUES.md, D2).
- Lean: JmTax.person (penContrib)
- status: model changed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | model-proved | JmTax #guard on Table 2 (model build). |
| F2 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F3 | fact | explained | Four bases (fact). |
| D2-1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/JM.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
