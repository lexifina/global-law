import LegalProofs.Amendments

/-!
# Running amending instructions against the US Code

An Act amends the Code with instructions in words: "Section 924(c) of title 18 is amended by striking 'X' and
inserting 'Y'", "in paragraph (2), by adding at the end the following", "by redesignating paragraphs (3) and (4) as
paragraphs (4) and (5)". Read literally, each instruction is a function on text, and it can fail in three ways:

* the struck words are not in the provision named (`failed`): the instruction cannot be executed, and the text is left
  as it was, as `Amendments.lean` treats an amendment of a provision that does not exist (`amendText_no_match`,
  `amendText_missing_target`);
* the words are there more than once and the instruction does not say "each place it appears" (`ambiguous`): every
  place is a possible reading, and two places give two different texts (`two_places_two_results`,
  `distinct_candidates`), so the words alone do not settle the result;
* the words are there exactly once (`unique_determined`): the result is fixed.

"Each place it appears" is a single function of the text (`each_never_ambiguous`).

The section is a list of lines, each with its designation path ("(c)(1)(A)"). An instruction aimed at "(c)(1)" acts on
the lines under that path (`region`); block instructions add, insert, replace, strike or redesignate whole lines. The
runner (`RunAmendmentCheck.lean`) applies each Act's instructions in order to the section as it stood the day before,
classifies every operation, and checks whether the record's next version shows the edit.
-/

namespace Legal.USCaseLaw.AmendmentCheck

abbrev Txt := List Char

/-! ## Finding the struck words -/

/-- Every position at which `pat` begins in `s`, counted from `i` (specification). -/
def occSpec (pat : Txt) : Txt → Nat → List Nat
  | [], i => if pat.isPrefixOf [] then [i] else []
  | c :: cs, i => (if pat.isPrefixOf (c :: cs) then [i] else []) ++ occSpec pat cs (i + 1)

/-- The same, tail-recursive (sections run to half a million characters). -/
def occGo (pat : Txt) : Txt → Nat → List Nat → List Nat
  | [], i, acc => if pat.isPrefixOf [] then i :: acc else acc
  | c :: cs, i, acc => occGo pat cs (i + 1) (if pat.isPrefixOf (c :: cs) then i :: acc else acc)

/-- The positions at which the words occur. -/
def occ (pat s : Txt) : List Nat := (occGo pat s 0 []).reverse

theorem occGo_eq (pat s : Txt) (i : Nat) (acc : List Nat) :
    occGo pat s i acc = (occSpec pat s i).reverse ++ acc := by
  induction s generalizing i acc with
  | nil => by_cases h : pat.isPrefixOf [] <;> simp [occGo, occSpec, h]
  | cons c cs ih =>
    by_cases h : pat.isPrefixOf (c :: cs) <;> simp [occGo, occSpec, h, ih]

theorem occ_eq (pat s : Txt) : occ pat s = occSpec pat s 0 := by
  simp [occ, occGo_eq]

/-- Every position reported is a real occurrence. -/
theorem occSpec_sound (pat : Txt) : ∀ (s : Txt) (k i : Nat), i ∈ occSpec pat s k →
    k ≤ i ∧ pat.isPrefixOf (s.drop (i - k)) = true
  | [], k, i, h => by
    by_cases hp : pat.isPrefixOf [] <;> simp_all [occSpec]
  | c :: cs, k, i, h => by
    simp only [occSpec, List.mem_append] at h
    rcases h with h | h
    · by_cases hp : pat.isPrefixOf (c :: cs)
      · simp [hp] at h; subst h; simp [hp]
      · simp [hp] at h
    · obtain ⟨h1, h2⟩ := occSpec_sound pat cs (k + 1) i h
      refine ⟨by omega, ?_⟩
      have : i - k = (i - (k + 1)) + 1 := by omega
      rw [this]; simpa using h2

theorem occ_sound (pat s : Txt) (i : Nat) (h : i ∈ occ pat s) : pat.isPrefixOf (s.drop i) = true := by
  rw [occ_eq] at h
  simpa using (occSpec_sound pat s 0 i h).2

/-- Does `pat` occur in `s` at all (tail-recursive). -/
def contains (pat : Txt) : Txt → Bool
  | [] => pat.isEmpty
  | c :: cs => pat.isPrefixOf (c :: cs) || contains pat cs

/-! ## Striking and inserting -/

/-- `s` with the `n` characters at `i` replaced by `new`. -/
def splice (s : Txt) (i n : Nat) (new : Txt) : Txt := s.take i ++ new ++ s.drop (i + n)

/-- Headings are printed in small capitals in an Act and in title case in the Code, so an instruction "in the heading"
compares letters without case (`fold`). Folding maps each character to one character, so positions carry over. -/
def key (fold : Bool) (t : Txt) : Txt := if fold then t.map Char.toLower else t

theorem key_length (fold : Bool) (t : Txt) : (key fold t).length = t.length := by
  cases fold <;> simp [key]

def isWordChar (c : Char) : Bool := c.isAlphanum

/-- Words are struck as words: "or" is not struck out of "for", nor "State" out of "States". A match that begins
(ends) with a letter or digit must not have one just before (after) it. -/
def bounded (a : Array Char) (pat : Txt) (i : Nat) : Bool :=
  (!(pat.head?.any isWordChar) || i == 0 || !(isWordChar a[i - 1]!)) &&
  (!(pat.getLast?.any isWordChar) || i + pat.length ≥ a.size || !(isWordChar a[i + pat.length]!))

/-- The places an instruction's words occur in a text, as words. -/
def places (fold : Bool) (pat s : Txt) : List Nat :=
  let a := (key fold s).toArray
  (occ (key fold pat) (key fold s)).filter (bounded a pat)

/-- Keep the occurrences that do not overlap an earlier one, left to right. -/
def nonOverlap (n : Nat) : List Nat → Nat → List Nat
  | [], _ => []
  | p :: ps, m => if m ≤ p then p :: nonOverlap n ps (p + n) else nonOverlap n ps m

/-- Splice at each position, right to left, so earlier positions stay valid. -/
def spliceAll (s : Txt) (ps : List Nat) (n : Nat) (new : Txt) : Txt :=
  ps.reverse.foldl (fun acc p => splice acc p n new) s

/-- "Each place it appears": every non-overlapping occurrence, left to right. -/
def replaceAll (fold : Bool) (pat new s : Txt) : Txt :=
  spliceAll s (nonOverlap pat.length (places fold pat s) 0) pat.length new

/-- What a strike-and-insert does to a text. -/
inductive Result where
  | done (t : Txt)               -- one determined result
  | failed                       -- the words are not there: nothing to do
  | ambiguous (cands : List Txt) -- several places, no "each place": each is a possible result
  deriving Repr, DecidableEq

/-- The text after the instruction: a failed or undetermined instruction leaves it as it was. -/
def Result.effect (s : Txt) : Result → Txt
  | .done t => t
  | .failed => s
  | .ambiguous _ => s

/-- The possible results: one per place the words occur. -/
def candidates (fold : Bool) (pat new s : Txt) : List Txt :=
  (places fold pat s).map (fun i => splice s i pat.length new)

/-- "By striking `pat` and inserting `new`" (an insertion is a strike of its anchor and an insert of the anchor with the
new words; a strike alone inserts nothing). `each`: "each place it appears". `nth`: "the second place it appears"
(0 when the law does not say). -/
def strike (pat new s : Txt) (each : Bool) (nth : Nat := 0) (fold : Bool := false) : Result :=
  if pat.isEmpty then .failed else
  match places fold pat s with
  | [] => .failed
  | [i] => if nth ≤ 1 then .done (splice s i pat.length new) else .failed
  | is =>
    if each then .done (replaceAll fold pat new s)
    else if nth ≥ 1 then
      match is[nth - 1]? with
      | some i => .done (splice s i pat.length new)
      | none => .failed
    else .ambiguous (candidates fold pat new s)

/-! ### The three properties -/

/-- **A unique match gives a determined result**: the text with those words, at that place, replaced. -/
theorem unique_determined (pat new s : Txt) (each : Bool) (fold : Bool) (i : Nat) (hp : pat ≠ [])
    (h : places fold pat s = [i]) :
    strike pat new s each 0 fold = .done (splice s i pat.length new) := by
  cases pat with
  | nil => exact absurd rfl hp
  | cons a as => simp [strike, h]

/-- With a unique match there is exactly one possible result. -/
theorem unique_one_candidate (pat new s : Txt) (fold : Bool) (i : Nat) (h : places fold pat s = [i]) :
    candidates fold pat new s = [splice s i pat.length new] := by
  simp [candidates, h]

/-- **No match leaves the text unchanged**: a failed amendment. -/
theorem no_match_unchanged (pat new s : Txt) (each : Bool) (nth : Nat) (fold : Bool) (h : places fold pat s = []) :
    strike pat new s each nth fold = .failed ∧ (strike pat new s each nth fold).effect s = s := by
  by_cases hp : pat.isEmpty <;> simp [strike, h, hp, Result.effect]

/-- **Two matches, no "each place": two possible results.** Both readings are candidates. -/
theorem two_places_two_results (pat new s : Txt) (fold : Bool) (i j : Nat) (rest : List Nat) (hp : pat ≠ [])
    (h : places fold pat s = i :: j :: rest) :
    strike pat new s false 0 fold = .ambiguous (candidates fold pat new s) ∧
      splice s i pat.length new ∈ candidates fold pat new s ∧ splice s j pat.length new ∈ candidates fold pat new s := by
  refine ⟨?_, ?_, ?_⟩
  · cases pat with
    | nil => exact absurd rfl hp
    | cons a as => simp [strike, h]
  · simp [candidates, h]
  · simp [candidates, h]

theorem prefix_head {p s : Txt} (h : p.isPrefixOf s = true) (hp : p ≠ []) : s.head? = p.head? := by
  cases p with
  | nil => exact absurd rfl hp
  | cons a as =>
    cases s with
    | nil => simp at h
    | cons b bs =>
      simp [List.isPrefixOf] at h
      simp [h.1]

/-- **The two readings differ**: when the struck words occur at `i` and at a later `j`, and the new words begin
differently from the struck ones, striking at `i` and striking at `j` give different texts. (Without that condition
they can coincide: deleting one "a" of "aa".) -/
theorem distinct_candidates (pat new s : Txt) (i j : Nat) (hij : i < j)
    (hi : pat.isPrefixOf (s.drop i) = true) (hp : pat ≠ []) (hn : new ≠ [])
    (hd : new.head? ≠ pat.head?) :
    splice s i pat.length new ≠ splice s j pat.length new := by
  intro heq
  have hlen : i < s.length := by
    rcases Nat.lt_or_ge i s.length with hc | hc
    · exact hc
    · have : s.drop i = [] := List.drop_eq_nil_of_le hc
      rw [this] at hi
      cases pat with
      | nil => exact absurd rfl hp
      | cons a as => simp at hi
  have hti : (s.take i).length = i := by simp; omega
  have h1 : (splice s i pat.length new)[i]? = new.head? := by
    unfold splice
    rw [List.append_assoc, List.getElem?_append_right (by omega), hti, Nat.sub_self]
    cases new with
    | nil => exact absurd rfl hn
    | cons a as => simp
  have h2 : (splice s j pat.length new)[i]? = (s.drop i).head? := by
    unfold splice
    rw [List.append_assoc, List.getElem?_append_left (by simp; omega)]
    simp [hij, List.head?_drop]
  have h3 : (s.drop i).head? = pat.head? := prefix_head hi hp
  rw [heq, h2, h3] at h1
  exact hd h1.symm

/-- The places found without folding are real occurrences, so `distinct_candidates` applies to the places of an
ambiguous instruction. -/
theorem places_sound (pat s : Txt) (i : Nat) (h : i ∈ places false pat s) : pat.isPrefixOf (s.drop i) = true := by
  simp only [places, List.mem_filter] at h
  simpa [key] using occ_sound pat s i h.1

/-- "Each place it appears" never leaves a choice. -/
theorem each_never_ambiguous (pat new s : Txt) (fold : Bool) :
    (∃ t, strike pat new s true 0 fold = .done t) ∨ strike pat new s true 0 fold = .failed := by
  unfold strike
  split
  · exact Or.inr rfl
  · split
    · exact Or.inr rfl
    · simp
    · simp

/-! ### Consistency with `Amendments.lean` -/

open Legal in
/-- A text amendment of provision `k` of a statute: "in `k`, strike `pat` and insert `new`". It replaces the provision
when the instruction determines a result, and otherwise leaves the statute alone. -/
def amendText (k : Key) (pat new : Txt) (each : Bool) (st : Statute) : Statute :=
  match st k with
  | none => (Amendment.replace k "").apply st
  | some u =>
    match strike pat new u.toList each with
    | .done t => (Amendment.replace k (String.ofList t)).apply st
    | _ => st

open Legal in
/-- Aimed at a provision that is not there, the text amendment is `Amendments.lean`'s failed replacement: a no-op. -/
theorem amendText_missing_target (k : Key) (pat new : Txt) (each : Bool) (st : Statute) (h : st k = none) :
    amendText k pat new each st = st := by
  simp [amendText, h, replace_missing_noop st k "" h]

open Legal in
/-- Words not found: the statute after the amendment is the statute before it. -/
theorem amendText_no_match (k : Key) (pat new : Txt) (each : Bool) (st : Statute) (u : String)
    (h : st k = some u) (hm : places false pat u.toList = []) : amendText k pat new each st = st := by
  have := (no_match_unchanged pat new u.toList each 0 false hm).1
  simp [amendText, h, this]

open Legal in
/-- A unique match: the provision is replaced by the one determined text. -/
theorem amendText_unique (k : Key) (pat new : Txt) (each : Bool) (st : Statute) (u : String) (i : Nat)
    (hp : pat ≠ []) (h : st k = some u) (hm : places false pat u.toList = [i]) :
    amendText k pat new each st = (Amendment.replace k (String.ofList (splice u.toList i pat.length new))).apply st := by
  have := unique_determined pat new u.toList each false i hp hm
  simp [amendText, h, this]

/-! ## Sections as designated lines -/

/-- A line of a section: its designation path ("(c)(1)(A)"; "#" for the section heading) and its words. -/
structure Line where
  path : Txt
  text : Txt
  deriving Repr, DecidableEq, Inhabited

/-- Where in the target an instruction acts: all of it, the matter before a child ("in the matter preceding
paragraph (1)"), or after one ("in the matter following subparagraph (C)"). -/
inductive Scope where
  | all
  | preceding (child : Txt)
  | following (child : Txt)
  | heading               -- "in the heading": the target's first line, up to its dash
  | sentence (n : Nat)    -- "in the second sentence" (0: the last)
  deriving Repr, DecidableEq

def isHeading (l : Line) : Bool := l.path == "#".toList

/-- The line belongs to the provision at `target` (the heading only when the target is the heading). -/
def under (target : Txt) (l : Line) : Bool :=
  if target == "#".toList then isHeading l else target.isPrefixOf l.path && !isHeading l

/-- Indices `[a, b)` of the lines an instruction acts on; `none` when the target provision is not in the section. -/
def region (ls : List Line) (target : Txt) (sc : Scope) : Option (Nat × Nat) :=
  let idx := (List.range ls.length).filter (fun k => under target ls[k]!)
  match idx.head?, idx.getLast? with
  | some a, some b =>
    match sc with
    | .all | .sentence _ => some (a, b + 1)
    | .heading => some (a, a + 1)
    | .preceding c =>
      let kids := idx.filter (fun k => (target ++ c).isPrefixOf ls[k]!.path)
      match kids.head? with
      | some k => if a < k then some (a, k) else none
      | none => none
    | .following c =>
      let kids := idx.filter (fun k => (target ++ c).isPrefixOf ls[k]!.path)
      match kids.getLast? with
      | some k => if k < b then some (k + 1, b + 1) else none
      | none => none
  | _, _ => none

def joinLines (ts : List Txt) : Txt := (ts.intersperse ['\n']).flatten

def splitLines (t : Txt) : List Txt := t.splitOn '\n'

/-- Write a region's new text back: line by line when the line count is kept, else all on the first line. -/
def writeBack (ls : List Line) (a b : Nat) (t : Txt) : List Line :=
  let olds := (ls.drop a).take (b - a)
  let parts := splitLines t
  let news :=
    if parts.length == olds.length then (olds.zip parts).map (fun (l, p) => { l with text := p })
    else match olds.head? with
      | some l => [{ l with text := t.map (fun c => if c == '\n' then ' ' else c) }]
      | none => []
  ls.take a ++ news ++ ls.drop b

/-! ## Operations and their outcomes -/

/-- One operation of an instruction, after the parser has read the words. Text operations act on the joined words of
the target; block operations on whole lines. -/
inductive Op where
  | strike (old new : Txt) (each : Bool) (nth : Nat) (fold : Bool) -- strike / insert / strike-and-insert / "each place"
  | strikeEnd (old new : Txt)                        -- "striking the period at the end and inserting ..."
  | range (start through new : Txt)                  -- "striking 'X' and all that follows through 'Y'"
  | toEnd (start new : Txt)                          -- "striking 'X' and all that follows"
  | addText (new : Txt)                              -- "adding at the end the following: '...'" (words)
  | addLines (ls : List Line)                        -- "adding at the end the following:" (provisions)
  | insertLines (sibling : Txt) (after : Bool) (ls : List Line)  -- "inserting after paragraph (2) the following"
  | strikeProv (target : Txt)                        -- "striking paragraph (3)"
  | replaceProv (target : Txt) (ls : List Line)     -- "amended to read as follows", "striking (3) and inserting"
  | redesignate (pairs : List (Txt × Txt))           -- "redesignating (3) and (4) as (4) and (5)"
  | unsupported
  deriving Repr

inductive Outcome where
  | applied      -- executed: one determined result
  | wrongTarget  -- the struck words are not in the provision named, but are elsewhere in the section
  | notFound     -- the struck words are nowhere in the section
  | ambiguous    -- several places, no "each place"
  | noTarget     -- the provision named is not in the section
  | unsupported  -- not modelled
  deriving Repr, DecidableEq, Inhabited

def Outcome.code : Outcome → String
  | .applied => "applied" | .wrongTarget => "wrong_target" | .notFound => "not_found"
  | .ambiguous => "ambiguous" | .noTarget => "no_target" | .unsupported => "unsupported"

/-- The result of one operation: its outcome, the new lines, how many places the words were found in the target,
the window of new text the record should show (empty when there is none to check), and the candidates of an
ambiguous instruction. -/
structure Step where
  outcome : Outcome
  lines : List Line
  nmatch : Nat
  window : Txt
  gone : List Txt := []
  cands : List Txt := []

def anywhere (ls : List Line) (pat : Txt) (fold : Bool := false) : Bool :=
  ls.any (fun l => !(places fold pat l.text).isEmpty)

/-- Ends of sentences: after ". " followed by a capital, an opening parenthesis or a quotation mark. -/
def sentenceEnds : Txt → Nat → List Nat
  | '.' :: ' ' :: c :: cs, i =>
    if c.isUpper || c == '(' || c == '"' then (i + 2) :: sentenceEnds (c :: cs) (i + 2)
    else sentenceEnds (' ' :: c :: cs) (i + 1)
  | _ :: cs, i => sentenceEnds cs (i + 1)
  | [], _ => []

/-- The part of the target's words an instruction acts on: (offset, words). The heading is the first line up to its
dash; a sentence is the span between sentence ends. -/
def focus (sc : Scope) (t : Txt) : Nat × Txt :=
  match sc with
  | .heading =>
    match t.findIdx? (· == '—') with
    | some k => (0, t.take k)
    | none => (0, t)
  | .sentence n =>
    let ends := sentenceEnds t 0
    let starts := 0 :: ends
    let stops := ends ++ [t.length]
    let k := if n == 0 then starts.length - 1 else n - 1
    match starts[k]?, stops[k]? with
    | some x, some y => (x, (t.drop x).take (y - x))
    | _, _ => (0, t)
  | _ => (0, t)

/-- A strike within the focus, put back into the whole text. -/
def strikeIn (sc : Scope) (pat new t : Txt) (each : Bool) (nth : Nat) (fold : Bool) : Result :=
  let (o, f) := focus sc t
  let back := fun (f' : Txt) => t.take o ++ f' ++ t.drop (o + f.length)
  match strike pat new f each nth fold with
  | .done f' => .done (back f')
  | .failed => .failed
  | .ambiguous cs => .ambiguous (cs.map back)

/-- With no focus, `strikeIn` is `strike`. -/
theorem strikeIn_all (pat new t : Txt) (each : Bool) (nth : Nat) (fold : Bool) :
    strikeIn .all pat new t each nth fold = strike pat new t each nth fold := by
  simp only [strikeIn, focus]
  split <;> simp_all

def endsWith (s suf : Txt) : Bool := suf.reverse.isPrefixOf s.reverse

def windowAt (t : Txt) (i n : Nat) : Txt :=
  ((t.drop (i - 20)).take (n + (i - (i - 20)) + 20)).map (fun c => if c == '\n' then ' ' else c)

/-- Lines under `base` for new provisions: the parser gives each new line its path relative to the target. -/
def rebase (base : Txt) (ls : List Line) : List Line := ls.map (fun l => { l with path := base ++ l.path })

/-- A redesignation: lines under `base ++ f` move to `base ++ t`, and their leading designation is renamed. -/
def renameLine (base f t : Txt) (l : Line) : Line :=
  if (base ++ f).isPrefixOf l.path then
    { path := base ++ t ++ l.path.drop (base.length + f.length),
      text := if f.isPrefixOf l.text then t ++ l.text.drop f.length else l.text }
  else l

def failStep (o : Outcome) (ls : List Line) (m : Nat := 0) : Step := ⟨o, ls, m, [], [], []⟩

/-- Text operation on a region, given the region's words `t`. -/
def textStep (ls : List Line) (a b : Nat) (t : Txt) (old : Txt) (r : Result) (fold : Bool := false)
    (sc : Scope := .all) : Step :=
  let (o, f) := focus sc t
  let ps := (places fold old f).map (· + o)
  let m := ps.length
  match r with
  | .done t' =>
    let i := (ps.head?).getD 0
    let n := t'.length + old.length - t.length
    ⟨.applied, writeBack ls a b t', m, windowAt t' i n, [], []⟩
  | .failed => failStep (if anywhere ls old fold then .wrongTarget else .notFound) ls m
  | .ambiguous cs =>
    ⟨.ambiguous, ls, m, [], [], (cs.zip ps).map (fun (c, i) => windowAt c i (c.length + old.length - t.length))⟩

/-- Run one operation on the section's lines. -/
def step (ls : List Line) (target : Txt) (sc : Scope) : Op → Step
  | .strike old new each nth fold =>
    match region ls target sc with
    | none => failStep .noTarget ls
    | some (a, b) =>
      let t := joinLines (((ls.drop a).take (b - a)).map (·.text))
      textStep ls a b t old (strikeIn sc old new t each nth fold) fold sc
  | .strikeEnd old new =>
    match region ls target sc with
    | none => failStep .noTarget ls
    | some (a, b) =>
      let t := joinLines (((ls.drop a).take (b - a)).map (·.text))
      if endsWith t old then
        let t' := t.take (t.length - old.length) ++ new
        ⟨.applied, writeBack ls a b t', 1, windowAt t' (t.length - old.length) new.length, [], []⟩
      else failStep (if ls.any (fun l => endsWith l.text old) then .wrongTarget else .notFound) ls
  | .range start through new =>
    match region ls target sc with
    | none => failStep .noTarget ls
    | some (a, b) =>
      let t := joinLines (((ls.drop a).take (b - a)).map (·.text))
      match occ start t with
      | [] => failStep (if anywhere ls start then .wrongTarget else .notFound) ls
      | [i] =>
        match occ through (t.drop i) with
        | j :: _ =>
          let t' := splice t i (j + through.length) new
          ⟨.applied, writeBack ls a b t', 1, windowAt t' i new.length, [], []⟩
        | [] => failStep (if anywhere ls through then .wrongTarget else .notFound) ls 1
      | is => failStep .ambiguous ls is.length
  | .toEnd start new =>
    match region ls target sc with
    | none => failStep .noTarget ls
    | some (a, b) =>
      let t := joinLines (((ls.drop a).take (b - a)).map (·.text))
      match occ start t with
      | [] => failStep (if anywhere ls start then .wrongTarget else .notFound) ls
      | [i] =>
        let t' := t.take i ++ new
        ⟨.applied, writeBack ls a b t', 1, windowAt t' i new.length, [], []⟩
      | is => failStep .ambiguous ls is.length
  | .addText new =>
    match region ls target sc with
    | none => failStep .noTarget ls
    | some (a, b) =>
      let t := joinLines (((ls.drop a).take (b - a)).map (·.text))
      let t' := t ++ [' '] ++ new
      ⟨.applied, writeBack ls a b t', 1, windowAt t' (t.length + 1) new.length, [], []⟩
  | .addLines nl =>
    match region ls target sc with
    | none => failStep .noTarget ls
    | some (_, b) =>
      let nl' := rebase target nl
      ⟨.applied, ls.take b ++ nl' ++ ls.drop b, 1, [], [], []⟩
  | .insertLines sib after nl =>
    match region ls (target ++ sib) .all with
    | none => failStep .noTarget ls
    | some (a, b) =>
      let nl' := rebase target nl
      let k := if after then b else a
      ⟨.applied, ls.take k ++ nl' ++ ls.drop k, 1, [], [], []⟩
  | .strikeProv p =>
    match region ls (target ++ p) .all with
    | none => failStep .noTarget ls
    | some (a, b) => ⟨.applied, ls.take a ++ ls.drop b, 1, [], ((ls.drop a).take (b - a)).map (·.text), []⟩
  | .replaceProv p nl =>
    match region ls (target ++ p) .all with
    | none => failStep .noTarget ls
    | some (a, b) =>
      let base := (target ++ p).reverse.dropWhile (· != '(') |>.drop 1 |>.reverse
      let nl' := rebase base nl
      ⟨.applied, ls.take a ++ nl' ++ ls.drop b, 1, [], [], []⟩
  | .redesignate pairs =>
    if pairs.all (fun (f, _) => (region ls (target ++ f) .all).isSome) then
      ⟨.applied, ls.map (fun l => pairs.foldl (fun l' (f, t) =>
          if (target ++ f).isPrefixOf l.path then renameLine target f t l else l') l), 1, [], [], []⟩
    else failStep .noTarget ls
  | .unsupported => failStep .unsupported ls

/-- A text operation that does not apply leaves the lines alone. -/
theorem textStep_unchanged (ls : List Line) (a b : Nat) (t old : Txt) (r : Result) (fold : Bool) (sc : Scope)
    (h : (textStep ls a b t old r fold sc).outcome ≠ .applied) : (textStep ls a b t old r fold sc).lines = ls := by
  unfold textStep at *
  rcases hf : focus sc t with ⟨o, f⟩
  cases r <;> simp_all [failStep]

/-- A failed or ambiguous strike leaves the section exactly as it was. -/
theorem step_failed_unchanged (ls : List Line) (target : Txt) (sc : Scope) (old new : Txt) (each : Bool) (nth : Nat)
    (fold : Bool) (ho : (step ls target sc (.strike old new each nth fold)).outcome ≠ .applied) :
    (step ls target sc (.strike old new each nth fold)).lines = ls := by
  simp only [step] at ho ⊢
  split
  · rfl
  · rename_i heq
    rw [heq] at ho
    exact textStep_unchanged _ _ _ _ _ _ _ _ ho

/-! ## Small examples (`#guard` runs at check time) -/

section
private def L (p t : String) : Line := ⟨p.toList, t.toList⟩
private def sec924 : List Line :=
  [L "#" "18 U.S.C. § 924. Penalties",
   L "(a)(1)" "(a)(1) Whoever ... shall be fined under this title, imprisoned not more than five years, or both.",
   L "(c)(1)(A)" "(c)(1)(A) any person who ... uses or carries a firearm, shall—",
   L "(c)(1)(A)(i)" "(i) be sentenced to a term of imprisonment of not less than 5 years;",
   L "(c)(2)" "(2) For purposes of this subsection, the term \"drug trafficking crime\" means any felony."]
private def tgt (s : String) : Txt := s.toList
-- unique: determined
#guard (step sec924 (tgt "(c)(1)") .all (.strike "5 years".toList "7 years".toList false 0 false)).outcome == .applied
-- in (a)(1), not (c): the words are elsewhere in the section
#guard (step sec924 (tgt "(a)(1)") .all (.strike "drug trafficking".toList "x".toList false 0 false)).outcome == .wrongTarget
#guard (step sec924 (tgt "(c)") .all (.strike "machinegun".toList "x".toList false 0 false)).outcome == .notFound
-- "the term" twice in (c)? once only; "of" many times: ambiguous unless each place
#guard (step sec924 (tgt "(c)") .all (.strike "of".toList "OF".toList false 0 false)).outcome == .ambiguous
#guard (step sec924 (tgt "(c)") .all (.strike "of".toList "OF".toList true 0 false)).outcome == .applied
#guard (step sec924 (tgt "(d)") .all (.strike "of".toList "OF".toList true 0 false)).outcome == .noTarget
#guard (step sec924 (tgt "(c)(1)(A)(i)") .all (.strikeEnd ";".toList "; and".toList)).outcome == .applied
#guard occ "aa".toList "aaa".toList == [0, 1]
#guard replaceAll false "of".toList "OF".toList "of of".toList == "OF OF".toList
#guard replaceAll false "--".toList "+".toList "---".toList == "+-".toList
-- words are struck as words
#guard places false "or".toList "for motor or".toList == [10]
#guard (step sec924 (tgt "(c)") .heading (.strike "drug".toList "x".toList false 0 false)).outcome == .wrongTarget
#guard (focus (.sentence 2) "One. Two words. Three.".toList).2 == "Two words. ".toList
-- a heading in small capitals still matches
#guard (step sec924 (tgt "#") .all (.strike "PENALTIES".toList "Penalties and forfeiture".toList false 0 true)).outcome == .applied
end

end Legal.USCaseLaw.AmendmentCheck
