import Std.Data.HashMap

/-!
# Exec: hash indexes, with their specification

`index key l` groups a list by key into a hash map. The one lemma every Exec equivalence rests on: looking a key up
in the index gives exactly the list filter the Spec uses (`index_getD`).
-/

namespace CaseLaw2.Exec
open Std

def index {α K} [BEq K] [Hashable K] (key : α → K) (l : List α) : HashMap K (List α) :=
  l.foldr (fun x m => m.insert (key x) (x :: m.getD (key x) [])) {}

theorem index_getD {α K} [BEq K] [Hashable K] [LawfulBEq K] [LawfulHashable K] (key : α → K) (l : List α) (k : K) :
    (index key l).getD k [] = l.filter (fun x => key x == k) := by
  induction l generalizing k with
  | nil => simp [index]
  | cons x l ih =>
    unfold index at ih ⊢
    simp only [List.foldr_cons]
    rw [HashMap.getD_insert]
    by_cases h : key x = k
    · subst h; simp [ih]
    · have : (key x == k) = false := by simpa using h
      simp [this, ih]

end CaseLaw2.Exec
