# Croatia (HR, City of Zagreb), tax year 2025: progress

Owner: HR worker of the Central Europe family. Folder `~/cmp20/central/hr/` only. Contracts: `~/cmp20/CONTRACT38.md`,
`~/cmp20/CONTRACT20.md`; kernel `~/cmp20/kernel/API.md` (1.2). Updated 2026-11-19.

## Status: done (7/7 steps); open items below

| Step | State | Where |
|---|---|---|
| 1 Model | done | `lean/` (HrTax, exe `hrtax`), builds clean, 0 sorry, no native_decide; TaxKernel by path. Params/Tax/Household: local rates (Zagreb 23/33 %, any unit via `lowerRate`/`higherRate`), allowance with child coefficients and dependants, young relief, pension contributions with the 2024 base reduction and monthly cap, final 12 % capital taxes, rent, obrt (books / paušal), doplatak za djecu. All income tax booked as `localIncomeTax` (shared tax of cities and counties, ZFJLP(R)S čl. 5) |
| 2 Validation | done | PU calculator formula 4.176/4.176 within 1 € (`tools/pu_calc.py`); PU young-worker examples 6/8 (2 PU errors, F3); PU allowance and paušal tables 50/50, Naredba/ZDD/EUROMOD amounts 16/16 (`Tests.lean`); Eurostat 2025 sanity check 35/39 exact with Eurostat's 22,4 % rate (F1, F2) |
| 3 Proofs | done | `Theorems.lean` (kernel schedule theorems for Zagreb; all allowed rate pairs progressive; base-reduction taper step and bounds; child scale), `Walls.lean` (findings on named households), `Tests.lean` |
| 4 Known loopholes | done | `CATALOGUE.md`: 17 catalogued, 12 recreated, 5 not modelled, 5 found blind (`tools/recreate.py`, `runs/recreate.md`) |
| 5 New loopholes | done | F10 (doplatak notches, METR > 100 %), F13 (uneven monthly pay vs ZD čl. 21.a/204); scanners `results/search/` (harness run_all.py HR); owner-manager `tools/owner_hr.py` (F16) |
| 6 Gov errors / statute faults | done | gov errors F3 (PU young examples), F4 Novigrad (calculator), F9 (calculator parsing); statute faults F4 Knin gap, F5 (čl. 24 st. 5 wording), F6 (10th-child step), F7 (2020-24 cross-reference); referee issues F1, F2, F5 (EUROMOD pensions) |
| 7 USEFUL.md | done | `USEFUL.md` |

Web searches used: 2 / 4 (Naredba 2025 bases; paušal / disguised-employment literature).

## Open
- Knin (F4): which higher rate (30 % or 32 %) the 2025 annual assessment actually used; no Knin decision found in
  NN 1-40/2025.
- Doplatak: the lone-parent 15 % supplement (ZDD; Eurostat applies it to all lone parents, F2) and the previous-year
  income test are not modelled (contract convention: the year's own income).
- Not modelled: assisted-area and returnee reliefs, minimum contribution base for full-time work (ZD čl. 200), annual
  max base (čl. 206), drugi dohodak, non-taxable employer payments, tourist letting per bed, self-employment losses,
  pensioner-specific items. EUROMOD's Y16 report was read (parameters), its hypothetical-household tool not used.
- `company.json` HR in the harness is still the OECD placeholder (sent to kernel INBOX with the statute side).

## How to resume
- Build: `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build`; run `lean/.lake/build/bin/hrtax < grid.jsonl`
  (extra input fields: `lowerRate`, `higherRate` (bp), `pausal`/`pausal2`, `pillar2`, `childShare1` (bp), `childBenefit`).
- Checks: `python3 tools/pu_calc.py "Grad Zagreb"`; `python3 ~/cmp20/harness/oecd_check38.py HR --referee eurostat --out
  results`; `python3 tools/eurostat_alt.py '{"lowerRate":2240}'`; `python3 ~/cmp20/harness/search/run_all.py HR --out
  results/search`; `python3 tools/owner_hr.py`; `python3 tools/recreate.py`; `python3 tools/stats.py`.
- Statute copies: `refs/nn*.txt` (ZPD NN 115/16 + amendments to NN 152/24; ZD NN 84/08, 115/16, 106/18, 114/23, 152/24;
  Naredba NN 137/24, 25/25; Zagreb NN 28/2025; Knin NN 154/24; Novigrad-Cittanova NN 34/25; Pravilnik PD NN 10/17, 16/25;
  Pravilnik o doprinosima NN 143/23, 14/24, 16/25; paušal NN 1/24, 16/25; ZDD NN 156/23; budget law NN 149/24; minimum wage
  NN 124/24; ZPDobit NN 138/20, 114/23; ZFJLP(R)S NN 127/17, 138/20, 151/22, 114/23), Porezna uprava pages `refs/pu_*.txt`,
  rate tables `refs/pu_stope_*.tsv`, calculator `refs/kalk/` (JS, podaci.json, Primjeri_izracuna_za_mlade.pdf), EUROMOD
  `refs/em_CR_HR_Y16.txt`, literature `refs/lit_*.txt`.
- Tools: `tools/fetch.py URL NAME` (polite, 1,5 s), `tools/nn_issue.py YEAR NUM PATTERN` (NN issue index), `tools/art.py`,
  `tools/xlsx2csv.py`.
