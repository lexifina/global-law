import TaxKernel

/-!
# Estonia 2025: parameters, each with its provision (amounts in euro CENTS, rates in basis points)

Statutes (Riigi Teataja, consolidated texts in force in 2025, saved under `cmp20/baltic/ee/refs/`):
* TuMS = Tulumaksuseadus, redaction RT I 20.12.2024, 5 (akt 120122024005, in force 1.1.2025-31.8.2025;
  https://www.riigiteataja.ee/akt/120122024005); the later 2025 redactions 109012025031 (from 1.9.2025) and
  112072025028 (from 1.10.2025) change nothing modelled here (diffed: `refs/tums_*.txt`).
* SMS = Sotsiaalmaksuseadus, akt 127092024008 (in force 1.1.2025-31.12.2025).
* KoPS = Kogumispensionide seadus, akt 103122024015 / 103122024016.
* TKindlS = Töötuskindlustuse seadus, akt 106072023111; rates: Vabariigi Valitsuse määrus RT I 24.09.2024, 4
  (akt 124092024004) "Kindlustatu ja tööandja töötuskindlustusmakse määrad aastatel 2025–2028".
* PHS = Perehüvitiste seadus, akt 112122024013 (1.1.2025), 108042025002 (18.4.2025).
* EMTA, "2025. aasta maksumuudatused" (21.10.2024), https://emta.ee/uudised/2025-aasta-maksumuudatused
  (`refs/emta/2025-aasta-maksumuudatused.txt`): confirms every 2025 amount below.
-/

namespace EeTax
open TaxKernel

/-- TuMS § 4(1): "Tulumaksu määr, välja arvatud lõigetes 2 ja 5 ning § 43 lõikes 4 nimetatud juhtudel, on 22%."
(RT I 30.06.2023, 107, in force 1.1.2025; 20 % until 31.12.2024.) -/
def rate : Int := 2200

/-- The flat schedule of § 4(1) on taxable income in cents. -/
def sched : Schedule := Schedule.flat rate

/-- TuMS § 4(1^1): distributions "jagatakse maksustatav summa enne maksumääraga korrutamist arvuga 0,78":
the company's tax on a net distribution D is D × 22/78 (CIT on distribution, § 50(1)). -/
def citNum : Int := 22
def citDen : Int := 78

/-- TuMS § 23(1)-(2): "maksuvaba tulu 7848 eurot" … "Kui tulu on suurem kui 14 400 eurot, arvutatakse maksuvaba
tulu summa järgmise valemi kohaselt: 7848 – 7848 / 10 800 × (tulu summa – 14 400). Seejuures ei või maksuvaba tulu
olla väiksem kui null ja suurem kui 7848."  7848 / 10 800 = 109 / 150 exactly, so the taper is written with
num = 109, den = 150 (every 150 cents of income above 14 400 euro withdraw 109 cents of exemption); the reduction
is rounded down to the cent (the statute gives no rounding; EMTA computes to the cent). Band: 14 400 - 25 200 euro. -/
def basicExemption : Taper := { full := 784800, start := 1440000, num := 109, den := 150 }

/-- 2026 (versioned law, used only when the input says `"year": 2026`): TuMS § 23(1) in redaction 118122025017
(in force 1.1.2026): "maksuvaba tulu 8400 eurot"; § 23(2)-(5) "Kehtetu" (RT I 30.06.2023, 107, entry into force moved
to 1.1.2026 by RT I 20.12.2024, 2). Rate still 22 %: the 24 % of RT I 08.07.2025, 1 § 3 never entered into force. -/
def exemption2026 : Int := 840000

/-- TuMS § 23^5(1): "Alates maksustamisperioodist, kui … füüsiline isik jõuab vanaduspensioniikka, arvatakse tema
maksustamisperioodi maksustatavast tulust maha maksuvaba tulu 9312 eurot." (RT I 19.06.2024, 1, from 1.1.2025.)
Not withdrawn with income; replaces § 23 (§ 23(1) last sentence). -/
def pensionAgeExemption : Int := 931200

/-- TuMS § 42(1) (monthly withholding, on the employee's written application, one payer only, § 42(2)):
"654 – 654 / 900 × (väljamakse – 1200). Nimetatud summa ei või olla väiksem kui null ja suurem kui 654."
654/900 = 109/150: the monthly taper is exactly the annual one divided by 12. -/
def monthlyExemption : Taper := { full := 65400, start := 120000, num := 109, den := 150 }

/-- TuMS § 28^2(1): §§ 26-27 deductions (training, gifts/donations) "kokku kuni 1200 eurot maksumaksja kohta, kuid
mitte rohkem kui 50% ulatuses maksumaksja sama maksustamisperioodi Eestis maksustatavast tulust". -/
def dedCap : Int := 120000
def dedPct : Int := 5000

/-- TuMS § 28(2): III-pillar / voluntary pension contributions "kuni 15% ulatuses … maksustatavast tulust …, kuid
mitte rohkem kui 6000 eurot". -/
def p3Pct : Int := 1500
def p3Cap : Int := 600000

/-- TuMS § 39^1: "eluruumi üürilepingu alusel saadud üürist … arvatakse … üürimisega seotud kulude katteks maha 20%." -/
def rentDeductionPct : Int := 2000

/-- Unemployment insurance, employee: TKindlS § 41(1),(4) and Government regulation RT I 24.09.2024, 4 § 1(1):
"Kindlustatu töötuskindlustusmakse määr aastatel 2025–2028 on 1,6 protsenti". Deductible: TuMS § 28^1(2). -/
def uiEmployee : Int := 160
/-- Same regulation § 1(2): "Tööandja töötuskindlustusmakse määr … on 0,8 protsenti" (employer; owner-manager only). -/
def uiEmployer : Int := 80

/-- KoPS § 9(1): "Makse määr on 2% …, kui kohustatud isik ei ole valinud … muud makse määra"; § 9(2): "4% või 6%".
Deductible: TuMS § 28^1(1). Default 2 %; input field `pillar2Rate` (bp: 0, 200, 400, 600). -/
def pillar2Default : Int := 200

/-- SMS § 7(1): "Sotsiaalmaksu määr on 33 protsenti maksustatavalt summalt." (employer side; FIE on own income.) -/
def socialTax : Int := 3300

/-- SMS § 2^1: monthly minimum base ("kuumäär") set by the budget, not below the minimum wage of 1 July of the
previous year; 2025: 820 euro (EMTA 2025 changes: "minimaalse kohustuse aluseks olev kuumäär 820 eurot ja
sotsiaalmaks 270,60 eurot"). -/
def kuumaar : Int := 82000

/-- 2025 monthly minimum wage 886 euro (EMTA, Sotsiaalmaks page: the 2026 kuumäär 886 euro is the minimum wage
in force on 1 July 2025). Used for the FIE ceiling, SMS § 2(1) p5: "mitte rohkem kui maksustamisperioodi kuude
töötasu alammäära 10-kordselt summalt aastas". -/
def minWage2025 : Int := 88600

/-- TuMS § 14(5^3): FIE business income "jagatakse enne maksumääraga korrutamist 1,33-ga" (social tax 33 %
deducted from its own base). -/
def fieDivNum : Int := 100
def fieDivDen : Int := 133

/-! ## Family benefits (PHS, monthly amounts; tax-exempt under TuMS § 19(3) p3) -/

/-- PHS § 17(3): "Lapsetoetuse suurus pere esimese ja teise lapse kohta on 80 eurot. Kolmanda ja iga järgmise lapse
kohta on lapsetoetuse suurus 100 eurot." § 17(1): from birth "kuni 19-aastaseks saamiseni". -/
def childAllowance12 : Int := 8000
def childAllowance3 : Int := 10000
def childAgeLimit : Nat := 19

/-- PHS § 19(3): "Üksikvanema lapse toetuse suurus on 80 eurot." Only for a child whose birth record has no other
parent or whose parent is a wanted person (§ 19(1)); input flag `otherParentUnrecorded`. -/
def singleParentAllowance : Int := 8000

/-- PHS § 21(2)-(3): "Lasterikka pere toetuse suurus kolme kuni kuut last kasvatavale perele on 450 eurot";
"seitset või enamat last kasvatavale perele on 650 eurot." -/
def largeFamily3to6 : Int := 45000
def largeFamily7 : Int := 65000

/-- Old-age pension age, used when the input gives an adult's age only: RPKS § 7 (64 y 9 m for persons born in
1961; 65 from those born 1962); EMTA 2026: "vanaduspensionieas inimesed, kes on sündinud 1961. aastani". In 2025
those born up to 1960 have reached it in or before the year; an age of 65 at the end of 2025 is used (input field
`pensionAgeYears` overrides; a per-adult boolean `pensionAge` in `adults[i]` is not in the contract). -/
def pensionAgeYears : Nat := 65

/-! ## Earlier years 2022-2024 (round 2, 2026-11-19): the redactions in force on 1 January of each year, fetched
from Riigi Teataja (`refs/tums_122122021041.txt` 2022, `tums_122122022010.txt` 2023, `tums_121112023006.txt` 2024;
`refs/phs_122122021020.txt`, `phs_107062022003.txt` 2022, `phs_111012023009.txt`, `phs_130062023051.txt` 2023,
`phs_106072023062.txt` 2024; `refs/kops_122122021039.txt`, `kops_116122022031.txt`, `kops_106072023045.txt`). -/

/-- TuMS § 4(1) in the 2022, 2023 and 2024 redactions: "Tulumaksu määr ... on 20%." [RT I 2017-07-07 3]; 22 % from
1.1.2025 (above). -/
def rateFor (y : Nat) : Int := if y ≤ 2024 then 2000 else rate

/-- TuMS § 23(1)-(2), redaction 122122021041 (2022): "maksuvaba tulu 6000 eurot" ... "6000 – 6000 / 10 800 × (tulu
summa – 14 400) ... ei või olla väiksem kui null ja suurem kui 6000"; 6000/10 800 = 5/9. From 2023 (RT I 2022-12-16 5,
in force 1.1.2023) 7848 as in `basicExemption`. -/
def exemption2022 : Taper := { full := 600000, start := 1440000, num := 5, den := 9 }

/-- The § 23 exemption schedule of a year (2022: 6000; 2023-2025: 7848). -/
def exemptionFor (y : Nat) : Taper := if y ≤ 2022 then exemption2022 else basicExemption

/-- TuMS § 23^1(1), redactions 2022 and 2023 (repealed from 1.1.2024, § 61(71)): a parent "kes peab ülal kahte või
enamat alaealist last, võib ... maha arvata täiendava maksuvaba tulu kuni 17 aasta vanuse lapse kohta alates teisest
lapsest. Täiendava maksuvaba tulu summa on 1848 eurot teise lapse kohta ja 3048 eurot alates kolmandast lapsest." -/
def childExtra2 : Int := 184800
def childExtra3 : Int := 304800

/-- TuMS § 23^4(1)-(3), redactions 2022 and 2023: "täiendav maksuvaba tulu 2160 eurot, kui ... isiku ja tema
abikaasa ... § 23 lõikes 3 nimetatud tulu kokku ei ületa 50 400 eurot"; (2) only "osas, mille võrra abikaasa ...
tulu on väiksem" than 2160; (3) not more than "50 400 euro ja abikaasade kogu maksustatava tulu vahe". -/
def spouseExtra : Int := 216000
def spouseCap : Int := 5040000

/-- The year has the § 23^1 / § 23^4 extra exemptions (2022, 2023). -/
def hasFamilyExemptions (y : Nat) : Bool := y ≤ 2023

/-- PHS § 17(3): 2022 (redactions 122122021020, 107062022003): "pere esimese ja teise lapse kohta on 60 eurot";
from 2023 (RT I 2023-01-11 2, applied from 1.1.2023): 80 eurot. Third and later child 100 eurot throughout. -/
def childAllowance12For (y : Nat) : Int := if y ≤ 2022 then 6000 else childAllowance12

/-- PHS § 19(3): 2022 "Üksikvanema lapse toetuse suurus on 19,18 eurot"; from 2023: 80 eurot. -/
def singleParentFor (y : Nat) : Int := if y ≤ 2022 then 1918 else singleParentAllowance

/-- PHS § 21(2)-(3): 2022 300 / 400 eurot [RT I 2016-12-24 1]; 2023 650 / 850 eurot [RT I 2023-01-11 2]; 2024
450 / 650 eurot [RT I 2023-07-06 3, in force 1.1.2024]; 2025 as above. -/
def largeFamily3to6For (y : Nat) : Int := if y ≤ 2022 then 30000 else if y = 2023 then 65000 else largeFamily3to6
def largeFamily7For (y : Nat) : Int := if y ≤ 2022 then 40000 else if y = 2023 then 85000 else largeFamily7

/-- KoPS § 9: "Makse määr on 2%" in the 2022 (122122021039), 2023 (116122022031) and 2024 (106072023045) redactions:
`pillar2Default` holds for every year. Unemployment insurance 1,6 %: the 2024 rate is VV määrus RT I 03.10.2023, 19
(akt 103102023019) § 1(1) "Kindlustatu töötuskindlustusmakse määr aastatel 2024–2027 on 1,6 protsenti"; for 2022 and
2023 the regulations then in force (nr 88 of 15.9.2022 "aastatel 2023–2026", repealed by 103102023019, and its
predecessor) were not retrieved; 1,6 % for those years rests on secondary reports (flagged in IMPROVE.md). -/
def uiEmployeeFor (_y : Nat) : Int := uiEmployee

end EeTax
