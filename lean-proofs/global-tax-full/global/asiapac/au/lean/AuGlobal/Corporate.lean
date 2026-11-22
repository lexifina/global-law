import AuGlobal.Pit

/-!
# Australia 2024-25: company tax and withholding on non-residents (1200)

Income Tax Rates Act 1986 and the Income Tax (Dividends, Interest and Royalties Withholding Tax) Act 1974: rates as read by the
registry from legislation.gov.au (B: compilations not fetched in this package).
* **ITRA s. 23 (2)**: 30 %; **s. 23AA**: base rate entities (aggregated turnover < $50 m) 25 % (flag `baseRate`).
* **DIRWT Act s. 7**: unfranked dividends 30 %, interest 10 %, royalties 30 %.

FT review (2026-11-21): **Income Tax Rates Act 1986, Compilation No. 65 (28 March 2025, in force on 2025-07-01)**,
legislation.gov.au C2004A03348 epub (`au/law/fedleg/itra_20250701.html`, sha256 in `SHA256SUMS`):
* **s. 23 (2)**: "The rate of tax in respect of the taxable income of a company is: (a) if the company is a base rate
  entity for a year of income—25%; or (b) otherwise—30%".
* **s. 23AA**: "An entity is a base rate entity for a year of income if: (a) no more than 80% of its assessable income
  for the year of income is base rate entity passive income; and (b) its aggregated turnover ... is less than
  $50 million."
* **s. 23AB (1)**: passive income includes "(a) a distribution ... by a corporate tax entity ..., other than a
  non-portfolio dividend", "(d) interest ..., royalties and rent", "(f) a net capital gain".
The test is applied to the entity's own fields: turnover for aggregated turnover (no connected entities), assessable
income = turnover + dividends received, passive income = dividends received from stakes under 10 % (portfolio; ITAA
1936 s. 317: non-portfolio = at least 10 %). Flags `baseRate` / `notBaseRate` override the test.
-/

namespace AuGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- ITRA 1986 s. 23AA (b): aggregated turnover less than $50 million. -/
def breTurnover : Int := 50000000
/-- s. 23AB (1) (a): portfolio dividends (stake under 10 %, ITAA 1936 s. 317) are passive; the entity carries no other
passive income (interest, rent, royalties, gains received). -/
def passiveIncome (co : Company) : Int := if co.participationBp < 1000 then pos co.dividendsReceived else 0
/-- s. 23AA: a base rate entity (flags `baseRate` / `notBaseRate` override the test on the entity's fields). -/
def baseRateEntity (co : Company) : Bool :=
  if co.flags.contains "baseRate" then true else if co.flags.contains "notBaseRate" then false else
  decide (co.turnover < breTurnover) && decide (passiveIncome co * 100 ≤ 80 * (pos co.turnover + pos co.dividendsReceived))
/-- s. 23 (2): 25 % for a base rate entity, otherwise 30 %. -/
def rateOf (co : Company) : Int := if baseRateEntity co then 2500 else 3000

def cit (co : Company) : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "ITRA 1986 s. 23 (2), ss. 23AA-23AB (Compilation No. 65, in force 2025-07-01)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 3000, statute := "Income Tax (Dividends, Interest and Royalties Withholding Tax) Act 1974 s. 7 (a): 30 % on income to which ITAA 1936 s. 128B (4) applies (dividends; franked parts exempt, s. 128B (3) (ga))" },
      { kind := .interest, rateBp := 1000, statute := "DIRWT Act 1974 s. 7 (b): 10 % on income to which ITAA 1936 s. 128B (5) applies (interest)" },
      { kind := .royalty, rateBp := 3000, statute := "DIRWT Act 1974 s. 7 (c): 30 % on income to which ITAA 1936 s. 128B (5A) applies (royalties)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [(cit g.company).citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["franking credits, the global and domestic minimum tax and thin capitalisation not modelled"] else [])
  ++ (if true then ["base rate entity test on the entity's own turnover and portfolio dividends (no connected entities; interest, rent, royalties and gains received not in the entity)"] else [])

#guard (cit { turnover := 60000000, profit := 1000000 }).citTax { turnover := 60000000, profit := 1000000 } == 300000
#guard wht.amount { kind := .dividend, amount := 1000 } == 300
#guard wht.amount { kind := .interest, amount := 1000 } == 100
#guard wht.amount { kind := .royalty, amount := 1000 } == 300
-- s. 23 (2) (a), s. 23AA (b): the $50 million edge
#guard (cit { turnover := 49999999, profit := 1000000 }).citTax { turnover := 49999999, profit := 1000000 } == 250000
#guard (cit { turnover := 50000000, profit := 1000000 }).citTax { turnover := 50000000, profit := 1000000 } == 300000
-- s. 23AA (a): more than 80 % portfolio dividends is not a base rate entity
#guard (cit { turnover := 100, profit := 1000, dividendsReceived := 1000, participationBp := 500 }).citTax { turnover := 100, profit := 1000, dividendsReceived := 1000, participationBp := 500 } == 300
#guard (cit { turnover := 100, profit := 1000, dividendsReceived := 1000, participationBp := 1000 }).citTax { turnover := 100, profit := 1000, dividendsReceived := 1000, participationBp := 1000 } == 250
#guard (cit { turnover := 1000, profit := 1000, flags := ["notBaseRate"] }).citTax { turnover := 1000, profit := 1000 } == 300

end AuGlobal.Corporate
