# India (IN) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 s. 16 (ia)'s 75,000 standard deduction points at the wrong clause for AY 2026-27
- kind: statute-fault
- Finance (No. 2) Act 2024 inserted the 75,000 proviso for 'income-tax … computed under clause (ii) of sub-section (1A) of section 115BAC'. The Finance Bill 2025 (cl. 24) limits clause (ii) to AY 2025-26 (omits 'or after') and adds clause (iii) for AY 2026-27 onward, without amending s. 16 (ia) (the Bill's list of clauses has no s. 16). Read literally the new-regime standard deduction for FY 2025-26 is 50,000: a salaried person on 12,75,000 pays 26,000 (25,000 + cess) instead of nil. Default model: 75,000 (Department practice); `--sd-literal` gives the literal reading. Status: lead, the enacted Finance Act 2025 text was not reached (it may have fixed the cross-reference).
- provisions: s. 16 (ia) proviso; s. 115BAC (1A) (ii)-(iii); Finance Bill 2025 cl. 24
- Lean: InTax.compute (--sd-literal)
- status: lead: confirm on Finance Act 2025 (Act 7 of 2025)

### F2 The 12-lakh rebate's marginal relief band costs 104 % per rupee
- kind: loophole-new
- s. 87A clause (b) caps the tax at the income above 12,00,000, and the 4 % cess is charged on that tax ('No marginal relief shall be available in respect of such cess', memo 2025). From 12,75,000 to about 13,45,588 of salary every extra rupee costs 1.04 rupees: earning 70,588 more leaves 2,823 less (13,45,588: tax 73,411, net 12,72,177, against 12,75,000 untaxed; measured on the exe). Scan: 76 grid steps with net-income falls.
- provisions: s. 87A first proviso (a)-(b); Finance Act cess paragraph
- Lean: InTax.rebateNew, results/search/b02scan.md
- status: measured; not found in the sources read (no search)

### F3 Surcharge marginal relief at 50 L / 1 Cr / 2 Cr (/ 5 Cr old regime)
- kind: loophole-known
- Implemented: tax + surcharge may not exceed the tax at the threshold plus the excess income; the relief band has METR 100 % before cess (104 % with it).
- provisions: Finance Act surcharge paragraphs
- Lean: InTax.surcharge
- status: modelled


### W5R-1 s. 288A / 288B rounding applied (W5 review pass 2, 2026-11-20)
- kind: model-fix
- Pointer (not the reason): 10 flagged W5 IN grids missed by 2-6 rupees on most cases; 7 of the 16 IN tools return every
  tax as a multiple of ten. The model had listed "s. 288A/288B rounding not applied".
- Text (Income-tax Act 1961; bare Act from courtbook.in, `law/w5/`, sha256 f76f2e1f… / 964be79e…; incometaxindia.gov.in
  refused automated fetches): s. 288A (as substituted by Act 19 of 1968, w.e.f. 1.4.1969) "The amount of total income
  computed in accordance with the foregoing provisions of this Act shall be rounded off to the nearest multiple of ten
  rupees ... if the last figure in that amount is five or more, the amount shall be increased to the next higher amount
  which is a multiple of ten and if the last figure is less than five, the amount shall be reduced to the next lower
  amount which is a multiple of ten; and the amount so rounded off shall be deemed to be the total income"; s. 288B (Act
  29 of 2006, w.e.f. 13.7.2006) "Any amount payable ... shall be rounded off to the nearest multiple of ten rupees" (same
  rule). Both in force for FY 2025-26 (the 2025 Act applies from 2026-04-01).
- Change: `round10`; total income rounded (288A) before slabs, rebate and surcharge; each person's payable (tax +
  surcharge + cess) rounded (288B), the difference booked on incomeTax. #guards (13,05,433 salary: total income
  12,30,430, payable 31,650). Largest change on 16,514 households: 14 rupees; every total now a multiple of ten.
- Local dev rerun (W5b frozen -> current, statute exact / covered): rounding tools rise (payroll_js_crmleaf 419 -> 944,
  payroll_core_crmleaf 462 -> 958, anivar 431 -> 943, easy_tax 432 -> 953, itr_agent 421 -> 1,009, itr_wala 474 -> 1,031,
  india_tax_engine_npm 299 -> 539 / 545); **regressions (reported):** the tools that do not round fall (aikar 532 -> 329,
  abhishek4411 578 -> 345, chennaiaps 472 -> 383, taxsimple 465 -> 355, toolwizhub 471 -> 353, drishit96 575 -> 346,
  indian_tax_calculator 444 -> 342, jantahr 703 -> 415, aamitsengar 684 -> 443): those tools omit ss. 288A/288B (minor
  software deviation, recorded in world/IMPROVE_W5.md); within 1 % unchanged. Rescanned (scan_world.py IN).
- provisions: Income-tax Act 1961 ss. 288A, 288B
- Lean: InTax.round10, personTI, personBest (#guard)
- status: model changed

### W5S-1 aikar (debjitl45): no surcharge (W5 review pass 2, 2026-11-20)
- kind: software-error
- `in_open_aikar_debjitl45_grid`: above 50 lakh the tool's tax is 1/1.10 of the model's; its code has no surcharge. The Finance Act 2025 First Schedule (Department's AY 2026-27 table: 10 % above 50 lakh, 15 % above 1 crore, 25 % above 2 crore, with marginal relief) applies. It also omits ss. 288A / 288B rounding.
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5S-2 Tax-Calculator-India (Abhishek4411): no surcharge, no s. 87A marginal relief (W5 review pass 2, 2026-11-20)
- kind: software-error
- `in_open_tax_calculator_india_abhishek4411_grid`: model above at 12.8-13.3 lakh (s. 87A first proviso cl. (b), Finance Bill 2025 cl. 20) and by 10 % above 50 lakh (surcharge).
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5S-3 KnowYourTaxes (chennaiAPS) and TaxSimple (GauravSamrat): no s. 87A marginal relief (W5 review pass 2, 2026-11-20)
- kind: software-error
- Both tax the whole slab amount just above 12 lakh total income (model / tool 0.02-0.6 there); chennaiAPS's code says 'Marginal relief applies (not implemented here for simplicity)'. s. 87A first proviso cl. (b).
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5S-4 toolwizhub (sorapallivenkatesh): no surcharge marginal relief (W5 review pass 2, 2026-11-20)
- kind: software-error
- Model below the tool just above 50 lakh (51-52 lakh) and 75-80 lakh: the tool charges the full surcharge where marginal relief limits tax + surcharge to the tax at the threshold plus the excess income.
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5S-5 wronglaw grids: bhandi, kernelctc, neontax, surajkumar12 (W5 review pass 2, 2026-11-20)
- kind: software-error
- bhandi (anuragkumar33): no 10 % band 8-12 lakh, no cess or surcharge; kernelctc (abhivaadyasharma): no 25 % band 20-24 lakh (+20,800 above 24 lakh); neontax: new-regime slabs with no s. 16 (ia) deduction and no s. 87A rebate; tax_calculator (surajkumar12): no s. 87A rebate, no cess, no surcharge. Each confirmed on its dev cases against s. 115BAC (1A) (iii), s. 16 (ia) and s. 87A (Finance Bill 2025 cls. 20, 24).
- status: recorded (world/IMPROVE_W5.md pass 2, wronglaw table)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | lead | 26,000 INR at 12,75,000 of salary if read literally. Finance Bill 2025 re-read: s. 115BAC cl. (ii) loses 'or after' and cl. (iii) is added, with no change to s. 16 (ia). The enacted Finance Act 2025 still not reached: stays a lead. Evidence: exe + Lean `L1IN.F1` (`world/loopholes/rest/lean/L1IN.lean`, 1 #guard): tot(b)-tot(a) = 26000; statute re-read: `law/finance_bill_2025.txt`. |
| F2 | loophole | confirmed | net income falls by 2,822 INR when salary rises from 12,75,000 to 13,45,588 (s. 87A marginal relief plus 4 % cess: 104 % band). exe and #guard L1IN.F2 (with ss. 288A/288B rounding). The slab table re-read; the 87A text itself was located only in the Bill's memorandum by the builder. Evidence: exe + Lean `L1IN.F2` (`world/loopholes/rest/lean/L1IN.lean`, 2 #guard): tot(a) = 0; net(b)-net(a) = -2822. Known/new: **known**: Business Today (3 Feb 2025) and Angel One work the 12-12.75 lakh band, including the 4 % cess on the relieved tax (Rs 25,000 + cess = Rs 26,000), which is the 104 % rate; web search 6. |
| F3 | loophole | confirmed | tax rises by 1,040 INR for 1,000 more income just above 50 lakh (104 % band). exe and #guard L1IN.F3. Evidence: exe + Lean `L1IN.F3` (`world/loopholes/rest/lean/L1IN.lean`, 1 #guard): tot(b)-tot(a) = 1040; statute re-read: `law/memo_2025.txt`. Known/new: **known**: tax2win.in 'Income tax surcharge and marginal relief' (found by web search 6) describes surcharge marginal relief; standard in Indian practice. |
| W5R-1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-2 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-3 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-4 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-5 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/IN.json`): METR 104 % at 12.84 lakh and 50.76 lakh and the bands above the 39 % top (with dividends or two earners they move) = F2 (s. 87A marginal relief) and F3 (surcharge marginal relief); timing 111,980 = F2/F3.
