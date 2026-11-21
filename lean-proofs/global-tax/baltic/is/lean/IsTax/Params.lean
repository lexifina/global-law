import TaxKernel

/-!
# Iceland (Reykjavík), income year (tekjuár) 2025: parameters, each with its source

Statute texts: Lagasafn (althingi.is), edition 156b (1 Sept 2025) and 155 (15 March 2025), read from the open
mirror github.com/althingi-net/lagasafn-xml (data/original/<edition>/2003090.html; althingi.is itself answers with a
bot challenge), saved under `refs/law/`. Indexed amounts: Auglýsing fjármála- og efnahagsráðuneytisins
nr. 1665/2024 (Stjórnartíðindi B, 30 Dec 2024; island.is/stjornartidindi/nr/de469729-327f-4dff-8e34-c94db60a1f3d),
`refs/gov/auglysing_1665_2024.txt`. Every amount in whole krónur, every rate in basis points.
-/

namespace IsTax
open TaxKernel

/-! ## State income tax (tekjuskattur), lög nr. 90/2003, 66. gr. 1. mgr. -/

/-- 66. gr. 1. mgr. 1.–3. tölul. ("[16,55%]", "[23,05%]", "[31,35%]", L. 100/2023, 25. gr.) with the 2025
thresholds of Auglýsing 1665/2024: "16,55% af tekjuskattsstofni að 5.664.062 kr., 23,05% af tekjuskattsstofni frá
5.664.063 kr. að 15.901.523 kr. og 31,35% af tekjuskattsstofni frá 15.901.524 kr." (statute base amounts 3.962.699 /
11.125.045 kr., indexed by 66. gr. 1. mgr. 5. tölul.: CPI + 1,0 % productivity). -/
def T1 : Int := 5664062
def T3 : Int := 15901523
def rate1 : Int := 1655
def rate2 : Int := 2305
def rate3 : Int := 3135
def stateSched : Schedule := Schedule.ofList [(0, rate1), (T1, rate2), (T3, rate3)]

/-- 66. gr. 1. mgr. 4. tölul. (L. 132/2019, 1. gr.; in force for tekjuár 2025, repealed for 2026 by L. 99/2025,
30. gr.): "Sé tekjuskattsstofn annars samskattaðs aðila hærri en 11.125.045 kr. skal það sem umfram er skattlagt með
[23,05%] skatthlutfalli allt að helmingi þeirrar fjárhæðar sem tekjuskattsstofn þess tekjulægri er undir 11.125.045
kr., þó reiknast [23,05%] skatthlutfall aldrei af hærri fjárhæð en 3.581.173 kr." The 2025 cap is not published in
Auglýsing 1665/2024; indexed like the other amounts (5. tölul.) it is 3.581.173 × 15.901.523 / 11.125.045
= 5.118.730,3 kr., i.e. half the 2025 middle band (15.901.523 − 5.664.062) / 2 = 5.118.730,5 (FINDINGS F7). -/
def bandTransferCap : Int := 5118730

/-! ## Municipal tax (útsvar), lög nr. 4/1995 um tekjustofna sveitarfélaga -/

/-- 23. gr.: "má þó eigi vera hærra en 14,97% og eigi lægra en 12,44% af útsvarsstofni". Reykjavíkurborg 2025:
14,97 % (Samband íslenskra sveitarfélaga, "Uppgjör útsvars 2026 vegna launa 2025", Álagningarprósenta útsvars
0.1497, `refs/gov/utsvar_uppgjor_2026_vegna_launa_2025.xlsx`). -/
def utsvarReykjavik : Int := 1497
/-- The weighted average 14,94 % used in withholding (staðgreiðsla) and by the OECD (Auglýsing 1665/2024:
"Meðalútsvar á árinu 2025 ... verður 14,94%"). -/
def utsvarAverage : Int := 1494

/-! ## Personal credit (persónuafsláttur), 67. gr. A -/

/-- 67. gr. A 1. mgr. (base 530.466 kr., indexed); Auglýsing 1665/2024: "persónuafsláttur hvers einstaklings á árinu
2025 vera 824.288 kr., eða 68.691 kr. að meðaltali á mánuði." -/
def persCredit : Int := 824288
def persCreditMonth : Int := 68691
/-- 67. gr. A 2. mgr. (L. 140/2024, 2. gr.; removed for 2026 by L. 99/2025, 31. gr.): "Af þeim persónuafslætti sem
þá er óráðstafað skal [22/31] hlutum ráðstafað til að greiða tekjuskatt sem lagður er á fjármagnstekjur". -/
def capCreditNum : Int := 22
def capCreditDen : Int := 31

/-! ## Deductions (30. gr. A) -/

/-- 30. gr. A 4. tölul.: "Iðgjöld launþega til öflunar lífeyrisréttinda ... að hámarki 4% af iðgjaldsstofni";
"Að auki allt að 4% af iðgjaldsstofni" (séreign). Same for the self-employed (5. tölul.). -/
def pensionRate : Int := 400
def sereignMaxRate : Int := 400
/-- 30. gr. A 7. tölul.: "Gjafir og framlög til lögaðila ..., að lágmarki samtals 10 þús. kr. og allt að hámarki
samtals 350 þús. kr. á almanaksári." -/
def giftMin : Int := 10000
def giftMax : Int := 350000

/-! ## Capital income (fjármagnstekjur), 66. gr. 3. mgr. -/

/-- "Tekjuskattur af fjármagnstekjum einstaklinga utan rekstrar skal vera [22%]" (L. 96/2017, 2. gr.). -/
def capRate : Int := 2200
/-- "ekki reikna tekjuskatt ... af annars vegar vaxtatekjum og hins vegar tekjum af hlutabréfaeign í formi arðs og
söluhagnaðar í félögum skráðum á skipulegum markaði ..., samtals allt að 300.000 kr. á ári hjá manni og skal frádráttur
nýttur þannig að fyrst skal jafna út vaxtatekjur, næst arðstekjur og loks söluhagnað" -/
def capExemption : Int := 300000
/-- "Enn fremur skal ekki reikna tekjuskatt af 50% af tekjum manns af útleigu íbúðarhúsnæðis ..." (25 % from 2026). -/
def rentExemptBp : Int := 5000

/-! ## Levies collected with the assessment (álagning) -/

/-- The two flat levies of an income year are laid on at the assessment of the following year at the amounts then in
force. Income year 2025 = álagning 2026: útvarpsgjald 22.200 kr. (lög nr. 23/2013, 14. gr., as amended by
L. 99/2025: "Gjaldið skal nema 22.200 kr."), gjald í Framkvæmdasjóð aldraðra 14.614 kr. (lög nr. 125/1999, 10. gr.:
"Gjaldið skal nema 14.614 kr."), income floor 2.617.618 kr. (10. gr.: "lægri en 1.361.468 kr." indexed; Skatturinn,
Gjald í framkvæmdasjóð aldraðra: "Í álagningu 2026 | 14.614 | 2.617.618"); ages 16–69 ("Undanþegin gjaldinu eru börn
innan 16 ára aldurs og þeir sem eru 70 ára og eldri í lok tekjuárs"). The OECD's 2025 row uses the álagning-2025
amounts (21.400, 14.093; floor 2.474.942), kept as `leviesAssess2025` to reproduce it (FINDINGS F5). -/
structure Levies where
  utvarp : Int
  aldradra : Int
  floor : Int
  deriving Repr, DecidableEq

def levies2025 : Levies := ⟨22200, 14614, 2617618⟩
def leviesAssess2025 : Levies := ⟨21400, 14093, 2474942⟩

/-! ## Child benefit (barnabætur), 68. gr. A with ákvæði til bráðabirgða LXXXII -/

/-- Brbákv. LXXXII (L. 127/2024, 29. gr.; year changed to "[2026]" by L. 99/2025, 34. gr., i.e. the assessment of
income year 2025): "345.000 kr. ... einstæðra foreldra skulu vera 514.500 kr. ... umfram 11.688.000 kr. hjá hjónum
og umfram 5.844.000 kr. hjá einstæðu foreldri ... Skerðingarhlutfallið skal vera 4% með öllum börnum óháð fjölda þeirra
... með hverju barni yngra en sjö ára ... 130.000 kr. og skal skerðingarhlutfall þeirra vera 4% með hverju barni".
68. gr. A 7. mgr.: "Barnabætur sem eru ákvarðaðar lægri en [5.000 kr.] á hvern framfæranda ... falla niður." -/
def bbCouple : Int := 345000
def bbSingle : Int := 514500
def bbUnder7 : Int := 130000
def bbStartCouple : Int := 11688000
def bbStartSingle : Int := 5844000
def bbPct : Int := 4
def bbMinPerCarer : Int := 5000

/-! ## Withholding (staðgreiðsla) 2025, for the RSK calculator check -/

/-- Auglýsing 1665/2024: "31,49% ... að 472.005 kr. að meðaltali á mánuði, 37,99% ... frá 472.006 kr. að 1.325.127
kr. ... og 46,29% ... frá 1.325.128 kr." -/
def wM1 : Int := 472005
def wM3 : Int := 1325127
def withholdSched : Schedule := Schedule.ofList [(0, 3149), (wM1, 3799), (wM3, 4629)]

/-! ## Income years 2022-2024 (round 5, 2026-11-19): a per-year record; 2025 keeps the constants above.

Sources (saved in `refs/r4/` and `refs/law/`):
* State rates, 66. gr. 1. mgr. 1.-3. tölul.: lagasafn 153c (in force 2023) "16,78% ... 23,28% ... 31,58%",
  154c (2024) "16,55% ... 23,05% ... 31,35%". 2022: no mirror edition; Skatturinn, Staðgreiðsla 2022: the withholding
  rate "samanstendur annarsvegar af tekjuskatti og hinsvegar meðalútsvari (14,45%)" with Skattþrep 2022 "31,45%",
  "37,95%", "46,25%", so the state rates are 17,00 / 23,50 / 31,80 %.
* Band thresholds: Skatturinn, Skattþrep í staðgreiðslu 2022 "0 – 370.482 kr.", "370.483 - 1.040.106 kr."; 2023
  "409.986", "1.151.012"; 2024 "446.136", "1.252.501" (monthly; × 12 for the year). The 4. tölul. cap moves with the
  same index as the thresholds (base 3.581.173 against 11.125.045), so cap = T3 × 3.581.173 / 11.125.045.
* Persónuafsláttur (67. gr. A): Skatturinn, "Persónuafsláttur fyrri ára": 2022 "646.993 kr.", 2023 "715.981 kr.",
  2024 "779.112 kr." a year.
* Útsvar: maximum (Reykjavík's rate), lög 4/1995 23. gr. 153c "má þó eigi vera hærra en 14,74%" (2023), 154c
  "14,97%" (2024); 2022 Reykjavík 14,52 % **not sourced** (flagged). Average (withholding): Skatturinn 14,45 % (2022),
  14,67 % (2023), 14,93 % (2024).
* Levies of the following assessment: útvarpsgjald (lög 23/2013, 14. gr.) "20.200 kr." (153c, álagning 2023),
  "20.900 kr." (154c, álagning 2024), "21.400 kr." (155, álagning 2025); framkvæmdasjóður aldraðra and its income floor,
  Skatturinn table: "Í álagningu 2023 | 13.284 | 2.057.211", "2024 | 13.749 | 2.276.569", "2025 | 14.093 | 2.474.942".
* Barnabætur (round 6): Skatturinn, "Barnabætur", tables "Fjárhæðir 2023/2024/2025" (the amounts of the assessment
  in that year, i.e. for income years 2022/2023/2024; "Fjárhæðir 2026" equals the 2025 constants above):
  2025 table: "Barnabætur með hverju barni | 514.500 kr. | 345.000 kr.", "Viðbót ... yngra en 7 ára | 130.000",
  "Skerðingarmörk ... 5.844.000 ... 11.688.000", "Skerðingarhlutfall, óháð fjölda barna | 4%";
  2024 table: 489.000 / 328.000, 130.000, 5.500.000 / 11.000.000, 4 %;
  2023 table: couple "Með hverju barni | 295.000", single "440.000", under 7 "138.000"; limits "9.500.000" / "4.750.000";
  "Skerðingarhlutföll ... Eitt barn | Tvö börn | Þrjú eða fleiri ... 4% | 6% | 8%"; the under-7 extra is reduced
  separately by 4 % per child. Saved as `refs/r4/bb2.html`. -/
structure YearP where
  year : Nat
  r1 : Int
  r2 : Int
  r3 : Int
  t1 : Int
  t3 : Int
  pers : Int
  utsvarRvk : Int
  utsvarAvg : Int
  levies : Levies
  /-- barnabætur of the following assessment (round 6): per child (couple, single parent), extra per child under 7,
  income limits (couple, single), reduction percent (whole %) for 1, 2, 3+ children -/
  bbCouple : Int := 0
  bbSingle : Int := 0
  bbUnder7 : Int := 0
  bbStartCouple : Int := 0
  bbStartSingle : Int := 0
  bbPct1 : Int := 4
  bbPct2 : Int := 4
  bbPct3 : Int := 4
  deriving Repr

def YearP.sched (q : YearP) : Schedule := Schedule.ofList [(0, q.r1), (q.t1, q.r2), (q.t3, q.r3)]
def YearP.cap (q : YearP) : Int := q.t3 * 3581173 / 11125045

def yp2025 : YearP :=
  { year := 2025, r1 := rate1, r2 := rate2, r3 := rate3, t1 := T1, t3 := T3, pers := persCredit,
    utsvarRvk := utsvarReykjavik, utsvarAvg := utsvarAverage, levies := levies2025 }
def yp2022 : YearP :=
  { year := 2022, r1 := 1700, r2 := 2350, r3 := 3180, t1 := 12 * 370482, t3 := 12 * 1040106, pers := 646993,
    utsvarRvk := 1452, utsvarAvg := 1445, levies := ⟨20200, 13284, 2057211⟩,
    bbCouple := 295000, bbSingle := 440000, bbUnder7 := 138000, bbStartCouple := 9500000, bbStartSingle := 4750000,
    bbPct1 := 4, bbPct2 := 6, bbPct3 := 8 }
def yp2023 : YearP :=
  { year := 2023, r1 := 1678, r2 := 2328, r3 := 3158, t1 := 12 * 409986, t3 := 12 * 1151012, pers := 715981,
    utsvarRvk := 1474, utsvarAvg := 1467, levies := ⟨20900, 13749, 2276569⟩,
    bbCouple := 328000, bbSingle := 489000, bbUnder7 := 130000, bbStartCouple := 11000000, bbStartSingle := 5500000 }
def yp2024 : YearP :=
  { year := 2024, r1 := 1655, r2 := 2305, r3 := 3135, t1 := 12 * 446136, t3 := 12 * 1252501, pers := 779112,
    utsvarRvk := 1497, utsvarAvg := 1493, levies := ⟨21400, 14093, 2474942⟩,
    bbCouple := 345000, bbSingle := 514500, bbUnder7 := 130000, bbStartCouple := 11688000, bbStartSingle := 5844000 }
def yearP (y : Nat) : YearP :=
  if y = 2022 then yp2022 else if y = 2023 then yp2023 else if y = 2024 then yp2024 else yp2025

end IsTax
