import LegalProofs.USTax.TaxCourt.Params
import TaxCode.Individual.D.Education

/-!
# §25A American opportunity and lifetime learning credits, tax years 2012–2024

* **AOTC** (§25A(b) as modified by §25A(i): enacted by ARRA §1004 for 2009–2010, extended by TRUIRJCA §103, ATRA §103
  and made permanent by PATH §102): per eligible student, 100% of the first $2,000 of qualified tuition and related
  expenses plus 25% of the next $2,000 (maximum $2,500). A student is eligible only if (§25A(b)(2), (i)(2)–(3)): the
  credit was not allowed for the student in any 4 earlier taxable years; the student is at least half-time in a degree
  program for at least one academic period beginning in the year; the student had not completed the first 4 years of
  postsecondary education before the year; no felony drug conviction. 40% of the credit (after the phase-out) is
  refundable (§25A(i)(5)), except for a taxpayer to whom §1(g) applies (`kiddieRule`).
* **LLC** (§25A(c)): 20% of up to $10,000 of qualified expenses per return (for students not taking the AOTC).
* **Phase-out** (§25A(d), (i)(4)): AOTC $80,000–$90,000 ($160,000–$180,000 joint), not indexed. LLC before 2021: the
  §25A(d)(1) $40,000 / $80,000 indexed by §25A(h)(2) (the year's Rev. Proc.); from 2021 the AOTC amounts (Pub. L.
  116-260 div. EE §104). The Form 8863 instructions multiply by the ratio rounded to three places; we use the exact
  statutory ratio (`TaxCode.Individual.D.eduPhaseStatute`) and round once.
* **Married filing separately**: no credit (§25A(g)(6)).

The AOTC and LLC figures here are reused from the 2025 model (`TaxCode.Individual.D.aotcPerStudent`, `llcTentative`).
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual

/-- One student, as the court finds. -/
structure StudentFacts where
  name : String := ""
  /-- Qualified tuition and related expenses paid for the student in the year, after tax-free assistance. -/
  qualifiedExpenses : Int := 0
  /-- Earlier taxable years for which the AOTC (or the Hope credit) was allowed for this student. -/
  aotcPriorYears : Nat := 0
  /-- At least half-time in a degree program for an academic period beginning in the year (§25A(b)(2)(B)). -/
  halfTime : Bool := true
  /-- Had completed the first 4 years of postsecondary education before the year (§25A(b)(2)(C), (i)(2)). -/
  completedFirstFourYears : Bool := false
  felonyDrugConviction : Bool := false
  /-- The taxpayer elects the lifetime learning credit for this student instead. -/
  electLlc : Bool := false
  deriving Repr, Inhabited

/-- Whether the student is eligible for the AOTC, and the failures. -/
def aotcFailures (s : StudentFacts) : List String :=
  (if s.aotcPriorYears < 4 then [] else ["§25A(i)(2)/(b)(2)(A): credit allowed in 4 earlier years"]) ++
  (if s.halfTime then [] else ["§25A(b)(2)(B): not at least half-time"]) ++
  (if s.completedFirstFourYears then ["§25A(b)(2)(C)/(i)(2): first 4 years of postsecondary education completed"]
   else []) ++
  (if s.felonyDrugConviction then ["§25A(b)(2)(D): felony drug conviction"] else [])

def aotcEligible (s : StudentFacts) : Bool := aotcFailures s |>.isEmpty

/-- The lifetime learning credit's §25A(d) lower amount (unmarried) by year, as the year's revenue procedure sets it
and Pub. 970 prints it (e.g. Rev. Proc. 2011-52 §3.05(2): "$52,000 ($104,000 for a joint return)"); 2021 on $80,000
(Pub. L. 116-260 div. EE §104; Pub. 970 (2021)). The AOTC range is $80,000–$90,000 / $160,000–$180,000 in every
Pub. 970, 2012–2024. The joint amount is twice it, and the
range is $10,000 ($20,000 joint). -/
def llcLower (y : Nat) : Int :=
  match y with
  | 2012 => 52000 | 2013 => 53000 | 2014 => 54000 | 2015 => 55000 | 2016 => 55000 | 2017 => 56000
  | 2018 => 57000 | 2019 => 58000 | 2020 => 59000 | _ => 80000

/-- §25A(d) phase-out with a given lower amount (unmarried), exactly, rounded once. -/
def eduPhase (lower : Int) (joint : Bool) (magi credit : Int) : Int :=
  let lo := if joint then 2 * lower else lower
  let range := if joint then 20000 else 10000
  roundDollar (credit * max 0 (min (lo + range - magi) range)) range

structure EducationResult where
  aotcRefundable : Int := 0
  /-- AOTC nonrefundable part plus the LLC, before the §26(a) limit. -/
  nonrefundable : Int := 0
  aotc : Int := 0
  llc : Int := 0
  deriving Repr, Inhabited, DecidableEq

/-- **The credits for the year.** `magi`: AGI (plus §§911, 931, 933 exclusions). -/
def educationCredits (p : Params) (f : Filing) (magi : Int) (students : List StudentFacts) (kiddieRule : Bool) :
    EducationResult :=
  if f == .mfs then {} else
  let joint := f == .mfj
  let aotcStudents := students.filter fun s => aotcEligible s && !s.electLlc
  let llcStudents := students.filter fun s => !(aotcEligible s && !s.electLlc)
  let aotc0 := D.aotcTentative (aotcStudents.map (·.qualifiedExpenses))
  let llc0 := D.llcTentative (llcStudents.foldl (fun t s => t + pos s.qualifiedExpenses) 0)
  let aotc := eduPhase 80000 joint magi aotc0
  let llc := eduPhase (llcLower p.year) joint magi llc0
  let refundable := if kiddieRule then 0 else pctRound aotc 4000
  { aotcRefundable := refundable, nonrefundable := aotc - refundable + llc, aotc := aotc, llc := llc }

/-! ## Tests -/

section
private def py (y : Nat) : Params := (params? y).getD default
private def st (e : Int) : StudentFacts := { name := "s", qualifiedExpenses := e }

-- One student, $4,000 of expenses, single, MAGI $50,000: $2,500, of which $1,000 refundable.
#guard educationCredits (py 2015) .single 50000 [st 4000] false =
  { aotcRefundable := 1000, nonrefundable := 1500, aotc := 2500, llc := 0 }
-- Fifth year of claims: no AOTC; the LLC instead (20% of $4,000 = $800).
#guard educationCredits (py 2015) .single 50000 [{ st 4000 with aotcPriorYears := 4 }] false =
  { aotcRefundable := 0, nonrefundable := 800, aotc := 0, llc := 800 }
-- AOTC phase-out: single MAGI $85,000: half.
#guard (educationCredits (py 2014) .single 85000 [st 4000] false).aotc = 1250
-- LLC phase-out by year: 2014 single $54,000–$64,000: at $59,000 half of $2,000.
#guard (educationCredits (py 2014) .single 59000 [{ st 10000 with electLlc := true }] false).llc = 1000
#guard (educationCredits (py 2022) .single 59000 [{ st 10000 with electLlc := true }] false).llc = 2000
-- Married filing separately: nothing.
#guard educationCredits (py 2019) .mfs 30000 [st 4000] false = {}
end

end Legal.USTax.TaxCourt
