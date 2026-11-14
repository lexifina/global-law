"""infra11 Part B: the order-node overlay (round11/nodes11.py) in the round-11 audit tools (asserted replacements).
Active only with --nodes DIR (make_packs11) or env R11_NODES=DIR; otherwise the tools are unchanged.

    python -X utf8 round11/agents/infra11/patch_audit11.py
"""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def patch(name, reps):
    p = os.path.join(C2, "round11", "audit", name)
    s = open(p, encoding="utf-8").read()
    assert "nodes11" not in s, "already patched " + name
    for a, b in reps:
        assert s.count(a) == 1, (name, a[:60], s.count(a))
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("patched round11/audit/" + name)


patch("audit11lib.py", [
    ('''def r6lib():
    if R6H not in sys.path:
        sys.path.insert(0, R6H)
    import r6lib as L
    return L
''', '''def r6lib():
    if R6H not in sys.path:
        sys.path.insert(0, R6H)
    import r6lib as L
    nodes11().patch(L)  # round 11: order nodes (DESIGN11 section 4) when a nodes folder is active
    nodes11().patch_audit(sys.modules[__name__])
    return L


def nodes11():
    """Round 11: round11/nodes11.py (active with make_packs11 --nodes DIR or env R11_NODES=DIR; else inert)."""
    if R8 not in sys.path:
        sys.path.insert(0, R8)
    import nodes11 as N
    return N
'''),
])
patch("make_packs11.py", [
    ('''    ap.add_argument("--seed", type=int, default=7)
''', '''    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--nodes", help="round 11: order-node folder (e.g. round11/data_orders; or env R11_NODES) so rows "
                                    "by / on order nodes show the node's own text and caption")
'''),
    ('''    a = ap.parse_args()
''', '''    a = ap.parse_args()
    if a.nodes:  # round 11 (infra11): DESIGN11 section 4 order nodes
        A.nodes11().activate(A.resolve(a.nodes))
'''),
])
