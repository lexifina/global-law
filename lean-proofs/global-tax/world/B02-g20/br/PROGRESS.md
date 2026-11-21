# Brazil (BR) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (ano-calendário 2025, Declaração de Ajuste Anual 2026); access tier A; reused patterns: PT.
- Statute read: Lei 7.713/1988, Lei 9.250/1995 arts. 4, 8, 10, 11 (Global law), Lei 11.482/2007 art. 1 XI-XII and parágrafo único (archived Planalto copy), Lei 15.191/2025 (Global law), EC 103/2019 art. 28 (archived Planalto), INSS 2025 bands (archived gov.br/inss page).
- Registry correction: 2025 has two monthly tables (XI Jan-Apr, XII May-Dec, Lei 15.191/2025); the annual table is their sum (Lei 11.482 art. 1 par. único). Unit individual (registry right). INSS bands are indexed with RGPS benefits (EC 103 art. 28 § 2): 2025 values are INSS's published table (official secondary).
- Lean: 150 lines, 20 defs, 5 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/brtax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): interest, capital gains (separate taxation); 13º salário; self-employed INSS.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.
