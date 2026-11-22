import SvTax.Basic

namespace SvTax
open TaxKernel

/-- **SV-F1.** The table's fixed amounts are not the band sums: entering tramo II costs US$ 212,12 at once, and at
US$ 10.742,86 the printed 720,00 is US$ 93,59 above 212,12 + 10 % of 4.142,86; at 24.457,14 the step is 0,0004 (ticks = cents x bp). -/
theorem art37_jumps :
    cumJumps art37 = [(0, 0), (660000, 212120000), (1074286, 93594000), (2445714, 4000)] := by decide

/-- **SV-F2 (notch).** One cent of base above US$ 6.600 costs US$ 212,12. -/
theorem entry_notch : tax37 660001 - tax37 660000 = 21212 := by decide

/-- **SV-F3 (notch).** A salaried person paid US$ 9.100,01 instead of US$ 9.100 loses the US$ 1.600 deduction:
US$ 160 more tax for one more dollar (no contributions passed; wages in whole dollars: 9.101 vs 9.100). -/
theorem deduction_notch : (person 9101 0).tax - (person 9100 0).tax = 160 := by decide

/-- **SV-F4 (notch).** At the tramo III threshold the printed fixed amount jumps by US$ 93,59. -/
theorem tramo3_notch : tax37 1074287 - tax37 1074286 > 9000 := by decide

end SvTax
