# Palestine (PS) progress

**Status (2026-11-20T11:39Z): built (access tier A; rescue pass, see ~/cmp20/world/RESCUE.md). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: JO, KH.
- Statute read: Decree-Law No. 8 of 2011 on Income Tax (Al-Waqa'i' al-Filastiniyya special issue 5, 2011-10-24) arts. 12, 14, 16, as amended by Decree-Laws No. 4 of 2014 (issue 106: dividends 10 % at source, art. 16(5); bank-interest final tax art. 31(8) repealed), No. 5 of 2015 (issue 112: exemption 36,000 ILS, art. 12(1)(a); rates 5 % to 75,000, 10 % to 150,000, 15 % above, art. 16(1)) and No. 14 of 2016 (issue 123: agricultural income exempt); texts from Al-Muqtafi (Birzeit University; ids 16266, 16576, 16702, 16814) via Internet Archive captures of 2025-01 (muqtafi does not answer directly). Global law's Waqa'i' catalogue (to 2026-10-29) supplied the gazette issues and muqtafi ids and lists no later income-tax text.
- Registry correction: Decree-Law 8/2011 as amended to 2016 (last amendment 14/2016): 5/10/15 % with bands at 75,000 and 150,000 ILS and a 36,000-ILS annual exemption per resident; spouses taxed separately. PA law (West Bank); Gaza administered separately since 2007.
- Lean: 79 lines, 6 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/pstax` (worldMain). Scale: `scale.json`.
- Sources: `law/` and `law/rescue/` (sha256 in each folder's SHA256SUMS).
- Unsupported: employee contributions to pension, health or social-security funds (exempt under art. 12(1)(d)) not modelled: employeeSocial = 0; interest (2014 repeal of the 5 % final tax; current treatment not established); capital gains; pensions; optional joint assessment of spouses (art. 14(3)); transport allowance exemptions (art. 12(1)(b)-(c)) need the allowance paid
- Routes tried in the rescue pass (UTC 2026-11-20):
  - Global law catalogue (metadata) read for the gazette issue and the Al-Muqtafi record id of Decree-Law 8/2011 and of each amending decree-law (4/2014, 5/2015, 14/2016)
  - muqtafi.birzeit.edu does not answer (lean1, laptop); Internet Archive CDX shows captures of getleg.asp?id=16266/16576/16702/16814 up to 2025-2026; the 2025 captures were read (ps/law/rescue/muq_*.html)
  - pmof.ps: no answer from lean1 this time
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B06-mena/ps/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py PS`.
