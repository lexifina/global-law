import TaxKernel.World

/-!
# Thailand: personal income tax, tax year 2025 (B.E. 2568)

Access tier A for the income tax (Revenue Code as published by the Revenue Department, rd.go.th, pages saved in
`th/law/`, fetched 2026-11-20; sha256 in `SHA256SUMS`). Provisions used (Thai text quoted):
* s. 42 bis (rd_5937): income under s. 40 (1) and (2) "ยอมให้หักค่าใช้จ่ายเป็นการเหมาได้ร้อยละ 50 แต่รวมกันต้องไม่เกิน
  100,000 บาท" (Revenue Code Amendment Act No. 44, B.E. 2560); each spouse deducts separately.
* s. 47 (1): (ก) taxpayer 60,000; (ข) spouse 60,000; (ค) (1) legitimate child "คนละ 30,000 บาท" and for the second and
  later child "ที่เกิดในหรือหลังปี พ.ศ. 2561 ให้หักลดหย่อนได้เพิ่มอีกคนละ 30,000 บาท" (Act No. 46, B.E. 2561); children
  counted only if minors or under 25 in higher education with income under 30,000; (ฌ) social security contributions
  as paid. s. 47 (2): where both spouses have income, (ก) and (ข) together 120,000 (so the spouse allowance only counts
  for a spouse without income).
* s. 48 (1) + "บัญชีอัตราภาษีเงินได้" (rd_5938, Act No. 44, B.E. 2560): net income to 300,000 5 %; 300,000-500,000 10 %;
  500,000-750,000 15 %; 750,000-1,000,000 20 %; 1,000,000-2,000,000 25 %; 2,000,000-5,000,000 30 %; above 35 %.
* Royal Decree No. 470 (B.E. 2551) s. 4 (rd_37669): net income "เฉพาะส่วนที่ไม่เกินหนึ่งแสนห้าหมื่นบาทแรก" is exempt.
* s. 48 (2): with assessable income of 120,000 or more (not counting s. 40 (1) income) tax is not less than 0.5 % of that
  income. Royal Decree No. 480 (B.E. 2552) s. 3 (law/rd_40923_rd480.html, law/dc480.pdf; read 2026-11-20 by L1-S):
  "ให้ยกเว้นภาษีเงินได้ ... สำหรับภาษีที่ต้องเสียตามมาตรา 48(2) เฉพาะกรณีผู้มีเงินได้มีภาษีที่ต้องเสียทั้งสิ้นจำนวนไม่เกินห้าพันบาท
  ในปีภาษีนั้น" (the s. 48 (2) tax is exempt when it is 5,000 baht or less; the s. 48 (1) tax stays due). So the 0.5 % floor
  applies only when it exceeds 5,000, i.e. above 1,000,000 of such income. s. 48 (3) (ก): bank and bond interest may be taxed separately at 15 % (the taxpayer's election; the cheaper of
  inclusion and 15 % is taken).
Not reached: the ministerial regulations fixing the social security rate and wage base (sso.go.th lists them but its
download links answer 404 to scripts), so employee social security and its s. 47 (1) (ฌ) deduction are `unsupported`.
W5 pattern A (2026-11-20): employee social security (s. 33 insured) added, input `"w5Contrib": false` drops it and
restores the earlier outputs. Ministerial regulations from the SSO's own copies (Wayback captures of 2021-06-21 of
sso.go.th files_storage PDFs; the live download links answer 404), read from the page images; files in `th/law/w5/`:
* กฎกระทรวงกำหนดอัตราเงินสมทบกองทุนประกันสังคม พ.ศ. 2545 (R.G. 119/125 ก, 27 Dec 2002) ข้อ 2 (2), บัญชี ข: insured
  1.5 % (injury, sickness, invalidity, death, maternity) from 1 Jan 2004; ข้อ 3, บัญชี ค: insured 3 % (child allowance,
  old age).
* กฎกระทรวงกำหนดอัตราเงินสมทบ...ในกรณีว่างงาน พ.ศ. 2546 (R.G. 120/129 ก, 31 Dec 2003) ข้อ 1 (3): insured 0.5 %.
  Total 5 % of wages.
* กฎกระทรวง ฉบับที่ 7 (พ.ศ. 2538) (R.G. 112/13 ก, 30 Mar 1995) ข้อ 1: wage base "ไม่ต่ำกว่าเดือนละหนึ่งพันหกร้อย
  ห้าสิบบาท และไม่เกินเดือนละหนึ่งหมื่นห้าพันบาท" (1,650 to 15,000 a month); in force through 2025 (repealed from
  1 Jan 2026 by the กฎกระทรวง of 2568, base 1,650-17,500, listed on sso.go.th).
* Act s. 46 (last paragraph, as amended 1999): fractions of 50 satang or more count as one baht; s. 33: employees aged
  15 to 60, and older employees already insured stay insured (applied to every wage earner aged 15 or more).
* Revenue Code s. 47 (1) (ฌ) (rd_5937): contributions deducted "ตามจำนวนที่จ่ายจริง".
Monthly wage = annual wages / 12; a positive wage below 1,650 a month is assessed on 1,650 (literal). The 2012 rate
regulation (พ.ศ. 2555, archived copy truncated) was not read; the 5 % total of the 2002-2003 regulations is taken as the
rate in force (no 2025 reduction regulation is listed by the SSO).
Unit: spouses file separately (s. 57 ter, joint filing of the wife's income, is marked repealed from tax year 2555);
children's allowance claimed by the higher earner (reading; s. 57 quinquies (2) "คนละกึ่งหนึ่ง" is marked repealed).
-/

namespace ThTax
open TaxKernel

/-- s. 48 (1) schedule with the first 150,000 exempt (Royal Decree 470). -/
def sched : Schedule := Schedule.ofList [(0, 0), (150000, 500), (300000, 1000), (500000, 1500), (750000, 2000),
  (1000000, 2500), (2000000, 3000), (5000000, 3500)]

/-- s. 48 (2) minimum tax on assessable income other than s. 40 (1) salary (0.5 % from 120,000), exempt by Royal Decree
No. 480 s. 3 when it is not more than 5,000 baht: due only when 0.5 % of that income exceeds 5,000 (income above 1,000,000). -/
def minTax (nonEmp : Int) : Int :=
  if nonEmp ≥ 120000 ∧ 50 * nonEmp > 5000 * BP then divR .down (50 * nonEmp) BP else 0

def expenseDeduction (e : Int) : Int := min (divR .down (5000 * pos e) BP) 100000
def personal : Int := 60000
def spouseAllowance : Int := 60000
def childAllowance : Int := 30000

/-- s. 47 (1) (ค): 30,000 a child, 30,000 more for the second and later child born in or after 2018 (age 7 or less in
2025); children under 20 counted (minors). Children ordered oldest first. -/
def childrenAllowance (ages : List Nat) : Int :=
  let eligible := (ages.mergeSort (fun a b => a ≥ b)).filter (· < 20)
  sumInts ((List.range eligible.length).zip eligible |>.map fun (i, a) =>
    childAllowance + (if i ≥ 1 ∧ a ≤ 7 then childAllowance else 0))

def progressive (net : Int) : Int := sched.tax Rule.unitDown (pos net)

/-- W5 pattern A: employee social security, 5 % of the monthly wage within 1,650-15,000 (กฎกระทรวง 2545, 2546;
ฉบับที่ 7 (2538)), rounded to the baht (s. 46: 50 satang and more up), twelve months. -/
def ssMonthly (m : Int) : Int := divR .halfUp (500 * max 1650 (min m 15000)) BP
def socialSecurity (a : Adult) : Int :=
  if a.wages ≤ 0 ∨ a.age < 15 then 0 else 12 * ssMonthly (a.wages / 12)

#guard ssMonthly 15000 = 750 ∧ ssMonthly 100000 = 750 ∧ ssMonthly 1000 = 83 ∧ ssMonthly 10010 = 501

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let w5 := (c.bool? "w5Contrib").getD true
  let ssOf (a : Adult) : Int := if w5 then socialSecurity a else 0
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let idx := List.range c.adults.length
  let assess (a : Adult) : Int := pos a.wages + pos a.selfEmployment
  let top : Nat := match c.adults with
    | [a0, a1] => if assess a1 > assess a0 then 1 else 0
    | _ => 0
  let hasIncome (a : Adult) : Bool := assess a > 0
  let person (a : Adult) (i : Nat) : Int × Int :=
    let others := (c.adults.zip idx).filter (fun (_, j) => j ≠ i)
    let sp := if c.isCouple ∧ others.all (fun (b, _) => !hasIncome b) then spouseAllowance else 0
    let ch := if i = top then childrenAllowance (c.children.map (·.age)) else 0
    let base := pos a.wages - expenseDeduction a.wages + pos a.selfEmployment
    let net := base - personal - sp - ch - ssOf a
    let intr := share c.interest i
    let incl := progressive (net + intr)
    let sep := progressive net + divR .down (1500 * pos intr) BP
    let t := min incl sep
    let nonEmp := pos a.selfEmployment + pos intr
    let floor := minTax nonEmp
    (max t floor, pos net)
  let rs := (c.adults.zip idx).map fun (a, i) => person a i
  Out.make c "TH" "THB" (sumInts (rs.map (·.1))) (employeeSocial := sumInts (c.adults.map ssOf))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.2))),
      Out.dStr "note" "interest: cheaper of inclusion and the 15 % separate tax (s. 48 (3)); self-employment taken as net of the s. 40 (8) deduction"])
    (unsupported := (if c.adults.any (fun a => a.wages > 0) ∧ !w5 then ["employee social security contributions and their s. 47 (1) (ฌ) deduction: ministerial regulations on rate and wage base not reached"] else []) ++
      (if c.dividends ≠ 0 then ["dividends: 10 % final withholding or inclusion with the s. 47 bis credit not modelled"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rent (s. 40 (5)): expense deduction by royal decree not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: depend on the asset (listed shares exempt; property s. 48 (4)); not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: treatment depends on the payer (s. 40 (1), s. 42 exemptions); not modelled"] else []) ++
      (if c.adults.any (fun a => a.selfEmployment > 0) then ["s. 48 (2) minimum tax: assessable (gross) non-salary income is taken as the self-employment input, which the model also treats as net of expenses"] else []))

def country : Country := { code := "TH", name := "Thailand", currency := "THB", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- The exemption of the first 150,000: no tax at 150,000 of net income, 5 % of the excess to 300,000. -/
#guard progressive 150000 = 0 ∧ progressive 300000 = 7500 ∧ progressive 500000 = 27500
/- RD 480 s. 3: no s. 48 (2) tax at 120,000 or at 1,000,000 (600 and 5,000 are "ไม่เกินห้าพันบาท"); due from 1,000,001. -/
#guard minTax 119999 = 0 ∧ minTax 120000 = 0 ∧ minTax 1000000 = 0 ∧ minTax 1000001 = 5000 ∧ minTax 2000000 = 10000
/- s. 42 bis cap reached at 200,000 of salary. -/
#guard expenseDeduction 200000 = 100000 ∧ expenseDeduction 300000 = 100000

end ThTax
