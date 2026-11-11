import json,urllib.request,time,os,sys
from pypdf import PdfReader
UA={"User-Agent":"taxcourt-research-corpus/0.1 (academic dataset build)"}
RAW='../cases/raw'
c=json.load(open('candidates.json'))
byd={}
for v in c.values():
    for x in v: byd.setdefault(x['docketNumberWithSuffix'],x)
meta=json.load(open('meta.json')) if os.path.exists('meta.json') else {}
for line in sys.argv[1:]:
    d,i=line.split(':'); x=byd[d]
    txt=f'{RAW}/{i}.txt'
    meta[i]=dict(x,id=i,api_url=f"https://public-api-green.dawson.ustaxcourt.gov/public-api/{x['docketNumber']}/{x['docketEntryId']}/public-document-download-url",
                 dawson_case_url=f"https://dawson.ustaxcourt.gov/case-detail/{x['docketNumber']}")
    if os.path.exists(txt): continue
    u=json.load(urllib.request.urlopen(urllib.request.Request(meta[i]['api_url'],headers=UA),timeout=60))['url']
    time.sleep(1)
    pdf=f'{RAW}/{i}.pdf'
    open(pdf,'wb').write(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=120).read())
    time.sleep(1)
    r=PdfReader(pdf)
    out=[f'\n=== [page {n}] ===\n'+(p.extract_text() or '') for n,p in enumerate(r.pages,1)]
    open(txt,'w',encoding='utf-8').write(''.join(out))
    print(i,len(r.pages),flush=True)
json.dump(meta,open('meta.json','w'),indent=1)
