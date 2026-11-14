p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a))
    s=s.replace(a,b)
rep("  let hotBefore := hotShares s none\n","")
rep("  let a? : Option Asset := ai.map (fun i => s.assets[i]!)\n","  let hotBefore := hotShares s none\n  let a? : Option Asset := ai.map (fun i => s.assets[i]!)\n")
rep("""          if s.assets[i]!.kind == .inventory then s := modA s i (fun a => { a with basis := a.basis + d })""",
"""          if s.assets[i]!.kind == .inventory then
            -- the distributee bought that share: cost basis, and so much less §731(a)(2) loss
            s := modA s i (fun a => { a with basis := a.basis + d })
            s := modP s p (fun P => { P with capGain := P.capGain + min d loss })""")
rep("def showMove : Move → String","def showMove (aname : Nat → String) : Move → String")
rep("(h.path.map showMove)","(h.path.map (showMove (fun i => aname ((h.st.assets[i]?.map (·.id)).getD i))))")
open(p,'w',encoding='utf-8',newline='').write(s)
