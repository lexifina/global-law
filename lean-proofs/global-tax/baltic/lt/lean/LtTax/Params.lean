import TaxKernel

/-!
# Lithuania 2025 (with 2022-2024 and 2026 for versioned-law checks): parameters, each with its source

Money is in **euro cents** (`Int`): the GPMĮ and Sodra compute in euros and cents. Rates in basis points.

Sources (saved under `cmp20/baltic/lt/refs/`):
* [GPMĮ] Gyventojų pajamų mokesčio įstatymas IX-1007, e-TAR TAR.C677663D2202
  (https://www.e-tar.lt/portal/lt/legalAct/TAR.C677663D2202/asr). e-TAR, e-seimas and vmi.lt answer 403
  (Cloudflare) to scripts; the text used is the archived consolidated version "Suvestinė redakcija nuo 2023-01-01"
  (web.archive.org capture 2023-04-11 of the e-TAR text frame), `refs/gpmi_2023_redakcija.txt`; the index page of the
  2025 version ("Galiojanti suvestinė redakcija: 2025-01-02 - 2025-12-31", capture 2025-09-16) is
  `refs/gpmi_asr_wb20250916001243.dec.html` (its text frame was not archived, so 2025 amounts come from [EM]/[PWC25]).
* [EM] EUROMOD Country Report Lithuania 2022-2025 (JRC, 2026), `refs/euromod_CR_LT.txt` §2.8.1 (NPD 2022-2025,
  "Source: State Tax Inspectorate"), §2.7 (contributions), §2.6.3-2.6.4 (child benefits), Tables 1.2, 1.5.
* [SODRA] sodra.lt "Įmokų tarifai, taikomi už samdomus darbuotojus" (archived 2026-10-09), `refs/sodra_samdomi_wb.txt`,
  and "... savarankiškai dirbantiems asmenims" (archived 2025-06-14), `refs/sodra_savarank_wb.txt`.
* [PWC25] PwC Worldwide Tax Summaries Lithuania, reviewed 5 March 2025 (archived), `refs/wb_taxsummaries*.txt`.
* [KPMG] KPMG Lithuania tax newsletter, August 2025, `refs/kpmg_2025_08.txt` (the 2026 NPD).
* [PWC26] PwC Worldwide Tax Summaries Lithuania (2026 pages), `refs/pwc_*.txt`.
-/

namespace LtTax
open TaxKernel

/-- A part of the year with constant benefit parameters (BSI = bazinė socialinė išmoka, VRP = valstybės remiamos
pajamos), monthly amounts in cents. -/
structure Seg where
  months : Int
  bsi : Int
  vrp : Int
  deriving Repr

/-- One year's parameters. -/
structure YP where
  year : Nat
  /-- GPMĮ 20 str. 1-2 d.: "minimaliosios mėnesinės algos, galiojusios einamųjų kalendorinių metų sausio 1 dieną" -/
  mma : Int
  /-- monthly NPD maximum (20 str. 2 d. 1 p.) -/
  npdMax : Int
  /-- first-formula coefficient in hundredths (0.49 → 49) -/
  c1 : Int
  /-- monthly / annual income above which the second formula applies (20 str. 2 d. 3 p., 1 d. 3 p.) -/
  thrM : Int
  thrY : Int
  /-- the second formula "400 – 0,18 × (P – 642)" exists (2022-2025; removed for 2026, [KPMG]) -/
  second : Bool := true
  /-- VDU "taikomos apdraustųjų asmenų einamųjų metų valstybinio socialinio draudimo įmokų bazei skaičiuoti",
  monthly cents (6 str. 1¹ d.) -/
  vdu : Int
  /-- employment-income schedule (6 str. 1¹ d.) -/
  emp : Schedule
  /-- child-benefit parameters by part of the year (empty: benefits not modelled for that year) -/
  segs : List Seg

/-- 6 str. 1¹ d. (2022-2025): "metinė pajamų dalis, neviršijanti 60 ... VDU ... apmokestinama taikant 20 procentų"
and "viršijanti 60 VDU ... 32 procentų". Threshold = 60 × monthly VDU (annual, cents). -/
def empSched2 (vdu : Int) : Schedule := Schedule.ofList [(0, 2000), (60 * vdu, 3200)]

/-- 2026 (adopted 2025, XV-343/XV-352): 20 % to 36 VDU, 25 % to 60 VDU, 32 % above ([PWC26], facts restated: the
36-VDU limit is EUR 83 237 in 2026). -/
def empSched3 (vdu : Int) : Schedule := Schedule.ofList [(0, 2000), (36 * vdu, 2500), (60 * vdu, 3200)]

/-- 2025, the model's default year.
* MMA 1 038 €: [SODRA] "Minimalioji mėnesinė alga ... nuo 2025 m. sausio 1 d. – 1038 Eur"; [EM] Table 1.5.
* NPD 747 €, 0.49, thresholds 2 387,29 € / 28 647,48 €: [EM] §2.8.1 "The rules applied for calculation of the basic
  allowance for 2025": "747 – 0.49 × (monthly employment income – 1038)", "8964 – 0.49 × (resident's annual income –
  12456)", "exceeds 2387.29 EUR (28647.48 EUR per year)"; the structure is GPMĮ 20 str. 1-3 d. (2023 text).
* VDU 2 108,88 €: [EM] Table 1.5 "Average monthly salary (AMS) ... 2108.88"; [PWC25] (facts restated): the 20 % band
  ends at EUR 126 532 of annual income in 2025 (= 60 VDU).
* BSI 70 €, VRP 221 €: [EM] Table 1.2 (2025 column). -/
def y2025 : YP :=
  { year := 2025, mma := 103800, npdMax := 74700, c1 := 49, thrM := 238729, thrY := 2864748, vdu := 210888,
    emp := empSched2 210888, segs := [⟨12, 7000, 22100⟩] }

/-- 2024: MMA 924, NPD 747 – 0.5 × (P – 924) to 2 167 € ([EM] §2.8.1 and Table 2.16 "0.5", "2167"); VDU 1 902,70;
BSI 55, VRP 176 ([EM] Tables 1.2, 1.5). -/
def y2024 : YP :=
  { year := 2024, mma := 92400, npdMax := 74700, c1 := 50, thrM := 216700, thrY := 2600400, vdu := 190270,
    emp := empSched2 190270, segs := [⟨12, 5500, 17600⟩] }

/-- 2023: the archived statute itself, GPMĮ 20 str. 2 d.: "taikomas mėnesio NPD yra 625 eurai", "625 – 0,42 × (...)",
"neviršija 1 926 eurų"; 1 d.: "7 500 eurų", "neviršija 23 112 eurų per metus", "4 800 – 0,18 × (GMP – 12 × 642)".
MMA 840, VDU 1 684,90, BSI 49, VRP 157 ([EM] Tables 1.2, 1.5). -/
def y2023 : YP :=
  { year := 2023, mma := 84000, npdMax := 62500, c1 := 42, thrM := 192600, thrY := 2311200, vdu := 168490,
    emp := empSched2 168490, segs := [⟨12, 4900, 15700⟩] }

/-- 2022 (rules of 1 June 2022 applied to the whole year): 540 – 0.34 × (P – 730) to 1 704 € ([EM] §2.8.1 text; its
Table 2.16 prints 0.26, which the OECD figures refute: FINDINGS F9). VDU 1 504,10. BSI 42 € January-May and 46 € from
June; VRP 129 € / 147 € ([EM] Table 1.2). -/
def y2022 : YP :=
  { year := 2022, mma := 73000, npdMax := 54000, c1 := 34, thrM := 170400, thrY := 2044800, vdu := 150410,
    emp := empSched2 150410, segs := [⟨5, 4200, 12900⟩, ⟨7, 4600, 14700⟩] }

/-- 2026 (for the reform-timing scan only): NPD "747 – 0,49 × (... – MMA)" with no second formula [KPMG]; MMA 1 153
[PWC26 "EUR 1,153 in 2026"]; VDU 2 312,14 (= 83 237 / 36, [PWC26]); three rates. Child benefits and the 2026
individual-activity regime are not modelled. -/
def y2026 : YP :=
  { year := 2026, mma := 115300, npdMax := 74700, c1 := 49, thrM := 1000000000, thrY := 1000000000,
    second := false, vdu := 231214, emp := empSched3 231214, segs := [] }

def yearParams (y : Nat) : YP :=
  match y with
  | 2022 => y2022 | 2023 => y2023 | 2024 => y2024 | 2026 => y2026 | _ => y2025

/-! ## Rates that did not change 2022-2025 -/

/-- 6 str. 1 d.: "Pajamų mokesčio tarifas yra 15 procentų, jeigu šiame straipsnyje nenustatyta kitaip" (dividends,
individual activity before the credit, other income up to 120 VDU). -/
def rate15 : Int := 1500
/-- 6 str. 1² d.: other (non-employment) income "dalis, viršijanti 120 VDU ... 20 procentų". -/
def otherSched (vdu : Int) : Schedule := Schedule.ofList [(0, 1500), (120 * vdu, 2000)]
/-- 17 str. 1 d. 20 p.: interest "suma, neviršijanti 500 eurų per mokestinį laikotarpį" is exempt. -/
def interestExempt : Int := 50000
/-- 17 str. 1 d. 30 p.: gain on financial instruments "neviršijantis 500 eurų per mokestinį laikotarpį" is exempt. -/
def gainExempt : Int := 50000
/-- 21 str. 3 d.: deductions "negali viršyti 25 procentų" of the taxable income; items 1, 2, 2¹ "negali viršyti
1 500 eurų". -/
def dedPct : Int := 25
def dedCap : Int := 150000

/-- Employee contributions 2025 ([SODRA] "Pensijų socialinis draudimas – 8,72 proc.; Ligos – 1,99 proc.; Motinystės –
1,81 proc. Sveikatos draudimas – 6,98 proc."; "papildomai priskaičiuojama 3 proc. įmoka" for the II pillar). VSD
(pension + sickness + maternity = 12.52 %) has the 60 VDU ceiling, PSD and the II pillar have none ([EM] §2.7.1 "the
ceilings of 60 AMS ... The ceiling does not apply for the healthcare contributions nor to the funded pension scheme";
[PWC25], facts restated: 19.5 % in all up to EUR 126 532 of the year's employment income, 6.98 % beyond it). -/
def vsdRate : Int := 1252
def psdRate : Int := 698
def pillar2Rate : Int := 300
def vsd (yp : YP) : Contribution :=
  { name := "VSD", sched := Schedule.flat vsdRate, ceiling := 60 * yp.vdu, round := Rule.unitHalfUp }
def psd : Contribution := { name := "PSD", sched := Schedule.flat psdRate, round := Rule.unitHalfUp }
def pillar2 : Contribution := { name := "pillarII", sched := Schedule.flat pillar2Rate, round := Rule.unitHalfUp }

/-- Individual activity ([SODRA] "VSD – 90 % nuo apmokestinamųjų pajamų", VSD 12,52, PSD 6,98, "PSD – kas mėnesį
nuo MMA"); ceiling 43 VDU ([EM] §2.7.4 "SIC contributions are subject to the ceilings of 43 AMS"). -/
def iaBasePct : Int := 90
def iaCeilingVdu : Int := 43

/-- Child benefits ([EM] §2.6.3: "1.75 BSA per child, which is 122.5 EUR in 2025"; §2.6.4: additional "1.03 BSA,
which equals to 72.1 EUR in 2025" for families with 3+ children, a disabled child, or up to two children with
"monthly income per each family member can't exceed the threshold of 2 SSI"). Coefficients in hundredths. -/
def cbUniversal : Int := 175
def cbAdditional : Int := 103
def cbVrpMult : Int := 2

end LtTax
