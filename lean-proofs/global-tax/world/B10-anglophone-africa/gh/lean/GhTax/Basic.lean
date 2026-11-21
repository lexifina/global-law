import TaxKernel.World

/-!
# Ghana: income tax of a resident individual, Income Tax Act 2015 (Act 896) as amended, year of assessment 2025

Sources (files in `gh/law/`):
* Income Tax Act 2015 (Act 896) as enacted (GRA "Acts" page, gra.gov.gh/wp-content/uploads/2020/09/INCOME-TAX-ACT-2015-
  ACT-896.pdf, a 182-page scan read by OCR, `act896_ocr.txt`). s. 51: "In arriving at the chargeable income of a
  resident individual for a year of assessment ... deduct the personal reliefs specified in the Fifth Schedule". Fifth
  Schedule para. 1: "(a) ... a dependant spouse or at least two dependant children ... two hundred currency points; ...
  (c) ... sixty years of age and above ... two hundred currency points; (d) ... sponsoring the education of the child
  or ward ... two hundred currency points per child or ward up to a maximum of three ..."; the interpretation section:
  "'currency point' means one Cedi". No amendment of the Fifth Schedule was found in the amending Acts read (1071, 1094,
  1111, 1134, the 2021 Act) nor in Global law's Ghana record (Acts 902, 907, 941, 956, 973).
* Income Tax (Amendment) (No. 2) Act 2023 (Act 1111), date of assent and gazette 29 December 2023 (Parliament of Ghana
  repository, handle 123456789/3974; scan, OCR checked against the page image of p. 3): First Schedule para. 1(1):
  "First GH¢5,880 Nil | Next GH¢1,320 5 per cent | Next GH¢1,560 10 per cent | Next GH¢38,000 17.5 per cent | Next
  GH¢192,000 25 per cent | Next GH¢366,240 30 per cent | Exceeding GH¢600,000 35 per cent". The "Next" amounts add up
  to 605,000, not 600,000 (FINDINGS F1). In force for 2024 and 2025: the next change is Act 1178 from 1 September 2026
  (GRA notice "Amendments - Income Tax Act, 2026 (Act 1178)"). The Income Tax (Amendment) Act 2025 (Act 1134, assent
  2 April 2025) only removes withholding on lottery winnings and unprocessed gold.
* National Pensions Act 2008 (Act 766) (Global law `ghana/national/acts/act/2008/766`, official text on
  repository.parliament.gh) s. 3(1): "a worker's contribution of an amount equal to five and half per centum of the
  worker's salary"; s. 89(1): "Tax is not payable by an employer or employee in respect of contribution towards
  retirement or pension schemes under this Act". Later amendments of Act 766 (any ceiling on insurable earnings) are
  not in the record: none modelled.
-/

namespace GhTax
open TaxKernel

/-- Act 1111 First Schedule para. 1(1), read with the explicit threshold of row 7 (35 % above 600,000): band 6 then
    covers 238,760 - 600,000 (361,240 instead of the printed 366,240). -/
def schedExplicit : Schedule :=
  Schedule.ofList [(0, 0), (5880, 500), (7200, 1000), (8760, 1750), (46760, 2500), (238760, 3000), (600000, 3500)]
/-- The same table read as a chain of "Next" amounts: 30 % up to 605,000, 35 % above. -/
def schedChain : Schedule :=
  Schedule.ofList [(0, 0), (5880, 500), (7200, 1000), (8760, 1750), (46760, 2500), (238760, 3000), (605000, 3500)]
/-- Act 766 s. 3(1). -/
def ssnitRate : Int := 550
/-- Fifth Schedule (currency points = cedis). -/
def reliefFamily : Int := 200
def reliefAged : Int := 200
def reliefEducation : Int := 200
def reliefEducationMax : Nat := 3

def pct (bp x : Int) : Int := divR .down (bp * x) BP

structure Person where
  tax : Int
  chargeable : Int
  ssnit : Int
  relief : Int

def person (chain : Bool) (a : Adult) (relief : Int) : Person :=
  let w := pos a.wages
  let ssnit := perPeriod 12 (fun m => pct ssnitRate (pos m)) w
  let assessable := pos (w + a.selfEmployment - ssnit)
  let ci := pos (assessable - relief)
  let s := if chain then schedChain else schedExplicit
  { tax := s.tax Rule.unitDown ci, chargeable := ci, ssnit := ssnit, relief := min relief assessable }

def out (c : Canon) : Out :=
  let chain := (c.str? "gh1111Reading").getD "" == "next"
  let inSchool := Int.ofNat (min ((c.int? "childrenInSchool").getD 0).toNat reliefEducationMax)
  let kids := c.childrenUnder 18
  let spouseDependant := match c.adult2? with
    | some b => c.married && b.wages + b.selfEmployment ≤ 0
    | none => false
  -- the family and education reliefs go to the first adult (one relief per child, Fifth Schedule para. 2)
  let r1 := (if spouseDependant || kids ≥ 2 then reliefFamily else 0) + reliefEducation * inSchool +
            (if c.adult1.age ≥ 60 then reliefAged else 0)
  let p1 := person chain c.adult1 r1
  let ps := p1 :: (match c.adult2? with
    | some b => [person chain b (if b.age ≥ 60 then reliefAged else 0)]
    | none => [])
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 then ["interest, dividends and rents: final withholding not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled (exempt from SSNIT, Act 766 s. 89(2))"] else [])
  Out.make c "GH" "GHS" (sumInts (ps.map (·.tax))) (employeeSocial := sumInts (ps.map (·.ssnit)))
    (detail := [Out.d "chargeableIncome" (sumInts (ps.map (·.chargeable))), Out.d "reliefs" (sumInts (ps.map (·.relief))),
      Out.dStr "reading" (if chain then "Act 1111 bands as a chain of Next amounts (35 % above 605,000)" else "Act 1111 row 7 threshold (35 % above 600,000)"),
      Out.dStr "note" "individual taxation; SSNIT 5.5 % exempt (Act 766 s. 89); Fifth Schedule reliefs (spouse/children 200, aged 200, education 200 per child up to 3)"])
    (unsupported := unsup ++ ["education relief needs input childrenInSchool (default 0)", "disability and dependant-relative reliefs need inputs not in the contract",
      "business income taxed on the same scale without business deductions"])

def country : Country := { code := "GH", name := "Ghana (Income Tax Act 2015, Act 896)", currency := "GHS", year := "2025", compute := out }

/-- The default schedule (the explicit-threshold reading). -/
def sched : Schedule := schedExplicit
theorem sched_progressive : sched.progressive = true := by decide
theorem chain_progressive : schedChain.progressive = true := by decide

/- The two readings differ on chargeable income between 600,000 and 605,000 only: at most 5 % of 5,000 = 250 cedis. -/
#guard schedChain.tax Rule.unitDown 605000 + 250 = schedExplicit.tax Rule.unitDown 605000
#guard schedChain.tax Rule.unitDown 600000 = schedExplicit.tax Rule.unitDown 600000
#guard schedChain.tax Rule.unitDown 700000 + 250 = schedExplicit.tax Rule.unitDown 700000
/- The "Next" amounts of Act 1111 sum to 605,000 while row 7 starts at 600,000; Act 1094 (2023) summed to 600,000. -/
#guard 5880 + 1320 + 1560 + 38000 + 192000 + 366240 = 605000
#guard 4824 + 1320 + 1560 + 36000 + 196740 + 359556 = 600000

end GhTax
