import sys
sys.path.insert(0, r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\tmp")
from common import write_pack, parse

PACK = "pack_T1f_045"
_items, _ = parse(PACK)


def span(iid, start_marker, end_marker):
    w = _items[iid]["window"]
    s = w.index(start_marker)
    e = w.index(end_marker, s) + len(end_marker)
    return w[s:e]


def F(i, reason, xkeys=None, ykeys=None):
    d = {"id": i, "states": False, "reason": reason, "conf": 0.9}
    if xkeys:
        d["xkeys"] = xkeys
    if ykeys:
        d["ykeys"] = ykeys
    return d


def T(i, quote, xkeys, ykeys, conf=0.85, scope="all"):
    return {"id": i, "states": True, "quote": quote, "kind": "overruled", "scope": scope,
            "field_limit": "", "doctrine": "", "conf": conf, "xkeys": xkeys, "ykeys": ykeys}


Q_3460 = span("s03460", "Walton v. Arizona, 497 U. S. 639, 653", "536 U. S. 584 (2002)")
Q_3462 = span("s03462", "Walton, supra, overruled on other grounds", "536 U. S. 584 (2002)")
Q_3461 = span("s03461", "In Ring, we applied", "497 U. S. 639 (1990)")

A = [
    F("s03449", "otherDecision"),
    T("s03460", Q_3460, ["Walton v. Arizona"], ["Ring v. Arizona"], scope="otherGrounds"),
    T("s03461", Q_3461, ["Walton v. Arizona"], ["Ring"], conf=0.8),
    T("s03462", Q_3462, ["Walton"], ["Ring v. Arizona"], scope="otherGrounds"),
    F("s03504", "noStatement"),
    F("s03068", "ownAct"),
    F("s03278", "noStatement"),
    F("s03320", "noStatement"),
    F("s03239", "cannotTell"),
    F("s03644", "noStatement"),
    F("s03256", "noStatement"),
    F("s03587", "noStatement"),
    F("s03158", "noStatement"),
    F("s03189", "noStatement"),
    F("s03192", "noStatement"),
    F("s03139", "noStatement"),
    F("s03624", "noStatement"),
    F("s03177", "noStatement"),
    F("s03279", "noStatement"),
    F("s03280", "noStatement"),
    F("s03316", "noStatement"),
    F("s03317", "noStatement"),
    F("s03693", "noStatement"),
    F("s03700", "noStatement"),
    F("s03184", "negation"),
    F("s03492", "cannotTell"),
    F("s03178", "noStatement"),
    F("s03225", "noStatement"),
    F("s03368", "negation"),
    F("s03387", "noStatement"),
    F("s03634", "noStatement"),
    F("s03285", "notOverruling"),
    F("s03484", "argument"),
    F("s03667", "argument"),
    F("s03206", "noStatement"),
    F("s03226", "noStatement"),
    F("s03324", "noStatement"),
    F("s03552", "noStatement"),
    F("s03553", "noStatement"),
    F("s03671", "noStatement"),
    F("s03436", "argument"),
    F("s03369", "noStatement"),
    F("s03216", "negation"),
    F("s03227", "noStatement"),
    F("s03342", "notMajority"),
    F("s03676", "notMajority"),
    F("s03281", "noStatement"),
    F("s03716", "noStatement"),
    F("s03547", "would"),
    F("s03685", "noStatement"),
]

write_pack(PACK, A)
