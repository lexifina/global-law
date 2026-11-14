p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
a="  s.assets.any (fun a => a.id == 0 ∧ (a.holder == .sold ∨ match a.holder with | .person p => !cfg.fam p | _ => false)) ∧"
assert a in s
s=s.replace(a,"  s.assets.any (fun a => a.id == 0 && a.holder != .pship && !isFamHolder cfg s a.holder) ∧")
open(p,'w',encoding='utf-8',newline='').write(s)
