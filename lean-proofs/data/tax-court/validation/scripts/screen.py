import sys,re,os,glob
H=r'~\Documents\tax-formalization-data\taxcourt\validation\holdout\raw'
for f in sys.argv[1:]:
    t=open(os.path.join(H,f+'.txt'),encoding='utf-8').read()
    t=re.sub(r'\s+',' ',t)
    m=re.search(r'(Memo\.|Opinion|OPINION) (\d{4}-\d+)',t); cit=m.group(0) if m else '?'
    m=re.search(r'(determined|determination|issues? (for|to) (decision|decide))',t)
    i=m.start() if m else 0
    print('#####',f,cit,len(t)); print(t[max(0,i-150):i+750]); print()
