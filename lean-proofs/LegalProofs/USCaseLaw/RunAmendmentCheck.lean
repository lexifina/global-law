import LegalProofs.USCaseLaw.AmendmentCheck

/-!
# Runner: execute Acts' amending instructions against the US Code record

    lake env lean --run LegalProofs/USCaseLaw/RunAmendmentCheck.lean <in.tsv> <out.tsv>

Each input row is one (Act, section): an id, the section's lines the day before the Act (`path US text`, separated by
RS), the record's lines after it, and the Act's operations on the section in enacted order (separated by GS; fields of
an operation separated by FS): id, kind, target path, scope (`all`/`pre`/`fol`), scope child, nth, each, three word
fields, new lines, redesignation pairs. Python only parses the Act and the record; every outcome below is computed here
by `AmendmentCheck.step`.

Each output row: group id, operation id, outcome, places found in the target, whether the record's next version shows
the edit (1/0, -1 when there is nothing to check), for an ambiguous one the 1-based candidate the record shows (0 if
none), and whether the candidates differ. One `G` row per group: whether the replayed section equals the record's.
-/

open Legal.USCaseLaw.AmendmentCheck

def sep (c : Nat) : String := String.singleton (Char.ofNat c)

def parseLines (s : String) : List Line :=
  if s.isEmpty then [] else
  (s.splitOn (sep 30)).map fun it =>
    match it.splitOn (sep 31) with
    | [p, t] => ⟨p.toList, t.toList⟩
    | _ => ⟨[], it.toList⟩

def parsePairs (s : String) : List (Txt × Txt) :=
  if s.isEmpty then [] else
  (s.splitOn (sep 30)).filterMap fun it =>
    match it.splitOn (sep 31) with
    | [a, b] => some (a.toList, b.toList)
    | _ => none

def parseOp (f : Array String) : Op :=
  let a := f[7]!.toList
  let b := f[8]!.toList
  let c := f[9]!.toList
  let nl := parseLines f[10]!
  match f[1]! with
  | "S" => .strike a b (f[6]! == "1") f[5]!.toNat! (f[12]! == "1")
  | "E" => .strikeEnd a b
  | "R" => .range a b c
  | "T" => .toEnd a b
  | "A" => .addText a
  | "B" => .addLines nl
  | "IA" => .insertLines a true nl
  | "IB" => .insertLines a false nl
  | "D" => .strikeProv a
  | "P" => .replaceProv a nl
  | "M" => .redesignate (parsePairs f[11]!)
  | _ => .unsupported

def parseScope (k o : String) : Scope :=
  match k with
  | "pre" => .preceding o.toList
  | "fol" => .following o.toList
  | "head" => .heading
  | "sent" => .sentence o.toNat!
  | _ => .all

def flat (ls : List Line) : Txt := joinLines (ls.map (·.text)) |>.map (fun c => if c == '\n' then ' ' else c)

/-- For comparing with the record: spaces dropped and case folded (the Code prints headings in sentence case). -/
def squeeze (t : Txt) : Txt := (t.filter (fun c => c != ' ')).map Char.toLower

def key60 (t : Txt) : Txt := t.take 60

/-- Does the record's version after the Act show this operation's edit? -/
def shows (after : List Line) (afterT : Txt) (op : Op) (target : Txt) (s : Step) : Int :=
  let b (x : Bool) : Int := if x then 1 else 0
  match op with
  | .strike .. | .strikeEnd .. | .range .. | .toEnd .. | .addText .. =>
    if s.window.isEmpty then -1 else b (contains (squeeze s.window) (squeeze afterT))
  | .addLines nl | .insertLines _ _ nl | .replaceProv _ nl =>
    let ks := (nl.map (fun l => squeeze (key60 l.text))).filter (fun k => k.length ≥ 8)
    if ks.isEmpty then -1 else b (ks.all (fun k => contains k (squeeze afterT)))
  | .strikeProv _ =>
    let ks := (s.gone.map (fun t => squeeze (key60 t))).filter (fun k => k.length ≥ 30)
    if ks.isEmpty then -1 else b (ks.all (fun k => !contains k (squeeze afterT)))
  | .redesignate pairs => b (pairs.all (fun (_, t) => (region after (target ++ t) .all).isSome))
  | .unsupported => -1

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, out] =>
    let s ← IO.FS.readFile inp
    let o ← IO.FS.Handle.mk out .write
    let mut nops := 0
    let mut ngroups := 0
    let mut same := 0
    for l in s.splitOn "\n" do
      if l.isEmpty then continue
      let f := (l.splitOn "\t").toArray
      if f.size < 4 then continue
      let gid := f[0]!
      let before := parseLines f[1]!
      let after := parseLines f[2]!
      let afterT := squeeze (flat after)
      let ops := if f[3]!.isEmpty then [] else f[3]!.splitOn (sep 29)
      let mut cur := before
      for os in ops do
        let g := (os.splitOn (sep 28)).toArray
        if g.size < 13 then continue
        let op := parseOp g
        let target := g[2]!.toList
        let st := step cur target (parseScope g[3]! g[4]!) op
        let rec_ := if st.outcome == .applied then shows after afterT op target st else -1
        let ci := (st.cands.zip (List.range st.cands.length)).find? (fun (w, _) => contains (squeeze w) afterT)
        let differ := match st.cands with
          | c1 :: c2 :: _ => if c1 != c2 then 1 else 0
          | _ => 0
        o.putStrLn s!"{gid}\t{g[0]!}\t{st.outcome.code}\t{st.nmatch}\t{rec_}\t{(ci.map (·.2 + 1)).getD 0}\t{differ}"
        cur := st.lines
        nops := nops + 1
      let eq := squeeze (flat cur) == afterT
      if eq then same := same + 1
      o.putStrLn s!"{gid}\tG\t{if eq then 1 else 0}"
      ngroups := ngroups + 1
    IO.println s!"{ngroups} (Act, section) groups, {nops} operations; replay equals the record in {same} groups"
    return 0
  | _ => IO.eprintln "usage: RunAmendmentCheck.lean <in.tsv> <out.tsv>"; return 2
