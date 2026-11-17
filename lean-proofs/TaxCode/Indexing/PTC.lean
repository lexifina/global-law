/-
  §36B applicable percentage table: 2025 (Rev. Proc. 2024-35) and 2026 (Rev. Proc. 2025-25).

  Percentages are held in hundredths of a percent (9.96% = 996).

  2025: §36B(b)(3)(A)(iii) (ARPA §9661, extended by IRA §12001 through 2025) replaces the table and switches off
  indexing (clause (ii)). The published 2025 table must therefore equal the statutory (iii) table.
  2026: the (iii) table has expired; the clause (i) table (2.0/3.0/4.0/6.3/8.05/9.5) is indexed under clause (ii)(I)
  by the excess of premium growth over income growth. Rev. Proc. 2025-25 states that the factor was computed from
  "the NHEA Projections, 2024-2033" with HHS's 2026 premium measure, but gives no numbers, so the table can only be
  checked for internal consistency (one common factor) and against the growth figures HHS itself published for the
  same period (HHS final rule, 90 FR 27074, 25 June 2025, Table: $4,714 / $7,885 premiums, $44,559 / $74,083 per
  capita personal income, NHEA Projections 2023–2032: factor 1.0060718427). For 2025, CMS's 2025 PAPI guidance
  (15 Nov 2023, NHEA Projections 2022–2031) gives factor 0.9101817337 (HHS required contribution percentage 7.28%).
-/
import TaxCode.Indexing.Formula
namespace TaxCode.Indexing.PTC
open TaxCode.Indexing

/-- statutory clause (iii) table for 2021–2025: (initial, final) per tier, hundredths of a percent -/
def tableIII : List (Nat × Nat) := [(0, 0), (0, 200), (200, 400), (400, 600), (600, 850), (850, 850)]
/-- Rev. Proc. 2024-35 §2.01 (2025) -/
def pub2025 : List (Nat × Nat) := [(0, 0), (0, 200), (200, 400), (400, 600), (600, 850), (850, 850)]

theorem table_2025_is_statutory : pub2025 = tableIII := by decide

/-- clause (i) base table, hundredths of a percent -/
def tableI : List (Nat × Nat) := [(200, 200), (300, 400), (400, 630), (630, 805), (805, 950), (950, 950)]
/-- Rev. Proc. 2025-25 §3.01 (2026) -/
def pub2026 : List (Nat × Nat) := [(210, 210), (314, 419), (419, 660), (660, 844), (844, 996), (996, 996)]

/-- index the base table by factor num/den, rounding to the nearest hundredth of a percent -/
def indexTable (num den : Nat) : List (Nat × Nat) :=
  tableI.map (fun p => (roundNear (p.1 * num) den 1, roundNear (p.2 * num) den 1))

/-- One factor reproduces all twelve published 2026 cells: any factor from 1.0479 to 1.0483 does. -/
theorem table_2026_consistent : indexTable 10479 10000 = pub2026 ∧ indexTable 10483 10000 = pub2026 := by decide

/-- ... and the factor lies strictly inside (1.0478, 1.0484): just outside, cells change. -/
theorem table_2026_factor_bounds : indexTable 10478 10000 ≠ pub2026 ∧ indexTable 10484 10000 ≠ pub2026 := by decide

/-- HHS's own published excess-of-premium-over-income-growth for 2013→2025 (1.0060718427) would give a top
    percentage of 9.56%, not 9.96%. -/
theorem table_2026_with_hhs_factor :
    indexTable 10060718427 10000000000 = [(201, 201), (302, 402), (402, 634), (634, 810), (810, 956), (956, 956)] := by decide

/-- Required contribution percentage (§36B(c)(2)(C)(i)(II), (iv)): 9.5% indexed the same way.
    Published: 9.02% (2025), 9.96% (2026). HHS's factors give 8.65% and 9.56%. -/
theorem rcp_hhs_factors :
    roundNear (950 * 9101817337) 10000000000 1 = 865 ∧ roundNear (950 * 10060718427) 10000000000 1 = 956 := by decide

/-- The published 9.02% for 2025 needs a factor between 0.9490 and 0.9499. -/
theorem rcp_2025_factor : roundNear (950 * 9490) 10000 1 = 902 ∧ roundNear (950 * 9499) 10000 1 = 902 ∧
    roundNear (950 * 9489) 10000 1 ≠ 902 ∧ roundNear (950 * 9500) 10000 1 ≠ 902 := by decide

end TaxCode.Indexing.PTC
