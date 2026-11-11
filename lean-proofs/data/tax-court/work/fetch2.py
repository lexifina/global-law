import json,os,subprocess,sys
c=json.load(open('candidates2.json'))
byd={}
for v in c.values():
    for x in v: byd.setdefault(x['docketNumberWithSuffix'],x)
PICK=[("11326-16S","tcsumm-2019-20"),("18272-17S","tcsumm-2022-14"),("33689-21S","tcsumm-2024-12"),("22316-21S","tcsumm-2023-6"),("12809-18S","tcsumm-2019-33"),("3154-19S","tcsumm-2021-6"),("22810-21S","tcsumm-2024-3")]
meta=json.load(open('meta.json'))
new=[]
for d,i in PICK:
    x=byd[d]
    meta[i]=dict(x,id=i,api_url=f"https://public-api-green.dawson.ustaxcourt.gov/public-api/{x['docketNumber']}/{x['docketEntryId']}/public-document-download-url",dawson_case_url=f"https://dawson.ustaxcourt.gov/case-detail/{x['docketNumber']}")
    if i=="tcsumm-2019-20": meta[i]['also_dockets']=["25317-16S"]
    new.append(i)
tmp='meta.json.tmp'; json.dump(meta,open(tmp,'w'),indent=1); os.replace(tmp,'meta.json')
subprocess.run([sys.executable,'-I','refetch.py',*new],check=True)
