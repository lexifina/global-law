# Equatorial Guinea (GQ) findings, B08-central-africa-fr (rescue pass 3, 2026-11-20T14:21Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 The 2024 code raises the tax on most wages unless the worker files the optional global return
- kind: fact
- Ley 4/2004 art. 252(2) applied the baremo after a 20 % deduction for professional expenses. Ley 1/2024 keeps that 20 % (capped at the annual SMI) only in the optional Declaración Global de Rentas Anuales (art. 29(5)); the ISS withheld by employers (arts. 129-130) has no such deduction, while the exempt band rises from 1.0 M to 1.4 M and the top rate falls from 35 % to 25 %. Reading the 2004 deduction as a 20 % cut of the base: 3.6 M FCFA paid 188.000 then and 220.000 now; 5 M 350.000 vs 360.000; from about 12.5 M the new law is cheaper (20 M: 3.050.000 vs 2.985.000).
- provisions: Ley 4/2004 art. 252; Ley 1/2024 arts. 29, 129, 130
- Lean: GqTax.tax2004, issTax; #guard comparisons
- status: model result

### F2 The non-resident 15 % rule cross-refers to a residence test
- kind: gov-error
- Art. 130(3) applies a 15 % final withholding on gross income 'para los casos previstos en el punto 1) inciso b) y punto 2) inciso b) del artículo 126'. Art. 126(1)(b) is the non-resident case, but art. 126(2)(b) defines residents ('centro de intereses vitales en Guinea Ecuatorial'). Read literally, residents by vital interests fall under the non-residents' 15 % instead of the baremo.
- provisions: Ley 1/2024 arts. 126, 130(3)
- Lean: not modelled (residents assumed)
- status: model result

### F3 Art. 130 has no paragraph 2) and art. 103 points to the wrong article for residence
- kind: gov-error
- Art. 130 goes from 1) (the baremo) to 3) (non-residents). Art. 103(1)(b) defines the IRCM beneficiary as a 'persona física residente en Guinea Ecuatorial en el sentido del artículo 129', but art. 129 lists the ISS deductions; residence is art. 126(2).
- provisions: Ley 1/2024 arts. 103, 126, 129, 130
- Lean: -
- status: model result

### F4 Employers report children, but the wage tax has no child relief
- kind: fact
- Art. 132(2)(e) makes employers report 'el número de hijos declarados ... no superior a diez (10) menores de veinticinco (25) años', yet neither the ISS base (arts. 128-129) nor the baremo gives any child or family relief; children matter only for school fees in the optional global return (art. 29(2)(i)).
- provisions: Ley 1/2024 arts. 29(2)(i), 128-132
- Lean: GqTax.out (no family input)
- status: model result

### F5 The global return exempts income up to the SMI outright
- kind: statute-fault
- Art. 29(6): taxpayers whose annual net taxable income is 'igual o inferior al Salario Mínimo Interprofesional Anual' are exempt; nothing tapers above it. Whether this creates a cliff depends on the SMI (not reached) relative to the 1.4 M zero band.
- provisions: Ley 1/2024 art. 29(5)-(6)
- Lean: not modelled (SMI not reached)
- status: model result

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | The 2024 code's ISS has no 20 % deduction unless the optional global return is filed: model #guard comparisons; the choice of return is a filing election, not modelled as a household variable. |
| F2, F3 | explained | Cross-reference errors in Ley 1/2024: gov records. |
| F4 | explained | No child relief in the ISS: design. |
| F5 | lead | SMI exemption in the global return: the SMI was not reached. |
| Leads | explained | Rescan: no notch; split gain 765,000 = individual taxation. |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 25.0 % (Ley 1/2024: 'El tipo de gravamen del Impuesto sobre Sociedades se fija en 25%' (law/rescue3/Ley1-2024_ocr_spa.txt:2805)); at a profit of 3 AW the best split costs 13.2 % of the profit, all salary 13.2 %, all dividends 32.5 % (employer contributions: not included); dividends beat salary once employer contributions exceed 31 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
