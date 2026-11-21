# Indonesia (ID) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: AU, NZ.
- Statute read: UU 7/2021 (HPP) Pasal 7, 17 and Penjelasan (pajak.go.id official copy); PMK 101/PMK.010/2016 (PTKP); PMK 168/2023 Pasal 8-11 (biaya jabatan, biaya pensiun, PKP rounding, PTKP of married women).
- Registry correction: Registry right; PTKP unchanged since tax year 2016 (no later PMK in the DGT catalogue).
- Lean: 100 lines, 13 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/idtax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): final taxes on interest, dividends, rent, shares; BPJS contributions.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent): BPJS Kesehatan employee 1 % of wages up to Rp12 million / month (reported; not deductible). Provision: Perpres 82/2018 as amended by Perpres 64/2020, Pasal 30 (1) b, Pasal 32 (1). Rebuilt (#guards pass), check `w5/pa/check.py ID` 0 / 300 differ with the switch off, rescanned (`scan_world.py ID`).
