import TaxKernel.World

/-!
# Cambodia: tax on salary (resident employees) and the tax on income of sole proprietorships, 2025

Access tier A for the tax (statute + sub-decree as dated law); NSSF contributions not reached (unsupported).
Sources (saved in `kh/law/`, sha256 in `kh/law/SHA256SUMS` and `kh/law/rescue/SHA256SUMS`):
* Law on Taxation (ច្បាប់ស្តីពីសារពើពន្ធ), promulgated by Royal Kram NS/RKM/0523/004 of 16 May 2023, published by the
  General Department of Taxation (tax.gov.kh), 84-page scan `law_taxation_2023.pdf`; read with tesseract Khmer
  (tessdata_best `khm`, OCR in `law_taxation_2023_khm_ocr.txt`) and checked on the page images (pp. 20-23):
  - art. 41: residents are taxed on Cambodian- and foreign-source salary.
  - art. 45: monthly base of a resident = taxable salary less (1) "ប្រាក់កាត់ទុកដែលជាកាតព្វកិច្ច" under the labour and
    social-security laws and (2) the exempt payments of art. 44.
  - art. 46(2): a resident employee with dependent children and/or a spouse who is only a homemaker ("សហព័ទ្ធដែល
    ធ្វើតែជាមេផ្ទះ") gets a reduction of the base "តាមចំនួនដែលត្រូវកំណត់ដោយអនុក្រឹត្យ" (amount set by sub-decree).
  - art. 47: progressive rates "០(សូន្យ)ភាគរយ ៥(ប្រាំ)ភាគរយ ១០(ដប់)ភាគរយ ១៥(ដប់ប្រាំ)ភាគរយ និង ២០(ម្ភៃ)ភាគរយ" on the
    monthly taxable salary, withheld by the employer; the bands are set by sub-decree.
  - art. 48: fringe benefits at 20 % of their market value (not in the household contract).
  - art. 49: non-residents 20 % final (not in the household contract).
* Sub-Decree No. 48 ANKr.BK of 11 March 2024 on the monthly taxable salary and annual taxable income bands (GDT
  sub-decree list, status "Valid" on 2026-11-20; `rescue/sd48.pdf`, 3-page scan, read on the page image p. 2):
  - art. 3(1) monthly bands (riel): 0-1,500,000 0 %; 1,500,001-2,000,000 5 %; 2,000,001-8,500,000 10 %;
    8,500,001-12,500,000 15 %; over 12,500,000 20 %.
  - art. 3(2): reduction of the base "១៥០ ០០០ រៀល ក្នុងកូនម្នាក់ៗក្នុងមួយខែ" (150,000 riel per dependent child per month)
    and 150,000 riel a month for one homemaker spouse; where both spouses work the child reduction goes to one spouse only.
  - art. 4 annual bands (riel) for sole proprietorships: 0-18,000,000 0 %; to 24,000,000 5 %; to 102,000,000 10 %;
    to 150,000,000 15 %; over 150,000,000 20 %.
  - art. 6: in force from the date of signature (11 March 2024), so for the whole of 2025.
Household mapping: each adult's `wages` is a year's taxable salary paid evenly over 12 months (`perPeriod 12`);
`selfEmployment` = the annual taxable income of a sole proprietorship (art. 4). Rounding: whole riel, down (the texts
print no rounding rule). Children in the household are taken as dependent children (the sub-decree does not define them).
-/

namespace KhTax
open TaxKernel

/-- Sub-decree 48/2024 art. 3(1): monthly salary bands (riel). -/
def sched : Schedule := Schedule.ofList [(0, 0), (1500000, 500), (2000000, 1000), (8500000, 1500), (12500000, 2000)]
/-- Sub-decree 48/2024 art. 4: annual bands for a sole proprietorship's taxable income (riel). -/
def schedSP : Schedule := Schedule.ofList [(0, 0), (18000000, 500), (24000000, 1000), (102000000, 1500), (150000000, 2000)]

/-- art. 3(2): 150,000 riel per dependent child and 150,000 for one homemaker spouse, per month. -/
def childRelief : Int := 150000
def spouseRelief : Int := 150000

/-- Tax for one month on a monthly salary `m` with a monthly base reduction `r`. -/
def monthTax (r m : Int) : Int := sched.tax Rule.unitDown (pos (m - r))

/-- A year's salary tax for one employee: 12 months of the monthly tax. -/
def yearTax (r wages : Int) : Int := perPeriod 12 (monthTax r) wages

/- The monthly table is the yearly table / 12: at the top band edge the month's tax is 5 % of 500,000 + 10 % of
   6,500,000 + 15 % of 4,000,000 = 25,000 + 650,000 + 600,000. -/
#guard sched.tax Rule.unitDown 12500000 = 1275000
#guard schedSP.tax Rule.unitDown 150000000 = 300000 + 7800000 + 7200000

structure Res where
  tax : Int
  base : Int
  reliefMonthly : Int

/-- Household: individual taxation; the child reduction goes to one spouse (taxpayer's choice: the cheaper one). -/
def wageTax (c : Canon) : Res :=
  let kids : Int := c.nChildren
  let ch := childRelief * kids
  match c.adults with
  | [a] => ⟨yearTax ch a.wages, pos (a.wages - 12 * ch), ch⟩
  | [a, b] =>
    let spA : Int := if c.married && b.earnings ≤ 0 then spouseRelief else 0
    let spB : Int := if c.married && a.earnings ≤ 0 then spouseRelief else 0
    -- option 1: children with a; option 2: children with b (only one spouse may claim them, art. 3(2))
    let o1 := yearTax (spA + ch) a.wages + yearTax spB b.wages
    let o2 := yearTax spA a.wages + yearTax (spB + ch) b.wages
    let base := pos (a.wages - 12 * spA) + pos (b.wages - 12 * spB) - 12 * ch
    ⟨min o1 o2, pos base, spA + spB + ch⟩
  | _ => ⟨sumInts (c.adults.map fun a => yearTax 0 a.wages), sumInts (c.adults.map (·.wages)), 0⟩

def out (c : Canon) : Out :=
  let r := wageTax c
  let sp := sumInts (c.adults.map fun a => schedSP.tax Rule.unitDown (pos a.selfEmployment))
  Out.make c "KH" "KHR" r.tax (surtaxes := [("taxOnIncomeSoleProprietorship", sp)])
    (employeeSocial := 0)
    (detail := [Out.d "monthlyBaseReduction" r.reliefMonthly, Out.d "annualTaxableSalaryAfterReliefs" r.base,
      Out.dStr "note" "Law on Taxation 2023 arts. 45-47 + Sub-Decree 48 ANKr.BK (11 Mar 2024) arts. 3-4; monthly salary = annual / 12; self-employment = sole-proprietorship taxable income (art. 4 annual bands)"])
    (unsupported := ["NSSF employee pension contribution (deductible under art. 45(1)) not read: employeeSocial = 0 and the base is not reduced"] ++
      (if c.interest ≠ 0 ∨ c.dividends ≠ 0 ∨ c.rentalIncome ≠ 0 ∨ c.capitalGains ≠ 0 then
        ["investment income: the withholding-tax and capital-gains provisions of the Law on Taxation 2023 were not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: treatment not read"] else []))

def country : Country := { code := "KH", name := "Cambodia", currency := "KHR", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide
theorem schedSP_progressive : schedSP.progressive = true := by decide

end KhTax
