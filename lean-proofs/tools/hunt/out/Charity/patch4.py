import io
p='LegalProofs/USTax/Hunt/Charity.lean'
s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b):
    global s
    assert a in s, a[:50]
    s=s.replace(a,b)
rep("let base := [u, 2 * u, 3 * u, p.target, rem, 30 * b0 / 100, 60 * b0 / 100]",
    "let base := [u, 2 * u, 3 * u, p.target, rem, 30 * b0 / 100]")
i=s.index("#eval run"); j=s.index("end Legal.USTax.Hunt.Charity")
s=s[:i]+'''def sel (l : List Nat) (c : Nat) : Bool := l.contains c
#eval run "C: cash, stock to public charity, SGO, QCD" pC (s0 1000000 3000000 1250000 0) (sel [0, 3, 5, 6])
#eval run "C: stock to either, QCD" pC (s0 1000000 3000000 1250000 0) (sel [3, 4, 6])
#eval run "C: stock, QCD, children's trust" pC (s0 1000000 3000000 1250000 0) (sel [3, 6, 8, 9, 10])
#eval run "F: cash, stock to public charity, SGO, QCD" pF (s0 1000000 3000000 1250000 0) (sel [0, 3, 5, 6])
#eval run "F: stock to either, no QCD" pF (s0 1000000 3000000 1250000 0) (sel [3, 4])
#eval run "F: stock, children's trust" pF (s0 1000000 3000000 1250000 0) (sel [3, 8, 9, 10])

'''+s[j:]
io.open(p,'w',encoding='utf-8',newline='').write(s)
