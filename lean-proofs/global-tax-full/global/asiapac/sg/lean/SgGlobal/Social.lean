import SgGlobal.Pit

/-!
# Singapore 2025: CPF (non-tax) and the skills development levy (3000)
(B: IRAS/SkillsFuture tables.) CPF (CPF Act 1953 First Schedule: employer 17 %) is a compulsory saving in the member's
account: OECD Revenue Statistics treat it as non-tax (cited absence of 2200). Skills Development Levy Act 1979 s. 4: 0.25 %
of each employee's monthly remuneration, at least S$2 and at most S$11.25 (on remuneration up to S$4,500): modelled on the
company payroll with the per-employee cap (`sdl`). Foreign worker levy not modelled.
-/

namespace SgGlobal.Social
open TaxKernel TaxKernel.Global

def sdl (bill : Int) (n : Nat) : Int := min (divR .down (25 * bill) BP) (1125 * 12 * (n : Int) / 100)
def sdlF : Family :=
  { name := "3000 skills development levy", covers := [.payroll],
    run := fun _ g _ => if g.entity != .company then [] else
      [charge .payroll "Skills development levy (0.25 %)" g.company.payroll id (fun b => sdl b g.company.employees) (statute := "Skills Development Levy Act 1979 s. 4")] }

def families : List Family := [sdlF]

def absent : List Absent :=
  [{ oecd := .sscEmployer, why := "CPF contributions (CPF Act 1953) are credited to members' accounts: non-tax under OECD Revenue Statistics; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard sdl 1000000 10 == 1350
#guard sdl 100000 10 == 250

end SgGlobal.Social
