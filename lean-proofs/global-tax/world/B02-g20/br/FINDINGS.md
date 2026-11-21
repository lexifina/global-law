# Brazil (BR) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 The annual table is a sum of two rounded tables: band form and parcela form differ by up to 7 centavos
- kind: statute-fault
- Lei 11.482 art. 1 par. único builds the annual table as the sum of the monthly tables; each monthly 'parcela a deduzir' is rounded to the centavo, so rate × base − Σ parcelas differs from the band sum by up to ~6-7 centavos per year. Immaterial, but two published forms of the same table disagree.
- provisions: Lei 11.482/2007 art. 1 XI, XII, par. único
- Lean: BrTax.annualParcela, #guard within
- status: proved on sample points (#guard)

### F2 Children are worth nothing to a one-earner family with one or two children
- kind: loophole-new
- The simplified discount (20 %, capped at R$ 16,754.34, Lei 9.250 art. 10) ignores dependants; the complete form gives INSS (at most about R$ 11,420 a year in 2025) plus R$ 2,275.08 per dependant (art. 8 II c). Once the cap binds, INSS + 2 dependants (about R$ 15,970) stays below it: measured at R$ 60k, 100k and 200k of wages, the tax with 0 and with 2 children is identical (2,745; 12,039; 39,539); only a third child changes it (2,533; 11,629; 39,129). Statute-faithful; the dependant amount has been frozen since 2015.
- provisions: Lei 9.250 arts. 8, 10
- Lean: BrTax.decl
- status: lead

### F3 Frozen nominal amounts since 2015
- kind: gov-error
- Dependant deduction (R$ 2,275.08), simplified-discount cap (R$ 16,754.34) and the 65+ pension exemption (R$ 1,903.98/month) are unchanged since April 2015 while the zero band rose in 2023-2025: a reading, not an error; record as a policy fact.
- provisions: Lei 9.250 arts. 4, 8, 10
- Lean: BrTax params
- status: fact

### F4 Generic scan: no notch, max METR 42.9 %
- kind: model-fix
- b02scan on 0-2.5 × R$ 55,976: no net-income fall.
- provisions: -
- Lean: results/search/b02scan.md
- status: scan done

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | model-proved | BrTax #guard (model build); Lei 11.482 art. 1 par. único as cited by the builder. Up to 7 centavos. |
| F2 | loophole | confirmed | the first two children are worth 0 to a one-earner family at R$ 60k, 100k and 200k of wages (tax 2,745 / 12,039 / 39,539 with 0 or 2 children); a third child 212-410. exe and #guard L1BR.F2 (nine households). Status raised from lead: the statute amounts re-read in Lei 9.250. Evidence: exe + Lean `L1BR.F2` (`world/loopholes/rest/lean/L1BR.lean`, 9 #guard): it(a0) = 2745; it(a2) = 2745; it(a3) = 2533; it(b0) = 12039; it(b2) = 12039; it(b3) = 11629; it(c0) = 39539; it(c2) = 39539; it(c3) = 39129; statute re-read: `law/l9250_3_4_8_10_11_20250630.txt`. Known/new: **known**: guiatributario.net 'IRPF: Dedução por Dependente Comum é Prejudicada no Caso de Declaração Simplificada?' and Pontotel / Fenacon guides: the simplified discount replaces the dependant deduction; web search 7. |
| F3 | fact | explained | Frozen amounts (policy fact; statute re-read in F2). |
| F4 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BR.json`): timing 3,768 (6.7 % of the scale) = the INSS contribution ceiling; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (dividends exempt for individuals in 2025).
