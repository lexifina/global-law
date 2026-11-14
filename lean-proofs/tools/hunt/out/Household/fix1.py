import sys,io
p=sys.argv[1]
s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)>=1,a
    s=s.replace(a,b)
rep('''credits [{", ".intercalate cs}], net''','''credits [{sep.intercalate cs}], net''')
rep('''  let cs := (o.parts.filter (·.2 > 0)).map (fun c => s!"{c.1} {c.2}")''','''  let cs := (o.parts.filter (·.2 > 0)).map (fun c => s!"{c.1} {c.2}")
  let sep := ", "''')
rep('''{"; ".intercalate (describe f d q)}''','''{semi (describe f d q)}''')
rep('''def showRet (name''','''def semi (l : List String) : String := "; ".intercalate l

def showRet (name''')
rep('''if ch.isEmpty then "deduction lost" else ", ".intercalate ch)''','''if ch.isEmpty then "deduction lost" else semi ch)''')
rep('''elder := if f.elder.isSome && (f.elder.map (·.income < 5200)).getD false then .a else .none,''','''elder := (match f.elder with
      | some e => if e.income < 5200 then Who.a else Who.none
      | none => Who.none),''')
rep('''let outs := (returns f p).map (fun r => (r.2.st, compute r.2))''','''let outs : List (Status × Out) := (returns f p).map (fun r => (r.2.st, compute r.2))''')
rep('''let p0 := (returns g0 (default g0)).flatMap (fun r => (compute r.2).parts)''','''let p0 : List (String × Nat) := (returns g0 (default g0)).flatMap (fun r => (compute r.2).parts)''')
rep('''let p1 := (returns g1 (default g1)).flatMap (fun r => (compute r.2).parts)''','''let p1 : List (String × Nat) := (returns g1 (default g1)).flatMap (fun r => (compute r.2).parts)''')
io.open(p,'w',encoding='utf-8',newline='').write(s)
