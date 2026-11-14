p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a))
    s=s.replace(a,b)
rep("capGain := Q.capGain - (if j == p ∧ liq then d else 0),","capGain := Q.capGain - (if j == p ∧ liq ∧ ai.isNone then d else 0),")
rep("""              s := modA s i (fun a => { a with basis := a.basis + g })""",
"""              if !liq then s := modA s i (fun a => { a with basis := a.basis + g })
          -- in liquidation his ordinary income is basis in his interest, and so in the property he takes
          if liq then
            if let some i := ai then s := modA s i (fun a => { a with basis := a.basis + d })""")
open(p,'w',encoding='utf-8',newline='').write(s)
