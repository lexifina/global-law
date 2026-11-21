# Holy See (Vatican City State) (VA) progress

**Status (2026-11-20T13:10Z): built (access tier B; rescue pass 2, see ~/cmp20/world/RESCUE.md, Pass 2). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: B15 no-PIT pattern.
- Statute read: vatican.va (official): Lateran Treaty 1929 art. 17 (Holy See remuneration exempt from Italian taxes); Regolamento per le Pensioni, AAS 84 (1992) pp. 1033-1052, art. 8 (20 % incl. the employee's 5 %; rates variable by the Secretary of State); Regolamento Generale del Fondo Pensioni (AAS 2004, April) art. 15(2) (rates set 'tempo per tempo' by the Secretary of State); Rescriptum of 6 April 2009 (AAS 2009, May) raising the Administrations' share 25 -> 26 %; Global law vatican-city (Legge fondamentale, Legge sulle fonti: no tax).
- Registry correction: No income tax (no Vatican text levies one; Lateran Treaty art. 17 exempts Holy See pay from Italian taxes); Fondo Pensioni employee share set by the Secretary of State, 2025 rate not published.
- Lean: 51 lines, 3 defs, 1 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/vatax` (worldMain). Scale: `scale.json`.
- Sources: `law/`, `law/rescue/` and `law/rescue2/` (sha256 in each folder's SHA256SUMS).
- Unsupported: Fondo Pensioni employee contribution: 2025 rate not published (last published 5 %, 1992)
- Routes tried in rescue pass 2 (UTC 2026-11-20; pass-1 routes below them):
  - vatican.va AAS archive (laptop index; lean1 download): 308 volumes/issues 1993-2026 scanned for 'Fondo Pensioni' / 'Regolamento per le Pensioni' (rescue2/va_aas/hits.tsv): the 1992 Regolamento (AAS 84 pp. 1033-1052), the 2004 Statute and Regolamento Generale, the 2009 rate rescript, the 2013 Gendarmeria special account (46.99 % incl. the employee share), the 2015 revised Statute, the 2024 motu proprio on the Fund; none states the employee share in force in 2025
  - vatican.va Lateran Treaty page (art. 17)
- Pass-1 routes (rescue agent):
  - vatican.va (archived and live): Secretariat of State decrees of 1989, 1992 (implementing the Regolamento per le Pensioni approved by motu proprio of 8 September 1992), 1993 and 1998 on pensions read: none states the employee contribution rate; the 1992 Regolamento itself (AAS 84 (1992)) was not found online
  - no tax on employees found in any text read
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/va/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py VA`.
