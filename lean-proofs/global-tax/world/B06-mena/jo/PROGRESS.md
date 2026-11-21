# Jordan (JO) progress

**Status (2026-11-20T05:30Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: UK, IE.
- Statute read: Income Tax Law No. 34 of 2014 as amended by Law No. 38 of 2018 (ISTD consolidated text, fetched 2026-11-20); Social Security Law No. 1 of 2014 as amended to 16/4/2023 (SSC PDF, scanned).
- Registry correction / check: Registry right (progressive, individual). Detail: six bands 5-30 %, 9,000 personal + 9,000 dependants exemption, couple cap 23,000, 1 % national contribution above 200,000, final 5 % on bank interest.
- Lean: 128 lines, 13 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/jotax` (worldMain).
- Sources (law/):
- `law/itl_p1.html` sha256 087138529bea8edacb2d02ab109f2477a4d7129717be57c748d03e685f92eac4
- `law/itl_p2.html` sha256 eb3dbb380f23c32b7f399ce8c66971fc2f1230363b058df90a8f2a6010799d3c
- `law/ssl2014.pdf` sha256 7bd6415d26a15ed0ecb3b0005d655f93455622f83a52c2375ef0bb53b975e8a6
- Unsupported (in every output line): art. 9 (أ) (3) expense exemptions (invoices); SSC ceiling indexation (art. 20 (ب)); rental expenses, excepted-sector dividends; self-employed social security.
- Scale for the scanners: `scale.json` (statutory threshold, cited).
- Steps: 1 model done; 2 validation: statute's own tables/formulas only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (`Theorems.lean`); 4-5 known/new loopholes: FINDINGS.md (scanner results in `results/search/`, probes in `../logs/probe.json`); 6 government errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent): SSC 7.5 % on wages up to the 2025 indexed ceiling 3,668 JOD / month (was the statutory 3,000). Provision: SSL art. 20 (أ)-(ب); SSC press release on the 2026 ceiling (3,733; "كان العام الماضي (3668)"), official secondary. Rebuilt (#guards pass), check `w5/pa/check.py JO` 0 / 300 differ with the switch off, rescanned (`scan_world.py JO`).
