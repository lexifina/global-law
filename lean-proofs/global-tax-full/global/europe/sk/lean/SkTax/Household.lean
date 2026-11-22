import SkTax.Tax

/-!
# A household: individual assessment of each adult, the spouse allowance, the bonus claimant, prídavok

Slovakia taxes each person separately (no joint return). The couple's choices: who claims the NČZD na manželku
(either spouse may, for the other, § 11 ods. 3), who claims the daňový bonus (one of them, § 33 ods. 4; "ak sa
nedohodnú inak ... matka, otec": the model takes the better one unless `skBonusBy` names an adult), and whether the
claimant adds the other's base (§ 33 ods. 8). Investment income of a couple is split equally (§ 4 ods. 8:
bezpodielové spoluvlastníctvo "v rovnakom pomere u každého z nich, ak sa nedohodnú inak").
-/

namespace SkTax
open TaxKernel

/-- One adult's inputs (cents). -/
structure Person where
  wages : Int := 0
  receipts : Int := 0      -- § 6 ods. 1, 2 príjmy
  profit : Int := 0        -- receipts − expenses, before contributions
  pension : Int := 0       -- dôchodok (exempt, § 9 ods. 2; reduces the NČZD, § 11 ods. 6)
  rental : Int := 0        -- § 6 ods. 3 (net; the § 9 ods. 1 písm. g) exemption applied to it)
  gains : Int := 0         -- § 8 ods. 1 písm. e) (gains on securities, taxable part before § 9 ods. 1 písm. i))
  dds : Int := 0           -- § 11 ods. 8 contributions
  /-- tax year (2022-2025) -/
  year : Nat := 2025
  deriving Repr, Inhabited

/-- One adult's computation. -/
structure PersonOut where
  eeSocial : Int
  eeHealth : Int
  seSocial : Int
  seHealth : Int
  otherHealth : Int
  zd5 : Int
  zd6 : Int
  rentalTaxable : Int
  gainsTaxable : Int
  deriving Repr, Inhabited

def PersonOut.zd (p : PersonOut) : Int := p.zd5 + p.zd6
def PersonOut.contributions (p : PersonOut) : Int := p.eeSocial + p.eeHealth + p.seSocial + p.seHealth + p.otherHealth
/-- § 11 ods. 4 písm. b): "vlastný príjem" = income less the compulsory contributions (pension included). -/
def PersonOut.ownIncome (p : PersonOut) (x : Person) : Int := p.zd5 + p.zd6 + pos x.pension

def personBases (x : Person) : PersonOut :=
  let es := eeSocialYearY x.year x.wages
  let eh := eeHealthYear x.wages
  let ss := seSocialYear x.receipts x.profit (min (pos x.wages / 12) socMaxMonthly)
  let sh := seHealthYear x.receipts x.profit (0 < x.wages)
  let exR := min (pos x.rental) smallIncomeExempt
  let exG := min (pos x.gains) (smallIncomeExempt - exR)
  let rt := pos x.rental - exR
  let gt := pos x.gains - exG
  { eeSocial := es, eeHealth := eh, seSocial := ss, seHealth := sh, otherHealth := otherHealthYear gt,
    zd5 := zd5OfY x.year x.wages, zd6 := pos (x.profit - ss - sh), rentalTaxable := rt, gainsTaxable := gt }

/-- The tax of one adult before the bonus, given the spouse allowance it claims. -/
structure TaxOut where
  ncz : Int
  nczSp : Int
  dds : Int
  baseA : Int
  baseB : Int
  taxA : Int
  taxB : Int
  deriving Repr, Inhabited

def TaxOut.tax (t : TaxOut) : Int := t.taxA + t.taxB

def personTax (x : Person) (p : PersonOut) (nczSp : Int) : TaxOut :=
  let ncz := nczWithPensionY x.year p.zd x.pension
  let dds := min (pos x.dds) ddsCap
  let total := ncz + nczSp + dds
  let n5 := min total p.zd5
  let n6 := min (total - n5) p.zd6
  let a := p.zd5 - n5 + p.rentalTaxable + p.gainsTaxable
  let b := p.zd6 - n6
  { ncz, nczSp, dds, baseA := a, baseB := b, taxA := taxSchedY x.year a, taxB := taxBizY x.year b x.receipts }

/-- Household-level options. -/
structure Opts where
  married : Bool := false
  spouseEligible : Bool := false     -- § 11 ods. 4 písm. a)
  bonusBy : Option Nat := none        -- § 33 ods. 4
  pooledTaper : Bool := true          -- Finančná správa reading of § 33 ods. 8 + 11
  divRate : Int := divRateOld
  year : Nat := 2025
  deriving Repr, Inhabited

/-- A taxpayer can claim the bonus with § 5 or § 6 ods. 1, 2 income (§ 33 ods. 1). -/
def canClaim (x : Person) : Bool := 0 < x.wages || 0 < x.receipts

structure HhOut where
  persons : List (Person × PersonOut × TaxOut)
  bonus : Int
  bonusBy : Nat
  withheld : Int
  pridavok : Int
  deriving Inhabited

def bonusFor (kids : List Kid) (ps : List (Person × PersonOut)) (i : Nat) (pooled : Bool) : Int :=
  match ps[i]? with
  | none => 0
  | some (x, p) =>
    if !canClaim x then 0 else
      let other := sumInts ((ps.zipIdx.filter (fun (_, j) => j != i)).map fun ((_, q), _) => q.zd)
      if x.year ≤ 2022 then
        claimBonus2022 kids p.zd (6 * minWage2022 ≤ x.wages || 6 * minWage2022 ≤ x.receipts)
      else if x.year ≤ 2024 then claimBonus2324 kids p.zd other
      else claimBonus kids p.zd other pooled

/-- Prídavok of tax year `y` (`Params.pridavokAt`, `schoolEntryFor`); 2025 = `pridavokFor`. -/
def pridavokForY (y : Nat) (kids : List Kid) : Int :=
  sumInts (kids.map fun k =>
    sumInts (months.map fun m =>
      if m < k.fromMonth then 0 else
        let a := if m ≤ k.birthMonth then k.age - 1 else k.age
        if a < 18 ∨ (k.student ∧ a < 25) then pridavokAt y m else 0)
    + (if k.schoolEntry then schoolEntryFor y else 0)
    -- NV 102/2020 § 1e: +70 € for October 2022 for a child born June–October 2022 (age 0, `skFromMonth` 6–10)
    + (if y ≤ 2022 ∧ k.age = 0 ∧ 6 ≤ k.fromMonth ∧ k.fromMonth ≤ 10 then pridavokOct2022Newborn else 0))

/-- ZPD § 8 ods. 1: 60 € a month per nezaopatrené dieťa (under 18 here, or a student up to 25 with `student`), plus
the one-off 110 € of § 8 ods. 1 písm. b) for a child who starts the first grade during the year. -/
def pridavokFor (kids : List Kid) : Int :=
  sumInts (kids.map fun k =>
    sumInts (months.map fun m =>
      if m < k.fromMonth then 0 else
        let a := if m ≤ k.birthMonth then k.age - 1 else k.age
        if a < 18 ∨ (k.student ∧ a < 25) then pridavok else 0)
    + (if k.schoolEntry then schoolEntryIncrease else 0))

def household (xs : List Person) (kids : List Kid) (interest dividends : Int) (o : Opts) : HhOut :=
  let ps := xs.map fun x => (x, personBases x)
  let n := ps.length
  -- § 11 ods. 3: each spouse may claim for the other
  let spouseOf (i : Nat) : Int :=
    if o.married && o.spouseEligible && n == 2 then
      match ps[i]?, ps[1 - i]? with
      | some (_, p), some (y, q) => nczSpouseY o.year p.zd (q.ownIncome y)
      | _, _ => 0
    else 0
  let taxes := ps.zipIdx.map fun ((x, p), i) => (x, p, personTax x p (spouseOf i))
  let cands := (List.range n).map fun i => (bonusFor kids ps i o.pooledTaper, i)
  let (b, by_) := match o.bonusBy with
    | some i => (bonusFor kids ps i o.pooledTaper, i)
    | none => cands.foldl (fun (acc : Int × Nat) (c : Int × Nat) => if acc.1 < c.1 then c else acc) (0, 0)
  { persons := taxes, bonus := b, bonusBy := by_,
    withheld := pctH (pos interest) interestRate + pctH (pos dividends) o.divRate,
    pridavok := if o.year ≥ 2025 then pridavokFor kids else pridavokForY o.year kids }

def HhOut.taxBeforeBonus (h : HhOut) : Int := sumInts (h.persons.map fun (_, _, t) => t.tax)
def HhOut.incomeTax (h : HhOut) : Int := h.taxBeforeBonus - h.bonus + h.withheld
def HhOut.contributions (h : HhOut) : Int := sumInts (h.persons.map fun (_, p, _) => p.contributions)
def HhOut.taxable (h : HhOut) : Int := sumInts (h.persons.map fun (_, _, t) => t.baseA + t.baseB)

end SkTax
