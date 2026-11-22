import TaxKernel.World

/-!
# Albania 2025: parameters, each with its dated source (whole lekë)

Sources (Global law, corpus `albania/national/acts`, publisher Qendra e Botimeve Zyrtare; copies in `../src/`):
* Ligj 29/2023 "Për tatimin mbi të ardhurat" (`ligj/2023/29`), read as in force on 2025-07-01. Every article used
  here is in its 2023 wording (last change 2023-05-17) except neni 69 (Ligj 9/2025, in force 2025-03-13, transitional
  rules for businesses) and nene 65 and 72 (Akti normativ 7/2023). Official text: https://qbz.gov.al/eli/ligj/2023/03/30/29
* Ligj 7703/1993 "Për sigurimet shoqërore" (consolidated text of 2023-07-21), neni 10.
* Ligj 10383/2011 as amended by Ligj 126/2013 (health insurance contribution).
* VKM 113/2023 (minimum wage 40 000 lekë) as quoted by VKM 434/2023 pika 4, and repealed by VKM 776/2025 pika 5
  only "nga data 1 janar 2026"; VKM 434/2023 pika 4 (b) (maximum wage for contributions 176 416 lekë).
-/

namespace AlTax
open TaxKernel

/-! ## Personal income tax on employment (Ligj 29/2023) -/

/-- Neni 24 (1): "0 - 2 040 000 lekë 13%; Mbi 2 040 000 lekë 23%" (annual tax base of employment income). -/
def empSchedule : Schedule := Schedule.ofList [(0, 1300), (2040000, 2300)]

/-- Neni 22 (1) (a)-(c): the personal deduction depends on the annual income: "600 000 lekësh nëse të ardhurat
vjetore janë deri 600 000 lekë", "420 000 lekësh ... mbi 600 000 lekë deri në 720 000 lekë", "360 000 lekësh ... mbi
720 000 lekë". -/
def personalDeduction (annualIncome : Int) : Int :=
  if annualIncome ≤ 600000 then 600000 else if annualIncome ≤ 720000 then 420000 else 360000

/-- Neni 22 (1) (ç): "një shumë kompensimi për çdo fëmijë në ngarkim të tij më pak se 18 vjeç prej 48 000 lekësh";
neni 23 (1): claimed by the family member with the higher annual taxable income. -/
def childDeduction : Int := 48000
def childAgeLimit : Nat := 18

/-- Neni 24 (2): business income of individual traders and the self-employed, 15 % to 14 000 000, 23 % above. -/
def busSchedule : Schedule := Schedule.ofList [(0, 1500), (14000000, 2300)]

/-- Neni 69 (1) (dh) (Ligj 9/2025): individual traders, the self-employed and entities "me të ardhura bruto deri 14
milionë lekë në vit, norma e tatimit mbi të ardhurat 0% do të aplikohet deri më 31 dhjetor 2029". -/
def busZeroLimit : Int := 14000000

/-- Neni 24 (3): "të ardhurat nga dividentët 8%; çdo zë tjetër i të ardhurave nga investimi 15%" (interest, rent of
immovable property and capital gains are investment income under neni 15 (1)). -/
def dividendRate : Int := 800
def investmentRate : Int := 1500

/-! ## Employee contributions -/

/-- Ligj 7703 neni 10 (b): "për personin e punësuar 9.5 për qind e pagesës së tij totale (bruto)". -/
def ssEmployee : Int := 950
/-- Ligj 126/2013 (amending Ligj 10383/2011): "3,4 për qind e pagës bruto ... ndahet në mënyrë të barabartë ndërmjet
punëdhënësit dhe të punësuarit" (employee half: 1,7 %), with the same minimum and maximum wage. -/
def healthEmployee : Int := 170
/-- Minimum monthly wage 2025: "pagës minimale në shkallë vendi, prej 40 000 lekësh, e përcaktuar sipas vendimit nr.
113, datë 1.3.2023" (VKM 434/2023 pika 4 (a)); VKM 776/2025 (50 000 lekë) takes effect only from 1 January 2026. -/
def minWage : Int := 40000
/-- Maximum monthly wage for contributions: "paga maksimale në shkallë vendi, prej 176 416 lekësh" (VKM 434/2023
pika 4 (b)); Ligj 7703 neni 10: it moves only when the minimum wage moves, which it did not in 2025. -/
def maxWage : Int := 176416

end AlTax
