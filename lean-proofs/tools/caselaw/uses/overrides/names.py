"""Does a law's text name a decision? By one of the decision's reporter citations, or by its parties' names."""
import re
STOP = set("""united states america state states people commonwealth commissioner internal revenue inc co corp corporation company
companies llc ltd lp llp plc dept department secretary sec et al ex rel the of and in re matter for a an supreme court courts in
county city board bank national american association assn federal government district town village township inc. co. corp.
attorney general director administrator commission agency service services authority insurance security securities trust
estate doe john jane unknown petitioner respondent appellant appellee plaintiff defendant n.a nos no inc., co., the
u.s u.s. us usa n. a. l. c. f. j. r. s. t. v jr mr ms dr""".split())
def toks(side):
    out = []
    for w in re.findall(r"[A-Za-z][A-Za-z'’\-]+", side):
        lw = w.lower().strip("'’")
        if len(lw) >= 3 and lw not in STOP:
            out.append(lw)
    return out
def sides(name):
    name = re.sub(r'^\s*(In re|In the Matter of|Ex parte|Matter of)\s+', '', name, flags=re.I)
    parts = re.split(r'\s+v\.?\s+|\s+vs\.?\s+', name, maxsplit=1)
    return [toks(p) for p in parts]
def norm_cite(c):
    c = re.sub(r'\s+', ' ', c.strip())
    m = re.match(r'(\d+) (.+?) (\d+)$', c)
    if not m: return None
    return f'{m.group(1)} {m.group(2).replace(" ", "")} {m.group(3)}'
def match(dname, dcites, law_cases, law_cites, df=None, rare=200):
    """'cite' | 'name2' (both parties) | 'name1' (the one party with a distinctive name) | ''."""
    lc = {c for c, _ in law_cites}
    for c in dcites:
        n = norm_cite(c)
        if n and n in lc: return 'cite'
    ds = sides(dname)
    dd = [s for s in ds if s]
    if not dd: return ''
    best = ''
    for L, R, _ in law_cases:
        ls = [set(toks(L)), set(toks(R))]
        for a, b in ((ls[0], ls[1]), (ls[1], ls[0])):
            if len(ds) == 2 and ds[0] and ds[1]:
                if ds[0][0] in a and ds[1][0] in b: return 'name2'
            else:
                s = dd[0]
                if s[0] in a and not b:
                    if df is None or df.get(s[0], 0) <= rare: best = 'name1'
    return best
