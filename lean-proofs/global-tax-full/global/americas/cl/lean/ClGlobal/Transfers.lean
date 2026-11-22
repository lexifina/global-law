import ClGlobal.Pit

/-!
# Chile 2025: 4300 herencias, asignaciones y donaciones (pilot, unchanged)

**Ley 16.271** (idNorma 28367, version 2025-07-01; last note D.O. 26.10.1998): art. 2 scale in UTA (1 % to 80, 2,5 % to
160, 5 % to 320, 7,5 % to 480, 10 % to 640, 15 % to 800, 20 % to 1.200, 25 % above), exempt 50 UTA for inheritances of
the spouse, ascendants and descendants and 5 UTA for donations to them; collateral relatives of the 2nd-4th degree 5
UTA and "la escala … recargada en un 20%", 40 % for more distant or no kinship; art. 23: repeated donations from the
same donor are summed and the tax already paid deducted (no time limit).
-/

namespace ClGlobal.Transfers
open TaxKernel TaxKernel.Global ClGlobal

def scale (pct : Int) : Schedule :=
  Schedule.ofList ([(0, 100), (80, 250), (160, 500), (320, 750), (480, 1000), (640, 1500), (800, 2000), (1200, 2500)].map
    fun (u, r) => (u * uta, r * pct / 100))

def htax (pct : Int) (exemptUTA : Int) : TaxClass := { allowance := exemptUTA * uta, sched := scale pct }

def hclass (r : Relation) : Nat :=
  match r with
  | .spouse | .child | .grandchild | .parent => 0
  | .sibling | .nieceNephew => 1
  | _ => 2

def asignaciones : InheritanceTax :=
  { name := "Impuesto a las asignaciones (herencias)", classOf := hclass,
    classes := [htax 100 50, htax 120 5, htax 140 0] }

def donaciones : InheritanceTax :=
  { name := "Impuesto a las donaciones", classOf := hclass, lookbackYears := 10000,
    classes := [htax 100 5, htax 120 5, htax 140 0] }

def herencias : Family :=
  { name := "4300 herencias y donaciones", covers := [.estate],
    run := fun _ g _ =>
      let ts := g.transfers.filter (·.relation != .charity)
      asignaciones.charges (ts.filter (·.kind == .inheritance)) "Ley 16.271 art. 2 (scale in UTA, exemptions, surcharges), art. 3"
      ++ donaciones.charges (ts.filter (·.kind == .gift)) "Ley 16.271 art. 2, art. 23 (repeated donations summed, tax paid deducted)" }

def families : List Family := [herencias]
def absent : List Absent := []
def notes : List String := []
def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (·.relation == .charity) then ["transfers to charities: Ley 16.271 art. 18 exemptions not modelled"] else [])

#guard asignaciones.tax { kind := .inheritance, value := 100 * uta, relation := .child } == 50 * uta / 100
#guard asignaciones.tax { kind := .inheritance, value := 100 * uta, relation := .sibling }
        == (80 * uta * 120 + 15 * uta * 300) / 10000
#guard donaciones.tax { kind := .gift, value := 100 * uta, relation := .child, prior := [(100 * uta, 3)] }
        == (80 * uta * 100 + 80 * uta * 250 + 35 * uta * 500) / 10000 - (80 * uta * 100 + 15 * uta * 250) / 10000

end ClGlobal.Transfers
