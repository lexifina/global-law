# Palestine (PS) findings, B06-mena (rescue pass, 2026-11-20T11:39Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 Since 2014 the law no longer lets the cabinet change the brackets, but still lets it change the exemptions
- kind: fact
- Decree-Law 4/2014 replaced art. 16(5) (the cabinet's power to amend the brackets and rates) with the 10 % dividend tax; art. 12(2) (the cabinet's power to amend the exemptions) was left in place. Brackets now need a decree-law; the 36,000-shekel exemption can move by cabinet decision, which the gazette catalogue would list (none found with 'ضريبة الدخل' in its title).
- provisions: Decree-Law 8/2011 arts. 12(2), 16(5) as amended by Decree-Law 4/2014
- Lean: PsTax.sched, PsTax.exemption
- status: model result

### F2 Bank interest lost its final 5 % tax in 2014 with nothing stated in its place
- kind: statute-fault
- Decree-Law 4/2014 art. 4 repealed art. 31(8) (5 % final withholding on deposit interest) without adding interest to the exemptions of art. 7 or giving another rate; read literally, interest is ordinary income at 5-15 %. The model leaves interest unsupported.
- provisions: Decree-Law 8/2011 art. 31(8); Decree-Law 4/2014 art. 4
- Lean: -
- status: model result

### F3 Dividends at 10 % while wage income starts at 5 %
- kind: fact
- A shareholder-employee choosing between salary and dividends faces 10 % on dividends (at source, art. 16(5)) against 0 % on the first 36,000 and 5 % to 111,000 of salary; the company itself pays 15 % (art. 16(2)), so salary is cheaper up to the 15 % band.
- provisions: arts. 12(1)(a), 16(1), 16(2), 16(5)
- Lean: PsTax.out
- status: model result


### W5S4-1 Tax_calculater notebook (Ibrahim-harb): no 36,000 exemption and 20 % / 30 % bands (W5 review pass 4, 2026-11-20)
- kind: software-error
- `ps_open_tax_calculater_ibrahimharb_grid`: tax from the first shekel and bands of 20 % (250,000-500,000) and 30 % (above); Decree-Law 8/2011 art. 12(1)(a) and art. 16(1) as replaced by Decree-Law 5/2015 give an annual exemption of 36,000 and 5 / 10 / 15 % (15 % above 150,000). Dev: every case below the tool by 5 / 10 / 15 % x 36,000 plus 5 % / 15 % of the excess over 250,000 / 500,000 (at 490,817: 5,400 + 12,041 = 17,441).
- status: recorded (world/IMPROVE_W5.md pass 4)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Cabinet power over exemptions but not brackets (Decree-Law 4/2014): legal record. |
| F2 | lead | Interest after the 2014 repeal of the 5 % final rate: unsupported in the model; reading only. |
| F3 | explained | Personal side only: 100,000 of salary replaced by dividends saves 150 of net at 200,000 (10 % at source vs 5-15 %); the company's 15 % is not modelled, so the claim 'salary cheaper up to the 15 % band' is not proved here. |
| W5S4-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: no notch, no band above the top rate; split gain 16,651 = separate taxation of spouses. |

<!-- L1-VERIFICATION END -->
