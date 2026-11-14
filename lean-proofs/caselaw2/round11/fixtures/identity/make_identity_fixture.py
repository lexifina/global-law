"""Round 11 fixture: identity-tie evidence, history_identity.tsv (DESIGN11 section 5.2, D11-5, D11-8; LEAN11.md 5.4).

    python make_identity_fixture.py     writes data/, data_noident/, data_emptyident/, edges/, expected_*.tsv here

Synthetic decisions only (no corpus text, no answer key). The tribunal fixture's courts and rows (D = node 100+n,
SUP, 2012-06-01, reversing T = node 200+n, APP, 2010-03-01, anchored with a tribunal name under an anchorTribunal
claim). D's text prints T's docket number, citation and date; T's text prints them too. Rows with an identity line:
docket / cite / date ok; the token in D's span only; a wrong citation; a date token other than date(T); a D span over
200 characters; a failing verdict kept (no claim: anchorNoCue); a bridged row with a good line; a row without a line;
table rules (a duplicate, an unknown id, three bad lines).

data_noident/ = the same data without history_identity.tsv (the section-5.1 verdicts, no identity counter; every
output byte-identical to the section-5.1 binary's); data_emptyident/ = an empty history_identity.tsv (= data_noident's
output byte for byte).
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
decisions, history, anchors, hclaims, idlines, bridges, cert_text, window_sha, cite = [], [], [], [], [], [], [], [], []
expected, expected_ni = [], []
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
FILL = "This filler sentence pads the text of the acting decision. " * 4


def tcase(n, verdict, noident, line=None, trib=True, bridge=False, fill=False):
    """`line` = (form, token, D span text, T span text) or None."""
    d, t = 100 + n, 200 + n
    tcit = "%d f supp 2d 456" % (100 + n)
    dk = "No. 14-501%02d" % n
    ttext = "Foo Corp. %d v. United States. %s. Decided Mar. 1, 2010. %d F. Supp. 2d 456. The judgment of the " \
            "trial court is affirmed. All concur." % (n, dk, 100 + n)
    dec(t, APP, 20100301, ttext)
    window(ttext, 0, len(ttext), 0)
    cite.append((tcit, t))
    anc = "Foo Corp. %d v. United States, %d F. Supp. 2d 456 (Court of International Trade)." % (n, 100 + n)
    dtext = "%s %s%s, decided March 1, 2010. %s" % (anc, FILL if fill else "", dk, DQ)
    dec(d, SUP, 20120601, dtext)
    s = dtext.index(DQ)
    rid = "h11i:%d:%d:reversed" % (d, t)
    history.append((rid, t, d, 20120601, "reversed", "all", sha(dtext), s, s + len(DQ), DQ, "cite:%s" % tcit,
                    "majority", "r11:fixture"))
    window(dtext, 0, len(dtext), 0)
    anchors.append((rid, 0, len(anc), anc, "majority", "r6:fixture"))
    if trib:
        hclaims.append((rid, "anchorTribunal", "r11:fixture"))
    if line:
        form, token, ds, ts = line
        ds = ds.replace("{dk}", dk).replace("{n}", str(100 + n))
        ts = ts.replace("{dk}", dk).replace("{n}", str(100 + n))
        token = token.replace("{dk}", dk).replace("{n}", str(100 + n))
        a = dtext.index(ds) if ds in dtext else 0
        b = ttext.index(ts) if ts in ttext else 0
        idlines.append((rid, form, token, a, a + len(ds), b, b + len(ts)))
    if bridge:
        w = 300 + n
        wq = "Foo Corp. %d v. United States, %d F. Supp. 2d 456 (CIT 2010), rev'd, 999 So. 2d %d (2012)" % (n, 100 + n, n)
        wt = "See " + wq + "."
        dec(w, APP2, 20130101, wt)
        cite.append(("999 so 2d %d" % n, d))
        bridges.append((rid, w, 4, 4 + len(wq), wq, "r11:fixture"))
        window(wt, 4, 4 + len(wq))
    expected.append(("history", rid, verdict, verdict))
    expected_ni.append(("history", rid, noident, noident))
    return rid


IT = "identityTie"
DOCKET = ("docket", "{dk}", "{dk}", "{dk}")
r1 = tcase(1, "ok", "ok", DOCKET)
tcase(2, "ok", "ok", ("cite", "{n} F.Supp.2d 456", "{n} F. Supp. 2d 456", "{n} F. Supp. 2d 456"))
tcase(3, "ok", "ok", ("date", "20100301", "March 1, 2010", "Mar. 1, 2010"))
tcase(4, IT, "ok", ("docket", "{dk}", "{dk}", "All concur."))                      # token in D's span only
tcase(5, IT, "ok", ("cite", "999 F.Supp.2d 456", "{n} F. Supp. 2d 456", "{n} F. Supp. 2d 456"))
tcase(6, IT, "ok", ("date", "20120601", "March 1, 2010", "Mar. 1, 2010"))         # not date(T)
tcase(7, IT, "ok", ("docket", "{dk}", FILL + "{dk}", "{dk}"), fill=True)           # D span over 200
tcase(8, "anchorNoCue", "anchorNoCue", DOCKET, trib=False)                       # a failing verdict kept
tcase(9, "ok", "ok", DOCKET, bridge=True)                                        # the bridge admits, the line checks
tcase(10, "ok", "ok")                                                            # no line
# table rules: a duplicate (a failing second line for row 1 is ignored), an unknown id, three bad lines
idlines.append((r1, "docket", "zzzz", 0, 4, 0, 4))
idlines.append(("h11i:999:299:reversed", "docket", "14-50101", 0, 4, 0, 4))
idlines.append((r1, "name", "Foo", 0, 4, 0, 4))
idlines.append((r1, "docket", "14-50101", "x", 4, 0, 4))
idlines.append((r1, "docket", "14-50101", 0, 4, 0))

for d, mode in ((os.path.join(HERE, "data"), "all"), (os.path.join(HERE, "data_noident"), "none"),
                (os.path.join(HERE, "data_emptyident"), "empty")):
    shutil.rmtree(d, ignore_errors=True)
    write("courts2.tsv", courts, d)
    write("decisions2.tsv", sorted(decisions), d)
    write("treatments.tsv", [], d)
    write("history.tsv", history, d)
    write("history_anchor.tsv", anchors, d)
    write("history_bridge.tsv", bridges, d)
    write("history_claim.tsv", hclaims, d)
    write("cert_text.tsv", cert_text, d)
    write("window_sha.tsv", sorted(window_sha), d)
    write("cite_index.tsv", cite, d)
    write("system_rules.tsv", [(30, "horizontal", "strong", 0, 99999999, "fixture", "S")], d)
    if mode == "all":
        write("history_identity.tsv", idlines, d)
    elif mode == "empty":
        write("history_identity.tsv", [], d)
write("edges-00.tsv", [], os.path.join(HERE, "edges"))
hdr = [("table", "id", "result_all", "result_firm")]
write("expected_certs.tsv", hdr + sorted(expected), HERE)
write("expected_certs_noident.tsv", hdr + sorted(expected_ni), HERE)
hids = {h[0] for h in history}
ok_forms = ("docket", "cite", "date")
kept, dup, bad = {}, 0, 0
for l in idlines:
    if len(l) != 7 or l[1] not in ok_forms or not all(isinstance(x, int) for x in l[3:]):
        bad += 1
    elif l[0] not in hids:
        continue
    elif l[0] in kept:
        dup += 1
    else:
        kept[l[0]] = l
base = {e[1]: e[2] for e in expected_ni}
fin = {e[1]: e[2] for e in expected}
checked = [r for r in kept if base[r] in ("ok", "okUnverifiedBy")]
failed = [r for r in checked if fin[r] == IT]
write("expected_identity_summary.tsv", [("identity_lines", len(kept)), ("identity_checked_rows", len(checked)),
                                        ("identity_failed_rows", len(failed)), ("identity_dup_rows", dup),
                                        ("identity_bad_rows", bad), ("bad_rows", "history_identity.tsv", bad)], HERE)
print("history", len(history), "identity lines", len(idlines), "kept", len(kept), "checked", len(checked),
      "failed", len(failed), "dup", dup, "bad", bad)
