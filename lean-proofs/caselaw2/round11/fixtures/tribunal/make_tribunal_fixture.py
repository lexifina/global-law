"""Round 11 fixture: the claim anchorTribunal (DESIGN11 section 5.1, D11-4; LEAN11.md 1.4).

    python make_tribunal_fixture.py     writes data/, data_noclaim/, edges/, expected_*.tsv here

Synthetic decisions only (no corpus text, no answer key). The court structure of round 10's tbridge fixture (system
30: SUP tier L, APP tier A, TRI tier T). Each history row is D (node 100+n, SUP, 2012-06-01) reversing T (node 200+n,
APP, 2010-03-01), anchored on T's citation with the deciding tribunal in parentheses
("Foo Corp. n v. United States, 1nn F. Supp. 2d 456 (Court of International Trade)."); its main quote is D's judgment
line. Rows with the claim anchorTribunal: one per tribunal phrase (ok), with anchorWide too, an anchor with no cue of
any list, the other anchored checks (disqualifier, part), a plain anchor cue under the claim, a counted trialBridge
claim with the tribunal anchor; unclaimed tribunal rows (anchorNoCue, also under anchorWide alone); the claim unused
(no anchor line; a bridge line); a duplicate claim line and an unknown id.

data_noclaim/ = the same data without the anchorTribunal claim lines (every other claim kept): round-10 verdicts
(expected_certs_noclaim.tsv), no tribunal counter, and every output byte-identical to the frozen round-10 binary's.
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SUP, APP, TRI, APP2 = 9101, 9102, 9103, 9104


def sha(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def write(name, rows, d):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


courts = [
    (SUP, 0, 99999999, "Supreme Court of Fixture", 30, "L", "all", 0, 0, "fixture", "S"),
    (APP, 0, 99999999, "Fixture Court of Appeal", 30, "A", "-", 0, 0, "fixture", "S"),
    (TRI, 0, 99999999, "Fixture District Court", 30, "T", "-", 0, 0, "fixture", "S"),
    (APP2, 0, 99999999, "Fixture Court of Appeal, Second Division", 30, "A", "-", 0, 0, "fixture", "S"),
]
decisions, history, anchors, hclaims, tlines, bridges, cert_text, window_sha, cite = [], [], [], [], [], [], [], [], []
expected, expected_nc = [], []
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


DQ = "The judgment is reversed."
TQ = "The judgment of the trial court is affirmed."
CIT = "Court of International Trade"


def tcase(n, verdict, noclaim, tribunal=CIT, dq=DQ, kind="reversed", pre="", part="majority", trib=True,
          anchored=True, bridge=False, tbridge=False, claims=()):
    d, t = 100 + n, 200 + n
    tcit = "%d f supp 2d 456" % (100 + n)
    ttext = "Foo Corp. %d v. United States. %s All concur." % (n, TQ)
    dec(t, APP, 20100301, ttext)
    cite.append((tcit, t))
    anc = "%sFoo Corp. %d v. United States, %d F. Supp. 2d 456 (%s)." % (pre, n, 100 + n, tribunal)
    dtext = "%s %s" % (anc, dq)
    dec(d, SUP, 20120601, dtext)
    s = dtext.index(dq)
    rid = "h11a:%d:%d:%s" % (d, t, kind)
    history.append((rid, t, d, 20120601, kind, "all", sha(dtext), s, s + len(dq), dq, "cite:%s" % tcit, "majority",
                    "r11:fixture"))
    window(dtext, 0, len(dtext), 0)
    if anchored:
        anchors.append((rid, 0, len(anc), anc, part, "r6:fixture"))
    if trib:
        hclaims.append((rid, "anchorTribunal", "r11:fixture"))
    for c in claims:
        hclaims.append((rid, c, "r11:fixture"))
    if tbridge:
        q = ttext.index(TQ)
        tlines.append((rid, q, q + len(TQ)))
        window(ttext, q, q + len(TQ))
    if bridge:
        w = 300 + n
        wq = "Foo Corp. %d v. United States, %d F. Supp. 2d 456 (CIT 2010), rev'd, 999 So. 2d %d (2012)" % (n, 100 + n, n)
        wt = "See " + wq + "."
        dec(w, APP2, 20130101, wt)
        cite.append(("999 so 2d %d" % n, d))
        bridges.append((rid, w, 4, 4 + len(wq), wq, "r11:fixture"))
        window(wt, 4, 4 + len(wq))
    expected.append(("history", rid, verdict, verdict))
    expected_nc.append(("history", rid, noclaim, noclaim))
    return rid


NC = "anchorNoCue"
rid_g = tcase(1, "ok", NC)
tcase(2, "ok", NC, tribunal="Customs Court")
tcase(3, "ok", NC, tribunal="Court of Federal Claims")
tcase(4, "ok", NC, tribunal="Claims Court", claims=("anchorWide",))      # both claims: the union
tcase(5, "ok", NC, tribunal="Veterans Court")
tcase(6, "ok", NC, tribunal="court of veterans appeals")
tcase(7, NC, NC, trib=False)                                            # no claim
tcase(8, NC, NC, trib=False, claims=("anchorWide",))                    # anchorWide alone
tcase(9, NC, NC, tribunal="2000")                                       # no cue of any list
tcase(10, "anchorDisqualified", NC, pre="See also ")                    # the other checks still bite
tcase(11, "anchorPart", NC, part="dissent")
tcase(12, "ok", "ok", tribunal="District Court")                        # an anchor cue: ok either way
tcase(13, "ok", NC, dq="The judgment of the trial court is reversed.", tbridge=True, claims=("trialBridge",))
tcase(14, "ok", "ok", anchored=False)                                   # unused: no anchor line
tcase(15, "ok", "ok", bridge=True)                                      # unused: a bridge line decides
# a duplicate claim line for row 1; an unknown id
hclaims.append((rid_g, "anchorTribunal", "r11:fixture"))
hclaims.append(("h11a:999:299:reversed", "anchorTribunal", "r11:fixture"))

for d, mode in ((os.path.join(HERE, "data"), "all"), (os.path.join(HERE, "data_noclaim"), "noclaim")):
    shutil.rmtree(d, ignore_errors=True)
    write("courts2.tsv", courts, d)
    write("decisions2.tsv", sorted(decisions), d)
    write("treatments.tsv", [], d)
    write("history.tsv", history, d)
    write("history_anchor.tsv", anchors, d)
    write("history_bridge.tsv", bridges, d)
    write("history_claim.tsv", [c for c in hclaims if mode == "all" or c[1] != "anchorTribunal"], d)
    write("history_tbridge.tsv", tlines, d)
    write("cert_text.tsv", cert_text, d)
    write("window_sha.tsv", sorted(window_sha), d)
    write("cite_index.tsv", cite, d)
    write("system_rules.tsv", [(30, "horizontal", "strong", 0, 99999999, "fixture", "S")], d)
write("edges-00.tsv", [], os.path.join(HERE, "edges"))
hdr = [("table", "id", "result_all", "result_firm")]
write("expected_certs.tsv", hdr + sorted(expected), HERE)
write("expected_certs_noclaim.tsv", hdr + sorted(expected_nc), HERE)
# the history-claim counters of data/ (L11-1, L11-4)
hids = {h[0] for h in history}
verdict = {e[1]: e[2] for e in expected}
seen, rows, dup, unknown = set(), set(), 0, 0
for rid, c, _ in hclaims:
    if rid not in hids:
        unknown += 1
    elif (rid, c) in seen:
        dup += 1
    else:
        seen.add((rid, c))
        rows.add(rid)
adm = sum(1 for r in rows if verdict[r] in ("ok", "okUnverifiedBy"))
wide = {r for r, c in seen if c == "anchorWide"}
trib = {r for r, c in seen if c == "anchorTribunal"}
anc_ids = {a[0] for a in anchors}
br_ids = {b[0] for b in bridges}
unused = lambda s: sum(1 for r in s if r not in anc_ids or r in br_ids)
write("expected_hclaim_summary.tsv", [
    ("hclaim_rows", len(rows)), ("hclaim_unknown_ids", unknown), ("hclaim_duplicates", dup),
    ("hclaim_admitted", adm), ("hclaim_rejected", len(rows) - adm),
    ("hclaim_anchorwide", len(wide)), ("hclaim_anchorwide_unused", unused(wide)),
    ("hclaim_anchortribunal", len(trib)), ("hclaim_anchortribunal_unused", unused(trib))], HERE)
print("history", len(history), "claims", len(hclaims), "tribunal", len(trib), "unused", unused(trib))
