import json,urllib.request,urllib.parse,time,sys
UA={"User-Agent":"taxcourt-research-corpus/0.1 (academic dataset build)"}
def q(**p):
    u="https://public-api-green.dawson.ustaxcourt.gov/public-api/opinion-search?"+urllib.parse.urlencode(p)
    r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    time.sleep(1.1); return r['results']
topics={'dsue':'"deceased spousal unused exclusion"','portability':'portability "2010(c)"',
 'annual':'"annual exclusion" gift "2503(b)"','crummey':'Crummey','netgift':'"net gift"',
 '2035b':'"2035(b)"','marital':'"marital deduction" "2056"','charit':'"charitable deduction" "2055"',
 '2053':'"section 2053" estate','adjtg':'"adjusted taxable gifts"'}
out={}
for k,kw in topics.items():
    for t in ['TCOP','MOP']:
        try: r=q(keyword=kw,opinionTypes=t,startDate='2012-01-01')
        except Exception as e: print(k,t,e); continue
        out[f'{k}:{t}']=r
        print(k,t,len(r))
        for x in r: print('   ',x.get('filingDate','')[:10],x.get('docketNumberWithSuffix'),x.get('caseCaption','')[:70],'|',x.get('documentTitle','')[:40])
json.dump(out,open('candidates.json','w'),indent=0)
