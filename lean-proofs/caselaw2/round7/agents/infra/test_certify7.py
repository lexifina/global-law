"""Unit tests of round7/certify7.py's check functions on synthetic texts (no git, no tables).

    python -X utf8 round7/agents/infra/test_certify7.py
Every new rule of DESIGN7 sections 2-3 is exercised once passing and once per failure it defines (the mutants of
DESIGN7 3.4 that a certifier can show: gap bound, anaphor, evidence in the joined quote only, tie cue, label in both,
third joined line, orderHead court / date / order line, setAside on another kind).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import certify7 as C7  # noqa: E402

CUES, SRC = C7.load_cues()
FAILS = []
N = [0]


def expect(name, got, want):
    N[0] += 1
    if got != want:
        FAILS.append("%s: got %r, want %r" % (name, got, want))


def span_of(text, s):
    i = text.index(s)
    return [i, i + len(s)]


def trow(text, main, ev, kind="overruled", claim="-", joined=(), part="majority", ordered=True, cite_fail=""):
    js = []
    for j in joined:
        js.append({"rel": j[0], "span": span_of(text, j[1]) if isinstance(j[1], str) else list(j[1]),
                   "part": j[2] if len(j) > 2 else "majority",
                   "label": C7.canon_label(j[3]) if len(j) > 3 else "-"})
    return {"table": "treatments", "kind": kind, "claim": claim, "main": span_of(text, main), "ev": ev, "part": part,
            "ordered": ordered, "cite_fail": cite_fail, "joined": js}


def treat(text, *a, **k):
    return C7.check_treat(trow(text, *a, **k), text, CUES)[0]


def hrow(text, main, kind, claim="-", part="majority", scotus=True, date=20150105, ev="name:self", self_text=True):
    return {"table": "history", "kind": kind, "claim": claim, "main": span_of(text, main), "ev": ev, "part": part,
            "anchor": None, "anchor_part": "", "self_text": self_text, "cite_fail": "", "ordered": True,
            "by_scotus": scotus, "by_date": date}


def hist(text, *a, **k):
    return C7.check_hist(hrow(text, *a, **k), text, CUES)[0]


def main():
    pre = "Background text. " * 30
    j1 = "In Smith v. Jones, 100 U.S. 1, the Court held that a seller is liable."
    m1 = "Those cases are overruled."
    text = pre + j1 + " " + m1 + " " + "More text follows here. " * 30
    ev = "cite:100 us 1"
    # antecedent (class i)
    expect("antecedent ok", treat(text, m1, ev, joined=[("antecedent", j1)]), None)
    expect("antecedent: evidence also resolves without joined in plain mode", treat(text, m1, ev), None)
    far = pre + j1 + " " + ("Filler sentence here. " * 20) + m1 + " " + "Tail. " * 80
    expect("gap > 300", treat(far, m1, ev, joined=[("antecedent", j1)]), "joinedRelation")
    after = pre + m1 + " " + j1 + " " + "Tail. " * 80
    expect("joined after the main quote", treat(after, m1, ev, joined=[("antecedent", j1)]), "joinedRelation")
    m_noana = "The decision is overruled."
    t2 = pre + j1 + " " + m_noana + " " + "Tail. " * 80
    expect("no anaphor", treat(t2, m_noana, ev, joined=[("antecedent", j1)]), "joinedRelation")
    m_nocue = "Those cases are distinguished on their facts."
    t3 = pre + j1 + " " + m_nocue + " " + "Tail. " * 80
    expect("no overruling cue in main", treat(t3, m_nocue, ev, joined=[("antecedent", j1)]), "joinedRelation")
    j_noev = "In an earlier case the Court held that a seller is liable."
    t4 = "Smith v. Jones, 100 U.S. 1. " + pre + j_noev + " " + m1 + " " + "Tail. " * 80
    expect("evidence only in the window", treat(t4, m1, ev, joined=[("antecedent", j_noev)]), "joinedUnresolved")
    m_ev = "Those cases, Smith v. Jones, 100 U.S. 1, are overruled."
    t5 = pre + j_noev + " " + m_ev + " " + "Tail. " * 80
    expect("evidence only in the main quote", treat(t5, m_ev, ev, joined=[("antecedent", j_noev)]),
           "joinedUnresolved")
    expect("joined part dissent", treat(text, m1, ev, joined=[("antecedent", j1, "dissent")]), "joinedPart")
    expect("joined part headmatter", treat(text, m1, ev, joined=[("antecedent", j1, "headmatter")]), "joinedPart")
    expect("joined span outside", treat(text, m1, ev, joined=[("antecedent", (len(text) - 5, len(text) + 5))]),
           "joinedMismatch")
    expect("joined span empty", treat(text, m1, ev, joined=[("antecedent", (10, 10))]), "joinedMismatch")
    j_dq = "On the point of error raised in Smith v. Jones, 100 U.S. 1, the Court held that a seller is liable."
    t6 = pre + j_dq + " " + m1 + " " + "Tail. " * 80
    expect("joined disqualifier", treat(t6, m1, ev, joined=[("antecedent", j_dq)]), "joinedDisqualified")
    expect("cite index failure", treat(text, m1, ev, joined=[("antecedent", j1)], cite_fail="index gives node 9"),
           "joinedUnresolved")
    expect("main quote part", treat(text, m1, ev, joined=[("antecedent", j1)], part="concurrence"),
           "partNotMajority")
    expect("main quote date order", treat(text, m1, ev, joined=[("antecedent", j1)], ordered=False), "targetLater")
    # doctrine (class ii)
    jd = "The doctrine of implied consent was first announced in Smith v. Jones, 100 U.S. 1."
    md = "The doctrine of implied consent has no place in our law."
    td = pre + jd + " " + "Middle. " * 200 + md + " " + "Tail. " * 80
    D = "doctrine of implied consent"
    expect("doctrine ok", treat(td, md, ev, kind="disapproved", claim="doctrine", joined=[("doctrineTie", jd,
                                                                                           "majority", D)]), None)
    expect("doctrine ok, label case/spacing canonical",
           treat(td, md, ev, kind="disapproved", claim="doctrine", joined=[("doctrineTie", jd, "majority",
                                                                             "Doctrine of Implied Consent")]), None)
    expect("doctrine on kind overruled", treat(td, md, ev, kind="overruled", claim="doctrine",
                                               joined=[("doctrineTie", jd, "majority", D)]), "doctrineBadRow")
    expect("doctrine without a tie line", treat(td, md, ev, kind="disapproved", claim="doctrine"), "doctrineBadRow")
    expect("doctrineTie without the claim", treat(td, md, ev, kind="disapproved",
                                                  joined=[("doctrineTie", jd, "majority", D)]), "joinedRelation")
    expect("label of one word", treat(td, md, ev, kind="disapproved", claim="doctrine",
                                      joined=[("doctrineTie", jd, "majority", "doctrine")]), "joinedRelation")
    expect("label not in main", treat(td, md, ev, kind="disapproved", claim="doctrine",
                                      joined=[("doctrineTie", jd, "majority", "implied consent was")]),
           "joinedRelation")
    jd2 = "Implied consent came from Smith v. Jones, 100 U.S. 1."
    td2 = pre + jd2 + " " + "Middle. " * 200 + md + " " + "Tail. " * 80
    expect("no tie phrase in joined", treat(td2, md, ev, kind="disapproved", claim="doctrine",
                                            joined=[("doctrineTie", jd2, "majority", "implied consent")]),
           "joinedRelation")
    md_nocue = "The doctrine of implied consent is ancient."
    td3 = pre + jd + " " + "Middle. " * 200 + md_nocue + " " + "Tail. " * 80
    expect("doctrine main without a reject cue", treat(td3, md_nocue, ev, kind="disapproved", claim="doctrine",
                                                        joined=[("doctrineTie", jd, "majority", D)]), "noCue")
    md_dq = "We reject the argument that the doctrine of implied consent applies."
    td4 = pre + jd + " " + "Middle. " * 200 + md_dq + " " + "Tail. " * 80
    expect("doctrine main with an operative disqualifier", treat(td4, md_dq, ev, kind="disapproved",
                                                                  claim="doctrine",
                                                                  joined=[("doctrineTie", jd, "majority", D)]),
           "disqualified")
    jop = "The argument in Smith v. Jones, 100 U.S. 1, was that a seller is liable."
    mop = "We reject that rule today and repudiate that case."
    top = pre + jop + " " + mop + " " + "Tail. " * 80
    expect("L7-5: an operative disqualifier in a joined quote does not disqualify it",
           treat(top, mop, ev, kind="disapproved", claim="operativeWords", joined=[("antecedent", jop)]),
           "joinedRelation")
    jq2 = "The dissent says Smith v. Jones, 100 U.S. 1, held that a seller is liable."
    t7 = pre + jq2 + " " + m1 + " " + "Tail. " * 80
    expect("disqualify_joined phrase", treat(t7, m1, ev, joined=[("antecedent", jq2)]), "joinedDisqualified")
    # operativeWords
    mo = "We reject the rule of Smith v. Jones, 100 U.S. 1, in its entirety."
    to = pre + mo + " " + "Tail. " * 80
    expect("operative ok", treat(to, mo, ev, kind="disapproved", claim="operativeWords"), None)
    expect("operative on overruled", treat(to, mo, ev, kind="overruled", claim="operativeWords"), "operativeBadRow")
    mo2 = "We reject the rule of that case in its entirety."
    to2 = "Smith v. Jones, 100 U.S. 1. " + pre[:200] + mo2 + " " + "Tail. " * 80
    expect("operative evidence must be in the quote", treat(to2, mo2, ev, kind="disapproved",
                                                            claim="operativeWords"), "targetUnresolved")
    # plain
    expect("plain evidence in the window", treat(to2, "Tail. Tail.", ev, kind="followed"), "noCue")
    # parse: a third joined line is a badRow
    try:
        C7.parse_row({"rule": "x", "table": "treatments", "by": 2, "target": 1, "kind": "overruled",
                      "main": [0, 5], "part": "majority", "ev": ev,
                      "joined": [{"rel": "antecedent", "span": [0, 1]}] * 3}, set(CUES["treat"]), set(CUES["hist"]))
        expect("third joined line", "parsed", "badRow")
    except ValueError:
        expect("third joined line", "badRow", "badRow")
    sar = "The judgment of the Court of Appeals is set aside."
    tsr = "X. " + sar + " Y."
    expect("setAside on reversed: no effect (L7-11)", hist(tsr, sar, "reversed", claim="setAside"), "noCue")
    # history claims
    oh = "Petition for writ of certiorari denied."
    th = "In re Order. " + oh + " Tail."
    expect("orderHead ok", hist(th, oh, "certDenied", claim="orderHead", part="headmatter"), None)
    expect("headmatter without the claim", hist(th, oh, "certDenied", part="headmatter"), "partNotMajority")
    expect("orderHead, not the Supreme Court", hist(th, oh, "certDenied", claim="orderHead", part="headmatter",
                                                    scotus=False), "orderHeadNotAllowed")
    expect("orderHead, before 2013", hist(th, oh, "certDenied", claim="orderHead", part="headmatter",
                                          date=20121231), "orderHeadNotAllowed")
    oh2 = "Petition for writ of certiorari to the Supreme Judicial Court of Maine denied."
    th2 = "X. " + oh2 + " Y."
    expect("orderHead, no order line form", hist(th2, oh2, "certDenied", claim="orderHead", part="headmatter"),
           "orderHeadNotAllowed")
    expect("orderHead with part majority: plain rule", hist(th2, oh2, "certDenied", claim="orderHead"), None)
    ohl = "Petition for writ of certiorari denied. " + "Names of the parties and counsel. " * 12
    thl = "X. " + ohl + " Y."
    expect("orderHead, quote > 400", hist(thl, ohl.strip(), "certDenied", claim="orderHead", part="headmatter"),
           "orderHeadNotAllowed")
    expect("orderHead with part dissent", hist(th, oh, "certDenied", claim="orderHead", part="dissent"),
           "partNotMajority")
    sa = "The judgment of the Court of Appeals is set aside and the case is remanded."
    ts = "X. " + sa + " Y."
    expect("set aside without the claim", hist(ts, sa, "vacated"), "noCue")
    expect("set aside with the claim", hist(ts, sa, "vacated", claim="setAside"), None)
    print("cue sources:", {k: v for k, v in SRC.items() if v != "cue_table.json"})
    print("%d checks, %d failed" % (N[0], len(FAILS)))
    for f in FAILS:
        print("FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
