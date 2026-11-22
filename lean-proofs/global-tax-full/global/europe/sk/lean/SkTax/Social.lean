import SkTax.Params

/-!
# Contributions (ZSP 461/2003, ZZP 580/2004), 2025, in cents

**Employee, social** (ZSP §§ 130–136): 1,4 + 4 + 3 + 1 = 9,4 % of the monthly vymeriavací základ (the month's wage,
§ 138 ods. 1), at most 15 730 € a month (§ 138 ods. 10), each insurance's amount rounded down to the cent (§ 129
ods. 2). An annual wage `w` is paid as 11 months of ⌊w/12⌋ and a December of the rest.

**Employee, health** (ZZP § 12 ods. 1 písm. a), § 19): 4 % of the annual base, no ceiling, the ročné zúčtovanie amount
rounded down to the cent.

**SZČO** (steady state: the same income every year, so the base fixed from last year's return equals this year's):
social only above the § 21 ods. 1 income test, monthly base = tax base before contributions / 1,486 / 12 (§ 138 ods. 2)
between 715 € and the 15 730 € shared with any employment (§ 138 ods. 9, 10), 4,4 + 18 + 6 + 4,75 = 33,15 %;
health 14 % of base / 1,486 (ZZP § 13 ods. 2), at least 12 × 715 € unless also an employee (§ 13 ods. 10, 11 písm. a)).

**Health on § 8 income** (ZZP § 10b ods. 1 písm. d), § 12 ods. 1 písm. b), § 13 ods. 7): 14 % of the § 8 tax base
(e.g. a taxable gain on securities). Dividends from profits taxed under ZDP are not "dividendy" of § 10b ods. 1
písm. e) (that letter covers only profit shares "ktoré nie sú predmetom dane").
-/

namespace SkTax
open TaxKernel

/-- One month's employee social contributions on the month's base `vz` (cents). -/
def eeSocialMonth (vz : Int) : Int :=
  let b := min (pos vz) socMaxMonthly
  pctD b sickEE + pctD b oldEE + pctD b invEE + pctD b unempEE

/-- A year's employee social contributions on annual wages `w` paid evenly (11 × ⌊w/12⌋ + the rest in December). -/
def eeSocialYear (w : Int) : Int := 11 * eeSocialMonth (w / 12) + eeSocialMonth (w - 11 * (w / 12))

/-- The same with the social-insurance ceiling of tax year `y` (`socMaxMonthlyFor`); rates unchanged 2022-2025 (ZSP
§§ 130 a), 131 ods. 1 a), 132 a), 136 a) in the versions of 1. 1. 2022, 2023 and 2024: 1,4 / 4 / 3 / 1 %). -/
def eeSocialMonthY (y : Nat) (vz : Int) : Int :=
  let b := min (pos vz) (socMaxMonthlyFor y)
  pctD b sickEE + pctD b oldEE + pctD b invEE + pctD b unempEE

def eeSocialYearY (y : Nat) (w : Int) : Int := 11 * eeSocialMonthY y (w / 12) + eeSocialMonthY y (w - 11 * (w / 12))

theorem eeSocialYearY_2025 (w : Int) : eeSocialYearY 2025 w = eeSocialYear w := by
  simp [eeSocialYearY, eeSocialYear, eeSocialMonthY, eeSocialMonth, socMaxMonthlyFor_2025]

/-- Employee health contribution for the year (ročné zúčtovanie, ZZP § 19). -/
def eeHealthYear (w : Int) : Int := pctD (pos w) healthEE

/-- ZDP § 5 ods. 8: "Základom dane (čiastkovým základom dane) sú zdaniteľné príjmy zo závislej činnosti znížené o
poistné a príspevky, ktoré je povinný platiť zamestnanec". -/
def zd5Of (w : Int) : Int := pos w - eeSocialYear w - eeHealthYear w

/-- § 5 ods. 8 base for tax year `y` (health 4 % unchanged: ZZP § 12 ods. 1 písm. a), versions 2022-2024). -/
def zd5OfY (y : Nat) (w : Int) : Int := pos w - eeSocialYearY y w - eeHealthYear w

/-- SZČO monthly social base: (profit before contributions) / 1,486 / 12, rounded down (ZSP § 138 ods. 2, § 138
"Vymeriavací základ sa zaokrúhľuje na najbližší eurocent nadol"), within the minimum and the room left under the
shared maximum by an employment base `eeVz`. -/
def seVzMonthly (profit eeVz : Int) : Int :=
  min (max ((pos profit * 1000) / (seCoef * 12)) socMinMonthly) (pos (socMaxMonthly - eeVz))

def seSocialMonth (b : Int) : Int := pctD b sickSE + pctD b oldSE + pctD b invSE + pctD b reserveSE

/-- SZČO social contributions for the year (zero below the § 21 ods. 1 income test). -/
def seSocialYear (receipts profit eeVz : Int) : Int :=
  if seThreshold < receipts then 12 * seSocialMonth (seVzMonthly profit eeVz) else 0

/-- SZČO health contributions for the year (ZZP § 13 ods. 2, 10, 11). `employee`: also an employee all year, so the
minimum base is reduced to nothing (§ 13 ods. 11 písm. a)). -/
def seHealthYear (receipts profit : Int) (employee : Bool) : Int :=
  if receipts ≤ 0 ∧ profit ≤ 0 then 0 else
    let vz := (pos profit * 1000) / seCoef
    pctD (max vz (if employee then 0 else 12 * healthMinMonthly)) healthSE

/-- Health on the § 8 base (ZZP § 13 ods. 7). -/
def otherHealthYear (base8 : Int) : Int := pctD (pos base8) healthSE

end SkTax
