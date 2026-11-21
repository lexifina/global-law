# Cameroon (CM) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The communal development tax (TDL) is a step function of the monthly base salary: one franc more than 250 000 a month costs 6 000 a year
- kind: statute-fault
- CGI art. C 58 (2024) / C 86 (2026) charges 3 000 to 30 000 a year by band of monthly base salary (62 000 / 75 000 / 100 000 / 125 000 / 150 000 / 200 000 / 250 000 / 300 000 / 500 000). Each edge is a notch: the largest is 18 000 -> 24 000 at 250 000 a month (exe: 2 999 988 a year pays TDL 18 000, 3 000 012 pays 24 000). Below 62 000 a month no TDL; at 62 000 3 000 a year, though the IRPP itself is zero there (art. 81 threshold). The scanner finds METR bands > 100 % at every edge (largest notch 5 999 at 1.0 'AW' = 3 M a year).
- provisions: CGI art. C 58 (2024) = C 86 (2026), C 59/C 87
- Lean: CmTax.tdl (#guard 61 999 -> 0, 62 000 -> 3 000)
- status: modelled; scan reproduces

### F2 The audiovisual fee (RAV) and the Crédit Foncier contribution are separate wage taxes with their own steps
- kind: loophole-known
- Ordonnance 89/004 art. 3 (5): a monthly flat amount rising 1 300 per 100 000 of monthly gross (750 at 50 001, 13 000 above 1 000 000), so each 100 000 edge costs 1 300 a month; CFC 1 % of gross rounded down to 1 000 a month (Loi 77-10 art. 6). Together with TDL they add 0.3-2.4 % of gross outside the IRPP; pensions are exempt from both (art. 5, art. 6).
- provisions: Ord. 89/004 arts. 3, 6; Loi 77-10 arts. 4-6
- Lean: CmTax.rav, CmTax.person (cfc)
- status: modelled

### F3 The 30 % flat deduction is capped at 4.8 M, and the CNPS ceiling at 9 M a year: the marginal rate rises at 16 M of gross
- kind: model-fix
- art. 34 caps the 30 % frais at 4 800 000, reached at 16 M gross; above it every franc is fully taxable (marginal IRPP + CAC 38.5 % instead of 27 %). The CNPS pension (4.2 %, cap 750 000 a month) stops at 9 M. Statutory top combined rate (scan, 10 'AW'): 39.3 %.
- provisions: CGI art. 34; Décret 2016/072 art. 4
- Lean: CmTax.person
- status: modelled

### F4 Owner-manager: dividends 16.5 % (11 % from a small company) against up to 38.5 % on salary
- kind: loophole-known
- IRCM is a final 15 % (art. 70 (1)) plus 10 % CAC (art. 71) = 16.5 %; from 2025 10 % + 1 % = 11 % for dividends 'régulièrement distribués' by companies with turnover <= 3 bn (art. 70 (2), LF 2025 circular §§ 121-126). 10 M as salary costs IRPP 1 242 700 + CAC 124 270 + levies; 10 M as dividends 1 650 000 (1 100 000 from an SME). The company-side IS (art. 17) was not modelled, so the full comparison needs the owner-manager scan's company side.
- provisions: CGI arts. 69, 70, 71; LF 2025 circular
- Lean: CmTax.out (input dividendsSmallCompany)
- status: modelled (personal side)

### F5 Individual taxation: no relief at all for children or a dependent spouse
- kind: model-fix
- The IRPP is assessed on each person's own income (art. 67) with one 500 000 abatement on wages (art. 29); there is no quotient and no child credit, so a one-earner family of four pays the same as a single person (scan: no marriage penalty or bonus; split gains up to 747 370 = 24.9 % of the scale wage come from moving income between two individual taxpayers).
- provisions: CGI arts. 29, 67
- Lean: CmTax.out
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Pay part of the wage as allowances 'destinées à couvrir les frais inhérents à la fonction' or family allowances (exempt) | not modelled: the household contract has no allowance field | CGI art. 31 1°-2° |
| K2 | Benefits in kind valued at a flat % of gross (art. 33 barème) below their real value | not modelled | CGI art. 33 |
| K3 | Pay the owner-manager in dividends (16.5 % / 11 % final) rather than salary | recreated: income-type scanner and F4 | CGI arts. 70, 71 |
| K4 | Shift income to a spouse or child (individual taxation, a 500 000 abatement each) | recreated: split-gain scanner | CGI arts. 29, 67 |
| K5 | Keep the monthly base salary just below a TDL or RAV band edge (bonuses not in 'salaire de base' for TDL) | recreated: METR scanner notches, F1 | CGI art. C 58; Ord. 89/004 art. 3 |
| K6 | Stay below 62 000 a month (no withholding, art. 81) | recreated: the annual IRPP is zero there anyway; TDL starts exactly there | CGI art. 81 |
| K7 | Exempt severance: the damages part of a dismissal indemnity | not modelled | CGI art. 31 12° |
| K8 | Choose the impôt libératoire / simplified regime for a side business | not modelled: self-employment unsupported | CGI art. 27 (4), art. 69 (2) |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with scale 3 M (art. 69 band)
- direct band-edge checks with the exe (TDL 250 000/month, 62 000/month; dividends vs wages)
- CGI 2024 vs CGI 2026 wage articles compared word for word (same text)

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (CM CG CD MG among the covered countries)
- IMF Article IV and technical-assistance reports on the CEMAC members, DRC, Madagascar, Burundi, Djibouti, Comoros
- CEMAC directives on the harmonisation of direct taxation (IRPP/IS) and the CIMA/CIPRES social-security rules
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- droit-afrique.com and juriafrique compilations (droit-afrique answered 403 to scripts and the laptop; not bypassed)
- Academic work on family quotients in francophone Africa and on informal-sector minimum taxes

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Round D6 (improvement agent, 2026-11-20): holdout gaps checked against the statute (aggregates only)

### D6-1 The DGI IRPP barème follows the DGI's own withholding formula, not the CGI: convention flag, statute unchanged
- kind: convention
- Statute re-read (CGI édition officielle 2026, identical in the 2024 edition; LF 2025 changes no wage provision):
  art. 29 abatement of 500 000 a year on wages; art. 34 "frais professionnels calculés forfaitairement au taux de 30 %,
  ainsi que les cotisations versées ... (CNPS) au titre de la retraite obligatoire" deducted, and "Le montant résultant
  de l'application du taux forfaitaire ... est plafonné à FCFA quatre millions huit cent mille (4 800 000) par an"; art.
  69 (1) 10 / 15 / 25 / 35 % on 0-2 M / 2-3 M / 3-5 M / above 5 M; art. 71 CAC 10 % of the tax; CNPS employee pension
  4,2 % up to 750 000 a month (Décret 2016/072 arts. 3-4). The model applies all of these: no statute error found.
- The DGI publishes its withholding method with the CGI: annex "NOTE EXPLICATIVE SUR L'UTILISATION DU BAREME DE L'IRPP
  (Nouvelle version)" (CGI 2026 pp. 877-879, signed by the Directeur Général des Impôts), whose "Formule de calcul ...
  servira ... à la rédaction des programmes informatiques de retenues de l'IRPP sur les salaires": Sbm x 70 % less "Sbm *
  2,8 %" (CNPS, "plafonné à 300 000") less 41 667, then fixed amounts 16 693 / 29 188 / 70 830 and (Sbm - band) x 70 % x
  15 / 25 / 35 %. It departs from the statute in two ways: CNPS at the pre-2016 2,8 % / 300 000 instead of 4,2 % /
  750 000, and no 4 800 000 cap on the 30 % frais. The second makes the barème lower than the statute above about
  1,33 M a month (24 M a year: 4 768 980 against the statute's 5 512 700, -13,5 %), the first slightly higher below.
  This fits the D6 aggregate (model above on 1,787 of 2,046 rows, median 14 %), though the per-case details are sealed.
- Change: convention flag `--dgi-bareme` (CmTax.dgiMonthly; #guards on the note's fixed amounts 16 693 / 29 188 and
  642 415 at 3 000 000; the note prints 70 830 where its own formula gives 70 838, kept as printed in the upper band),
  declared in conventions.json per dataset for `world_cm_dgi_bareme_irpp_2025` with the citation (rule 8). Statute mode
  unchanged (0 of 300 random households differ from the D6 exe).
- Finding for the DGI: its withholding barème under-deducts the 4,2 % CNPS and ignores the art. 34 cap; employees above
  about 1,33 M a month are under-withheld and owe the difference on assessment.
- status: convention flag added

## Round D7 (improvement agent, 2026-11-20)

### D7-1 `--dgi-bareme` re-checked against the DGI note: the formula is as published; the 2025 barème is not
- kind: test-note
- Checked element by element against the note (CGI 2026 pp. 877-879): CNPS term "Sbm * 2,8 %" with the 300 000 cap (the
  note's text, and its fixed amount 16 693 = (217 000 - 8 400 - 41 667) x 10 %); frais "Sbm * 70 %" with no cap; the
  monthly abatement 41 667 (500 000 / 12, art. 29); bounds 62 000 / 310 000 / 429 000 / 667 000 and fixed amounts
  16 693 / 29 188 / 70 830 (consistent with the annual bands 2 / 3 / 5 M at 70 % less 8 400 and 41 667); CAC 10 % of the
  IRPP (art. 71; mapped to detail.centimesAdditionnels); monthly tax rounded to the franc, x 12 (the note's rows are every
  250 F; "l'arrondi se fera à la ligne inférieure" concerns the salary lookup, not the tax). No error in the flag.
- The D7 aggregate (model above on every row, median 6,5 %) therefore means the 2025 DSSI barème was not computed with the
  note's parameters. From aggregates only: a CNPS deduction of 4,2 % without the 750 000 ceiling and no frais cap would put
  the note's formula about 3-8 % above (7 % at 1,2-3 M a month), close to the reported median; this is a lead, not a
  citation. Under rule 8 a second flag needs the DGI's own statement of the 2025 parameters (e.g. a note printed on the
  barème itself): for the test agent to check without reading values. Statute mode and the flag unchanged.
- status: open (convention parameters)

### W5S4-1 syscohada-fiscal 3.0.0 (hypnozbizo), Cameroon: no 500,000 abatement and no CNPS deduction (W5 review pass 4, 2026-11-20)
- kind: software-error
- `cm_open_syscohada_fiscal_hypnozbizo_grid`: the art. 69 barème is applied to 70 % of gross; CGI art. 29 'après abattement d'un montant forfaitaire de 500 000 F CFA' and the deduction of the CNPS pension contribution (salary capped at 4,800,000 a year) are omitted. Dev: tool above in every case (-307,300 = 35 % x (500,000 + 378,000) at high wages).
- status: recorded (world/IMPROVE_W5.md pass 4)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/CmTax/Verify.lean` (imported by the `CmTax` library and built; each guard evaluates `CmTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/CM.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | TDL steps by monthly base salary: crossing 250,000 a month costs 6,098 of net a year (18,000 -> 24,000); rescan notches at every edge (largest 5,999). G: f1_tdl_250k_month; T: #guard tdl 61 999 -> 0, 62 000 -> 3 000. S: law/cgi2024.raw.txt:29703 (art. C 58: 'Les taux maxima de la taxe de développement local sont' ... the monthly-salary bands). |
| F2 | explained | RAV and CFC steps: known levies, small. |
| F3 | explained | 30 % frais cap at 4.8 M: design (rate rises at 16 M). |
| F4 | confirmed (personal side) | 10 M as dividends keeps 357,530 more than as salary (IRCM 15 % + 10 % CAC final), 907,530 more from a company with turnover <= 3 bn (10 % + 1 %, LF 2025). The company's IS is not modelled. G: f4_dividends_vs_salary, f4_sme_dividends_vs_salary. S: law/cgi2024.raw.txt:5314 (art. 70 (1)); LF 2025 circular §§ 121-126 as cited. |
| F5 | explained | No family relief: design. |
| D6-1, D7-1, W5S4-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: 13 notches, all TDL edges (F1); bands above the top rate (up to 631 %) are those edges; timing gain 39,242 = TDL edges. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: TDL steps by monthly base salary | cliff or notch | **new**: Nothing found (no PwC page for the country under 'cameroon'; OpenAlex: nothing on the TDL). | 2026-11-20: OpenAlex specific queries 'Cameroun taxe de développement local salaire de base barème'; 'Cameroon local development tax wages' (6646 hits, titles checked); OpenAlex broad 'Cameroon personal income tax', 'Cameroon income tax wages', 'Cameroon tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Cameroon tax policy' (8374 records, titles only). Record: world/loopholes/africa_mena/search/CM-F1.json |
| F4: Dividends 16.5 % (11 % from an SME, LF 2025) against wage rates to 38.5 % | income-type gap | **new**: Nothing found on the IRCM/salary gap or the 2025 SME rate (no PwC page for the country; OpenAlex: nothing). | 2026-11-20: OpenAlex specific queries 'Cameroon dividends IRCM 16.5% salary owner manager'; 'Cameroun revenus de capitaux mobiliers 10% PME loi de finances 2025' (22 hits, titles checked); OpenAlex broad 'Cameroon personal income tax', 'Cameroon income tax wages', 'Cameroon tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country. Record: world/loopholes/africa_mena/search/CM-F4.json |

<!-- L1-VERIFICATION END -->
