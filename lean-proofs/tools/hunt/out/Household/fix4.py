import sys,io
p=sys.argv[1]
s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
rep('''def cliffs (name : String) (f : Facts) (lo hi : Nat) : IO Unit := do
  let net (w : Nat) : Int :=
    let g := { f with a := { f.a with wages := w } }
    total g (default g)''','''def cliffs (name : String) (f : Facts) (lo hi : Nat) (tweak : Plan → Plan := id) : IO Unit := do
  let net (w : Nat) : Int :=
    let g := { f with a := { f.a with wages := w } }
    total g (tweak (default g))''')
rep('''(returns g0 (default g0))''','''(returns g0 (tweak (default g0)))''')
rep('''(returns g1 (default g1))''','''(returns g1 (tweak (default g1)))''')
rep('''  let big := found.qsort (fun x y => x.2.1 > y.2.1)
  IO.println s!"== cliffs, {name}: {found.size} points where $1 more of A's wages costs $2 or more"
  for (x, j, why) in big.toList.take 10 do
    IO.println s!"  at A wages ${x}: +${j} ({why})"''','''  IO.println s!"== cliffs, {name}: {found.size} points where $1 more of A's wages costs $2 or more"
  -- grouped by provision and size: count, first and last wage
  let mut groups : Array (String × Int × Nat × Nat × Nat) := #[]
  for (x, j, why) in found do
    match groups.findIdx? (fun g => g.1 == why && g.2.1 == j) with
    | some i => groups := groups.modify i (fun g => (g.1, g.2.1, g.2.2.1 + 1, g.2.2.2.1, x))
    | none => groups := groups.push (why, j, 1, x, x)
  for (why, j, n, first, last) in (groups.qsort (fun x y => x.2.1 > y.2.1)).toList.take 12 do
    IO.println s!"  +${j} ({why}): {n} point(s), A wages ${first}" ++ (if n > 1 then s!" to ${last}" else "")''')
rep('''a := adult 95000 true false, b := adult 26000 false true,''','''a := adult 95000 true false, b := adult 40000 false true,''')
rep('''def pair (name''','''/-- A's parent lives with them; A earns less; everyone but the parent is on the Exchange. -/
def h7 (married : Bool) : Facts :=
  { married := married, apart := false, a := adult 30000 false false, b := adult 68000 false false,
    kids := [kid 6 0], elder := some { income := 0, inMainHome := true }, aKeepsElderHome := false,
    marketplace := true, premAdult := 6600, premKid := 3900, adoption := 0 }

def pair (name''')
rep('''  pair "H6" h6
''','''  pair "H6" h6
  pair "H7" h7
''')
rep('''  cliffs "H4 unmarried" (h4 false) 0 200000
''','''  cliffs "H4 unmarried" (h4 false) 0 200000
  cliffs "H3 unmarried" (h3 false) 0 200000
  cliffs "H1 married, each spouse puts $2,000 in a Roth IRA" (h1 true) 30000 200000
    (fun p => { p with rothA := 2000, rothB := 2000 })
''')
io.open(p,'w',encoding='utf-8',newline='').write(s)
