import TaxKernel.World

/-!
# Israel 2025: parameters with their sources

Global law holds no Israeli tax law (its Israel corpus is the Basic Laws). Statute texts: Hebrew Wikisource, the
publisher Global law uses for Israel (an unofficial consolidation that cites each amendment's Reshumot entry), at the
revision in force in mid-2025 (`../src/wikisource/`):
* פקודת מס הכנסה [נוסח חדש] (Income Tax Ordinance), revision 2935650 of 2025-05-27: s. 33א, 34, 36, 36א, 66(ג),
  120ב (with (ה): no indexation on 1 January 2025-2027, amounts "as on 1 January 2024", amendment תשפ״ה־2), 121,
  121ב, 125ב.
* חוק הביטוח הלאומי (National Insurance Law), revision 2946268 of 2025-06-29: s. 334(א), לוח י׳ (temporary table
  2025-2026), לוח י״א.
* חוק ביטוח בריאות ממלכתי (National Health Insurance Law), revision 2924411: s. 14(ב).
Official secondary: National Insurance Institute, "שיעורי דמי ביטוח ... לעובדים שכירים" (btl.gov.il, fetched
2026-11-20): employee rates with their start dates.
Not reached: the 2025 "הסכום הבסיסי" (the monthly maximum insurable income is 5 × it, לוח י״א), so no ceiling.
-/

namespace IlTax
open TaxKernel

/-- ITO s. 121(א), (ב)(1) as tabulated for "2024–2027" (s. 120ב(ה): the 2025 amounts are those of 1 January 2024):
personal-exertion income "עד 84,120 10%; 84,121 עד 120,720 14%; 120,721 עד 193,800 20%; 193,801 עד 269,280 31%;
269,281 עד 560,280 35%; כל שקל נוסף 47%". (The running text of s. 121(א)(2) in this revision reads "מ־560,280 ... עד
542,160", an evident transcription slip: FINDINGS IL-S1.) -/
def exertionScale : Schedule :=
  Schedule.ofList [(0, 1000), (84120, 1400), (120720, 2000), (193800, 3100), (269280, 3500), (560280, 4700)]

/-- ITO s. 121(א): other income (not personal exertion, under 60): 31 % to 269,280, 35 % to 560,280, 47 % above. -/
def otherScale : Schedule := Schedule.ofList [(0, 3100), (269280, 3500), (560280, 4700)]

/-- ITO s. 121ב(א): "מס נוסף ... בשיעור של 3%" above 640,000 "(נקוב לשנת 2017 ...; בשנים 2024–2027, 721,560 ש״ח)";
(א1) (amendment תשפ״ה־2): a further 2 % on taxable income from capital sources above the same amount. -/
def surtaxThreshold : Int := 721560
def surtaxRate : Int := 300
def surtaxCapitalRate : Int := 200

/-- ITO s. 33א: "נקודת זיכוי" — 504 NIS (1987) "בשנים 2024–2027, 2,904 ש״ח" per tax year. -/
def creditPoint : Int := 2904
/-- s. 34: "שתי נקודות זיכוי" for a resident; s. 36: "1/4 נקודת זיכוי כזיכוי נסיעה"; s. 36א: "בחישוב המס של אשה
תובא בחשבון 1/2 נקודת זיכוי". In half-quarter units: points × 4. -/
def residentQuarters : Int := 9      -- 2 + 1/4 = 9/4
def womanQuarters : Int := 2         -- 1/2

/-- ITO s. 66(ג)(4)(א) (mother) and (5) (father): points per child by age at the end of the year, in quarters.
Mother: birth year 2½, ages 1-2 4½, age 3 3½, ages 4-5 2½, ages 6-17 2, the year of majority (18) ½.
Father: birth year 2½, ages 1-2 4½, age 3 3½, ages 4-5 2½, ages 6-17 1. -/
def motherChildQuarters (age : Nat) : Int :=
  if age == 0 then 10 else if age ≤ 2 then 18 else if age == 3 then 14 else if age ≤ 5 then 10
  else if age ≤ 17 then 8 else if age == 18 then 2 else 0
def fatherChildQuarters (age : Nat) : Int :=
  if age == 0 then 10 else if age ≤ 2 then 18 else if age == 3 then 14 else if age ≤ 5 then 10
  else if age ≤ 17 then 4 else 0

/-- ITO s. 125ב(1): "דיבידנד בידי יחיד – 25%". s. 91 (capital gains) and 125ג (interest) were not read: the same
25 % is applied to them (flagged in `unsupported`). -/
def dividendRate : Int := 2500

/-! ## National insurance and health insurance (employee) -/

/-- NI Law s. 334(א) as amended (תשפ״ה): "מדרגת גבייה מופחתת – (החל משנת 2026): סכום של 7,522 שקלים חדשים, כשהוא
מעודכן ב־1 בינואר של כל שנה"; for 2025 the tables use "60% מהשכר הממוצע". The 2026 amount is 7,522 updated on
1 January 2026, so 7,522 is the amount of 2025. Confirmed in round D2 from the NII's dated table "שכר ממוצע לפי
סעיפים 1 ו-2 לחוק הביטוח הלאומי" (btl.gov.il, src/btl/d2/avg_wage.html, fetched 2026-11-20): from 1.01.2025 the average
wage under s. 2 for contributions ("דמי ביטוח") is 12,536 (change 0.0); 60 % x 12,536 = 7,521.6 -> 7,522. -/
def reducedBandMonth : Int := 7522

/-- NI Law s. 348 (א) with לוח י״א: income above "הסכום המרבי" (5 x the basic amount a month) is not counted. The NII's
dated table "הסכום הבסיסי לחישוב קצבאות" (src/btl/d2/basic_amount.html, fetched 2026-11-20): from 1.01.2025 "סכום בסיסי
3 ... וחישוב הכנסה מרבית לגביית דמי ביטוח" = 10,139: ceiling 5 x 10,139 = 50,695 a month (round D2). -/
def niCeilingMonth : Int := 5 * 10139

/-- Child allowance (NI Law s. 66, 68; קצבת ילדים): the same NII table, from 1.01.2025 "בעד הילד הראשון, החמישי ואילך"
169 and "בעד הילד השני, השלישי והרביעי" 214 NIS a month (round D2). -/
def childAllowance (k : Nat) : Int := if k == 0 || k ≥ 4 then 169 else 214

/-- NII rates for employees (btl.gov.il): national insurance "עובד ... 1.04% (החל ב- 01.01.2025)" on the reduced band
and "7% (החל ב- 01.01.2006)" above; health "3.23% (החל ב- 01.01.2025)" and "5.17% (החל ב- 01.02.2025)". National
Health Insurance Law s. 14(ב)(1): 5.17 % "(עד ועד בכלל 2024, 5%; בינואר 2025, 5.16%)". In hundredths of a bp. -/
def niLowcBp : Int := 10400
def niHighcBp : Int := 70000
def healthLowcBp : Int := 32300
def healthHighJancBp : Int := 51600
def healthHighcBp : Int := 51700

end IlTax
