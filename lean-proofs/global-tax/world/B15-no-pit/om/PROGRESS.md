# OM progress

**Status (2026-11-20 02:07 UTC): built** (access tier A). Lean model `om/lean` (`omtax`, kernel 1.3.0 TaxKernel.World, worldMain), 74 lines, 3 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- qanoon.om: Royal Decree 56/2025 (Individuals' Income Tax Law) art. 4 of the decree: in force 1 January 2028
- qanoon.om amended text of Royal Decree 52/2023 (Social Protection Law): decree art. 6 (as amended by RD 60/2025), law art. 1(15)-(16), 52, 70, 71, 115, 116, 139
- Global law oman/national/acts/rd/2009/28 (Income Tax Law, companies)

## Registry correction (fold back)
PIT N in 2025, verified: RD 56/2025 Individuals' Income Tax Law in force 1 January 2028. Contributions: Social Protection Law RD 52/2023 (in force 1 Jan 2024): 7.5 % up to OMR 3,000 a month + 0.5 % job security (Omanis).

## Not modelled (`unsupported`)
- Ministry of Finance subsidy of the insured's share (art. 71, decision not read)
- GCC nationals

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/om/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/omtax`.
- 2026-11-20 W5 review: see FINDINGS W5-1.
