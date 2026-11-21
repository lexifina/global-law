import TaxKernel

/-!
# NLTax.Params: every 2025 parameter, with its provision

Units. Money is `Int` in **cents** (the Dutch statute states no rounding of box-1 tax or of the heffingskortingen;
the OECD books cents; whole euros appear only where the statute writes them). Rates are `Int` in **basis points**
(bp, 1 % = 100) where the statute's percentage has two decimals, and in **pcm** (per cent mille, 1 % = 1 000) where
it has three (arbeidskorting 8,053 %, algemene heffingskorting 6,337 %).

Sources (all read through the Global law record of wetten.overheid.nl, text in force on 2025-01-01 unless stated;
official text: https://wetten.overheid.nl/BWBR0011353 (Wet IB 2001), BWBR0017745 (Wfsv), BWBR0002368 (AKW),
BWBR0022751 (Wet op het kindgebonden budget), BWBR0002638 (WML); copies in `../law/`):
* Wet IB 2001 art. 2.10, 2.10a, 2.12, 5.3, 5.5, 8.10, 8.11, 8.14a, 8.16a, 8.17, 8.18: amounts as replaced by the
  inflatiecorrectie regeling 2025 (Stcrt. 2024, 38492) under art. 10.1.
* art. 5.2 lid 2 box-3 percentages: 5,88 % (overige bezittingen) set at the start of 2025; 1,37 % (banktegoeden) and
  2,70 % (schulden) set after the year with retroactive effect (art. 10.6ter lid 2 and 4) by Stcrt. 2026, 3708
  (the text of art. 5.2 from 2026-02-21 reads "1,37% ... en 6% ... verminderd met 2,70%"; 6 % is 2026's rate for
  overige bezittingen, set by Stcrt. 2025, 40487 for 2026).
* Wfsv art. 11 percentages for 2025 (ministeriële regeling; Belastingdienst, "Hoeveel moet u betalen"
  volksverzekeringen: "| 2025 | 17,90% | 0,10% | 9,65% | € 38.441 |"), cap art. 8 lid 3.
* Zvw inkomensafhankelijke bijdrage 2025: 5,26 % (aanslag / inhouding), werkgeversheffing 6,51 %, maximum
  bijdrage-inkomen € 75.864 (Belastingdienst "Percentages bijdrage Zvw": "4,85% (was 5,26% in 2025)",
  "€ 79.409 (was € 75.864 in 2025)").
* AKW art. 12 lid 3 (from 2025-01-01, Stcrt. 2024, 42409; from 2025-07-01, Stcrt. 2025, 21953).
* Wet op het kindgebonden budget art. 1 lid 1 d, lid 4, art. 2 (Stb. 2024, 433 / Stcrt. 2024, 39288); WML art. 8
  lid 1 b "per 1 januari 2025: € 2.191,80".
-/

namespace NLTax

/-- Whole euros to cents. -/
@[reducible] def eur (e : Int) : Int := 100 * e

/-! ## Box 1: art. 2.10 lid 1 (and 2.10a for those born before 1946) -/

/-- A three-row tariff table as the Wet IB writes it: "Bij een belastbaar inkomen ... van meer dan [I] maar niet meer
dan [II] bedraagt de belasting het in kolom III vermelde bedrag, vermeerderd met het bedrag dat wordt berekend door het
in kolom IV vermelde percentage te nemen van het gedeelte ... dat het in kolom I vermelde bedrag te boven gaat".
`b1`, `b2`: kolom I of rows 2 and 3 (cents); `c2`, `c3`: kolom III of rows 2 and 3 (cents); `r1..r3`: kolom IV (bp).
-/
structure Table3 where
  b1 : Int
  b2 : Int
  c2 : Int
  c3 : Int
  r1 : Int
  r2 : Int
  r3 : Int
  deriving Repr

/-- Art. 2.10 lid 1, 2025: "– | € 38.441 | – | 8,17%"; "€ 38.441 | € 76.817 | € 3.140 | 37,48%";
"€ 76.817 | – | € 17.523 | 49,50%". (The tax part only: premies volksverzekeringen are levied by the Wfsv.) -/
def t210 : Table3 := { b1 := 3844100, b2 := 7681700, c2 := 314000, c3 := 1752300, r1 := 817, r2 := 3748, r3 := 4950 }

/-- Art. 2.10a lid 1 (born before 1 January 1946), 2025: "– | € 40.502 | – | 8,17%"; "€ 40.502 | € 76.817 |
€ 3.309 | 37,48%"; "€ 76.817 | – | € 16.919 | 49,50%". -/
def t210a : Table3 := { b1 := 4050200, b2 := 7681700, c2 := 330900, c3 := 1691900, r1 := 817, r2 := 3748, r3 := 4950 }

/-- Art. 2.10 lid 2: "vermeerderd met 12,02% van het bedrag waarmee de som van het belastbare inkomen ... en de in
aftrek gebrachte bedragen ter zake van grondslagverminderende posten ... het ... laatstvermelde bedrag te boven gaat,
doch ten hoogste met 12,02% van de in aftrek gebrachte bedragen" (bp). -/
def grondslagRate : Int := 1202

/-! ## Box 2: art. 2.12 (two rows) -/

/-- Art. 2.12, 2025: "– | € 67.804 | – | 24,5%"; "€ 67.804 | – | € 16.611 | 31%". -/
def box2B1 : Int := 6780400
def box2C2 : Int := 1661100
def box2R1 : Int := 2450
def box2R2 : Int := 3100

/-! ## Box 3: art. 2.13, 5.2, 5.3, 5.5 -/

/-- Art. 2.13: "bedraagt 36%". -/
def box3Rate : Int := 3600
/-- Art. 5.2 lid 2 (2025, definitive): banktegoeden 1,37 %, overige bezittingen 5,88 %, schulden 2,70 % (bp). -/
def box3Bank : Int := 137
def box3Other : Int := 588
def box3Debt : Int := 270
/-- Art. 5.5: "Het heffingvrije vermogen bedraagt € 57.684." (per person; art. 5.2 lid 5 adds the partner's). -/
def hvv : Int := eur 57684
/-- Art. 5.3 lid 3 f: debts count only "voorzover de gezamenlijke waarde daarvan meer bedraagt dan € 3.800"
(partners together € 7.600). -/
def debtThreshold : Int := eur 3800

/-! ## Premies volksverzekeringen: Wfsv art. 8, 10, 11 -/

/-- Wfsv art. 11 percentages for 2025 (bp): AOW 17,90, Anw 0,10, Wlz 9,65. -/
def pAOW : Int := 1790
def pAnw : Int := 10
def pWlz : Int := 965
/-- Wet IB art. 8.1 c: "gecombineerd heffingspercentage: de som van het belastingtarief eerste schijf en de ...
premiepercentages": 8,17 + 17,90 + 0,10 + 9,65 = 35,82 (bp). -/
def gecombineerd : Int := 817 + pAOW + pAnw + pWlz

/-- Pensioengerechtigde leeftijd 2025 (AOW art. 7a): 67 years. The model treats an adult aged 67 or more as above
it for the whole year (simplification: the age in the contract is one number for the year). -/
def aowAge : Nat := 67

/-! ## Zorgverzekeringswet: inkomensafhankelijke bijdrage (self-employed and pensions; employers pay for employees) -/

def zvwRate : Int := 526
def zvwMax : Int := eur 75864

/-! ## Heffingskortingen, hoofdstuk 8 (pcm = 1/100 000) -/

/-- Art. 8.10 lid 2: "€ 3.068, verminderd, doch niet verder dan tot nihil, met 6,337% van het gedeelte van het
verzamelinkomen dat meer bedraagt dan € 28.406". -/
def ahkMax : Int := eur 3068
def ahkRate : Int := 6337
def ahkStart : Int := eur 28406

/-- Art. 8.11 lid 2: "a. 8,053% van het arbeidsinkomen met een maximum van € 980, vermeerderd met: b. 30,030% ...
meer bedraagt dan € 12.169, ... niet meer bedraagt dan € 5.220, ... c. 2,258% ... meer bedraagt dan € 26.288, ...
niet meer bedraagt dan € 5.599, en verminderd ... met: d. 6,51% van het arbeidsinkomen voor zover dat meer bedraagt
dan € 43.071". -/
def akRateA : Int := 8053
def akCapA : Int := eur 980
def akRateB : Int := 30030
def akStartB : Int := eur 12169
def akCapB : Int := eur 5220
def akRateC : Int := 2258
def akStartC : Int := eur 26288
def akCapC : Int := eur 5599
def akRateD : Int := 6510
def akStartD : Int := eur 43071

/-- Art. 8.14a: arbeidsinkomen "meer dan € 6.145"; "11,45% van het arbeidsinkomen, voor zover dat ... meer beloopt
dan € 6.145, doch niet meer dan € 2.986". -/
def iackStart : Int := eur 6145
def iackRate : Int := 11450
def iackMax : Int := eur 2986

/-- Art. 8.17 lid 2: "€ 2.035, verminderd ... met 15% van het verzamelinkomen voor zover dat meer bedraagt dan
€ 45.308". -/
def okMax : Int := eur 2035
def okRate : Int := 15000
def okStart : Int := eur 45308
/-- Art. 8.18 lid 2: "De alleenstaande ouderenkorting bedraagt € 531." -/
def aokAmount : Int := eur 531

/-! ## Ondernemers: art. 3.76, 3.79a -/

/-- Art. 3.76 lid 2: "bedraagt de zelfstandigenaftrek € 2.470" (lid 4: 50 % above the AOW age). -/
def zelfstandigenaftrek : Int := eur 2470
/-- Art. 3.79a: "De MKB-winstvrijstelling bedraagt 12,7%" (pcm). -/
def mkbRate : Int := 12700

/-! ## Giften: art. 6.39 -/
/-- Art. 6.39 lid 1: andere giften count "voor zover zij samen zowel € 60 als 1% van het verzamelinkomen vóór
toepassing van de persoonsgebonden aftrek te boven gaan, en vervolgens tot ten hoogste 10%". -/
def giftFloor : Int := eur 60

/-! ## Kinderbijslag: AKW art. 12 lid 3 (per kalenderkwartaal, cents) -/

/-- Quarters 1-2 (text from 2025-01-01): "a. jonger is dan 6 jaar: € 286,45 b. ... jonger is dan 12 jaar: € 347,83
en c. ... jonger is dan 18 jaar: € 409,21". -/
def kbQ1 (age : Nat) : Int := if age < 6 then 28645 else if age < 12 then 34783 else if age < 18 then 40921 else 0
/-- Quarters 3-4 (text from 2025-07-01): "€ 291,49", "€ 353,95", "€ 416,41". -/
def kbQ3 (age : Nat) : Int := if age < 6 then 29149 else if age < 12 then 35395 else if age < 18 then 41641 else 0

/-! ## Kindgebonden budget: Wet op het kindgebonden budget art. 1, 2 -/

/-- Art. 2 lid 2: "€ 2.511" for one child, "€ 2.511 per kind voor het tweede of volgende kind". -/
def kgbPerChild : Int := eur 2511
/-- Art. 2 lid 4: 12 to 15 years "€ 703"; lid 5: 16 or 17 years "€ 936,00". -/
def kgb12 : Int := eur 703
def kgb16 : Int := eur 936
/-- Art. 2 lid 6: "De ouder die geen partner heeft, heeft aanspraak op een verhoging ... van € 3.389." -/
def kgbAlo : Int := eur 3389
/-- Art. 2 lid 7-8: "verminderd met 7,10% van het verschil" (pcm). -/
def kgbRate : Int := 7100
/-- Art. 2 lid 8: "het met € 9.139,00 verhoogde drempelinkomen" (partners). -/
def kgbPartnerExtra : Int := eur 9139
/-- Art. 1 lid 1 d: "drempelinkomen: 108% van het twaalfvoud van het voor de maand januari ... geldende in artikel
8, eerste lid, onderdeel b, van de Wet minimumloon ... bedoelde bedrag per maand"; WML art. 8 lid 1 b "per 1 januari
2025: € 2.191,80". 1,08 × 12 × 2 191,80 = 28 405,728 euro: in **tenths of a cent**, 28 405 728. The statute states
no rounding (Dienst Toeslagen publishes € 28.406). -/
def kgbDrempelMilli : Int := 108 * 12 * 219180 / 10
/-- Art. 1 lid 4: no kindgebonden budget if the rendementsgrondslag (box 3, before the heffingvrij vermogen) at
1 January exceeds "€ 141.896" (single) or "€ 179.429" (partners). -/
def kgbWealthSingle : Int := eur 141896
def kgbWealthPartners : Int := eur 179429

/-! ## OECD Taxing Wages convention (only under `--oecd`) -/

/-- Employee contribution to an occupational pension fund, as the OECD's Netherlands tables book it (an "other
standard tax allowance", OSTA). Not published as a rate; derived from the OECD's own 2025 lines, which it fits to
the cent at all three wage levels: S67 OSTA 1 761,37 on 46 249,07; S100 3 171,41 on 69 028,46; S167 6 034,23 on
115 277,52, i.e. 6,19 % of the wage above 17 794 euro (see `../FINDINGS.md`, F1). -/
def oecdPensionRate : Int := 619
def oecdPensionFranchise : Int := eur 17794

end NLTax
