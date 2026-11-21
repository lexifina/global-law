import StTax.Basic

namespace StTax
open TaxKernel

theorem bands2016_mono : Monotone' bands2016.ticks := Schedule.ticks_mono_of_progressive _ bands2016_progressive
theorem bands2016_convex : Convex bands2016.ticks := Schedule.ticks_convex _ bands2016_progressive
/-- The 2016 table (in force for 2025 on the OGE 2025 bill) equals its marginal bands at every band edge. -/
theorem table2016_edges : subAgrees rows2016 bands2016 [11700, 50000, 100000, 150000, 240000] = true := by decide
/-- The OGE 2024 band: one dobra into it raises the tax by 122 more than the 25 % rate. -/
theorem band2024_jump : irsOn rows2024 420000 = 80952 := by decide

end StTax
