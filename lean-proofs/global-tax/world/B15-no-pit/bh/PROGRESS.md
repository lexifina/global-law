# BH progress

**Status (2026-11-20 02:07 UTC): built** (access tier B). Lean model `bh/lean` (`bhtax`, kernel 1.3.0 TaxKernel.World, worldMain), 86 lines, 3 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- LLOC consolidated Decree-Law 24/1976 (Social Insurance Law) with amendments (/FullAr/L2476.docx): art. 2, 3, 17, 33
- Law 14/2022 (LLOC K1422) substituting art. 33(1)-(2)
- Decree-Law 44/2026 and Law 19/2026 (amendment list): no change to art. 17/33
- LLOC consolidated Decree-Law 78/2006 (unemployment insurance) art. 1(17), 2, 6

## Registry correction (fold back)
PIT N (no act found). Contributions: DL 24/1976 art. 33 (7 %, Law 14/2022) up to BHD 4,000 a month (art. 17) + DL 78/2006 art. 6 unemployment 1 % (all nationalities).

## Not modelled (`unsupported`)
- old-age branch for non-Bahraini workers (phased application by decisions not read)
- GCC nationals
- public servants (Law 13/1975)

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/bh/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/bhtax`.
