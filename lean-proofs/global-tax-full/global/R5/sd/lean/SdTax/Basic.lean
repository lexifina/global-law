import TaxKernel.World

/-!
# Sudan: personal income tax, Income Tax Act 1986 as amended, assessment year 2025 (law of the Government of Sudan)

Authority: the model is the law administered by the Taxation Chamber of the Government of the Republic of the Sudan
(tax.gov.sd), the only authority with published tax law; territory under other control during the conflict is not
distinguished. Grade B: the Act is accessible but its amounts may have been changed by later finance laws not reached.

Sources (Taxation Chamber, tax.gov.sd/laws/ "القوانين و اللوائح", uploads of February 2025, fetched from a second machine;
files in `sd/law/`):
* "The Income Tax Act, 1986" (Ministry of Justice English consolidation, Sudan Currency Printing Press;
  `Income-tax.pdf`, 140 pages). s. 30: "The tax, on the personal income, shall be paid at the rates set forth in Sector
  (B) of Schedule III annexed hereto"; Schedule III Sector (B) "Rates of Personal Income Tax (See Section 30) ...
  Resident and non-resident person | Income in Sudanese Pound | Rate | For the 9,090 pounds | Nill | For the next 120
  pounds | 5% | For the next 240 pounds | 10% | Above that | 15% | The threshhold exempted from tax shall not be enjoyed
  by non-resident individuals"; the amendment note under the table reads "Act No. 25, 2013" (symbol font). s. 2:
  "Assessment year" means twelve months. The table does not say whether its amounts are monthly or annual; the model
  applies them to annual personal income (the assessment is annual; employers withhold monthly, s. 41).
* The Arabic text (`income1.pdf`) and the Income Tax Regulations 2021/2022 were downloaded; their text layer is not
  searchable (no Arabic OCR on the build server): not used.
Not reached: finance laws after 2013 that may change Sector (B); social insurance (National Social Insurance Fund law).
-/

namespace SdTax
open TaxKernel

/-- Schedule III Sector (B), applied to annual personal income (see the note on the unit). -/
def sched : Schedule := Schedule.ofList [(0, 0), (9090, 500), (9210, 1000), (9450, 1500)]

def out (c : Canon) : Out :=
  let ps := c.adults.map fun a => sched.tax Rule.unitDown (pos a.wages)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business profits (Sector A) not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["estates leases income and other income not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "SD" "SDG" (sumInts ps)
    (detail := [Out.d "personalIncome" (sumInts (c.adults.map fun a => pos a.wages)),
      Out.dStr "authority" "Government of Sudan (Taxation Chamber, tax.gov.sd)",
      Out.dStr "note" "Schedule III Sector (B) as printed in the Ministry of Justice consolidation (amendment note Act No. 25, 2013), applied annually"])
    (unsupported := unsup ++ ["Schedule I exemptions (allowances) and Schedule II deductions not modelled: gross wage taxed",
      "finance laws after 2013 not reached: Sector (B) amounts may be out of date", "social insurance contributions not reached",
      "unit of the Sector (B) amounts (monthly or annual) not stated in the table: annual assumed"])

def country : Country := { code := "SD", name := "Sudan (Income Tax Act 1986)", currency := "SDG", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: tax on the first 9,450 pounds = 6 + 24 = 30; every pound above that bears 15 %. -/
#guard sched.tax Rule.unitDown 9450 = 30
#guard sched.tax Rule.unitDown 19450 = 30 + 1500

end SdTax
