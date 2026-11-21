# Sources: Australia (AU)

The model in `lean/` cites the provision behind each rule in its comments. The law texts, official pages and tables it was built from are not copied into this repository: some were read from secondary hosts, and many publishers do not allow redistribution. Each file used is listed below with its SHA-256, so a copy fetched from the publisher can be checked against the one the model was built from. Paths are as they were in the build folder.

## Source notes written during the build

### AU sources (every parameter and test value in `lean/` cites one of these)

Statute text: Global law record `australia/federal/acts` (Federal Register of Legislation compilations; the record
holds the 2024-25 text of ITRA 1986, MLA 1986, FA Act 1999, PHI Act 2007, HESA 2003; ITAA 1997 only from its
2026-07-01 compilation, LITO unchanged since 2020-21). Official text: legislation.gov.au.

- Income Tax Rates Act 1986 (C2004A03348): https://www.legislation.gov.au/C2004A03348/2024-10-01/text (Sch 7 Pt I
  cl 1; table amended 2025-03-28 to "2024-25 or 2025-26", 15 % for 2026-27, 14 % from 2027-28).
- Income Tax Assessment Act 1997 ss. 61-110, 61-115 (LITO), 4-10, 4-15, 6-5, 26-55, 30-15, 67-25, 115-25, 115-100,
  202-60, 207-20, 290-150, 291-20, 293-20, 295-160, 995-1: https://www.legislation.gov.au/C2004A05138/latest/text
- Medicare Levy Act 1986 (C2004A03351) ss. 3, 6, 7, 8, 8B-8D: compilation 2025-01-01 and the amendments by
  C2025A00028 (TLA (More Cost of Living Relief) Act 2025, in force 2025-03-28) and Act No. 58, 2026 (in force
  2026-07-01); s. 8(2) formula from the official epub alt text:
  https://www.legislation.gov.au/C2004A03351/2026-07-01/2026-07-01/text/original/epub/OEBPS/document_1/document_1.html
- Private Health Insurance Act 2007 ss. 22-30 to 22-45 (MLS tiers, indexed): https://www.legislation.gov.au/C2007A00031/2025-12-05/text
- A New Tax System (Family Assistance) Act 1999 (C2004A00490) Sch 1 cll 1-4, 6A, 7, 25, 28, 28B, 28D, 29, 30, 32,
  33, 38A, 38L-38N; Sch 3 cll 2-3; Sch 4 cl 2: https://www.legislation.gov.au/C2004A00490/2024-10-14/text
- Higher Education Support Act 2003 ss. 154-5, 154-10: https://www.legislation.gov.au/C2004A01234/2026-04-29/text
- PAYG withholding schedules (TAA 1953 Sch 1 s. 15-25): F2024L00664 (from 1 July 2024), F2025L00647 (from 1 July
  2025), F2025L01016 (from 24 September 2025):
  https://www.legislation.gov.au/F2024L00664/asmade/2024-06-11/text/original/word (same pattern for the others);
  local copies `F20*.docx`, extracted text `F20*.txt`; `schedule1_sample_weekly_2024.json` = the weekly
  "Sample data" table (48 rows x 5 scales).

Agency pages (ATO and DSS answer 403 to automated clients; read from web.archive.org snapshots of the official pages):

- ATO "Tax rates - Australian residents": web.archive.org/web/20260106055531/https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents
- ATO "Medicare levy reduction for low-income earners" (Angie example): web.archive.org/web/20251202031136/https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners
- ATO "Medicare levy surcharge income, thresholds and rates": web.archive.org/web/20260112000320/https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy-surcharge/medicare-levy-surcharge-income-thresholds-and-rates
- ATO "Low and middle income earner tax offsets": web.archive.org/web/20250404212639/https://www.ato.gov.au/forms-and-instructions/low-and-middle-income-earner-tax-offsets
- ATO "Study and training loan repayment thresholds and rates" (examples 1-4): web.archive.org/web/20251219160401/https://www.ato.gov.au/tax-rates-and-codes/study-and-training-support-loans-rates-and-repayment-thresholds
- ATO "Division 293 tax on concessional contributions by high-income earners": web.archive.org/web/20260215111033/https://www.ato.gov.au/individuals-and-families/super-for-individuals-and-families/super/growing-and-keeping-track-of-your-super/caps-limits-and-tax-on-super-contributions/division-293-tax-on-concessional-contributions-by-high-income-earners
- DSS Family Assistance Guide 3.6.1 (FTB A historical rates; "Last reviewed: 1 July 2025"): web.archive.org/web/2025id_/https://guides.dss.gov.au/family-assistance-guide/3/6/1
- DSS Family Assistance Guide 3.6.3 (FTB B historical rates; "Last reviewed: 1 July 2025"): web.archive.org/web/20251206031407/https://guides.dss.gov.au/family-assistance-guide/3/6/3
- OECD, Taxing Wages 2026, country chapter "Australia (2024-2025 income tax year)" (PP(S), ES, FTB description):
  web.archive.org/web/20260925013739/https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/australia-2024-2025-income-tax-year_f05427e5.html
- OECD Taxing Wages country tables: `~/cmp20/anglo/data/oecd/tw_cou_xdc_anglo.json` (same source as the kernel's
  `~/cmp20/harness/data/oecd/tw_cou_xdc.json`).

Literature for the loophole catalogue (identifiers; not fetched unless stated): Grattan Institute, "Hot property:
negative gearing and capital gains tax reform" (April 2016); Treasury, Tax Expenditures and Insights Statement;
Australia's Future Tax System Review ("Henry Review", 2010); ATO TR 2022/4 (s. 100A reimbursement agreements) and
PCG 2022/2; ATO TD 2022/11 (Division 7A, unpaid present entitlements); House of Representatives Standing Committee
on Economics, inquiry into the implications of removing refundable franking credits (2018-19).

## Files used (42)

| file | SHA-256 | where it came from |
|---|---|---|
| `refs/F2024L00664.docx` | `cd0ae028f2b522cfdae3b831f3f1c6f9c2410de4c8ced49d9249cb2c696f237b` | not recorded |
| `refs/F2024L00664.html` | `c3abc3d2885332f64e590738a0552dfbd02ef14200c0e4aafa7e28a963a42c19` | not recorded |
| `refs/F2024L00664.txt` | `62ed9a9752358020131b0108cda2ca4f5574ebcf5554a41bfd070346e1286bf5` | not recorded |
| `refs/F2025L00647.docx` | `d4fac5428d9e7cef7ecf837a5411acca6c05191a879033bc699b0eac0393e023` | not recorded |
| `refs/F2025L00647.txt` | `56d6c56b88ccfde7e0181f7dde322945c566ceb11c2ee7caee790f3649f83433` | not recorded |
| `refs/F2025L01016.docx` | `679fce75ca186f085ee42d3f2cf409375cdd49c028827ed2348166c9059a6ba9` | not recorded |
| `refs/F2025L01016.txt` | `9424dbf93eb71e0f704474851182691501d25144d37bce7b1bc2355c1b5fce85` | not recorded |
| `refs/MLA1986_2025-03-28.docx` | `0da9d0f6c840fe39fdad6b10bc736d300141ffdd06d05c0073fb092720193cdc` | not recorded |
| `refs/MLA1986_2026-07-01.html` | `a306696d3e1ad77ab10aee18c4771d390000bcdd43266798c6fe7c193e0c75bd` | not recorded |
| `refs/SOURCES.md` | `73c8da2978782422bcdcbd8441f57c667a348c1c7bd0bc2d27dbb9c51f7d3181` | site named in the notes: legislation.gov.au |
| `refs/ato_div293.html` | `ad3c792951c3c32df7c37fdaacfefbe7732cdeba46abe79649732a0ca252948d` | not recorded |
| `refs/ato_div293.txt` | `21a71c2ebad0864352c745d79b4cf09ebb7a9437b033d0051668e366f6a6ed9a` | not recorded |
| `refs/ato_help.html` | `a4ad164560167d91935b0063255d9ec250915f979a16c31cbea79c1645d9351f` | not recorded |
| `refs/ato_help.txt` | `d654e1741eae364eec9c090846ff7d13976e4b003191cbcb9b1a86d8495fe73a` | not recorded |
| `refs/ato_keysuper.html` | `f3966a852306e33f95ad3f5ac5bf186594453bd1e6135557984276c43573c203` | not recorded |
| `refs/ato_keysuper.txt` | `599d8d7492baa55b39e18efc48e5648845cc9506e82576e33476942e788215c0` | not recorded |
| `refs/ato_lito.html` | `e0c864b6e42189ff97df646412ac20d9e4343f1c68375e73363d01ca115dafec` | not recorded |
| `refs/ato_lito.txt` | `5e90e9929d7be81538817e82c5513b30c29ad879a4d4a0830b15d5bcdce64fa4` | not recorded |
| `refs/ato_ml_family.html` | `110954ed8a6e0e4e7bb51811e8aa0e741914e23e81490cfcface0cf8c9c75204` | not recorded |
| `refs/ato_ml_family.txt` | `7b303eaba5366be2ed30b21e2baf05c125aa581e186ef5d474c60e818d552dd1` | not recorded |
| `refs/ato_ml_low.html` | `2b7dada528f808f869216e697f41f12f8ec93325db8562e2ced63f6478d7c432` | not recorded |
| `refs/ato_ml_low.txt` | `ae99af553d6d858804d8c5839fde2157ac37947468bc0e220e5e9bf28fac2ad6` | not recorded |
| `refs/ato_mls_thresholds.html` | `9ba2be6bd2ff050811af5791be22ac683193ce9c6634294532cef6a8f4a587d8` | not recorded |
| `refs/ato_mls_thresholds.txt` | `7199a24bbfaeb45dd2d023b0184b1ccc6009d03ecdd1f18f54d58dfbd02e0e44` | not recorded |
| `refs/ato_rates.html` | `6af602ab983f77251edaa4c2a4935e735f323110cf8365e7f801b5717089dadc` | not recorded |
| `refs/ato_rates.txt` | `cbde0d3a1bfd630822be1c4b2cb14e305d0906581f919805fb9abe5d9bf97b94` | not recorded |
| `refs/ato_sapto.html` | `c45a7af4aa29d12a4e672c344b410b4820868447b9ca93a54d78d16bd1733889` | not recorded |
| `refs/ato_sapto.txt` | `c06f5818d83ddc8a5be2117b49ddbd215998d1ddada4d26c73aac221bcd30c38` | not recorded |
| `refs/dss_3_6_1.html` | `e9f4e997a8ee791c6b6c79912e71fc3890d755f722e57ca2f1a7087104c39358` | https://guides.dss.gov.au/family-assistance-guide/3/6/1 |
| `refs/dss_3_6_1.txt` | `82cd5c18f4fd8a10558df5cf7f1d635f64883b784474b8cba31701b70d35f3d8` | not recorded |
| `refs/dss_3_6_2.html` | `0e0e5adea466faf2b7e96cca5a9533731fe8b5fb0a8ad745db3c5c028778145d` | https://guides.dss.gov.au/family-assistance-guide/3/6/2 |
| `refs/dss_3_6_2.txt` | `cdeb16b46ed7163bc2edde2dd52c606f555f560e25b84915edcfb61224780d97` | not recorded |
| `refs/dss_3_6_3.html` | `67b1545682a7cecf674581ab8e4a40945e0bb2fbbd59b80e2d36e1f89b2ab4ac` | https://guides.dss.gov.au/family-assistance-guide/3/6/3 |
| `refs/dss_3_6_3.txt` | `d2b62581ae0c6886d99182b3493348a7eab6b4d402932445f67bb728c98bdfc4` | not recorded |
| `refs/dss_3_6_4.html` | `66cb49d8cd97ca3c6faf74abd5e829cee330390fc7e12fba34a71a22d0e1f7e4` | https://guides.dss.gov.au/family-assistance-guide/3/6/4 |
| `refs/dss_3_6_4.txt` | `5c6b4084cbd1b7d560084608be36121e9a4b858135d71e198e3ed3f3fc261d3b` | not recorded |
| `refs/oecd_tw2026_aus.html` | `955cb84d68453cb9f04a7597f0f0d25cb62157e91dc8cb071d583fe34ea31810` | https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/australia-2024-2025-income-tax-year_f05427e5.html |
| `refs/oecd_tw2026_aus.txt` | `66b1200fc5023a3af9efc96a0b4bf275ca7377daf82d141678402d8e72773c9d` | not recorded |
| `refs/oecd_tw_aus.html` | `a722b633dca97cfa388763f4aef4c2fe26d02cea63367df96508bc10c860d281` | not recorded |
| `refs/phi_mls.html` | `dc1d54dab6ec8c00f70137927504e4f222c8395f10760b6beecfcfa94e08249f` | not recorded |
| `refs/schedule1_sample_weekly_2024.json` | `9530787fc2ec77391d20f97376e153199bb2148dca8ef94c97c50ac6dfd64fd2` | not recorded |
| `refs/tw2026_fullreport.txt` | `8b44d77a12295c7d84463199164632c094e53105a67f693d2eb247e2042f8a5e` | not recorded |

## Addresses cited in the model and notes (0)

None beyond the files above.
