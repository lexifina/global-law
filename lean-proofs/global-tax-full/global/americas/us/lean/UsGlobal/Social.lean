import UsGlobal.Pit

/-!
# United States 2025: employer FICA and FUTA (2200)

Source: 26 U.S.C. (Cornell LII, current Code; `us/law/usc26_31*.txt`, `usc26_33*.txt`).
* **§ 3111 (a)** "an excise tax … equal to 6.2 percent of the wages (as defined in section 3121 (a))": wages up to the
  contribution and benefit base, $176,100 for 2025 (the 1.x model's `Compare.Us.wageBase`, from 89 FR 85276);
  **§ 3111 (b)** "1.45 percent of the wages".
* **§ 3301** "equal to 6 percent of the total wages (as defined in section 3306 (b))"; **§ 3306 (b) (1)** wages above
  "$7,000" are excluded; **§ 3302 (b)** the credit for state contributions "shall not exceed 90 percent of the tax":
  0.6 % net when the state contributions are paid (California's 2025 credit reduction, § 3302 (c) (2), not modelled).
* State payroll contributions (California UI, ETT; SDI is employee-paid) not read: unsupported.

**P7 triage pass (2026-11-21): 3000 California Employment Training Tax**, re-filed from the P4 C entry "California UI and
ETT" (OECD Guide §40: a levy on payroll that confers no entitlement to benefit is 3000, not 2000; §47). Cal. Unemployment
Insurance Code (lexifina/united-states-california-law, Legislative Counsel database snapshot 2016-11-27, commit 3e9e994dd132):
* **§ 976.6**: "every employer, except an employer defined by Section 676, 684, or 685, and except an employer that has
  elected an alternate method of financing ... shall pay into the Employment Training Fund contributions at the rate of
  0.1 percent of wages specified in Section 930" (as amended by Stats. 2001, Ch. 111).
* **§ 930**: "'Wages' does not include remuneration in excess of seven thousand dollars ($7,000) paid to an individual by
  an employer during any calendar year".
At most $7 per employee and year. Grade B: the text read is a 2016 snapshot (sections last amended 2001 and 1984); its
2025 wording was not read from a 2025 text. California UI contributions stay in the P4 C entry.
-/

namespace UsGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon UsGlobal

def oasdi : Contribution := Contribution.flatCapped "OASDI (employer)" 620 Compare.Us.wageBase
def hi : Contribution := { name := "Hospital insurance (employer)", sched := Schedule.flat 145 }
def futa : Contribution := Contribution.flatCapped "FUTA (net of the § 3302 credit)" 60 7000

def sscF : Family := employerFamily "2200 employer FICA and FUTA" [oasdi, hi, futa]
  "26 U.S.C. § 3111 (a) 6.2 % to $176,100, (b) 1.45 %; § 3301 6 % on $7,000 (§ 3306 (b) (1)) less the § 3302 credit (90 %)"

/-- Cal. UIC § 976.6: 0.1 % of wages as defined in § 930 (the first $7,000 per employee and year). -/
def ett : Contribution := Contribution.flatCapped "Employment Training Tax (California)" 10 7000

def ettF : Family := employerFamily "3000 California Employment Training Tax" [ett]
  "Cal. Unemployment Insurance Code § 976.6 (0.1 %), § 930 (first $7,000 per employee)" (oecd := .payroll) (level := .state)

def families : List Family := [sscF, ettF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.company.payroll > 0) "California employer UI contributions; ETT charged at 0.1 % of the first $7,000 (employer types of UIC §§ 676, 684, 685 and reimbursable employers not inputs), and the 2025 FUTA credit reduction for California (§ 3302 (c) (2)), not modelled; one employer per adult"

#guard oasdi.amount 73520 == 4558
#guard oasdi.amount 300000 == 10918
#guard hi.amount 73520 == 1066
#guard futa.amount 73520 == 42
#guard ett.amount 73520 == 7
#guard ett.amount 5000 == 5

end UsGlobal.Social
