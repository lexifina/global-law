import LegalProofs.USTax.TaxCourt.Basic

/-!
# Alimony: §71 (inclusion) and §215 (deduction) for pre-2019 instruments

§71(a) included alimony or separate maintenance payments in the payee's gross income and §215(a) allowed the payor
the same amount as a deduction (above the line, §62(a)(10)). Pub. L. 115-97 (TCJA) §11051 repealed both for
"any divorce or separation instrument (as defined in section 71(b)(2) as in effect before the date of the enactment of
this Act) executed after December 31, 2018", and for an instrument executed on or before that date and modified after
it "if the modification expressly provides that the amendments made by this section apply to such modification"
(§11051(c)). For every year 2012–2024 the old rules therefore still govern an older instrument.

§71(b)(1), the four requirements of an "alimony or separate maintenance payment" (a cash payment):
* (A) received by (or on behalf of) a spouse under a divorce or separation instrument;
* (B) the instrument does not designate the payment as not includible / not deductible;
* (C) for spouses legally separated under a decree of divorce or separate maintenance, they are not members of the
  same household when the payment is made;
* (D) no liability to make any such payment (or a substitute) after the payee's death.

§71(c): amounts fixed as child support are not alimony (c)(1); amounts reduced on a contingency relating to a child
are treated as child support (c)(2); a short payment is first applied to child support (c)(3). §71(e): no alimony
between spouses filing a joint return. The §71(f) excess front-loading recapture is not modelled.
-/

namespace Legal.USTax.TaxCourt.Extra
open Legal.USTax.TaxCourt

/-- Findings about payments under one instrument for one year. Amounts are whole dollars. -/
structure AlimonyFacts where
  /-- Date the divorce or separation instrument was executed. -/
  executed : Date
  /-- A post-2018 modification that expressly adopts the TCJA §11051 amendments. -/
  modifiedOptIn : Bool := false
  /-- Cash (or cash equivalents) paid in the year to or on behalf of the payee spouse under the instrument. -/
  paid : Int
  /-- (b)(1)(A): payment made under a divorce or separation instrument (§71(b)(2)). -/
  underInstrument : Bool := true
  /-- (b)(1)(B): the instrument does not designate the payment as not includible/deductible. -/
  noNonAlimonyDesignation : Bool := true
  /-- (b)(1)(C): not members of the same household (true when not legally separated under a decree). -/
  notSameHousehold : Bool := true
  /-- (b)(1)(D): no liability to pay after the payee's death. -/
  noPostDeathLiability : Bool := true
  /-- §71(e): spouses filing a joint return with each other. -/
  jointReturn : Bool := false
  /-- §71(c)(1)–(2): child support required for the year (fixed, or the amount of a child-contingent reduction). -/
  childSupport : Int := 0
  deriving Repr, Inhabited

/-- TCJA §11051(c): the old rules no longer apply (instrument executed after 31 Dec 2018, or opted in). -/
def postTcjaInstrument (a : AlimonyFacts) : Bool :=
  decide (a.executed.days > (⟨2018, 12, 31⟩ : Date).days) || a.modifiedOptIn

/-- §71(b)(1)(A)–(D) and §71(e). -/
def meetsAlimonyRequirements (a : AlimonyFacts) : Bool :=
  a.underInstrument && a.noNonAlimonyDesignation && a.notSameHousehold && a.noPostDeathLiability && !a.jointReturn

/-- §71(a) as limited by §71(c): the alimony amount for the year (zero for a post-2018 instrument). A payment short of
the total due is applied first to child support (§71(c)(3)). -/
def alimonyAmount (a : AlimonyFacts) : Int :=
  if postTcjaInstrument a || !meetsAlimonyRequirements a then 0
  else pos (a.paid - pos a.childSupport)

/-- §71(a): included in the payee's gross income. -/
def alimonyIncluded (a : AlimonyFacts) : Int := alimonyAmount a

/-- §215(a): deducted by the payor (the same amount: §215(b)). -/
def alimonyDeduction (a : AlimonyFacts) : Int := alimonyAmount a

theorem alimonyAmount_le_paid (a : AlimonyFacts) (h : 0 ≤ a.paid) : alimonyAmount a ≤ a.paid := by
  unfold alimonyAmount pos; split <;> omega

/-! ## Tests (Pub. 504, "Alimony" — the rules for instruments executed before 2019) -/

private def base : AlimonyFacts := { executed := ⟨2015, 6, 1⟩, paid := 24000 }
-- All four requirements met, no child support: $24,000 included by the payee and deducted by the payor.
#guard alimonyIncluded base = 24000 ∧ alimonyDeduction base = 24000
-- Pub. 504: $2,000 a month of which $500 is designated child support ($6,000 a year): $18,000 alimony.
#guard alimonyAmount { base with childSupport := 6000 } = 18000
-- §71(c)(3): only $5,000 paid against $6,000 child support due: no alimony.
#guard alimonyAmount { base with paid := 5000, childSupport := 6000 } = 0
-- Liability continues after the payee's death: not alimony.
#guard alimonyAmount { base with noPostDeathLiability := false } = 0
-- Designated as not alimony (§71(b)(1)(B)): not alimony.
#guard alimonyAmount { base with noNonAlimonyDesignation := false } = 0
-- Legally separated but sharing a household: not alimony.
#guard alimonyAmount { base with notSameHousehold := false } = 0
-- Joint return (§71(e)): not alimony.
#guard alimonyAmount { base with jointReturn := true } = 0
-- Instrument executed 31 Dec 2018: old rules; 1 Jan 2019: neither included nor deducted.
#guard alimonyAmount { base with executed := ⟨2018, 12, 31⟩ } = 24000
#guard alimonyAmount { base with executed := ⟨2019, 1, 1⟩ } = 0
-- A 2015 instrument modified in 2020 to adopt the TCJA rules: excluded.
#guard alimonyAmount { base with modifiedOptIn := true } = 0

end Legal.USTax.TaxCourt.Extra
