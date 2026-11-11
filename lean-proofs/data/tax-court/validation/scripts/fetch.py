import json,urllib.request,time,os,sys,subprocess
H=r'C:\Users\alany\Documents\tax-formalization-data\taxcourt\validation\holdout'
UA={"User-Agent":"taxcourt-research-corpus/0.1 (academic dataset build)"}
c={x['docketNumberWithSuffix']:x for x in json.load(open(H+r'\search_results.json'))}
pool=sys.argv[1].split(',')
for d in pool:
    x=c[d]; base=os.path.join(H,'raw',d)
    if os.path.exists(base+'.txt'): continue
    api=f"https://public-api-green.dawson.ustaxcourt.gov/public-api/{x['docketNumber']}/{x['docketEntryId']}/public-document-download-url"
    try:
        u=json.load(urllib.request.urlopen(urllib.request.Request(api,headers=UA),timeout=60))['url']; time.sleep(1.1)
        open(base+'.pdf','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=120).read()); time.sleep(1.1)
    except Exception as e:
        print('ERR',d,e,flush=True); continue
    from pypdf import PdfReader
    r=PdfReader(base+'.pdf'); out=[]
    for n,p in enumerate(r.pages,1): out.append(f'\n=== [page {n}] ===\n'+(p.extract_text() or ''))
    open(base+'.txt','w',encoding='utf-8').write(''.join(out))
    print(d,len(r.pages),sum(map(len,out)),flush=True)
