import sys; sys.path.insert(0,'.')
import fp, analyze
P=15650
for Bm in (14000,7500):
  Q=Bm; bad=[]; first=None; last=None
  for I in range(60000, 77000):
    s=analyze.scan_one(2026,I,P,Q,Bm,10**9)
    if not s:
      first = first or I; last=I
      d1,C1=fp.g(2026,Q,I,P,Q,Bm,10**9)
      d2,C2=fp.g(2026,d1,I,P,Q,Bm,10**9)
      if not (abs(d2-Q)<1e-9 and d1<Q): bad.append(I)
  print(Bm,'none-band',first,last,'2-cycle fails at',len(bad), bad[:3])
  osc=[I for I in range(60000,77000,1) if analyze.scan_one(2026,I,P,Q,Bm,10**9) and fp.iterative(2026,I,P,Q,Bm,10**9)[0]=='no-convergence']
  print(' FP exists but iterative fails:', osc[0] if osc else None, osc[-1] if osc else None, len(osc))
for Bm in (14000,7500):
  two=[I for I in range(15000,30000) if len(analyze.scan_one(2026,I,P,Bm,Bm,10**9))==2]
  print('floor two-answer I0 range',Bm,two[0],two[-1],len(two))
