# Japanese statutes used by the model

The model was written from the statutes' official XML, fetched from the e-Gov 法令API v2 at the dates below with
`../scripts/fetch_law.py` (`https://laws.e-gov.go.jp/api/2/law_data/<law_id>?asof=<date>`). The XML files (143 MB) are
not copied here: each `<file>.info.json` records the request and the version e-Gov returned, and the table lists them.
`txt/` holds the plain-text extracts of the provisions and tables the Lean files were written from (所得税法 第21条ほか,
別表第二, 別表第五).

| File | Law | As of | Revision | Current text |
|---|---|---|---|---|
| `chihozeiho_2025-12-31` | 地方税法 (昭和二十五年法律第二百二十六号) | 2025-12-31 | `325AC0000000226_20251212_507AC0000000087` | [e-Gov](https://laws.e-gov.go.jp/law/325AC0000000226) |
| `chihozeiho_2026-06-01` | 地方税法 (昭和二十五年法律第二百二十六号) | 2026-06-01 | `325AC0000000226_20260525_506AC0000000052` | [e-Gov](https://laws.e-gov.go.jp/law/325AC0000000226) |
| `chihozeiho_rei_2026-06-01` | 地方税法施行令 (昭和二十五年政令第二百四十五号) | 2026-06-01 | `325CO0000000245_20260521_508CO0000000038` | [e-Gov](https://laws.e-gov.go.jp/law/325CO0000000245) |
| `choshuho_2025-12-31` | 労働保険の保険料の徴収等に関する法律 (昭和四十四年法律第八十四号) | 2025-12-31 | `344AC0000000084_20251001_506AC0000000026` | [e-Gov](https://laws.e-gov.go.jp/law/344AC0000000084) |
| `dc_rei_2025-12-31` | 確定拠出年金法施行令 (平成十三年政令第二百四十八号) | 2025-12-31 | `413CO0000000248_20250601_507CO0000000193` | [e-Gov](https://laws.e-gov.go.jp/law/413CO0000000248) |
| `fukko_2025-12-31` | 東日本大震災からの復興のための施策を実施するために必要な財源の確保に関する特別措置法 (平成二十三年法律第百十七号) | 2025-12-31 | `423AC0000000117_20250601_504AC0000000068` | [e-Gov](https://laws.e-gov.go.jp/law/423AC0000000117) |
| `hasu_2025-12-31` | 国等の債権債務等の金額の端数計算に関する法律 (昭和二十五年法律第六十一号) | 2025-12-31 | `325AC0000000061_20101001_422AC0000000015` | [e-Gov](https://laws.e-gov.go.jp/law/325AC0000000061) |
| `jidoteate_2025-12-31` | 児童手当法 (昭和四十六年法律第七十三号) | 2025-12-31 | `346AC0000000073_20250601_504AC0000000068` | [e-Gov](https://laws.e-gov.go.jp/law/346AC0000000073) |
| `kenpo_2025-12-31` | 健康保険法 (大正十一年法律第七十号) | 2025-12-31 | `211AC0000000070_20251212_507AC0000000087` | [e-Gov](https://laws.e-gov.go.jp/law/211AC0000000070) |
| `kounen_2025-12-31` | 厚生年金保険法 (昭和二十九年法律第百十五号) | 2025-12-31 | `329AC0000000115_20251201_507AC0000000074` | [e-Gov](https://laws.e-gov.go.jp/law/329AC0000000115) |
| `kounen_grade_rei_2025-12-31` | 厚生年金保険法の標準報酬月額の等級区分の改定等に関する政令 (令和二年政令第二百四十六号) | 2025-12-31 | `502CO0000000246_20200901_000000000000000` | [e-Gov](https://laws.e-gov.go.jp/law/502CO0000000246) |
| `shinrin_2026-06-01` | 森林環境税及び森林環境譲与税に関する法律 (平成三十一年法律第三号) | 2026-06-01 | `431AC0000000003_20260401_508AC0000000002` | [e-Gov](https://laws.e-gov.go.jp/law/431AC0000000003) |
| `shotokuzeiho_2025-11-30` | 所得税法 (昭和四十年法律第三十三号) | 2025-11-30 | `340AC0000000033_20251001_506AC0000000026` | [e-Gov](https://laws.e-gov.go.jp/law/340AC0000000033) |
| `shotokuzeiho_2025-12-31` | 所得税法 (昭和四十年法律第三十三号) | 2025-12-31 | `340AC0000000033_20251218_507AC0000000013` | [e-Gov](https://laws.e-gov.go.jp/law/340AC0000000033) |
| `shotokuzeiho_2026-06-01` | 所得税法 (昭和四十年法律第三十三号) | 2026-06-01 | `340AC0000000033_20260401_508AC0000000012` | [e-Gov](https://laws.e-gov.go.jp/law/340AC0000000033) |
| `shotokuzeiho_rei_2025-12-31` | 所得税法施行令 (昭和四十年政令第九十六号) | 2025-12-31 | `340CO0000000096_20251201_507CO0000000120` | [e-Gov](https://laws.e-gov.go.jp/law/340CO0000000096) |
| `sochiho_2025-11-30` | 租税特別措置法 (昭和三十二年法律第二十六号) | 2025-11-30 | `332AC0000000026_20251121_507AC0000000013` | [e-Gov](https://laws.e-gov.go.jp/law/332AC0000000026) |
| `sochiho_2025-12-31` | 租税特別措置法 (昭和三十二年法律第二十六号) | 2025-12-31 | `332AC0000000026_20251231_507AC1000000081` | [e-Gov](https://laws.e-gov.go.jp/law/332AC0000000026) |
| `sochiho_2026-06-01` | 租税特別措置法 (昭和三十二年法律第二十六号) | 2026-06-01 | `332AC0000000026_20260501_508AC0000000012` | [e-Gov](https://laws.e-gov.go.jp/law/332AC0000000026) |
| `sochiho_rei_2025-12-31` | 租税特別措置法施行令 (昭和三十二年政令第四十三号) | 2025-12-31 | `332CO0000000043_20251231_507CO0000000401` | [e-Gov](https://laws.e-gov.go.jp/law/332CO0000000043) |
| `tsusokuho_2025-12-31` | 国税通則法 (昭和三十七年法律第六十六号) | 2025-12-31 | `337AC0000000066_20251001_505AC0000000053` | [e-Gov](https://laws.e-gov.go.jp/law/337AC0000000066) |
