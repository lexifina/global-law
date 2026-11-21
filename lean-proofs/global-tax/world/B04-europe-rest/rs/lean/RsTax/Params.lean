import TaxKernel.World

/-!
# Serbia 2025: parameters, each with its dated source (whole dinars)

Sources (Global law, corpus `serbia/national/acts`, dated versions, publisher Службени гласник / Правно-информациони
систем РС; copies in `../src/`):
* Закон о порезу на доходак грађана (ЗПДГ, `zakon/2001/24-1`) read as in force on 2025-07-01; every article cited
  carries its last change. Art. 15а was set by 94/2024 from 2025-01-01 and next changed by 109/2025 from 2026-01-01
  (provision_history), so its amount holds for all twelve months of 2025.
* Закон о доприносима за обавезно социјално осигурање (`zakon/2004/84-37`) read as in force on 2025-07-01.
-/

namespace RsTax
open TaxKernel

/-- ЗПДГ чл. 16: "Зарада ... опорезује се по стопи од 10%." -/
def wageRate : Int := 1000
/-- ЗПДГ чл. 15а ст. 2 (94/2024, from 2025-01-01): the base is the wage "умaњeнa зa изнoс oд 28.423 динара мeсeчнo зa
лицe кoje рaди сa пуним рaдним врeмeнoм". -/
def monthlyNonTaxable : Int := 28423

/-- ЗПДГ чл. 38: "Стопа пореза на приходе од самосталне делатности износи 10%." -/
def selfRate : Int := 1000
/-- ЗПДГ чл. 64 (capital income: interest, dividends) and чл. 77 (capital gains): 15 %. -/
def capitalRate : Int := 1500
/-- ЗПДГ чл. 65г: rent 20 %; чл. 65в: the base is the gross rent "умањен за нормиране трошкове у висини од 25%". -/
def rentRate : Int := 2000
def rentCosts : Int := 2500

/-- Закон о доприносима чл. 44 ст. 2-3 (138/2022, from 2023-01-01): the employee's share "14% за лица из члана 7 ...
5,15% [здравствено] ... 0,75%" (unemployment, paid from the base). -/
def pioEmployee : Int := 1400
def healthEmployee : Int := 515
def unemploymentEmployee : Int := 75

/-- ЗПДГ чл. 89: the annual citizens' income tax: 10 % up to six average annual salaries, 15 % above (bands as
multiples of the average annual salary `A`); чл. 87 ст. 1: only income above 3 × `A` is taxed; чл. 88: personal
deductions 40 % of `A` (taxpayer) and 15 % of `A` per dependant, together at most 50 % of the income. `A` is the 2025
average annual salary published by the statistical office: NOT reached (unsupported). -/
def annualRates : List (Int × Int) := [(0, 1000), (6, 1500)]

end RsTax
