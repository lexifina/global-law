import json,urllib.request,time,os,sys
from pypdf import PdfReader
UA={"User-Agent":"taxcourt-research-corpus/0.1 (academic dataset build)"}
PICK="""9875-18S tcsumm-2021-26
22530-17S tcsumm-2020-25
1860-18S tcsumm-2020-9
14996-17S tcsumm-2019-23
4951-23 tcmemo-2025-132
13403-23 tcmemo-2025-31
19487-22 tcmemo-2024-20
4044-24 tcmemo-2025-116
13479-20S tcsumm-2023-35
18270-17S tcsumm-2022-17
20779-17S tcsumm-2021-41
18832-18 tcmemo-2023-2
11907-20S tcsumm-2024-22
8246-17S tcsumm-2021-37
13352-15S tcsumm-2019-29
5733-19S tcsumm-2021-31
12027-22S tcsumm-2024-10
26962-21S tcsumm-2024-4
27901-21S tcsumm-2023-13
3842-18S tcsumm-2020-14
14862-18S tcsumm-2020-5
15766-23 tcmemo-2025-23
15210-22 tcmemo-2023-141
1239-23 tcmemo-2024-67
14225-22S tcsumm-2024-11
1587-18S tcsumm-2022-23
17307-19S tcsumm-2021-9
8129-17S tcsumm-2021-2
5238-22 tcmemo-2024-23
34218-21 tcmemo-2023-37
7107-17 tcmemo-2019-41
19351-18S tcsumm-2020-18
22364-22S tcsumm-2024-24
26170-22S tcsumm-2024-15
11819-17 tcmemo-2019-83
4491-19 tcmemo-2020-101
12283-20S tcsumm-2023-1
21655-17S tcsumm-2019-24
8579-22S tcsumm-2025-3
13942-23S tcsumm-2024-13
10233-21S tcsumm-2023-9
20914-21S tcsumm-2023-3
18079-17 tcmemo-2023-56
7453-19 tcmemo-2022-77
9946-23S tcsumm-2024-19
7862-18S tcsumm-2019-8
8987-20S tcsumm-2023-5
6928-21S tcsumm-2023-25
20912-19S tcsumm-2022-10"""
c=json.load(open('candidates.json'))
byd={}
for v in c.values():
    for x in v: byd.setdefault(x['docketNumberWithSuffix'],x)
meta={}
if os.path.exists('meta.json'): meta=json.load(open('meta.json'))
for line in PICK.split('\n'):
    d,i=line.split(); x=byd[d]
    txt=f'../cases/text/{i}.txt'
    meta[i]=dict(x,id=i,api_url=f"https://public-api-green.dawson.ustaxcourt.gov/public-api/{x['docketNumber']}/{x['docketEntryId']}/public-document-download-url",
                 dawson_case_url=f"https://dawson.ustaxcourt.gov/case-detail/{x['docketNumber']}")
    if os.path.exists(txt): continue
    u=json.load(urllib.request.urlopen(urllib.request.Request(meta[i]['api_url'],headers=UA),timeout=60))['url']
    time.sleep(1)
    pdf=f'pdf/{i}.pdf'
    open(pdf,'wb').write(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=120).read())
    time.sleep(1)
    r=PdfReader(pdf)
    out=[]
    for n,p in enumerate(r.pages,1): out.append(f'\n=== [page {n}] ===\n'+(p.extract_text() or ''))
    open(txt,'w',encoding='utf-8').write(''.join(out))
    os.remove(pdf)
    print(i,len(r.pages),sum(len(o) for o in out),flush=True)
json.dump(meta,open('meta.json','w'),indent=1)
