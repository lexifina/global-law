import json,shutil,os
H=r'C:\Users\alany\Documents\tax-formalization-data\taxcourt\validation\holdout'
c={x['docketNumberWithSuffix']:x for x in json.load(open(H+r'\search_results.json'))}
M={'10104-18':'tcmemo-2020-85','10198-17':'tcmemo-2020-96','24305-18S':'tcsumm-2020-28','6448-24':'tcmemo-2026-116',
'1044-25':'tcmemo-2026-25','1468-20S':'tcsumm-2023-11','20268-19S':'tcsumm-2022-19','24551-18S':'tcsumm-2021-13',
'11872-22':'tcmemo-2025-7','16983-24':'tcmemo-2026-93','22664-18S':'tcsumm-2020-6','5367-18S':'tcsumm-2019-13',
'10750-20S':'tcsumm-2022-7','13323-18S':'tcsumm-2019-28','24311-18S':'tcsumm-2021-7','6561-23S':'tcsumm-2025-8'}
sel={}
for d,i in M.items():
    x=c[d]
    for ext in ('.txt','.pdf'): shutil.copyfile(os.path.join(H,'raw',d+ext),os.path.join(H,'raw',i+ext))
    y,n=i.split('-',1)[1].split('-')
    cit=('T.C. Memo. ' if i.startswith('tcmemo') else 'T.C. Summary Opinion ')+f'{y}-{n}'
    sel[i]=dict(id=i,citation=cit,caseCaption=x['caseCaption'],docket=x['docketNumberWithSuffix'],filingDate=x['filingDate'][:10],
        docketEntryId=x['docketEntryId'],judge=x.get('judge'),
        source_url=f"https://public-api-green.dawson.ustaxcourt.gov/public-api/{x['docketNumber']}/{x['docketEntryId']}/public-document-download-url",
        dawson_case_url=f"https://dawson.ustaxcourt.gov/case-detail/{x['docketNumber']}")
json.dump(sel,open(H+r'\selected.json','w'),indent=1)
print(len(sel))
