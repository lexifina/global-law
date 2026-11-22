import TaxKernel.World

/-!
# Maldives: income tax of a resident individual, tax year 2025 (calendar year)

Access tier A. Statute: ޤާނޫނު ނަންބަރު 25/2019 (އާމްދަނީން ޓެކްސް ނެގުމުގެ ޤާނޫނު, Income Tax Act), in the consolidation
with the first amendment (ޤާނޫނު ނަންބަރު 15/2021), in force from 20 July 2021 until the consolidation with the second
amendment (Law 11/2026) of 31 August 2026: mvlaw.gov.mv/en/legislations/294/consolidations/1313 (Attorney General's
Office; page saved `mv/law/mvlaw294_1313.html`, sha256 691b23f2...; Global law `maldives/national/acts/law-294` holds only
the 2026 consolidation, whose s. 7 table is identical, checked). Pension: ޤާނޫނު ނަންބަރު 8/2009 (Maldives Pension Act)
s. on contributions, unamended paragraph (mvlaw legislation 113; Global law law-113). Dhivehi text read directly; every
amount below is printed in the act in digits and words.
-/

namespace MvTax
open TaxKernel

def roundR : Rule := { mode := .halfUp }

/-- s. 7 (ހ) (ފަރުދުންގެ ޓެކްސް ރޭޓު, individuals' tax rates): "720,000 (ހަތް ލައްކަ ވިހި ހާސް) ރުފިޔާ ނުވަތަ އެއަށްވުރެ
ކުޑަ 0%"; above 720,000 to 1,200,000 "5.5%"; above 1,200,000 to 1,800,000 "8%"; above 1,800,000 to 2,400,000 "12%";
above 2,400,000 "15%"; s. 7 (ށ): the tax is the sum over the brackets. -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (720000, 550), (1200000, 800), (1800000, 1200), (2400000, 1500)]

/-- s. 54 (ހ): the employer's monthly withholding table (60,000 / 100,000 / 150,000 / 200,000 a month, same rates) is the
annual table divided by 12: checked. -/
def monthly : Schedule := Schedule.ofList [(0, 0), (60000, 550), (100000, 800), (150000, 1200), (200000, 1500)]
#guard [720000, 960000, 1200000, 1500000, 1800000, 2400000, 3000000].all fun y => monthly.ticks (y / 12) * 12 == sched.ticks y

/-- s. 12 (ޅ)(2): interest (other than listed securities) exempt "ޖުމްލަ 5,000 (ފަސް ހާސް) ރުފިޔާއާ ހަމައަށް" (up to
5,000 in a period); s. 12 (ހ): dividends from a resident company exempt; s. 12 (ދ): pensions under the Pension Act
exempt. s. 19: contributions to the Maldives Retirement Pension Scheme are deductible. -/
def interestExempt : Int := 5000

/-- Pension Act 8/2009 (unamended paragraph): "ޕެންޝަނަބަލް ވޭޖްގެ މަދުވެގެން %7 އެމުވައްޒަފަކު" (at least 7 % of the
pensionable wage by the employee), for employees aged 16 to 65. Pensionable wage read as wages. -/
def pensionRate : Int := 700

structure PersonOut where
  ti : Int
  tax : Int
  pens : Int

def person (age : Nat) (wages se rent interest : Int) (donation : Int) : PersonOut :=
  let pens := if age ≥ 16 && age < 65 then divR .halfUp (pensionRate * pos wages) BP else 0
  let ti := pos (wages + se + rent + pos (interest - interestExempt) - pens - donation)
  { ti, tax := sched.tax roundR ti, pens }

def compute (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let rs := (c.adults.zip (List.range n)).map fun (a, i) =>
    person a.age a.wages a.selfEmployment (share c.rentalIncome i) (share c.interest i) (if i = 0 then c.charitable else 0)
  Out.make c "MV" "MVR" (sumInts (rs.map (·.tax))) (employeeSocial := sumInts (rs.map (·.pens)))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.ti)))])
    (unsupported := ["dividends from resident companies exempt (s. 12 (ހ)); pensions under the Pension Act exempt (s. 12 (ދ))",
      "capital gains (ss. 30-34) not modelled; charitable donations deducted in full (the s. 19 cap is not modelled)",
      "pension contribution applies to Maldivian employees under the Pension Act; expatriate coverage not modelled"])

def country : Country :=
  { code := "MV", name := "Maldives (tax year 2025)", currency := "MVR", year := "2025", compute := compute }

theorem sched_progressive : sched.progressive = true := by decide

end MvTax
