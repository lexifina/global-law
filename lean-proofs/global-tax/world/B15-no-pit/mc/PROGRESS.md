# MC progress

**Status (2026-11-20 02:07 UTC): built** (access tier B). Lean model `mc/lean` (`mctax`, kernel 1.3.0 TaxKernel.World, worldMain), 103 lines, 7 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- Caisses Sociales de Monaco, page 'Cotisations' (employer) in Internet Archive copies of 2025-04-21, 2025-09-10, 2025-12-15 (official secondary): C.A.R., assurance chômage, CMRC rates and ceilings
- Live page 2026-11-20 (for comparison only)

## Registry correction (fold back)
PIT N (French nationals: French tax). Contributions (official secondary, CSM tables): C.A.R. 6.85 %, unemployment 2.40 %, CMRC 40 % of 10.02 % / 24.29 %.

## Not modelled (`unsupported`)
- French nationals (French income tax under the 1963 convention)
- self-employed
- the ordonnances / arrêtés fixing the rates were not read

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/mc/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/mctax`.
