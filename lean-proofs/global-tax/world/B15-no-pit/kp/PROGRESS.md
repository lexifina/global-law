# Democratic People's Republic of Korea (KP) progress

**Status (2026-11-20T13:10Z): built (access tier B; rescue pass 2, see ~/cmp20/world/RESCUE.md, Pass 2). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: B15 no-PIT pattern.
- Statute read: Constitution of the DPRK (1972, rev. 2016), English text on constituteproject.org ('Korea (Democratic People's Republic of) 1972 (rev. 2016)', marked 'Subsequently amended'; kp/law/rescue2/cp_kp2016.html), art. 25: '... in our country, where taxes have been abolished ...'.
- Registry correction: No income tax: Constitution art. 25 ('taxes have been abolished'); employee social-insurance withholding not reached.
- Lean: 44 lines, 3 defs, 1 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/kptax` (worldMain). Scale: `scale.json`.
- Sources: `law/`, `law/rescue/` and `law/rescue2/` (sha256 in each folder's SHA256SUMS).
- Unsupported: employee social-insurance contributions (if withheld): no text reached
- Routes tried in rescue pass 2 (UTC 2026-11-20; pass-1 routes below them):
  - constituteproject.org (laptop): DPRK constitution 1972 (rev. 2016), English; art. 25 quoted; the page says the text was amended later (2019 and later revisions not reached)
  - naenara.com.kp/index.php/Main/load_view/constitution1 from the laptop: no answer (as from lean1 in pass 1)
  - Global law north-korea: catalogue entries only (pass 1); WIPO Lex profile KP not tax-related
- Pass-1 routes (rescue agent):
  - Global law north-korea: 4 acts, catalogue entries only; '세금' / '세금제도': 0
  - naenara.com.kp answers lean1; its 'politics' page loads the Constitution by an AJAX view (index.php/Main/load_view/constitution1), which did not answer (two tries, 40 s and 90 s)
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/kp/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py KP`.
