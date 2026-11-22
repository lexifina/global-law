S = dict(cc="ID", family_name="5111 PPN",
doc=r'''# Indonesia 2025: value added tax, PPN (5111); excise (cukai) not modelled

Source: UU 7/2021 (Harmonisasi Peraturan Perpajakan), official text on the build server (`cmp20/world/B02-g20/id/law/uu_7_2021.txt`,
OCR of the JDIH PDF; sha256 in `law/SOURCES.tsv`), amending UU 8/1983 (PPN):
* **Pasal 7 (1)**: "Tarif Pajak Pertambahan Nilai yaitu: a. sebesar 11% … mulai berlaku pada tanggal 1 April 2022;
  b. sebesar 12% (dua belas persen) yang mulai berlaku paling lambat pada tanggal 1 Januari 2025"; (2) 0 % on exports.
* **Pasal 4A (2) c, (3) l**: food and drink served by hotels, restaurants and caterers, and hotel rooms, are not subject to
  PPN (they are regional taxes): restaurants and hotels outside PPN.
* **Pasal 16B (1a) j**: facilities (PPN not collected or exempted) for 1. basic necessities, 2. medical services in the
  national health insurance, 4. financial services, 5. insurance, 6. education, 7. public land and water transport. The
  implementing PP 49/2022 was not read: these classes are taken as exempt.
* **PMK 131/2024** (not read; value flagged): goods other than luxury goods are taxed on "DPP nilai lain" of 11/12 of the
  price, so 12 % × 11/12 = 11 % effective; the basket uses the effective 11 % on standard goods, the statutory 12 % on
  `recreation` (luxury goods proxy: not distinguished).''',
vat=dict(name="Pajak Pertambahan Nilai", standard=1100, reduced=1200, statute="UU 8/1983 Pasal 7 (1) b as amended by UU 7/2021 (12 %), PMK 131/2024 (DPP 11/12: 11 % effective), Pasal 4A, Pasal 16B (1a) j",
  classes={"restaurants":"exempt","hotels":"exempt","food":"exempt","health":"exempt","financial":"exempt","insurance":"exempt","education":"exempt","transport":"exempt"}),
notes=["ID 5111: UU 7/2021 Pasal 7, 4A, 16B; effective 11 % per PMK 131/2024 (not read)"],
unsupported=[[["spirits","wine","beer","cigarettes","tobaccoOther"],"cukai (excise) on tobacco and alcohol (PMK tariffs per stick and litre) not modelled"],
 [["petrol","diesel"],"PBBKB (regional fuel tax, UU 1/2022) not modelled"],
 [["restaurants","hotels"],"PBJT (regional tax on restaurants and hotels, UU 1/2022; DKI Jakarta) not modelled"],
 [["food"],"food taken as basic necessities (PPN facility); processed food is taxable"]],
guards=["vat.embedded { good := .clothing, amount := 11100 } == 1100","vat.embedded { good := .restaurants, amount := 11100 } == 0"],
taxes=[{"oecd":"5111","tax":"Pajak Pertambahan Nilai","statute":"UU 8/1983 as amended by UU 7/2021: Pasal 4A, 7, 16B; PMK 131/2024","dated":"UU 7/2021 official text (rates 2025 per Pasal 7 (1) b)","grade":"B","kernel_parts":["Vat"],"unsupported":["PMK 131/2024 (effective 11 %) and PP 49/2022 (facilities) not read","PPnBM on luxury goods","PKP threshold (PMK) not modelled"]},
 {"oecd":"5121","tax":"Cukai (tobacco, alcohol)","statute":"UU 11/1995 as amended (UU 39/2007, UU 7/2021); PMK tariffs","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["PMK 97/2024 (tobacco) and the alcohol tariff PMK not reached; would unlock: the 2025 PMK texts from jdih.kemenkeu.go.id"]}])

# ---- R3 session 6 (2026-11-21): cukai on drinks containing ethyl alcohol (MMEA), PMK 160 Tahun 2023 (in force 1 January
# 2024; JDIH Kemenkeu status "Berlaku"; id/law/id_pmk160_2023_cukai_ea_mmea.pdf). Pre-change copy: tools/bak6/ID_cons.py.
S["imports"] = ["TaxKernel.Global2"]
S["family_name"] = "5111 PPN; 5121 cukai MMEA"
S["doc"] = S["doc"].replace("; excise (cukai) not modelled", "; cukai on alcoholic drinks (5121); tobacco cukai not modelled") + r'''

**Cukai MMEA (session 6, grade A)**: PMK 160 Tahun 2023 tentang Tarif Cukai Etil Alkohol, Minuman yang Mengandung Etil
Alkohol, dan Konsentrat yang Mengandung Etil Alkohol (in force 1 January 2024, art. on commencement; JDIH Kemenkeu
status "Berlaku" when read 2026-11-21), art. 3 (5) groups and Lampiran II, rupiah per litre, domestic production:
group A (up to 5 %) 16 500; group B (above 5 % to 20 %) 42 500 (imports 53 000); group C (above 20 % to 55 %) 101 000
(imports 152 000). Applied by the line's strength to beer, wine and spirits; domestic rates (the basket carries no
origin). Tobacco cukai (PMK 97/2024, not read) not modelled.'''
S["extra_lean"] = r'''/-- PMK 160/2023 Lampiran II (MMEA, domestic production), rupiah per litre by strength group: A ≤ 5 %, B 5-20 %, C 20-55 %. -/
def idMmea : List ExciseRule :=
  let r (g : Good) (lo hi rate : Int) (grp : String) : ExciseRule :=
    { good := g, name := s!"Cukai MMEA golongan {grp}", perUnitNum := rate, minAbvBp := lo, maxAbvBp := hi,
      statute := s!"PMK 160 Tahun 2023 Pasal 3 ayat (5), Lampiran II: golongan {grp}, Rp{rate} per liter (produksi dalam negeri)" }
  [.beer, .wine, .spirits].flatMap fun g => [r g (-1) 500 16500 "A", r g 500 2000 42500 "B", r g 2000 5500 101000 "C"]'''
S["extra_run"] = S.get("extra_run", []) + ["exciseRuleCharges idMmea g"]
S["extra_covers"] = S.get("extra_covers", []) + [".excise"]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("cukai (excise) on tobacco and alcohol")] + [
 [["cigarettes", "tobaccoOther"], "cukai on tobacco (PMK 97/2024, not read) not modelled"],
 [["beer", "wine", "spirits"], "cukai MMEA at the domestic rates (imports: group B Rp53 000, group C Rp152 000 per litre); a line without a strength falls in group A"]]
S["guards"] = S["guards"] + ["idMmea.length == 9",
 "(idMmea.find? (fun e => e.good == .spirits && e.minAbvBp < 4000 && 4000 <= e.maxAbvBp)).map (·.perUnitNum) == some 101000",
 "(idMmea.find? (fun e => e.good == .beer && e.minAbvBp < 480 && 480 <= e.maxAbvBp)).map (·.perUnitNum) == some 16500"]
S["notes"] = S["notes"] + ["ID 5121: PMK 160/2023 Lampiran II (cukai MMEA, domestic rates); tobacco not modelled"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "5121"] + [
 {"oecd": "5121", "tax": "Cukai on alcoholic drinks (MMEA groups A/B/C: Rp16 500 / 42 500 / 101 000 per litre)",
  "statute": "UU 11/1995 as amended; PMK 160 Tahun 2023 Pasal 3, Lampiran II", "dated": "PMK 160/2023 in force from 1 January 2024, status Berlaku on JDIH Kemenkeu (read 2026-11-21)",
  "grade": "A", "kernel_parts": ["ExciseRule"],
  "unsupported": ["tobacco cukai (PMK 97/2024, not read) not modelled", "import rates not distinguished"]}]

# ---- R3 session 8 (2026-11-21): cukai hasil tembakau (5121), PMK 97 Tahun 2024 (grade A). Pre-change copy:
# tools/bak8/ID_cons.py. Source: jdih.kemenkeu.go.id /dok/pmk-97-tahun-2024 (status "Berlaku") ->
# /api/download/06ef74b0-c127-4f42-8785-6b34384841ec/2024pmkeuangan097.pdf: id/law/id_pmk97_2024_cht.pdf.
S["family_name"] = "5111 PPN; 5121 cukai MMEA and tobacco"
S["doc"] = S["doc"].replace("; tobacco cukai not modelled", "; tobacco cukai (5121)") + r'''

**Cukai hasil tembakau (session 8, grade A)**: PMK 97 Tahun 2024 (third amendment of PMK 192/PMK.010/2021; signed
4 December 2024), Lampiran I (domestic products) "mulai berlaku pada tanggal 1 Januari 2025", rupiah per stick by type
and producer class (golongan, set by the producer's annual output, not by price; the line field `"sub"` names it):
SKM I 1 231 (default for a line without `"sub"`: machine-made kretek of the largest producers), SKM II 746, SPM I 1 336,
SPM II 794, SKT/SPT I 483 when the retail price per stick is above Rp2 170 and 378 from Rp1 555 to Rp2 170 (2.4.0 price
tier on the stick price), SKT II 223, SKT III 122. The minimum retail prices (Batasan Harga Jual Eceran "paling rendah")
are floors, not tiers. Imports (Lampiran II) are not distinguished.'''
S["extra_lean"] = S["extra_lean"] + r'''

/-- PMK 97/2024 Lampiran I (domestic), rupiah per stick; `firstOnly` order (named classes first, SKM I last as default). -/
def idTobacco : List ExciseRule :=
  let st (k : String) (r : Int) := s!"UU 11/1995 as amended; PMK 192/PMK.010/2021 as amended by PMK 97 Tahun 2024, Lampiran I: {k}, Rp{r} per batang (from 1 January 2025)"
  let r (sub k : String) (rate : Int) : ExciseRule :=
    { good := .cigarettes, sub := sub, name := s!"Cukai hasil tembakau ({k})", perUnitNum := rate, statute := st k rate }
  [r "SKM-II" "SKM golongan II" 746, r "SPM-I" "SPM golongan I" 1336, r "SPM-II" "SPM golongan II" 794,
   { r "SKT" "SKT/SPT golongan I, HJE above Rp2 170" 483 with minUnitPrice := 2170 },
   { r "SKT" "SKT/SPT golongan I, HJE Rp1 555 to Rp2 170" 378 with minUnitPrice := 1554, maxUnitPrice := 2170 },
   r "SKT-II" "SKT/SPT golongan II" 223, r "SKT-III" "SKT/SPT golongan III" 122,
   r "" "SKM golongan I" 1231]'''
S["extra_run"] = S.get("extra_run", []) + ["exciseRuleCharges idTobacco g (firstOnly := true)"]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("cukai on tobacco (PMK 97/2024")] + [
 [["cigarettes"], "cukai hasil tembakau by producer class: a line without \"sub\" is taken as SKM golongan I; PPN on tobacco products (PPN hasil tembakau) and the regional cigarette tax (pajak rokok, UU 1/2022) are not modelled"],
 [["tobaccoOther"], "cukai on cigars, klobot and cut tobacco (TIS, KLB, CRT per stick or gram) not modelled"]]
S["guards"] = S["guards"] + [
 "idTobacco.length == 8",
 "(idTobacco.find? (fun e => e.sub == \"\")).map (fun e => e.dutyOn { good := .cigarettes, amount := 60000, quantity := 20000 } {}) == some 24620",
 "((idTobacco.filter (fun e => e.sub == \"SKT\")).getD 1 default).perUnitNum == 378"]
S["notes"] = S["notes"] + ["ID 5121: PMK 97/2024 Lampiran I (cukai hasil tembakau, domestic, from 1 Jan 2025)"]
for t in S["taxes"]:
    if t["oecd"] == "5121":
        t["tax"] = "Cukai on alcoholic drinks (MMEA) and tobacco products (per stick by class)"
        t["statute"] += "; PMK 192/PMK.010/2021 as amended by PMK 97 Tahun 2024, Lampiran I"
        t["dated"] += "; PMK 97/2024 Lampiran I from 1 January 2025 (status Berlaku, read 2026-11-21)"
        t["unsupported"] = [u for u in t["unsupported"] if not u.startswith("tobacco cukai")] + [
            "tobacco: producer class from the line's sub (default SKM I); cigars and cut tobacco not modelled; PPN hasil tembakau and pajak rokok not modelled"]
