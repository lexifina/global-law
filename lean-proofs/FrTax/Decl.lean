import Std.Data.HashMap
import FrTax.Params

/-!
# A return, as the boxes of form 2042 that are filled in

A return is a map from box codes ("1AJ", "0CF", "7UF", ...) to whole numbers: amounts in euros, counts of
children, years of birth, or 1 for a ticked box. An empty box reads as 0.
-/

namespace FrTax

structure Decl where
  year : Nat
  boxes : Std.HashMap String Int

namespace Decl

/-- The value in a box; 0 when empty. -/
def get (d : Decl) (b : String) : Int := d.boxes.getD b 0

/-- Is the box ticked (or non-zero)? -/
def has (d : Decl) (b : String) : Bool := d.get b ≠ 0

/-- Sum of several boxes. -/
def sum (d : Decl) (bs : List String) : Int := bs.foldl (fun a b => a + d.get b) 0

/-- Taxed jointly (art. 6, 1): married (box 0AM) or in a civil partnership (box 0AO). -/
def couple (d : Decl) : Bool := d.has "0AM" || d.has "0AO"

/-- Widowed (box 0AV). -/
def widowed (d : Decl) : Bool := d.has "0AV"

end Decl

/-- The members of the household with their own column on the return: declarant 1, declarant 2 and up to
four dependants (art. 6, 1 and 3). -/
inductive Who | v | c | p1 | p2 | p3 | p4
  deriving Repr, DecidableEq, BEq

def Who.all : List Who := [.v, .c, .p1, .p2, .p3, .p4]

/-- The box of a person in a row of six ("1AJ", "1BJ", "1CJ", "1DJ", "1EJ", "1FJ"): the row's letter
pattern is `1?J` with `?` = A, B, C, D, E, F. -/
def Who.letter : Who → String
  | .v => "A" | .c => "B" | .p1 => "C" | .p2 => "D" | .p3 => "E" | .p4 => "F"

def row (pre suf : String) (w : Who) : String := pre ++ w.letter ++ suf

end FrTax
