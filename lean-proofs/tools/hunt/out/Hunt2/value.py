"""T7: dollar value of the credit-bearing answer vs the Pub. 974 answer, single, 2026, Schedule C only."""
import sys; sys.path.insert(0,'.')
import fp, analyze
def tax(ti):
    br=[(12400,.10),(50400,.12),(105700,.22),(201775,.24),(256225,.32),(640600,.35),(1e18,.37)]
    t=lo=0
    for hi,r in br:
        if ti>lo: t+=(min(ti,hi)-lo)*r
        lo=hi
    return t
P=15650
for Q in (7500,14000):
  for I0 in (17000,20000,24000,28000):
    if I0-Q>=P: continue
    sols=analyze.scan_one(2026,I0,P,Q,Q,10**9)
    out=[]
    for d,C in sols:
        agi=I0-d; ti=max(0,agi-16100); qbi=0.2*min(agi, ti); t=tax(ti-qbi)
        out.append((round(d),round(C),round(t),round(C-t)))
    print(f"Q=B={Q} I0={I0} ({100*I0/P:.0f}% FPL): answers (deduction, credit, income tax, credit-tax) {out}; gain {out[0][3]-out[-1][3] if len(out)==2 else 'n/a'}")
