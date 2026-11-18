"""Candidate: separate returns put the children on the lower earner's return, so the other spouse's income escapes
the §24(b) phase-out (threshold $400,000 joint, $200,000 'any other case', §24(h)(3)). Grid of couples, 1-4 children."""
import json
from model import H, run, kid
rows=[]; cases=[]
for n in (1,2,3,4):
    ks=[kid(5+i) for i in range(n)]
    for a in range(100000,800001,5000):
        for b in range(0,a+1,5000):
            cases += [H(filing="mfj",wages=a+b,wagesSpouse=b,dependents=ks),
                      H(filing="mfs",wages=a,facts={"electItemize":False}),
                      H(filing="mfs",wages=b,dependents=ks,facts={"electItemize":False})]
            rows.append((n,a,b))
rs=run(cases)
best={}; cnt={}
for i,(n,a,b) in enumerate(rows):
    j,x,y=rs[3*i:3*i+3]
    g=j["netTax"]-(x["netTax"]+y["netTax"])
    if g>0:
        cnt[n]=cnt.get(n,0)+1
        if g>best.get(n,(0,))[0]: best[n]=(g,a,b,j["ctc"],y["ctc"],j["netTax"],x["netTax"]+y["netTax"])
print("wins per n:",cnt); print("best:",best)
json.dump(dict(wins=cnt,best=best),open("../runs/ctc_mfs.json","w"))
