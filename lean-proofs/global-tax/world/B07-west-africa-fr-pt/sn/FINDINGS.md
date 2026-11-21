# SN findings (Senegal (impôt sur le revenu, TRIMF; family reduction by parts), 2025)
Batch B07-west-africa-fr-pt, built 2026-11-20 03:57 UTC. Status: built, access A (no referee values used). Scanner output: `results/search/SUMMARY.md` (scale 3,000,000 XOF: gross annual wage at which the 30 % wage deduction reaches its 900 000 F cap (900 000 / 30 %); a statutory threshold, not an average wage).
Scanner leads: single|none: max 45.0 %, average 45.0 % (top 40.0 %) from 594,000 to 600,000 (0.198-0.2 AW); causes: taxableIncome, trimf; single|none: max 133.3 %, average 133.3 % (top 40.0 %) from 1,998,000 to 2,004,000 (0.666-0.668 AW); causes: trimf, taxableIncome, irBareme; single|none: max 135.0 %, average 135.0 % (top 40.0 %) from 6,996,000 to 7,002,000 (2.332-2.334 AW); causes: irBareme; single|none: max 337.0 %, average 337.0 % (top 40.0 %) from 11,994,000 to 12,000,000 (3.998-4.0 AW); causes: trimf, taxableIncome, irBareme

### F1 TRIMF steps make net pay fall (art. 282)
- kind: loophole-new (structure; statute-visible notch)
- status: proved

The TRIMF is a flat amount by gross-income band (900 / 3 600 / 4 800 / 12 000 / 18 000 / 36 000 F). One franc of gross pay at 600 000 F costs 2 700 F; at 12 000 000 F it costs 18 000 F (Lean `SnTax.trimf_notch_600k`, `trimf_notch_12m`). The scanner (scale 3 000 000 F) finds the largest net-income fall of 18 369 F at 11 999 999 F for a single person and 36 276 F for a one-earner couple, because art. 276 makes the earner pay the TRIMF for a spouse without income too. Taxpayers just above a band limit lose net pay; a salary agreed just below a limit is worth more.

### F2 A spouse's first franc of income costs the household (art. 174 3.)
- kind: loophole-new (structure)
- status: scanner + statute

A married sole earner gets an extra half-part 'dans la mesure où un seul conjoint dispose de revenus imposables' and pays the TRIMF for the spouse (art. 276). When the spouse earns any taxable income both disappear: the scanner's second-earner family loses 42 899 F at the first franc (METR 715 %). The cliff is the size of one half-part's reduction plus one TRIMF.

### F3 The family 'parts' are a reduction table, not a quotient (registry correction)
- kind: statute-fault (registry description) / reading
- status: reading

Art. 174 1. applies to the tax of the barème a reduction = rate × tax, bounded by a minimum and a maximum per number of parts (1,5 parts: 10 %, 100 000 to 300 000 F ... 5 parts: 45 %, 800 000 to 3 180 000 F). The minimum wipes out small taxes (`red15_wipes`: 1,5 parts pay nothing up to a tax of 100 000 F); the maximum caps the relief for high incomes. The registry's 'family-quotient (reuse FR)' is corrected: there is no income splitting, and spouses are taxed separately (art. 59).

### F4 The 43 % cap of art. 174 1. never binds
- kind: observation (dead letter)
- status: proved

'le montant de l'impôt ne peut excéder 43 % du revenu imposable': with a top marginal rate of 43 % and a zero band, the average rate is always below 43 % (`cap_not_binding` at 100 M F). The sentence has no effect on any household.

### F5 Reading: married sole earner without children has 2 parts
- kind: reading
- status: open

The table gives 'Marié sans enfant à charge 1,5' and 174 3. adds a half-part when only one spouse has income; the model adds them (2 parts). An official worked example or the software phase (OpenFisca-Senegal) should settle it; under the other reading the sole earner has 1,5 parts.

### F6 Model limits
- kind: model limitation
- status: open

IPRES/IPM employee contributions (no accessible rate text: ipres.sn, secusociale.sn unreachable); self-employment regimes (CGU, réel simplifié), capital gains; children 18-24 in education (each listed in the exe's `unsupported`).

## Step 4: known ways of paying less tax that the statute makes visible (catalogue)

| # | item (provision) | in the model | recreated by model/scanner |
|---|---|---|---|
| L1 | Choosing the contribution globale foncière (1/12 of rents) instead of the IR on rents (arts. 74-78) | modelled (election snRental); recreated by the elections harness | yes |
| L2 | Final withholding on dividends (10 %) and bank interest (8 %) instead of the 43 % barème (arts. 173 2., 203, 209): an owner-manager pays himself dividends | modelled; recreated by the income-type scanner | yes |
| L3 | Expense allowances exempt (art. 167 3.-4., arrêté 11719/2009 list) and benefits in kind valued at the arrêté 12914/2013 flat amounts (art. 166) | not modelled (no input) | no |
| L4 | Health-insurance contributions exempt up to 10 % of gross pay (art. 167 15.) and voluntary retirement savings deductible up to 10 % of pay (art. 55 3.) | art. 55 3. modelled; art. 167 15. not modelled | yes |
| L5 | Spreading exceptional or arrears income back over earlier years (art. 171) | not modelled (one-year model) | no |
| L6 | Keeping gross pay just below a TRIMF band limit (art. 282) | recreated (scanner notches, F1) | yes |
| L7 | Spouse with no income: extra half-part and the earner's TRIMF for the spouse (arts. 174 3., 276) | recreated (second-earner cliff, F2) | yes |
| L8 | Pensions: 40 % deduction with a 1,8 M F floor (art. 164) and the 80 % decote for foreign-source pensions (art. 180) | 40 % modelled; art. 180 not modelled | yes |
| L9 | Capital gains on securities held through approved collective funds exempt (art. 167 14.) | not modelled | no |

Catalogued 9, recreated 6, not modelled 3.

## Step 5: what was searched

Literature NOT checked (no web-search budget this session): IMF Article IV / TADAT reports, the OECD 'Revenue Statistics in Africa' country notes, ATAF/FERDI and ICTD working papers on West African PIT, UEMOA directive commentaries, the West African tax-planning guides of the Big Four, and any official guidance (instructions, notes de service) beyond the texts cited. Searched instead: the statute text listed under Sources (every article on wages, pensions, family relief, investment income and rents), the kernel's generic scanners (results/search/), and the proved Lean statements in lean/*Tax/Theorems.lean. Novelty is never claimed: 'not found in the 0 external sources searched'.

Registry correction: SN: unit is the individual with a family reduction by parts (not a family quotient); main statute confirmed (Loi 2012-31, DGID edition Jan. 2025 incl. LF 2025).

## Round W2 (improvement agent, 2026-11-20): W1 software-grid dev failures settled from the statute

### W2-1 OpenFisca-Senegal agrees once the family is entered (case-building error; the parts question is closed)
- kind: test-note
- The package's family variables (`nombre_enfants`, `statut_marital`, `conjoint_a_des_revenus`) are plain inputs the
  grid never set, so it computed every adult as single without children (1 part, reduction 0). Its art. 174 formula and
  parts follow the same reading as the model (1.5 married, + 0.5 per child to each parent with income, + 0.5 when one
  spouse alone has income). With the inputs set: case 0905 245,300 and case 0544 1,640,500, both equal to the model.
- provisions: CGI art. 174 1.-4.
- Lean: SnTax.halfParts, SnTax.reduction (unchanged)
- status: reported to the test agent (software/ISSUES.md, W2)

### W5S-1 payroll_africa (Senegal): IR base after actual contributions instead of the 30 % abatement (W5 review pass 2, 2026-11-20)
- kind: software-error
- `sn_open_payroll_africa_grid`: the app's IR base is gross - IPRES - CSS (calculators/senegal.py); CGI art. 168 b) gives 'un abattement forfaitaire de 30 % représentatif des cotisations versées à titre obligatoire ... 900 000 francs' instead. Its tax is above the model's by up to ~244,000 a year.
- status: recorded (world/IMPROVE_W5.md pass 2)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/SnTax/Verify.lean` (imported by the `SnTax` library and built; each guard evaluates `SnTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/SN.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | TRIMF by gross-income band: one franc at 600,000 costs 2,699; at 12,000,000 18,369 (single) and 36,313 for a one-earner couple (the earner pays the spouse's TRIMF, art. 276). G: f1_trimf_600k, f1_trimf_12m, f1_trimf_12m_couple; T: SnTax.trimf_notch_600k, trimf_notch_12m. S: src/CGI-2025.txt:6862-6868 (art. 282 table: '600 000 999 999 3 600' ... '12 000 000 et plus 36 000'). |
| F2 | confirmed | Second-earner trap: the half-part 'dans la mesure où un seul conjoint dispose de revenus imposables' and the spouse's TRIMF both end at her first franc: 185,549 of household net at a 12 M earner, 42,899 at 3 M with two children. G: f2_spouse_first_franc, f2_spouse_first_franc_3m_2kids. S: src/CGI-2025.txt:4526 (art. 174 3.). |
| F3 | explained | Reduction table, not a quotient: registry correction. |
| F4 | explained | Dead 43 % cap (T: cap_not_binding). |
| F5 | explained | Settled by W2-1 (OpenFisca-Senegal follows the same 2-part reading). |
| F6 | explained | Model limits. |
| W2-1, W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: 10 notches, all TRIMF edges (F1) or the second earner (F2); timing gain 198,145 (one-earner couple at 2.33 +- 1.0 'AW') = F1 edges plus the reduction table's minimum/maximum. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: TRIMF steps by gross-income band; the earner pays the spouse's TRIMF too | cliff or notch | **new**: PwC Senegal: no mention of the TRIMF; OpenAlex: a 2026 incidence study of Senegalese taxes (abstract silent on the TRIMF steps). | 2026-11-20: OpenAlex specific queries 'Sénégal TRIMF taxe représentative de l'impôt du minimum fiscal'; 'Senegal minimum fiscal tax TRIMF wage brackets' (3 hits, titles checked); OpenAlex broad 'Senegal personal income tax', 'Senegal income tax wages', 'Senegal tax system reform' (75 records, titles and abstracts grepped, 3 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (senegal, 5 individual pages): 0 passages with the item's terms; Crossref IMF prefix 10.5089 'Senegal tax policy personal income tax' (9149 records, titles only). Record: world/loopholes/africa_mena/search/SN-F1.json |
| F2: Half-part for a sole-earning spouse and the spouse's TRIMF end at her first franc | second-earner trap | **new**: PwC Senegal: nothing on the half-part or the spouse's TRIMF; OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'Sénégal impôt sur le revenu réduction pour charges de famille demi-part conjoint sans revenu'; 'Senegal family tax reduction parts spouse without income' (731 hits, titles checked); OpenAlex broad 'Senegal personal income tax', 'Senegal income tax wages', 'Senegal tax system reform' (75 records, titles and abstracts grepped, 3 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (senegal, 5 individual pages): 2 passages with the item's terms. Record: world/loopholes/africa_mena/search/SN-F2.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 30.0 % (CGI art. 36: 'Le taux de l'impôt sur les sociétés est fixé à 30 % du bénéfice imposable' (src/CGI-2025.txt:1872)); at a profit of 3 AW the best split costs 26.4 % of the profit, all salary 26.4 %, all dividends 37.0 % (employer contributions: not included); dividends beat salary once employer contributions exceed 20 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
- mix.py (wage vs fee split): lead: small.
<!-- R2-SCANNERS:END -->
