p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
a="    !mine ∨ (match a.holder with | .person p => cfg.fam p | _ => false))"
assert a in s
s=s.replace(a,"    !mine || (match a.holder with | .person p => cfg.fam p | _ => false))")
open(p,'w',encoding='utf-8',newline='').write(s)
