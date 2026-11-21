# Indonesia (ID) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 PTKP frozen since 2016
- kind: fact
- PMK 101/2016 Pasal 3: in force from tax year 2016; no later adjustment found.
- provisions: UU PPh Pasal 7 (3); PMK 101/2016
- Lean: IdTax.ptkp
- status: fact

### F2 Married women employed by one employer are taxed apart with a single PTKP
- kind: loophole-known
- Penjelasan Pasal 7 (1) example; PMK 168/2023 Pasal 9 (2) a: the wife's PTKP is 54 m; the household gains from separate bands relative to joining.
- provisions: Pasal 7, 8 UU PPh
- Lean: IdTax.out
- status: modelled

### F3 Generic scan: no notch, max METR 30 %
- kind: model-fix
- b02scan.
- provisions: -
- Lean: results/search/b02scan.md
- status: scan done


## Round W2 (improvement agent, 2026-11-20): pointers from the new software probes (coordinator)

### W2-1 Employer-paid insurance is income and employee JHT/JP is deductible (PMK 168/2023); now inputs
- kind: model-fix
- PMK 168/2023 Pasal 5 (3) (id/law/pmk168_2023.txt): the employee's income includes "d. pembayaran iuran jaminan
  kecelakaan kerja dan iuran jaminan kematian ... yang dibayarkan oleh pemberi kerja; e. pembayaran iuran jaminan
  pemeliharaan kesehatan ... yang dibayarkan oleh pemberi kerja; dan f. pembayaran premi asuransi kesehatan, asuransi
  kecelakaan kerja, asuransi jiwa, asuransi dwiguna, dan asuransi beasiswa yang dibayarkan oleh pemberi kerja"; Pasal 7
  c excludes employer-paid pension / JHT contributions; Pasal 10 (1) b deducts "iuran terkait program pensiun dan hari
  tua, yang terkait dengan gaji, yang dibayar oleh Pegawai melalui pemberi kerja". So gajian's treatment (gross with
  employer JKK/JKM/Kesehatan, less employee JHT + JP) is the statute's, and the model lacked both. The rates are in
  PP 44/45/46/2015 and the BPJS Kesehatan Perpres (not read; not in Global law's Indonesia corpus, which holds regional
  acts). Change: optional inputs `idEmployerInsuranceRate` and `idEmployeeRetirementRate` (basis points of wages);
  biaya jabatan is taken on the gross including the employer-paid part (Pasal 10 (2): "5% ... dari penghasilan bruto");
  the employee's retirement contributions are deducted and reported as employeeSocial; base caps (JP, Kesehatan) not
  applied. Defaults 0 leave the model as it was. #guards.
- provisions: PMK 168/2023 Pasal 5 (3) d-f, Pasal 7 c, Pasal 10 (1) b, (2)
- Lean: IdTax.Bpjs, IdTax.empNeto (#guard)
- status: model changed (defaults unchanged); rates open

## Round W4 (improvement agent, 2026-11-20): W3 dev failures settled from the statute

### W4-1 Employee JHT 2 % and JP 1 % deducted by default (PP 46/2015, PP 45/2015; PMK 168/2023 Pasal 10 (1) b)
- kind: model-fix
- Read on JDIH Kemnaker (law/w4/, sha256 in the Lean docstring): PP 46/2015 Pasal 16 (1) "Iuran JHT ... 5,7% ... dari
  Upah ... a. 2% (dua persen) ditanggung oleh Pekerja"; PP 45/2015 Pasal 28 (1) "Iuran Jaminan Pensiun wajib dibayarkan
  setiap bulan", (3) b "1% (satu persen) dari upah ditanggung oleh Peserta"; Pasal 29 (2) cap "untuk tahun 2015 ...
  Rp7.000.000,00 ... setiap bulan", (3)-(4) indexed yearly by BPJS Ketenagakerjaan (1 + previous year's GDP growth) and
  announced by it. The 2025 announcement was not reached (bpjsketenagakerjaan.go.id search, peraturan.bpk.go.id 403):
  the JP base cap is the input `idJpWageCapMonthly`, default the statute's own Rp7,000,000 (flagged). Both
  contributions are now deducted and reported as employeeSocial by default.
- Employer-paid JKK, JKM and health contributions are income (PMK 168/2023 Pasal 5 (3) d-e), but JKK depends on the
  employer's risk class (PP 7/2025 lists 0.24 % to 1.74 % for 2025, with a 50 % relief for some sectors), the JKM rate
  (PP 44/2015) and the health rate (Perpres 82/2018) were not read: still the input `idEmployerInsuranceRate`, default 0.
- Effect (dev, regression reported): indo-salary 47 / 188 -> 47 / 504; gajian 50 / 348 -> 49 / 95; Peco 43 / 958 -> 43 /
  43; id-utils 1,038 / 1,038 -> 40 / 40. id-utils computes PPh 21 with no BPJS at all (a simplification: PMK 168/2023
  Pasal 10 (1) b); gajian and Peco deduct employee JHT + JP but also add employer-paid JKK / JKM / health to gross,
  which the model cannot yet do by default, so the half the statute lets us cite now moves the model below them. Peco's
  employeeSocial implies a 2025 JP cap of Rp10,547,400 and a 1 % health contribution capped at Rp12,000,000 (pointers,
  not citable). Next: read PP 44/2015 (JKM 0.30 %), Perpres 82/2018 and the BPJS 2025 JP-cap announcement.
- provisions: PMK 168/2023 Pasal 5 (3), 10 (1) b; PP 45/2015 Pasal 28-29; PP 46/2015 Pasal 16; PP 7/2025
- Lean: IdTax.Bpjs, IdTax.employeeRetirement (#guards)
- status: model changed; employer side open

### W5S-1 payroll-calculator (riod94): no biaya jabatan (W5 review pass 2, 2026-11-20)
- kind: software-error
- `id_open_payroll_calculator_riod94_grid`: the tool's taxable income is gross less PTKP only (at 58,209,158 single: 5 % x 4,209,000 = 210,450); PMK 168/2023 Pasal 10 (2) deducts 'biaya jabatan ... 5% (lima persen) dari penghasilan bruto', at most 6,000,000 a year (IdTax). Misses are marginal rate x the biaya jabatan (900,000 / 1,500,000 / 1,800,000 at the cap).
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Perpres 82/2018 as amended by Perpres 64/2020, Pasal 30 (1) b, Pasal 32 (1)
- BPJS Kesehatan employee 1 % of wages up to Rp12 million / month (reported; not deductible). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | fact | explained | PTKP unchanged since PMK 101/2016 (builder); fact. |
| F2 | loophole | model-proved | the employed wife's own PTKP: her 54 M of wages adds 0 tax to the household. exe and #guard L1ID.F2; the 54 M amount is in PMK 101/2016 (not in the files re-read). Known design of separate taxation of employed wives. Evidence: exe + Lean `L1ID.F2` (`world/loopholes/rest/lean/L1ID.lean`, 1 #guard): it(b)-it(a) = 0. Known/new: **unclear**: pattern: final (non-cumulative) withholding penalises uneven pay; no description found in the Crossref record (hits on withholding were unrelated). |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W2-1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W4-1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/ID.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F2 pattern).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: floor at low pay AW (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
