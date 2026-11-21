import TaxKernel.World

/-!
# Botswana: income tax on resident individuals under the Income Tax Act, 2026 (No. 13 of 2026), tax year 2026/27

Access tier B, **and the year is not 2025**: the tax year 2025/26 (1 July 2025 - 30 June 2026) is governed by the
Income Tax Act Cap. 52:01, whose rate schedule was not reached (Botswana e-Laws, botswanalaws.com, now shows the 2026
Act and sells the PDF; no archived copy of the Cap. 52:01 page; BURS serves only amendment acts: Income Tax
(Amendment) Act No. 1 of 2024, scanned and OCR'd, amends s. 32 and the Second Schedule (retirement lump sums 50 %, P20 000)
but not the rates). Income Tax Act, 2026 s. 144 (a): "the repealed Act shall continue to apply to tax years prior to
the tax year in which this Act comes into operation". This model is therefore the **Income Tax Act, 2026**, served by
BURS (burs.org.bw "Tax Laws 2026", download 954, Supplement A, Botswana Government Extraordinary Gazette of 1 July
2026; sha256 in `bw/law/SHA256SUMS`), for the tax year 2026/27, the first year it governs:
* "Date of Assent: 29.06.26 / Date of Commencement: 01.07.2026"; s. 2 "tax year" means "a period of 12 months beginning
  on 1st July".
* s. 9 (1), (3): income tax "at the rate specified in Schedule 1, on a person who has taxable income for the year".
* Schedule 1 Part I para 1, Resident Individuals: "0 – 48,000 0 per cent; 48,001 – 84,000 0 + 5 per cent of excess
  48,000; 84,001 – 120,000 1,800 + 12.5 per cent of excess over P84,000; 120,001 – 156,000 6,300 + 18.75 per cent ...;
  156,001 – 400,000 13,050 + 25 per cent ...; 400,001 and above 74,050 + 27.5 per cent of excess over P400,000".
* para 2: net aggregate gain of individuals: "0 – 36,000 0 per cent; 36,001 – 84,000 0 + 5 per cent ...; 84,001 –
  120,000 2,400 + 12.5 ...; 120,001 – 156,000 6,900 + 18.75 ...; 156,001 – 400,000 13,650 + 25 ...; 400,001 and above
  74,650 + 27.5 per cent". (The contract's `capitalGains` is read as the net aggregate gain.)
* para 7: resident withholding tax "(a) Dividends ... 10 per cent; (b) Interest ... 10 per cent"; s. 140: final
  charge for "(b) dividends to which section 133 (1) applies; and (c) payment of interest to a resident individual
  from a banking institution or building society".
* s. 28 (4)-(5): retirement-fund contributions deductible, "shall not exceed 15 per cent of the taxable income".
Unit: individual. No employee social-security contribution modelled (no statute found).
-/

namespace BwTax
open TaxKernel

def sched : Schedule := Schedule.ofList [(0, 0), (48000, 500), (84000, 1250), (120000, 1875), (156000, 2500), (400000, 2750)]
def gainSched : Schedule := Schedule.ofList [(0, 0), (36000, 500), (84000, 1250), (120000, 1875), (156000, 2500), (400000, 2750)]

/- Schedule 1 printed cumulative columns. -/
#guard [(84000, 1800), (120000, 6300), (156000, 13050), (400000, 74050)].all fun (t, b) => sched.ticks t = b * BP
#guard [(84000, 2400), (120000, 6900), (156000, 13650), (400000, 74650)].all fun (t, b) => gainSched.ticks t = b * BP

def whtRate : Int := 1000

/-- s. 28 (5): deduction capped at 15 % of taxable income (read as taxable income before the deduction). -/
def personTI (gross retire : Int) : Int := pos (gross - min (pos retire) (divR .down (1500 * pos gross) BP))

def personTax (ti : Int) : Int := sched.tax Rule.unitDown (pos ti)

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let rows := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    (personTI (a.wages + a.selfEmployment + a.pension + share c.rentalIncome i) (share c.pensionContributions i),
     share c.capitalGains i)
  let it := sumInts (rows.map fun r => personTax r.1)
  let cgt := sumInts (rows.map fun r => gainSched.tax Rule.unitDown (pos r.2))
  let wht := divR .down (whtRate * (c.interest + c.dividends)) BP
  Out.make c "BW" "BWP" it (surtaxes := [("capitalGainsTax", cgt), ("finalWithholdingInterestDividends", wht)])
    (detail := [Out.d "taxableIncome" (sumInts (rows.map (·.1))), Out.d "taxBeforeCredits" it,
      Out.dStr "note" "Income Tax Act 2026 Schedule 1 (tax year 2026/27); 2025/26 rates under Cap. 52:01 not reached"])
    (unsupported := ["tax year 2025/26 (Cap. 52:01 Tenth/rate schedule) not reached: the model is the Income Tax Act 2026 for 2026/27",
       "interest is read as bank / building-society interest (final 10 % WHT); dividends as s. 133 (1) dividends (final 10 %)"])

def country : Country := { code := "BW", name := "Botswana (Income Tax Act 2026, tax year 2026/27)", currency := "BWP", year := "2026/27", compute := out }

theorem sched_progressive : sched.progressive = true := by decide
theorem gainSched_progressive : gainSched.progressive = true := by decide

end BwTax
