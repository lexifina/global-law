import DeTax.Tariff

/-!
# The amounts German law fixes for VZ 2025

Each amount is copied from the provision that fixes it, in its wording for 2025 (`law/2025/`; gesetze-im-internet.de
XML of 2026-11-18 for provisions unchanged since 2025-01-01, the germany-law record at 2025-07-01 for the others).
Euro amounts are whole euros unless the name ends in `C` (cents); rates are in basis points (1 bp = 0,01 %).
-/

namespace DeTax.P

/-! ## Einkommensteuergesetz -/

/-- § 9a Satz 1 Nr. 1 Buchstabe a: "ein Arbeitnehmer-Pauschbetrag von 1 230 Euro". -/
def arbeitnehmerPausch : Int := 1230
/-- § 9a Satz 1 Nr. 3: "von den Einnahmen im Sinne des § 22 Nummer 1, 1a und 5: ein Pauschbetrag von insgesamt
102 Euro". -/
def wkPausch22 : Int := 102
/-- § 20 (9) Satz 1–2: "ein Betrag von 1 000 Euro abzuziehen (Sparer-Pauschbetrag)"; "Ehegatten, die zusammen
veranlagt werden, wird ein gemeinsamer Sparer-Pauschbetrag von 2 000 Euro gewährt". -/
def sparerPausch : Int := 1000
/-- § 10c: "ein Pauschbetrag von 36 Euro ... (Sonderausgaben-Pauschbetrag)"; doubled for joint assessment. -/
def sonderausgabenPausch : Int := 36
/-- § 10 (3) Satz 1: Vorsorgeaufwendungen nach Absatz 1 Nummer 2 "bis zu dem Höchstbeitrag zur knappschaftlichen
Rentenversicherung, aufgerundet auf einen vollen Betrag in Euro". 2025: 24,7 % (RVBeitrSBek 2025) of 118 800 €
(SVBezGrV 2025 § 4 (1) Nr. 2) = 29 343,60 €, aufgerundet 29 344 €. `hb10_3_ok` checks the arithmetic. -/
def hb10_3 : Int := 29344
theorem hb10_3_ok : hb10_3 = cdiv (2470 * 118800) 10000 := by decide
/-- § 10 (4) Satz 1–2: "bis 2 800 Euro"; "1 900 Euro bei Steuerpflichtigen, die ... ohne eigene Aufwendungen einen
Anspruch auf ... Erstattung oder Übernahme von Krankheitskosten haben oder für deren Krankenversicherung Leistungen
im Sinne des § 3 Nummer 9, 14, 57 oder 62 erbracht werden". -/
def hb10_4 : Int := 2800
def hb10_4Employee : Int := 1900
/-- § 10 (1) Nr. 3 Buchstabe a Satz 4: "ist der jeweilige Beitrag um 4 Prozent zu vermindern" (Krankengeld). -/
def kvKrankengeldCutBp : Int := 400
/-- § 10b (1) Satz 1 Nr. 1: "bis zu 20 Prozent des Gesamtbetrags der Einkünfte". -/
def spendenQuoteBp : Int := 2000
/-- § 24b (2): "4 260 Euro"; "erhöht sich ... um 240 Euro je weiterem Kind". -/
def entlastungAE : Int := 4260
def entlastungAEWeiteres : Int := 240
/-- § 32 (6) Satz 1 (VZ 2025): "ein Freibetrag von 3 336 Euro für das sächliche Existenzminimum des Kindes
(Kinderfreibetrag) sowie ein Freibetrag von 1 464 Euro für den Betreuungs- und Erziehungs- oder
Ausbildungsbedarf"; Satz 2: doubled for jointly assessed parents. -/
def kinderfreibetrag : Int := 3336
def bea : Int := 1464
/-- § 66 (1) (VZ 2025): "Das Kindergeld beträgt monatlich für jedes Kind 255 Euro." -/
def kindergeldMonat : Int := 255
/-- § 32d (1) Satz 1: "Die Einkommensteuer für Einkünfte aus Kapitalvermögen ... beträgt 25 Prozent." -/
def abgeltungBp : Int := 2500

/-- § 22 Nr. 1 Satz 3 Buchstabe a Doppelbuchstabe aa, table "Jahr des Rentenbeginns / Besteuerungsanteil in %"
(wording since the Wachstumschancengesetz): "bis 2005: 50,0", "ab 2006: 52,0" ... "2020: 80,0", "2021: 81,0",
"2022: 82,0", "2023: 82,5", "2024: 83,0", "2025: 83,5", ... "2058: 100,0". In tenths of a per cent. -/
def besteuerungsanteil (rentenbeginn : Int) : Int :=
  if rentenbeginn ≤ 2005 then 500
  else if rentenbeginn ≤ 2020 then 500 + 20 * (rentenbeginn - 2005)
  else if rentenbeginn ≤ 2022 then 800 + 10 * (rentenbeginn - 2020)
  else if rentenbeginn ≤ 2058 then 820 + 5 * (rentenbeginn - 2022)
  else 1000

/-- § 24a Satz 5, table: for "Das auf die Vollendung des 64. Lebensjahres folgende Kalenderjahr" `j`, the
Altersentlastungsbetrag "in % der Einkünfte" (here in tenths of a per cent) and the "Höchstbetrag in Euro":
2005: 40,0 / 1 900; ... 2020: 16,0 / 760; 2021: 15,2 / 722; 2022: 14,4 / 684; 2023: 14,0 / 665;
2024: 13,6 / 646; 2025: 13,2 / 627; ... 2058: 0,0 / 0. -/
def altersentlastung (j : Int) : Int × Int :=
  if j ≤ 2005 then (400, 1900)
  else if j ≤ 2020 then (400 - 16 * (j - 2005), 1900 - 76 * (j - 2005))
  else if j ≤ 2022 then (160 - 8 * (j - 2020), 760 - 38 * (j - 2020))
  else if j ≤ 2058 then (144 - 4 * (j - 2022), 684 - 19 * (j - 2022))
  else (0, 0)

/-! ## Solidaritätszuschlaggesetz 1995 (2025 wording) -/

/-- § 4 Satz 1: "5,5 Prozent der Bemessungsgrundlage"; Satz 2: "nicht mehr als 11,9 Prozent des
Unterschiedsbetrages". In tenths of a per cent. -/
def soliRate : Int := 55
def soliMilderung : Int := 119
/-- § 3 (3) Satz 1: Freigrenze "1. in den Fällen des § 32a Absatz 5 und 6 ... 39 900 Euro, 2. in anderen Fällen
19 950 Euro". -/
def soliFreigrenze (joint : Bool) : Int := if joint then 39900 else 19950

/-! ## Social insurance (2025) -/

/-- RVBeitrSBek 2025: "in der allgemeinen Rentenversicherung 18,6 Prozent"; half borne by the employee
(SGB VI § 168 (1) Nr. 1). -/
def rvEmployeeBp : Int := 930
/-- SGB III § 341 (2): "Der Beitragssatz beträgt 2,6 Prozent"; half by the employee (§ 346 (1)). -/
def avEmployeeBp : Int := 130
/-- SGB V § 241: "Der allgemeine Beitragssatz beträgt 14,6 Prozent"; § 249 (1): "jeweils zur Hälfte". -/
def kvEmployeeBp : Int := 730
/-- Durchschnittlicher Zusatzbeitragssatz 2025 (SGB V § 242a (2), BMG-Bekanntmachung): 2,5 %; the PAP 2025 uses it
for the employer's share of private insurance ("KVSATZAG = 0.0125 + 0.07"). Employee half: 1,25 %. -/
def kvZusatzBp : Int := 250
/-- SGB V § 243: "Der ermäßigte Beitragssatz beträgt 14,0 Prozent" (no Krankengeld). -/
def kvErmaessigtBp : Int := 1400
/-- PBAV 2025 § 1 (1): PV "Beitragssatz ... zum 1. Januar 2025 auf 3,6 Prozent"; employee half 1,8 %
(SGB XI § 58 (1)); § 55 (3): "Beitragszuschlag in Höhe von 0,6 Beitragssatzpunkten" for the childless after age 23
(not for those born before 1940); "für jedes Kind ab dem zweiten Kind bis zum fünften Kind um jeweils einen
Abschlag in Höhe von 0,25 Beitragssatzpunkten" while the child is under 25. -/
def pvBp : Int := 360
def pvEmployeeBp : Int := 180
def pvKinderlosBp : Int := 60
def pvAbschlagBp : Int := 25
/-- SVBezGrV 2025 § 4 (1) Nr. 1: BBG allgemeine RV "96 600 Euro jährlich" (also AV: SGB III § 341 (4));
§ 2 (2): Jahresarbeitsentgeltgrenze § 6 (7) SGB V "66 150 Euro", which is the KV/PV BBG (SGB V § 223 (3),
SGB XI § 55 (2)). -/
def bbgRV : Int := 96600
def bbgKV : Int := 66150
/-- SGB IV § 8 (1a): Geringfügigkeitsgrenze 2025 = Mindestlohn 12,82 € × 130 / 3, aufgerundet: 556 € a month. -/
def minijobMonat : Int := 556
theorem minijob_ok : minijobMonat = cdiv (1282 * 130) 300 := by decide
/-- SGB IV § 20 (2): Übergangsbereich up to "2 000 Euro im Monat". -/
def uebergangOG : Int := 2000
/-- SGB IV § 20 (2a) Satz 2: "der Faktor, der sich berechnet, indem der Wert 28 Prozent geteilt wird durch den
Gesamtsozialversicherungsbeitragssatz": 2025: 18,6 + 3,6 + 2,6 + 14,6 + 2,5 = 41,9 %, F = 0,6683 (BMAS
Bekanntmachung for 2025). In ten-thousandths. -/
def faktorF : Int := 6683
theorem faktorF_ok : faktorF = rndHalf (280 * 10000) (186 + 36 + 26 + 146 + 25) := by decide
/-- SVBezGrV 2025 § 1: Bezugsgröße "3 745 Euro" a month. SGB V § 240 (4): voluntary members' minimum base
"der neunzigste Teil der monatlichen Bezugsgröße" per calendar day = 1 248,33 € a month (14 980 € a year);
SGB V § 10 (1) Nr. 5: family insurance while income is at most one seventh of the monthly Bezugsgröße (535 €). -/
def bezugsgroesseMonat : Int := 3745
def mindestBemessungJahrC : Int := 1498000
def familienversicherungMonat : Int := 535

end DeTax.P
