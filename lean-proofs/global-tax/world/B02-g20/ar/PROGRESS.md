# Argentina (AR) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (período fiscal 2025); access tier B; reused patterns: ES, MX.
- Statute read: Ley de Impuesto a las Ganancias t.o. 2019 (Decreto 824/2019) as replaced by Ley 27.743 (InfoLEG consolidated text via argentina.gob.ar/normativa) arts. 30, 82, 85, 94; ARCA annual 2025 art. 30 table (official secondary); Leyes 24.241 art. 11, 19.032 art. 8 (d), 23.660 art. 16 (b).
- Registry correction: Amounts are adjusted every January and July by IPC from 2025 (art. 30, 94 last paragraphs, Ley 27.743); the annual 2025 art. 30 amounts are ARCA's; the art. 94 scale is derived with the same coefficient (tier B).
- Lean: 110 lines, 15 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/artax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): impuesto cedular; pensions; self-employed; contribution ceiling.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent 2): SIPA 11 % computed monthly on wages / 12 capped at the ANSES maximum base of each 2025 month (2.910.574,49 in January to 3.731.212,01 in December); INSSJP and obra social 3 % + 3 % stay on all wages. Provision: Ley 24.241 art. 9 (texto Ley 26.222), ANSES Resoluciones 1247/2024, 66, 145, 179, 211, 237, 251, 278, 298, 317, 338, 359/2025 art. 3 (Boletín Oficial). Rebuilt (#guards pass), check `w5/pa/check.py AR` 0 / 300 differ with the switch off, rescanned (`scan_world.py AR`).
