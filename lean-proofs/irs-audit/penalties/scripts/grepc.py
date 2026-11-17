import json,re,sys
P=json.load(open('data/parsed.json')); by={o.get('cite'):o for o in P}
o=by[sys.argv[1]]; t=re.sub(r'\s+',' ',open('data/txt/%s.txt'%o['id']).read())
for pat in sys.argv[2:]:
    for m in re.finditer(pat,t,re.I):
        print('...',t[max(0,m.start()-int(400)):m.end()+400],'...\n')
