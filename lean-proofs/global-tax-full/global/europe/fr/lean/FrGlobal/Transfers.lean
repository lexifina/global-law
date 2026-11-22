import FrGlobal.Pit

/-!
# France 2025: droits de mutation à titre gratuit (4300)

Sources: the CGI article copies of the 1.x French model (`fr/law/y2025/`; Légifrance blocked): art. 777 (version
2014-12-30), 779 (2013-01-01), 784 (2017-01-01), 796-0 bis (2007-08-22), all in force in 2025.
* **art. 777** Tableau I, ligne directe: "N'excédant pas 8 072 € 5"; "entre 8 072 € et 12 109 € 10"; "entre 12 109 € et
  15 932 € 15"; "entre 15 932 € et 552 324 € 20"; "entre 552 324 € et 902 838 € 30"; "entre 902 838 € et 1 805 677 €
  40"; "Au-delà de 1 805 677 € 45". Tableau III: "Entre frères et sœurs ...: N'excédant pas 24 430 € 35; Supérieure à
  24 430 € 45"; "Entre parents jusqu'au 4e degré inclusivement 55"; "Entre parents au-delà du 4e degré et entre
  personnes non-parentes 60".
* **art. 779**: abattements "100 000 € sur la part de chacun des ascendants et sur la part de chacun des enfants";
  "15 932 € sur la part de chacun des frères ou sœurs"; "7 967 € sur la part de chacun des neveux et nièces".
* **art. 784**: earlier gifts added "à l'exception de celles passées depuis plus de quinze ans".
* **art. 796-0 bis**: "Sont exonérés de droits de mutation par décès le conjoint survivant et le partenaire lié au
  défunt par un pacte civil de solidarité."


FT review (2026-11-21), same CGI copies (`fr/law/y2025/`):
* **art. 777 Tableau II** "Tarif des droits applicables entre époux et entre partenaires liés par un pacte civil de
  solidarité": 5 % to 8 072 €; 10 % to 15 932 €; 15 % to 31 865 €; 20 % to 552 324 €; 30 % to 902 838 €; 40 % to
  1 805 677 €; 45 % above. **art. 790 E** (2013-01-01): "Pour la perception des droits de mutation à titre gratuit entre
  vifs, il est effectué un abattement de 80 724 € sur la part du conjoint du donateur." (Gifts between spouses were left
  untaxed before; art. 796-0 bis exempts the surviving spouse only.)
* **art. 790 B**: "un abattement de 31 865 € sur la part de chacun des petits-enfants" (gifts).
* **art. 788 IV** (2020-08-01): "A défaut d'autre abattement, ... un abattement de 1 594 € est opéré sur chaque part
  successorale" (inheritances by grandchildren, other relatives and non-relatives).
-/

namespace FrGlobal.Transfers
open TaxKernel TaxKernel.Global

def ligneDirecte : Schedule :=
  Schedule.ofList [(0, 500), (8072, 1000), (12109, 1500), (15932, 2000), (552324, 3000), (902838, 4000), (1805677, 4500)]
def freresSoeurs : Schedule := Schedule.ofList [(0, 3500), (24430, 4500)]

/-- art. 777, 779: 0 child or parent (ligne directe, 100 000 €), 1 grandchild (ligne directe; its abatement is not in
art. 779: 0 here), 2 sibling (15 932 €), 3 niece/nephew (7 967 €, 55 %), 4 other relative (55 %), 5 unrelated (60 %). -/
def classIdx (r : Relation) : Nat :=
  match r with
  | .child | .parent => 0 | .grandchild => 1 | .sibling => 2 | .nieceNephew => 3 | .otherRelative => 4 | _ => 5

/-- art. 777 Tableau II: between spouses and PACS partners. -/
def entreEpoux : Schedule :=
  Schedule.ofList [(0, 500), (8072, 1000), (15932, 1500), (31865, 2000), (552324, 3000), (902838, 4000), (1805677, 4500)]

/-- Gifts: class 6 for a spouse (art. 790 E, Tableau II). -/
def classIdxGift (r : Relation) : Nat := if r == .spouse then 6 else classIdx r

/-- art. 788 IV: 1 594 € on a share of an inheritance that has no other abatement (death only). -/
def otherAbatement (death : Bool) : Int := if death then 1594 else 0

def dmtg (death : Bool) : InheritanceTax :=
  { name := if death then "Droits de succession" else "Droits de donation",
    classOf := if death then classIdx else classIdxGift, lookbackYears := 15,
    exemptRelations := if death then [.spouse] else [],
    classes := [{ allowance := 100000, sched := ligneDirecte },
                { allowance := if death then 1594 else 31865, sched := ligneDirecte },
                { allowance := 15932, sched := freresSoeurs }, { allowance := 7967, sched := Schedule.flat 5500 },
                { allowance := otherAbatement death, sched := Schedule.flat 5500 },
                { allowance := otherAbatement death, sched := Schedule.flat 6000 },
                { allowance := 80724, sched := entreEpoux }] }

def charges (g : CanonGlobal) : List Charge :=
  (g.transfers.filter (fun t => t.relation != .charity)).zipIdx.map fun (t, i) =>
    let it := dmtg (t.kind == .inheritance)
    charge .estate it.name t.statutoryValue (fun v => if it.exemptRelations.contains t.relation then 0 else it.taxableOf t (it.priorWithin t + v))
      (fun _ => it.tax t) (event := s!"{if t.kind == .gift then "gift" else "inheritance"} {i + 1}")
      (statute := "CGI art. 777 (Tableaux I-III), 779, 784, 788 IV, 790 B, 790 E, 796-0 bis")

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 droits de mutation à titre gratuit", covers := [.estate],
     run := fun args g prev =>
       charges g }]

def absent : List Absent :=
  []

def notes : List String := ["FR 4300: CGI art. 777, 779, 784, 796-0 bis (local copies)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (·.relation == .charity) then ["gifts and legacies to charities (art. 794-795) not charged"] else [])
  ++ (if g.transfers.any (fun t => t.homeValue ≠ 0 || t.businessValue ≠ 0) then ["Dutreil (art. 787 B) and main-home (art. 764 bis) reliefs not modelled"] else [])
  ++ (if g.transfers.any (·.relation == .grandchild) then ["grandchildren inheriting by representation (art. 779 I) not modelled: 1 594 € (art. 788 IV) applied"] else [])

#guard (dmtg true).tax { kind := .inheritance, value := 300000, relation := .child } == 38194
#guard (dmtg true).tax { kind := .inheritance, value := 300000, relation := .spouse } == 0
#guard (dmtg true).tax { kind := .inheritance, value := 100000, relation := .unrelated } == 59043
#guard (dmtg true).tax { kind := .inheritance, value := 40000, relation := .sibling } == 8423
-- art. 784: a gift of 200 000 to a child 10 years after one of 200 000 bears the tax on the second slice
#guard (dmtg false).tax { kind := .gift, value := 200000, relation := .child, prior := [(200000, 10)] } == 40000
#guard (dmtg false).tax { kind := .gift, value := 200000, relation := .child, prior := [(200000, 16)] } == 18194
-- art. 790 E, Tableau II: a 200 000 € gift to a spouse: 119 276 taxable: 403.6 + 786 + 2 389.95 + 17 482.2
#guard (dmtg false).tax { kind := .gift, value := 200000, relation := .spouse } == 21061
#guard (dmtg true).tax { kind := .inheritance, value := 900000, relation := .spouse } == 0
-- art. 790 B: 31 865 € on a grandchild's gift; art. 788 IV: 1 594 € on other shares of an inheritance
#guard (dmtg false).tax { kind := .gift, value := 31865, relation := .grandchild } == 0
#guard (dmtg true).tax { kind := .inheritance, value := 11594, relation := .unrelated } == 6000
#guard (dmtg false).tax { kind := .gift, value := 10000, relation := .unrelated } == 6000

end FrGlobal.Transfers
