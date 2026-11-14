import sys,io
p=sys.argv[1]
s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
rep('''  let mineInc := ad.wages + ad.invest - p.fsa w
  let o := other w
  let inc := if p.joint then mineInc + (f.ad o).wages + (f.ad o).invest - p.fsa o - p.pre o else mineInc
  ([0, 2000, 7000, 23500] ++ (lines.filter (· < inc)).map (inc - ·)).filter (· ≤ 23500) |>.eraseDups''',
'''  let mineInc := ad.wages + ad.invest
  let o := other w
  let inc := if p.joint then mineInc + (f.ad o).wages + (f.ad o).invest else mineInc
  let lim := if ad.hasPlan then 23500 else 7000
  ([0, 2000, lim] ++ (lines.filter (· < inc)).map (inc - ·)).filter (· ≤ lim) |>.eraseDups''')
rep('''(maxStates : Nat := 400000)''','''(maxStates : Nat := 60000)''')
i=s.index('#eval do\n  let _ ← search "H1 unmarried"')
s=s[:i]+'''#eval do
  let t0 ← IO.monoMsNow
  let _ ← search "H1 unmarried" (h1 false)
  let t1 ← IO.monoMsNow
  IO.println s!"ms {t1 - t0}"

end Legal.USTax.Hunt.Household
'''
io.open(p,'w',encoding='utf-8',newline='').write(s)
