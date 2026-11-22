import AuTax.Household
import AuTax.Schedule1

/-!
# Official worked examples (every value cited; snapshot dates in `refs/SOURCES.md`)
-/

namespace AuTax

/-! ATO, "Tax rates - Australian residents", 2024-25 table: "$45,001 - $135,000: $4,288 plus 30c for each $1
over $45,000"; "$135,001 - $190,000: $31,288 plus 37c"; "$190,001 and over: $51,638 plus 45c". -/
#guard basicTaxC p2025 (aud 45000) = aud 4288
#guard basicTaxC p2025 (aud 135000) = aud 31288
#guard basicTaxC p2025 (aud 190000) = aud 51638

/-! ATO, "Medicare levy reduction for low-income earners": "Angie's taxable income is $29,000 ... her Medicare
levy will be reduced to $177.80". Thresholds table 2024-25: $27,222 / $34,027. -/
#guard levyS7C p2025 (aud 29000) = 17780

/-! ATO, "Study and training loan repayment thresholds and rates", examples 1-3 (2025-26) and 4 (2024-25). -/
#guard helpRepaymentC p2026 (aud 73810) = 102150        -- Christina: $1,021.50
#guard helpRepaymentC p2026 (aud 127064) = 905088       -- Neil: $9,050.88
#guard helpRepaymentC p2026 (aud 238537) = 2385370      -- Priya: ATO prints "$23,854" (rounded to the dollar)
#guard helpRepaymentC p2025 (aud 99736) = 548548        -- Branson: ATO prints "$5,485.52"; 5.5 % x 99,736 = 5,485.48

/-! PAYG Schedule 1 (F2024L00664), Medicare levy adjustment examples and general example 1. -/
#guard wla2 535 0 true = 4          -- Example 1: x = 535.99, WLA = 3.5990 -> $4.00
#guard wla2 1200 4 true = 19        -- Example 3: four children, WLA = 19.2168 -> $19.00
#guard wla2 943 1 true = 17         -- fortnightly example: weekly equivalent 943.99, one child -> $17.00
#guard wla2 646 0 true = 13         -- monthly example: 646.99, spouse, no children -> $13.00
#guard withhold scale2 1333 = 250 ∧ wla2 1333 5 true = 16   -- general example 1: $250.00 - $16.00 = $234.00
#guard withhold scale5 649 = 46     -- general example 2: (0.1600 x 649.99) - 57.8462 = 46.1522 -> $46.00

/-! DSS Family Assistance Guide 3.6.1 / 3.6.3 and OECD TW 2026 Australia chapter: "maximum payment ... AUD 3 883.60
(including a one-off supplement of AUD 448.95)" (FTB B, youngest 5-15), "AUD 5 372.80" (youngest under 5). -/
#guard p2025.ftbB5plusC + p2025.ftbBSuppC = 388360
#guard p2025.ftbBUnder5C + p2025.ftbBSuppC = 537280

end AuTax
