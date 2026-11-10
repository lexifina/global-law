/-!
# Who owns a trust? Two tests, written separately

The income tax and the estate tax each ask whether a trust is still, in substance, the grantor's. They ask it in
different places, in different words:

* **Income tax, §§671–679 (the grantor trust rules).** The grantor is treated as the owner of a trust, and taxed on its
  income, if the grantor or a nonadverse party holds any of a list of powers (§§673–677).
* **Estate tax, §§2036–2038 and 2042.** Trust property is in the grantor's estate if the grantor kept the income, or a
  power over who enjoys the property, or a power to alter, amend or revoke, or a reversion, or the incidents of
  ownership of a policy on the grantor's life.

This file writes each test from its own provisions, over a description of a single power in a trust instrument: what
it does, who holds it, in what capacity, and whether it is limited by an ascertainable standard. Neither test refers to
the other, and nothing here mentions any planning technique. Whether the two tests disagree, and what follows if they
do, is for the search and the theorems.

Simplifications: the grantor's spouse is treated as the grantor where §672(e) says so; "independent" means an
independent trustee within §674(c) (not related or subordinate to the grantor); state-law questions (whether the
grantor's creditors can reach the trust, which can bring it into the estate) are assumed against inclusion except
where the grantor is entitled to the income.
-/

namespace Legal.USTax.Trusts

/-- What a power lets its holder do. -/
inductive Kind where
  | revoke          -- revest title in the grantor
  | incomeToGrantor -- distribute or accumulate income for the grantor
  | incomeToSpouse  -- distribute or accumulate income for the grantor's spouse
  | premiums        -- apply income to premiums on insurance on the grantor's life
  | substitute      -- reacquire trust property by substituting property of equal value
  | borrow          -- lend to the grantor without adequate interest or security
  | sprinkle        -- decide which beneficiaries receive income or corpus, and how much
  | addBeneficiary  -- add to the class of beneficiaries
  | voteStock       -- vote shares of a corporation the grantor controls
  | reversion       -- a reversion to the grantor worth more than 5% of the trust
  deriving DecidableEq, Repr

inductive Holder where
  | grantor | spouse | nonadverse | adverse | independent
  deriving DecidableEq, Repr

structure Power where
  kind : Kind
  holder : Holder
  fiduciary : Bool      -- held in a fiduciary capacity (as trustee)
  standard : Bool       -- limited by a reasonably definite (ascertainable) standard
  deriving DecidableEq, Repr

/-- §672(a), (b), (e): a power held by the grantor, the spouse, or a party without a substantial adverse interest. -/
def grantorOrNonadverse : Holder → Bool
  | .grantor | .spouse | .nonadverse | .independent => true
  | .adverse => false

/-! ## The income-tax test: is the grantor treated as owner? -/

/-- §§673–677, one power at a time. -/
def ownerPower (p : Power) : Bool :=
  match p.kind with
  | .reversion => true                                            -- §673(a)
  | .revoke => grantorOrNonadverse p.holder                       -- §676(a)
  | .incomeToGrantor | .incomeToSpouse | .premiums =>
    grantorOrNonadverse p.holder                                  -- §677(a)(1)–(3)
  | .substitute | .voteStock => !p.fiduciary                      -- §675(4)(A), (C): nonfiduciary capacity, any person
  | .borrow => grantorOrNonadverse p.holder                       -- §675(2)
  | .addBeneficiary => grantorOrNonadverse p.holder               -- §674(a); excluded from §674(b)(5), (c), (d)
  | .sprinkle =>                                                  -- §674(a), with its exceptions
    grantorOrNonadverse p.holder && !p.standard                   --   §674(b)(5)(A): a definite standard, any holder
      && !(p.holder == .independent)                              --   §674(c): independent trustees

/-! ## The estate-tax test: is the property in the grantor's estate? -/

/-- §§2036–2038, 2042, one power at a time. A power counts only if the grantor holds it (alone or with others). -/
def estatePower (p : Power) : Bool :=
  match p.kind with
  | .reversion => true                                             -- §2037 (reversion > 5%, survivorship assumed)
  | .incomeToGrantor => true                                       -- §2036(a)(1): income retained (creditor access)
  | .revoke => p.holder == .grantor                                -- §2038(a)(1)
  | .sprinkle | .addBeneficiary =>                                 -- §2036(a)(2), §2038: power over enjoyment;
    p.holder == .grantor && !p.standard                            --   an ascertainable standard is not such a power
  | .voteStock => p.holder == .grantor                             -- §2036(b): any capacity
  | .incomeToSpouse | .premiums | .borrow | .substitute => false                 -- not an interest the grantor retained; §2042 needs
                                                                   --   incidents of ownership, which paying premiums is not;
                                                                   --   a power to substitute equal value is not one either
                                                                   --   (Rev. Rul. 2008-22)

/-- A trust instrument is a list of powers. Each test asks whether any power triggers it. -/
abbrev Instrument := List Power

def grantorTrust (i : Instrument) : Bool := i.any ownerPower
def inEstate (i : Instrument) : Bool := i.any estatePower

/-- How the two tests can come out for one instrument. -/
inductive Status where
  | complete        -- neither: a separate taxpayer, out of the estate
  | defective       -- the grantor pays its income tax, but it is out of the estate
  | trap            -- in the estate, but not the grantor's for income tax
  | incomplete      -- both: the grantor's for every purpose
  deriving DecidableEq, Repr

def status (i : Instrument) : Status :=
  match grantorTrust i, inEstate i with
  | false, false => .complete
  | true, false => .defective
  | false, true => .trap
  | true, true => .incomplete

end Legal.USTax.Trusts
