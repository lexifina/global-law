"""Compare two revisions of a Mlang tests/<year> directory: find test files whose primitive inputs are identical
but whose expected primitive results differ (evidence of an output-changing change between the DGFiP releases
that generated them)."""
import subprocess, sys, hashlib, collections
repo, a, b, d = sys.argv[1:5]
def files(rev):
    out = subprocess.run(["git","-C",repo,"ls-tree","-r","--name-only",rev,"--",d],capture_output=True,text=True).stdout.split()
    return out
def blob(rev, f):
    return subprocess.run(["git","-C",repo,"show",f"{rev}:{f}"],capture_output=True).stdout.decode("latin1")
def sections(t):
    s=collections.defaultdict(list); cur=None
    for line in t.splitlines():
        line=line.strip()
        if line.startswith("#"): cur=line; continue
        if cur and line: s[cur].append(line)
    return s
def index(rev):
    idx={}
    for f in files(rev):
        if not f.endswith(".irj"): continue
        s=sections(blob(rev,f))
        key=hashlib.md5("\n".join(sorted(s.get("#ENTREES-PRIMITIF",[]))).encode()).hexdigest()
        idx.setdefault(key,[]).append((f,s))
    return idx
A=index(a); B=index(b)
common=set(A)&set(B)
print("files A",sum(map(len,A.values())),"B",sum(map(len,B.values())),"same-input",len(common))
nd=0
for k in sorted(common):
    fa,sa=A[k][0]; fb,sb=B[k][0]
    ra=dict(x.split("/",1) for x in sa.get("#RESULTATS-PRIMITIF",[]) if "/" in x)
    rb=dict(x.split("/",1) for x in sb.get("#RESULTATS-PRIMITIF",[]) if "/" in x)
    ca=sa.get("#CONTROLES-PRIMITIF",[]); cb=sb.get("#CONTROLES-PRIMITIF",[])
    diff={v:(ra.get(v),rb.get(v)) for v in set(ra)|set(rb) if ra.get(v)!=rb.get(v)}
    if diff or ca!=cb:
        nd+=1
        if nd<=40: print(fa, fb, "ctl" if ca!=cb else "", sorted(diff.items())[:8])
print("same input, different results:", nd)
