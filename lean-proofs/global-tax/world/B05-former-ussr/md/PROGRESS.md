# Moldova (MD) progress

**Status (2026-11-20T11:11Z): built (access tier A; rescue pass, see ~/cmp20/world/RESCUE.md). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: RO, KH.
- Statute read: Codul fiscal nr. 1163/1997, consolidated 'act la zi' text with amendment notes, served by weblex.md through the Ministry of Finance's link (mf.gov.md/ro -> 'Codul fiscal al Republicii Moldova'), fetched from the laptop 2026-11-20 (md/law/rescue/weblex_cf_current_20261120.html): art. 12 pct. 4, 11, 12; art. 15 a) 12 % (from 2021); art. 33(1) 29,700 lei if annual taxable income < 360,000 (Law 214/2024 from 01.01.2025); art. 34(2); art. 35(1),(2) 9,900 lei per dependant (from 01.01.2025); art. 35^2(1),(2) contributions deductible; art. 90^1(31),(37) 6 % final on dividends and interest. Global law holds the Codul fiscal only as the 2019 table of contents (metadata).
- Registry correction: Flat 12 % (art. 15 a) with a personal exemption of 29,700 lei that is withdrawn in full at 360,000 lei of annual taxable income, and 9,900 lei per dependant (2025).
- Lean: 97 lines, 9 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/mdtax` (worldMain). Scale: `scale.json`.
- Sources: `law/` and `law/rescue/` (sha256 in each folder's SHA256SUMS).
- Unsupported: employee health-insurance premium and state social-insurance contribution (rates outside the Codul fiscal, not reached): employeeSocial = 0 and their art. 35^2 deduction not applied; rent (12 % or 7 % by tenant); capital gains (cap. 5); pensions
- Routes tried in the rescue pass (UTC 2026-11-20):
  - Global law find_provision 'Codul fiscal' + search '1163-XIII': moldova/national/acts/law/1997/1163 exists but holds only the 2019 table of contents (commit kind 'metadata')
  - Wayback CDX of legis.md getResults (2025): ~2,400 distinct doc_ids, no title index (not scanned: would need thousands of archive fetches)
  - mf.gov.md (answers lean1): its menu links the Codul fiscal to demo.weblex.md (ref/mf); the page loads its text by the site's own AJAX call (?ajax=1), which answers the laptop (lean1 gets empty bodies); 1.5 MB consolidated text saved
  - legis.md, sfs.md, parlament.md: 403 (not bypassed); monitorul.gov.md: no answer
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B05-former-ussr/md/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py MD`.
