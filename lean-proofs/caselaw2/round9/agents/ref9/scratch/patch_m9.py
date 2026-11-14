p = 'make_r9.py'
s = open(p, encoding='utf-8').read()
old = """    rows, r8, v8, D, known = round8_verdicts(d)
    by_node = defaultdict(list)
"""
new = """    rows, r8, v8, D, known = round8_verdicts(d)
    tot, bad, out = check_r9_cases(d, v8)
    gen.write(os.path.join(d, 'r9cases_check.tsv'), [[tot, bad]] + [[x] for x in out])
    for x in out:
        print(x, flush=True)
    by_node = defaultdict(list)
"""
assert old in s
s = s.replace(old, new)
old = """def cmd_check(root, ref):
    return m7.cmd_check(root, ref)
"""
new = """def cmd_check(root, ref):
    \"\"\"make_r7.py check on the zone expectations, then the round-9 cases (DESIGN9 §5, §7) against the reference
    with part_zone.tsv removed (their expectations are DESIGN9's, independent of the zones).\"\"\"
    rc = m7.cmd_check(root, ref)
    tot = bad = 0
    for d in m7.universes(root):
        tmp = tempfile.mkdtemp(prefix='r9c_')
        shutil.copytree(os.path.join(d, 'data'), os.path.join(tmp, 'data'))
        pz = os.path.join(tmp, 'data', 'part_zone.tsv')
        if os.path.exists(pz):
            os.remove(pz)
        shutil.copy(os.path.join(d, 'expect7.tsv'), os.path.join(tmp, 'expect7.tsv'))
        v8 = round8_verdicts(tmp)[2]
        t, b, out = check_r9_cases(tmp, v8)
        tot, bad = tot + t, bad + b
        for x in out:
            print(x.replace(os.path.basename(tmp), os.path.basename(d)))
        shutil.rmtree(tmp, ignore_errors=True)
    print('%d round-9 case expectations (DESIGN9 §5, §7), %d differ' % (tot, bad))
    return 1 if (rc or bad) else 0
"""
assert old in s
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
