import VuGlobal.Pit

/-!
# Vanuatu 2025: no corporate income tax (1200)

Vanuatu has no income tax act (the 1.x model is in B15-no-pit); companies pay business licence fees (P7).
-/

namespace VuGlobal.Corporate
open TaxKernel TaxKernel.Global

def wht : Wht :=
  { name := "No withholding on payments abroad (no income tax)", rules := [
      { kind := .dividend, rateBp := 0, statute := "Vanuatu levies no income tax (no income tax act; cited absence of the CIT, grade B): nothing is withheld from payments abroad" },
      { kind := .interest, rateBp := 0, statute := "Vanuatu levies no income tax (no income tax act; cited absence of the CIT, grade B): nothing is withheld from payments abroad" },
      { kind := .royalty, rateBp := 0, statute := "Vanuatu levies no income tax (no income tax act; cited absence of the CIT, grade B): nothing is withheld from payments abroad" },
      { kind := .services, rateBp := 0, statute := "Vanuatu levies no income tax (no income tax act; cited absence of the CIT, grade B): nothing is withheld from payments abroad" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       wht.charges g.company }]

def absent : List Absent :=
  [{ oecd := .cit, why := "Vanuatu levies no income tax on companies or individuals (no income tax act; 1.x model B15-no-pit); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 1

end VuGlobal.Corporate
