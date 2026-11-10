import TaxCode.Model

/-!
# Drafting checks over the whole of Title 26

Each check is a plain function from the Code to a list of findings, so the same definitions run as a test suite on
every release point (`lake exe taxcheck`) and are what the certificates in `TaxCode/Certs` restate for the kernel.

* **dangling-ref**: an in-force provision links to an identifier that exists nowhere in the US Code.
* **ref-to-inactive**: an in-force provision links to a provision that is repealed, reserved, omitted or renumbered.
* **dangling-word-ref**: an in-force provision refers in words to a subdivision ("paragraph (5)") that does not exist
  where the words point.
* **word-ref-to-inactive**: the same, to a subdivision that is repealed or reserved.
* **duplicate-designation**: two in-force provisions under the same parent carry the same designation.
-/

namespace TaxCode

structure Finding where
  cls : String
  citing : String
  target : String
  detail : String
  deriving Repr, Inhabited

def Finding.key (f : Finding) : String := f.cls ++ "|" ++ f.citing ++ "|" ++ f.target

/-- The deepest ancestor of an identifier that does exist, and how many levels are missing below it. -/
def nearestExisting (c : Code) (id : String) : String × Nat := Id.run do
  let mut parts := (id.splitOn "/").toArray
  let mut missing := 0
  while parts.size > 4 do
    let cand := "/".intercalate parts.toList
    if c.all.contains cand then return (cand, missing)
    parts := parts.pop
    missing := missing + 1
  return ("", missing)

def statusOf (c : Code) (id : String) : Option String :=
  match c.byId.get? id with
  | some _ => some (if c.inForce id then "in-force" else "inactive")
  | none => c.all.get? id

def checkRefs (c : Code) : Array Finding := Id.run do
  let mut out := #[]
  for p in c.provs do
    if !c.inForce p.id then continue
    do
      for r in p.refs do
        match statusOf c r with
        | none =>
          let (anc, miss) := nearestExisting c r
          out := out.push ⟨"dangling-ref", p.id, r, s!"nearest existing: {anc} ({miss} level(s) missing)"⟩
        | some "in-force" => pure ()
        | some s => out := out.push ⟨"ref-to-inactive", p.id, r, s⟩
      for w in p.rel ++ p.secrefs do
        -- a reference is sound if any reading of it lands on a provision in force
        let readings := #[w.target] ++ w.alts
        if w.inline || readings.any (fun t => statusOf c t == some "in-force") then continue
        if let some (word, fits, tgt) := w.levelSlip then
          out := out.push ⟨"wrong-level-word", p.id, w.target, s!"{w.phrase} — no {word} so designated; the {fits} {tgt} exists"⟩
          continue
        let pre := if w.historical then "historical-" else ""
        match readings.findSome? (statusOf c) with
        | none =>
          let (anc, miss) := nearestExisting c w.target
          out := out.push ⟨pre ++ "dangling-word-ref", p.id, w.target, s!"{w.phrase} — nearest existing: {anc} ({miss} level(s) missing)"⟩
        | some s => out := out.push ⟨pre ++ "word-ref-to-inactive", p.id, w.target, s!"{w.phrase} — {s}"⟩
  return out

def checkDuplicates (c : Code) : Array Finding := Id.run do
  let mut seen : Std.HashMap String String := {}
  let mut out := #[]
  for p in c.provs do
    if !c.inForce p.id then continue
    match p.parent, p.num with
    | some par, some n =>
      let k := par ++ "#" ++ n
      match seen.get? k with
      | some first => out := out.push ⟨"duplicate-designation", p.id, first, s!"designation ({n}) used twice under {par}"⟩
      | none => seen := seen.insert k p.id
    | _, _ => pure ()
  return out

/-- Parentheses that do not balance within one provision's own words (ignoring the marker for a link). -/
def parenDepth (s : String) : Int × Int :=
  -- text inside curly quotation marks is quoted (a substitution or a defined term), so it is not counted
  let (d, low, _) := s.foldl (fun (d, low, q) ch =>
    if ch == '“' then (d, low, q + 1) else if ch == '”' then (d, low, q - 1)
    else if q > 0 then (d, low, q)
    else if ch == '(' then (d + 1, low, q) else if ch == ')' then (d - 1, min low (d - 1), q) else (d, low, q)) ((0 : Int), (0 : Int), (0 : Int))
  (d, low)

def checkParens (c : Code) : Array Finding := Id.run do
  let mut out := #[]
  for p in c.provs do
    if !c.inForce p.id || p.text.isEmpty then continue
    let (d, low) := parenDepth p.text
    if d != 0 || low < 0 then
      out := out.push ⟨"unbalanced-parentheses", p.id, p.id, s!"{if d > 0 then s!"{d} unclosed" else if d < 0 then s!"{-d} unopened" else "closed before opened"}"⟩
  return out

def runAll (c : Code) : Array Finding := checkRefs c ++ checkDuplicates c ++ checkParens c

end TaxCode
