"""Round 10 fixture: the trial-judgment bridge, claim trialBridge (DESIGN10 section 6, D10-8, D10-9; LEAN10.md 6).

    python make_tbridge_fixture.py     writes data/, data_noclaim/, data_notable/, edges/, expected_*.tsv here

Synthetic decisions only (no corpus text, no answer key). A state system (30): the court of last resort SUP (tier L),
the intermediate court APP (tier A), a trial court TRI. Each history row is D (node 100+n, SUP, 2012-06-01)
reversing (or vacating) T (node 200+n, APP, 2010-03-01), anchored on T's citation ("..., decision below."); its main
quote is D's judgment line. Rows with the claim trialBridge and a history_tbridge.tsv line quoting T's own judgment
line. One row passes; one row fails each new reason; the claim is ignored where it does not count (certDenied kind,
no anchor, a bridge line); a claimed row without a line fails trialBridgeT; the table rules are counted.

data_noclaim/ = the same data without the trialBridge claim lines and without history_tbridge.tsv (round-9
verdicts, expected_certs_noclaim.tsv, no tbridge counter); data_notable/ = with the claims but no history_tbridge.tsv
(every claimed row that counts fails trialBridgeT).
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
expected, expected_nc, expected_nt = [], [], []
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


DQ = "The judgment of the district court is reversed."
TQ = "The judgment of the trial court is affirmed."


def tcase(n, verdict, noclaim, notable, dq=DQ, kind="reversed", tq=TQ, ddate=20120601, tdate=20100301, tcourt=APP,
          claim=True, anchored=True, line=True, bridge=False, claims=()):
    d, t = 100 + n, 200 + n
    tcit = "%d so 2d 5" % (100 + n)
    ttext = "Smith v. Jones %d. Fixture Court of Appeal. %s All concur." % (n, tq)
    dec(t, tcourt, tdate, ttext)
    cite.append((tcit, t))
    anc = "Smith v. Jones %d, %d So. 2d 5 (Ct. App. 2010), decision below." % (n, 100 + n)
    dtext = "%s %s" % (anc, dq)
    dec(d, SUP, ddate, dtext)
    s = dtext.index(dq)
    rid = "h10t:%d:%d:%s" % (d, t, kind)
    history.append((rid, t, d, ddate, kind, "all", sha(dtext), s, s + len(dq), dq, "cite:%s" % tcit, "majority",
                    "r10:fixture"))
    window(dtext, 0, len(dtext), 0)
    if anchored:
        anchors.append((rid, 0, len(anc), anc, "majority", "r6:fixture"))
    if claim:
        hclaims.append((rid, "trialBridge", "r10:fixture"))
    for c in claims:
        hclaims.append((rid, c, "r10:fixture"))
    if line:
        q = ttext.index(tq)
        tlines.append((rid, q, q + len(tq)))
        window(ttext, q, q + len(tq))
    if bridge:
        w = 300 + n
        wq = "Smith v. Jones %d, %d So. 2d 5 (Ct. App. 2010), rev'd, 999 So. 2d %d (2012)" % (n, 100 + n, n)
        wt = "See " + wq + "."
        dec(w, APP2, 20130101, wt)
        cite.append(("999 so 2d %d" % n, d))
        bridges.append((rid, w, 4, 4 + len(wq), wq, "r10:fixture"))
        window(wt, 4, 4 + len(wq))
    expected.append(("history", rid, verdict, verdict))
    expected_nc.append(("history", rid, noclaim, noclaim))
    expected_nt.append(("history", rid, notable, notable))
    return rid


T = "trialBridgeT"
rid_g = tcase(1, "ok", "ok", T)
tcase(2, "trialBridgeD", "ok", "trialBridgeD", dq="The judgment of the court of appeals and of the district court is reversed.")
tcase(3, "trialBridgeD", "ok", "trialBridgeD", dq="The judgment is reversed.")
tcase(4, "trialBridgeT", "ok", T, tq="The judgment is affirmed in part and reversed in part.")
tcase(5, "trialBridgeT", "ok", T, tq="The judgment of the trial court is modified.")
tcase(6, "trialBridgeDate", "targetLater", T, tdate=20130101)
tcase(7, "trialBridgeDate", "ok", T, tdate=20050301)
tcase(8, "trialBridgeDate", "ok", T, tcourt=SUP)
tcase(9, "ok", "ok", T, dq="The judgment of the circuit court is vacated.", kind="vacated")
tcase(10, "ok", "ok", T, dq="The judgment of the circuit court is set aside.", kind="vacated", claims=("setAside",))
tcase(11, "trialBridgeT", "ok", T, line=False)                       # a claimed row without a line
tcase(12, "ok", "ok", "ok", claim=False)                             # no claim: round 9 (the line is unused)
tcase(13, "anchorPart", "anchorPart", "anchorPart")                 # its anchor's part is set to dissent below
# the claim does not count: no anchor line (round 9: the plain check of D's quote; the window holds T's citation)
tcase(14, "ok", "ok", "ok", anchored=False)
# the claim does not count: a certDenied row; a bridged row (the bridge decides)
tcase(15, "noCue", "noCue", "noCue", kind="certDenied")
tcase(16, "ok", "ok", "ok", bridge=True, tq="The judgment is reversed.")
# table rules: a second line for row 1 (duplicate), an unknown id, a non-numeric offset, a line of 2 fields
tlines.append((rid_g, 0, 5))
tlines.append(("h10t:999:299:reversed", 0, 5))
tlines.append((rid_g, "x", 5))
tlines.append((rid_g, 0))

# row 13: an anchor failure comes first (the anchor names another case)
r13 = [h for h in history if h[0].startswith("h10t:113:")][0]
anchors[:] = [a if a[0] != r13[0] else (a[0], a[1], a[2], a[3], "dissent", a[5]) for a in anchors]
expected[:] = [e if e[1] != r13[0] else ("history", r13[0], "anchorPart", "anchorPart") for e in expected]
expected_nc[:] = [e if e[1] != r13[0] else ("history", r13[0], "anchorPart", "anchorPart") for e in expected_nc]
expected_nt[:] = [e if e[1] != r13[0] else ("history", r13[0], "anchorPart", "anchorPart") for e in expected_nt]

for d, mode in ((os.path.join(HERE, "data"), "all"), (os.path.join(HERE, "data_noclaim"), "noclaim"),
                (os.path.join(HERE, "data_notable"), "notable")):
    shutil.rmtree(d, ignore_errors=True)
    write("courts2.tsv", courts, d)
    write("decisions2.tsv", sorted(decisions), d)
    write("treatments.tsv", [], d)
    write("history.tsv", history, d)
    write("history_anchor.tsv", anchors, d)
    write("history_bridge.tsv", bridges, d)
    write("history_claim.tsv", [c for c in hclaims if mode == "all" or mode == "notable" or c[1] != "trialBridge"], d)
    write("cert_text.tsv", cert_text, d)
    write("window_sha.tsv", sorted(window_sha), d)
    write("cite_index.tsv", cite, d)
    write("system_rules.tsv", [(30, "horizontal", "strong", 0, 99999999, "fixture", "S")], d)
    if mode == "all":
        write("history_tbridge.tsv", tlines, d)
write("edges-00.tsv", [], os.path.join(HERE, "edges"))
hdr = [("table", "id", "result_all", "result_firm")]
write("expected_certs.tsv", hdr + sorted(expected), HERE)
write("expected_certs_noclaim.tsv", hdr + sorted(expected_nc), HERE)
write("expected_certs_notable.tsv", hdr + sorted(expected_nt), HERE)
hids = {h[0] for h in history}
kept, dup, bad = set(), 0, 0
for l in tlines:
    if len(l) != 3 or not all(isinstance(x, int) for x in l[1:]):
        bad += 1
    elif l[0] not in hids:
        continue
    elif l[0] in kept:
        dup += 1
    else:
        kept.add(l[0])
write("expected_tbridge_summary.tsv", [("tbridge_lines", len(kept)), ("tbridge_dup_rows", dup),
                                       ("tbridge_bad_rows", bad), ("bad_rows", "history_tbridge.tsv", bad)], HERE)
print("history", len(history), "tbridge lines", len(tlines), "claims", len(hclaims))
