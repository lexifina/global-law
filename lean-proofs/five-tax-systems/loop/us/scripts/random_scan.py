"""Novel search, part 3: random households (seeded), +$1,000 of one income type; flags burden rises > $1,000 (marginal
rate > 100%) and attributes each to the line that moved most. Output ../runs/random_scan.json."""
import json, random
from collections import Counter
from model import H, run, kid, fica
random.seed(2025)
INC = ["wages","seIncome","taxableInterest","longTermGains","iraDistributions","qualifiedDividends"]
LINES = ["eitc","ctc","actc","odc","cdcc","aotc","llc","saver","ptc","regularTax","amt","seTax","niit","additionalMedicare","belowTheLine","qbiDeduction","deduction","taxableSocialSecurity"]
def rnd():
    f = random.choice(["single","mfj","hoh","mfs"])
    age = random.choice([30,45,60,66,70])
    nk = 0 if f in ("single","mfs") else random.choice([0,1,2,3])
    if f=="hoh" and nk==0: nk=1
    w = random.choice([0,random.randint(0,60000),random.randint(0,250000),random.randint(0,700000)])
    kw = dict(filing=f, head={"age":age,"blind":False}, wages=w, dependents=[kid(random.choice([2,6,12,16,19]), student=True) for _ in range(nk)])
    if f=="mfj": kw["spouse"]={"age":age,"blind":False}; kw["wagesSpouse"]=random.randint(0,w) if w else 0
    if random.random()<.3: kw["seIncome"]=random.randint(0,200000)
    if random.random()<.3: kw["taxableInterest"]=random.randint(0,15000)
    if random.random()<.3: kw["longTermGains"]=random.randint(0,100000)
    if age>=60 and random.random()<.6: kw["socialSecurity"]=random.randint(10000,70000); kw["iraDistributions"]=random.randint(0,80000)
    if random.random()<.3: kw["qualifiedTips"]=min(w//4,random.randint(0,25000))
    if random.random()<.3: kw["qualifiedOvertime"]=min(w//10,random.randint(0,12500))
    if random.random()<.2: kw["carLoanInterest"]=random.randint(0,10000)
    if random.random()<.4: kw["stateLocalTaxes"]=random.randint(0,60000); kw["mortgageInterest"]=random.randint(0,30000)
    if nk and random.random()<.4: kw["childCareExpenses"]=random.randint(0,8000)
    if nk and random.random()<.3: kw["qualifiedTuition"]=[4000]
    if random.random()<.3: kw["iraContributions"]=random.choice([2000,4000,7000]); kw["retirementContributions"]=kw["iraContributions"]
    if random.random()<.3: kw["marketplacePremium"]=kw["benchmarkPremium"]=random.randint(6000,30000)
    if random.random()<.2: kw["hsaContributions"]=random.randint(0,8550)
    return H(**kw)
N=60000
base=[rnd() for _ in range(N)]
cases=[]; meta=[]
for i,c in enumerate(base):
    for inc in INC:
        d=json.loads(json.dumps(c)); d["h"][inc]+=1000
        if inc=="qualifiedDividends": d["h"]["ordinaryDividends"]+=1000
        if inc=="wages" and d["f"] and c["h"]["filing"]=="mfj": pass
        cases.append(d); meta.append((i,inc))
rb=run(base); rp=run(cases)
hits=[]; cause=Counter()
for (i,inc),r in zip(meta,rp):
    b=rb[i]; extra = fica(base[i]["h"]["wages"]+1000)-fica(base[i]["h"]["wages"]) if inc=="wages" else 0
    dlt=r["netTax"]-b["netTax"]+extra
    if dlt>1000:
        mv=max(LINES,key=lambda k: abs(r[k]-b[k]))
        cause[(inc,mv)]+=1
        hits.append(dict(d=dlt,inc=inc,cause=mv,i=i))
hits.sort(key=lambda x:-x["d"])
print("households",N,"perturbations",len(cases),"hits",len(hits))
for k,v in cause.most_common(25): print(k,v)
json.dump(dict(n=N,hits=len(hits),cause={f"{a}|{b}":v for (a,b),v in cause.items()},top=[dict(h,household=base[h["i"]]["h"]) for h in hits[:30]],odd=[dict(h,household=base[h["i"]]["h"]) for h in hits if h["cause"]!="eitc"]),open("../runs/random_scan.json","w"))
