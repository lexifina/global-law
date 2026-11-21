import TaxKernel.World

/-!
# Laos: income tax on salaries (resident), social security (private-sector employee), 2025

Access tier A for the tax (two dated laws, a mid-year change); the social-security wage ceiling is not reached.
Sources: Lao Official Gazette (laoofficialgazette.gov.la, "ນິຕິກໍາ / ກົດໝາຍ" lists, read 2026-11-20), scans OCR'd with
tesseract `lao` (tessdata_best) and the tables read on the page images; files in `la/law/rescue/` (sha256 in SHA256SUMS):
* Law on Income Tax No. 67/NA of 18 June 2019 (`pit2019.pdf`, gazette id 1581, status "old version"):
  - art. 35(1): exempt "ເງິນເດືອນ ແລະ ເງິນລາຍໄດ້ອືນ ແຕ່ ຫນຶ່ງລ້ານສາມແສນກີບ ລົງມາ" (salary up to 1,300,000 kip);
  - art. 36(2): salary tax computed and withheld monthly;
  - art. 39(1) table (p. 18 of the law, image): monthly income to 1,300,000 0 %; 1,300,000-5,000,000 5 % (185,000);
    5,000,000-15,000,000 10 % (1,000,000; cumulative 1,185,000); 15,000,000-25,000,000 15 % (1,500,000; 2,685,000);
    25,000,000-65,000,000 20 % (8,000,000; 10,685,000); over 65,000,000 25 %;
  - art. 39(5): 10 % of dividends and of rent; art. 35(11): bank-deposit interest exempt.
  The Law No. 01/NA of 7 August 2021 amending tax laws replaced only arts. 14, 16, 18 and 73 of this law (its art. 3).
* Law on Income Tax (amended), adopted by National Assembly resolution 164/NA of 25 June 2025, promulgated by presidential decree of August 2025
  (`pit2025.pdf`, gazette id 2597, published 19 June 2026, status "current"):
  - art. 74: "ມີຜົນສັກສິດ ນັບແຕວັນທີ 1 ກັນຍາ 2025" (in force from 1 September 2025), replacing Law 67/NA;
  - art. 38(1) table (p. 18, image): to 2,500,000 0 %; 2,500,000-5,000,000 5 % (125,000); 5,000,000-15,000,000 10 %
    (1,000,000; cumulative 1,125,000); 15,000,000-25,000,000 15 % (2,625,000); 25,000,000-65,000,000 20 %
    (10,625,000); over 65,000,000 25 %; the bands "ຈະມີການປັບປຸງ ຕາມຄາແຮງງານຂັ້ນຕໍ່າ" (adjusted with the minimum wage);
  - art. 34(1): salary at the government's minimum wage is exempt; art. 34(12) bank-deposit interest exempt;
    art. 38(5.1) dividends 10 %, (5.3) rent 10 %.
* Law on Social Security (amended) No. 54/NA of 27 June 2018 (`ssl2018.pdf`, gazette id 1442): art. 74(2.2)
  employee of an enterprise "ຫ້າຈຸດຫ້າ ສ່ວນຮ້ອຍ (5,5%) ຂອງເງິນປະກັນຕົນ"; art. 77: the government sets the ceiling
  of the insured wage (not reached). The 2025 edict amended only arts. 34 and 38 (pension conditions).
Household mapping: `wages` = a year's salary paid evenly (perPeriodIdx 12: months 1-8 under Law 67/NA, months 9-12
under the 2025 law); individual taxation; `dividends` and `rentalIncome` taxed at 10 % of the amount (the law taxes the
gross rent); `interest` read as bank-deposit interest (exempt). Rounding: whole kip, down (no rule printed).
-/

namespace LaTax
open TaxKernel

/-- Law 67/NA (2019) art. 39(1) monthly bands, kip. -/
def sched2019 : Schedule := Schedule.ofList [(0, 0), (1300000, 500), (5000000, 1000), (15000000, 1500), (25000000, 2000), (65000000, 2500)]
/-- Law on Income Tax (amended 2025) art. 38(1) monthly bands, kip; in force from 1 September 2025 (art. 74). -/
def sched2025 : Schedule := Schedule.ofList [(0, 0), (2500000, 500), (5000000, 1000), (15000000, 1500), (25000000, 2000), (65000000, 2500)]

/- Each law's printed cumulative column. -/
#guard sched2019.tax Rule.unitDown 5000000 = 185000 ∧ sched2019.tax Rule.unitDown 15000000 = 1185000 ∧
  sched2019.tax Rule.unitDown 25000000 = 2685000 ∧ sched2019.tax Rule.unitDown 65000000 = 10685000
#guard sched2025.tax Rule.unitDown 5000000 = 125000 ∧ sched2025.tax Rule.unitDown 15000000 = 1125000 ∧
  sched2025.tax Rule.unitDown 25000000 = 2625000 ∧ sched2025.tax Rule.unitDown 65000000 = 10625000

/-- Month `i` (0 = January): Law 67/NA to August, the 2025 law from September. -/
def monthTax (i : Nat) (m : Int) : Int :=
  if i < 8 then sched2019.tax Rule.unitDown (pos m) else sched2025.tax Rule.unitDown (pos m)

def salaryTax (wages : Int) : Int := perPeriodIdx 12 monthTax wages

/-- SSL art. 74(2.2): 5.5 % of the insured wage (ceiling of art. 77 not reached: applied without a ceiling). -/
def sscMonth (m : Int) : Int := divR .down (550 * pos m) BP
def ssc (wages : Int) : Int := perPeriod 12 sscMonth wages

def out (c : Canon) : Out :=
  let wt := sumInts (c.adults.map fun a => salaryTax a.wages)
  let ss := sumInts (c.adults.map fun a => ssc a.wages)
  let divTax := divR .down (1000 * pos c.dividends) BP
  let rentTax := divR .down (1000 * pos c.rentalIncome) BP
  Out.make c "LA" "LAK" wt (surtaxes := [("dividendTax", divTax), ("rentalIncomeTax", rentTax)])
    (employeeSocial := ss)
    (detail := [Out.d "salaryTaxJanAug" (sumInts (c.adults.map fun a => perPeriodIdx 12 (fun i m => if i < 8 then monthTax i m else 0) a.wages)),
      Out.dStr "note" "Law 67/NA (2019) art. 39(1) for January-August, amended Law on Income Tax (2025) art. 38(1) from 1 September 2025 (art. 74); bank-deposit interest exempt (art. 35(11) / 34(12)); dividends and rent 10 %"])
    (unsupported := (if c.adults.any (fun a => a.wages > 0) then ["social security: the insured-wage ceiling (SSL art. 77, government decision) was not reached; 5.5 % applied without a ceiling"] else []) ++
      (if c.adults.any (fun a => a.selfEmployment ≠ 0) then ["self-employment: the law taxes gross receipts of unregistered professionals by activity (art. 39/38 items 3-5); not mapped from net income"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: 2 % of the sale price of shares or land (art. 39(3) / 38(3)) needs the price"] else []) ++
      ["minimum wage (2025 law art. 34(1) and the note to art. 38(1)): bands used as printed; a government minimum-wage change in Sep-Dec 2025 was not checked"])

def country : Country := { code := "LA", name := "Laos", currency := "LAK", year := "2025", compute := out }

theorem sched_progressive : sched2019.progressive = true := by decide
theorem sched2025_progressive : sched2025.progressive = true := by decide

/-- The scaffold's theorems refer to `sched`: the schedule in force at the start of 2025. -/
abbrev sched := sched2019

/- The 2025 law cuts tax at every income: the bands above 1,300,000 shift down by 60,000 of tax at most. -/
#guard (List.range 200).all fun k => let m : Int := 500000 * k; sched2025.tax Rule.unitDown m ≤ sched2019.tax Rule.unitDown m
#guard sched2019.tax Rule.unitDown 70000000 - sched2025.tax Rule.unitDown 70000000 = 60000

end LaTax
