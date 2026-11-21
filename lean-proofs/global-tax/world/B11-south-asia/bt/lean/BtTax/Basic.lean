import TaxKernel.World

/-!
# Bhutan: personal income tax, income year 2025 (calendar year)

Access tier A. Income year 2025 is governed by the Income Tax Act of the Kingdom of Bhutan 2001: the Income Tax Act
of Bhutan 2025 (DRC, `bt/law/Income-Tax-Act-of-Bhutan-2025.pdf`, sha256 d264ef94...) s. 2 "comes into force ... 1st
January 2026" and s. 4 "all provisions of the Income Tax Act of the Kingdom of Bhutan 2001 ... shall continue to apply in
full force and effect until the date on which this Act comes into force". Text used: "Income Tax Act of the Kingdom of
Bhutan 2001_Fourth Edition" (Department of Revenue and Customs, drc.gov.bt/acts-policy, `bt/law/...Fourth-Edition.pdf`,
sha256 ef70913c...), which prints the amendments of the Income Tax (Amendment) Act of Bhutan 2020 with footnotes;
Rules on the Income Tax Act, Fifth Edition (DRC, sha256 05364a73...). Global law holds only the 2001 original
(basic exemption Nu 100,000): superseded for this year.
-/

namespace BtTax
open TaxKernel

def roundR : Rule := { mode := .halfUp }

/-- Part III s. 14 as amended by the Income Tax (Amendment) Act 2020 (footnote 16): nil to Nu 300,000; 10 % to 400,000;
"Nu.10,000.00 plus 15%" to 650,000; "Nu. 47,500.00 plus 20%" to 1,000,000; "Nu. 117,500.00 plus 25%" to 1,500,000;
"Nu. 242,499.00 plus 30% of the amount by which the total net taxable income exceeds Nu.1,500,000.00". -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (300000, 1000), (400000, 1500), (650000, 2000), (1000000, 2500), (1500000, 3000)]

/-- The table as printed (rate column with its fixed amounts), the statute's literal tax. -/
def printed (x : Int) : Int :=
  if x ≤ 300000 then 0
  else if x ≤ 400000 then divR .halfUp (1000 * (x - 300000)) BP
  else if x ≤ 650000 then 10000 + divR .halfUp (1500 * (x - 400000)) BP
  else if x ≤ 1000000 then 47500 + divR .halfUp (2000 * (x - 650000)) BP
  else if x ≤ 1500000 then 117500 + divR .halfUp (2500 * (x - 1000000)) BP
  else 242499 + divR .halfUp (3000 * (x - 1500000)) BP

/- The printed fixed amounts against the band sums: 10,000 / 47,500 / 117,500 agree; the last row prints 242,499,
one ngultrum below the band sum 242,500 (English and Dzongkha texts alike), so the literal tax falls at 1,500,000. -/
#guard sched.tax roundR 400000 = 10000 ∧ sched.tax roundR 650000 = 47500 ∧ sched.tax roundR 1000000 = 117500
#guard sched.tax roundR 1500000 = 242500
#guard printed 1500000 = 242500 ∧ printed 1500001 = 242499 ∧ printed 1500003 = 242500

/-- s. 14 A (inserted 2020): "Surcharge at the rate of 10 percent shall be applicable on Personal Income Tax amount if
the annual Personal Income Tax is equal to or more than Nu.1,000,000" (no marginal relief). -/
def surcharge (pit : Int) : Int := if pit ≥ 1000000 then divR .halfUp (1000 * pit) BP else 0

/-- s. 8.3: "Total dividend income from Bhutanese companies not exceeding Nu.30,000 per annum shall be exempt";
read as an exemption of the first Nu 30,000. s. 6.3 (b): "20 per cent of the rental income" for repairs.
s. 5.3: "pension income shall be exempt". s. 12.2-12.3 education Nu 350,000 per child (documents) or Nu 20,000
(without); Rules r. 36 (2)(iv): donations up to "5% of the Total Adjusted Gross Income". -/
def dividendExempt : Int := 30000

/-- The literal-table variant (`--printed`) uses the table as printed; default the band sums. -/
def person (literal : Bool) (wages se div rent pf donation education : Int) : Int × Int × Int :=
  let salary := pos (wages - pf)
  let adj := salary + pos se + pos (div - dividendExempt) + (rent - rent / 5)
  let don := min donation (divR .down (500 * pos adj) BP)
  let ti := pos (adj - don - education)
  let pit := if literal then printed ti else sched.tax roundR ti
  (ti, pit, surcharge pit)


/-! ## Income year 2026: Income Tax Act of Bhutan 2025 (round D4)

Income Tax Act of Bhutan 2025 (DRC, `bt/law/Income-Tax-Act-of-Bhutan-2025.pdf`, sha256 d264ef94...), in force 1 January
2026 (s. 2); Rules on the Income Tax Act of Bhutan 2025 (DRC, drc.gov.bt/wp-content/uploads/2026/01/, `bt/law/d4/
Rules-ITA-2025.pdf`, sha256 3798a629...; only Rules 47-50, 61-64, 148-150 and 153's first sentence read; its Annexure I
withholding tables were not opened: they are a referee dataset). Provisions used:
* Schedule 1 para 1 (individuals): nil to Nu 300,000; "5% of the amount by which the total taxable income exceeds Nu.
  300,000" to 500,000; "Nu. 10,000 plus 10%" to 750,000; "Nu. 35,000 plus 15%" to 1,200,000; "Nu. 102,500 plus 20%" to
  2,000,000; "Nu. 262,500 plus 25%" to 3,500,000; "Nu. 637,500 plus 30%" above (#guards: the printed fixed amounts equal
  the band sums). No surcharge: the 2001 Act's s. 14 A has no counterpart in the 2025 Act.
* s. 44: "deduct 15 per cent of the amount of total employment income of that individual or Nu. 150,000, whichever is
  lower". The employer's contributions to NPPF / approved funds are excluded from employment income (s. 24 (4), within
  the prescribed limits); no deduction of the employee's own provident-fund contribution was found in the Act or Rules:
  btPF1/btPF2 are reported as employeeSocial only.
* Schedule 6: para 1 education (actual, max Nu 350,000, or Nu 50,000 without documents; Rules 47-50: one parent per
  child): input btEducation (adult 1); para 7 donations up to "5 per cent of the person's adjusted income"; para 9
  "Health contribution paid to the recognized agency by an individual, shall be allowed as deduction": inputs
  btHealth1/btHealth2 (annual; the rate is not in the tax law).
* s. 160: parenthood child tax credit for a citizen's child below 18: Nu 1,000 / 1,250 / 5,000 / 10,000 for the first /
  second / third / fourth and later child; s. 162 not refundable; Rules 148-150: one parent per child, never split: the
  model gives each child's credit, largest first, to the parent with the most tax left (reading); s. 161: a child's
  education relief excludes the credit (when btEducation is given the credits are not claimed: reading).
* s. 10 (2), s. 280 (1), Schedule 1 para 7 (2)(b): interest and dividends of individuals are final withholding payments
  at 10 %; Schedule 3 para 8 (fixed-deposit interest to Nu 400,000) and para 9 (dividends to Nu 300,000) exempt.
* Schedule 3 para 13 ("Pension income": sums in an NPPF / approved fund account): pensions taken as exempt (reading).
-/

def sched2026 : Schedule :=
  Schedule.ofList [(0, 0), (300000, 500), (500000, 1000), (750000, 1500), (1200000, 2000), (2000000, 2500), (3500000, 3000)]

/-- Schedule 1 para 1 as printed (fixed amounts). -/
def printed2026 (x : Int) : Int :=
  if x ≤ 300000 then 0
  else if x ≤ 500000 then divR .halfUp (500 * (x - 300000)) BP
  else if x ≤ 750000 then 10000 + divR .halfUp (1000 * (x - 500000)) BP
  else if x ≤ 1200000 then 35000 + divR .halfUp (1500 * (x - 750000)) BP
  else if x ≤ 2000000 then 102500 + divR .halfUp (2000 * (x - 1200000)) BP
  else if x ≤ 3500000 then 262500 + divR .halfUp (2500 * (x - 2000000)) BP
  else 637500 + divR .halfUp (3000 * (x - 3500000)) BP

theorem sched2026_progressive : sched2026.progressive = true := by decide

#guard sched2026.tax roundR 500000 = 10000 ∧ sched2026.tax roundR 750000 = 35000 ∧ sched2026.tax roundR 1200000 = 102500 ∧
  sched2026.tax roundR 2000000 = 262500 ∧ sched2026.tax roundR 3500000 = 637500
#guard [0, 299999, 300001, 456789, 500001, 999999, 1500000, 2500000, 3500001, 9000000].all
  fun x => sched2026.tax roundR x = printed2026 x

/-- s. 44 employment deduction. -/
def empDeduction (w : Int) : Int := min (divR .down (1500 * pos w) BP) 150000
#guard empDeduction 600000 = 90000 ∧ empDeduction 1000000 = 150000 ∧ empDeduction 2000000 = 150000

/-- s. 160 credit for the k-th child (0-based). -/
def childCredit (k : Nat) : Int := if k == 0 then 1000 else if k == 1 then 1250 else if k == 2 then 5000 else 10000

def finalWHRate : Int := 1000
def interestExempt : Int := 400000
def dividendExempt2026 : Int := 300000

/-- One person in 2026: (taxable income, tax before credits, final withholding on interest and dividends). -/
def person2026 (wages se rent interest div health donation education : Int) : Int × Int × Int :=
  let emp := pos (pos wages - empDeduction wages)
  let adj := emp + pos se + pos rent
  let don := min (pos donation) (divR .down (500 * adj) BP)
  let edu := min (pos education) 350000
  let ti := pos (adj - pos health - don - edu)
  let fw := divR .halfUp (finalWHRate * (pos (interest - interestExempt) + pos (div - dividendExempt2026))) BP
  (ti, sched2026.tax roundR ti, fw)

/-- Child credits assigned child by child (largest first) to the parent with the most tax left (Rules 148-150). -/
def assignCredits (taxes : List Int) (credits : List Int) : List Int :=
  credits.foldl (fun (left : List Int) cr =>
    let best := (left.zipIdx).foldl (fun b (t, i) => if t > (left.getD b 0) then i else b) 0
    left.zipIdx.map fun (t, i) => if i == best then pos (t - cr) else t) taxes

def compute2026 (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let edu := (c.int? "btEducation").getD 0
  let rs := (c.adults.zip (List.range n)).map fun (a, i) =>
    person2026 a.wages a.selfEmployment (share c.rentalIncome i) (share c.interest i) (share c.dividends i)
      ((c.int? (if i = 0 then "btHealth1" else "btHealth2")).getD 0)
      (if i = 0 then c.charitable else 0) (if i = 0 then edu else 0)
  let kids := (c.children.filter (·.age < 18)).length
  let credits := if edu > 0 then [] else ((List.range kids).map childCredit).reverse
  let before := rs.map (·.2.1)
  let after := assignCredits before credits
  let pf (i : Nat) := (c.int? (if i = 0 then "btPF1" else "btPF2")).getD 0
  Out.make c "BT" "BTN" (sumInts after)
    (surtaxes := [("finalWithholdingInterestDividends", sumInts (rs.map (·.2.2)))])
    (employeeSocial := pf 0 + (if n = 2 then pf 1 else 0))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.1))), Out.d "taxBeforeCredits" (sumInts before),
                Out.d "childCredits" (sumInts before - sumInts after),
                Out.dStr "law" "Income Tax Act of Bhutan 2025 (income year 2026)"])
    (unsupported := ["employee NPPF/PF contributions: no deduction in the 2025 Act or Rules found; btPF1/btPF2 reported as employeeSocial only",
      "health contribution (Schedule 6 para 9) deducted only when btHealth1/btHealth2 are given (its rate is not in the tax law)",
      "child credit assumes citizen parents and children below 18; education relief (btEducation) replaces the credits (s. 161, reading)",
      "rent: gross rent taken as property income; rental expenses (Rules) not modelled",
      "interest read as fixed-deposit interest (Schedule 3 para 8 exemption); savings-account interest is exempt (para 7)",
      "pension income exempt (Schedule 3 para 13, reading); presumptive taxation of small businesses (Schedule 2) not modelled"])

/- A married couple, wages 1,000,000 and 0, two children: taxable 850,000; tax 35,000 + 15,000 = 50,000; credits
1,250 + 1,000 to the earner: 47,750. -/
#guard (let r := person2026 1000000 0 0 0 0 0 0 0; r.1 = 850000 ∧ r.2.1 = 50000)
#guard assignCredits [50000, 0] [1250, 1000] = [47750, 0]

def computeWith2025 (literal : Bool) (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let pf (i : Nat) := (c.int? (if i = 0 then "btPF1" else "btPF2")).getD 0
  let rs := (c.adults.zip (List.range n)).map fun (a, i) =>
    person literal a.wages a.selfEmployment (share c.dividends i) (share c.rentalIncome i) (pf i)
      (if i = 0 then c.charitable else 0) (if i = 0 then (c.int? "btEducation").getD 0 else 0)
  Out.make c "BT" "BTN" (sumInts (rs.map (·.2.1)))
    (surtaxes := [("surcharge14A", sumInts (rs.map (·.2.2)))])
    (employeeSocial := pf 0 + (if n = 2 then pf 1 else 0))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.1))),
                Out.dStr "table" (if literal then "as printed (242,499)" else "band sums")])
    (unsupported := ["NPPF/GPF and GIS contributions are deductible (Rules r. 35) at rates set outside the tax law: give btPF1/btPF2 (annual); default 0",
      "interest is not a PIT source after the 2016 repeal of s. 4.2 (d); TDS on interest not modelled",
      "pension income exempt (s. 5.3); capital gains not taxed under the 2001 Act"])

/-- Income year 2025: ITA 2001 (Fourth Edition); income year 2026: ITA 2025. -/
def computeWith (literal : Bool) (c : Canon) : Out :=
  if c.year == 2026 then compute2026 c else computeWith2025 literal c

def country : Country :=
  { code := "BT", name := "Bhutan (income years 2025 and 2026)", currency := "BTN", year := "2025, 2026", compute := computeWith false,
    computeWith := fun args c => computeWith (args.contains "--printed") c }

theorem sched_progressive : sched.progressive = true := by decide

/- Surcharge cliff: PIT reaches Nu 1,000,000 at a net taxable income of 4,024,999 (band sums, rounded to the ngultrum); one ngultrum of tax
more brings 100,000 of surcharge. -/
#guard sched.tax roundR 4024998 < 1000000 ∧ sched.tax roundR 4024999 ≥ 1000000
#guard (let t := sched.tax roundR 4024999; t + surcharge t) - (let t := sched.tax roundR 4024998; t + surcharge t) = 100001

end BtTax
