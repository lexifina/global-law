import PlTax.Kernel

/-!
# Parameters for 2025 (amounts in grosze unless the name ends in `Zl`; rates in basis points)

Sources (official texts, fetched 2026-11-19 into `pl/refs/`):
* **PIT** = ustawa z 26 lipca 1991 r. o podatku dochodowym od osób fizycznych, tekst jednolity Dz.U. 2025 poz. 163
  (https://api.sejm.gov.pl/eli/acts/DU/2025/163/text.pdf); also Global law `poland/national/acts/ustawa/1991/350/`
  (record to tekst jednolity Dz.U. 2024 poz. 226; the 2025 provisions used here read the same in both).
* **Ryczałt** = ustawa z 20 listopada 1998 r. o zryczałtowanym podatku dochodowym..., t.j. Dz.U. 2025 poz. 843
  (https://api.sejm.gov.pl/eli/acts/DU/2025/843/text.pdf). Not in Global law as a consolidated act.
* **Zdrowotna** = ustawa z 27 sierpnia 2004 r. o świadczeniach opieki zdrowotnej..., t.j. Dz.U. 2025 poz. 1461
  (https://api.sejm.gov.pl/eli/acts/DU/2025/1461/text.pdf), with art. 4 of the amending act of 2024 quoted in its
  obwieszczenie (75 % of the minimum wage as the 2025 minimum base). Not in Global law as a consolidated act.
* **SUS** = ustawa z 13 października 1998 r. o systemie ubezpieczeń społecznych, t.j. Dz.U. 2025 poz. 350
  (https://api.sejm.gov.pl/eli/acts/DU/2025/350/text.pdf).
* Notices: M.P. 2024 poz. 1051 (ceiling 260 190 zł, prognozowane wynagrodzenie 8673 zł), M.P. 2025 poz. 84 (GUS Q4 2024
  wage with profit payouts 8549,18 zł), M.P. 2024 poz. 1084 (liniowy health deduction limit 12 900 zł), M.P. 2024
  poz. 1055 (IKZE limits 10 407,60 / 15 611,40 zł), Dz.U. 2024 poz. 1362 (minimum wage 4666 zł). URLs:
  https://api.sejm.gov.pl/eli/acts/MP/2024/1051 , .../MP/2025/84 , .../MP/2024/1084 , .../MP/2024/1055 ,
  https://api.sejm.gov.pl/eli/acts/DU/2024/1362 .
-/

namespace PlTax

/-! ## Income tax scale, PIT art. 27 ust. 1
"do 120 000 | 12% minus kwota zmniejszająca podatek 3600 zł ; ponad 120 000 | 10 800 zł + 32% nadwyżki ponad 120 000 zł" -/
def scaleThreshold : Int := 12000000
def rateLow : Int := 1200
def rateHigh : Int := 3200
def kwotaZmniejszajaca : Int := 360000

/-- The scale as kernel bands (on a base in grosze). -/
def plScale : List Band := [⟨0, some scaleThreshold, rateLow⟩, ⟨scaleThreshold, none, rateHigh⟩]

/-! ## Employee costs, PIT art. 22 ust. 2
pkt 1: "250 zł miesięcznie, a za rok podatkowy łącznie nie więcej niż 3000 zł"; pkt 3 (commuter): "300 zł miesięcznie,
a za rok podatkowy łącznie nie więcej niż 3600 zł". -/
def kupAnnual : Int := 300000
def kupCommuterAnnual : Int := 360000
def kupMonthly : Int := 25000
def kupCommuterMonthly : Int := 30000

/-! ## Zero-PIT exemptions, PIT art. 21 ust. 1 pkt 148, 152–154 and ust. 44
"do wysokości nieprzekraczającej w roku podatkowym kwoty 85 528 zł"; ust. 44: the sum of all four "nie może w roku
podatkowym przekroczyć kwoty 85 528 zł". -/
def zeroPitLimit : Int := 8552800

/-! ## Child relief, PIT art. 27f ust. 2
"kwota 92,67 zł" a month for each of the first two children, "166,67 zł na trzecie dziecko", "225 zł na czwarte i każde
kolejne"; one child only when income does not exceed "112 000 zł" (married, or single parent under art. 6 ust. 4c) or
"56 000 zł" (others). -/
def childMonthly12 : Int := 9267
def childMonthly3 : Int := 16667
def childMonthly4 : Int := 22500
def oneChildLimitCouple : Int := 11200000
def oneChildLimitSingle : Int := 5600000

/-! ## Flat rates
art. 30a ust. 1 pkt 3, 4 (interest, dividends) and art. 30b ust. 1 (gains on shares): 19 %; art. 30c ust. 1 (liniowy):
"19% podstawy obliczenia podatku". Ryczałt art. 12 ust. 1 pkt 4: "8,5 % przychodów do kwoty 100 000 zł oraz 12,5 %
przychodów od nadwyżki ponad kwotę 100 000 zł" (rental, art. 6 ust. 1a); pkt 2b: 12 % (IT services, the default
business rate here). -/
def flatRate : Int := 1900
def rentLow : Int := 850
def rentHigh : Int := 1250
def rentThreshold : Int := 10000000
def ryczaltDefaultBp : Int := 1200

/-! ## Deductions
art. 26 ust. 1 pkt 9 lit. a, ust. 5: gifts "nie więcej jednak niż kwoty stanowiącej 6% dochodu"; art. 26 ust. 1 pkt 2b
IKZE, limit per M.P. 2024 poz. 1055: 10 407,60 zł (art. 13a ust. 1 of the IKE/IKZE act), 15 611,40 zł for the
self-employed (ust. 1a); art. 30c ust. 2 pkt 2 + M.P. 2024 poz. 1084: liniowy health deduction "nie może przekroczyć
12 900 zł"; ryczałt art. 11 ust. 1a: "50 % składek na ubezpieczenie zdrowotne". -/
def giftCapBp : Int := 600
def ikzeLimit : Int := 1040760
def ikzeLimitSelf : Int := 1561140
def liniowyHealthCap : Int := 1290000

/-! ## Social insurance (SUS art. 22 ust. 1, art. 16 ust. 1, 1b; art. 19 ust. 1; M.P. 2024 poz. 1051)
Rates: emerytalne 19,52 % (half each: employee 9,76 %), rentowe 8 % (employee 1,5 %), chorobowe 2,45 % (employee only),
wypadkowe 1,67 % (self-employed, standard rate per ZUS). Ceiling for emerytalne + rentowe: "260 190 zł" (30 × 8673 zł).
SUS art. 22 ust. 3 pkt 2: "7,3 % podstawy wymiaru składki jest ewidencjonowana ... na subkoncie" (employee half 3,65 %;
used only to report the OECD's convention, see `oecd_map.py`). -/
def ceiling : Int := 26019000
def eeEmerytalne : Int := 976
def eeRentowe : Int := 150
def eeChorobowe : Int := 245
def subkontoEe : Int := 365
def seEmerytalne : Int := 1952
def seRentowe : Int := 800
def seWypadkowe : Int := 167
def seChorobowe : Int := 245
def funduszPracy : Int := 245
/-- Standard declared base: 60 % of 8673 zł = 5203,80 zł a month (SUS art. 18 ust. 8). -/
def seBaseStandard : Int := 520380
/-- Preferential base: 30 % of the minimum wage 4666 zł = 1399,80 zł a month (SUS art. 18a). No Fundusz Pracy on it. -/
def seBasePreferential : Int := 139980

/-! ## Health insurance (Zdrowotna)
art. 79 ust. 1: "9 % podstawy wymiaru"; art. 79a ust. 1: liniowy "4,9 % podstawy wymiaru"; minimum for skala / liniowy in
2025: 9 % of 75 % of 4666 zł = 9 % × 3499,50 = 314,96 zł a month; ryczałt art. 81 ust. 2e/2f: 60 % / 100 % / 180 % of
8549,18 zł for revenue up to 60 000 / up to 300 000 / above: 461,66 / 769,43 / 1384,97 zł a month. -/
def healthRate : Int := 900
def healthLiniowyRate : Int := 490
def healthMinMonthly : Int := 31496
def ryczHealth1 : Int := 46166
def ryczHealth2 : Int := 76943
def ryczHealth3 : Int := 138497
def ryczBand1 : Int := 6000000
def ryczBand2 : Int := 30000000

/-! ## Cash benefits
800+: ustawa z 11 lutego 2016 r. o pomocy państwa w wychowywaniu dzieci, art. 5 ust. 1 as amended by Dz.U. 2023
poz. 1565 art. 1 pkt 1 ("500,00 zł" → "800,00 zł"), to age 18. Dobry start: rozporządzenie RM Dz.U. 2018 poz. 1061 § 5
ust. 1: "300 zł", once a year for a child starting the school year, up to age 20 (§ 4 ust. 2–3), not for the
pre-school year (§ 6 pkt 2). -/
def benefit800Annual : Int := 960000
def dobryStart : Int := 30000


/-! ## Tax year 2024 (tests round 2, `cmp20/improve-emerging/IMPROVE.md`)

For an employee household 2024 differs from 2025 only in the SUS art. 19 ust. 1 ceiling: M.P. 2023 poz. 1342
(`refs/MP_2023_1342.txt`): "kwota ograniczenia rocznej podstawy wymiaru składek na ubezpieczenia emerytalne i rentowe w
roku 2024 wynosi 234 720 zł". The PIT provisions used (art. 27 ust. 1 scale 12 % / 32 % above 120 000 zł, kwota
zmniejszająca 3 600 zł, art. 22 ust. 2 KUP, art. 27f, art. 21 ust. 1 pkt 148 limit 85 528 zł) read the same in the
tekst jednolity Dz.U. 2024 poz. 226 (cited above); 800+ applies from 1 January 2024 (ustawa Dz.U. 2023 poz. 1565, cited
above); Dobry start unchanged. Not re-parametrised for 2024 (the output says so): IKZE limits, the self-employed bases
and health amounts, the liniowy health cap (2024: 11 600 zł, M.P. 2023 poz. 1456), the ryczałt health bands. -/

def ceilingY (y : Int) : Int := if y = 2024 then 23472000 else ceiling

theorem ceilingY_2025 : ceilingY 2025 = ceiling := rfl


/-! ## Tax year 2023 (tests round 3)

* SUS art. 19 ust. 1 ceiling 2023: M.P. 2022 poz. 1014 (`refs/years/MP_2022_1014.txt`): "kwota ograniczenia rocznej
  podstawy wymiaru składek na ubezpieczenia emerytalne i rentowe w roku 2023 wynosi 208 050 zł".
* Świadczenie wychowawcze 2023: ustawa o pomocy państwa w wychowywaniu dzieci, t.j. Dz.U. 2023 poz. 810, art. 5 ust. 1
  (`refs/years/DU_2023_810.txt`): "w wysokości 500,00 zł miesięcznie na dziecko" (800 zł from 2024: Dz.U. 2023 poz. 1565).
* PIT as in force for 2023, t.j. Dz.U. 2022 poz. 2647 (`refs/years/DU_2022_2647.txt`): art. 27 ust. 1 "do 120 000 /
  12% minus kwota zmniejszająca podatek 3600 zł / 10 800 zł + 32% nadwyżki ponad 120 000 zł", art. 22 ust. 2 (250 zł a
  month), art. 21 ust. 1 pkt 148 ("85 528 zł"): the same as 2024–2025.
Not re-parametrised (said in the output): IKZE limits, the self-employed bases and health amounts, the liniowy cap. -/

def ceilingY3 (y : Int) : Int := if y = 2023 then 20805000 else if y = 2022 then 17766000 else ceilingY y

/-- Świadczenie wychowawcze a year per child, złoty: 500 zł a month in 2023, 800 zł from 2024 (years not modelled: 2025). -/
def benefitChildAnnual (y : Int) : Int := if y = 2023 ∨ y = 2022 then 6000 else 9600


/-! ## Tax year 2022 (tests round 4)

* SUS art. 19 ust. 1 ceiling 2022: M.P. 2021 poz. 1056 (`refs/years/MP_2021_1056.txt`): "w roku 2022 wynosi 177 660 zł".
* Świadczenie wychowawcze 500 zł (the 800 zł amount applies from 2024, Dz.U. 2023 poz. 1565; t.j. Dz.U. 2023 poz. 810 art.
  5 ust. 1 "500,00 zł" — unchanged since 2019).
* The tax: `Scale.lean` (the 12 % scale for the whole of 2022 and the art. 26 refund of Dz.U. 2022 poz. 1265). -/


/-! ## Self-employed contributions 2022–2024 (tests round 7)

* SUS art. 18 ust. 8: standard base 60 % of the prognozowane przeciętne wynagrodzenie of the notices above: 2022 5 922 zł
  (M.P. 2021 poz. 1056) → 3 553,20; 2023 6 935 (M.P. 2022 poz. 1014) → 4 161,00; 2024 7 824 (M.P. 2023 poz. 1342) → 4 694,40.
* SUS art. 18a: preferential base 30 % of the minimum wage: Dz.U. 2021 poz. 1690 § 1 "3010 zł" (2022); Dz.U. 2022 poz. 1952
  § 1 "3490 zł", § 3 "Od dnia 1 lipca 2023 r. … 3600 zł"; Dz.U. 2023 poz. 1893 § 1 "4242 zł", § 3 "Od dnia 1 lipca 2024 r. …
  4300 zł" (`refs/years/DU_*`).
* Zdrowotna (t.j. Dz.U. 2022 poz. 2561) art. 81 ust. 2b/2d: the skala / liniowy health base is at least "minimalnego
  wynagrodzenia obowiązującego w pierwszym dniu roku składkowego" (100 %, before the 2025 change to 75 %): 9 % of 3 010 /
  3 490 / 4 242 zł; ust. 2e: ryczałt bases 60 % / 100 % / 180 % of the GUS fourth-quarter wage with profit payouts: M.P.
  2022 poz. 82 "6221,04 zł", M.P. 2023 poz. 130 "6965,94 zł", M.P. 2024 poz. 82 "7767,85 zł".
* PIT art. 30c ust. 2 cap on the liniowy health deduction: 2022 "8700 zł" (Dz.U. 2022 poz. 1265), 2023 "10 200 zł"
  (M.P. 2022 poz. 1238), 2024 11 600 zł (M.P. 2023 poz. 1456). The calendar year is used for the contribution year (which
  runs February–January) — a simplification the 2025 model also makes. -/

def seBaseStandardY (y : Int) : Int :=
  if y = 2022 then 355320 else if y = 2023 then 416100 else if y = 2024 then 469440 else seBaseStandard

/-- Preferential base for month `m` (grosze). -/
def seBasePreferentialM (y : Int) (m : Nat) : Int :=
  if y = 2022 then 90300 else if y = 2023 then (if m ≤ 6 then 104700 else 108000)
  else if y = 2024 then (if m ≤ 6 then 127260 else 129000) else seBasePreferential

/-- Minimum wage of month `m` (grosze): the preferential base is 30 % of it (SUS art. 18a), so it is that base x 10 / 3:
2022 3 010 zł; 2023 3 490 / 3 600 zł; 2024 4 242 / 4 300 zł; 2025 4 666 zł (Dz.U. 2024 poz. 1362 § 1). -/
def minWageM (y : Int) (m : Nat) : Int := seBasePreferentialM y m * 10 / 3

#guard minWageM 2025 1 = 466600 ∧ minWageM 2023 7 = 360000 ∧ minWageM 2024 1 = 424200 ∧ minWageM 2022 3 = 301000

def healthMinMonthlyY (y : Int) : Int :=
  if y = 2022 then 27090 else if y = 2023 then 31410 else if y = 2024 then 38178 else healthMinMonthly

/-- GUS fourth-quarter wage of the previous year (grosze), for the ryczałt bands. -/
def ryczAvgQ4 (y : Int) : Int :=
  if y = 2022 then 622104 else if y = 2023 then 696594 else if y = 2024 then 776785 else 854918

def ryczHealthY (y : Int) (band : Nat) : Int :=
  if y ≥ 2025 ∨ y < 2022 then (if band = 1 then ryczHealth1 else if band = 2 then ryczHealth2 else ryczHealth3)
  else pctGr (if band = 1 then pctGr (ryczAvgQ4 y) 6000 else if band = 2 then ryczAvgQ4 y else pctGr (ryczAvgQ4 y) 18000) healthRate

def liniowyHealthCapY (y : Int) : Int :=
  if y = 2022 then 870000 else if y = 2023 then 1020000 else if y = 2024 then 1160000 else liniowyHealthCap

theorem ryczHealth_2022 : ryczHealthY 2022 1 = 33594 ∧ ryczHealthY 2022 2 = 55989 ∧ ryczHealthY 2022 3 = 100781 := by decide
theorem ryczHealth_2025_same : ryczHealthY 2025 1 = ryczHealth1 := rfl

end PlTax
