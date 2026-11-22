import KrGlobal.Pit

/-!
# Korea 2025: employer social insurance and the employee-based resident tax (2200, 3000)
Employer shares (B, official 2025 tables): 국민연금 4.5 % (국민연금법 art. 88; monthly income cap 6,170,000 for July 2024 - June 2025 and 6,370,000 for July 2025 - June
2026: session 12, see below); 건강보험 3.545 % (국민건강보험법 art. 73, 시행령 art. 44: 7.09 %); 장기요양 12.95 % of the health premium (0.4591 %);
고용보험 0.9 % + 고용안정 0.25 % (< 150 employees). 지방세법 art. 84-3 (1) (A): 주민세 종업원분 "종업원 급여총액의 1천분의 5",
art. 84-4: not levied when the monthly average payroll ≤ 50 × the decree amount (360만: 1.8억 a month).

Session 12 (registry sample): the pension cap had been applied as 6,170,000 a month all year (74.04 m), labelled "from
2025-07". The cap changes every July: 6,170,000 for July 2024 - June 2025 and 6,370,000 for July 2025 - June 2026 (PwC
Worldwide Tax Summaries, Korea individual other taxes, Internet Archive 2025-04-25 (reviewed 23 Dec 2024) and 2025-12-16
(reviewed 28 Jul 2025): secondary, B; the 보건복지부 고시 was not reached). The year's wages are spread evenly: half against
6 x 6,170,000 = 37,020,000, half against 6 x 6,370,000 = 38,220,000 (`npF`). Health 7.09 % and long-term care (8.008 % with
it, employer 4.004 %) confirmed by the same source.
-/

namespace KrGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "건강보험 (employer 3.545 %)" a.wages pos (fun b => divR .down (3545 * b) 100000) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "국민건강보험법 art. 73; 시행령 art. 44 (7.09 %)"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "장기요양보험 (employer 0.4591 %)" a.wages pos (fun b => divR .down (4591 * b) 1000000) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "노인장기요양보험법 art. 9 (12.95 % of the health premium)"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "고용보험 (employer 1.15 %)" a.wages pos (fun b => divR .down (115 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "고용보험료징수법 art. 14 (0.9 % + 0.25 %)")) }

/-- 지방세법 art. 84-3 (1), 84-4: 0.5 % of the payroll when the monthly average exceeds 1.8억 (threshold, not allowance). -/
def jumin (bill : Int) : Int := if bill ≤ 12 * 180000000 then 0 else divR .down (50 * bill) BP
def juminF : Family :=
  { name := "3000 주민세 종업원분", covers := [.payroll],
    run := fun _ g _ => if g.entity != .company then [] else
      [charge .payroll "주민세 종업원분 (0.5 %)" g.company.payroll id jumin (level := .local) (statute := "지방세법 arts. 84-3 (1), 84-4")] }
/-- 국민연금 employer 4.5 %: wages spread evenly over 2025; monthly cap 6,170,000 to June, 6,370,000 from July 2025. -/
def npBase (w : Int) : Int := min (pos w / 2) 37020000 + min (pos w - pos w / 2) 38220000
def npF : Family :=
  { name := "2200 국민연금 (employer)", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "국민연금 (employer 4.5 %; cap 6.17 m a month to June, 6.37 m from July 2025)" a.wages npBase (fun b => divR .down (450 * b) BP)
          (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "국민연금법 art. 88 (9 %, half); 기준소득월액 상한 6,170,000 (2024-07 to 2025-06), 6,370,000 (2025-07 to 2026-06)") }

def families : List Family := [fam0, npF, juminF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => a.wages > 0) then ["산재보험 (by industry) and the lower pension income floor not modelled"] else [])

#guard jumin 2000000000 == 0
#guard jumin 3000000000 == 15000000
#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 50000000 }] } } []).map (·.due) == [1772500, 229550, 575000]
#guard (npF.run [] { id := "t", household := { id := "t", adults := [{ wages := 50000000 }] } } []).map (·.due) == [2250000]
#guard (npF.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000000 }] } } []).map (·.due) == [3385800]
#guard npBase 80000000 == 75240000

end KrGlobal.Social
