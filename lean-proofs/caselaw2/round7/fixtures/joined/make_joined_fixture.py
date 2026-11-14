"""Round 7 fixture: joined certificates, doctrine rows, history claims (round7/DESIGN7.md sections 1-3, LEAN7.md).

    python make_joined_fixture.py        writes data/, data_nojoined/, edges/, expected_*.tsv here

Synthetic decisions only (no corpus text, no answer key). Every acting decision has its own text; windows are cut
narrow (a few characters around each quote) so that a citation outside a quote's window is outside the one-quote
certificate, as it is when two sentences are far apart in a real opinion. One row passes each new rule; one row
fails each new reason code; a few rows show that check 6 is the row's own check and that the tables' own rules
(two lines per id, unknown ids, history and witness lines, repeated claims, malformed lines) are counted.

data_nojoined/ is the same data without joined.tsv and history_claim.tsv and without the doctrine class lines: the
round-6 checks (expected_certs_nojoined.tsv).
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
EDGES = os.path.join(HERE, "edges")
SCOTUS, CA5, NOCOURT = 2906, 346, 9999


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
]
# targets: (node, court, date, text, citation)
targets = [
    (0, SCOTUS, 19000101, "Smith v. Jones. Opinion of the Court.", "100 us 1"),
    (1, SCOTUS, 19100101, "Brown v. White. Opinion of the Court.", "200 us 2"),
    (2, SCOTUS, 18960518, "Plessy v. Ferguson. Opinion of the Court.", "163 us 537"),
    (3, SCOTUS, 19190303, "Schenck v. United States. Opinion of the Court.", "249 us 47"),
    (4, SCOTUS, 19190601, "Abrams v. United States. Opinion of the Court.", "250 us 616"),
    (5, CA5, 20130601, "Doe v. Roe. Affirmed.", "500 f3d 1"),
]
decisions = [(n, c, d, 0, "panel", "published", "full", sha(t), "fixture") for n, c, d, t, _ in targets]
treatments, classes, joined, witness, history, anchors, hclaims = [], [], [], [], [], [], []
cert_text, window_sha, expected, expected_nj, expected_classes = [], [], [], [], []
win_seen = set()


def window(text, s, e, margin=8, bad_hash=False):
    s0, e0 = max(0, s - margin), min(len(text), e + margin)
    key = (sha(text), s0, e0)
    if key in win_seen:
        return
    win_seen.add(key)
    cert_text.append((sha(text), s0, e0, text[s0:e0]))
    window_sha.append((sha(text), s0, e0, "0" * 40 if bad_hash else sha(text[s0:e0]), "fixture"))


FILL = "The facts are not in dispute and need no restatement here. " * 8
SMITH = "In Smith v. Jones, 100 U. S. 1, this Court held that a State may tax the mails."
ACT = "That case is overruled."


def tcase(node, parts, main, verdict, joins=(), kind="overruled", target=0, evidence="cite:100 us 1", part="majority",
          court=SCOTUS, date=19500101, claim=None, doctrine="-", field="-", explicit=1, nojoined=None, margin=8):
    """One acting decision `node` with one treatments row. joins: dicts q, rel, part, label, shift, bad_hash,
    nowin (no window cut), at (offset override: another text's offset)."""
    text = " ".join(parts)
    decisions.append((node, court, date, 0, "wholeCourt", "published", "full", sha(text), "fixture"))
    s = text.index(main)
    rid = "t7:%d:%d:%d" % (node, target, s)
    treatments.append((rid, node, target, date, kind, "all", "unknown", explicit, sha(text), s, s + len(main), main,
                       evidence, part, "fixture", "1"))
    window(text, s, s + len(main), margin)
    for j in joins:
        q = j["q"]
        a = j["at"] if "at" in j else text.index(q)
        sh = j.get("shift", 0)
        joined.append((rid, "treatments", j.get("rel", "antecedent"), a + sh, a + sh + len(q), q,
                       j.get("part", "majority"), j.get("label", "-"), "r7:fixture"))
        if not j.get("nowin"):
            window(text, a, a + len(q), margin, bad_hash=j.get("bad_hash", False))
    if claim:
        classes.append((rid, claim, field, doctrine, "r7:fixture"))
    expected.append(("treatment", rid, verdict, verdict))
    expected_nj.append(("treatment", rid, nojoined or verdict, nojoined or verdict))
    return rid, text


# ---------------------------------------------------------------- antecedent rows (class (i))
# the admitted row: the cases in one sentence, the act two sentences later; without the line the act names nothing
rid_a, text_a = tcase(10, ["Mr. Justice X delivered the opinion of the Court.", FILL, SMITH, "We now hold otherwise.", ACT,
                           FILL], ACT, "ok", [{"q": SMITH}], nojoined="targetUnresolved")
# the same row whose only joined line is malformed (a non-numeric offset): checked as before
rid_b, _ = tcase(11, ["Mr. Justice Y delivered the opinion of the Court.", FILL, SMITH, "We now hold otherwise.", ACT],
                 ACT, "targetUnresolved")
joined.append((rid_b, "treatments", "antecedent", "x", 5, SMITH, "majority", "-", "r7:fixture-malformed"))
joined.append((rid_b, "treatments", "antecedant", 0, 5, SMITH, "majority", "-", "r7:fixture-unknown-rel"))
# check 1: offset shifted; the joined window's hash wrong; the joined quote of another text (row 10's offset)
tcase(12, ["No. 12.", FILL, SMITH, "We now hold otherwise.", ACT], ACT, "joinedMismatch", [{"q": SMITH, "shift": 3}],
      nojoined="targetUnresolved")
tcase(13, ["No. 13.", FILL, SMITH, "We now hold otherwise.", ACT], ACT, "joinedMismatch", [{"q": SMITH, "bad_hash": True}],
      nojoined="targetUnresolved")
tcase(14, ["Mr. Justice Z delivered the opinion of the Court.", FILL + "Here the facts differ in several respects.",
           "We now hold otherwise.", ACT], ACT, "joinedMismatch",
      [{"q": SMITH, "at": text_a.index(SMITH), "nowin": True}], nojoined="targetUnresolved")
# check 2: a dissent's sentence; check 3: a dissent's account
tcase(15, ["No. 15.", FILL, SMITH, "We now hold otherwise.", ACT], ACT, "joinedPart", [{"q": SMITH, "part": "dissent"}],
      nojoined="targetUnresolved")
DIS = "As the dissent notes, in Smith v. Jones, 100 U. S. 1, this Court held that a State may tax the mails."
tcase(16, ["No. 16.", FILL, DIS, "We now hold otherwise.", ACT], ACT, "joinedDisqualified", [{"q": DIS}],
      nojoined="targetUnresolved")
# check 4: too far before the act; no anaphor in the act
tcase(17, ["No. 17.", SMITH, FILL, "We now hold otherwise.", ACT], ACT, "joinedRelation", [{"q": SMITH}],
      nojoined="targetUnresolved")
NOANA = "The tax rule of the mails is overruled."
tcase(18, ["No. 18.", FILL, SMITH, "We now hold otherwise.", NOANA], NOANA, "joinedRelation", [{"q": SMITH}],
      nojoined="targetUnresolved")
# check 5: the citation is in the act's window but not in the joined quote
HELD = "this Court held that a State may tax the mails."
tcase(19, ["No. 19.", FILL, "We decided Smith v. Jones, 100 U. S. 1, long ago; there", HELD, ACT], ACT,
      "joinedUnresolved", [{"q": HELD}], margin=60, nojoined="ok")
# two lines (the second carries the citation); a third line for the id is ignored (joined_extra)
BOTH = "Both decisions rested on the same reasoning."
rid_k, _ = tcase(20, ["No. 20.", FILL, SMITH, BOTH, "Those cases are overruled."], "Those cases are overruled.", "ok",
                 [{"q": BOTH}, {"q": SMITH}, {"q": BOTH}], nojoined="targetUnresolved")
# check 6: the act is a dissent's; the acting court has no epoch (power unverified)
tcase(21, ["No. 21.", FILL, SMITH, "We now hold otherwise.", ACT], ACT, "partNotMajority", [{"q": SMITH}],
      part="dissent", nojoined="targetUnresolved")     # without the line: the evidence test comes before the part test
tcase(22, ["No. 22.", FILL, SMITH, "We now hold otherwise.", ACT], ACT, "okUnverifiedBy", [{"q": SMITH}],
      court=NOCOURT, nojoined="targetUnresolved")
# an operative-words row with a joined line: its own check is the operative check (whole case: not demoted)
OPACT = "Those decisions are disapproved and are no longer good law."
tcase(23, ["No. 23.", FILL, SMITH, OPACT], OPACT, "ok", [{"q": SMITH}], kind="disapproved", claim="operativeWords",
      nojoined="targetUnresolved")
# an operative act without a cue of its kind's plain list ("disapprov"): the antecedent relation fails (LEAN7 L7-13)
OPACT2 = "Those decisions are no longer good law."
tcase(24, ["No. 24.", FILL, SMITH, OPACT2], OPACT2, "joinedRelation", [{"q": SMITH}], kind="disapproved",
      claim="operativeWords", nojoined="targetUnresolved")

# ---------------------------------------------------------------- doctrine rows (class (ii))
TIE = ("The doctrine of \"separate but equal\" did not make its appearance in this Court until 1896 in the case of "
       "Plessy v. Ferguson, 163 U. S. 537, involving not education but transportation.")
DMAIN = "We conclude that in the field of public education the doctrine of \"separate but equal\" has no place."
PLESSY = dict(target=2, evidence="cite:163 us 537", kind="disapproved", date=19540517)


def drow(node, parts, main, verdict, joins, claim="doctrine", nojoined=None, **kw):
    args = dict(PLESSY)
    args.update(kw)
    return tcase(node, parts, main, verdict, joins, claim=claim, doctrine="separate but equal",
                 field="public education", nojoined=nojoined, **args)


TIEJ = {"q": TIE, "rel": "doctrineTie", "label": "separate but equal"}
rid_d, _ = drow(30, [TIE, FILL, DMAIN], DMAIN, "ok", [TIEJ], nojoined="noCue")
drow(31, [TIE, FILL, DMAIN], DMAIN, "doctrineBadRow", [], nojoined="noCue")
drow(32, [TIE, FILL, DMAIN], DMAIN, "doctrineBadRow", [TIEJ], kind="overruled", nojoined="noCue")
NOTIE = "Plessy v. Ferguson, 163 U. S. 537, upheld \"separate but equal\" railway cars."
drow(33, [NOTIE, FILL, DMAIN], DMAIN, "joinedRelation", [{"q": NOTIE, "rel": "doctrineTie", "label": "separate but equal"}],
     nojoined="noCue")
NOLAB = "The rule of Plessy v. Ferguson, 163 U. S. 537, governed railway cars."
drow(34, [NOLAB, FILL, DMAIN], DMAIN, "joinedRelation", [{"q": NOLAB, "rel": "doctrineTie", "label": "separate but equal"}],
     nojoined="noCue")
DARG = "The argument that \"separate but equal\" has no place is rejected."
drow(35, [TIE, FILL, DARG], DARG, "disqualified", [TIEJ], nojoined="noCue")
# one label tied to two targets by two rows: both fail
CPD1 = "The rule of \"clear and present danger\" was first announced in Schenck v. United States, 249 U. S. 47."
CPD2 = "The rule of \"clear and present danger\" was laid down in Abrams v. United States, 250 U. S. 616."
CMAIN = "The test of \"clear and present danger\" has no place in this field."
drow(36, [CPD1, FILL, CMAIN], CMAIN, "doctrineAmbiguous",
     [{"q": CPD1, "rel": "doctrineTie", "label": "clear and present danger"}], target=3, evidence="cite:249 us 47",
     date=19690609, nojoined="noCue")
drow(37, [CPD2, FILL, CMAIN], CMAIN, "doctrineAmbiguous",
     [{"q": CPD2, "rel": "doctrineTie", "label": "Clear and Present Danger"}], target=4, evidence="cite:250 us 616",
     date=19690610, nojoined="noCue")
# a tie line on a row without a doctrine claim
drow(38, [TIE, FILL, DMAIN], DMAIN, "joinedRelation", [TIEJ], claim=None, nojoined="noCue")

# ---------------------------------------------------------------- a witness row: its joined line is ignored
rid_w, _ = tcase(39, ["No. 39.", FILL, SMITH, "We now hold otherwise.", ACT], ACT, "witnessBadRow", explicit=0,
                 nojoined="witnessBadRow")
witness.append((rid_w, 77777, "cite:200 us 2", "fixture"))
joined.append((rid_w, "treatments", "antecedent", 0, 5, "No. 3", "majority", "-", "r7:fixture-witness"))
joined.append(("t7:99:0:0", "treatments", "antecedent", 0, 5, "No. 3", "majority", "-", "r7:fixture-unknown"))


# ---------------------------------------------------------------- history claims
def hcase(node, text, disp, verdict, claims=(), kind="certDenied", part="headmatter", court=SCOTUS, date=20140106,
          evidence="cite:500 f3d 1", margin=60, anchor=None, nojoined=None):
    decisions.append((node, court, date, 0, "wholeCourt", "published", "full", sha(text), "fixture"))
    s = text.index(disp)
    rid = "h7:%d:5:%s" % (node, kind)
    history.append((rid, 5, node, date, kind, "all", sha(text), s, s + len(disp), disp, evidence, part, "r7:fixture"))
    window(text, s, s + len(disp), margin)
    if anchor:
        a = text.index(anchor)
        anchors.append((rid, a, a + len(anchor), anchor, "headmatter", "r6:fixture"))
        window(text, a, a + len(anchor), 8)
    for c in claims:
        hclaims.append((rid, c, "r7:fixture"))
    expected.append(("history", rid, verdict, verdict))
    expected_nj.append(("history", rid, nojoined or verdict, nojoined or verdict))
    return rid


ORDER = "No. 13-%d. Doe v. Roe. C. A. 5th Cir. Certiorari denied. Reported below: 500 F. 3d 1."
rid_h = hcase(50, ORDER % 50, "Certiorari denied.", "ok", ["orderHead"], nojoined="partNotMajority")
LONGCOURT = ("No. 13-51. Doe v. Roe. Petition for writ of certiorari to the United States Court of Appeals for the Fifth "
             "Circuit denied. Reported below: 500 F. 3d 1.")
hcase(51, LONGCOURT, "Petition for writ of certiorari to the United States Court of Appeals for the Fifth Circuit denied.",
      "ok", ["orderHead"], nojoined="partNotMajority")
hcase(52, ORDER % 52, "Certiorari denied.", "orderHeadNotAllowed", ["orderHead"], date=20121001,
      nojoined="partNotMajority")
hcase(53, ORDER % 53, "Certiorari denied.", "orderHeadNotAllowed", ["orderHead"], court=CA5,
      nojoined="partNotMajority")
hcase(54, "No. 13-54. Doe v. Roe. C. A. 5th Cir. Motion for leave to file out of time denied. Reported below: 500 F. 3d 1.",
      "Motion for leave to file out of time denied.", "orderHeadNotAllowed", ["orderHead"], nojoined="partNotMajority")
LONGQ = "Certiorari denied, " + "the petition having been considered with care and at length, " * 7 + "and leave is refused."
hcase(55, "No. 13-55. Doe v. Roe. C. A. 5th Cir. " + LONGQ + " Reported below: 500 F. 3d 1.", LONGQ,
      "orderHeadNotAllowed", ["orderHead"], nojoined="partNotMajority")
hcase(56, ORDER % 56, "Certiorari denied.", "partNotMajority")                       # head matter, no claim
hcase(57, "No. 13-57. Doe v. Roe. C. A. 5th Cir. Reported below: 500 F. 3d 1. " + FILL + "Certiorari denied.",
      "Certiorari denied.", "ok", ["orderHead"], margin=8, anchor="Reported below: 500 F. 3d 1.",
      nojoined="partNotMajority")                                                    # anchored, under the claim
hcase(58, ORDER % 58, "Certiorari denied.", "partNotMajority", ["orderHead"], part="dissent")
hcase(59, "No. 13-59. Doe v. Roe. C. A. 5th Cir. Judgment modified. Reported below: 500 F. 3d 1.",
      "Judgment modified.", "orderHeadNotAllowed", ["orderHead"], kind="modified", nojoined="partNotMajority")
SETA = "In Doe v. Roe, 500 F. 3d 1, the Court of Appeals held for the State. The judgment of the Court of Appeals is set aside."
SDISP = "The judgment of the Court of Appeals is set aside."
hcase(60, SETA, SDISP, "ok", ["setAside"], kind="vacated", part="majority", nojoined="noCue")
hcase(61, SETA + " No. 61.", SDISP, "noCue", ["setAside"], kind="reversed", part="majority")
hcase(62, SETA + " No. 62.", SDISP, "noCue", [], kind="vacated", part="majority")
hcase(63, "In Doe v. Roe, 500 F. 3d 1, the Court of Appeals held for the State. The judgment is vacated.",
      "The judgment is vacated.", "ok", ["setAside", "orderHead"], kind="vacated", part="majority")
# the table's own rules: a repeated (id, claim) line, an unknown id, a malformed line (unknown claim)
hclaims.append((rid_h, "orderHead", "r7:fixture-duplicate"))
hclaims.append(("h7:99:5:certDenied", "orderHead", "r7:fixture-unknown"))
hclaims.append((rid_h, "orderHeads", "r7:fixture-malformed"))
# a history joined line (reserved this round: ignored, counted)
joined.append((rid_h, "history", "antecedent", 0, 5, "No. 1", "majority", "-", "r7:fixture-history"))

# ---------------------------------------------------------------- write
cite = [(c, n) for n, _, _, _, c in targets]
for d, with_r7 in ((DATA, True), (os.path.join(HERE, "data_nojoined"), False)):
    shutil.rmtree(d, ignore_errors=True)
    write("courts2.tsv", courts, d)
    write("decisions2.tsv", sorted(decisions), d)
    write("treatments.tsv", treatments, d)
    write("treatment_witness.tsv", witness, d)
    write("treatment_class.tsv", [c for c in classes if with_r7 or c[1] != "doctrine"], d)
    write("history.tsv", history, d)
    write("history_anchor.tsv", anchors, d)
    write("cert_text.tsv", cert_text, d)
    write("window_sha.tsv", sorted(window_sha), d)
    write("cite_index.tsv", cite, d)
    write("system_rules.tsv", [(0, "horizontal", "strong", 0, 99999999, "fixture", "S")], d)
    if with_r7:
        write("joined.tsv", joined, d)
        write("history_claim.tsv", hclaims, d)
write("edges-00.tsv", [], EDGES)
hdr = [("table", "id", "result_all", "result_firm")]
write("expected_certs.tsv", hdr + sorted(expected), HERE)
write("expected_certs_nojoined.tsv", hdr + sorted(expected_nj), HERE)
# the counters: computed from the rows above, independently of the runner
tids = {t[0] for t in treatments}
wids = {w[0] for w in witness}
hids = {h[0] for h in history}
kept, unknown, extra, hist_ign, wit_ign, bad_j = {}, 0, 0, 0, 0, 0
for j in joined:
    if not isinstance(j[3], int) or j[2] not in ("antecedent", "doctrineTie"):
        bad_j += 1
    elif j[1] == "history":
        if j[0] in hids:
            hist_ign += 1
        else:
            unknown += 1
    elif j[0] not in tids:
        unknown += 1
    elif j[0] in wids:
        wit_ign += 1
    elif len(kept.get(j[0], [])) >= 2:
        extra += 1
    else:
        kept.setdefault(j[0], []).append(j)
verdict = {e[1]: e[2] for e in expected}
adm = sum(1 for r in kept if verdict[r] in ("ok", "okUnverifiedBy"))
claims, unk_c, dup_c, bad_c = {}, 0, 0, 0
for c in hclaims:
    if c[1] not in ("orderHead", "setAside"):
        bad_c += 1
    elif c[0] not in hids:
        unk_c += 1
    elif c[1] in claims.get(c[0], set()):
        dup_c += 1
    else:
        claims.setdefault(c[0], set()).add(c[1])
hadm = sum(1 for r in claims if verdict[r] in ("ok", "okUnverifiedBy"))
docs = [c[0] for c in classes if c[1] == "doctrine"]
write("expected_summary.tsv", [
    ("joined_rows", len(kept)), ("joined_lines", sum(len(v) for v in kept.values())), ("joined_unknown_ids", unknown),
    ("joined_extra", extra), ("joined_history_ignored", hist_ign), ("joined_witness_ignored", wit_ign),
    ("joined_admitted", adm), ("joined_rejected", len(kept) - adm),
    ("hclaim_rows", len(claims)), ("hclaim_unknown_ids", unk_c), ("hclaim_duplicates", dup_c),
    ("hclaim_admitted", hadm), ("hclaim_rejected", len(claims) - hadm),
    ("doctrine_rows", len(docs)), ("doctrine_admitted", sum(1 for r in docs if verdict[r] in ("ok", "okUnverifiedBy"))),
    ("doctrine_ambiguous", sum(1 for r in docs if verdict[r] == "doctrineAmbiguous")),
    ("bad_rows", "joined.tsv", bad_j), ("bad_rows", "history_claim.tsv", bad_c)], HERE)
# classes of the doctrine and operative rows (classes.tsv: id, class, claim, verdict, field_limit, doctrine, witness)
cls = {c[0]: c for c in classes}
rows = []
for t in treatments:
    rid, kind, explicit = t[0], t[4], t[7]
    c = cls.get(rid)
    if c and c[1] == "doctrine" and kind == "disapproved" and explicit == 1:
        rows.append((rid, "doctrine", "doctrine", verdict[rid], c[2], c[3], "-"))
    elif c and c[1] == "operativeWords":
        rows.append((rid, "selfAnnounced" if "disapprov" in t[11].lower() else "operativeWords", "operativeWords",
                     verdict[rid], c[2], c[3], "-"))
write("expected_classes.tsv", sorted(rows), HERE)
print("treatments", len(treatments), "joined lines", len(joined), "history", len(history), "claims", len(hclaims))
