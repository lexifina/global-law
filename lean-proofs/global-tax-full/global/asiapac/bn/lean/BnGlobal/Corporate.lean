import BnGlobal.Pit

/-!
# Brunei 2025: income tax on companies and withholding on non-residents (1200)

Source: Laws of Brunei Chapter 35, Income Tax, revised edition B.L.R.O. 1/2024 (`cmp20/world/B15-no-pit/bn/law/ita_cap35_2024.txt`;
sha256 in `law/SOURCES.tsv`).
* **s. 35 (1) (f)**: "the year of assessment 2015 and subsequent years of assessment upon the chargeable income of every company,
  tax at the rate of 18.5 per cent".
* **s. 35 (2)**: "tax at the rate of 2.5 per cent … on the gross amount of any income referred to in section 9(4)" (interest,
  commission and fees on loans) of a non-resident; **(2A)**: payments of s. 9 (5) (a), (b), (ba), (d) (royalties, technical
  knowledge and services, rent of movable property) and (c) (management) "at the rate of 10 per cent".
Dividends are not taxed (no dividend withholding).
-/

namespace BnGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat 1850 }

def citStatute : String := "Income Tax Act (Cap. 35) s. 35 (1) (f) (18.5 % from the year of assessment 2015)"

def wht : Wht :=
  { name := "Withholding tax on non-residents", rules := [
      { kind := .interest, rateBp := 250, statute := "Cap. 35 s. 35 (2), s. 9 (4) (2.5 % of the gross interest)" },
      { kind := .royalty, rateBp := 1000, statute := "Cap. 35 s. 35 (2A) (a), s. 9 (5) (a) (10 %)" },
      { kind := .services, rateBp := 1000, statute := "Cap. 35 s. 35 (2A), s. 9 (5) (ba), (c) (technical and management services 10 %)" },
      { kind := .rent, rateBp := 1000, statute := "Cap. 35 s. 35 (2A) (a), s. 9 (5) (d) (rent of movable property 10 %)" },
      { kind := .dividend, rateBp := 0, statute := "Cap. 35 s. 35 (2), (2A): the non-resident tax covers s. 9 (4) interest and s. 9 (5) payments only; dividends are not charged (s. 36 is the company's own deduction at its rate, not a tax on the shareholder)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.lossesForward ≠ 0 then ["loss carry-forward period (s. 32) not checked; losses offset in full"] else [])
  ++ (if true then ["petroleum income (Income Tax (Petroleum) Act) not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 185000
#guard wht.amount { kind := .interest, amount := 1000 } == 25
#guard wht.amount { kind := .royalty, amount := 1000 } == 100
#guard wht.amount { kind := .dividend, amount := 1000 } == 0

end BnGlobal.Corporate
