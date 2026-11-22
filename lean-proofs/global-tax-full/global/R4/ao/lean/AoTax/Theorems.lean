import AoTax.Basic

namespace AoTax
open TaxKernel

/-- The Anexo I table has twelve rows with increasing lower bounds. -/
theorem table_rows : table.length = 12 := by decide
theorem table_sorted : (table.map (·.lo)) = [0, 100001, 150001, 200001, 300001, 500001, 1000001, 1500001, 2000001, 2500001, 5000001, 10000001] := by decide
/-- Statute notches in the Lei 18/24 table: one more kwanza of monthly base costs 6,001 / 10,751 Kz. -/
theorem notch_150001 : monthTax 150001 - monthTax 150000 = 6001 := by decide
theorem notch_200001 : monthTax 200001 - monthTax 200000 = 10751 := by decide

end AoTax
