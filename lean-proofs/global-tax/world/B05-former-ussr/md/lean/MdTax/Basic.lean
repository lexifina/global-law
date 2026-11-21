import TaxKernel.World

/-!
# Moldova: impozitul pe venit of resident individuals (Codul fiscal, Title II), 2025

Access tier A for the tax (Codul fiscal as dated law); compulsory contributions not reached (unsupported).
Source: Codul fiscal nr. 1163/1997, consolidated text "Act la zi" (last change in force 01.11.2026) served by weblex.md
through the Ministry of Finance's own link (mf.gov.md/ro, menu "Codul fiscal al Republicii Moldova" ->
demo.weblex.md/item/view/iddbtype/1/id/LPLP199704241163/specialview/1/ref/mf), fetched 2026-11-20
(`md/law/rescue/weblex_cf_current_20261120.html`, sha256 ac5695fd…). Each provision carries its amendment notes; the
2025 wording is the current wording wherever the last note is in force on or before 01.01.2025:
* art. 15 lit. a): "în mărime de 12% din venitul anual impozabil" (last changed by Law 257/2020, from 01.01.2021).
* art. 12 pct. 4), 11), 12): taxable income = gross income less deductions and exemptions (art. 33-35).
* art. 33(1): a resident "care are un venit anual impozabil mai mic de 360000 de lei" has "o scutire personală în sumă
  de 29700 lei pe an" (Law 214/2024, from 01.01.2025; the next change, alin. (11), applies from 01.01.2026).
* art. 34(2): spouse exemption 21780 lei only for spouses of the persons in art. 33(2) (disability, Chernobyl, war
  veterans): not in the household contract.
* art. 35(1),(2): 9900 lei a year per dependant (ascendant or descendant) whose own income does not exceed 12400 lei
  (Law 214/2024, from 01.01.2025).
* art. 35^2(1),(2): compulsory health-insurance premiums and state social-insurance contributions paid by the
  individual are deductible "în cuantumurile stabilite de legislaţie" (their rates are set outside the Codul fiscal).
* art. 90^1(37): banks withhold a final 6 % of interest paid to residents (Law 214/2024, from 15.08.2024);
  art. 90^1(31): 6 % final on dividends (last changed by Law 257/2020; completed from 01.01.2026).
Household mapping: each adult files alone (no joint filing in Title II); wages + self-employment (art. 15 a: individual
entrepreneurs at 12 %) form the annual gross income; each child is a dependant of one parent (the statute names no
rule for two claimants: the model gives the children to the higher earner); interest and dividends taxed by the final
withholding. Rounding: whole lei, down.
Reading taken (FINDINGS F2): the 360,000 lei test of art. 33(1) is applied to taxable income before the personal
exemption (the definition in art. 12 pct. 4 would include the exemption itself, which is circular).
-/

namespace MdTax
open TaxKernel

/-- art. 15 lit. a): one 12 % rate. -/
def sched : Schedule := Schedule.ofList [(0, 1200)]

def personalExemption : Int := 29700
def personalLimit : Int := 360000
def dependantExemption : Int := 9900

/-- art. 33(1): the exemption is lost once the annual taxable income reaches 360,000 lei. -/
def pe (ti : Int) : Int := if ti < personalLimit then personalExemption else 0

/-- Tax of one adult with `kids` dependants claimed. -/
def tax1 (gross : Int) (kids : Int) : Int × Int :=
  let base := pos gross
  let ti := pos (base - pe base - dependantExemption * kids)
  (sched.tax Rule.unitDown ti, ti)

/- The notch of art. 33(1): one more leu of income at 360,000 costs 12 % of the 29,700 exemption (3,564 lei) plus
   the leu's own tax and the rounding: 43,200 - 39,635 = 3,565 lei. -/
#guard (tax1 359999 0).1 = 39635 ∧ (tax1 360000 0).1 = 43200
/- Net income does not recover its 359,999-lei level until gross income passes 364,050 lei (360,000 + 3,564 / 0.88). -/
#guard 364050 - (tax1 364050 0).1 ≤ 359999 - (tax1 359999 0).1 ∧ 364051 - (tax1 364051 0).1 > 359999 - (tax1 359999 0).1

def out (c : Canon) : Out :=
  let kids : Int := c.nChildren
  let gross (a : Adult) : Int := a.wages + a.selfEmployment
  let res : List (Int × Int) :=
    match c.adults with
    | [a] => [tax1 (gross a) kids]
    | [a, b] => if gross a ≥ gross b then [tax1 (gross a) kids, tax1 (gross b) 0] else [tax1 (gross a) 0, tax1 (gross b) kids]
    | l => l.map fun a => tax1 (gross a) 0
  let it := sumInts (res.map (·.1))
  let intTax := divR .down (600 * pos c.interest) BP
  let divTax := divR .down (600 * pos c.dividends) BP
  Out.make c "MD" "MDL" it (surtaxes := [("interestFinalWithholding", intTax), ("dividendFinalWithholding", divTax)])
    (employeeSocial := 0)
    (detail := [Out.d "taxableIncome" (sumInts (res.map (·.2))),
      Out.dStr "note" "Codul fiscal art. 15 a) 12 %, art. 33(1) 29,700 lei below 360,000 lei, art. 35 9,900 lei per dependant (texts in force 01.01.2025); interest/dividends 6 % final (art. 90^1)"])
    (unsupported := (if c.adults.any (fun a => a.wages > 0) then ["compulsory health-insurance premium and state social-insurance contribution of the employee (rates outside the Codul fiscal, not reached): employeeSocial = 0 and their art. 35^2 deduction is not applied"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rent: 12 % withheld by a business tenant (art. 90^1(3)) or 7 % of the monthly contract value paid by the owner (art. 90^1(34)): tenant unknown"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains (cap. 5, art. 37-42) not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: treatment not read"] else []))

def country : Country := { code := "MD", name := "Moldova", currency := "MDL", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end MdTax
