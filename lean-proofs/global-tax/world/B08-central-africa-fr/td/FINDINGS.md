# Chad (TD) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Since 2023 work income and capital income are taxed separately: dividends 20 % flat against at most 18 % of gross on salary
- kind: loophole-known
- CGI art. 1 IV-V (LF 2023 art. 36): work income on the barème, capital income at 20 % of each category's net. With the 40 % wage deduction (2016 art. 48) the top rate on gross salary is 30 % x 60 % = 18 % (scan), below the 20 % on dividends: unlike most countries, an owner-manager pays less as an employee. 30 M of salary: 3 621 000; 30 M of dividends: 6 000 000 (exe).
- provisions: CGI art. 1 (LF 2023 art. 36); CGI 2016 art. 48
- Lean: TdTax.out
- status: modelled (base flagged)

### F2 The quotient's tariff reference was dropped in 2025 but the quotient articles were never repealed in the texts read
- kind: statute-fault
- LF 2025 art. 22 rewrote art. 116 without 'se substitue au tarif fixé par l'article 115'; art. 1 IV (2023) applies the barème to 'les revenus visés à l'article 9-II'. Whether arts. 109-115 (parts, the 2016 tariff) survive could not be settled without a current CGI: two readings, the model takes 'no quotient'.
- provisions: CGI arts. 1, 109-116 (2016), LF 2025 art. 22
- Lean: -
- status: reading recorded

### F3 A flat 4 800 a year PSA on every salary, whatever its size
- kind: model-fix
- LF 2024 circular § 57: 'Le tarif du PSA est de 400 FCFA et s'applique sur l'ensemble des traitements et salaires' (food-security levy replacing ONASA): regressive, an entry cost of 4 800 a year (scan notch 4 799 at the first franc).
- provisions: LF 2024 (circular 001 § 56-58)
- Lean: TdTax.out (PSA)
- status: modelled (official secondary)

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Take income as salary rather than dividends (18 % vs 20 %) | recreated: income-type scanner, F1 | CGI art. 1 IV-V; 2016 art. 48 |
| K2 | 40 % flat deduction on net wages | recreated: assumed still in force | CGI 2016 art. 48 |
| K3 | Benefits in kind capped at flat % of gross (logement 15 %, véhicule 8 %, nourriture 25 % max 50 000) | not modelled | CGI 2016 art. 46 |
| K4 | Women's groups producing fortified foods exempt (LF 2023 art. 35) | not modelled | LF 2023 art. 35 |
| K5 | Split income with a spouse (individual barème) | recreated: split-gain scanner: up to 1.08 M | CGI art. 1 IV |

## Step 5: what was searched

- kernel scanners via scan_world.py (scale 6 M, art. 1 IV band)
- LF 2023, LF 2025 OCR for IRPP articles; LF 2024 circular
- salary vs dividends (exe)

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (CM CG CD MG among the covered countries)
- IMF Article IV and technical-assistance reports on the CEMAC members, DRC, Madagascar, Burundi, Djibouti, Comoros
- CEMAC directives on the harmonisation of direct taxation (IRPP/IS) and the CIMA/CIPRES social-security rules
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- droit-afrique.com and juriafrique compilations (droit-afrique answered 403 to scripts and the laptop; not bypassed)
- Academic work on family quotients in francophone Africa and on informal-sector minimum taxes

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5R sweep P2-6: household-total employee-contribution input allotted by wages (W5 review pass 2, 2026-11-20)
- kind: model-fix (cross-country sweep from NI W5R-1)
- The optional household-total employee-contribution input was halved between two adults, so a one-earner couple
  deducted half of the earner's own contributions. The deduction provision this model already cites deducts each
  employee's own contributions from that employee's income; the total is now allotted in proportion to wages (halves
  only when nobody has wages). Checked on 400 random households: outputs change only for two adults with the input and
  unequal wages. Script: world/w5/review2/sweep_alloc.py. Rescanned (scan_world.py).
- status: model changed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/TdTax/Verify.lean` (imported by the `TdTax` library and built; each guard evaluates `TdTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/TD.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed (personal side) | Since LF 2023 capital income pays 20 % flat while salary pays at most 18 % of gross: 30 M as salary keeps 2,374,200 more than as dividends. An owner-manager is better off as an employee (company-side tax not modelled, which widens the gap: salary is deductible). G: f1_salary_cheaper_than_dividends. S: CGI art. 1 IV-V (LF 2023 art. 36) as cited; law/cgi2016.raw.txt:36 ('Revenus de capitaux mobiliers' as a category). |
| F2 | lead | Whether the quotient articles survive LF 2025: reading. |
| F3 | confirmed | PSA 400 a month on every salary: 12 F of annual pay costs 4,788 of net; regressive entry cost. G: f3_psa_entry. S: law/circ_lf2024.raw.txt:453-454 ('57. Le tarif du PSA est de 400 FCFA et s'applique sur l'ensemble des traitements et salaires'). |
| W5R P2-6 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: first-unit notch 4,799 = F3; bands above the top rate (20 % max, 18 % avg) = rounding. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Since 2023 dividends pay 20 % flat, salary at most 18 % of gross: pay yourself a salary | income-type gap | **new**: PwC Chad prints the 2023 split (work incomes on the barème, capital incomes at proportional rates: 'Dividends, incomes from shares 5/10/20'), not that salary now beats dividends for owner-managers; OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'Tchad loi de finances 2023 IRPP revenus de capitaux mobiliers 20% revenus du travail'; 'Chad personal income tax reform 2023 capital income' (1246 hits, titles checked); OpenAlex broad 'Chad personal income tax', 'Chad income tax wages', 'Chad tax system reform' (75 records, titles and abstracts grepped, 2 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (chad, 5 individual pages): 14 passages with the item's terms; Crossref IMF prefix 10.5089 'Chad tax policy' (8302 records, titles only). Record: world/loopholes/africa_mena/search/TD-F1.json |
| F3: PSA of 400 F a month on every salary from the first franc | cliff or notch | **new**: PwC Chad: no PSA (only a 15 % food benefit-in-kind rule); OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'Tchad prélèvement pour la sécurité alimentaire PSA salaires'; 'Chad food security levy salaries' (1073 hits, titles checked); OpenAlex broad 'Chad personal income tax', 'Chad income tax wages', 'Chad tax system reform' (75 records, titles and abstracts grepped, 2 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (chad, 5 individual pages): 1 passages with the item's terms. Record: world/loopholes/africa_mena/search/TD-F3.json |

<!-- L1-VERIFICATION END -->
