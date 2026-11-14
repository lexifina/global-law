p='LegalProofs/USTax/Hunt/Residence.lean'
s=open(p,encoding='utf-8',newline='').read()
a="""    (fun (o : Option St) m => o.bind fun s => step p s m) (step p (initSt p b) .sell)"""
b="""    (fun (o : Option St) m => o.bind fun s => step p s m)
    ((step p (initSt p b) .sell).bind fun s => if s.home then some s else step p s .relocate)"""
assert a in s; s=s.replace(a,b)
open(p,'w',encoding='utf-8',newline='').write(s)
