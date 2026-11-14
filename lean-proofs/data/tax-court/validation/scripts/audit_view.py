import json,glob,os,sys
B=r'~\Documents\tax-formalization-data\taxcourt\encoded'
ids=sorted(os.path.basename(f)[:-12] for f in glob.glob(B+r'\*.result.json'))
lo,hi=int(sys.argv[1]),int(sys.argv[2])
for n,cid in enumerate(ids[lo:hi],lo):
    c=json.load(open(os.path.join(B,cid+'.case.json'),encoding='utf-8'))
    r=json.load(open(os.path.join(B,cid+'.result.json'),encoding='utf-8'))
    print('#####',n,cid,r.get('citation'))
    for yr in (c if isinstance(c,list) else [c]):
        print(' Y',yr.get('taxYear'),'NOTE:',yr.get('note'))
        rest={k:v for k,v in yr.items() if k not in('note','citation','taxYear','expected')}
        print(' F',json.dumps(rest,separators=(',',':')))
        print(' E',json.dumps(yr.get('expected'),separators=(',',':')))
    for i,x in enumerate(r['issues']):
        print(f" [{i}] {x['verdict'].upper()} | {x['issue']} | court: {x['court']} | lean: {x['lean']}")
        print('     D:',x.get('diagnosis'))
    print(' DEF',r.get('deficiency'),'| NOTES:',r.get('notes'))
