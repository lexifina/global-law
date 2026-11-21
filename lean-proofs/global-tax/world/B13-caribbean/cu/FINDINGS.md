# Cuba (CU) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The law that taxes wages in 2025 does not print the wage scale
- kind: statute-fault
- Ley 174 art. 67.1 'Aplicar en el año 2025, a los trabajadores de todos los sectores, el pago del Impuesto sobre los Ingresos Personales por las remuneraciones salariales', but neither Ley 174 nor the annotated Ley 113 contains a scale for salaries (art. 26 is the annual scale with 39,120 exempt; art. 65 of Ley 174 gives a 5-50 % scale for other 2024 declarants). Read literally, wages fall under art. 26 (15-50 % above 39,120) - the model's default, with a switch to zero.
- provisions: Ley 174 arts. 65, 67.1; Ley 113 arts. 19 g), 22, 26
- Lean: CuTax.person (cuWageTax)
- status: modelled as a documented reading

### F2 The special social-security contribution doubles from 5 % to 10 % above 15,000 CUP a month and has no ceiling
- kind: loophole-known
- Ley 174 art. 20.2; with the art. 26 top rate of 50 % (literal reading) the combined marginal rate above about 7,400 CUP a month is 55 % (scanner top rate 55.0 %).
- provisions: Ley 174 art. 20.2; Ley 113 art. 26
- Lean: CuTax.cessMonth
- status: modelled

### F3 Two annual scales for the same tax in the same year
- kind: statute-fault
- Ley 113 art. 26 (15/20/30/40/50 % at 10,000-step bands) and Ley 174 art. 65 (5-50 % at 25,000 ... 1,000,000) both set 'tipo impositivo' for the annual liquidation; Ley 174 confines art. 65 to listed categories, leaving art. 26 for the rest.
- provisions: Ley 113 art. 26; Ley 174 art. 65
- Lean: -
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | 5 % bonus for declaring and paying before 28 February | not modelled | Ley 113 art. 39; Ley 174 art. 68.1 |
| K2 | Non-residents: 15 % flat on gross (art. 27); work abroad contracts 4 % (art. 28) | not modelled | Ley 113 arts. 27-28 |
| K3 | Sale of home/vehicle and prizes: 4 % (8 % from the second sale) | not modelled | Ley 113 arts. 42, 45 |

## Step 5: what was searched

- kernel scanners with scale 180,000 (CESS threshold x 12)
- gacetaoficial.gob.cu search (Ley 113, presupuesto 2025); Ley 174 read in full for the personal income tax and contributions

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5S4-1 Inventario payroll-utils (kr4t3rdev): an 'example' scale and a flat 5 % contribution (W5 review pass 4, 2026-11-20)
- kind: software-error
- `cu_open_inventario_kr4t3rdev_grid`: the tool's own comment calls its scale an example ('ajustar segun Excel'; exempt to 3,260 CUP a month, 3 % / 5 %); the model taxes salaries under Ley 174 art. 67.1 with the Ley 113 art. 26 scale (reading, F1) and charges the contribution of Ley 174 art. 20.2 (5 % to 15,000 a month, 10 % above), the tool a flat 5 %. Dev: tool far below on tax (ratio ~0.1), equal on the contribution below 15,000 a month.
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | explained | Reading recorded. |
| F2 | fact | explained | Probe: no notch at 15,000 a month (the 10 % applies to the excess); fact. |
| F3 | statute-fault | explained | Two scales (builder). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/CU.json`): the bands flagged sit below the 55 % top (no lead); income-type +51 % = the F1 reading (only wages carry the art. 26 scale in the model).
