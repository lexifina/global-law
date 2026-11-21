import BfTax.Params

/-!
# Burkina Faso 2025: impôt unique sur les traitements et salaires (IUTS), IRF, IRCM, CNSS

The IUTS is "calculé et retenu mensuellement" (art. 112) on the month's net taxable pay (art. 111); the year is twelve
equal months, with the annual regularisation of art. 119 on the same basis. Spouses are taxed separately (art. 113 3)):
the family charges go to the husband unless retained by the employed wife; reading: to the higher earner; a spouse
without pay is one charge (art. 113 2) c)). Pensions are exempt (art. 106 3)). The IRF and IRCM are schedular taxes
withheld at source; no global income tax applies to individuals' wages.

Reading: the household's wage is the "salaire de base" of art. 111 (the contract has no indemnities), so the 25 %
abattement applies to the whole wage; the option `"bfCategory": "superior"` gives the 20 % rate of the higher
categories.
-/

namespace BfTax
open TaxKernel

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
def monthOf (annual : Int) (m : Int) : Int := annual * m / 12 - annual * (m - 1) / 12

def cnssMonth (g : Int) : Int := if g ≤ 0 then 0 else divR .down (g * cnssEmployee) BP

/-- Art. 111: net taxable monthly pay. -/
def netMonth (abat g : Int) : Int :=
  if g ≤ 0 then 0 else
  pos (g - min (cnssMonth g) (g * pensionDedCap / BP) - g * abat / BP)

/-- Art. 112-113: one month's IUTS with `n` family charges. -/
def iutsMonth (abat n g : Int) : Int :=
  let t := divR .down (monthly.ticks (netMonth abat g)) BP
  t - divR .down (t * chargeRate n) BP

def iutsYear (abat n w : Int) : Int := sumInts (months.map fun m => iutsMonth abat n (monthOf w m))

def irfYear (rent : Int) : Int :=
  sumInts (months.map fun m =>
    let r := monthOf (pos rent) m
    divR .down (irfMonthly.ticks (r - r * rentAbat / BP)) BP)

def out (c : Canon) : Out :=
  let kids : Int := c.childrenUnder childAgeLimit
  let abat := if (c.str? "bfCategory").getD "" == "superior" then abatSuperior else abatOrdinary
  let married := c.married && c.adults.length == 2
  let ws := c.adults.map (·.wages)
  let top := ws.foldl max 0
  let idxTop := (ws.findIdx? (· == top)).getD 0
  let spouseCharge : Int := if married && ws.any (· ≤ 0) then 1 else 0
  let iuts := sumInts ((ws.zipIdx).map fun (w, i) =>
    if w ≤ 0 then 0 else iutsYear abat (min 4 (if i == idxTop then kids + spouseCharge else 0)) w)
  let irf := irfYear c.rentalIncome
  let ircm := divR .down (pos c.interest * bankInterestRate + pos c.dividends * dividendRate) BP
  let soc := sumInts (ws.map fun w => sumInts (months.map fun m => cnssMonth (monthOf w m)))
  let unsup :=
    ["loi de finances 2025 not reached: amounts are the CGI 2023 edition's (LF 2024 and LFR 2024 checked: no change)",
     "employeeSocial: CNSS 5,5 % (décret 2003-252) without the contribution ceiling (not read)"] ++
    (if c.capitalGains != 0 then ["capitalGains: not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: BIC/BNC and the CME not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: civil and military pensions exempt (art. 106 3)); other pensions treated the same (reading)"] else [])
  Out.make c "BF" "XOF" (iuts + irf + ircm) (employeeSocial := soc)
    (detail := [Out.d "iuts" iuts, Out.d "irf" irf, Out.d "ircm" ircm,
                Out.d "taxableIncome" (sumInts (ws.map fun w => sumInts (months.map fun m => netMonth abat (monthOf w m)))),
                Out.dStr "note" "CGI 2023 (LF 2023) arts. 111-113 monthly IUTS with 8-14 % family reduction; IRF 50 % abattement 18/25 %; IRCM 12,5 %; CNSS 5,5 %"])
    (unsupported := unsup)

def country : Country :=
  { code := "BF", name := "Burkina Faso (IUTS, IRF, IRCM, CNSS)", currency := "XOF", year := "2025", compute := out }

end BfTax
