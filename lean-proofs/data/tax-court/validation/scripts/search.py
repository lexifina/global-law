import json,urllib.request,urllib.parse,time,re,os
BASE=r'~\Documents\tax-formalization-data\taxcourt'
UA={"User-Agent":"taxcourt-research-corpus/0.1 (academic dataset build)"}
# exclusion set
excl_d=set(); excl_e=set()
for f in [BASE+r'\index.json',BASE+r'\work\meta.json']:
    s=open(f,encoding='utf-8').read()
    excl_d|=set(re.findall(r'\b(\d{1,5}-\d{2})[A-Z]{0,2}\b',s))
    excl_e|=set(re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',s))
meta=json.load(open(BASE+r'\work\meta.json',encoding='utf-8'))
excl_d|={v['docketNumber'] for v in meta.values()}
print('excluded dockets',len(excl_d),'entries',len(excl_e))
def q(**p):
    u="https://public-api-green.dawson.ustaxcourt.gov/public-api/opinion-search?"+urllib.parse.urlencode(p)
    req=urllib.request.Request(u,headers=UA)
    r=json.load(urllib.request.urlopen(req,timeout=60)); time.sleep(1.1)
    return r['results'] if isinstance(r,dict) else r
topics={
 'hoh':'"head of household"','eitc':'"earned income credit"','qc':'"qualifying child"',
 '72t':'"10% additional tax"','72t2':'"72(t)"','ss':'"social security benefits"','roll':'rollover',
 'ctc':'"child tax credit"','ptc':'"premium tax credit"','aotc':'"American opportunity"',
 '6654':'"estimated tax" 6654','6651':'"6651(a)(1)"','hsa':'"health savings account"',
 'gamb':'"gambling losses"','alim':'alimony','feie':'"foreign earned income"','qr':'"qualifying relative"',
 'ira':'"individual retirement account" distribution','se':'"self-employment tax"',
}
out={}; seen={}
for k,kw in topics.items():
    for t in ['SOP','MOP']:
        try: r=q(keyword=kw,opinionTypes=t,startDate='2019-01-01')
        except Exception as e: print('ERR',k,t,e,flush=True); continue
        n=len(r)
        r=[x for x in r if '2019'<=x['filingDate'][:4]<='2026' and not x.get('isStricken')]
        for x in r:
            d=x['docketNumber']
            if d in excl_d or x['docketEntryId'] in excl_e: continue
            seen.setdefault(x['docketEntryId'],dict(x,hits=[]))['hits'].append(k)
        print(k,t,n,len(r),flush=True)
json.dump(list(seen.values()),open(BASE+r'\validation\holdout\search_results.json','w'),indent=0)
print('new unique',len(seen))
