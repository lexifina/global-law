import LegalProofs.USCaseLaw.Precedent

/-!
# Worked examples, checked on every build

A small record of real decisions, with the model's answers checked by `#guard`:

* Gideon v. Wainwright, 372 U.S. 335 (18 March 1963), overrules Betts v. Brady, 316 U.S. 455 (1 June 1942).
* Lawrence v. Texas, 539 U.S. 558 (26 June 2003), overrules Bowers v. Hardwick, 478 U.S. 186 (30 June 1986).
* A state court of last resort cannot overrule the US Supreme Court, and a state intermediate court cannot overrule
  its own supreme court.
* A district court citing Bowers in 2005 cites a decision the Supreme Court, which binds it, had already overruled.
-/

namespace Legal.USCaseLaw.Examples
open Legal.USCaseLaw

def scotus : Court := { id := 0, system := 0, tier := .last }
def georgiaSup : Court := { id := 1, system := 11, tier := .last }
def georgiaApp : Court := { id := 2, system := 11, tier := .appellate }
def ndTex : Court := { id := 3, system := 0, tier := .trial, circuit := 5 }

def betts : Decision := { id := 0, court := scotus, date := 19420601 }
def gideon : Decision := { id := 1, court := scotus, date := 19630318, cites := [0] }
def bowers : Decision := { id := 2, court := scotus, date := 19860630 }
def lawrence : Decision := { id := 3, court := scotus, date := 20030626, cites := [2] }
/-- A Georgia Supreme Court decision that (wrongly) claims to overrule Bowers. -/
def gaClaim : Decision := { id := 4, court := georgiaSup, date := 19900101, cites := [2] }
/-- A Georgia Court of Appeals decision claiming to overrule a Georgia Supreme Court decision. -/
def gaSupCase : Decision := { id := 5, court := georgiaSup, date := 19800101 }
def gaAppClaim : Decision := { id := 6, court := georgiaApp, date := 19950101, cites := [5] }
/-- A district court in Texas citing Bowers after Lawrence. -/
def txCite : Decision := { id := 7, court := ndTex, date := 20050101, cites := [2] }

def decs : List Decision := [betts, gideon, bowers, lawrence, gaClaim, gaSupCase, gaAppClaim, txCite]

def record : Record :=
  { dec := fun i => (decs.find? (·.id == i)).getD default
    events := [⟨1, 0⟩, ⟨3, 2⟩, ⟨4, 2⟩, ⟨6, 5⟩] }

-- Betts was good law until Gideon, and overruled from the day Gideon was decided.
#guard record.overruledOn 0 19630317 == false
#guard record.overruledOn 0 19630318 == true
-- Bowers: overruled only from Lawrence.
#guard record.overruledOn 2 20030625 == false
#guard record.overruledOn 2 20030626 == true
-- Gideon and Lawrence are valid overrulings; the Georgia claims are not.
#guard record.valid ⟨1, 0⟩ == true
#guard record.valid ⟨3, 2⟩ == true
#guard record.valid ⟨4, 2⟩ == false
#guard record.valid ⟨6, 5⟩ == false
-- The Georgia Supreme Court's claim does not make Bowers overruled in 1990.
#guard record.overruledOn 2 19950101 == false
-- The Texas district court, bound by the Supreme Court, cites Bowers after it was overruled.
#guard (record.findings 7).citesOverruled == [(2, 3)]
#guard (record.findings 4).invalidOverrulings == [2]
#guard (record.findings 6).invalidOverrulings == [5]
-- Gideon cites only earlier decisions.
#guard (record.findings 1).citesLater == []

end Legal.USCaseLaw.Examples
