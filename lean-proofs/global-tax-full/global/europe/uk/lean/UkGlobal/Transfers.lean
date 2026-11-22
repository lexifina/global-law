import UkGlobal.Pit

/-!
# United Kingdom 2025: inheritance tax on the estate (4300)

Sources: IHTA 1984 s. 7, s. 18 and Sch. 1 at 2025-07-01 (legislation.gov.uk, `uk/law/ihta_*_2025-07-01.html`).
* **Sch. 1** Table of Rates of Tax: "0 | 325,000 | Nil"; "325,000 | ... | 40" per cent.
* **s. 18 (1)**: "A transfer of value is an exempt transfer to the extent that the value transferred is attributable to
  property which becomes comprised in the estate of the transferor's spouse or civil partner".
The entity's inheritances are read as the legacies of one estate (estate-based tax, `estateCharge`); lifetime gifts
are potentially exempt transfers (s. 3A) and are not charged here.
-/

namespace UkGlobal.Transfers
open TaxKernel TaxKernel.Global

def ihtCharge (ts : List Transfer) : Charge :=
  estateCharge "Inheritance tax" (Schedule.flat 4000) {} 325000 [.spouse, .charity] (ts.filter (·.kind == .inheritance))
    "IHTA 1984 s. 7, Sch. 1 (nil-rate band £325,000, 40 %), s. 18 (spouse)"

def charges (g : CanonGlobal) : List Charge :=
  if g.transfers.any (·.kind == .inheritance) then [ihtCharge g.transfers] else []

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 inheritance tax", covers := [.estate],
     run := fun args g prev =>
       charges g }]

def absent : List Absent :=
  []

def notes : List String := ["UK 4300: IHTA 1984, estate of the entity's legacies"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (·.kind == .inheritance) then ["residence nil-rate band (s. 8D), transferable nil-rate band (s. 8A), 36 % charity rate, reliefs (BPR, APR) and taper not modelled; charities taken as exempt (s. 23, not read)"] else [])
  ++ (if g.transfers.any (·.kind == .gift) then ["lifetime gifts: potentially exempt transfers (s. 3A) not charged; chargeable lifetime transfers not modelled"] else [])

#guard (ihtCharge [{ kind := .inheritance, value := 500000, relation := .child }]).due == 70000
#guard (ihtCharge [{ kind := .inheritance, value := 325000, relation := .child }]).due == 0
#guard (ihtCharge [{ kind := .inheritance, value := 900000, relation := .spouse }]).due == 0

end UkGlobal.Transfers
