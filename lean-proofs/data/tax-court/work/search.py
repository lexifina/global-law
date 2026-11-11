import json,urllib.request,urllib.parse,time,re,sys
UA={"User-Agent":"taxcourt-research-corpus/0.1 (academic dataset build)"}
def q(**p):
    u="https://public-api-green.dawson.ustaxcourt.gov/public-api/opinion-search?"+urllib.parse.urlencode(p)
    r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    time.sleep(1.1); return r['results']
topics={
 'eitc':'"earned income credit" "qualifying child"',
 'hoh':'"head of household"',
 'ctc':'"child tax credit"',
 'actc2021':'"child tax credit" 2021 "American Rescue Plan"',
 '72t':'"additional tax" "72(t)"',
 'ss86':'"social security benefits" "section 86"',
 'se':'"self-employment tax"',
 'ira219':'"IRA deduction" "section 219"',
 'rollover':'rollover "60 days"',
 'educ':'"American opportunity" credit',
 'sli':'"student loan interest"',
 'alimony':'alimony "section 71"',
 'gambling':'"gambling losses" "165(d)"',
 '6654':'"section 6654" "estimated tax"',
 'dep152':'"qualifying relative" dependency',
}
out={}
for k,kw in topics.items():
    for t in ['SOP','MOP']:
        try: r=q(keyword=kw,opinionTypes=t,startDate='2019-01-01')
        except Exception as e: print(k,t,e); continue
        r=[x for x in r if '2019'<=x['filingDate'][:4]<='2025' and not x.get('isStricken')]
        out[f'{k}:{t}']=r; print(k,t,len(r))
json.dump(out,open('candidates.json','w'),indent=0)
