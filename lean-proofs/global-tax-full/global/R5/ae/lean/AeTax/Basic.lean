import TaxKernel.World

/-!
# United Arab Emirates 2025: no personal income tax on wages; employee pension (nationals) and ILOE premium (all)

Sources (all read 2026-11-20, copies in `ae/law/`):
* Federal Decree-Law No. 47 of 2022 on the Taxation of Corporations and Businesses, as amended (MoF consolidated
  English text, mof.gov.ae, `fdl47-2022_ct_en.pdf`): art. 11(3)(c) "A natural person who conducts a Business or
  Business Activity in the State" is a Resident Person; art. 11(6) the Cabinet specifies "the categories of Business
  or Business Activity conducted by a resident or non-resident natural person that are subject to Corporate Tax";
  art. 12(2) a natural person's Taxable Income is income "insofar as it relates to the Business or Business
  Activity". No federal law levies a tax on employment income.
* Federal Tax Authority, "Basis of Taxation - Natural Person" (tax.gov.ae, last updated 2024-05-06; official
  secondary): "Sources generating the following income streams are not considered as Business or Business
  Activities: Wages; Personal Investment Income; Real Estate Investment Income".
* Federal Decree-Law No. 57 of 2023 on Pensions and Social Security (GPSSA English text "and its amendments",
  `fdl57-2023_en.pdf`; Official Gazette 762, in force 31 October 2023): art. 2(1) applies "to an insured who starts
  working for an employer as of the date of its implementation"; art. 1 "The Insured: Every Emirati working for an
  employer"; art. 3(1) age not less than 18; art. 4(1)(a) "Monthly contributions born by the insured, in the value
  of (11%)"; art. 5(2) private sector: "not less than Dh3,000 ... with a maximum of Dh70,000".
* Federal Law No. 7 of 1999 (GPSSA English text, scanned 2022 edition, OCR in `fl7-1999_en_2022_ocr.txt`), for
  Emiratis insured before 31 October 2023 (option `"aePensionLaw": "1999"`): art. 2 "Monthly subscriptions born by
  the insured, amounting to 5%"; art. 1 private sector salary "less than 1.000 Dirhams ... such minimum limit",
  "exceed 50.000 Dirhams per month, such amount shall not be taken into account".
* Federal Decree-Law No. 13 of 2022 on the Unemployment Insurance Scheme (ILOE pool copy, `fdl13-2022_iloe.pdf`,
  "not an official translation"): art. 3(1) all workers except investors, domestic workers, temporary contract
  workers, juveniles under 18 and pension-receiving retirees; art. 4 the Cabinet sets "the value of the monthly
  subscription payable by the insured". Premium (Cabinet Resolution 97 of 2022, not read; official secondary: the
  scheme operator's page iloe.ae): "Basic Salary 16,000 AED or below 5 AED+ VAT/MONTH", "Basic Salary Above
  16,000 AED 10 AED+VAT/ Month".

Household mapping: each adult's `wages` are the contract salary = basic salary (the contract has no allowances);
the federal (GPSSA) scheme, private sector; Abu Dhabi's own pension scheme is not modelled (`"emirate":"abudhabi"`).
Nationality from the optional input field `"nationality"`: `national` (default), `expatriate`, `gcc`.
-/

namespace AeTax
open TaxKernel

/-- `rate` basis points of `base`, whole dirhams, rounded down. -/
def pct (rate base : Int) : Int := divR .down (rate * pos base) 10000

def nationality (c : Canon) : String := (c.str? "nationality").getD "national"

/-! ## FDL 57/2023 (default) and FL 7/1999 employee pension, private sector -/

/-- FDL 57/2023 art. 4(1)(a): 11 %. -/
def rate2023 : Int := 1100
/-- FDL 57/2023 art. 5(2): contribution salary between Dh3,000 and Dh70,000 a month (annual: × 12). -/
def floor2023 : Int := 3000 * 12
def ceiling2023 : Int := 70000 * 12
/-- FL 7/1999 art. 2: 5 %; art. 1 (private sector): Dh1,000 minimum, Dh50,000 maximum a month. -/
def rate1999 : Int := 500
def floor1999 : Int := 1000 * 12
def ceiling1999 : Int := 50000 * 12

/-- Contribution on a salary clamped to [floor, ceiling] (nothing without wages). -/
def clampedContribution (rate floor ceiling w : Int) : Int :=
  if w ≤ 0 then 0 else pct rate (clamp floor ceiling w)

def pension2023 (w : Int) : Int := clampedContribution rate2023 floor2023 ceiling2023 w
def pension1999 (w : Int) : Int := clampedContribution rate1999 floor1999 ceiling1999 w

/-! ## ILOE premium (FDL 13/2022 art. 4; amounts official secondary) -/

/-- 5 AED a month up to a basic salary of 16,000 AED a month, 10 AED above; VAT on the premium not included. -/
def iloeThreshold : Int := 16000 * 12
def iloe (w : Int) : Int := if w ≤ 0 then 0 else if w ≤ iloeThreshold then 5 * 12 else 10 * 12

def personSocial (nat lawYear : String) (a : Adult) : Int × Int :=
  let ilo := if a.age < 18 then 0 else iloe a.wages
  let pen :=
    if nat ≠ "national" ∨ a.age < 18 then 0
    else if lawYear = "1999" then pension1999 a.wages else pension2023 a.wages
  (pen, ilo)

def out (c : Canon) : Out :=
  let nat := nationality c
  let lawYear := (c.str? "aePensionLaw").getD "2023"
  let parts := c.adults.map (personSocial nat lawYear)
  let pen := sumInts (parts.map (·.1))
  let ilo := sumInts (parts.map (·.2))
  let se := c.adults.any (fun a => a.selfEmployment > 0)
  let uns :=
    (if se then ["self-employment: UAE Corporate Tax on a natural person's Business (FDL 47/2022 art. 11(6), Cabinet decision not read) not modelled"] else [])
    ++ (if c.str? "emirate" = some "abudhabi" then ["Abu Dhabi pension scheme (Emiratis employed in Abu Dhabi) not modelled"] else [])
    ++ (if nat = "gcc" then ["GCC national: contributions follow the home state's law (GCC unified insurance extension), not modelled"] else [])
  Out.make c "AE" "AED" 0 (employeeSocial := pen + ilo)
    (detail := [Out.d "pension" pen, Out.d "iloePremium" ilo, Out.dStr "nationality" nat,
      Out.dStr "pensionLaw" (if lawYear = "1999" then "FL 7/1999 art. 2 (5 %)" else "FDL 57/2023 art. 4 (11 %)"),
      Out.dStr "note" "no personal income tax: FDL 47/2022 art. 11-12 tax a natural person only on Business income; FTA: wages are not Business"])
    (unsupported := uns)

def country : Country :=
  { code := "AE", name := "United Arab Emirates (federal; GPSSA private sector)", currency := "AED", year := "2025",
    compute := out }

end AeTax
