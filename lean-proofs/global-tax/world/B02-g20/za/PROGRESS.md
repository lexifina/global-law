# South Africa (ZA) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2026 year of assessment (1 Mar 2025 - 28 Feb 2026); access tier B; reused patterns: UK, IE, AU.
- Statute read: Income Tax Act 58 of 1962 not reachable (SARS LexisNexis portal); SARS tables (official secondary): rates of tax for individuals (2026 = 2024 table, 'No changes'), rebates 17,235 / 9,444 / 3,145, interest exemption 23,800 / 34,500, dividends tax 20 %, UIF 1 % up to R17,712/month.
- Registry correction: Tax year 2026 YoA as contract; unit individual; the 2026 Rates and Monetary Amounts Act text not found on gov.za's act list.
- Lean: 92 lines, 13 defs, 5 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/zatax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): capital gains; retirement-fund deduction s. 11F; medical credits s. 6A/6B.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.
