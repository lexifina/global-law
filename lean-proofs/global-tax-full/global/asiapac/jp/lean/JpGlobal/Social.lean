import JpGlobal.Pit

/-!
# Japan 2025: employer social insurance and the office tax (2200, 3000)
Rates from the official tables (B: the acts' rate articles not re-read this session): 厚生年金保険法 art. 81 (4) 18.3 %
(employer half 9.15 %, standard monthly remuneration capped at 650,000: 7.8 m a year); 健康保険法 art. 160 協会けんぽ Tokyo
9.91 % (half 4.955 %, monthly cap 1.39 m); 雇用保険 (徴収法 art. 12, FY2025 general 1.45 %, employer 0.9 %); 子ども・子育て
拠出金 0.36 % (employer only, 厚生年金 base). 事業所税 従業者割 (地方税法 art. 701-42, 0.25 % of payroll, designated cities,
more than 100 employees).

Session 12 (registry sample, year in force): the FY2025 rates had been applied to the whole calendar year. 協会けんぽ Tokyo
was 9.98 % (half 4.99 %) from March 2024 to February 2025 and 9.91 % (4.955 %) from March 2025; 雇用保険 一般の事業 was
15.5/1000 in FY2024 (employer 9.5/1000) and 14.5/1000 from April 2025 (employer 9/1000; the employee share 6 -> 5.5/1000).
Source: PwC Worldwide Tax Summaries, Japan individual other taxes, Internet Archive 2025-01-13 (reviewed 9 Jul 2024: 4.99 %,
0.60 %) and 2025-12-16 (reviewed 2 Jul 2025: 4.955 % from March 2025, 0.55 % from April 2025) - secondary, B; the employer
share follows from the totals (two-business 3.5/1000 on the employer). Wages spread evenly over the year: health 2/12 at
4.99 % + 10/12 at 4.955 %; employment insurance 3/12 at 0.95 % + 9/12 at 0.9 %.
-/

namespace JpGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "厚生年金保険料 (employer, 9.15 %)" a.wages (fun w => min (pos w) 7800000) (fun b => divR .down (915 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "厚生年金保険法 art. 81 (4) (18.3 %, half)"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "健康保険料 (協会けんぽ Tokyo, employer 4.99 % Jan-Feb, 4.955 % from Mar 2025)" a.wages (fun w => min (pos w) 16680000) (fun b => divR .down (59530 * b) 1200000) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "健康保険法 art. 160; 協会けんぽ 東京 9.98 % (to Feb 2025), 9.91 % (from Mar 2025), by months"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "雇用保険料 (employer 0.95 % Jan-Mar, 0.9 % from Apr 2025)" a.wages pos (fun b => divR .down (1095 * b) 120000) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "労働保険徴収法 art. 12 (一般の事業: FY2024 15.5/1000, employer 9.5; FY2025 14.5/1000, employer 9), by months"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "子ども・子育て拠出金 (0.36 %)" a.wages (fun w => min (pos w) 7800000) (fun b => divR .down (36 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "子ども・子育て支援法 art. 70 (0.36 %)")) }

/-- 事業所税 従業者割: 0.25 % of the payroll of employers with more than 100 employees in designated cities. -/
def jigyoshoF : Family :=
  { name := "3000 事業所税 従業者割", covers := [.payroll],
    run := fun _ g _ => if g.entity != .company || g.company.employees ≤ 100 then [] else
      [charge .payroll "事業所税 従業者割 (0.25 %)" g.company.payroll id (fun b => divR .down (25 * b) BP) (level := .local) (statute := "地方税法 art. 701-42 (designated cities)")] }

def families : List Family := [fam0, jigyoshoF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => a.age ≥ 40 && a.age < 65 && a.wages > 0) then ["介護保険料 (40-64, 1.59 %) not modelled"] else [])
  ++ (if g.household.adults.any (fun a => a.wages > 0) then ["労災保険 (by industry) and bonus caps not modelled; 協会けんぽ rate taken for Tokyo"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 6000000 }] } } []).map (·.due) == [549000, 297650, 54750, 21600]

end JpGlobal.Social
