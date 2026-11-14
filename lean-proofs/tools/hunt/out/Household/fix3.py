import sys,io
p=sys.argv[1]
s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
rep('''  ++ ws.flatMap (fun w => ([0, 3750, 7500, min 7500 care].eraseDups).map (Move.fsa w))''',
'''  ++ ws.flatMap (fun w => (([0, 3750, 7500, min 7500 care]
        ++ (f.kids.filter isQual).map (fun k => min 7500 k.care)).eraseDups).map (Move.fsa w))''')
rep('''  let mut shown := 0
  for (k, (t, q)) in ranked do
    -- a family is listed only if it beats every family that uses a subset of its choices... kept simple: top 14
    if shown < 14 then
      shown := shown + 1
      IO.println s!"  {base - t} better [{k}]: {semi (describe f d q)}"
      if shown ≤ 2 then showPlan f q''',
'''  let mut shown := 0
  for (k, (t, q)) in ranked do
    -- a family is listed only if it beats every family that uses a strict subset of its choices
    let tags := k.splitOn "+"
    let dominated := ranked.any (fun e =>
      let ts := e.1.splitOn "+"
      ts.length < tags.length && ts.all tags.contains && e.2.1 ≤ t)
    if !dominated && shown < 12 then
      shown := shown + 1
      IO.println s!"  {base - t} better [{k}]: {semi (describe f d q)}"
      if shown ≤ 1 then showPlan f q''')
i=s.index('#eval show IO Unit from do')
s=s[:i]+'''/-- Tipped and overtime workers, one child, A's parent in a separate home that A pays for. -/
def h3 (married : Bool) : Facts :=
  { married := married, apart := false,
    a := { adult 52000 false false with tips := 24000 },
    b := { adult 46000 false false with tips := 15000, overtime := 6000 },
    kids := [kid 10 0], elder := some { income := 0, inMainHome := false }, aKeepsElderHome := true,
    marketplace := false, premAdult := 0, premKid := 0, adoption := 0 }

/-- The adults live apart; both children live with B; everyone is on the Exchange. -/
def h4 (married : Bool) : Facts :=
  { married := married, apart := true, a := adult 95000 true false, b := adult 26000 false true,
    kids := [{ kid 5 6000 with withA := false }, { kid 11 0 with withA := false }], elder := none,
    aKeepsElderHome := false, marketplace := true, premAdult := 6600, premKid := 3900, adoption := 0 }

/-- A college student with a job, and a younger child with investment income. -/
def h5 (married : Bool) : Facts :=
  { married := married, apart := false, a := adult 98000 true false, b := adult 72000 true false,
    kids := [{ kid 19 0 with tuition := 9000, earned := 14000 }, { kid 15 0 with unearned := 6000 }], elder := none,
    aKeepsElderHome := false, marketplace := false, premAdult := 0, premKid := 0, adoption := 0 }

/-- An adoption by both adults, final this year, $20,000 of expenses. -/
def h6 (married : Bool) : Facts :=
  { married := married, apart := false, a := adult 38000 false false, b := adult 34000 false false,
    kids := [kid 2 0], elder := none, aKeepsElderHome := false, marketplace := false, premAdult := 0, premKid := 0,
    adoption := 20000 }

def pair (name : String) (h : Bool → Facts) : IO Unit := do
  let u ← search (name ++ " unmarried") (h false)
  let m ← search (name ++ " married") (h true)
  IO.println s!"## {name}: best unmarried {u}, best married {m}; marrying costs {m - u}"

#eval show IO Unit from do
  let t0 ← IO.monoMsNow
  pair "H1" h1
  pair "H2" h2
  pair "H3" h3
  pair "H4" h4
  pair "H5" h5
  pair "H6" h6
  let t1 ← IO.monoMsNow
  cliffs "H1 married" (h1 true) 0 200000
  cliffs "H2 married" (h2 true) 0 200000
  cliffs "H4 unmarried" (h4 false) 0 200000
  let t2 ← IO.monoMsNow
  IO.println s!"search {t1 - t0} ms, cliffs {t2 - t1} ms"

end Legal.USTax.Hunt.Household
'''
io.open(p,'w',encoding='utf-8',newline='').write(s)
