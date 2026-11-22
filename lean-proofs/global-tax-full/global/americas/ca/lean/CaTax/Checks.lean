import CaTax.Household

/-!
# Checks against published figures (`#guard`, evaluated at build time)

OECD Taxing Wages 2026, country table for Canada, year 2025 (DSD_TAX_WAGES_COU@DF_TW_COU 2.1, fetched 2026-11-19,
`cmp20/anglo/data/oecd/tw_cou_anglo.csv`), single person at 100 % of the average wage (GEBT 92,400.83): CGTC
91,326.83; CGITLETC 15,279.50; CGITFP 12,084.63; SLT 5,320.46; EECSSC 6,257.58 (CPP 4,430.10 + EI 1,077.48 +
Ontario Health Premium 750); and the one-earner couple with two children (M100_0): CGITFP 9,745.93, SLT 4,773.90.
-/

namespace CaTax

def aw : Person :=
  { age := 40, wages := 9240083, se := 0, pension := 0, interest := 0, dividends := 0, capitalGains := 0,
    rent := 0, rrsp := 0 }
def single : Family := { spouseNet := none, eligibleDependant := false, onDependants := 0, familyNet := (income aw).net, gifts := 0 }
def oneEarner : Family := { spouseNet := some 0, eligibleDependant := false, onDependants := 2, familyNet := (income aw).net, gifts := 0 }

#guard (income aw).taxable = 9132683
#guard (fedTax aw (income aw) single).basicTax = 1527950
#guard (fedTax aw (income aw) single).tax = 1208463
#guard (onTax aw (income aw) single).tax = 532046
#guard (income aw).social.total + (onTax aw (income aw) single).ohp = 625758
#guard (fedTax aw (income aw) oneEarner).tax = 974593
#guard (onTax aw (income aw) oneEarner).tax = 477390

-- CRA T4127 (120th ed.) ch. 7 example: "$30,000 × 1.64% = $492.00".
#guard (social 40 (dol 30000) 0).ei = dol 492

-- T4127 Table 8.3-8.6 maxima: base 3,356.10 + first additional 678.00 (employee), CPP2 396.00.
#guard (social 40 (dol 200000) 0).base = 335610
#guard (social 40 (dol 200000) 0).enhanced = 67800 + 39600
#guard (social 40 (dol 200000) 0).ei = 107748

end CaTax
