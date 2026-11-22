import TaxKernel

/-!
# Romania 2025: parameters, each with its source

Statute: Codul fiscal (Legea nr. 227/2015), read in Global law as in force on the dates named
(`romania/national/acts/lege/2015/227/art-NNN.md`; official consolidated text
https://legislatie.just.ro/Public/DetaliiDocument/171282 and the dated versions named in `law/*.txt`).
Money in whole lei (RON); rates in basis points. Every figure below is quoted from the text saved under `law/`.
-/

namespace RoTax
open TaxKernel

/-! ## Minimum wage -/

/-- HG nr. 1.506/2024 (MO nr. 1185 din 28.11.2024): "4.050 lei lunar" from 1 January 2025 (quoted by CCR Decizia
nr. 287/2026 §112, `romania/national/acts/jurisprudenta/ccr/2026/287/decizie.md`); unchanged until 30 June 2026
(HG nr. 146/2026 sets 4.325 lei from 1 July 2026). EUROMOD CR RO (Y16) §2.5.3 uses 4.050 lei for 2025. -/
def minWage2025 : Int := 4050

/-! ## Income tax: rates (art. 64, 97, 84) -/

/-- art. 64 alin. (1): "Cota de impozit este de 10% și se aplică asupra venitului impozabil" (wages lit. b, rents
lit. c, investments lit. d, pensions lit. e). -/
def taxRate : Int := 1000

/-- art. 97 alin. (1)-(2): interest "se impun cu o cotă de 10% din suma acestora, impozitul fiind final". -/
def interestRate : Int := 1000

/-- art. 97 alin. (7) as amended by OUG nr. 156/2024 (in force 2025-01-01): dividends "se impozitează cu o cotă de 10%
din suma acestora, impozitul fiind final". 8 % for dividends distributed in 2024; 16 % for dividends distributed from
1 January 2026 (Legea nr. 141/2025 art. II pct. 5 with art. VII alin. (1) lit. c)). -/
def dividendRate2025 : Int := 1000
def dividendRate2024 : Int := 800

/-- Audit round 8: art. 97 alin. (7) as in force 2024-12-31 (`law/art-097_2024-12-31.txt`, legislatie.just.ro
262796 via its archived copy): "se impozitează cu o cotă de 8% din suma acestora, impozitul fiind final", "Last
changed by OG nr. 16/2022, in force 2023-01-01": dividends distributed in 2023 and 2024 are taxed at 8 %. The 2022
rate (before OG 16/2022) is not in a fetched text: tax year 2022 keeps the 2025 rate and says so. -/
def dividendRateForYear (y : Nat) : Int :=
  if y = 2023 ∨ y = 2024 then dividendRate2024 else dividendRate2025

theorem dividendRateForYear_2025 : dividendRateForYear 2025 = dividendRate2025 := by decide
def dividendRate2026 : Int := 1600

/-- art. 97 alin. (8^1) lit. a) pct. (i): gains on securities through a Romanian intermediary (art. 96^1) "cote de 1%
asupra fiecărui câștig ... dobândite și înstrăinate într-o perioadă mai mare de 365 de zile"; pct. (ii) 3 % under
365 days. Gains through a non-resident intermediary: 10 % of the annual net gain (art. 64 alin. (1) lit. d, art. 94-96). -/
def gainRateLong : Int := 100
def gainRateShort : Int := 300

/-- art. 84 alin. (3): rent net income "prin deducerea din venitul brut a cheltuielilor determinate prin aplicarea
cotei de 20% asupra venitului brut". -/
def rentForfeit : Int := 2000

/-! ## Wages: deducere personală (art. 77, wording of OG nr. 16/2022, in force 2023-01-01, unchanged in 2025) -/

/-- art. 77 alin. (3): the basic deduction for "un venit lunar brut de până la 2.000 de lei peste nivelul salariului
de bază minim brut pe țară". -/
def dedBand : Int := 2000

/-- art. 77 alin. (10) lit. a): "15% din salariul de bază minim brut ... pentru persoanele fizice cu vârsta de până la
26 de ani", wages up to the level of alin. (3). -/
def youngPct : Int := 1500
def youngAge : Nat := 26

/-- art. 77 alin. (10) lit. b): "100 de lei lunar pentru fiecare copil cu vârsta de până la 18 ani, dacă acesta este
înscris într-o unitate de învățământ, părintelui ... indiferent de nivelul acestora"; one parent only (alin. (12)). -/
def schoolChildDed : Int := 100

/-- art. 77 alin. (5): a dependant's income must not exceed monthly "20% din salariul de bază minim brut". -/
def dependantPct : Int := 2000

/-- art. 77 alin. (7): "Copiii minori, în vârstă de până la 18 ani împliniți, ai contribuabilului sunt considerați
întreținuți"; alin. (6): for minor children the deduction goes to "fiecărui contribuabil în întreținerea căruia/cărora
se află aceștia" (both parents). -/
def minorAge : Nat := 18

/-! ## Wages: the 2025 non-taxable 300 lei (OUG nr. 156/2024 art. LXVI, outside the Codul fiscal) -/

/-- OUG nr. 156/2024 art. LXVI alin. (1): "nu se datorează impozit pe venit și nu se cuprinde în baza lunară de calcul
al contribuțiilor sociale obligatorii suma de 300 lei/lună" if (a) the contractual base salary "este egal cu nivelul
salariului minim brut" and (b) the gross wage "nu depășește nivelul de 4.300 lei inclusiv"; alin. (6): "lunilor
ianuarie-decembrie 2025 inclusiv". -/
def untaxed2025 : Int := 300
def untaxedCeiling2025 : Int := 4300

/-! ## Employee contributions (art. 138, 156) -/

/-- art. 138 lit. a): CAS "25% datorată de către persoanele fizice care au calitatea de angajați". No ceiling for
employees (art. 139). -/
def casRate : Int := 2500

/-- art. 156: CASS "este de 10%". -/
def cassRate : Int := 1000

/-! ## Pensions (art. 100, 157^6; Legea nr. 141/2025) -/

/-- art. 100 alin. (1): "suma neimpozabile lunare de 3.000 lei". -/
def pensionAllow : Int := 3000

/-- art. 157^6 (Legea nr. 141/2025 art. II pct. 25, applied "începând cu veniturile aferente lunii august 2025", art.
VII alin. (1) lit. e), until 31 Dec 2027, alin. (3)): CASS base "deducerea din venitul din pensie a sumei lunare de
3.000 lei"; art. 100 alin. (1) as amended deducts the CASS before the tax. First month of the new rule: -/
def pensionCassFirstMonth : Nat := 8

/-! ## Non-wage income: CASS (art. 170, 174) and CAS (art. 148) for 2025 -/

/-- art. 170 alin. (2)-(3): CASS on income from art. 155 lit. c)-h) (rents, investments, ...) on a base of 6, 12 or 24
minimum wages when the income reaches 6, 12 or 24 minimum wages. -/
def cassBands : List Int := [6, 12, 24]

/-- art. 170 alin. (1): independent activities: base = net income, "nu poate fi mai mare decât ... 60 de salarii
minime brute pe țară"; art. 174 alin. (6): topped up to 6 minimum wages unless alin. (7) applies. -/
def cassPfaCap : Int := 60
def cassPfaFloor : Int := 6

/-- art. 148 alin. (1)-(2): CAS for independent activities: due when net income reaches 12 minimum wages, base at least
12 (income in [12, 24) minimum wages) or 24 minimum wages (income at least 24). -/
def casPfaLow : Int := 12
def casPfaHigh : Int := 24

/-! ## Child benefit (Legea nr. 61/1993) -/

/-- Legea nr. 61/1993 art. 3 alin. (1)-(2): indexed yearly by inflation since January 2023; alin. (5) rounding "la leu
în favoarea beneficiarului". Amounts for 2025: 719 lei (under 2) and 292 lei (2-18): indexation suspended in 2025
(EUROMOD Country Report Romania 2022-2025, Y16, Table 2.4, p. 37; Eurostat earn_nt_net 2025 FAM = 7.008 lei a year
for two children = 2 x 292 x 12). -/
def allowanceUnder2 : Int := 719
def allowance2to18 : Int := 292

/-! ## Company side (owner-manager scans) -/

/-- art. 17: "Cota de impozit pe profit ... este de 16%". -/
def citRate : Int := 1600
/-- art. 51 alin. (1): micro-enterprise tax 1 % (revenue up to 60.000 euro, not the listed CAEN codes) or 3 %. -/
def microLow : Int := 100
def microHigh : Int := 300
/-- art. 47 alin. (1) lit. c): revenue "nu au depășit echivalentul în lei a 250.000 euro, respectiv 100.000 euro
începând cu 1 ianuarie 2026"; lit. g) at least one employee. -/
def microCeilingEur2025 : Int := 250000
def microCeilingEur2026 : Int := 100000

/-- Basis points of `x`, rounded half up to the leu (the rounding observed in every published 2025-2026 payroll figure;
HG nr. 1/2016 norms to art. 64: bases rounded "la un leu, prin neglijarea fracțiunilor de până la 50 de bani
inclusiv sau prin majorarea fracțiunilor ce depășesc 50 de bani"). -/
def pctOf (p x : Int) : Int := divR .halfUp (p * x) BP

/-! ## Earlier years 2022-2024 (round 2, 2026-11-19; texts under `law/r2/`)

* Minimum wage (Global law read_law of each HG, art. 1): HG nr. 1071/2021 "Începând cu data de 1 ianuarie 2022 ...
  2.550 lei lunar"; HG nr. 1447/2022 "Începând cu data de 1 ianuarie 2023 ... 3.000 lei lunar"; HG nr. 900/2023
  "Începând cu data de 1 octombrie 2023 ... 3.300 lei lunar"; HG nr. 598/2024 "Începând cu data de 1 iulie 2024 ...
  3.700 lei lunar".
* Non-taxable sum for minimum-wage earners: OUG nr. 168/2022 art. XXXVII alin. (1) (`law/r2/oug168_2022_art037.txt`):
  "începând cu data de 1 ianuarie 2023 ... nu se datorează impozit pe venit și nu se cuprinde în baza lunară de calcul
  al contribuțiilor sociale obligatorii suma de 200 lei/lună" if the base salary "este egal cu nivelul salariului minim
  brut pe țară garantat în plată ... în vigoare în luna căreia îi sunt aferente veniturile" and the gross "nu depășește
  nivelul de 4.000 lei inclusiv"; alin. (6) "lunilor ianuarie-decembrie 2023 inclusiv". OUG nr. 115/2023 art. LXXIII
  (official PDF `law/r2/OUG_115_2023.pdf`, ANAF): the same, 200 lei, 4.000 lei, "ianuarie - decembrie 2024"; OUG nr.
  59/2024 art. II (`law/r2/OUG_59_2024.pdf`): "Începând cu veniturile ... aferente lunii iulie 2024, suma de 200
  lei/lună ... prevăzută la art. LXXIII alin. (1), (4) şi (5) din [OUG nr. 115/2023] ... se majorează la nivelul de
  300 lei/lună" (the 4.000 lei ceiling of alin. (1) lit. b) is unchanged). 2022: no such sum found (Global law phrase
  search, all acts; OUG nr. 130/2021 read in full): none modelled.
* Personal deduction: 2023 and 2024 have the OG nr. 16/2022 wording (art. 77 as in force 2024-06-30: "Last changed by
  OG nr. 16/2022, in force 2023-01-01"), i.e. the 2025 table, young and school deductions with that month's minimum
  wage; 2022: `Deduction2022.lean`.
* CAS 25 % (art. 138 lit. a)) and CASS 10 % (art. 156, unchanged since OUG nr. 79/2017, `law/hist/art-156.txt`) in all
  years; tax 10 % (art. 64, unchanged since 2018-03-23, `law/hist/art-064.txt`).
* Child allowance, Legea nr. 61/1993 art. 3 as in force 2022-06-30 (`law/r2/l61_dates.txt`, OUG nr. 126/2021):
  "(1) Începând cu drepturile aferente lunii ianuarie 2022 ... a) 600 lei pentru copiii cu vârsta de până la 2 ani ...
  b) 243 lei pentru copiii cu vârsta cuprinsă între 2 ani și 18 ani"; alin. (2): indexed yearly from January 2023 "cu
  rata medie anuală a inflației ... indicatorul definitiv cunoscut în anul curent pentru anul calendaristic anterior";
  alin. (5): rounded up to the leu. 2023: 631 / 256 lei, 2024: 719 / 292 lei. Source chain (round 3, 2026-11-19): the
  amounts are not printed in any act; alin. (2) indexes them "din oficiu" by the INS average annual inflation rate of
  the previous year (2021: 5,1 %; 2022: 13,8 %) and alin. (5) rounds up, which gives exactly 631 / 256 and 719 / 292
  (`allowance_indexation`). The two rates are INS's December press releases (ipc12r21, ipc12r22); insse.ro answered
  503 to an automated fetch on 2026-11-19 (not bypassed), so the rates are still taken as reported by the EUROMOD CR
  RO Y16 (Table 2.4), which prints the same indexed amounts. -/

def allowanceUnder2Y (y : Nat) : Int :=
  if y ≤ 2022 then 600 else if y = 2023 then 631 else allowanceUnder2
def allowance2to18Y (y : Nat) : Int :=
  if y ≤ 2022 then 243 else if y = 2023 then 256 else allowance2to18

/-- `ceil (x * (1000 + r) / 1000)`: the alin. (5) rounding "în favoarea beneficiarului". -/
def indexUp (x r : Int) : Int := (x * (1000 + r) + 999) / 1000

theorem allowance_indexation :
    indexUp 600 51 = 631 ∧ indexUp 243 51 = 256 ∧ indexUp 631 138 = 719 ∧ indexUp 256 138 = 292 := by decide

end RoTax
