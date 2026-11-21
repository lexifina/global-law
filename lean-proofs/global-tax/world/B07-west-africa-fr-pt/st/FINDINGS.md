# Sao Tome and Principe (ST) findings, B07-west-africa-fr-pt (rescue pass 3, 2026-11-20T14:21Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 The 2024 top band starts with a 122-dobra jump
- kind: gov-error
- OGE 2024 art. 8(11) adds a 30 % band from Dbs. 420.000 with a parcela of 45.048. Continuity with the 25 % row (parcela 24.170 after the redenomination) needs 24.170 + 5 % x 420.000 = 45.170: at 420.000 the tax is 80.952 instead of 80.830, so the first dobra of the band costs 122 dobras (#guard; theorem band2024_jump). 45.048 is what a 25 % parcela of 24.048 would give.
- provisions: CIRS art. 66 (DL 16/2016); OGE 2024 art. 8(11)
- Lean: StTax.rows2024; #guard ... = 122
- status: model result

### F2 From 2009 to 2016 every band edge was a tax cliff; the 2016 fix cost so much that family deductions were suspended
- kind: fact
- Lei 11/2009's art. 66 printed parcelas (881.250; 1.380.000; 1.875.000; 5.625.000; 9.000.000 old dobras) far below the band sums, so one dobra above 11.700.000 raised the tax from 0 to 288.750 (#guard). DL 16/2016 rewrote them to the exact band sums, its preamble saying no taxpayer just above an edge may keep less than one at it. DL 10/2019's preamble says that correction 'resultou numa perda de receitas bastante significativa' and, on IMF advice, suspended the personal and family deductions of art. 74 with no end date.
- provisions: CIRS art. 66 (Lei 11/2009; DL 16/2016), art. 74; DL 10/2019 arts. 1-2
- Lean: StTax.rows2009old, rows2016; #guard subAgrees rows2016 bands2016
- status: model result

### F3 Budget-law tax changes that expire with the next budget law
- kind: statute-fault
- OGE 2024 art. 8(14): 'Todas as alterações constantes na presente Lei manter-se-ão em vigor até a aprovação e publicação da Lei do OGE do ano seguinte'. The 30 % band and the IERS (both first adopted in the OGE 2023) therefore lapse unless each budget re-enacts them; the OGE 2025 bill re-enacts the IERS ('São mantidas', art. 8(18)) but not the band, and takes effect retroactively from 1 January 2025 (art. 22). Whether the band applied between 1 January 2025 and the 2025 law's publication depends on two provisions that point in opposite directions.
- provisions: OGE 2024 art. 8(11), (12), (14); OGE 2025 bill art. 8(18), 22
- Lean: StTax.table2025 (= rows2016); detail.irsWith2024Band
- status: model result

### F4 The IERS taxes 'rendimento disponível', which no law defines
- kind: statute-fault
- The IERS 'incide sobre parte do rendimento disponível que exceder Dbs. 50.000,00 mensal' at 20 %. Neither the budget laws nor the CIRS define disposable income (after IRS? after INSS? all categories?). Read as englobed income less IRS, a single earner pays it from about 64.000 dobras a month of pay; the combined marginal rate there is 25 % + 20 % x 75 % = 40 %.
- provisions: OGE 2024 art. 8(12); OGE 2025 bill art. 8(18)
- Lean: StTax.iers
- status: model result

### F5 A pension one dobra above 24.000 a year is half taxed
- kind: fact
- Art. 6(1)(b) exempts pensions 'de quantitativo anual inferior ou igual a Dbs. 24.000.000,00' (24.000 new dobras); above, art. 44(d) englobes 50 % of the whole pension. At 24.001 the englobed amount jumps to 12.001, still inside the 11.700 zero band plus 30 dobras of tax: a small cliff that grows only once other income fills the zero band.
- provisions: CIRS arts. 6(1)(b), 44(d)
- Lean: StTax.pensionPart
- status: model result


### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (statute)
- provisions: Regulamentação da Protecção Social Obrigatória, Decreto-Lei n.º 19/2022 (DR n.º 53, 15/07/2022) as amended by DL 25/2022, INSS consolidated text, art. 101.º 3 (worker 4 %, employer 6 %), art. 102.º (base)
- INSS worker 4 % of gross remuneration (no ceiling), deducted under CIRS art. 44(a). Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: INSS minimum contributory wage (REPSO art. 102.º 6-7) not applied. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | The 2024 30 % band's parcela gives a 122-dobra jump at 420,000 (T: band2024_jump); the 2025 table (= 2016 rows) has no such band, so no 2025 household is affected: a statute fault of 2024, not a 2025 loophole. |
| F2 | explained | Historic (2009-2016) cliffs and the 2019 suspension of family deductions: record. |
| F3 | explained | Budget-law changes lapse yearly: statute fault. |
| F4 | lead | IERS on undefined 'rendimento disponível': reading. |
| F5 | explained | Pension cliff at 24,000 a year: 30 dobras of tax at the edge; small. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) | INSS 4 % present. |
| Leads | explained | Rescan: no notch; split gain 47,234 = individual taxation. |

<!-- L1-VERIFICATION END -->
