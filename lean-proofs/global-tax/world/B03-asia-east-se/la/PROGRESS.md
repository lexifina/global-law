# Laos (LA) progress

**Status (2026-11-20T11:11Z): built (access tier A; rescue pass, see ~/cmp20/world/RESCUE.md). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: KH, MN.
- Statute read: Lao Official Gazette (laoofficialgazette.gov.la): Law on Income Tax No. 67/NA of 18 June 2019 (gazette id 1581) arts. 35(1), 36(2), 39(1) table (page image), 39(5); Law No. 01/NA of 7 August 2021 amending tax laws (id 1828: replaced only arts. 14, 16, 18, 73 of the income-tax law); Law on Income Tax (amended), adopted by NA resolution 164/NA of 25 June 2025, promulgated August 2025 (id 2597, gazetted 19 June 2026) arts. 34(1), 38(1) table (page image), 74 'in force from 1 September 2025'; Law on Social Security No. 54/NA of 27 June 2018 (id 1442) art. 74 (employee 5.5 %), art. 77 (ceiling set by the government).
- Registry correction: Law on Income Tax 67/NA (2019) to 31 Aug 2025, then the amended Law on Income Tax (2025) from 1 Sep 2025 (art. 74): monthly progressive 0-25 % on salary; the zero band rises from 1.3m to 2.5m kip.
- Lean: 99 lines, 10 defs, 6 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/latax` (worldMain). Scale: `scale.json`.
- Sources: `law/` and `law/rescue/` (sha256 in each folder's SHA256SUMS).
- Unsupported: social security insured-wage ceiling (SSL art. 77; government decision) not reached: 5.5 % applied without a ceiling; self-employment (gross-receipt rates by activity) not mapped from net income; capital gains (2 % of sale price) needs the price; a government change of the minimum wage in Sep-Dec 2025 (2025 law art. 34(1), note to art. 38(1)) not checked
- Routes tried in the rescue pass (UTC 2026-11-20):
  - laoofficialgazette.gov.la answered from lean1 this time (the batch pass had timeouts); law lists scanned politely (la/law/rescue/laws_list.txt, decrees_list.txt)
  - Lao OCR: tessdata_best lao.traineddata in user space; four scans OCR'd (pit2019, taxamend2021, pit2025, ssl2018) and the rate tables read on page images
  - tax.gov.la: no answer (timeout) from lean1
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B03-asia-east-se/la/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py LA`.
