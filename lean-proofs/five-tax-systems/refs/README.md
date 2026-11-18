# Sources not copied here

The models were written from the statutes and checked against the documents, data and programs below. They are
other publishers' work (or too large), so they are listed rather than copied. Each document says which page,
table or section a figure came from.

## Germany

| Source | Where |
|---|---|
| EStG, SolZG 1995, EStDV, BKGG, SGB III, IV, V, VI and XI, and three 2025 instruments on contribution ceilings and rates (`svbezgrv_2025`, `rvbeitrsbek_2025`, `pbav_2025`): XML of gesetze-im-internet.de, downloaded 2026-11-18. The provisions the model uses are in [`../de/law/2025`](../de/law/2025) | [estg](https://www.gesetze-im-internet.de/estg/), [solzg_1995](https://www.gesetze-im-internet.de/solzg_1995/), [estdv_1955](https://www.gesetze-im-internet.de/estdv_1955/), [bkgg_1996](https://www.gesetze-im-internet.de/bkgg_1996/), [sgb_3](https://www.gesetze-im-internet.de/sgb_3/), [sgb_4](https://www.gesetze-im-internet.de/sgb_4/), [sgb_5](https://www.gesetze-im-internet.de/sgb_5/), [sgb_6](https://www.gesetze-im-internet.de/sgb_6/), [sgb_11](https://www.gesetze-im-internet.de/sgb_11/), [svbezgrv_2025](https://www.gesetze-im-internet.de/svbezgrv_2025/), [rvbeitrsbek_2025](https://www.gesetze-im-internet.de/rvbeitrsbek_2025/), [pbav_2025](https://www.gesetze-im-internet.de/pbav_2025/) |
| Single provisions read for the loophole search (EStG §§ 3b, 8, 9, 10, 22, 23, 32a for 2026, 32b, 33, 34, 34g, 35a; BEEG §§ 2, 2c, 2e, 2f; SGB V § 10; SvEV § 1) | `https://www.gesetze-im-internet.de/<law>/__<section>.html`, e.g. [EStG § 32a](https://www.gesetze-im-internet.de/estg/__32a.html), [BEEG § 2](https://www.gesetze-im-internet.de/beeg/__2.html), [SGB V § 10](https://www.gesetze-im-internet.de/sgb_5/__10.html), [SvEV § 1](https://www.gesetze-im-internet.de/svev/__1.html) |
| BMF Steuerrechner: PAP pseudo-code (XML) and flow chart, the external calculator interface (the 644 cases were asked of it 61 s apart), the tariff history | [pseudocodes](https://www.bmf-steuerrechner.de/interface/pseudocodes.xhtml), [Programmablauf](https://www.bmf-steuerrechner.de/interface/programmablauf.xhtml), [interface](https://www.bmf-steuerrechner.de/interface/einganginterface.xhtml), [Tarifhistorie (2025-10-14)](https://www.bmf-steuerrechner.de/javax.faces.resource/2025_10_14_Tarifhistorie_Steuerrechner.pdf.xhtml) |
| BMF: Programmablaufplan 2025 (22.11.2024 and the amended version of 22.1.2025) | [PAP 2025](https://www.bundesfinanzministerium.de/Content/DE/Downloads/Steuern/Steuerarten/Lohnsteuer/Programmablaufplan/2024-11-22-PAP-2025.html), [amended PAP 2025](https://www.bundesfinanzministerium.de/Content/DE/Downloads/Steuern/Steuerarten/Lohnsteuer/Programmablaufplan/2025-01-22-geaenderte-PAP-2025.html) |
| BMF: Datensammlung zur Steuerpolitik 2026 (Tab. 2.4.1, 2.5.2, 2.6, 2.8.3) | [PDF](https://www.bundesfinanzministerium.de/Content/DE/Downloads/Broschueren_Bestellservice/datensammlung-zur-steuerpolitik-2026.pdf?__blob=publicationFile&v=4) |
| Deutscher Bundestag, Wissenschaftliche Dienste, WD 4 - 3000 - 065/24 (the child-by-child Günstigerprüfung) | [Analysen der Wissenschaftlichen Dienste](https://www.bundestag.de/dokumente/analysen) |
| GETTSIM 1.3.2 (the independent model; installed from PyPI, not copied) | [PyPI](https://pypi.org/project/gettsim/1.3.2/), [source](https://github.com/iza-institute-of-labor-economics/gettsim) |

## Japan

| Source | Where |
|---|---|
| Statutes and orders (XML, e-Gov 法令API v2) | [`../jp/law/README.md`](../jp/law/README.md) lists every law, date and revision |
| NTA タックスアンサー No. 1130, 1150, 1171, 1180, 1191, 1195, 1199, 1250, 1410, 1411, 1600, 2260 | `https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/<No>.htm`, e.g. [No. 2260](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2260.htm) |
| NTA, 令和7年分 年末調整のしかた (the printed 別表第五 copy, worked examples, 設例 pp. 57–58) | [年末調整のしかた](https://www.nta.go.jp/publication/pamph/gensen/nencho2025/01.htm) |
| NTA, 源泉徴収税額表 (令和7年分 and 令和6年分) | [令和7年分](https://www.nta.go.jp/taxes/tetsuzuki/shinsei/annai/gensen/zeigakuhyo2025/02.htm), [令和6年分](https://www.nta.go.jp/taxes/tetsuzuki/shinsei/annai/gensen/zeigakuhyo2024/02.htm) |
| 全国健康保険協会 (協会けんぽ), 令和6年度 and 令和7年度 保険料額表, 東京 | [kyoukaikenpo.or.jp](https://www.kyoukaikenpo.or.jp/) |
| 厚生労働省, 雇用保険料率 (令和6年度, 令和7年度) | [雇用保険料率](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000108634.html) |
| こども家庭庁, 児童手当 | [児童手当](https://www.cfa.go.jp/policies/kokoseido/jidouteate/) |
| 総務省, 個人住民税 | [個人住民税](https://www.soumu.go.jp/main_sosiki/jichi_zeisei/czaisei/czaisei_seido/150790_06.html) |
| OpenFisca-Japan v2.2.0 (referee B; not copied) | [project-inclusive/OpenFisca-Japan at 1f8d13d](https://github.com/project-inclusive/OpenFisca-Japan/tree/1f8d13dbe735b064373fe67377859454dd750b9c) |

## United Kingdom

The legislation, GOV.UK guidance and HMRC test data the UK model used are fetched by the scripts in
[`../../official-checks/uk-model/harness`](../../official-checks/uk-model/harness) (`fetch_leg.sh`, `fetch_leg2.sh`,
`fetch_govuk.sh`), which name every URL. The legislation.gov.uk XML is not copied: link to the point-in-time pages
instead, as [`../../official-checks/hmrc-tax-kalculator/refs/README.md`](../../official-checks/hmrc-tax-kalculator/refs/README.md)
does. PolicyEngine-UK 2.179.1 was the referee: [PolicyEngine/policyengine-uk](https://github.com/PolicyEngine/policyengine-uk).

## The comparison

| Source | Where |
|---|---|
| OECD, Taxing Wages 2026 (22 April 2026), year 2025: country tables, decomposition and marginal rates (SDMX). The figures for the five countries are in [`../shared/oecd_taxing_wages_2025.json`](../shared/oecd_taxing_wages_2025.json), [`../compare/data/oecd/tw_cou_xdc.json`](../compare/data/oecd/tw_cou_xdc.json) and [`../compare/data/oecd/tw_marginal_2025.json`](../compare/data/oecd/tw_marginal_2025.json); the raw CSV and structure files are not copied | [publication](https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en.html), [SDMX query](https://sdmx.oecd.org/public/rest/data/OECD.CTP.TPS,DSD_TAX_WAGES_COU@DF_TW_COU,/USA+FRA+GBR+DEU+JPN......A?startPeriod=2022) |
| World Bank WDI: PPP conversion factors (PA.NUS.PRVT.PP, PA.NUS.PPP) and exchange rates (PA.NUS.FCRF), 2025; the values used are in [`../compare/data/params.json`](../compare/data/params.json) | [PA.NUS.PRVT.PP](https://api.worldbank.org/v2/country/USA;FRA;GBR;DEU;JPN/indicator/PA.NUS.PRVT.PP?format=json&date=2025), [PA.NUS.PPP](https://api.worldbank.org/v2/country/USA;FRA;GBR;DEU;JPN/indicator/PA.NUS.PPP?format=json&date=2025), [PA.NUS.FCRF](https://api.worldbank.org/v2/country/USA;FRA;GBR;DEU;JPN/indicator/PA.NUS.FCRF?format=json&date=2025) |
| DGFiP, simulateur de l'impôt sur le revenu (calc-2026.cgi, calc-2025.cgi), asked twice for the OECD's two-earner family; its answers are in [`../compare/refs/dgfip`](../compare/refs/dgfip) | [simulateur](https://simulateur-ir-ifi.impots.gouv.fr/cgi-bin/calc-2026.cgi) |
| France's and the US's other sources | the reports of [`../../FrTax`](../../FrTax/reports) and [`../../TaxCode`](../../TaxCode) |
