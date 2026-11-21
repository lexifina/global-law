import TaxKernel

/-!
# NOTax.Params: every 2025 amount and rate, with its provision

Income year 2025 (inntektsåret 2025 = calendar year 2025), a resident of Oslo. Money in whole kroner, rates in
basis points (kernel convention). Sources and URLs: `refs/PARAMS.md` (P1-P26).

* **sktl.** skatteloven (lov 26. mars 1999 nr. 14), read in the Global law record (Lovdata consolidated text).
* **SV 2025** Stortingets skattevedtak for inntektsåret 2025, FOR-2024-12-13-3203 (amended FOR-2025-12-18-2746).
* **ftrl.** folketrygdloven (lov 28. februar 1997 nr. 19); **TA 2025** the Storting's resolution on contributions
  to the National Insurance for 2025 (Innst. 3 S (2024–2025) III).
-/

namespace NOTax
open TaxKernel

/-! ## Tax on alminnelig inntekt (22 %): three taxes on one base -/

/-- SV 2025 § 3-8: "Den kommunale inntektsskattøren for personlige skattytere og dødsbo skal være maksimum
12,75 pst." (Oslo assumed at the maximum). -/
def kommuneRate : Int := 1275
/-- SV 2025 § 3-8: "Den fylkeskommunale inntektsskattøren ... skal være maksimum 2,65 pst." -/
def fylkeRate : Int := 265
/-- SV 2025 § 3-2 (2): "For personlig skattepliktig og dødsbo ellers: 6,6 pst."; (1) "Fellesskatten skal
beregnes på samme grunnlag som inntektsskatten til kommunene." -/
def fellesRate : Int := 660

theorem alminnelig_22 : kommuneRate + fylkeRate + fellesRate = 2200 := by decide

/-! ## Trinnskatt on personinntekt -/

/-- SV 2025 § 3-1: "1,7 pst. for den delen av inntekten som overstiger 217 400 kroner, 4,0 pst. ... 306 050
kroner, 13,7 pst. ... 697 150 kroner, 16,7 pst. ... 942 400 kroner, og 17,7 pst. ... 1 410 750 kroner". -/
def trinnskatt : Schedule :=
  Schedule.ofList [(0, 0), (217400, 170), (306050, 400), (697150, 1370), (942400, 1670), (1410750, 1770)]

/-- sktl. § 17-1 (2) d: "trinnskatt til staten fastsatt etter de to laveste prosentsatsene" (the part of the
trinnskatt charged in trinn 1 and 2). -/
def trinnskattLow2 : Schedule :=
  Schedule.ofList [(0, 0), (217400, 170), (306050, 400), (697150, 0)]

/-! ## Minstefradrag and personfradrag -/

/-- sktl. § 6-32 (1) a: "gis med 46 prosent av summen av slik inntekt". -/
def minstWageRate : Int := 4600
/-- SV 2025 § 6-1: "skal ikke settes høyere enn 92 000 kroner". -/
def minstWageMax : Int := 92000
/-- sktl. § 6-32 (1) b: "Minstefradrag i pensjonsinntekt ... gis med 40 prosent". -/
def minstPensionRate : Int := 4000
/-- SV 2025 § 6-1 annet ledd: "skal ikke settes høyere enn 73 150 kroner". -/
def minstPensionMax : Int := 73150
/-- sktl. § 15-4; SV 2025 § 6-3: "Fradrag etter skatteloven § 15-4 er 108 550 kroner i klasse 1." -/
def personfradrag : Int := 108550

/-! ## Trygdeavgift (ftrl. § 23-3, TA 2025 §§ 6-8) -/

/-- TA 2025 § 6 (low rate: pensions, persons under 17 or over 69): "beregnes trygdeavgift med 5,1 pst." -/
def taLow : Int := 510
/-- TA 2025 § 7 (middle rate: wages, ftrl. § 23-3 annet ledd nr. 2): "med 7,7 pst." -/
def taMid : Int := 770
/-- TA 2025 § 8 (high rate: business income, nr. 3): "med 10,9 pst." -/
def taHigh : Int := 1090
/-- ftrl. § 23-3 (4): "Det skal ikke betales avgift når inntekten er inntil 99 650 kroner." -/
def taFloor : Int := 99650
/-- ftrl. § 23-3 (4): "Avgiften må ikke utgjøre mer enn 25 prosent av den del av inntekten som overstiger
99 650 kroner." -/
def taCapRate : Int := 2500

/-! ## Owner income (aksjonærmodellen) -/

/-- sktl. § 10-11 (1) and § 10-31 (1)-(2): "oppjusteres med 1,72" (as a fraction 172/100). -/
def oppNum : Int := 172
def oppDen : Int := 100
/-- FSFIN § 10-12-1; Skatteetaten satser 2025: "3,6 prosent for inntektsåret 2025". -/
def skjermingsrente : Int := 360

/-! ## Deductions in alminnelig inntekt -/

/-- sktl. § 6-48 (3); SV 2025 § 6-2: "ikke settes høyere enn 25 000 kroner for ett barn. Fradragsgrensen økes
med inntil 15 000 kroner for hvert ytterligere barn." -/
def foreldreFirst : Int := 25000
def foreldreNext : Int := 15000
/-- sktl. § 6-48 (1): "hjemmeboende barn som er under 12 år i inntektsåret". -/
def foreldreAge : Nat := 12
/-- sktl. § 6-47 (1) c-d (2025 limit; the 2026 text reads 25 000): Skatteetaten satser 2025 "15 000 kroner". -/
def ipsMax : Int := 15000
/-- sktl. § 6-50 (5): "bare når gaven utgjør minst 500 kroner ... maksimalt fradrag ... 25 000 kroner". -/
def giftMin : Int := 500
def giftMax : Int := 25000

/-! ## Tax credits (skattefradrag) and the low-income limit -/

/-- SV 2025 § 6-5: "Fradraget som nevnt i skatteloven § 16-1 første ledd skal være 36 000 kroner." -/
def pensionCreditFull : Int := 36000
/-- SV 2025 § 6-5 annet ledd ("276 400 kroner i trinn 1 og 422 950 kroner i trinn 2"); taper rates 16,7 % and
6,0 % for 2025 (Skatteetaten satser 2025; sktl. § 16-1 (3), whose 2026 text reads 19,1 %). Banded, as the
statute's other "som overstiger" lists are read. -/
def pensionCreditTaper : Schedule := Schedule.ofList [(0, 0), (276400, 1670), (422950, 600)]
/-- sktl. § 16-10 (2)-(3): "10 prosent av innbetalt sparebeløp", "kan ikke overstige 27 500 kroner". -/
def bsuRate : Int := 1000
def bsuMax : Int := 27500
/-- sktl. § 16-10 (1): "til og med det inntektsåret vedkommende fyller 33 år". -/
def bsuLastAge : Nat := 33
/-- SV 2025 § 6-4 as amended 18 Dec 2025 (FOR-2025-12-18-2746): "157 450 kroner for enslige og 145 550 kroner for
hver ektefelle" (original resolution: 147 450 and 135 550). -/
def sbSingle : Int := 157450
def sbSpouse : Int := 145550
/-- sktl. § 17-1 (2): "ikke utgjøre mer enn 55 prosent av overstigende beløp". -/
def sbRate : Int := 5500
/-- sktl. § 17-1 (3): "en og en halv prosent av skattyters nettoformue ... utover 200 000 kroner for enslige og
100 000 kroner for hver ektefelle". -/
def sbWealthRate : Int := 150
def sbWealthFreeSingle : Int := 200000
def sbWealthFreeSpouse : Int := 100000

/-! ## Benefits (NAV) -/

/-- Barnetrygd per child under 18 for 2025: 1 766 kr a month January-April, 1 968 kr May-December (nav.no). -/
def barnetrygdYear : Int := 4 * 1766 + 8 * 1968
/-- Utvidet barnetrygd 2025: 2 516 kr a month (nav.no), one amount per single parent. -/
def utvidetYear : Int := 12 * 2516

theorem barnetrygd_value : barnetrygdYear = 22808 := by decide
theorem utvidet_value : utvidetYear = 30192 := by decide

/-! ## Company side (owner-manager comparisons only) -/

/-- SV 2025 § 3-3: "svarer skatt til staten med 22 pst. av inntekten". -/
def corpRate : Int := 2200
/-- TA 2025 § 3: "Sone I: 14,1 pst." (arbeidsgiveravgift, Oslo). -/
def agaRate : Int := 1410

end NOTax
