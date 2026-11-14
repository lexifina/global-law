import sys,io
p=sys.argv[1]
s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
rep('''def pair (name''','''/-- Two older adults, no children, A's parent lives with them; both adults are on the Exchange. -/
def h8 (married : Bool) : Facts :=
  { married := married, apart := false, a := { adult 20000 false false with age := 62 },
    b := { adult 80000 false false with age := 60 },
    kids := [], elder := some { income := 0, inMainHome := true }, aKeepsElderHome := false,
    marketplace := true, premAdult := 13200, premKid := 0, adoption := 0 }

def pair (name''')
rep('''  pair "H7" h7
''','''  pair "H7" h7
  pair "H8" h8
''')
io.open(p,'w',encoding='utf-8',newline='').write(s)
