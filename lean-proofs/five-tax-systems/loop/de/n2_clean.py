import de, itertools, json
from de import A,H,run,burden
hs=[]; keys=[]
for wa,wb,age,D,rent in itertools.product(range(0,80001,2500),[0,3000,6672,12000],[40,70],range(0,120001,5000),[0,-10000,-20000]):
    hs.append(H([A(age=age,wages=wa),A(age=age,wages=wb)],married=True,dividends=D,rentalIncome=rent)); keys.append((wa,wb,age,D,rent))
best=[]
for fl in ([],['--kist=900']):
    j=run(hs,*fl); s=run(hs,*fl,'--separate'); n=run(hs,*fl,'--no-32d6'); ns=run(hs,*fl,'--no-32d6','--separate')
    for k,rj,rs,rn,rns in zip(keys,j,s,n,ns):
        g=burden(rj)-burden(rs); g0=burden(rn)-burden(rns)
        best.append((round(g,2),round(g0,2),bool(fl),k))
best.sort(reverse=True)
print('cases',len(best),'joint worse >2:',sum(1 for b in best if b[0]>2),' of which gap <=2 without 32d6:',sum(1 for b in best if b[0]>2 and b[1]<=2))
for b in best[:6]: print(b)
# simplest: no rental, no kist, age 40
c=[b for b in best if b[3][4]==0 and not b[2] and b[3][2]==40]; print('no rental, age 40:', c[:3])
c=[b for b in best if b[3][4]==0 and not b[2] and b[3][2]==70]; print('no rental, age 70:', c[:3])
