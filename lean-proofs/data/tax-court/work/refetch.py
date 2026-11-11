import json,urllib.request,time,os,sys,subprocess
UA={"User-Agent":"taxcourt-research-corpus/0.1 (academic dataset build)"}
meta=json.load(open('meta.json'))
for i in sys.argv[1:]:
    u=json.load(urllib.request.urlopen(urllib.request.Request(meta[i]['api_url'],headers=UA),timeout=60))['url']; time.sleep(1)
    pdf=f'pdf/{i}.pdf'
    open(pdf,'wb').write(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=120).read()); time.sleep(1)
    import pymupdf
    d=pymupdf.open(pdf); out=[]
    for n,p in enumerate(d,1): out.append(f'\n=== [page {n}] ===\n'+p.get_text())
    d.close()
    t=''.join(out)
    print(i, round(t.count(' ')/len(t),3), flush=True)
    open(f'../cases/text/{i}.txt','w',encoding='utf-8').write(t)
    os.remove(pdf)
