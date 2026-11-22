import TaxKernel.World

/-!
# Antigua and Barbuda 2025: personal income tax repealed in 2016; social security and medical benefits

Sources (laws.gov.ag, read 2026-11-20; `ag/law/`):
* Unincorporated Business Tax Act, 2016 (No. 7 of 2016; Gazette 23 June 2016; `ubt_2016.pdf`), s. 47 "Repeal: The
  Personal Income Tax Act 2005 is repealed with effect from 1st July, 2016"; s. 46 transitional. (The Personal
  Income Tax (Amendment) Act 2016, No. 8 of 2016, set the 2016 allowance at $21,000 and the last returns.) The
  Income Tax Act, Cap. 212 (1957) taxes companies; unincorporated business income is taxed under the 2016 Act
  (not modelled: `unsupported` for self-employment).
* Social Security Act, Cap. 408 and the Social Security (Collection of Contributions) Regulations, 2013 (S.I. 15 of
  2013, `ss_coll_regs_2013.pdf`) reg. 4(1)(iii): "no contribution is payable in respect of any wages in excess of one
  thousand, three hundred and ninety five dollars a week or monthly wages in excess of six thousand five hundred
  dollars"; as amended by S.I. 60 of 2016 (scanned; OCR `ss_coll_amend_2016_ocr.txt`): reg. 4(1)(b) "Effective 1st
  January, 2017 in the case of employees other than employees in the public service, 12% of the wages up to the
  contribution ceiling ... 5% of which is payable by the employee and 7% by the employer", rising "to a maximum of
  16% by 1st January, 2025" (Schedule 1, row 2025: private sector employee 7 %, employer 9 %, total 16 %; public
  service 6 % / 9 % / 15 %); the 2016 Schedule 2 prints the ceiling "$1,500.00 per week and $6,500.00 per month".
* Medical Benefits Act, 2010 (No. 4 of 2010) and Medical Benefits Regulations, 2011 (S.I. 27 of 2011,
  `mb_regs_2011.pdf`) reg. 17(2) employed person 16 to 60: "3½% of that person's salary or wages"; reg. 17(3) 60 to
  70: "2½%". No ceiling is printed.

Not found / not modelled: an education levy on employees (no act or instrument found in the laws.gov.ag indexes:
`unsupported` for wage earners, see FINDINGS); the social security pensionable age (Age Pensions and Grants
Regulations 2013, not read): contributions are modelled from 16 to 59 and flagged from 60. Default: private sector;
`"agSector": "public"` uses the public-service row.
-/

namespace AgTax
open TaxKernel

def ceiling : Int := 6500 * 12
def ssPrivate : Contribution := Contribution.flatCapped "socialSecurity" 700 ceiling   -- S.I. 60/2016 Sch. 1, 2025
def ssPublic : Contribution := Contribution.flatCapped "socialSecurity" 600 ceiling    -- idem, public service
def mbUnder60 : Contribution := { name := "medicalBenefits", sched := Schedule.flat 350 }  -- reg. 17(2)
def mb60to70 : Contribution := { name := "medicalBenefits", sched := Schedule.flat 250 }   -- reg. 17(3)

def ss (isPublic : Bool) (a : Adult) : Int :=
  if a.age < 16 then 0 else if isPublic then ssPublic.amount a.wages else ssPrivate.amount a.wages

def mb (a : Adult) : Int :=
  if a.age < 16 then 0 else if a.age < 60 then mbUnder60.amount a.wages
  else if a.age < 70 then mb60to70.amount a.wages else 0

def out (c : Canon) : Out :=
  let isPublic := c.str? "agSector" = some "public"
  let s := sumInts (c.adults.map (ss isPublic))
  let m := sumInts (c.adults.map mb)
  let uns :=
    (if c.adults.any (fun a => a.wages > 0) then
      ["education levy on employees: no accessible act or regulation found, not included"] else [])
    ++ (if c.adults.any (fun a => a.age ≥ 60 ∧ a.wages > 0) then
      ["social security liability at and after pensionable age (Age Pensions and Grants Regulations 2013, not read): contributions kept"] else [])
    ++ (if c.adults.any (fun a => a.selfEmployment > 0) then
      ["self-employment: Unincorporated Business Tax Act 2016 and self-employed contributions not modelled"] else [])
  Out.make c "AG" "XCD" 0 (employeeSocial := s + m)
    (detail := [Out.d "socialSecurity" s, Out.d "medicalBenefits" m,
      Out.dStr "note" "Personal Income Tax Act 2005 repealed from 1 July 2016 (UBT Act 2016 s. 47); SS regs (S.I. 60/2016) 7 % up to $6,500 a month; MB regs 2011 reg. 17: 3.5 %"])
    (unsupported := uns)

def country : Country :=
  { code := "AG", name := "Antigua and Barbuda (private-sector employee)", currency := "XCD", year := "2025",
    compute := out }

end AgTax
