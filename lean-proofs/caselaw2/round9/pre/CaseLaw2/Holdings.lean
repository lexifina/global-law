import LegalProofs.CaseLaw2.Courts

/-!
# caselaw-lean-2: decisions and holdings

A decision is a node with its court, date, unit, bench, publication and form (`decisions2.tsv`), plus the optional
`decisions2_extra.tsv` columns (Tax Court appeal venue for *Golsen*, Texas TRAP 41.3 transferor). Unknown fields are
`none`.

A holding is one issue of one decision (doctrine §8). Issue keys are interned to `Nat`; issue `0` is the anonymous
issue ⊤ that stands for the whole decision when no holding has been extracted (§8.2). Only majority, per curiam and
*Marks*-backed plurality holdings carry binding force (F6, HD1); `role = none` is the anonymous issue.
-/

namespace CaseLaw2

structure Decision where
  id : Nat
  court : Nat
  date : Date
  unit : Option Nat := none
  bench : Option Bench := none
  pub : Option Publication := none
  form : Option Form := none
  /-- *Golsen* (F12): the circuit a Tax Court case is appealable to. -/
  appealVenue : Option Nat := none
  /-- TRAP 41.3: the court a Texas appeal was transferred from. -/
  transferFrom : Option Nat := none
  /-- H4: the adoption notation of a commission or commissioner opinion (`commission.tsv`). -/
  commission : Option Notation := none
  deriving Repr, DecidableEq, Inhabited

/-- The anonymous issue. -/
def anonIssue : Nat := 0

structure Holding where
  id : Nat
  node : Nat
  /-- Interned issue key; `0` = anonymous ⊤. -/
  issue : Nat
  domain : Option Domain := none
  role : Option Role := none
  answer : Option Answer := none
  /-- A `marks.tsv` row gives this (node, issue) a narrowest-ground holding. -/
  marks : Bool := false
  deriving Repr, DecidableEq, Inhabited

/-- The anonymous holding of a decision. -/
def Holding.anon (x : Decision) : Holding := { id := 0, node := x.id, issue := anonIssue }

end CaseLaw2
