import io
p='LegalProofs/USTax/Hunt/Charity.lean'
s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert a in s, a[:50]
    s=s.replace(a,b)
rep("(fam ||| (1 <<< c)) acc","(fam ||| (1 <<< grp c)) acc")
rep('''def famName (f : Nat) : String :=
  " + ".intercalate ((List.range nChan).filter (fun c => f &&& (1 <<< c) != 0) |>.map chanName)''',
'''def famName (f : Nat) : String :=
  " + ".intercalate ((List.range 8).filter (fun c => f &&& (1 <<< c) != 0) |>.map grpName)''')
rep('''abbrev Path := List Mv''','''abbrev Path := List Mv

/-- Families of plans, by kind of move: results are reported as the best plan in each family. -/
def grp : Nat → Nat
  | 0 | 1 | 2 => 0 | 3 | 4 => 1 | 5 => 2 | 6 => 3 | 7 => 4 | 8 | 9 | 10 => 5 | 11 | 12 => 6 | _ => 7
def grpName : Nat → String
  | 0 => "cash gift" | 1 => "stock gift" | 2 => "SGO" | 3 => "QCD" | 4 => "sell" | 5 => "children's trust"
  | 6 => "CRAT" | _ => "corporate gift"''')
rep('''  IO.println s!"== {label} =="''','''  IO.println s!"== {label} =="
  let t0 ← IO.monoMsNow''')
rep('''  IO.println s!"{sorted.size} families deliver exactly {p.target}; best {topN}:"''',
'''  IO.println s!"{sorted.size} families deliver exactly {p.target} ({(← IO.monoMsNow) - t0} ms); best {topN}:"''')
i=s.index("def giftsOnly"); j=s.index("end Legal.USTax.Hunt.Charity")
s=s[:i]+'''def giftsOnly (c : Nat) : Bool := c < 7
def noSell (c : Nat) : Bool := c != 7
#eval run "A: moderate income, gifts and QCD only" pA (s0 1000000 500000 1000000 0) giftsOnly
#eval run "A: every move but a sale" pA (s0 1000000 500000 1000000 0) noSell

'''+s[j:]
io.open(p,'w',encoding='utf-8',newline='').write(s)
