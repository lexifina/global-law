import TaxKernel.World

/-!
# Afghanistan: income tax of a resident natural person, 2025 (Islamic Republic statute; status under the de facto
# authorities unverified)

Access tier B, with an authority caveat. **Whose law**: the Income Tax Law 2009 of the Islamic Republic of
Afghanistan (Official Gazette 976, 18 March 2009) as consolidated to the amendment in Official Gazette 1209 of 13 April
2016, in the English translation of the Afghanistan Revenue Department ("An unofficial translation ... prepared by the
Afghanistan Revenue Department, Ministry of Finance"), read from the Internet Archive copy (2018-12-22) of
ard.gov.af/wp-content/uploads/2017/07/Income-Tax-Law-2009-Consolidated-to-Dec-2016-clean-1.pdf (`af/law/
itl2009_consol2016.pdf`, sha256 4f50ddde...). Since August 2021 the de facto authorities (the "Islamic Emirate")
administer taxes; no text from them was reachable: ard.gov.af answers with a PHP fatal error, moj.gov.af does not
connect, mof.gov.af (Next.js, de facto ministry) publishes no legislation section, and Global law holds only the 2004
Constitution. The model therefore states the last accessible statute; whether the de facto authorities apply it
unchanged in 2025 is not verified (summary.json `unsupported`). The Dari/Pashto Official Gazette text (authoritative)
was not reached.
-/

namespace AfTax
open TaxKernel

def roundR : Rule := { mode := .halfUp }

/-- Art. 4 (3): "From Afs.0 to Afs.5,000 monthly 0%; From Afs.5,001 to Afs.12,500 2%; From Afs. 12,501 to Afs. 100,000
10% + Afs. 150 fixed amount; From Afs. 100,000 and above 20% + Afs.8,900 fixed amount" (a monthly schedule). -/
def monthly : Schedule := Schedule.ofList [(0, 0), (5000, 200), (12500, 1000), (100000, 2000)]

/- The fixed amounts (150; 8,900) are the band sums. -/
#guard monthly.tax roundR 12500 = 150 ∧ monthly.tax roundR 100000 = 8900

/-- Annual tax of a natural person: the monthly schedule applied to one twelfth of the year's taxable income, times 12
(the table is printed per month; reading noted). -/
def annual (x : Int) : Int := 12 * monthly.tax roundR (pos x / 12)

def compute (c : Canon) : Out :=
  let rs := c.adults.map fun a => (a.wages + a.selfEmployment, annual (a.wages + a.selfEmployment))
  Out.make c "AF" "AFN" (sumInts (rs.map (·.2)))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.1))),
                Out.dStr "authority" "Income Tax Law 2009 (Islamic Republic), consolidated to OG 1209 (2016); application by the de facto authorities in 2025 unverified"])
    (unsupported := ["statute status in 2025 under the de facto authorities not verified (no accessible text from them)",
      "rent (Art. 16, 59), interest and dividends (withholding Arts. 13, 72) and pensions (Art. 17 (2): government pensions exempt) not modelled",
      "no employee social contribution modelled (pension law not reached)"])

def country : Country :=
  { code := "AF", name := "Afghanistan (Income Tax Law 2009 as consolidated 2016; de facto status unverified)",
    currency := "AFN", year := "2025", compute := compute }

theorem sched_progressive : monthly.progressive = true := by decide
abbrev sched : Schedule := monthly

end AfTax
