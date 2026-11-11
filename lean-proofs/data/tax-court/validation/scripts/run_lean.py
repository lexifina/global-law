"""Run case JSON files through a Lean TaxCourt runner (current shared build or an exported historical copy).
usage: python run_lean.py <lean-proofs dir> <out.json> <case.json>...   -> per-case checks"""
import json,subprocess,sys,os,tempfile
root,out,files=sys.argv[1],sys.argv[2],sys.argv[3:]
env=dict(os.environ); env['PATH']=os.path.expanduser('~/.elan/bin')+os.pathsep+env['PATH']
res={}
tmp=tempfile.mkdtemp()
for f in files:
    cid=os.path.basename(f).split('.')[0]
    c=json.load(open(f,encoding='utf-8'))
    cases=c if isinstance(c,list) else [c]
    inp=os.path.join(tmp,'in.json'); o=os.path.join(tmp,'out.json')
    json.dump(cases,open(inp,'w',encoding='utf-8'))
    p=subprocess.run(['lake','env','lean','--run','LegalProofs/USTax/TaxCourt/Run.lean',inp,o],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',shell=False)
    if p.returncode==2 or not os.path.exists(o):
        res[cid]={'error':(p.stderr or p.stdout)[-400:]}; continue
    outs=json.load(open(o,encoding='utf-8')); os.remove(o)
    res[cid]={'outcomes':[{'citation':x['citation'],'errors':x.get('errors',[]),'deficiency':x.get('deficiency'),'checks':x.get('checks',[])} for x in outs]}
json.dump(res,open(out,'w',encoding='utf-8'),indent=1)
print('done',len(res))
