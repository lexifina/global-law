# SA progress

**Status (2026-11-20 02:07 UTC): built** (access tier B). Lean model `sa/lean` (`satax`, kernel 1.3.0 TaxKernel.World, worldMain), 82 lines, 2 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- BOE (Internet Archive copy 2024-02-21): Income Tax Law art. 1 (activity), 2 (persons subject)
- BOE (Internet Archive copy 2024-04-23): Social Insurance Law 1421 H art. 4, 18, 19
- BOE (Internet Archive copy 2024-05-24): Unemployment Insurance Law art. 7 as amended by M/160 (1441 H)
- Global law saudi-arabia/national/acts/labour-law art. 92 (deductions: social insurance contributions)

## Registry correction (fold back)
PIT N verified (Income Tax Law art. 1-2). Contributions: SIL 1421 H art. 18(2)(a) 9 % up to SAR 45,000 a month (art. 19) for Saudis; SANED share per CEDA decision (0.25 %-1 %). Zakat: not on wages (law not read).

## Not modelled (`unsupported`)
- SANED employee share (rate set by a CEDA decision not found)
- insured under the later social insurance law for new entrants
- non-Saudi residents' taxable activity (rent, professions)
- zakat law not read

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/sa/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/satax`.

- 2026-11-20 W5 pattern A (contributions agent): SANED employee share 0.75 % on the SIL contribution wage (cap 45,000 / month). Provision: Unemployment Insurance Law art. 7 as amended by M/160 (rate by CEDA decision, 0.5-2 %); rate in force from GOSI SANED guide (PDF 5 June 2023), official secondary. Rebuilt (#guards pass), check `w5/pa/check.py SA` 0 / 300 differ with the switch off, rescanned (`scan_world.py SA`).
