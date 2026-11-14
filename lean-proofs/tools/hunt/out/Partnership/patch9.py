p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a))
    s=s.replace(a,b)
rep("""            -- the distributee bought that share: cost basis, and so much less §731(a)(2) loss
            s := modA s i (fun a => { a with basis := a.basis + d })
            s := modP s p (fun P => { P with capGain := P.capGain + min d loss })""",
"""            -- the distributee bought that share with his interest in other property: gain on what he gave up
            -- (taken in full, the conservative figure) and a cost basis in the share
            s := modA s i (fun a => { a with basis := a.basis + d })
            s := modP s p (fun P => { P with capGain := P.capGain + d })""")
rep("""        if j == p then s := adjust734 s d true""",
"""        if j == p then
          s := adjust734 s d true
          -- if they paid with appreciated property rather than money, they sold that much of it: gain to those
          -- who remain, and a cost basis for the distributee in that part
          if let some i := ai then
            let a := s.assets[i]!
            if a.kind != .inventory ∧ a.fmv > 0 ∧ inside < a.fmv then
              let g := d * (a.fmv - inside) / a.fmv
              let sh := spread (caps s) g
              for k in [0:s.persons.size] do
                if sh[k]! != 0 then
                  s := modP s k (fun Q => { Q with capGain := Q.capGain + sh[k]!, outside := Q.outside + sh[k]! })
              s := modA s i (fun a => { a with basis := a.basis + g })""")
open(p,'w',encoding='utf-8',newline='').write(s)
