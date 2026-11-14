import sys
sys.path.insert(0, r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog\ans_prescreen\tmp")
from common import write_pack, parse

PACK = "pack_T1f_043"
_items, _ = parse(PACK)
_w = _items["s03173"]["window"]
_s = _w.index("Casey and once again allow")
_e = _w.index("(1986))", _s) + len("(1986))")
QS_03173 = _w[_s:_e]


def F(i, reason, xkeys=None, ykeys=None):
    d = {"id": i, "states": False, "reason": reason, "conf": 0.9}
    if xkeys:
        d["xkeys"] = xkeys
    if ykeys:
        d["ykeys"] = ykeys
    return d


def T(i, quote, xkeys, ykeys):
    return {"id": i, "states": True, "quote": quote, "kind": "overruled", "scope": "all",
            "field_limit": "", "doctrine": "", "conf": 0.9, "xkeys": xkeys, "ykeys": ykeys}


A = [
    T("s03173", QS_03173, ["Thornburgh"], ["Casey"]),
    F("s03049", "wrongDirection"),
    F("s03065", "noStatement"),
    F("s03405", "argument"),
    F("s03447", "ownAct"),
    F("s02997", "noStatement"),
    F("s03174", "notOverruling"),
    F("s03283", "notOverruling"),
    F("s03284", "otherDecision"),
    F("s03457", "otherDecision"),
    T("s03482",
      "overruled Bowers, holding that laws making same-sex intimacy a crime \u201cdemea[n] the lives of homosexual persons.\u201d Lawrence v. Texas, 539 U. S. 558, 575",
      ["Bowers"], ["Lawrence v. Texas"]),
    F("s03185", "noStatement"),
    F("s03323", "noStatement"),
    F("s03076", "noStatement"),
    F("s03289", "cannotTell"),
    F("s03252", "cannotTell"),
    F("s03016", "noStatement"),
    F("s03175", "noStatement"),
    F("s02952", "question"),
    F("s02953", "question"),
    F("s02954", "argument"),
    F("s03502", "noStatement"),
    F("s03022", "wrongDirection"),
    F("s02975", "noStatement"),
    F("s02984", "noStatement"),
    F("s02985", "noStatement"),
    F("s02986", "noStatement"),
    F("s03050", "wrongDirection"),
    F("s03270", "noStatement"),
    F("s03407", "noStatement"),
    F("s03594", "noStatement"),
    F("s03220", "argument"),
    F("s03004", "noStatement"),
    F("s03335", "noStatement"),
    F("s03402", "noStatement"),
    F("s03472", "noStatement"),
    F("s03205", "noStatement"),
    F("s03444", "noStatement"),
    F("s02998", "noStatement"),
    F("s02999", "noStatement"),
    F("s03000", "refusal"),
    F("s03294", "noStatement"),
    F("s03443", "noStatement"),
    F("s03543", "noStatement"),
    F("s03144", "noStatement"),
    F("s03293", "noStatement"),
    F("s03354", "noStatement"),
    F("s03202", "negation"),
    F("s03215", "negation"),
    F("s02942", "wrongDirection"),
]

write_pack(PACK, A)
