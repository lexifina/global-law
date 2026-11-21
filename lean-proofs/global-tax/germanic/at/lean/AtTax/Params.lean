import TaxKernel

/-!
# Austria, tax year 2025: parameters (euro **cents**, rates in **basis points**)

Every number cites its provision. Statute texts: RIS (Rechtsinformationssystem des Bundes, www.ris.bka.gv.at),
consolidated "Fassung vom 01.07.2025" unless stated, saved in `../law/` (`*_2025-07-01.txt`):
EStG 1988 (Gesetzesnummer 10004570), ASVG (10008147), AMPFG (10008903), AKG 1992 (10008787),
WBFG 2018 (20010012), GSVG (10008422), FLAG 1967 (10008220). Where RIS prints a base amount with an "Anm." note
giving the value for a year, the note and the BGBl. II ordinance it names are cited. The 2025 EStG amounts in
§ 33 Abs. 1, 4, 5, 6, 8, § 41 Abs. 4 and § 67 Abs. 1 are those of BGBl. I Nr. 144/2024, "erstmalig anzuwenden …
bei der Veranlagung für das Kalenderjahr 2025" (§ 124b Z 466).
-/

namespace AtTax
open TaxKernel

/-! ## Income tax (EStG 1988) -/

/-- § 33 Abs. 1: "für die ersten 13 308 Euro 0% / über 13 308 bis 21 617 Euro 20% / … bis 35 836 Euro 30% /
… bis 69 166 Euro 40% / … bis 103 072 Euro 48% / über 103 072 Euro 50%"; "Für Einkommensteile über eine Million
Euro beträgt der Steuersatz in den Kalenderjahren 2016 bis 2029 55%". Cents. -/
def tariff : Schedule := Schedule.ofList
  [(0, 0), (1330800, 2000), (2161700, 3000), (3583600, 4000), (6916600, 4800), (10307200, 5000),
   (100000000, 5500)]

/-- § 39 Abs. 3: "Die im Bescheid festgesetzte Einkommensteuer ist auf volle Euro abzurunden oder aufzurunden.
Dabei sind Beträge unter 0,50 Euro abzurunden, Beträge ab 0,50 Euro aufzurunden." (cents → euros) -/
def assessedRound (cents : Int) : Int := divR .halfUp cents 100

/-- § 16 Abs. 3: "ein Pauschbetrag von 132 Euro jährlich" (Werbungskostenpauschale, employees only). -/
def wkPauschale : Int := 13200

/-- § 33 Abs. 3a Z 1 lit. a: Familienbonus Plus "bis zum Ablauf des Monats, in dem das Kind das 18. Lebensjahr
vollendet, für jeden Kalendermonat 166,68 Euro". -/
def fbpMonthUnder18 : Int := 16668
/-- § 33 Abs. 3a Z 1 lit. b: "nach Ablauf des Monats, in dem das Kind das 18. Lebensjahr vollendet, für jeden
Kalendermonat 58,34 Euro". -/
def fbpMonth18 : Int := 5834

/-- § 33 Abs. 3 Z 1 (base 67,80 Euro) with RIS Anm. 1: "gemäß BGBl. II Nr. 314/2024 für 2025: 70,9 €" monthly
Kinderabsetzbetrag, paid with the Familienbeihilfe (booked as a cash benefit here, as the OECD does). -/
def kabMonth : Int := 7090

/-- § 33 Abs. 4 Z 1 and Z 2: Alleinverdiener- and Alleinerzieherabsetzbetrag "bei einem Kind 601 Euro, bei zwei
Kindern 813 Euro … für das dritte und jedes weitere Kind um jeweils 268 Euro". -/
def avabAmount (n : Nat) : Int :=
  if n = 0 then 0 else if n = 1 then 60100 else 81300 + 26800 * ((n : Int) - 2)

/-- § 33 Abs. 4 Z 1: the (Ehe-)Partner "Einkünfte von höchstens 7 284 Euro jährlich erzielt". -/
def avabPartnerLimit : Int := 728400

/-- § 33 Abs. 5 Z 1: "Ein Verkehrsabsetzbetrag von 487 Euro jährlich." -/
def vab : Int := 48700

/-- § 33 Abs. 5 Z 3: the Verkehrsabsetzbetrag "erhöht sich um 790 Euro (Zuschlag), wenn das Einkommen des
Steuerpflichtigen 19 424 Euro im Kalenderjahr nicht übersteigt. Der Zuschlag vermindert sich zwischen Einkommen von
19 424 Euro und 29 743 Euro gleichmäßig einschleifend auf null." A kernel `Taper`: 790 € over 10 319 €. -/
def zuschlag : Taper := { full := 79000, start := 1942400, num := 79000, den := 2974300 - 1942400 }
def zuschlagEnd : Int := 2974300

/-- § 33 Abs. 6 Z 3: Pensionistenabsetzbetrag "1 002 Euro … vermindert sich gleichmäßig einschleifend zwischen zu
versteuernden laufenden Pensionseinkünften von 21 245 Euro und 30 957 Euro auf null". -/
def pab : Taper := { full := 100200, start := 2124500, num := 100200, den := 3095700 - 2124500 }
/-- § 33 Abs. 6 Z 2: erhöhter Pensionistenabsetzbetrag "1 476 Euro, wenn die laufenden Pensionseinkünfte …
24 196 Euro … nicht übersteigen … zwischen … 24 196 Euro und 30 957 Euro auf null". -/
def pabHigh : Taper := { full := 147600, start := 2419600, num := 147600, den := 3095700 - 2419600 }
/-- § 33 Abs. 6 Z 1: erhöhter PAB if the partner has "Einkünfte im Sinne des Abs. 4 Z 1 von höchstens 2 673 Euro". -/
def pabPartnerLimit : Int := 267300

/-- § 33 Abs. 7: "Die Differenz zwischen 700 Euro und der Einkommensteuer nach Abs. 1 ist als Kindermehrbetrag zu
erstatten … Dieser Betrag erhöht sich für jedes weitere Kind … um den Betrag von 700 Euro." -/
def kmbPerChild : Int := 70000

/-- § 33 Abs. 8 Z 2: SV-Rückerstattung "55% der Werbungskosten im Sinne des § 16 Abs. 1 Z 3 lit. a (ausgenommen
Betriebsratsumlagen) und des § 16 Abs. 1 Z 4 und 5, höchstens aber 487 Euro"; "um 790 Euro zu erhöhen (SV-Bonus)"
for those entitled to the Zuschlag. -/
def svrRate : Int := 5500
def svrMax : Int := 48700
def svBonus : Int := 79000
/-- § 33 Abs. 8 Z 3: pensioners "80% der Werbungskosten im Sinne des § 16 Abs. 1 Z 4, höchstens aber 710 Euro". -/
def svrPenRate : Int := 8000
def svrPenMax : Int := 71000

/-- § 67 Abs. 1: sonstige Bezüge within the Jahressechstel after the SV of Abs. 12: "für die ersten 620 Euro 0%,
für die nächsten 24 380 Euro 6%, für die nächsten 25 000 Euro 27%, für die nächsten 33 333 Euro 35,75%".
(Above 83 333 Euro: § 67 Abs. 2 and 10, at the tariff.) -/
def szSchedule : Schedule := Schedule.ofList [(0, 0), (62000, 600), (2500000, 2700), (5000000, 3575)]
/-- § 67 Abs. 2: "nach Abzug der in Abs. 12 genannten Beträge mehr als 83 333 Euro" → tariff. -/
def szFixedMax : Int := 8333300
/-- § 41 Abs. 4 (Veranlagung): recomputed "wenn diese sonstigen Bezüge 2 570 Euro übersteigen" (Freigrenze, also
§ 67 Abs. 1 for withholding). -/
def szFreigrenze : Int := 257000
/-- § 41 Abs. 4: "Bis zu einem Jahressechstel von 25 000 Euro beträgt die Steuer 6% der 620 Euro übersteigenden
Bemessungsgrundlage, jedoch höchstens 30% der 2 447 Euro übersteigenden Bemessungsgrundlage." -/
def szGlideStart : Int := 244700
def szGlideRate : Int := 3000
def szGlideMaxSixth : Int := 2500000
def szFreibetrag : Int := 62000
def szRate : Int := 600

/-- § 39 Abs. 5: "ein Veranlagungsfreibetrag bis zu 730 Euro … Der Freibetrag vermindert sich um jenen Betrag, um
den die anderen Einkünfte 730 Euro übersteigen." -/
def vfb : Int := 73000

/-- § 27a Abs. 1 Z 1: "Geldeinlagen … bei Kreditinstituten … 25%"; Z 2: "in allen anderen Fällen … 27,5%". -/
def kestBank : Int := 2500
def kestOther : Int := 2750

/-- § 10 Abs. 1 Z 2-3: Gewinnfreibetrag "Für die ersten 33 000 Euro der Bemessungsgrundlage 15 %" without
investment (Grundfreibetrag, "höchstens daher mit 4 950 Euro"). The investment-related part is not modelled. -/
def gfbRate : Int := 1500
def gfbBase : Int := 3300000

/-- § 18 Abs. 1 Z 7: Spenden deductible "insoweit, als sie … insgesamt 10% des sich nach Verlustausgleich
ergebenden Gesamtbetrages der Einkünfte … nicht übersteigen". -/
def spendenCap : Int := 1000

/-! ## Employee social insurance (ASVG, AMPFG, AKG, WBFG 2018) -/

/-- ASVG § 5 Abs. 2 with Anm. 1 "gemäß BGBl. II Nr. 417/2024 für 2025: 551,1 €": an employment "gilt als geringfügig,
wenn daraus im Kalendermonat kein höheres Entgelt als 551,10 € gebührt" (no employee contributions). -/
def geringfuegig : Int := 55110
/-- ASVG § 45 Abs. 1, § 108 Abs. 3 with Anm. 2 "gemäß BGBl. II Nr. 417/2024 für 2025: 215,00 €" daily
Höchstbeitragsgrundlage; a full month counts 30 days (§ 45 Abs. 1): 6 450 € per month. -/
def hbglDay : Int := 21500
def hbglMonth : Int := 30 * hbglDay
/-- ASVG § 54 Abs. 1: Sonderzahlungen "bis zum 60fachen Betrag der … Höchstbeitragsgrundlage" a year (12 900 €);
AMPFG § 2 Abs. 2 uses the same ceiling for the AV. -/
def szCeiling : Int := 60 * hbglDay
/-- ASVG § 51 Abs. 3 Z 1: Krankenversicherung "Beitragsteil des/der Versicherten auf 3,87%". -/
def kvRate : Int := 387
/-- ASVG § 51 Abs. 3 Z 2: Pensionsversicherung "des (der) Versicherten auf 10,25%". -/
def pvRate : Int := 1025
/-- AMPFG § 2 Abs. 1 and 3: Arbeitslosenversicherungsbeitrag "5,9 vH", "zu gleichen Teilen zu tragen": 2,95 %. -/
def avRateFull : Int := 295
/-- AMPFG § 2a Abs. 1 (base amounts 1 648 / 1 798 / 1 948 €, in force July 2018, § 10 Abs. 66, 68) raised by Abs. 2
"jährlich mit der Aufwertungszahl gemäß § 108a ASVG … kaufmännisch auf volle Eurobeträge zu runden" with the
Aufwertungszahlen 2019-2025 (1,020 1,031 1,033 1,021 1,031 1,035 1,063; ASVG § 108a Anm. 1): 2 074 / 2 262 /
2 451 € (computed, `harness/ampfg_chain.py`). Employee share 0 / 1 / 2 % below them. -/
def avStep1 : Int := 207400
def avStep2 : Int := 226200
def avStep3 : Int := 245100
/-- AKG 1992 § 61 Abs. 2: Arbeiterkammerumlage "höchstens 0,5% der für die gesetzliche Krankenversicherung geltenden
allgemeinen Beitragsgrundlage" up to the Höchstbeitragsgrundlage (charged at the maximum by every chamber). -/
def akRate : Int := 50
/-- WBFG 2018 § 2 Abs. 1 and 3: Wohnbauförderungsbeitrag on the "allgemeine Beitragsgrundlage in der
Krankenversicherung", employer pays "eine Abgabe in gleicher Höhe"; the rate is Land law (Abs. 2). 0,5 % employee
share (1 % in total) is the rate of every Land in 2025 (assumption checked against the OECD's EECSSC, which it
reproduces to the cent; the Land laws were not read). -/
def wbfRate : Int := 50

/-- ASVG § 73 Abs. 1 Z 1: KV on pensions "5,1%" (Fassung vom 01.01.2025) and "6%" from 1 June 2025 (§ 809 Abs. 1
Z 2, BGBl. I Nr. 20/2025). Sonderzahlungen in April and October (§ 105 Abs. 1). -/
def kvPenOld : Int := 510
def kvPenNew : Int := 600

/-! ## Self-employed (GSVG) -/

/-- GSVG § 27 Abs. 1a Z 1: KV "Leistungen der Pflichtversicherten in der Höhe von 6,8 %". -/
def gsvgKv : Int := 680
/-- GSVG § 27 Abs. 2 Z 1: PV "18,5 %". -/
def gsvgPv : Int := 1850
/-- GSVG § 25 Abs. 4: Mindestbeitragsgrundlage = ASVG § 5 Abs. 2 amount (551,10 € per month in 2025). -/
def gsvgMinMonth : Int := geringfuegig
/-- GSVG § 48 with Anm. 1 "gemäß BGBl. II Nr. 417/2024 für 2025: 7 525,00 €" per month. -/
def gsvgMaxMonth : Int := 752500
/-- ASVG § 74 Abs. 1 Z 1 with Anm. 1 "gemäß BGBl. II Nr. 417/2024 für 2025: 12,07 €" a month (Unfallversicherung). -/
def gsvgUvMonth : Int := 1207

/-! ## Family benefits (FLAG 1967) -/

/-- FLAG § 8 Abs. 2 Z 3 with Anm. 1-4 "gemäß BGBl. II Nr. 314/2024 … für 2025: 138,4 € / 148 € / 171,8 € /
200,4 €": monthly Familienbeihilfe from birth, from the month the child turns 3, 10, 19. -/
def fbByAge (age : Nat) : Int :=
  if age < 3 then 13840 else if age < 10 then 14800 else if age < 19 then 17180 else 20040
/-- FLAG § 8 Abs. 3 Z 3 with Anm. 5-10 (2025): per child and month when paid for 2 / 3 / 4 / 5 / 6 / 7+ children:
8,6 / 21,1 / 32,1 / 38,9 / 43,4 / 63,1 €. -/
def geschwister (n : Nat) : Int :=
  if n ≤ 1 then 0 else if n = 2 then 860 else if n = 3 then 2110 else if n = 4 then 3210
  else if n = 5 then 3890 else if n = 6 then 4340 else 6310
/-- FLAG § 8 Abs. 8 with Anm. 12 "für 2025: 121,4 €": once for each child aged 6 to 15 (Schulstartgeld). -/
def schulstart : Int := 12140
/-- FLAG § 9 with Anm. 1 "für 2025: 24,4 €" monthly Mehrkindzuschlag for the third and each further child. -/
def mkzMonth : Int := 2440
/-- FLAG § 9a Abs. 1: only if the "zu versteuernde Einkommen (§ 33 Abs. 1 EStG 1988)" of the parent and partner
"55 000 € nicht übersteigt" (of the previous year; the model uses the current year). -/
def mkzLimit : Int := 5500000


/-! ## Tax years 2022-2024 (improvement round 4, 2026-11-19)

Every year-dependent amount, collected per tax year. Sources (RIS consolidated versions, copies in
`~/cmp20/improve-central/refs/at/`):
* EStG 1988 "Fassung vom 01.09.2022" (2022 amounts), "01.07.2023" (2023), "01.07.2024" (2024); the year-end
  versions (31.12.2022 / 31.12.2023) already print the next year's amounts, so the mid-year versions are used.
  § 124b Z 390 (2022: the 35 % → 30 % cut "für das gesamte Kalenderjahr ein Steuersatz von 32,5%"), Z 391 (2023:
  42 % → 40 %, "für das gesamte Kalenderjahr ein Steuersatz von 41%"), Z 392 (Familienbonus Plus 166,68 € from
  January 2022), Z 394 (Kindermehrbetrag 550 € for 2022), Z 407 (2022 Teuerungsabsetzbetrag 500 € and the 2022
  SV-Rückerstattung of 70 %, at most 1 550 €), Z 449 (§ 41 Abs. 4 / § 67 Abs. 1: 2 447 € and 2 330 € for 2024).
  Kinderabsetzbetrag: 58,40 € (2022, § 33 Abs. 3 Z 1), 61,8 € (2023, BGBl. II Nr. 413/2022), 67,80 € (2024).
* ASVG: the annual ordinances BGBl. II Nr. 590/2021 (2022), 459/2022 (2023), 407/2023 (2024) (`bgbl_*.txt`):
  "die tägliche Höchstbeitragsgrundlage auf Grund des § 108 Abs. 3 ASVG mit 189,00 € / 195,00 € / 202,00 €";
  "im § 5 Abs. 2 statt 475,86 € mit 485,85 €" / "statt 485,85 € mit 500,91 €" / "statt 500,91 € mit 518,44 €";
  GSVG § 48 maximum 6 615 / 6 825 / 7 070 € a month; ASVG § 74 Abs. 1 Z 1 10,64 / 10,97 / 11,35 €; Aufwertungszahl
  1,021 / 1,031 / 1,035. ASVG § 51 Abs. 3 (3,87 % KV, 10,25 % PV) in the 2022-09-01, 2023-07-01, 2024-07-01 versions.
* AMPFG § 2 Abs. 1: "6 vH" (versions 2022-09-01, 2023-07-01), "5,9 vH" from 1 January 2024 (§ 10 Abs. 83,
  Budgetbegleitgesetz 2024, BGBl. I Nr. 152/2023); § 2a thresholds by the Aufwertungszahl chain
  (`harness/ampfg_chain.py`): 1 828 / 1 994 / 2 161 € (2022), 1 885 / 2 056 / 2 228 € (2023), 1 951 / 2 128 / 2 306 € (2024).
* FLAG 1967 § 8 Abs. 2, 3, 8, 10 and § 9 (versions 2022-09-01, 2023-07-01, 2024-07-01; RIS Anm. 1-12 with
  BGBl. II Nr. 413/2022 for 2023 and Nr. 328/2023 for 2024); § 8 Abs. 10: "Die Familienbeihilfe erhöht sich für den
  August 2022 um eine Einmalzahlung von 180 Euro für jedes Kind".
-/

/-- The amounts that change between tax years (cents, bp). -/
structure YP where
  year : Nat
  tariff : Schedule
  fbpU18 : Int
  fbp18 : Int
  kabMonth : Int
  avab1 : Int
  avab2 : Int
  avabMore : Int
  avabPartnerLimit : Int
  vab : Int
  zuschlag : Taper
  zuschlagEnd : Int
  pab : Taper
  pabHigh : Taper
  pabPartnerLimit : Int
  kmbPerChild : Int
  svrRate : Int
  svrMax : Int
  svBonus : Int
  svrPenRate : Int
  svrPenMax : Int
  /-- § 124b Z 407 (2022 only): Teuerungsabsetzbetrag for those entitled to the Verkehrsabsetzbetrag -/
  tabWage : Taper
  szFreigrenze : Int
  szGlideStart : Int
  gfbBase : Int
  geringfuegig : Int
  hbglDay : Int
  hbglMonth : Int
  szCeiling : Int
  avRateFull : Int
  avStep1 : Int
  avStep2 : Int
  avStep3 : Int
  kvPenOld : Int
  kvPenNew : Int
  gsvgMaxMonth : Int
  gsvgUvMonth : Int
  fb0 : Int
  fb3 : Int
  fb10 : Int
  fb19 : Int
  gs2 : Int
  gs3 : Int
  gs4 : Int
  gs5 : Int
  gs6 : Int
  gs7 : Int
  schulstart : Int
  mkzMonth : Int
  /-- FLAG § 8 Abs. 10: one-off amount per child in the year -/
  fbOneOff : Int

/-- No allowance (a taper with nothing to withdraw). -/
def noTaper : Taper := { full := 0 }

/-- 2025: exactly the constants above (so every 2025 result is unchanged). -/
def yp2025 : YP :=
  { year := 2025, tariff := tariff, fbpU18 := fbpMonthUnder18, fbp18 := fbpMonth18, kabMonth := kabMonth,
    avab1 := 60100, avab2 := 81300, avabMore := 26800, avabPartnerLimit := avabPartnerLimit, vab := vab,
    zuschlag := zuschlag, zuschlagEnd := zuschlagEnd, pab := pab, pabHigh := pabHigh,
    pabPartnerLimit := pabPartnerLimit, kmbPerChild := kmbPerChild, svrRate := svrRate, svrMax := svrMax,
    svBonus := svBonus, svrPenRate := svrPenRate, svrPenMax := svrPenMax, tabWage := noTaper,
    szFreigrenze := szFreigrenze, szGlideStart := szGlideStart, gfbBase := gfbBase, geringfuegig := geringfuegig,
    hbglDay := hbglDay, hbglMonth := hbglMonth, szCeiling := szCeiling, avRateFull := avRateFull,
    avStep1 := avStep1, avStep2 := avStep2, avStep3 := avStep3, kvPenOld := kvPenOld, kvPenNew := kvPenNew,
    gsvgMaxMonth := gsvgMaxMonth, gsvgUvMonth := gsvgUvMonth,
    fb0 := 13840, fb3 := 14800, fb10 := 17180, fb19 := 20040,
    gs2 := 860, gs3 := 2110, gs4 := 3210, gs5 := 3890, gs6 := 4340, gs7 := 6310,
    schulstart := schulstart, mkzMonth := mkzMonth, fbOneOff := 0 }

/-- 2022. EStG (Fassung 01.09.2022) § 33 Abs. 1: "für die ersten 11 000 Euro 0% / … bis 18 000 Euro 20% / … bis
31 000 Euro 30% / … bis 60 000 Euro 42% / … bis 90 000 Euro 48% / über 90 000 Euro 50%", with § 124b Z 390 lit. b
(32,5 % for the whole of 2022 in the Veranlagung). Abs. 3a: 166,68 € / 54,18 €. Abs. 4: AVAB/AEAB 494 / 669 / +220 €,
partner "Einkünfte von höchstens 6 000 Euro". Abs. 5: VAB 400 €, Zuschlag 650 € to 16 000 €, nil at 24 500 €.
Abs. 6: PAB 825 € (17 500-25 500 €), erhöht 1 214 € (19 930-25 500 €), partner 2 200 €. Abs. 7: 550 €. Abs. 8 as
modified for 2022 by § 124b Z 407: "70% der Werbungskosten … höchstens aber 1 550 Euro" (employees), "100% … höchstens
aber 1 050 Euro" (pensioners); Teuerungsabsetzbetrag 500 € to an Einkommen of 18 200 €, nil at 24 500 €.
§ 41 Abs. 4 / § 67 Abs. 1: Freigrenze 2 100 €, "höchstens 30% der 2 000 Euro übersteigenden Bemessungsgrundlage".
§ 10 Abs. 1 Z 3: Grundfreibetrag "Bis zu einer Bemessungsgrundlage von 30 000 Euro". FLAG § 8 Abs. 2: 114 / 121,9 /
141,5 / 165,1 €; Abs. 3: 7,1 / 17,4 / 26,5 / 32 / 35,7 / 52 €; Abs. 8: 100 €; Abs. 10: 180 €; § 9: 20 €. -/
def yp2022 : YP :=
  { year := 2022,
    tariff := Schedule.ofList [(0, 0), (1100000, 2000), (1800000, 3250), (3100000, 4200), (6000000, 4800),
      (9000000, 5000), (100000000, 5500)],
    fbpU18 := 16668, fbp18 := 5418, kabMonth := 5840,
    avab1 := 49400, avab2 := 66900, avabMore := 22000, avabPartnerLimit := 600000, vab := 40000,
    zuschlag := { full := 65000, start := 1600000, num := 65000, den := 2450000 - 1600000 }, zuschlagEnd := 2450000,
    pab := { full := 82500, start := 1750000, num := 82500, den := 2550000 - 1750000 },
    pabHigh := { full := 121400, start := 1993000, num := 121400, den := 2550000 - 1993000 },
    pabPartnerLimit := 220000, kmbPerChild := 55000,
    svrRate := 7000, svrMax := 155000, svBonus := 0, svrPenRate := 10000, svrPenMax := 105000,
    tabWage := { full := 50000, start := 1820000, num := 50000, den := 2450000 - 1820000 },
    szFreigrenze := 210000, szGlideStart := 200000, gfbBase := 3000000,
    geringfuegig := 48585, hbglDay := 18900, hbglMonth := 30 * 18900, szCeiling := 60 * 18900,
    avRateFull := 300, avStep1 := 182800, avStep2 := 199400, avStep3 := 216100,
    kvPenOld := 510, kvPenNew := 510, gsvgMaxMonth := 661500, gsvgUvMonth := 1064,
    fb0 := 11400, fb3 := 12190, fb10 := 14150, fb19 := 16510,
    gs2 := 710, gs3 := 1740, gs4 := 2650, gs5 := 3200, gs6 := 3570, gs7 := 5200,
    schulstart := 10000, mkzMonth := 2000, fbOneOff := 18000 }

/-- 2023. EStG (Fassung 01.07.2023) § 33 Abs. 1: 11 693 / 19 134 / 32 075 / 62 080 / 93 120 €, the fourth band at 41 %
for the whole year (§ 124b Z 391 lit. b). Abs. 3: 61,8 € (BGBl. II Nr. 413/2022). Abs. 3a: 166,68 / 54,18 €.
Abs. 4: 520 / 704 / +232 €, partner 6 312 €. Abs. 5: VAB 421 €, Zuschlag 684 € (16 832-25 774 €). Abs. 6: 868 €
(18 410-26 826 €), erhöht 1 278 € (20 967-26 826 €), partner 2 315 €. Abs. 7: 550 €. Abs. 8: 55 %, 421 € + SV-Bonus
684 €; pensioners 80 %, 579 €. § 41 Abs. 4 / § 67 Abs. 1: 2 100 € / 2 000 €. § 10: 30 000 €. FLAG Anm. "für 2023":
120,6 / 129 / 149,7 / 174,7 €; 7,5 / 18,4 / 28 / 33,9 / 37,8 / 55 €; Schulstartgeld 105,8 €; Mehrkindzuschlag 21,2 €. -/
def yp2023 : YP :=
  { year := 2023,
    tariff := Schedule.ofList [(0, 0), (1169300, 2000), (1913400, 3000), (3207500, 4100), (6208000, 4800),
      (9312000, 5000), (100000000, 5500)],
    fbpU18 := 16668, fbp18 := 5418, kabMonth := 6180,
    avab1 := 52000, avab2 := 70400, avabMore := 23200, avabPartnerLimit := 631200, vab := 42100,
    zuschlag := { full := 68400, start := 1683200, num := 68400, den := 2577400 - 1683200 }, zuschlagEnd := 2577400,
    pab := { full := 86800, start := 1841000, num := 86800, den := 2682600 - 1841000 },
    pabHigh := { full := 127800, start := 2096700, num := 127800, den := 2682600 - 2096700 },
    pabPartnerLimit := 231500, kmbPerChild := 55000,
    svrRate := 5500, svrMax := 42100, svBonus := 68400, svrPenRate := 8000, svrPenMax := 57900,
    tabWage := noTaper,
    szFreigrenze := 210000, szGlideStart := 200000, gfbBase := 3000000,
    geringfuegig := 50091, hbglDay := 19500, hbglMonth := 30 * 19500, szCeiling := 60 * 19500,
    avRateFull := 300, avStep1 := 188500, avStep2 := 205600, avStep3 := 222800,
    kvPenOld := 510, kvPenNew := 510, gsvgMaxMonth := 682500, gsvgUvMonth := 1097,
    fb0 := 12060, fb3 := 12900, fb10 := 14970, fb19 := 17470,
    gs2 := 750, gs3 := 1840, gs4 := 2800, gs5 := 3390, gs6 := 3780, gs7 := 5500,
    schulstart := 10580, mkzMonth := 2120, fbOneOff := 0 }

/-- 2024. EStG (Fassung 01.07.2024) § 33 Abs. 1: 12 816 / 20 818 / 34 513 / 66 612 / 99 266 €, 20 / 30 / 40 / 48 /
50 %. Abs. 3: 67,80 €. Abs. 3a: 166,68 / 58,34 €. Abs. 4: 572 / 774 / +255 €, partner 6 937 €. Abs. 5: VAB 463 €,
Zuschlag 752 € (18 499-28 326 €). Abs. 6: 954 € (20 233-29 482 €), erhöht 1 405 € (23 043-29 482 €), partner 2 545 €.
Abs. 7: 700 €. Abs. 8: 55 %, 463 € + 752 €; pensioners 80 %, 637 €. § 41 Abs. 4 / § 67 Abs. 1 per § 124b Z 449:
2 447 € / 2 330 €. § 10: 33 000 €. AMPFG § 2 Abs. 1 5,9 %. FLAG Anm. "für 2024": 132,3 / 141,5 / 164,2 / 191,6 €;
8,2 / 20,2 / 30,7 / 37,2 / 41,5 / 60,3 €; Schulstartgeld 116,1 €; Mehrkindzuschlag 23,3 €. -/
def yp2024 : YP :=
  { year := 2024,
    tariff := Schedule.ofList [(0, 0), (1281600, 2000), (2081800, 3000), (3451300, 4000), (6661200, 4800),
      (9926600, 5000), (100000000, 5500)],
    fbpU18 := 16668, fbp18 := 5834, kabMonth := 6780,
    avab1 := 57200, avab2 := 77400, avabMore := 25500, avabPartnerLimit := 693700, vab := 46300,
    zuschlag := { full := 75200, start := 1849900, num := 75200, den := 2832600 - 1849900 }, zuschlagEnd := 2832600,
    pab := { full := 95400, start := 2023300, num := 95400, den := 2948200 - 2023300 },
    pabHigh := { full := 140500, start := 2304300, num := 140500, den := 2948200 - 2304300 },
    pabPartnerLimit := 254500, kmbPerChild := 70000,
    svrRate := 5500, svrMax := 46300, svBonus := 75200, svrPenRate := 8000, svrPenMax := 63700,
    tabWage := noTaper,
    szFreigrenze := 244700, szGlideStart := 233000, gfbBase := 3300000,
    geringfuegig := 51844, hbglDay := 20200, hbglMonth := 30 * 20200, szCeiling := 60 * 20200,
    avRateFull := 295, avStep1 := 195100, avStep2 := 212800, avStep3 := 230600,
    kvPenOld := 510, kvPenNew := 510, gsvgMaxMonth := 707000, gsvgUvMonth := 1135,
    fb0 := 13230, fb3 := 14150, fb10 := 16420, fb19 := 19160,
    gs2 := 820, gs3 := 2020, gs4 := 3070, gs5 := 3720, gs6 := 4150, gs7 := 6030,
    schulstart := 11610, mkzMonth := 2330, fbOneOff := 0 }

/-- The parameters of a tax year: 2022, 2023, 2024; 2025 for 2025 and later (as before this round). -/
def ypOf (year : Nat) : YP :=
  if year ≤ 2022 then yp2022 else if year = 2023 then yp2023 else if year = 2024 then yp2024 else yp2025

/-- Years the model implements with their own amounts (`years.json`). -/
def implementedYears : List Nat := [2022, 2023, 2024, 2025]

/-- § 33 Abs. 4 Z 1-2 for a year. -/
def avabAmountY (y : YP) (n : Nat) : Int :=
  if n = 0 then 0 else if n = 1 then y.avab1 else y.avab2 + y.avabMore * ((n : Int) - 2)

/-- FLAG § 8 Abs. 2 for a year. -/
def fbByAgeY (y : YP) (age : Nat) : Int :=
  if age < 3 then y.fb0 else if age < 10 then y.fb3 else if age < 19 then y.fb10 else y.fb19

/-- FLAG § 8 Abs. 3 for a year. -/
def geschwisterY (y : YP) (n : Nat) : Int :=
  if n ≤ 1 then 0 else if n = 2 then y.gs2 else if n = 3 then y.gs3 else if n = 4 then y.gs4
  else if n = 5 then y.gs5 else if n = 6 then y.gs6 else y.gs7

theorem avabAmountY_2025 : ∀ n, n ≤ 8 → avabAmountY yp2025 n = avabAmount n := by decide
theorem fbByAgeY_2025 : ∀ a, a ≤ 30 → fbByAgeY yp2025 a = fbByAge a := by decide
theorem geschwisterY_2025 : ∀ n, n ≤ 12 → geschwisterY yp2025 n = geschwister n := by decide
theorem ypOf_2025 : ypOf 2025 = yp2025 := rfl

end AtTax
