import sys
sys.path.insert(0, r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\tmp")
from common import write_pack, parse

PACK = "pack_T1f_044"
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


def T(i, quote, xkeys, ykeys, conf=0.9):
    return {"id": i, "states": True, "quote": quote, "kind": "overruled", "scope": "all",
            "field_limit": "", "doctrine": "", "conf": conf, "xkeys": xkeys, "ykeys": ykeys}


Q_3113 = span("s03113", "Payne v. Tennessee, 501 U. S. 808, 830", "(1989))")
Q_3272 = span("s03272", "In Seminole Tribe, of course", "491 U. S. 1 (1989)")

A = [
    F("s03243", "noStatement"),
    F("s03336", "noStatement"),
    F("s03337", "noStatement"),
    F("s03338", "quotation"),
    F("s03427", "quotation"),
    F("s03489", "quotation"),
    F("s03448", "wrongDirection"),
    F("s03176", "noStatement"),
    F("s03250", "noStatement"),
    T("s03113", Q_3113, ["South Carolina v. Gathers", "Gathers"], ["Payne v. Tennessee"]),
    F("s03117", "negation"),
    F("s03191", "negation"),
    F("s03114", "otherDecision"),
    T("s03272", Q_3272, ["Pennsylvania v. Union Gas"], ["Seminole Tribe"], conf=0.85),
    F("s03273", "noStatement"),
    F("s03051", "wrongDirection"),
    F("s03210", "cannotTell"),
    F("s03408", "noStatement"),
    F("s03458", "noStatement"),
    F("s03496", "cannotTell"),
    F("s03562", "noStatement"),
    F("s03088", "noStatement"),
    F("s03089", "noStatement"),
    F("s03274", "noStatement"),
    F("s03276", "noStatement"),
    F("s03123", "noStatement"),
    F("s03137", "noStatement"),
    F("s03138", "noStatement"),
    F("s03319", "noStatement"),
    F("s03296", "noStatement"),
    F("s03033", "noStatement"),
    F("s03052", "wrongDirection"),
    F("s03067", "wrongDirection"),
    F("s03115", "otherDecision"),
    F("s03277", "otherDecision"),
    F("s03433", "ownAct"),
    F("s03491", "otherDecision"),
    F("s03577", "ownAct"),
    F("s03597", "otherDecision"),
    F("s03116", "ownAct"),
    F("s03141", "would"),
    F("s03181", "cannotTell"),
    F("s03196", "would"),
    F("s03127", "noStatement"),
    F("s03242", "otherDecision"),
    F("s03315", "otherDecision"),
    F("s03395", "otherDecision"),
    F("s03409", "otherDecision"),
    F("s03410", "ownAct"),
    F("s03411", "otherDecision"),
]

write_pack(PACK, A)
