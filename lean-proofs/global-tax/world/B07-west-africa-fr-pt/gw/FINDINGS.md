# Guinea-Bissau (GW) findings, B07-west-africa-fr-pt (rescue pass 3, 2026-11-20T14:21Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 The 14 % row's 'parcela a abater' is off by 16.020 FCFA a month: one franc more pay cuts the tax by 16.020
- kind: gov-error
- CIP art. 27(1) as written by Lei 1/2021 art. 10 prints for 400.501-750.000 a month 14 % with a parcela of 37.947. A table that matches its own marginal rates (art. 27(3): 'representam taxas marginais'; art. 28) needs 13.917 + (14 - 12) % x 400.500 = 21.927; 37.947 is 13.917 + 6 % x 400.500, the step to the 18 % of the struck 2020 table. Tax at 400.500 a month is 34.143, at 400.501 it is 18.123 (#guard; theorem printed_table_falls). Everyone paid more than 400.500 a month pays 16.020 a month (192.240 a year) less than the marginal reading, and the next rows (52.947, 74.947, 104.947) carry the error up. The annual column repeats it (455.364 = 12 x 37.947).
- provisions: CIP art. 27(1), (3), art. 28; Lei 1/2021 art. 10
- Lean: GwTax.ipRows, ipMarginal; #guard subAgrees ... [400501] = false; theorem printed_table_falls
- status: model result (printed table modelled; marginal reading in detail.ipMarginalReadingWages)

### F2 Art. 27(3) contradicts itself above 400.500 a month
- kind: statute-fault
- The first sentence says column B holds marginal rates valid within each band; the second says column C is subtracted from the rate applied to the whole income. Both give the same tax up to 400.500 a month and differ by 16.020 a month above it. Art. 18 tells employers to apply 'as taxas previstas no artigo 27º': it does not say which reading.
- provisions: CIP arts. 18, 27(3), 28
- Lean: GwTax.ipMonth vs ipMarginalMonth
- status: model result

### F3 A pension one franc a month above 200.000 is taxed in full
- kind: loophole-new (literature not searched)
- Art. 2(c) keeps pensions 'de valor igual ou inferior a 200.000 Fcfa mensais' outside income; above it nothing limits the tax to the excess. Read with art. 27(1), 200.000 a month pays 0 and 200.001 pays 8 % x 200.001 - 3.750 = 12.250 a month (147.000 a year; #guard pensionTax 2400012).
- provisions: CIP arts. 2(c), 27(1)
- Lean: GwTax.pensionTax
- status: model result

### F4 The annual column's top parcela is one franc short and its bands leave gaps
- kind: gov-error
- Every annual parcela is 12 times the monthly one except the top row (1.259.363 vs 12 x 104.947 = 1.259.364), and the annual bands run 'De 0 até 500.004' then 'De 500.016', leaving 500.005-500.015 (and similar 11-franc gaps at each edge) in no row.
- provisions: CIP art. 27(1) annual columns
- Lean: #guard on ipAnnualParcelas
- status: model result

### F5 No exempt band: 1 % from the first franc
- kind: fact
- The employees' table starts at 0 with 1 %; there is no personal or family allowance anywhere in the code. A monthly wage of 41.667 pays 416.
- provisions: CIP art. 27(1)
- Lean: #guard ipMonth 41667 = 416
- status: model result

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/GwTax/Verify.lean` (imported by the `GwTax` library and built; each guard evaluates `GwTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/GW.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | The printed 14 % row's parcela (37,947 instead of 21,927) makes the tax fall by 16,020 a month when pay passes 400,500: everyone above pays 192,240 a year less than the table's own marginal rates. G: f1_printed_table_fall (incomeTax -192,240 from 4,806,000 to 4,806,012); T: GwTax.printed_table_falls. S: law/rescue3/cip_section_extracted.md:392 ('De 400.501 a 750.000 / ... / 14% / 37.947 / 455.364') and :378 (the struck 2020 row). |
| F2 | explained | Art. 27(3) self-contradiction: the statute fault behind F1. |
| F3 | confirmed | Pension cliff: pensions 'de valor igual ou inferior a 200.000 Fcfa mensais' are outside income; one franc a month more taxes the whole pension: 146,988 of net a year. G: f3_pension_cliff. S: law/rescue3/cip_section_extracted.md:156 (art. 2(c)). |
| F4 | explained | Annual column off by one and 11-franc gaps: gov record. |
| F5 | explained | No exempt band: design. |
| Leads | explained | Rescan timing gain 192,252 (two earners at 2.92 'AW') and 411 edge dips = F1's falling table. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: The 2021 table's 14 % row subtracts 37,947 instead of 21,927: tax falls 16,020 a month at 400,501 | rule set outside the law | **new**: Nothing found (no PwC page for the country; OpenAlex: nothing); one web search (see record) found the DGCI's 2021 filing instructions and IMF reports but no account of the table or its error. | 2026-11-20: OpenAlex specific queries 'Guiné-Bissau imposto profissional tabela taxas 2021 parcela a abater'; 'Guinea-Bissau employment income tax table 2021' (1474 hits, titles checked); OpenAlex broad 'Guinea-Bissau personal income tax', 'Guinea-Bissau income tax wages', 'Guinea-Bissau tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Guinea-Bissau tax policy' (8858 records, titles only); web search: WebSearch 2026-11-20 'Guinea-Bissau imposto profissional tabela 2021 parcela a abater erro': kontaktu.mef.gw DGCI instructions (3 Dec 2021), EY Guia Fiscal 2022/2025, IMF country reports; nothing on the table's parcela. Record: world/loopholes/africa_mena/search/GW-F1.json |
| F3: Pensions up to 200,000 F a month are outside income; above, the whole pension is taxed | cliff or notch | **new**: Nothing found (no PwC page for the country; OpenAlex: nothing). | 2026-11-20: OpenAlex specific queries 'Guiné-Bissau imposto profissional pensões 200.000 isenção' (1 hits, titles checked); OpenAlex broad 'Guinea-Bissau personal income tax', 'Guinea-Bissau income tax wages', 'Guinea-Bissau tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country. Record: world/loopholes/africa_mena/search/GW-F3.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **GW-R1** Imposto profissional on wages and the annual tax on self-employment (art. 13 / 27(2) annual column) are separate. Money: 86,400 XOF a year on 7,200,000 (2 AW) vs all wages. Lean: `world/loopholes/round2/v/lean/R2GW.lean` (R2GW.R1 (4 #guard)); exe check `round2/v/out/GW.json`. Provision: Código do Imposto Profissional arts. 13, 27 (model citation). Status: model-proved. Known/new: new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point (`round2/v/novelty/`).
<!-- R2-SCANNERS:END -->
