# Togo (TG) findings, B07-west-africa-fr-pt (rescue pass 2, 2026-11-20T13:10Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 A spouse's first franc of income ends the 'conjoint sans ressource' dependant
- kind: loophole-new (literature not searched)
- Art. 72 counts 'le (ou les) conjoint(s) ne disposant pas de ressource' as a dependant (10,000 FCFA a month, art. 73). Any income of the spouse ends it: 120,000 FCFA of base, worth 3,600-42,000 FCFA of tax by the earner's band. The second-earner scanner finds a 17,999 FCFA notch at the first franc (earner at the scale wage, 15 % band).
- provisions: CGI 2025 arts. 6, 72, 73
- Lean: TgTax.household (noResource)
- status: model result

### F2 A pension one franc above 3,600,000 doubles its taxable part
- kind: statute-fault
- Art. 27 retains 25 % of a pension between 2.4 M and 3.6 M and 50 % above 3.6 M, on the whole pension, not the excess: 3,600,000 gives a base of 900,000 (exempt band), 3,600,001 gives 1,800,000 and 27,000 FCFA of tax (#guard). Pensions above 2.4 M are otherwise exempt up to 2.4 M (art. 23-3), so the cliff at 2,400,000 is invisible (600,000 base is inside the exempt band).
- provisions: CGI 2025 arts. 23-3, 27, 74, 76
- Lean: TgTax.pensionTax; #guard pensionTax 3600001 = 27000
- status: model result

### F3 The 28 % flat deduction stops at 10 M: the marginal rate jumps by a third above it
- kind: fact
- Art. 26 gives 28 % 'sur la fraction du revenu n'excédant pas dix millions'. Below 10 M gross a band rate t costs 0.72 t per franc; above, t. At 10 M the base is 7.2 M (20 % band): the marginal rate goes from 14.4 % to 20 % at the cap.
- provisions: CGI 2025 art. 26
- Lean: TgTax.abattement
- status: model result

### F4 Art. 74 ends with a stray 'Abrogé.' and its footnote cites the LF 2023
- kind: gov-error
- The consolidated art. 74 prints the 2024 barème ('Nouveau Barème', the PLF 2024 wording) followed by a paragraph reading only 'Abrogé.', and its footnote names the LF 2023 (Loi n° 2022-022) as the source. The reader cannot tell from the code which law set the table in force or what was repealed.
- provisions: CGI 2025 art. 74 and footnote 6; PLF 2024 art. 16
- Lean: TgTax.bareme (doc comment)
- status: model result

### F5 Each income category gets its own pass through the barème
- kind: fact
- Arts. 74-77 apply the barème to employment income, managers' pay, pensions and rents 'également'; the family reduction is 'exclusivement en matière de revenus d'emplois'. Read literally (as modelled), a retiree with a pension and a salary gets two 900,000 exempt bands. The opposite reading (one global base) is not excluded by the text.
- provisions: CGI 2025 arts. 13, 72, 74-77
- Lean: TgTax.household
- status: model result


### W5S-1 payroll_africa (Togo): no 28 % forfait (W5 review pass 2, 2026-11-20)
- kind: software-error
- `tg_open_payroll_africa_grid`: calculators/togo.py taxes gross - CNSS - INAM; CGI art. 26 then deducts 'une déduction calculée forfaitairement ... fixée à 28 % sur la fraction du revenu n'excédant pas dix millions (10 000 000) de francs CFA' (TgTax). The app's tax is far above the model's at middle wages.
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: CNSS page "Cotisations sociales" (official secondary; rate decree under Code 2011 art. 13 not reached); Décret 2023-096/PR arts. 12, 29
- CNSS 4 % and AMU 5 % of gross remuneration, both deducted under CGI art. 26 (1)-(2) before the 28 % forfait. Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

### W5S4-1 syscohada-fiscal 3.0.0 (hypnozbizo), Togo: the barème on gross pay (W5 review pass 4, 2026-11-20)
- kind: software-error
- `tg_open_syscohada_fiscal_hypnozbizo_grid`: CGI art. 74 barème applied to the gross wage; CGI art. 26 deducts the CNSS and AMU contributions and 'une déduction calculée forfaitairement ... fixée à 28 %' first (as W5S-1 for payroll_africa). Dev: tool above in 1,027 of 1,056 cases (2,261,162: 40,835 vs 17,430).
- status: recorded (world/IMPROVE_W5.md pass 4)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/TgTax/Verify.lean` (imported by the `TgTax` library and built; each guard evaluates `TgTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/TG.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Second-earner trap: 'le (ou les) conjoint(s) ne disposant pas de ressource' is a dependant; her first franc costs 17,999 of net at a 10 M earner. G: f1_spouse_dependant. S: law/rescue2/otr_cgi_lpf_2025.txt:1563 (art. 72). |
| F2 | confirmed | Pension cliff: 50 % of the whole pension is taxable above 3,600,000: one franc more costs 26,999. G: f2_pension_cliff; T: #guard pensionTax 3600001 = 27000. S: law/rescue2/otr_cgi_lpf_2025.txt:912-913 (art. 27: '25% ... entre 2 400 000 et 3 600 000', '50% lorsque le montant annuel excède trois millions six cent mille'). |
| F3 | explained | 28 % forfait capped at 10 M (art. 26): marginal rate rises at the cap; design. |
| F4 | explained | Stray 'Abrogé.' and LF 2023 footnote: gov record. |
| F5 | lead | Separate barème passes per category (arts. 74-77): reading. |
| W5S-1, W5A-1, W5S4-1 | explained (record of model/test work, not a loophole; kept as written) | CNSS 4 % + AMU 5 % present (900,000 at 10 M). |
| Leads | explained | Rescan notch = F1; bands above the top rate (42.2 % max, 40.8 % average) are rounding above the cap. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: 'Conjoint ne disposant pas de ressource' as a dependant: lost at her first franc | second-earner trap | **new**: Nothing found (no PwC page for the country; OpenAlex: nothing). | 2026-11-20: OpenAlex specific queries 'Togo IRPP charges de famille conjoint sans ressource'; 'Togo personal income tax dependent spouse deduction' (74 hits, titles checked); OpenAlex broad 'Togo personal income tax', 'Togo income tax wages', 'Togo tax system reform' (75 records, titles and abstracts grepped, 3 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Togo tax policy' (8293 records, titles only). Record: world/loopholes/africa_mena/search/TG-F1.json |
| F2: 50 % of the whole pension taxable above 3.6 M | cliff or notch | **new**: Nothing found (no PwC page for the country; OpenAlex: nothing on pensions). | 2026-11-20: OpenAlex specific queries 'Togo impôt sur le revenu pensions abattement 3 600 000'; 'Togo pension income tax threshold' (887 hits, titles checked); OpenAlex broad 'Togo personal income tax', 'Togo income tax wages', 'Togo tax system reform' (75 records, titles and abstracts grepped, 3 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country. Record: world/loopholes/africa_mena/search/TG-F2.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **TG-R1** Wages on the art. 74 barème, business income at a flat 30 % (art. 78): wages up to where the barème passes 30 %, the rest as business income. Money: 2,023,000 XOF a year less on 40,000,000 (4 AW) than all wages; 2,000,000 less than all business income (5 %). Lean: `world/loopholes/round2/v/lean/R2TG.lean` (R2TG.R1 (4 #guard)); exe check `round2/v/out/TG.json`. Provision: CGI 2025 art. 74, art. 78 'l'impôt est déterminé par application du taux de 30%' (law/rescue2/otr_cgi_lpf_2025.txt:1650-1657). Status: confirmed. Known/new: new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point; web search 2 found no source on the two schedules (`round2/v/novelty/`).
- **Owner-manager (company_world.py)**: corporate rate 27.0 % (CGI: 'Le taux de l'impôt sur les sociétés est fixé à 27 % du bénéfice imposable' (law/rescue2/otr_cgi_lpf_2025.txt:2776)); at a profit of 3 AW the best split costs 32.1 % of the profit, all salary 35.3 %, all dividends 36.5 % (employer contributions: statute rate 17.50 %); dividends beat salary once employer contributions exceed 21 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
