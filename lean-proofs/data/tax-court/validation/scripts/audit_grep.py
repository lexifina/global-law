import sys,re,os
B=r'~\Documents\tax-formalization-data\taxcourt\cases\text'
cid=sys.argv[1]; W=int(os.environ.get('W','90'))
t=open(os.path.join(B,cid+'.txt'),encoding='utf-8',errors='replace').read()
t=re.sub(r'\s+',' ',t)
for term in sys.argv[2:]:
    ms=[m.start() for m in re.finditer(re.escape(term),t,re.I)]
    print(f'== {term!r}: {len(ms)} hits')
    for p in ms[:2]:
        print('   ...'+t[max(0,p-W):p+len(term)+W]+'...')
