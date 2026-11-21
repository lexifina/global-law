# Sources: New Zealand (NZ)

The model in `lean/` cites the provision behind each rule in its comments. The law texts, official pages and tables it was built from are not copied into this repository: some were read from secondary hosts, and many publishers do not allow redistribution. Each file used is listed below with its SHA-256, so a copy fetched from the publisher can be checked against the one the model was built from. Paths are as they were in the build folder.

## Source notes written during the build

### Sources saved in refs/ (fetched 2026-11-19, sequential, >= 2 s apart)

Statute access: the Income Tax Act 2007 is not in the Global law corpus for New Zealand (50 acts; not the tax Acts).
legislation.govt.nz answers automated requests with an AWS WAF challenge (HTTP 202, empty body; WebFetch 403) and
NZLII with a Cloudflare challenge (403 "Just a moment..."). Neither is bypassed. Parameters are cited to Inland
Revenue's publications, which name the sections; the Accident Compensation Act 2001 is read in Global law
(official text: https://www.legislation.govt.nz/act/public/2001/0049/latest/whole.html).

| File | URL | What |
|---|---|---|
| ird_rates.txt | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/tax-codes-and-tax-rates-for-individuals/tax-rates-for-individuals | rates from 1 April 2025; 2024-25 composite rates; secondary codes |
| ird_ietc.txt | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/individual-tax-credits/independent-earner-tax-credit-ietc | IETC |
| wb_ftc_2025.txt | https://web.archive.org/web/20251014154310/https://www.ird.govt.nz/working-for-families/types/family-tax-credit | FTC 2025-26 (7,524 / 6,130; 42,700; 27 %) |
| wb_iwtc_2025.txt | http://web.archive.org/web/20250817002422/https://www.ird.govt.nz/working-for-families/types/in-work-tax-credit | IWTC 2025-26 (5,070; +780) |
| wb_mftc_2025.txt | http://web.archive.org/web/20251008092405/https://www.ird.govt.nz/working-for-families/types/minimum-family-tax-credit | MFTC 2025-26 (35,316) and the Jeremy example |
| ird_wff_*.txt | https://www.ird.govt.nz/working-for-families/types/... | current (2026-27) pages: FTC 7,921 / 6,454, 44,900, 27.5 %; IWTC 7,670 temporary |
| ir271-2026.pdf/.txt | https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir200---ir299/ir271/ir271-2026.pdf | IR271 July 2025: WFF weekly payments 1 April 2025 - 31 March 2026 |
| ir271-2025.pdf/.txt | .../ir271/ir-271-2025.pdf | IR271 April 2024 (2024-25, before the Budget) |
| ir271-2025-jul-2024.pdf/.txt | .../ir271/ir271-2025-jul-2024.pdf | IR271 July 2024 (2024-25 after the Budget) |
| ir340-2025.pdf/.txt | https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir300---ir399/ir340/ir340-2025.pdf | IR340 April 2025 weekly/fortnightly PAYE tables 2025-26 |
| spec2026_v8.pdf/.txt | https://www.ramco.com/hubfs/compliance-portal/payroll-calculations-and-business-rules-specification-2026-v8.pdf | IRD "Payroll Calculations & Business Rules Specification 1 April 2025 to 31 March 2026", v0.8, 03-02-2025 (an IRD document; copy hosted by a payroll vendor because IRD's site now serves only the 2026-27 edition and no archive copy exists) |
| spec2027.pdf/.txt | https://www.ird.govt.nz/-/media/project/ir/home/documents/digital-service-providers/software-providers/payroll-calculations-business-rules-specifications/payroll-calculations-and-business-rules-specification.pdf | the same, 2026-27 |
| sr_budget_2024.pdf/.txt | https://www.taxpolicy.ird.govt.nz/-/media/project/ir/tp/publications/2024/taxation-budget-measures-bill/special-report---taxation-budget-measures-act-2024.pdf | IRD Special report, Taxation (Budget Measures) Act 2024 (June 2024) |
| ../data/oecd/tw_cou_xdc_anglo.json | OECD SDMX (see family PROGRESS.md) | OECD Taxing Wages country table, NZL 2022-2025 |

## Files used (76)

| file | SHA-256 | where it came from |
|---|---|---|
| `refs/SOURCES.md` | `a8aa8e5f8fc61ee80d0db73e546ead8ce79df47a3069bb9dbd5cd1d3556267ea` | site named in the notes: legislation.govt.nz |
| `refs/ir271-2025-jul-2024.pdf` | `fe797b2a6503e1ad333182926c67777a3a510e0eae2843307dd47fa474add48f` | not recorded |
| `refs/ir271-2025-jul-2024.txt` | `8b0e9eae799753e432278af3c03b5126012b1802cc39fd837691c42b58159305` | not recorded |
| `refs/ir271-2025.pdf` | `5f2fcbcb4a2ca8cfcb224fc60f1724880406c6a36feec69f2b2c84cf0033bf8e` | not recorded |
| `refs/ir271-2025.txt` | `cddc03c0c5903d5780d9456c93e0f52a89d90bbcf975a5cfb509c26fba4195ac` | not recorded |
| `refs/ir271-2026.pdf` | `492cf9fc20111255c36d30f074946f5f21e337dca1fdb37d02697e3fab1b9d6f` | https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir200---ir299/ir271/ir271-2026.pdf |
| `refs/ir271-2026.txt` | `3b36017282d50b7f5de9a5d17acace71d38a3aa613c0fdf58e25cf7359a29c13` | not recorded |
| `refs/ir340-2025.pdf` | `47cac39d30ee58d5cfd2d9b6481c96b26f41196eb9ed6c1011268664bbe9ea6f` | https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir300---ir399/ir340/ir340-2025.pdf |
| `refs/ir340-2025.txt` | `18ef32b07d29930e9fb97e5b9fb13d0dd9516f4979f8c7ea9b5f21bddae94e33` | not recorded |
| `refs/ird_acc.html` | `8dbe6c21ef2866717b39f5318bf57737becf57611f71dffa91e2ca37be1317cd` | https://www.ird.govt.nz/404 |
| `refs/ird_acc.txt` | `81f968c853c8ff1743840d5f9cb1b3efd2c2152f1401c45d2d751fa822d149d2` | not recorded |
| `refs/ird_acc_rates.html` | `b4816696c9ccbdefba1e9407dc8d4fc73f9b1fa2f15e41bc333e24a773e5a16f` | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/acc-clients-and-carers/acc-earners-levy-rates |
| `refs/ird_acc_rates.txt` | `69c0470cabb812f0d7753dec72cb0a984afb4113dd3a3e72f6586dc208ed4073` | not recorded |
| `refs/ird_attribution.html` | `f69816a5e2f2e7de2bffb3c593b97de8e2484f6b6cdde5f8b4e3b03bdbe9eafa` | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/how-income-is-taxed/attribution-rule-for-income-from-personal-services |
| `refs/ird_attribution.txt` | `fa9f0bf3fb2a4674ce7fe809cbbcc5747227f4cde90679cb5dad1cbbd2455197` | not recorded |
| `refs/ird_brightline.html` | `824d036b04f0c7d2b61d2531700e382e6da3c398346d0921ca55491c9fec100c` | https://www.ird.govt.nz/404 |
| `refs/ird_brightline.txt` | `574b89a751a67c21cb32303b4f5ec47b99bdcc63e17f53087f53f872fb073856` | not recorded |
| `refs/ird_donation.html` | `3e6174156835a96f1d15a9418c6f64ca30bd70c5fdeefdfea3236e5e63d46581` | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/individual-tax-credits/donation-tax-credits |
| `refs/ird_donation.txt` | `266a16f105d82cb30924860cb45189b7a3bc699a6e014ee47ef4af9f02c3dad3` | not recorded |
| `refs/ird_family_income.html` | `c03108050bdd7a9af9305b9532a7cc63ba35dae401ba870ecf2f79e845361777` | https://www.ird.govt.nz/working-for-families/all-about-working-for-families/working-out-your-family-income |
| `refs/ird_family_income.txt` | `b59091cde6982dd4772bf5ee1a29d4eb102a071aa3b3fd1b945d7fad3f00c103` | not recorded |
| `refs/ird_hwi.html` | `a6703f79225223e3323a45a28620d43805237bb5819c30485f075d0a1c2a9d82` | https://www.ird.govt.nz/about-us/who-we-are/organisation-structure/significant-enterprises/high-wealth-individuals-research-project |
| `refs/ird_hwi.txt` | `ec34f786b61238ba2ab337e2484382692a9b03ba638306b5a4a5a0d43843edee` | not recorded |
| `refs/ird_ietc.html` | `9c5239e168879b2e894723b53bcbe708f98c8c15e1235f53afecd0f493c118a4` | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/individual-tax-credits/independent-earner-tax-credit-ietc |
| `refs/ird_ietc.txt` | `70736942472da17215d3955fec87792ca9e8024ed8d814d64b8dfd339c9d6233` | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/individual-tax-credits/independent-earner-tax-credit-ietc |
| `refs/ird_imputation.html` | `7c8f6640718945184ffce7b9d00e3e259bef06db86a46b16309f2195619b847d` | https://www.ird.govt.nz/404 |
| `refs/ird_imputation.txt` | `574b89a751a67c21cb32303b4f5ec47b99bdcc63e17f53087f53f872fb073856` | not recorded |
| `refs/ird_iwtc2026.html` | `4308a79a41aec328bbaf0ee8f74ea92eb6f346bca80f02b8cdfcfd9ad6eba0dc` | https://www.ird.govt.nz/updates/news-folder/2026/in-work-tax-credit-increase-from-1-april |
| `refs/ird_ltc.html` | `312be9a6a450396f848faaad1431b96fcc5c8f2dcd4a3161272c07911f997ba9` | https://www.ird.govt.nz/income-tax/income-tax-for-businesses-and-organisations/income-tax-for-companies/look-through-companies |
| `refs/ird_ltc.txt` | `fe7675b548ff46fce21d2bee44d1986890fa514a9ff5537415f5e76e23dc0a00` | not recorded |
| `refs/ird_max_imputation.html` | `f0a9669fad7856de78f0b4219ec91028ad1580b307b9a7ecf407698d19ff1e8a` | https://www.ird.govt.nz/income-tax/income-tax-for-businesses-and-organisations/income-tax-for-companies/imputation-for-companies/how-imputation-credits-work/maximum-imputation-ratio |
| `refs/ird_max_imputation.txt` | `e12559f1938673d8ca10744f8c13b14e6a40acb3fa989e1782a21ec2fa31f25e` | not recorded |
| `refs/ird_payroll_spec.html` | `02b32dd748467604313a754ac37159a99374ac81fc7d0b1da28654ab9b13f86e` | https://www.ird.govt.nz/digital-service-providers/services-catalogue/returns-and-information/payday-filing/payroll-calculations-and-business-rules |
| `refs/ird_pir.html` | `95df57df4e6112ef1bdc2f135baa8e83b0d93f462c550344f66b4ddc713baf24` | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/types-of-individual-income/portfolio-investment-entity-income-for-individuals/prescribed-investor-rates/find-my-prescribed-investor-rate |
| `refs/ird_pir.txt` | `b3340defb9c5027ab1989038060067e84f9604fe2d347fabb6900f08d2c8feca` | not recorded |
| `refs/ird_pir_rates.html` | `510d4fe15175f41c984ea6acd4d6e949973eb687f7c03a9a18a24e55b2065c8c` | https://www.ird.govt.nz/404 |
| `refs/ird_pir_rates.txt` | `574b89a751a67c21cb32303b4f5ec47b99bdcc63e17f53087f53f872fb073856` | not recorded |
| `refs/ird_rates.html` | `7c43968b3253c08e7ae545ad1769952a5be0cf956f73dc785df837dac247ac90` | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/tax-codes-and-tax-rates-for-individuals/tax-rates-for-individuals |
| `refs/ird_rates.txt` | `4908393993f1b45b9d3738a360af0fd340c84eaae1c8e946ce2cb66dcc3b2bf4` | https://www.ird.govt.nz/income-tax/income-tax-for-individuals/tax-codes-and-tax-rates-for-individuals/tax-rates-for-individuals |
| `refs/ird_sitemap.xml` | `9f1311a470e235d9dfb62e404017b8caf8c9889d4d19d285845368cc2a8c8ebf` | not recorded |
| `refs/ird_sl.html` | `d88b14859393bcafe6a10fcfe5fe223b4908ef0110d52f0ba6a5fad255a49bf1` | https://www.ird.govt.nz/404 |
| `refs/ird_sl.txt` | `81f968c853c8ff1743840d5f9cb1b3efd2c2152f1401c45d2d751fa822d149d2` | not recorded |
| `refs/ird_trust_rate.html` | `3fa828f8df994b688e4916fe566872ef1d153440bc334acc140c9c7e814a4af9` | https://www.ird.govt.nz/404 |
| `refs/ird_trust_rate.txt` | `574b89a751a67c21cb32303b4f5ec47b99bdcc63e17f53087f53f872fb073856` | not recorded |
| `refs/ird_trustee_rate2.html` | `c0c8cd3a14e3fecee53ff67661f0bdaa76249f2ba6aea5350471563cfd85eb3e` | https://www.ird.govt.nz/404 |
| `refs/ird_trustee_rate2.txt` | `574b89a751a67c21cb32303b4f5ec47b99bdcc63e17f53087f53f872fb073856` | not recorded |
| `refs/ird_trustee_rates.html` | `278880a95b5db334c63cfc0e1275c7c66f698e1ae84db557c1b131178d149c73` | https://www.ird.govt.nz/income-tax/income-tax-for-businesses-and-organisations/trusts-and-estates/income/trustee-tax-rates |
| `refs/ird_trustee_rates.txt` | `9d8506eb6ba04875ccca4c95f6022281d4961917e48f495277e37ce6dbcbf713` | not recorded |
| `refs/ird_urls.txt` | `637f13199c3842f7dbd6d0a4281ed8e0c33e1a09d0a43dbbad5d78c63b54f9a3` | not recorded |
| `refs/ird_wff.html` | `4484acdcd7213a753c0b11b6c168f12e0ee674c1d810c7c44291d20f5362e499` | https://www.ird.govt.nz/working-for-families |
| `refs/ird_wff.txt` | `493ce5d3ff7c23398eb054ed3d9072687627c9cdad0b2fb45297ea65e514364b` | not recorded |
| `refs/ird_wff_all.html` | `eddc26f789e9cd38cae10810761d08dfbcf580e37ed889bae48086f2ca47f74a` | https://www.ird.govt.nz/working-for-families/all-about-working-for-families |
| `refs/ird_wff_best-start.html` | `e312f8e9a77a97950f21472a152305d08b17ae03c707120ca6979ef6d9760e1b` | https://www.ird.govt.nz/working-for-families/types/best-start |
| `refs/ird_wff_best-start.txt` | `630e3e478df40f05a4259eaecdb9a8b007a2311dda3b6327a9ba5acb89f16a7d` | not recorded |
| `refs/ird_wff_est.html` | `2ec1376e497bf375e077e7f189d71c1fc24bf0ea9b2331edb38a44d22d55e7ac` | https://www.ird.govt.nz/working-for-families/estimate-your-entitlement |
| `refs/ird_wff_family-tax-credit.html` | `34f183376026198bff8f56a70340666e9f56aa7a19086375d47eaaf841721595` | https://www.ird.govt.nz/working-for-families/types/family-tax-credit |
| `refs/ird_wff_family-tax-credit.txt` | `1740ab50fb3c588821201f38eb22627513bdbe899caa4f9b48b9f1bae14d6f18` | not recorded |
| `refs/ird_wff_in-work-tax-credit.html` | `f1fdc3d6cb249d453c1db3b7bd81167c15ced08627d50f652d8b55f22787fcef` | https://www.ird.govt.nz/working-for-families/types/in-work-tax-credit |
| `refs/ird_wff_in-work-tax-credit.txt` | `c50344c7f82bd193b30eb45778b3dbf86abbfec700b368b3e8566b6569b4bd76` | not recorded |
| `refs/ird_wff_minimum-family-tax-credit.html` | `8e1ce82a69ac8cb316eadc0ce0fe9b536327c78d66e472b132c0900c45e96433` | https://www.ird.govt.nz/working-for-families/types/minimum-family-tax-credit |
| `refs/ird_wff_minimum-family-tax-credit.txt` | `84e9e9ee6a104b1df1e584b367e1c0e86d1b9c56306643430326804820dc45b8` | not recorded |
| `refs/ird_wff_types.html` | `93001153bc4dc42f5d9f2df3f8b3b53151bd81642f9f462c1380ed10739a3da7` | https://www.ird.govt.nz/working-for-families/types |
| `refs/spec2026_v8.pdf` | `1d2cb4e3a1066384db6026899a7b303f3b3feba05d8b7c9d8e3d1286cf11a856` | https://www.ramco.com/hubfs/compliance-portal/payroll-calculations-and-business-rules-specification-2026-v8.pdf |
| `refs/spec2026_v8.txt` | `291d20fada898d4dd5a299a4b3909f49b1a9e57bb9d17ecd638405ac769ffdb7` | not recorded |
| `refs/spec2027.pdf` | `4fb1c1ecc760ad7fe7dc912904c76522dee29b282dc9217afeb9b266d9af1dc7` | https://www.ird.govt.nz/-/media/project/ir/home/documents/digital-service-providers/software-providers/payroll-calculations-business-rules-specifications/payroll-calculations-and-business-rules-specification.pdf |
| `refs/spec2027.txt` | `253feb89ae8603b30fe01724d7cb7b03089ce8b42da10513792b0ef0101342db` | not recorded |
| `refs/sr_budget_2024.pdf` | `1b1e3b4927397843ba8a9e86ebbe3488a6d8b8b102957e5c947bf10daad4982d` | https://www.taxpolicy.ird.govt.nz/-/media/project/ir/tp/publications/2024/taxation-budget-measures-bill/special-report---taxation-budget-measures-act-2024.pdf |
| `refs/sr_budget_2024.txt` | `49c68da843d614da203d842d2c9d203041b947412f4d035ff77e3b53e39838c0` | not recorded |
| `refs/tp_sr_2024.html` | `2bedee7ea14ebb6fa4a8c5525a892cd909a542c33e70d09798f09529faa2463b` | https://www.taxpolicy.ird.govt.nz/publications/2024/sr-taxation-budget-measures-2024 |
| `refs/tp_sr_2024.txt` | `1981db8526820e7672d2358735d8a805a191eabfb28f7f286f3bc5c2b03cddaa` | not recorded |
| `refs/wb_ftc_2025.html` | `fcaa26d801532d5b5640389fc6a6d0f1bd65ca71d1b2138eb67bf6e9f0454459` | https://web.archive.org/web/20251014154310/https://www.ird.govt.nz/working-for-families/types/family-tax-credit |
| `refs/wb_ftc_2025.txt` | `ecc0d08ea04dcb77c10ebb503d0a405f3c3adf1ffd5b2a6efebbfe3192c259fa` | https://web.archive.org/web/20251014154310/https://www.ird.govt.nz/working-for-families/types/family-tax-credit |
| `refs/wb_iwtc_2025.html` | `5f30828ca7c3e46d2d89438a4e8a8d1784002c3ad7311a326b31cc95d9bbfa1b` | http://web.archive.org/web/20250817002422/https://www.ird.govt.nz/working-for-families/types/in-work-tax-credit |
| `refs/wb_iwtc_2025.txt` | `ded6f9d287e73a452e07c858733ef29c92155ca1fc2de41c73d9ae5361a156e9` | http://web.archive.org/web/20250817002422/https://www.ird.govt.nz/working-for-families/types/in-work-tax-credit |
| `refs/wb_mftc_2025.html` | `f643bcbc457c88fa660a1141f9de2bc7d8194bd001751910258bc95314af6d7d` | http://web.archive.org/web/20251008092405/https://www.ird.govt.nz/working-for-families/types/minimum-family-tax-credit |
| `refs/wb_mftc_2025.txt` | `559d47217c4c65d6df26d080e6cfcd45adaee9d353f2f3285837ab33c800884e` | http://web.archive.org/web/20251008092405/https://www.ird.govt.nz/working-for-families/types/minimum-family-tax-credit |

## Addresses cited in the model and notes (0)

None beyond the files above.
