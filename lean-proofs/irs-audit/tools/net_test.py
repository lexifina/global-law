import requests, concurrent.futures as cf, collections, time, threading
UA='Mozilla/5.0 (compatible; tax-guidance-audit/1.0; research use)'
tl=threading.local()
def s():
    if not hasattr(tl,'s'): tl.s=requests.Session(); tl.s.headers['User-Agent']=UA
    return tl.s
urls=['https://www.irs.gov/pub/irs-wd/2025%02d%03d.pdf'%(w,n) for w in range(20,32) for n in range(1,26)]
bad=[]
def h(u):
    r=s().head(u,timeout=30)
    if r.status_code==403: bad.append((u,dict(r.headers)))
    return r.status_code
t=time.time()
with cf.ThreadPoolExecutor(16) as ex: c=collections.Counter(ex.map(h,urls))
print(c, round(time.time()-t,1),'s')
for u,hd in bad[:2]: print(u, {k:v for k,v in hd.items() if k.lower() in ('server','x-request-id','content-type','content-length','x-ah-environment','x-cache-hits','x-age','via','x-served-by','retry-after')})
