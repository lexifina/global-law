"""infra11 Part B: add the DESIGN11 section-4 order-node overlay to round11/zones11.py (asserted replacements)."""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(C2, "round11", "zones11.py")
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a))
    s = s.replace(a, b)


rep('''L = PZ.L
TAB = b"\\t"
''', '''L = PZ.L
TAB = b"\\t"
sys.path.insert(0, HERE)
import nodes11  # noqa: E402  (round 11: DESIGN11 section-4 order nodes; inactive unless --nodes / R11_NODES)
nodes11.patch(L)
''')
rep('''    out = {}
    if not want:
        return out
    mx = max(want)''', '''    out = {}
    for k in [x for x in want if nodes11.is_extra(x)]:  # round 11: order nodes (sha1 of the text file)
        out[k] = (nodes11.sha(k) or "-").encode("ascii")
    want = {x for x in want if not nodes11.is_extra(x)}
    if not want:
        return out
    mx = max(want)''')
rep('''    by_repo = collections.defaultdict(list)
    for n in sorted(nodes):
        nr = L.node_row(n)''', '''    by_repo = collections.defaultdict(list)
    per = collections.defaultdict(list)
    st = collections.Counter()
    for n in sorted(x for x in nodes if nodes11.is_extra(x)):  # round 11: order nodes, same builder over their text
        zl, s2 = extra_zones(n)
        for z in zl:
            per[n].append(z.encode("utf-8"))
        st.update(s2)
    nodes = [x for x in nodes if not nodes11.is_extra(x)]
    for n in sorted(nodes):
        nr = L.node_row(n)''')
rep('''    jobs.sort(key=lambda j: -len(j[1]))
    per = collections.defaultdict(list)
    st = collections.Counter()
    if not jobs:''', '''    jobs.sort(key=lambda j: -len(j[1]))
    if not jobs:''')
rep('''def missing_zone_lines(''', '''def extra_zones(n):
    """Round 11: zone lines of one order node = build_zones.work's per-node step over the node's own text."""
    st = collections.Counter()
    text = nodes11.text(n)
    if text is None:
        st["missing_text"] += 1
        return [], st
    try:
        zs, info = PZ.zones(text)
    except Exception as ex:  # count, keep going (as build_zones.work)
        st["zone_err"] += 1
        sys.stderr.write("order node %d: %r\\n" % (n, ex))
        return [], st
    src = PZ.MODE["pm"] + ("hw" if info["hw"] else "") + ("+PJ" if info["pj"] else "")
    st["nodes"] += 1
    return ["%d\\t%d\\t%d\\t%s\\t%s" % (n, a, b, zp, src) for a, b, zp in zs], st


def missing_zone_lines(''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched round11/zones11.py")
