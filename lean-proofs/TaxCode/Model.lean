import Lean.Data.Json
import Std.Data.HashMap

/-!
# Title 26 as data

The Internal Revenue Code at one OLRC release point, read from `t26.json` (written by `tools/taxcode/parse_uslm.py`
from the official USLM XML), and the identifier of every structural element of every title of the US Code, from
`ids.tsv`. The model keeps what the drafting checks need: the tree of provisions, each one's status, its own words,
the references it makes in hyperlinks, and the references it makes in words ("paragraph (2) of subsection (b)").
-/

namespace TaxCode

open Lean

structure Rel where
  phrase : String
  target : String
  /-- Other readings of the same words (a reference that follows "section 219(g)(5) (without regard to ..."). -/
  alts : Array String
  range : Bool
  /-- The words say the reference is to the law as it stood before ("as in effect on January 1, 1986"). -/
  historical : Bool
  /-- The designation is written inline in the citing provision's own words ("(A) a minister ... or (B) ..."). -/
  inline : Bool
  /-- No reading lands, but the same designations do exist one level up or down: the level word looks wrong. -/
  levelSlip : Option (String × String × String)
  deriving Repr, Inhabited

structure Prov where
  id : String
  kind : String
  parent : Option String
  num : Option String
  status : String
  heading : String
  text : String
  refs : Array String
  rel : Array Rel
  secrefs : Array Rel
  deriving Repr, Inhabited

def Rel.fromJson (j : Json) : Except String Rel := do
  return ⟨← j.getObjValAs? String "phrase", ← j.getObjValAs? String "target",
    (j.getObjValAs? (Array String) "alts").toOption.getD #[], ← j.getObjValAs? Bool "range",
    (j.getObjValAs? Bool "historical").toOption.getD false,
    (j.getObjValAs? Bool "inline").toOption.getD false,
    (do let ls ← j.getObjVal? "levelSlip"
        return (← ls.getObjValAs? String "word", ← ls.getObjValAs? String "fits", ← ls.getObjValAs? String "target")).toOption⟩

def Prov.fromJson (j : Json) : Except String Prov := do
  let parent := (j.getObjValAs? String "parent").toOption
  let num := (j.getObjValAs? String "num").toOption
  let refs ← j.getObjValAs? (Array String) "refs"
  let relJ ← j.getObjValAs? (Array Json) "rel"
  let rel ← relJ.mapM Rel.fromJson
  let secJ ← j.getObjValAs? (Array Json) "secrefs"
  let secrefs ← secJ.mapM Rel.fromJson
  return ⟨← j.getObjValAs? String "id", ← j.getObjValAs? String "kind", parent, num,
    ← j.getObjValAs? String "status", ← j.getObjValAs? String "heading", ← j.getObjValAs? String "text", refs, rel, secrefs⟩

structure Code where
  release : String
  provs : Array Prov
  byId : Std.HashMap String Prov
  /-- Every identifier in every title, with its status. -/
  all : Std.HashMap String String

def Code.inForce (c : Code) (id : String) : Bool :=
  -- a provision is in force if it and every ancestor are
  let rec go (fuel : Nat) (id : String) : Bool :=
    match fuel, c.byId.get? id with
    | 0, _ => true
    | _, none => true
    | n + 1, some p => p.status == "in-force" && (match p.parent with | some q => go n q | none => true)
  go 20 id

def load (t26 ids : System.FilePath) : IO Code := do
  let j ← IO.ofExcept (Json.parse (← IO.FS.readFile t26))
  let release ← IO.ofExcept (j.getObjValAs? String "release")
  let ps ← IO.ofExcept (j.getObjValAs? (Array Json) "provisions")
  let provs ← IO.ofExcept (ps.mapM Prov.fromJson)
  let byId := provs.foldl (fun m p => if m.contains p.id then m else m.insert p.id p) {}
  let mut all : Std.HashMap String String := {}
  for line in (← IO.FS.lines ids) do
    match line.splitOn "\t" with
    | [i, s] => all := if all.contains i then all else all.insert i s
    | _ => pure ()
  return ⟨release, provs, byId, all⟩

end TaxCode
