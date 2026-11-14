"""Round 9 batch-2 fixture: far joined antecedents (DESIGN9 section 5, claim joinedFar) and implicit rejection
(section 7, claim implicitReject).

    python make_farimplicit_fixture.py      writes data/, data_noclaim/, edges/, expected_certs*.tsv here

Synthetic decisions only (no corpus text, no answer key). Every acting decision has its own text; the narrow windows
of round 7 (a few characters around each quote) plus, where a row needs it, one window over the whole text (so the
gap between a far joined quote and the act is covered). data_noclaim/ is the same data without the two new claim
lines: the round-8 checks (expected_certs_noclaim.tsv). The paragraph test cannot be exercised here (a window line of
cert_text.tsv holds no newline); `Examples.lean` covers it.
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SCOTUS = 2906


def sha(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def write(name, rows, d):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


courts = [(SCOTUS, 0, 99999999, "Supreme Court of the United States", 0, "L", "all", 0, 0, "fixture", "S")]
targets = [(0, SCOTUS, 19000101, "Smith v. Jones. Opinion of the Court.", "100 us 1"),
           (6, SCOTUS, 19050101, "Doe v. Roe. Opinion of the Court.", "300 us 3"),
           (7, SCOTUS, 19200101, "Green v. Black. Opinion of the Court.", "400 us 4")]
decisions = [(n, c, d, 0, "panel", "published", "full", sha(t), "fixture") for n, c, d, t, _ in targets]
treatments, classes, joined, cert_text, window_sha, expected, expected_nc = [], [], [], [], [], [], []
seen = set()


def window(text, s, e, margin=8):
    s0, e0 = max(0, s - margin), min(len(text), e + margin)
    if (sha(text), s0, e0) in seen:
        return
    seen.add((sha(text), s0, e0))
    cert_text.append((sha(text), s0, e0, text[s0:e0]))
    window_sha.append((sha(text), s0, e0, sha(text[s0:e0]), "fixture"))


FILL = "The facts are not in dispute and need no restatement here. " * 8
SMITH = "In Smith v. Jones, 100 U. S. 1, this Court held that a State may tax the mails."
ACT = "That case is overruled."


def tcase(node, parts, main, verdict, noclaim, joins=(), kind="overruled", target=0, evidence="cite:100 us 1",
          part="majority", claim=None, whole=False):
    text = " ".join(parts)
    decisions.append((node, SCOTUS, 19500101, 0, "wholeCourt", "published", "full", sha(text), "fixture"))
    s = text.index(main)
    rid = "t9:%d:%d:%d" % (node, target, s)
    treatments.append((rid, node, target, 19500101, kind, "all", "unknown", 1, sha(text), s, s + len(main), main,
                       evidence, part, "fixture", "1"))
    window(text, s, s + len(main))
    if whole:
        window(text, 0, len(text), 0)
    for q in joins:
        a = text.index(q)
        joined.append((rid, "treatments", "antecedent", a, a + len(q), q, "majority", "-", "r9:fixture"))
        window(text, a, a + len(q))
    if claim:
        classes.append((rid, claim, "-", "-", "r9:fixture"))
    expected.append(("treatment", rid, verdict, verdict))
    expected_nc.append(("treatment", rid, noclaim, noclaim))
    return rid, text


# ---- far antecedents (claim joinedFar): the cases named some 480 characters before the act
_, t110 = tcase(110, ["No. 110.", SMITH, FILL, ACT], ACT, "ok", "joinedRelation", [SMITH], claim="joinedFar", whole=True)
print("gap of row 110:", t110.index(ACT) - (t110.index(SMITH) + len(SMITH)))
tcase(111, ["No. 111.", SMITH, FILL, "See Doe v. Roe, 300 U. S. 3, at 4.", ACT], ACT, "joinedFarKey", "joinedRelation",
      [SMITH], claim="joinedFar", whole=True)
tcase(112, ["No. 112.", SMITH, FILL * 3, ACT], ACT, "joinedFarGap", "joinedRelation", [SMITH], claim="joinedFar",
      whole=True)
tcase(113, ["No. 113.", SMITH, FILL, ACT], ACT, "joinedFarWindow", "joinedRelation", [SMITH], claim="joinedFar")
# a near antecedent under the claim: unchanged
tcase(114, ["No. 114.", SMITH, "We now hold otherwise.", ACT], ACT, "ok", "ok", [SMITH], claim="joinedFar")
# the far row without the claim
tcase(115, ["No. 115.", SMITH, FILL, ACT], ACT, "joinedRelation", "joinedRelation", [SMITH], whole=True)

# ---- implicit rejection (claim implicitReject): soft rows of Green v. Black
IQ = "We are unpersuaded by the reasoning of Green v. Black, 400 U. S. 4."
G = dict(target=7, evidence="cite:400 us 4")
tcase(120, ["No. 120.", FILL, IQ, "The judgment is affirmed."], IQ, "ok", "noCue", kind="declinedToFollow",
      claim="implicitReject", **G)
tcase(121, ["No. 121.", FILL, IQ, "The judgment is affirmed."], IQ, "implicitBadKind", "noCue", kind="overruled",
      claim="implicitReject", **G)
DQ = "We doubt the reasoning of Green v. Black, 400 U. S. 4."
tcase(122, ["No. 122.", FILL, DQ], DQ, "ok", "ok", kind="questioned", claim="implicitReject", **G)
tcase(123, ["No. 123.", FILL, IQ], IQ, "partNotMajority", "noCue", kind="declinedToFollow", part="dissent",
      claim="implicitReject", **G)
tcase(124, ["No. 124.", FILL, IQ], IQ, "noCue", "noCue", kind="declinedToFollow", **G)

cite = [(c, n) for n, _, _, _, c in targets]
for d, with_claims in ((DATA, True), (os.path.join(HERE, "data_noclaim"), False)):
    shutil.rmtree(d, ignore_errors=True)
    write("courts2.tsv", courts, d)
    write("decisions2.tsv", sorted(decisions), d)
    write("treatments.tsv", treatments, d)
    write("treatment_class.tsv", classes if with_claims else [], d)
    write("joined.tsv", joined, d)
    write("history.tsv", [], d)
    write("cert_text.tsv", cert_text, d)
    write("window_sha.tsv", sorted(window_sha), d)
    write("cite_index.tsv", cite, d)
    write("system_rules.tsv", [(0, "horizontal", "strong", 0, 99999999, "fixture", "S")], d)
write("edges-00.tsv", [], os.path.join(HERE, "edges"))
hdr = [("table", "id", "result_all", "result_firm")]
write("expected_certs.tsv", hdr + sorted(expected), HERE)
write("expected_certs_noclaim.tsv", hdr + sorted(expected_nc), HERE)
print("rows", len(treatments), "claims", len(classes))
