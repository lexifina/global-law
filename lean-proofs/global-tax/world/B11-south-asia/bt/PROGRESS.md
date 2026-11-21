# Bhutan (BT) progress

**Status (2026-11-20T06:25Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md; SOFTWARE.md lists none for this country unless updated), then datasets.**

- Year: 2025 (calendar income year); access tier A; reused patterns: IN, UK.
- Statute read: Income Tax Act of the Kingdom of Bhutan 2001, Fourth Edition (DRC, drc.gov.bt/acts-policy; amendments of the Income Tax (Amendment) Act of Bhutan 2020 with footnotes): Part III ss. 2, 4.1, 5.3, 6.3, 8.3, 12, 13, 14, 14A; Rules on the Income Tax Act, Fifth Edition (r. 35, 36); Income Tax Act of Bhutan 2025 ss. 2, 4 (in force 1 January 2026: income year 2025 stays under the 2001 Act).
- Registry correction: Registry: 'Income Tax Act' -> ITA 2001 (4th edition, as amended 2020) governs income year 2025; the new ITA 2025 applies from 1 January 2026. Rates: nil 300,000; 10 % to 400,000; 15 % to 650,000; 20 % to 1 m; 25 % to 1.5 m; 30 % above; 10 % surcharge when PIT >= 1 m; each spouse taxed separately; pensions exempt.
- Lean: 106 lines, 9 defs, 5 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/bttax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS).
- Unsupported: NPPF/GPF and GIS contributions (rates outside the tax law; optional btPF1/btPF2); interest (not a PIT source after the 2016 repeal); education deduction only via btEducation.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean) + #guard notches; 4-5: FINDINGS.md (catalogue, scanners, search record); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 round D4: income year 2026 added from the Income Tax Act of Bhutan 2025 (Schedule 1, s. 44, s. 160, Schedules 3 and 6) and the Rules on the ITA 2025 (Rules 47-50, 61-64, 148-150, 153); years.json [2025, 2026]; 2025 unchanged. The Rules' Annexure I (TDS tables) was not opened: it is the D3 referee.
