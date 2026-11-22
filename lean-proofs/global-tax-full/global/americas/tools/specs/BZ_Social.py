S = dict(cc="BZ", fam="Social",
doc=r'''# Belize 2025: employer Social Security contributions (2200)

Source: Social Security (Collection of Contributions) Regulations (Cap. 44, subsidiary), reg. 6 (1) and the Schedule,
Table 2 "RATES OF WEEKLY CONTRIBUTIONS PAYABLE BY EMPLOYED PERSON AND EMPLOYER FOR THE PERIOD JANUARY 6, 2020 UNTIL THE
DECLARATION OF THE PERIOD OF TABLE 3" (S.I. 184 of 2020), the 1.x builder's copy of the record as in force on 2025-06-30
(`world/B13-caribbean/bz/law/gl_ss_collection_sched.txt`). The 1.x model charges the employed person's column of the same
Table 2 (no notice declaring the Table 3 period was found for 2020-2026). Reg. 6 (1): the contribution "payable by the
employer, shall be the amounts set out in columns 2, 3, and 4 of the respective tables ... which corresponds to the
actual weekly earnings". Grade B (a third-party consolidation of the official Schedule).
Employer's weekly contribution by actual weekly earnings (lower bound of the band): under $70 $4.02; $70 $6.58; $110
$9.51; $140 $10.86; $180 $12.66; $220 $14.46; $260 $16.26; $300 $18.06; $340 $19.81; $380 $21.46; $420 $23.00; $460 and
over $24.42. Wages are read as paid evenly over 52 weeks.''',
lean=r'''/-- Table 2: (lower bound of actual weekly earnings in cents, employer's weekly contribution in cents). -/
def empTable2 : List (Int × Int) :=
  [(0, 402), (7000, 658), (11000, 951), (14000, 1086), (18000, 1266), (22000, 1446), (26000, 1626), (30000, 1806),
   (34000, 1981), (38000, 2146), (42000, 2300), (46000, 2442)]

def empWeek (wc : Int) : Int := if wc ≤ 0 then 0 else empTable2.foldl (fun acc r => if wc ≥ r.1 then r.2 else acc) 0

/-- Annual employer contribution (dollars) on an annual wage paid evenly over 52 weeks. -/
def empAnnual (w : Int) : Int := divR .down (52 * empWeek (divR .down (pos w * 100) 52)) 100

def ssStatute : String := "Social Security (Collection of Contributions) Regulations reg. 6 (1), Schedule Table 2 (S.I. 184 of 2020), employer column"

def sscF : Family :=
  { name := "2200 Social Security employer (Table 2)", covers := [.sscEmployer],
    run := fun _ g _ =>
      if g.entity == .company then
        [charge .sscEmployer "Social Security (employer)" g.company.payroll id (fun _ => payrollAmount empAnnual g.company)
          (event := "payroll") (level := .social) (bearer := .entity) (statute := ssStatute)]
      else
        (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
          charge .sscEmployer "Social Security (employer)" a.wages id empAnnual (event := s!"adult {i + 1}")
            (level := .social) (bearer := .employer) (statute := ssStatute) }''',
families="[sscF]",
unsupported=[["g.household.adults.any (·.wages > 0) || g.entity == .company", "employer Social Security by the Table 2 weekly bands; wages read as paid evenly over 52 weeks; the Table 3 period (if declared) not applied"]],
guards=["empAnnual 52000 == 1269", "empAnnual 5200 == 342", "empAnnual 0 == 0"],
taxes=[dict(oecd="2200", tax="Social Security (employer)", statute="Social Security (Collection of Contributions) Regulations reg. 6 (1), Schedule Table 2 (S.I. 184 of 2020)", dated="Schedule as in force on 2025-06-30 (Table 2 from 6 January 2020 until a Table 3 notice)", grade="B", package="P4", kernel_parts=["Family", "charge"], unsupported=["weekly pay pattern"])])
