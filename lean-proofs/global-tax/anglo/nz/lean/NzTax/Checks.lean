import NzTax.Basic

/-!
# Official worked examples, checked at build time (`#guard`)

Each value is copied from the Inland Revenue page or document named (files in `refs/`, see `refs/SOURCES.md`).
Examples whose printed figure is wrong are checked against the correct arithmetic and listed in FINDINGS.md.
-/

namespace NzTax
open TaxKernel

/-- Tax (cents) on a whole-dollar income, 2025-26. -/
def tax25 (x : Int) : Int := taxOn sched2025 (nzd x)

-- IRD "Minimum family tax credit" (archived 2025-10-08), Jeremy: "$27,000 − tax payable: $3,633"
#guard tax25 27000 = 363300
-- Casey: "$33,000 − tax payable: $4,683"; Casey over the limit: "$41,800 − tax payable: $6,223"
#guard tax25 33000 = 468300
#guard tax25 41800 = 622300
-- Jeremy: "$35,316 − family income after tax: $24,367 = minimum family tax credit for the full year: $10,949"
-- (family income: salary 27,000 + child support 1,000)
#guard (wff p2025 2 0 0 (nzd 28000) true true (tax25 27000)).mftc = nzd 10949
-- Casey: "$35,316 − Family income after tax: $28,317 = ... $6,999" (the page's headline "$7,111" is wrong: F)
#guard (wff p2025 3 0 0 (nzd 33000) true true (tax25 33000)).mftc = nzd 6999
-- Casey over the limit: after-tax income $35,577 > $35,316: no MFTC
#guard (wff p2025 3 0 0 (nzd 41800) true true (tax25 41800)).mftc = 0

-- IRD "Family tax credit" (archived 2025-10-14), Sarah: 2 children, $37,800: "it totals $13,654"
#guard (wff p2025 2 0 0 (nzd 37800) true false 0).ftc = nzd 13654
-- Rahui: 3 children, $100,000: "$57,300 × 27% = abatement: $15,471 ... $19,784 − $15,471 = $4,313"
#guard (wff p2025 3 0 0 (nzd 100000) true false 0).abatement = nzd 15471
#guard (wff p2025 3 0 0 (nzd 100000) true false 0).ftc = nzd 4313
-- Claire and Laura: 2 children, $100,000: no FTC; IWTC "$5,070 − $1,817 = $3,253" (IRD "In-work tax credit",
-- archived 2025-08-17)
#guard (wff p2025 2 0 0 (nzd 100000) true false 0).ftc = 0
#guard (wff p2025 2 0 0 (nzd 100000) true false 0).iwtc = nzd 3253
-- Jaimee: 5 children, $41,600: "$5,070 ... $780 ... $780 Total $6,630" (the headline "$5,330" is stale: F)
#guard (wff p2025 5 0 0 (nzd 41600) true false 0).iwtc = nzd 6630

-- Special report, Taxation (Budget Measures) Act 2024, p. 14, Elizabeth (2024-25, $45,000): "= $476.90"
#guard ietc2024 (nzd 45000) = 47690
-- Special report p. 12, Alvien (2025-26, $66,000, 11 eligible months): printed "$477.66"; 520 × 11/12 = 476.66…
#guard ietc p2025 (nzd 66000) * 11 / 12 = 47666

-- IRD payroll spec 2025-26 s. 2.1: "Maximum ACC Earner Levy ... $2,551.59" (and 2024-25 "$2,276.52")
#guard accLevy p2025 (nzd 200000) = 255159
#guard accLevy p2024 (nzd 200000) = 227652

-- OECD Taxing Wages 2025, NZL (income year 2025-26): S100 CGITLETC 17,291.59 at 83,073; S167 35,659.03 at
-- 138,731.91 (model on whole dollars: 35,659.06 at 138,732); SP67 CTTC 15,225.09 at 55,658.91;
-- M100_0 CTTC 7,823.29 at 83,073
#guard tax25 83073 = 1729159
-- (the model rounds the abatement down to the cent: 15,225.10; the OECD keeps 15,225.0943)
#guard (wff p2025 2 0 0 5565891 true true (taxOn sched2025 5565891)).ftc
        + (wff p2025 2 0 0 5565891 true true (taxOn sched2025 5565891)).iwtc - 1522509 ≤ 1
#guard (wff p2025 2 0 0 (nzd 83073) true true (tax25 83073)).total = 782329

end NzTax
