"""Round 10 fixture: remand bridge evidence (DESIGN10 section 4, D10-5, D10-6, D10-7; round10/LEAN10.md).

    python make_remand_fixture.py      writes data/, data_noremand/, data_emptyremand/, edges/, expected_*.tsv here

Synthetic decisions only (no corpus text, no answer key), in the style of round8/fixtures/bridge. Each history row is
a Supreme Court order O (node 100+n, 2016-01-11) that vacates and remands the Fifth Circuit's judgment X (node 5,
2015-06-01, No. 14-50123); its own quote names X's citation, so its round-9 verdict is `ok`. A remand line names B
(node 200+n), quotes B's text and gives the docket spans of B's and X's texts, the reason-case tie string and its
span of O's text (D10-7: 12 columns). Windows are cut a few characters
around each quote / span (window_sha.tsv supplied, so every window is hash-checked). One row passes each tie; one row
fails each reason; a failing round-9 verdict is kept; the table rules (duplicate, unknown id, malformed lines) are
counted.

data_noremand/ is the same data without history_remand.tsv (the round-9 verdicts, expected_certs_noremand.tsv, and
no remand counter); data_emptyremand/ has an empty history_remand.tsv (output byte-identical to data_noremand's).
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
decisions, history, remands, cert_text, window_sha, cite = [], [], [], [], [], []
expected, expected_n = [], []
win_seen = set()
bad_hash = set()   # text hashes whose windows get a wrong recorded hash


def window(text, s, e, margin=8):
    s0, e0 = max(0, s - margin), min(len(text), e + margin)
    key = (sha(text), s0, e0)
    if key in win_seen:
        return
    win_seen.add(key)
    cert_text.append((sha(text), s0, e0, text[s0:e0]))
    h = sha(text[s0:e0])
    if sha(text) in bad_hash:
        h = "0" * 40
    window_sha.append((sha(text), s0, e0, h, "fixture"))


def dec(node, court, date, text):
    decisions.append((node, court, date, 0, "wholeCourt", "published", "full", sha(text), "fixture"))


XTEXT = "United States Court of Appeals, Fifth Circuit. No. 14-50123. Smith v. Jones. Opinion of the Court."
DK = "No. 14-50123"
dec(5, CA5, 20150601, XTEXT)
cite.append(("123 f3d 456", 5))
window(XTEXT, XTEXT.index(DK), XTEXT.index(DK) + len(DK))
dec(7, SCOTUS, 20150301, "Doe v. Roe. Opinion.")
cite.append(("576 us 900", 7))

DISP = ("The judgment is vacated, and the case is remanded for further consideration in light of Doe v. Roe, "
        "576 U. S. 900 (2015).")
OSPAN = "in light of Doe v. Roe, 576 U. S. 900 (2015)"
TIE = "Doe v. Roe, 576 U. S. 900"


def good_q(n):
    return ("The Supreme Court vacated our judgment, 577 U. S. %d (2016), and remanded for further consideration in "
            "light of Doe v. Roe." % (1000 + n))


def rcase(n, verdict, noremand, bquote=None, bcourt=CA5, bdate=20160601, part="majority", tspan=DK, docket="14-50123",
          bnode=True, badhash=False, ospan=OSPAN, tie=TIE):
    """A history row: O (node 100+n) vacates X (node 5); its remand line names B (node 200+n)."""
    o, b = 100 + n, 200 + n
    otext = "No. 15-%d. Smith v. Jones, 123 F. 3d 456. %s" % (n, DISP)
    dec(o, SCOTUS, 20160111, otext)
    cite.append(("577 us %d" % (1000 + n), o))
    s = otext.index(DISP)
    rid = "h10:%d:5:vacated" % o
    history.append((rid, 5, o, 20160111, "vacated", "all", sha(otext), s, s + len(DISP), DISP, "cite:123 f3d 456",
                    part, "r10:fixture"))
    window(otext, 0, len(otext), 0)
    if bquote is not None:
        btext = ("On remand from the Supreme Court of the United States. %s. Before Smith, Circuit Judge. %s We "
                 "reinstate our judgment." % (DK, bquote))
        if badhash:
            bad_hash.add(sha(btext))
        if bnode:
            dec(b, bcourt, bdate, btext)
        q, d = btext.index(bquote), btext.index(DK)
        t = XTEXT.index(tspan)
        window(btext, q, q + len(bquote))
        window(btext, d, d + len(DK))
        window(XTEXT, t, t + len(tspan))
        o0 = otext.index(ospan)
        remands.append((rid, b, q, q + len(bquote), docket, d, d + len(DK), t, t + len(tspan), tie, o0,
                        o0 + len(ospan)))
    expected.append(("history", rid, verdict, verdict))
    expected_n.append(("history", rid, noremand, noremand))
    return rid


rid_g = rcase(1, "ok", "ok", good_q(1))
rcase(2, "remandCourt", "ok", good_q(2), bcourt=NDGA)
rcase(3, "remandDate", "ok", good_q(3), bdate=20151201)
rcase(4, "remandDocket", "ok", good_q(4), tspan="Smith v. Jones.")
rcase(5, "remandCue", "ok", "The Court vacated our judgment, 577 U. S. 1005 (2016), and remanded.")
rcase(6, "remandTie", "ok",
      "The Supreme Court vacated our judgment and remanded for further consideration in light of Doe v. Roe.")
rcase(7, "remandTie", "ok", "The Supreme Court vacated our judgment in No. 14-50123 and remanded.")  # D10-7
rcase(8, "ok", "ok", "On January 11, 2016, the Supreme Court vacated our judgment and remanded.")
rcase(9, "partNotMajority", "partNotMajority", good_q(9), bcourt=NDGA, part="dissent")
rcase(10, "remandDocket", "ok", good_q(10), badhash=True)
LONG = ("The Supreme Court vacated our judgment, 577 U. S. 1011 (2016), and remanded" +
        ", the panel considering the matter with care and at length" * 12 + ".")
rcase(11, "remandCue", "ok", LONG)
rcase(12, "remandCourt", "ok", good_q(12), bnode=False)
rcase(13, "remandDocket", "ok", good_q(13), docket="")
rcase(14, "ok", "ok", "On Jan. 11, 2016, the Supreme Court vacated and remanded the case to us.")
rcase(15, "ok", "ok", None)   # a row without a remand line: unchanged
# D10-7 (c2): the reason case in O's span and in B's quote; the tie string in B's quote only
RQ = "The Supreme Court vacated our judgment and remanded in light of Doe v. Roe, 576 U. S. 900 (2015)."
rcase(16, "ok", "ok", RQ)
rcase(17, "remandTie", "ok", RQ, ospan="No. 15-17.")
rcase(18, "remandTie", "ok", RQ, tie="Doe v. Roe")
# table rules: a second line for row 1 (duplicate), an unknown id, a non-numeric node, a line of 8 fields
remands.append((rid_g, 299, 0, 5, "14-50123", 0, 5, 0, 5, "", 0, 0))
remands.append(("h10:999:5:vacated", 201, 0, 5, "14-50123", 0, 5, 0, 5, "", 0, 0))
remands.append((rid_g, "b", 0, 5, "14-50123", 0, 5, 0, 5, "", 0, 0))
remands.append((rid_g, 201, 0, 5, "14-50123", 0, 5, 0, 5))
remands.append((rid_g, 201, 0, 5, "14-50123", 0, 5, 0, 5, "", "x", 0))

for d, mode in ((DATA, "remand"), (os.path.join(HERE, "data_noremand"), "none"),
                (os.path.join(HERE, "data_emptyremand"), "empty")):
    shutil.rmtree(d, ignore_errors=True)
    write("courts2.tsv", courts, d)
    write("decisions2.tsv", sorted(decisions), d)
    write("treatments.tsv", [], d)
    write("history.tsv", history, d)
    write("cert_text.tsv", cert_text, d)
    write("window_sha.tsv", sorted(window_sha), d)
    write("cite_index.tsv", cite, d)
    write("system_rules.tsv", [(0, "horizontal", "strong", 0, 99999999, "fixture", "S")], d)
    if mode == "remand":
        write("history_remand.tsv", remands, d)
    elif mode == "empty":
        write("history_remand.tsv", [], d)
write("edges-00.tsv", [], EDGES)
hdr = [("table", "id", "result_all", "result_firm")]
write("expected_certs.tsv", hdr + sorted(expected), HERE)
write("expected_certs_noremand.tsv", hdr + sorted(expected_n), HERE)
# counters, from the rows above, independently of the runner (Q10-9 / LEAN10 L10-10, L10-11)
hids = {h[0] for h in history}
nor = {e[1]: e[2] for e in expected_n}
ver = {e[1]: e[2] for e in expected}
kept, dup, bad = {}, 0, 0
for r in remands:
    if len(r) != 12 or not all(isinstance(r[i], int) for i in (1, 2, 3, 5, 6, 7, 8, 10, 11)):
        bad += 1
    elif r[0] not in hids:
        continue
    elif r[0] in kept:
        dup += 1
    else:
        kept[r[0]] = r
checked = [r for r in kept if nor[r] in ("ok", "okUnverifiedBy")]
write("expected_remand_summary.tsv", [
    ("remand_lines", len(kept)), ("remand_checked_rows", len(checked)),
    ("remand_failed_rows", sum(1 for r in checked if ver[r] not in ("ok", "okUnverifiedBy"))),
    ("remand_dup_rows", dup), ("remand_bad_rows", bad), ("bad_rows", "history_remand.tsv", bad)], HERE)
print("history", len(history), "remand lines", len(remands))
