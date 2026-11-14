p = 'make_r9.py'
s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new)
rep('''    """The round-9 cases' expectations (expect7.tsv rows of R9 cases) against the reference without zones."""
    names = {c[0] for c in R9_MAIN + R9_PROBE}
    bad = tot = 0
    out = []
    for r in rows_of(os.path.join(d, 'expect7.tsv')) or []:
        if r[2] not in names or r[4] == '?':
            continue
        tot += 1
        g = v8.get(('treatments', r[1]), '-')''', '''    """The round-9 cases' expectations (expect7.tsv / expect8.tsv rows of R9 cases) against the reference without
    zones."""
    names = {c[0] for c in R9_MAIN + R9_PROBE + R9_AW}
    bad = tot = 0
    out = []
    for r in (rows_of(os.path.join(d, 'expect7.tsv')) or []) + (rows_of(os.path.join(d, 'expect8.tsv')) or []):
        if r[2] not in names or r[4] == '?':
            continue
        tot += 1
        g = v8.get((r[0].replace('.tsv', ''), r[1]), '-')''')
rep('''    for name, fn, o in cases:
        fn(U, name, fl7, **o)
    if flavour != 'probe':
        for name, fn, o in m8.oc_cases():''', '''    for name, fn, o in cases:
        fn(U, name, fl7, **o)
    for name, fn, o in R9_AW:
        fn(U, name, fl7, **o)
    if flavour != 'probe':
        for name, fn, o in m8.oc_cases():''')
rep("""        shutil.copy(os.path.join(d, 'expect7.tsv'), os.path.join(tmp, 'expect7.tsv'))""",
    """        for fn in ('expect7.tsv', 'expect8.tsv'):
            shutil.copy(os.path.join(d, fn), os.path.join(tmp, fn))""")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
