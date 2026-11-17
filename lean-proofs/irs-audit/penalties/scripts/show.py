import json,re,sys,os
P=json.load(open('data/parsed.json')); by={o.get('cite'):o for o in P}
for c in sys.argv[1:]:
    o=by[c]; t=open('data/lay/%s.txt'%o['id']).read()
    b=t[re.search(r'(?:Judge|JUDGE)\s*:',t).end():] if re.search(r'(?:Judge|JUDGE)\s*:',t) else t
    m=re.search(r'determined',b); print('########',c,o['docket'],o['title']); print(re.sub(r'\n\s*\n','\n',b[max(0,m.start()-50):m.start()+1400]))
