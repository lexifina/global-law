import TaxKernel.World

/-!
# Zimbabwe: income tax on individuals, year of assessment 1 January - 31 December 2025, income earned in ZiG (ZWG)

Access tier B. Sources (Veritas, veritaszim.net, official Acts as published in the Government Gazette; sha256 in
`zw/law/`): Finance (No. 2) Act No. 7 of 2024 (node 7325), Finance Act No. 13 of 2023 (node 6808), Finance Act No. 7
of 2025 (node 7806); Finance Act [Chapter 23:04] consolidated to 14 March 2018 (ZimLII search excerpt only: ZimLII
document pages answer a Cloudflare challenge). The Income Tax Act [Chapter 23:06] itself was not reached.
* Finance (No. 2) Act 7/2024 s. 4: "With effect from the year of assessment beginning on the 1st January, 2025, section
  14 ... (2) ... (a) in the case of a person other than a company, a trust or a pension fund, at the specified
  percentage of each portion of his or her taxable income from employment earned in local currency — (i) so much as does
  not exceed thirty-three thousand six hundred ZiG; (ii) ... one hundred thousand eight hundred ZiG; (iii) ... three
  hundred and thirty-six thousand ZiG; (iv) ... six hundred and seventy-two thousand ZiG; (v) ... one million eight
  thousand ZiG; (vi) so much as exceeds one million eight thousand ZiG".
* s. 5 (Schedule "Credits and Rates of Income Tax", Part II, from 1 January 2025): "Up to ZiG33 600 0; ZiG33 601 to
  ZiG100 800 20; ZiG100 801 to ZiG336 000 25; ZiG336 001 to ZiG672 000 30; ZiG672 001 to ZiG1 008 000 35;
  14(2)(a)(vii) ZiG1 008 001 and more 40". (The last row cites a paragraph (vii) that s. 14 (2) (a) does not have:
  FINDINGS F2.)
* Finance Act 13/2023 s. 3 (b) (from 1 January 2024): "14(2)(b) Taxable income of individuals from trade or investment
  25".
* Finance Act 7/2025: its income-tax rate changes take effect "from the year of assessment beginning on the 1st
  January, 2026", except new 15 % items (b2, e2) for expatriates in an international financial centre and BKPO
  services (not modelled) and Fifteenth / Seventeenth / Thirty-Sixth Schedule changes.
* AIDS levy: Finance Act [Chapter 23:04] s. 14 (consolidated 2018, ZimLII excerpt): "levy equal to three per centum of
  the amount of income tax with which he or she [is chargeable] ... [after] any credits"; no amendment of it found in
  the Finance Acts of 2023-2025 read.
Unit: individual. Not modelled (listed in `unsupported`): income earned in foreign currency (s. 14 (2) (e)-style USD
bands are in the consolidated Finance Act, not reached), the Part I credits (elderly, blind, disabled: 2018 text gives
US$900 each, 2025 amounts not reached), NSSA contributions (rates in SI under Chapter 17:04, not reached), residents'
tax on interest and residents' shareholders' tax (rates not reached).
-/

namespace ZwTax
open TaxKernel

/-- Finance Act s. 14 (2) (a) bands (Finance (No. 2) Act 7/2024 s. 4) with the Schedule Part II percentages (s. 5). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (33600, 2000), (100800, 2500), (336000, 3000), (672000, 3500), (1008000, 4000)]

def tradeRate : Int := 2500   -- 14(2)(b), Act 13/2023 s. 3 (b)
def aidsLevy : Int := 300     -- Cap. 23:04 s. 14: three per centum of income tax

def empTax (x : Int) : Int := sched.tax Rule.unitDown (pos x)
def personTax (emp trade : Int) : Int := empTax emp + divR .down (tradeRate * pos trade) BP

#guard empTax 33600 = 0 ∧ empTax 100800 = 13440 ∧ empTax 336000 = 13440 + 58800

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let taxes := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    personTax (a.wages + a.pension) (a.selfEmployment + share c.rentalIncome i)
  let it := sumInts taxes
  let levy := divR .down (aidsLevy * it) BP
  Out.make c "ZW" "ZWG" it (surtaxes := [("AIDSLevy", levy)]) (employeeSocial := 0)
    (detail := [Out.d "taxableIncome" (sumInts (c.adults.map fun a => a.wages + a.pension + a.selfEmployment) + c.rentalIncome),
      Out.d "taxBeforeCredits" it,
      Out.dStr "note" "Finance Act Cap. 23:04 s. 14 (2) (a) ZiG bands 2025 (Finance (No. 2) Act 7/2024); trade/investment 25 % (14 (2) (b)); AIDS levy 3 % of tax"])
    (unsupported := (if c.interest ≠ 0 ∨ c.dividends ≠ 0 then ["residents' tax on interest and residents' shareholders' tax: rates not reached"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains tax (Capital Gains Tax Act) not modelled"] else []) ++
      (if c.pensionContributions ≠ 0 then ["pension contribution deduction: limits in the consolidated Act not reached"] else []) ++
      ["income earned in foreign currency (USD bands of the consolidated Finance Act) not reached; all income is read as ZiG",
       "Part I credits (elderly, blind, disabled persons) 2025 amounts not reached",
       "NSSA pension contributions: rates and insurable-earnings ceiling in SIs not reached"])

def country : Country := { code := "ZW", name := "Zimbabwe (2025, income in ZiG)", currency := "ZWG", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end ZwTax
