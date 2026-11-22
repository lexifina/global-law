S = dict(cc="KR", family_name="5111 부가가치세, 5121 담배소비세·지방교육세",
doc=r'''# South Korea 2025: value added tax (5111), tobacco consumption tax and its local education tax (5121)

Sources: law.go.kr (국가법령정보센터) texts saved in `kr/law/lawgo/` (sha256 in `SHA256SUMS`). The site served the
current versions (부가가치세법 시행 2026-01-02, 지방세법 시행 2026-07-01); the articles used carry their amendment notes:
* **부가가치세법 제30조**: "부가가치세의 세율은 10퍼센트로 한다" (unchanged since the 2013 recodification).
* **제26조 ①** (<개정 … 2024. 12. 31.>, so the 2025 wording): exempt 1. unprocessed food, 2. tap water, 5. medical and
  health services, 6. education services, 7. passenger transport (air, express and chartered buses, taxis, high-speed
  rail excepted), 8. books, newspapers, magazines, 11. financial and insurance services, 12. letting of housing.
* **지방세법 제52조 ① 1. 가.** 담배소비세 "제1종 궐련: 20개비당 1,007원"; **제151조 ① 4.** 지방교육세 "담배소비세액의
  1만분의 4,399".
The 2026 texts are used as the 2025 texts for these provisions (grade B for the tobacco taxes: the version in force on
2025-07-01 was not fetched; law.go.kr's version walk did not answer).''',
vat=dict(name="부가가치세", standard=1000, statute="부가가치세법 제30조 (10퍼센트), 제26조 ①",
  classes={"food":"exempt","water":"exempt","health":"exempt","education":"exempt","transport":"exempt","books":"exempt",
           "newspapers":"exempt","financial":"exempt","insurance":"exempt","rent":"exempt"}),
extra_lean=r'''def tobacco (xs : List Spend) : List Charge :=
  (xs.filter (·.good == .cigarettes)).flatMap fun s =>
    let dambae := divR .down (s.quantity * 1007) (20 * 1000)
    [charge .excise "담배소비세" s.quantity id (fun _ => dambae) (event := "cigarettes") (level := .local) (bearer := .consumer)
       (statute := "지방세법 제52조 ① 1. 가. (20개비당 1,007원)"),
     charge .excise "지방교육세 (담배소비세분)" dambae id (fun x => divR .down (x * 4399) BP) (event := "cigarettes")
       (level := .local) (bearer := .consumer) (statute := "지방세법 제151조 ① 4. (담배소비세액의 1만분의 4,399)")]''',
extra_run=["tobacco g.consumption"], extra_covers=[".excise"],
notes=["KR 5111/5121: law.go.kr texts (current versions, amendment notes checked)"],
unsupported=[[["food"], "food taken as unprocessed (exempt, 부가가치세법 제26조 ① 1.); processed food is taxable at 10 %"],
  [["cigarettes"], "개별소비세 on cigarettes (개별소비세법 별표) and 국민건강증진부담금 not modelled"],
  [["petrol","diesel"], "교통·에너지·환경세 (statutory 475 / 340 won per litre, flexible rates by decree with 2025 temporary cuts), 주행분 자동차세 and 교육세 not modelled"],
  [["beer","wine","spirits"], "주세 and 교육세 on liquor not modelled"]],
guards=["vat.embedded { good := .clothing, amount := 11000 } == 1000","vat.embedded { good := .rent, amount := 11000 } == 0",
  "(tobacco [{ good := .cigarettes, amount := 4500, quantity := 20000 }]).map (·.due) == [1007, 442]"],
taxes=[{"oecd":"5111","tax":"부가가치세","statute":"부가가치세법 제26조 ①, 제30조","dated":"law.go.kr current text; 제26조 last amended 2024-12-31, 제30조 unchanged","grade":"A","kernel_parts":["Vat"],"unsupported":["간이과세자 (simplified taxpayers)","processed vs unprocessed food"]},
 {"oecd":"5121","tax":"담배소비세, 지방교육세 (담배소비세분)","statute":"지방세법 제52조 ① 1. 가., 제151조 ① 4.","dated":"law.go.kr version in force 2026-07-01 (2025 version not fetched)","grade":"B","kernel_parts":["charge"],"unsupported":["개별소비세 on cigarettes, 국민건강증진부담금","fuel (교통·에너지·환경세: decree rates), liquor (주세)"]}])

# ---- R3 session 7 (2026-11-21): vehicle taxes (5200), kernel 2.5.0 VehicleTax. 지방세법 (law.go.kr text of the version in
# force 2026-07-01, kr/law/lawgo/지방세법_20260701.*; art. 127 (1) carries no amendment after 2011-12-02 and art. 151 (1) none
# after 2021-12-28, so the same text applies in 2025). The art. 127 tables are images; their official alt text was read.
# Pre-change copy: tools/bak7/KR_cons.py.
S["imports"] = S.get("imports", []) + (["TaxKernel.Global2"] if "TaxKernel.Global2" not in S.get("imports", []) else [])
S["doc"] = S["doc"] + r'''

**Vehicle taxes (5200, session 7, grade A; kernel `VehicleTax`)**: 지방세법 (law.go.kr):
* **art. 127 (1) 1** 자동차세 on passenger cars (비영업용): displacement × won per cc by band: up to 1,000 cc 80; up to
  1,600 cc 140; above 1,600 cc 200 (the rate of the band applies to the whole displacement); **(1) 2**: non-commercial
  cars aged 3 years or more: each half-year amount = A/2 - (A/2 × 5/100)(n - 2), n = 차령 (2 ≤ n ≤ 12, older counted as
  12), so the year's tax is A × (1 - 0.05 (n - 2)); **(1) 3** other passenger cars (no displacement: electric, hydrogen)
  100,000 won (비영업용); **(3)**: a local government may set up to 50 % more by ordinance (standard rates applied).
* **arts. 150, 151 (1) 7** 지방교육세: 30 % of the 자동차세 payable.
* 차령 is defined by the Enforcement Decree (not read): taken as the tax year less the year of first registration plus 1.
* Art. 130 / 128 (5): part-year ownership by days; modelled by months held (kernel `months`).'''
S["extra_lean"] = S.get("extra_lean", "") + r'''

/-- 지방세법 art. 127 (1) 2: 차령 n = age + 1; factor 1 - 0.05 (n - 2) for 3 ≤ n ≤ 12 (age 2 .. 11), 50 % from n = 12. -/
def krAge : List (Int × Int) := [(2, 9500), (3, 9000), (4, 8500), (5, 8000), (6, 7500), (7, 7000), (8, 6500), (9, 6000), (10, 5500), (11, 5000)]

def krCcTax (nm st : String) (mult : Int) : List VehicleTax :=
  [(0, 1000, 80), (1000, 1600, 140), (1600, VehicleTax.noBound, 200)].map fun (lo, hi, r) =>
    { name := nm, kinds := ["car"], when := [(.engineCcm, lo, hi)], parts := [(.engineCcm, QtyTable.perUnit r 1)],
      ageFactors := krAge, multiplierBp := mult, level := .local, statute := st }

def krEvTax (nm st : String) (mult : Int) : VehicleTax :=
  { name := nm, kinds := ["car"], fuels := [.electric, .hydrogen], fixed := 100000, multiplierBp := mult, level := .local, statute := st }

def krVehicleTaxes : List VehicleTax :=
  krCcTax "자동차세 (비영업용 승용자동차)" "지방세법 제127조 제1항 제1호, 제2호 (배기량 시시당 세액, 차령 경감)" 10000
  ++ [krEvTax "자동차세 (그 밖의 승용자동차)" "지방세법 제127조 제1항 제3호 (비영업용 100,000원)" 10000]
  ++ krCcTax "지방교육세 (자동차세분)" "지방세법 제150조, 제151조 제1항 제7호 (자동차세액의 100분의 30)" 3000
  ++ [krEvTax "지방교육세 (자동차세분)" "지방세법 제150조, 제151조 제1항 제7호 (자동차세액의 100분의 30)" 3000]'''
S["extra_run"] = S.get("extra_run", []) + ["vehicleTaxCharges krVehicleTaxes g"]
S["extra_covers"] = S.get("extra_covers", []) + [".useOfGoods"]
S["extra_unsupported"] = S.get("extra_unsupported", []) + [
 "vehicleTaxUnknown \"자동차세\" krVehicleTaxes g",
 "vehicleTaxUnmatched \"자동차세\" krVehicleTaxes g",
 "(if g.vehicles.isEmpty then [] else [\"자동차세 at the standard rates of 지방세법 art. 127 for non-commercial passenger cars (ordinance surcharge up to 50 % not read; commercial vehicles, vans, trucks not distinguished); 차령 taken as year - first registration + 1 (Enforcement Decree not read); 취득세 on vehicle acquisition not modelled\"])"]
S["guards"] = S.get("guards", []) + ["krVehicleTaxes.length == 8", "(krAge.map (·.2)).getLast? == some 5000"]
S["notes"] = S.get("notes", []) + ["KR 5200: 지방세법 art. 127 (자동차세) and art. 151 (1) 7 (지방교육세) via kernel VehicleTax"]
S["taxes"] = S["taxes"] + [
 {"oecd": "5200", "tax": "자동차세 on passenger cars (with 지방교육세 30 %)",
  "statute": "지방세법 제127조 제1항 제1호-제3호, 제150조, 제151조 제1항 제7호",
  "dated": "law.go.kr version in force 2026-07-01; art. 127 (1) unchanged since 2011-12-02, art. 151 (1) since 2021-12-28 (in force 2025)", "grade": "A", "kernel_parts": ["VehicleTax"],
  "unsupported": ["standard rates (local ordinance surcharge not read)", "차령 per the Enforcement Decree not read (year - first registration + 1)", "commercial vehicles and non-passenger vehicles not distinguished"]}]

# ---- R3 session 10 (2026-11-21): FT reviewer 6 item 2: the 2025 지방세법 read. law.go.kr version list
# (`LSW/lsHstListR.do`, tools/p10/kr10.py): lsiSeq 268065 = Law 20630 of 2024-12-31, in force 2025-01-01
# (kr/law/lawgo/지방세법_20250101_268065.*). art. 52 (1) <개정 … 2017. 12. 26.>: 1. 가. 제1종 궐련 20개비당 1,007원;
# art. 151 (1) 4.: 담배소비세액의 1만분의 4,399. The next change to art. 52 (1) is Law 21308 of 2025-12-31 (in force from
# a date in 2026, its 부칙 arts. 1, 2, 7); the 2025-10-01 version (Law 21065) does not amend it.
S["doc"] = S["doc"].replace('''The 2026 texts are used as the 2025 texts for these provisions (grade B for the tobacco taxes: the version in force on
2025-07-01 was not fetched; law.go.kr's version walk did not answer).''', '''Session 10: the 지방세법 version in force from 2025-01-01 (law.go.kr lsiSeq 268065, Law No. 20630,
`kr/law/lawgo/지방세법_20250101_268065.txt`, found through the site's version list) has the same art. 52 (1) 1. 가.
(<개정 … 2017. 12. 26.>) and art. 151 (1) 4.; art. 52 (1) is next amended by Law No. 21308 of 2025-12-31, from 2026.''')
assert "lsiSeq 268065" in S["doc"]
for t in S["taxes"]:
    if t["oecd"] == "5121":
        t.update(statute="지방세법 제52조 ① 1. 가., 제151조 ① 4. (version in force 2025-01-01, Law 20630)",
                 dated="law.go.kr version in force 2025-01-01 (lsiSeq 268065); art. 52 (1) unchanged from 2017-12-26 to Law 21308 (2025-12-31, in force 2026)",
                 grade="A")
    if t["oecd"] == "5200":
        t["dated"] = t["dated"] + "; checked in the 2025-01-01 version (lsiSeq 268065): art. 127 (1) <개정 2011. 12. 2.>, the same text"
S["notes"] = [n.replace("(current versions, amendment notes checked)", "(부가가치세법 current version with amendment notes; 지방세법 2025 version)") for n in S["notes"]]
