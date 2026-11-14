"""Round 8 fixture: bridge evidence (DESIGN8 section 4), wide anchor cues (section 5), old circuits (section 6).

    python make_bridge_fixture.py        writes data/, data_nor8/, edges/, expected_*.tsv here

Synthetic decisions only (no corpus text, no answer key). Each history row has its own acting order O and, when it
carries a bridge line, its own bridge text W; windows are cut a few characters around each quote. One row passes each
rule; one row fails each new reason code; the table rules (duplicate, unknown id, malformed line, an anchor line on
a bridged row, claims on rows they do not fit) are counted.

data_nor8/ is the same data without history_bridge.tsv and without the anchorWide / oldCircuit claim lines: the
round-7 checks (expected_certs_nor8.tsv), and no round-8 counter.
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
EDGES = os.path.join(HERE, "edges")
SCOTUS, CA5, NDGA = 2906, 346, 5011


def sha(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def write(name, rows, d=DATA):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


courts = [
    (SCOTUS, 0, 99999999, "Supreme Court of the United States", 0, "L", "all", 0, 0, "fixture", "S"),
    (CA5, 0, 99999999, "United States Court of Appeals for the Fifth Circuit", 0, "A", "-", 5, 0, "fixture", "S"),
    (NDGA, 0, 99999999, "United States District Court for the Northern District of Georgia", 0, "T", "-", 11, 0,
     "fixture", "S"),
]
decisions, history, anchors, hclaims, bridges = [], [], [], [], []
cert_text, window_sha, expected, expected_n = [], [], [], []
cite = []
win_seen = set()


def window(text, s, e, margin=8):
    s0, e0 = max(0, s - margin), min(len(text), e + margin)
    key = (sha(text), s0, e0)
    if key in win_seen:
        return
    win_seen.add(key)
    cert_text.append((sha(text), s0, e0, text[s0:e0]))
    window_sha.append((sha(text), s0, e0, sha(text[s0:e0]), "fixture"))


def dec(node, court, date, text):
    decisions.append((node, court, date, 0, "wholeCourt", "published", "full", sha(text), "fixture"))


# targets X (node 5 and others) and the other cited decisions
dec(5, CA5, 20150601, "Smith v. Jones. Opinion of the Court of Appeals.")
cite.append(("123 f3d 456", 5))
dec(6, CA5, 19990601, "Doe v. Roe. Opinion.")
cite.append(("200 f3d 9", 6))
dec(7, SCOTUS, 20150301, "Other v. Case. Order.")
cite.append(("576 us 900", 7))

ORDER = "No. 15-%d. Smith v. Jones. Certiorari denied."
DISP = "Certiorari denied."


def bcase(n, verdict, nor8, wquote=None, wtext=None, wdate=20170101, odate=20160111, kind="certDenied",
          part="majority", claims=(), nowin=False, shift=0, anchor=None, order=None, ocite=None, extra_lines=()):
    """A history row: O (node 100+n) acting on X (node 5); its bridge W (node 200+n) quotes wquote."""
    o, w = 100 + n, 200 + n
    otext = order or (ORDER % n)
    dec(o, SCOTUS, odate, otext)
    oc = ocite or "577 us %d" % (1000 + n)
    cite.append((oc, o))
    s = otext.index(DISP)
    rid = "h8:%d:5:%s" % (o, kind)
    history.append((rid, 5, o, odate, kind, "all", sha(otext), s, s + len(DISP), DISP, "cite:123 f3d 456", part,
                    "r8:fixture"))
    window(otext, s, s + len(DISP), 60)
    if anchor:
        a = otext.index(anchor)
        anchors.append((rid, a, a + len(anchor), anchor, "headmatter", "r6:fixture"))
        window(otext, a, a + len(anchor), 8)
    if wquote is not None:
        wt = wtext or ("The facts are set out below. See " + wquote + ". We turn to the merits.")
        dec(w, CA5, wdate, wt)
        b = wt.index(wquote) + shift
        bridges.append((rid, w, b, b + len(wquote), wquote, "r8:fixture"))
        if not nowin:
            window(wt, wt.index(wquote), wt.index(wquote) + len(wquote), 8)
    for c in claims:
        hclaims.append((rid, c, "r8:fixture"))
    for l in extra_lines:
        bridges.append((rid,) + tuple(l))
    expected.append(("history", rid, verdict, verdict))
    expected_n.append(("history", rid, nor8, nor8))
    return rid


def good(n):
    return "Smith v. Jones, 123 F. 3d 456 (CA5 2015), cert. denied, 577 U. S. %d (2016)" % (1000 + n)


# ---------------------------------------------------------------- bridge rows
rid_g = bcase(1, "ok", "targetUnresolved", good(1))
bcase(2, "bridgeMismatch", "targetUnresolved", good(2), shift=2)
bcase(3, "bridgeDate", "targetUnresolved", good(3), wdate=20150101)
bcase(4, "bridgeClause", "targetUnresolved", good(4) + "; Doe v. Roe, 200 F. 3d 9 (CA5 1999)")
bcase(5, "bridgeTarget", "targetUnresolved",
      "Doe v. Roe, 200 F. 3d 9 (CA5 1999), cert. denied, 577 U. S. 1005 (2016)")
bcase(6, "bridgeCue", "targetUnresolved", "Smith v. Jones, 123 F. 3d 456 (CA5 2015), aff'd, 577 U. S. 1006 (2016)")
bcase(7, "bridgeChain", "targetUnresolved",
      "Smith v. Jones, 123 F. 3d 456 (CA5 1998), aff'd, 200 F. 3d 9 (CA5 1999), cert. denied, 577 U. S. 1007 (2016)")
bcase(8, "bridgeActor", "targetUnresolved",
      "Smith v. Jones, 123 F. 3d 456 (CA5 2015), cert. denied, 576 U. S. 900 (2015)")
bcase(9, "bridgeActor", "targetUnresolved",
      "Smith v. Jones, 577 U. S. 1009, and 123 F. 3d 456 (CA5 2015), cert. denied")
bcase(10, "bridgeMismatch", "targetUnresolved", good(10), nowin=True)
bcase(11, "partNotMajority", "targetUnresolved", good(11), part="dissent")
LONG = ("Smith v. Jones, 123 F. 3d 456 (CA5 2015) (" +
        "the panel considering the matter with care and at length, " * 12 + "), cert. denied, 577 U. S. 1013 (2016)")
bcase(13, "bridgeMismatch", "targetUnresolved", LONG)
# an anchor line on a bridged row: ignored (bridge_anchor_ignored); without the bridge table the anchor decides
ANC_ORDER = "No. 15-12. Smith v. Jones. On petition for writ of certiorari to the Court of Appeals. Certiorari denied."
bcase(12, "ok", "anchorUnresolved", good(12), order=ANC_ORDER,
      anchor="On petition for writ of certiorari to the Court of Appeals.")
# head matter under an orderHead claim (a Supreme Court order of 2016), with a bridge
bcase(14, "ok", "targetUnresolved", good(14), part="headmatter", claims=["orderHead"])
# table rules: a second line for row 1 (duplicate), an unknown id, a malformed line (non-numeric node)
bridges.append((rid_g, 201, 0, 5, "See S", "r8:fixture-duplicate"))
bridges.append(("h8:999:5:certDenied", 201, 0, 5, "See S", "r8:fixture-unknown"))
bridges.append((rid_g, "w", 0, 5, "See S", "r8:fixture-malformed"))

# ---------------------------------------------------------------- wide anchor cues (section 5)
dec(9, CA5, 20070601, "Iqbal v. Hasty. Opinion.")
cite.append(("490 f3d 143", 9))
AW = "Iqbal v. Hasty, 490 F. 3d 143 (CA2 2007). The judgment of the Court of Appeals is reversed."
AWD = "The judgment of the Court of Appeals is reversed."
AWA = "Iqbal v. Hasty, 490 F. 3d 143 (CA2 2007)."


def awcase(node, text, verdict, nor8, claims=(), anchored=True, target=9, evidence="cite:490 f3d 143"):
    dec(node, SCOTUS, 20090518, text)
    s = text.index(AWD)
    rid = "h8:%d:%d:reversed" % (node, target)
    history.append((rid, target, node, 20090518, "reversed", "all", sha(text), s, s + len(AWD), AWD, evidence,
                    "majority", "r8:fixture"))
    window(text, s, s + len(AWD), 8)
    if anchored:
        a = text.index(AWA)
        anchors.append((rid, a, a + len(AWA), AWA, "majority", "r6:fixture"))
        window(text, a, a + len(AWA), 8)
    for c in claims:
        hclaims.append((rid, c, "r8:fixture"))
    expected.append(("history", rid, verdict, verdict))
    expected_n.append(("history", rid, nor8, nor8))
    return rid


awcase(300, AW, "ok", "anchorNoCue", ["anchorWide"])
awcase(301, AW + " No. 301.", "anchorNoCue", "anchorNoCue")
# the claim on a row without an anchor line: no effect (counted unused); the window holds the citation
awcase(302, AW + " No. 302.", "targetUnresolved", "targetUnresolved", ["anchorWide"], anchored=False)

# ---------------------------------------------------------------- old circuits (section 6)
dec(11, NDGA, 19750301, "Doe v. Georgia. District Court.")
cite.append(("400 fsupp 1", 11))
OCQ = "The judgment of the District Court in Doe v. Georgia, 400 F. Supp. 1, is reversed."


def occase(node, date, verdict, nor8, claims=("oldCircuit",)):
    text = "Before the Court of Appeals. " + OCQ + " No. %d." % node
    dec(node, CA5, date, text)
    s = text.index(OCQ)
    rid = "h8:%d:11:reversed" % node
    history.append((rid, 11, node, date, "reversed", "all", sha(text), s, s + len(OCQ), OCQ, "cite:400 fsupp 1",
                    "majority", "r8:fixture"))
    window(text, s, s + len(OCQ), 8)
    for c in claims:
        hclaims.append((rid, c, "r8:fixture"))
    expected.append(("history", rid, verdict, verdict))
    expected_n.append(("history", rid, nor8, nor8))
    return rid


occase(400, 19780301, "ok", "noAuthority")
occase(401, 19820301, "noAuthority", "noAuthority")
occase(402, 19780301, "noAuthority", "noAuthority", claims=())
# claims of the table rules: a repeated anchorWide line, an oldCircuit claim on an unknown (treatments-like) id
hclaims.append(("h8:300:9:reversed", "anchorWide", "r8:fixture-duplicate"))
hclaims.append(("t8:400:11:0", "oldCircuit", "r8:fixture-treatments-id"))

# ---------------------------------------------------------------- write
R8_CLAIMS = ("anchorWide", "oldCircuit")
for d, r8 in ((DATA, True), (os.path.join(HERE, "data_nor8"), False)):
    shutil.rmtree(d, ignore_errors=True)
    write("courts2.tsv", courts, d)
    write("decisions2.tsv", sorted(decisions), d)
    write("treatments.tsv", [], d)
    write("history.tsv", history, d)
    write("history_anchor.tsv", anchors, d)
    write("history_claim.tsv", [c for c in hclaims if r8 or c[1] not in R8_CLAIMS], d)
    write("cert_text.tsv", cert_text, d)
    write("window_sha.tsv", sorted(window_sha), d)
    write("cite_index.tsv", cite, d)
    write("system_rules.tsv", [(0, "horizontal", "strong", 0, 99999999, "fixture", "S")], d)
    if r8:
        write("history_bridge.tsv", bridges, d)
write("edges-00.tsv", [], EDGES)
hdr = [("table", "id", "result_all", "result_firm")]
write("expected_certs.tsv", hdr + sorted(expected), HERE)
write("expected_certs_nor8.tsv", hdr + sorted(expected_n), HERE)
# counters, computed from the rows above, independently of the runner
hids = {h[0] for h in history}
verdict = {e[1]: e[2] for e in expected}
adm = lambda r: verdict[r] in ("ok", "okUnverifiedBy")
kept, unk, dup, bad = {}, 0, 0, 0
for b in bridges:
    if not isinstance(b[1], int):
        bad += 1
    elif b[0] not in hids:
        unk += 1
    elif b[0] in kept:
        dup += 1
    else:
        kept[b[0]] = b
anc_ids = {a[0] for a in anchors}
claims, unk_c, dup_c = {}, 0, 0
for c in hclaims:
    if c[0] not in hids:
        unk_c += 1
    elif c[1] in claims.get(c[0], set()):
        dup_c += 1
    else:
        claims.setdefault(c[0], set()).add(c[1])
wide = [r for r in claims if "anchorWide" in claims[r]]
old = [r for r in claims if "oldCircuit" in claims[r]]
anchored_rows = [r for r in anc_ids if r in hids]
write("expected_summary.tsv", [
    ("anchor_rows", len(anchored_rows)), ("anchor_unknown_ids", 0), ("anchor_duplicates", 0),
    ("anchored_admitted", sum(1 for r in anchored_rows if r not in kept and adm(r))),
    ("anchored_rejected", sum(1 for r in anchored_rows if r not in kept and not adm(r))),
    ("hclaim_rows", len(claims)), ("hclaim_unknown_ids", unk_c), ("hclaim_duplicates", dup_c),
    ("hclaim_admitted", sum(1 for r in claims if adm(r))), ("hclaim_rejected", sum(1 for r in claims if not adm(r))),
    ("hclaim_anchorwide", len(wide)), ("hclaim_anchorwide_unused", sum(1 for r in wide if r not in anc_ids or r in kept)),
    ("hclaim_oldcircuit", len(old)), ("hclaim_oldcircuit_used", sum(1 for r in old if adm(r))),
    ("bridge_rows", len(kept)), ("bridge_unknown_ids", unk), ("bridge_duplicates", dup),
    ("bridge_anchor_ignored", sum(1 for r in kept if r in anc_ids)),
    ("bridge_admitted", sum(1 for r in kept if adm(r))), ("bridge_rejected", sum(1 for r in kept if not adm(r))),
    ("bad_rows", "history_bridge.tsv", bad)], HERE)
print("history", len(history), "bridge lines", len(bridges), "claims", len(hclaims))
