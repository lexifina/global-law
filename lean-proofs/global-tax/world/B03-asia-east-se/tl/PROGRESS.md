# Timor-Leste (TL) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: PT.
- Statute read: Lei n.º 8/2008 Lei Tributária (Jornal da República Série I N.º 26, 2008), republished by Lei 5/2019; Anexo V (wage tax), Anexo VI (income tax), arts. 20-27; Lei 17/2023 art. 8 (PE definition only); DL 20/2017 art. 10 as republished by DL 30/2021 (4 % employee contribution).
- Registry correction: Wage income tax: 10 % of monthly taxable wages above US$500 for residents (Anexo V), final (art. 25); other income of individuals: 10 % above US$6,000 a year (Anexo VI); employee social security 4 % with no ceiling for private-sector employees. Global law holds only the Constitution and Lei 11/2009.
- Lean: 79 lines, 9 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/tltax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS where files were saved).
- Unsupported: interest and dividends (withholding regime arts. 53-56); capital gains; pensions.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py + b03scan); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.
