"""infra11 Part B: add the DESIGN11 section-4 order-node overlay to round11/certify11.py and
round11/certify11_claims.py (asserted replacements; same edit in both).

    python -X utf8 round11/agents/infra11/patch_certify11.py
"""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def patch(name):
    p = os.path.join(C2, "round11", name)
    s = open(p, encoding="utf-8").read()
    if "nodes11" in s:
        print("already patched", name)
        return

    def rep(a, b):
        nonlocal s
        assert s.count(a) == 1, (name, a[:60], s.count(a))
        s = s.replace(a, b)

    rep('''L = C6.L
''', '''L = C6.L
sys.path.insert(0, HERE)
import nodes11  # noqa: E402  (round 11, DESIGN11 section 4: order nodes; active with --nodes DIR or R11_NODES)
nodes11.patch(L)
''')
    rep('''    ap.add_argument("--base", default=BASE)
''', '''    ap.add_argument("--base", default=BASE)
    ap.add_argument("--nodes", help="round 11: order-node folder (e.g. round11/data_orders; or env R11_NODES): rows "
                                    "may name its node ids (round11/nodes11.py); their text is the node's text file")
''')
    rep('''    a = ap.parse_args()
''', '''    a = ap.parse_args()
    if a.nodes:  # round 11: also exported as R11_NODES so the worker processes load the same nodes
        nodes11.activate(a.nodes)
        nodes11.patch(L)
''')
    rep('''    out = {}
    if not want:
        return out
    top = max(want)''', '''    out = {}
    for k in [x for x in want if nodes11.is_extra(x)]:  # round 11: order nodes (court 2906, date, sha1 of the text)
        out[k] = (nodes11.SCOTUS, nodes11.meta(k)["date"], nodes11.sha(k) or "-")
    want = {x for x in want if not nodes11.is_extra(x)}
    if not want:
        return out
    top = max(want)''')
    rep('''    out = []
    p = subprocess.Popen(["git", "-C", os.path.join(C6.REPOS, repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=NOWIN)
''', '''    out = []
    if repo == nodes11.REPO:  # round 11: order nodes are read from their text files, same checks
        for path, sha, rows in items:
            raw = nodes11.raw(nodes11.node_of(path))
            if raw is None:
                out.extend((r["i"], "textMissing", repo + ":" + path, None) for r in rows)
                continue
            got = hashlib.sha1(raw).hexdigest()
            if got != sha:
                out.extend((r["i"], "shaMismatch", "file %s, decisions2 %s" % (got, sha), None) for r in rows)
                continue
            text = raw.decode("utf-8", "replace").replace(CR + NL, NL)
            for r in rows:
                fn = check_treat if r["table"] == "treatments" else check_hist
                reason, detail, pay = fn(r, text, cues)
                out.append((r["i"], reason, detail, pay))
        return out
    p = subprocess.Popen(["git", "-C", os.path.join(C6.REPOS, repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=NOWIN)
''')
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("patched", name)


patch("certify11.py")
patch("certify11_claims.py")
