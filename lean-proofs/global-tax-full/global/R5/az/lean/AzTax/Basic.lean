import TaxKernel.World

/-!
# Azerbaijan: income tax (Tax Code 2000, ch. on gəlir vergisi) and employee social, unemployment and medical
insurance premiums, tax year 2025

Statutes read (Global law `azerbaijan/national/acts`, official text e-qanun.az; files in `az/law/`), as in force on
2025-07-01 (art. 101 also compared 2025-01-01..2025-12-31: three amending laws, "No difference in the text"):
* Tax Code art. 101.1 table 1 (official https://e-qanun.az/framework/59338): "2500 manatadək | 14 faiz"; "2500 manatdan
  çox olduqda | 350 manat + 2500 manatdan çox olan məbləğin 25 faizi".
* art. 101.1-1 table 2: employees of taxpayers outside the oil-gas sector and the state sector, "2019-cu il yanvarın
  1-dən 7 il müddətində": "8000 manatadək | 0 faiz"; above, "8000 manatdan çox olan məbləğin 14 faizi".
* art. 101.2: non-entrepreneurial annual income 14 %; art. 101.3: entrepreneurs without a legal entity 20 %.
* art. 102.1.6: at the main place of work "aylıq gəliri 2500 manatadək olduqda, 200 manat" is exempt; 102.1.4 state
  pensions exempt; 102.1.22-3: bank interest on manat deposits "aylıq faiz gəlirlərinin 200 manatadək olan hissəsi"
  per bank exempt.
* art. 122.1: dividends "5 faiz dərəcə ilə" at source, final (122.2); art. 123.1: interest 10 % at source, final (123.2).
* Law on Social Insurance 250-IQ art. 14 (consolidated text first recorded 2025-08-13, https://e-qanun.az/versions/3/
  v_3813_2.html; identical to amending Law 1360-VQD in force 2019-01-01): 14.3.2 employee "əməkhaqqının ... 3 faizi";
  14.4 (non-oil, non-state, 7 years from 2019): "200 manatadək | ... | 3 faiz" and above "6 manat + 200 manatdan çox
  olan hissənin 10 faizi".
* Law on Unemployment Insurance 765-VQ art. 9.0.2: employee "işçinin əməkhaqqının 0,5 faizi".
* Law on Medical Insurance 725-IQ art. 15-10.1.2: employee "əməkhaqqının 8000 manatadək olan hissəsindən 2 faiz, 8000
  manatdan yuxarı olan hissəsindən 0,5 faiz".
Default sector: a private employer outside oil and gas (tables 2 and 14.4); input `"sector": "public"` (state or
oil-gas employer) selects table 1, 102.1.6 and 14.3.2.
-/

namespace AzTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 101.1 table 1 (monthly). -/
def table1 : Schedule := Schedule.ofList [(0, 1400), (2500, 2500)]
/-- art. 101.1-1 table 2 (monthly). -/
def table2 : Schedule := Schedule.ofList [(0, 0), (8000, 1400)]
/- The printed fixed sum of table 1: "350 manat". -/
#guard table1.ticks 2500 = 350 * BP

/-- art. 102.1.6: 200 manat exempt when the monthly income is at most 2 500. -/
def smallExempt (m : Int) : Int := if m ≤ 2500 then 200 else 0

/-- 250-IQ art. 14.4 (employee part, monthly). -/
def socPrivate : Schedule := Schedule.ofList [(0, 300), (200, 1000)]
#guard socPrivate.ticks 200 = 6 * BP
/-- 250-IQ art. 14.3.2. -/
def socPublic : Schedule := Schedule.flat 300
/-- 765-VQ art. 9.0.2. -/
def unemp : Schedule := Schedule.flat 50
/-- 725-IQ art. 15-10.1.2 (employee). -/
def medical : Schedule := Schedule.ofList [(0, 200), (8000, 50)]

def nonEntRate : Int := 1400   -- art. 101.2
def entRate : Int := 2000      -- art. 101.3
def divRate : Int := 500       -- art. 122.1
def intRate : Int := 1000      -- art. 123.1
/-- art. 102.1.22-3: 200 manat a month per bank (one bank assumed). -/
def depositExemptYear : Int := 12 * 200

def r (s : Schedule) (x : Int) : Int := s.tax Rule.unitHalfUp (pos x)

/-- Monthly income tax and employee premiums on a monthly wage `m`. -/
def monthTax (pub : Bool) (m : Int) : Int :=
  if pub then r table1 (m - smallExempt m) else r table2 m
def monthSoc (pub : Bool) (m : Int) : Int :=
  (if pub then r socPublic m else r socPrivate m) + r unemp m + r medical m

def out (c : Canon) : Out :=
  let pub := (c.str? "sector") == some "public"
  let rows := c.adults.map fun a =>
    let m := divR .halfUp (pos a.wages) 12
    let wageTax := if a.wages > 0 then 12 * monthTax pub m else 0
    let soc := if a.wages > 0 then 12 * monthSoc pub m else 0
    (wageTax + pct entRate (pos a.selfEmployment), soc)
  let earnTax := sumInts (rows.map (·.1))
  let soc := sumInts (rows.map (·.2))
  let divTax := pct divRate (pos c.dividends)
  let intTax := pct intRate (pos (c.interest - depositExemptYear))
  let rentTax := pct nonEntRate (pos c.rentalIncome)
  let cgTax := pct nonEntRate (pos c.capitalGains)
  Out.make c "AZ" "AZN" (earnTax + divTax + intTax + rentTax + cgTax) (employeeSocial := soc)
    (detail := [Out.d "earningsTax" earnTax, Out.d "employeePremiums" soc, Out.d "dividendTax" divTax,
      Out.d "interestTax" intTax, Out.d "rentTax" rentTax, Out.d "capitalGainsTax" cgTax,
      Out.dStr "sector" (if pub then "public (state or oil-gas): TC 101.1 table 1, 250-IQ 14.3.2" else "private non-oil (default): TC 101.1-1 table 2, 250-IQ 14.4")])
    (unsupported := ["wages assumed paid evenly over 12 months at one main workplace (the tables are monthly; 101.1-2 taxes each workplace separately)",
       "self-employed: 20 % on the given profit (101.3); exemptions 102.1.30 and the social premium on entrepreneurs (250-IQ 14.5.1, a share of the minimum wage, not read) not modelled",
       "interest assumed manat deposits at one bank (102.1.22-3: 2 400 a year exempt); 18-month deposits (102.1.22-4) not modelled",
       "capital gains taxed as non-entrepreneurial income at 14 % (101.2); 102.1.27 (50 % of gains on shares held 3+ years) not modelled",
       "pensions assumed state pensions: exempt (102.1.4)"])

def country : Country := { code := "AZ", name := "Azerbaijan (income tax + employee premiums)", currency := "AZN", year := "2025", compute := out }

theorem table2_progressive : table2.progressive = true := by decide
theorem table1_progressive : table1.progressive = true := by decide
/-- The scanners' flat-schedule slot: the private-sector table. -/
def sched : Schedule := table2
theorem sched_progressive : sched.progressive = true := by decide

/- 1 000 manat a month in the private sector: no income tax; premiums 6+80 + 5 + 20 = 111 a month. -/
#guard (out { id := "z", adults := [{ wages := 12000 }] }).incomeTax = 0
#guard (out { id := "z", adults := [{ wages := 12000 }] }).employeeSocial = 12 * 111
/- The table-1 notch at 2 500 a month (state sector): 2 500 -> 14 % of 2 300 = 322; 2 501 -> 350 + 0.25 = 350. -/
#guard monthTax true 2500 = 322 ∧ monthTax true 2501 = 350

end AzTax
