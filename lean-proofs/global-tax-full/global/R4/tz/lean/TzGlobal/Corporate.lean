import R4Common

/-!
# Tanzania 2025: corporate income tax (1200) and withholding — grade B

Source: Income Tax Act Cap. 332 R.E. 2023 (`cmp20/world/B10-anglophone-africa/tz/law/The_Income_Tax_Act.txt`), with
the Finance Act 2024 (No. 6, Part X, s. 33-47) and the Finance Act 2025 (No. 11, Part XIII, s. 46-61; in force 1 July
2025, s. 2) read against these rules (`THE_FINANCE_ACT_2025.txt`, `Finance_Act_2024_1.txt` in the same folder).

* First Schedule para 3 (1): "The total income of a corporation … for a year of income shall be taxed at the rate of
  thirty percent" (not amended in 2024-2025). (3): "Income of a corporation with perpetual unrelieved loss for three
  consecutive years shall be taxed at the rate of 0.5 percent of the turnover of the third year" (flag
  `perpetualLoss3`); FA 2025 s. 60 (d) (ii) substitutes "1" for "0.5" from 1 July 2025. **Year in force (twentieth
  pass):** para 5 (3) of the First Schedule: where a para 1-3 rate changes "and the change takes effect on a date other
  than the start of a person's year of income … (a) the person's total income shall be apportioned between the part of
  the year of income occurring before the change and the remaining part according the number of days in each part;
  (b) the total income attributable to the part … before the change shall be taxed at the rate applicable before the
  change and that attributable to the remaining part shall be taxed at the rate applicable after the change". A
  calendar year of income 2025: turnover × (0.5 % × 181/365 + 1 % × 184/365), rounded down once. FA 2025 s. 60 (d) (i)
  ("thirty percent" -> "twenty five percent" in para 3 (2) (a)) is the public float a newly listed company needs for
  the reduced 25 % rate, not a rate: the listed-company rate is not modelled. (4): repatriated income of a domestic PE
  "ten percent" (not modelled).
* Para 4 (withholding): (a) (ii) payments under s. 104 to a non-resident "fifteen percent"; (b) (i) (bb) dividends
  "of any other corporation – ten percent"; (ii) "interest … paid to a non-resident withholdee – ten percent"; (iv)
  "other payments - fifteen percent" (royalties); (c) (i) service fees under s. 106 (1) (a): "fifteen percent for a
  non-resident". FA 2025 s. 60 (e) raises the resident rates of para 4 (c) (i)-(ii) (5 -> 10 %) and adds (v) (gaming
  commissions 10 %); FA 2024 s. 46 (b)-(c) adds resident sports royalties (5 %), digital content (5 %) and digital
  assets (3 %): none of these is a non-resident rate modelled here, so no withholding rule changes in 2025.
-/

namespace TzGlobal
open TaxKernel TaxKernel.Global

def cit : CorpRegime := { name := "Corporate income tax", sched := Schedule.flat 3000 }

/-- The perpetual-loss minimum for a calendar year of income 2025 (First Schedule para 3 (3) and para 5 (3)):
0.5 % on 181/365 of the turnover (1 January-30 June) and 1 % on 184/365 (1 July-31 December), rounded down once:
turnover × (50 × 181 + 100 × 184) / (10 000 × 365) = turnover × 27 450 / 3 650 000. -/
def amt2025 (turnover : Int) : Int := (27450 * max turnover 0) / 3650000

def amtOf (co : Company) : R4.MinTax := if co.flags.contains "perpetualLoss3" then { fixed := amt2025 co.turnover } else {}

def wht : Wht :=
  { name := "Withholding tax (non-residents)",
    rules := [{ kind := .dividend, rateBp := 1000, statute := "ITA First Schedule para 4 (b) (i) (bb) (10 %)" },
              { kind := .interest, rateBp := 1000, statute := "ITA First Schedule para 4 (b) (ii) (10 %)" },
              { kind := .royalty, rateBp := 1500, statute := "ITA First Schedule para 4 (b) (iv) (15 %)" },
              { kind := .services, rateBp := 1500, statute := "ITA First Schedule para 4 (c) (i) (15 %, non-resident)" }] }

def citStatute : String :=
  "ITA First Schedule para 3 (1) (30 %); para 3 (3) perpetual-loss minimum 0.5 % of turnover to 30 June 2025 and 1 % from 1 July 2025 (FA 2025 s. 60 (d) (ii)), the year of income apportioned by days (para 5 (3)): 181/365 at 0.5 %, 184/365 at 1 % for a calendar year 2025"

def corporate : Family :=
  { name := "1200 corporate income tax", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [R4.citCharge cit (amtOf g.company) g.company citStatute]
      ++ wht.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.profit < 0 then ["ITA First Schedule para 3 (3): the turnover minimum (0.5 % to 30 June 2025, 1 % from 1 July, apportioned by days, para 5 (3)) only after three consecutive years of perpetual unrelieved loss (flag perpetualLoss3)"] else [])
  ++ (if g.company.flags.contains "perpetualLoss3" then ["ITA First Schedule para 5 (3): the year of income is taken as the calendar year 2025 (181 days before the change, 184 after); another accounting year splits differently"] else [])

#guard R4.corpTax cit (amtOf {}) { profit := 1000000 } == 300000
-- 1 000 000 turnover after three loss years: 0.5 % × 181/365 = 2 479.45, 1 % × 184/365 = 5 041.10; together 7 520.5 -> 7 520
-- (the whole year at 0.5 % would be 5 000, at 1 % 10 000)
#guard amt2025 1000000 == 7520
#guard (let co : Company := { profit := -5, turnover := 1000000, flags := ["perpetualLoss3"] }; R4.corpTax cit (amtOf co) co) == 7520
-- 365 000 000: 1 825 000 × 181/365 = 905 000 and 3 650 000 × 184/365 = 1 840 000, exactly
#guard amt2025 365000000 == 905000 + 1840000
-- a profitable company with the flag: the larger of 30 % and the minimum
#guard (let co : Company := { profit := 100000, turnover := 10000000, flags := ["perpetualLoss3"] }; R4.corpTax cit (amtOf co) co) == 75205
#guard wht.amount { kind := .dividend, amount := 1000000 } == 100000
#guard wht.amount { kind := .services, amount := 1000000 } == 150000

end TzGlobal
