# -*- coding: utf-8 -*-
import io, json, os, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
BANNED = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]


def F(reason, conf=0.9):
    return {"states": False, "reason": reason, "conf": conf}


def T(kind, scope, start, end, xtok, ytok, conf=0.9, field_limit="", doctrine=""):
    return {"states": True, "kind": kind, "scope": scope, "start": start, "end": end, "xtok": xtok, "ytok": ytok,
            "conf": conf, "field_limit": field_limit, "doctrine": doctrine}


ANS = {}

ANS["pack_T1s_008"] = [
    ("s02078", F("negation", 0.7)),
    ("s01983", F("otherDecision")),
    ("s02472", F("notOverruling", 0.95)),
    ("s02473", F("notOverruling", 0.95)),
    ("s02254", T("overruled", "all", "National League of Cities, overruled Maryland v. Wirtz", None,
                 "Wirtz", "National League of Cities", 0.95)),
    ("s02255", T("overruled", "all",
                 "National League of Cities v. Usery, 426 U. S. 833 (1976) (overruling Maryland v. Wirtz", None,
                 "Wirtz", "National League of Cities", 0.95)),
    ("s02256", T("overruled", "all", "National League of Cities v. Usery, 426 U. S. 833 (1976) (overruling Wirtz",
                 None, "Wirtz", "National League of Cities", 0.95)),
    ("s02701", F("otherDecision", 0.85)),
    ("s02207", F("notOverruling", 0.9)),
    ("s02346", F("notOverruling", 0.9)),
    ("s02428", F("cannotTell", 0.9)),
    ("s02170", T("overruled", "partialUnknown",
                 "Edelman v. Jordan, 415 U. S. 651 (1974) (overruling in part Shapiro v. Thompson", None,
                 "Shapiro v. Thompson", "Edelman v. Jordan", 0.95)),
    ("s02187", F("otherDecision", 0.95)),
    ("s02176", F("otherDecision", 0.95)),
    ("s02945", T("overruled", "partialUnknown", "Alabama v. Smith, 490 U. S. 794 (1989) (overruling Simpson v. Rice",
                 "395 U. S. 711", "North Carolina v. Pearce", "Alabama v. Smith", 0.55)),
    ("s02720", F("negation", 0.9)),
    ("s02384", F("otherDecision", 0.9)),
    ("s02054", F("otherDecision", 0.95)),
    ("s02065", F("otherDecision", 0.9)),
    ("s02171", F("cannotTell", 0.8)),
    ("s02069", T("overruled", "partialUnknown", "Illinois v. Milwaukee, 406 U. S. 91 (1972). The Court",
                 "contrary suggestion in Wyandotte", "Wyandotte", "Illinois v. Milwaukee", 0.8)),
    ("s02833", F("otherDecision", 0.85)),
    ("s03204", T("overruled", "partialUnknown", "Harper overruled Chevron Oil", None, "Chevron Oil", "Harper", 0.55,
                 field_limit="insofar as the case (selectively) permitted the prospective-only application of a new rule of law")),
    ("s02110", F("otherDecision", 0.95)),
    ("s03400", F("refusal", 0.9)),
    ("s02236", F("otherDecision", 0.9)),
    ("s03666", F("cannotTell", 0.8)),
    ("s02217", F("argument", 0.9)),
    ("s02361", F("argument", 0.9)),
    ("s02423", F("quotation", 0.85)),
    ("s02852", F("ownAct", 0.85)),
    ("s02924", T("overruled", "partialUnknown",
                 "Thornburgh v. Abbott, 490 U. S. 401 (1989) (overruling in part Procunier v. Martinez", None,
                 "Procunier v. Martinez", "Thornburgh v. Abbott", 0.95)),
    ("s02912", F("negation", 0.95)),
    ("s02297", F("otherDecision", 0.95)),
    ("s02417", T("overruled", "all", "United States v. Scott, supra, overruling United States v. Jenkins", None,
                 "United States v. Jenkins", "United States v. Scott", 0.9)),
    ("s02418", T("overruled", "partialUnknown", "United States v. Scott, supra, overrules Jenkins", None,
                 "Jenkins", "United States v. Scott", 0.9,
                 field_limit="only insofar as Jenkins bars an appeal by the government when a defendant successfully moves for dismissal on a ground")),
    ("s02419", T("overruled", "all",
                 "United States v. Scott, 437 U. S. 82 (1978) (overruling United States v. Jenkins", None,
                 "United States v. Jenkins", "United States v. Scott", 0.95)),
    ("s02349", F("ownAct", 0.9)),
    ("s03306", F("negation", 0.9)),
    ("s02702", F("otherDecision", 0.9)),
    ("s02406", F("otherDecision", 0.9)),
    ("s02362", F("argument", 0.9)),
    ("s03012", F("otherDecision", 0.95)),
    ("s02336", F("refusal", 0.95)),
    ("s02781", F("refusal", 0.95)),
    ("s02895", F("refusal", 0.95)),
]

ANS["pack_T1s_009"] = [
    ("s03623", F("notOverruling", 0.95)),
    ("s02554", F("negation", 0.9)),
    ("s02907", F("would", 0.9)),
    ("s02827", F("otherDecision", 0.9)),
    ("s02420", F("otherDecision", 0.95)),
    ("s03419", F("negation", 0.9)),
    ("s02839", F("argument", 0.9)),
    ("s03180", F("notOverruling", 0.95)),
    ("s03236", F("ownAct", 0.9)),
    ("s03583", F("otherDecision", 0.9)),
    ("s02400", F("otherDecision", 0.95)),
    ("s02679", F("otherDecision", 0.9)),
    ("s03307", F("negation", 0.9)),
    ("s02708", F("otherDecision", 0.9)),
    ("s03440", F("notOverruling", 0.95)),
    ("s03249", F("ownAct", 0.9)),
    ("s03475", F("negation", 0.9)),
    ("s03246", T("abrogated", "partialUnknown", "Sandin abrogated Greenholtz", None, "Greenholtz", "Sandin", 0.9,
                 doctrine="methodology for establishing the liberty interest")),
    ("s03072", T("overruled", "all", "California v. Acevedo, 500 U. S. 565 (1991) (overruling Arkansas v. Sanders",
                 None, "Arkansas v. Sanders", "California v. Acevedo", 0.95)),
    ("s02621", F("negation", 0.95)),
    ("s03119", F("negation", 0.95)),
    ("s03498", T("overruled", "all", "Crawford, in which we overruled Roberts", None, "Roberts", "Crawford", 0.95)),
    ("s02754", F("quotation", 0.9)),
    ("s03365", F("would", 0.9)),
    ("s02686", F("otherDecision", 0.9)),
    ("s02761", T("overruled", "partialUnknown",
                 "Daniels v. Williams, 474 U. S. 327 (1986) (overruling in part Parratt v. Taylor", None,
                 "Parratt v. Taylor", "Daniels v. Williams", 0.95)),
    ("s02694", F("negation", 0.9)),
    ("s03585", F("quotation", 0.7)),
    ("s03586", T("overruled", "all", "Arizona v. Gant , 556 U.S. 332", "New York v. Belton", "New York v. Belton",
                 "Arizona v. Gant", 0.5)),
    ("s02654", F("argument", 0.9)),
    ("s03247", T("abrogated", "partialUnknown", "Sandin abrogated Greenholtz", "and Hewitt", "Hewitt", "Sandin", 0.9,
                 doctrine="methodology for establishing the liberty interest")),
    ("s03604", F("refusal", 0.95)),
    ("s03166", T("overruled", "partialUnknown", "Casey. That requirement involved only", "prior holding in Akron",
                 "Akron", "Casey", 0.8)),
    ("s03168", F("notInOneSpan", 0.6)),
    ("s03726", F("cannotTell", 0.9)),
    ("s03230", F("refusal", 0.95)),
    ("s03232", F("refusal", 0.95)),
    ("s02802", F("otherDecision", 0.9)),
    ("s03727", F("otherDecision", 0.9)),
    ("s03678", T("overruled", "all", "Hurst v. Florida, 577 U. S. 92, 101", "and Spaziano v. Florida",
                 "Spaziano v. Florida", "Hurst v. Florida", 0.95)),
    ("s03219", F("ownAct", 0.9)),
    ("s03524", F("ownAct", 0.9)),
    ("s03692", F("ownAct", 0.9)),
    ("s02983", F("otherDecision", 0.9)),
    ("s03169", F("ownAct", 0.9)),
    ("s03310", T("overruled", "partialUnknown", "Agostini of course overruled Aguilar in Ml and Ball", None,
                 "Ball", "Agostini", 0.9)),
]

ANS["pack_T1s_010"] = [
    ("s02765", F("argument", 0.9)),
    ("s03134", F("argument", 0.9)),
    ("s03170", F("ownAct", 0.9)),
    ("s03224", F("would", 0.9)),
    ("s03312", T("overruled", "all", "Agostini of course overruled Aguilar", None, "Aguilar", "Agostini", 0.9)),
    ("s03313", T("overruled", "all", "Agostini v. Felton, 521 U. S. 203 (1997) (approving",
                 "overruling Aguilar v. Felton", "Aguilar v. Felton", "Agostini v. Felton", 0.95)),
    ("s03314", T("overruled", "all", "Agos- tini v. Felton, 521 U. S. 203", "overruling Aguilar v. Felton",
                 "Aguilar v. Felton", "521 U. S. 203", 0.95)),
    ("s03421", F("ownAct", 0.9)),
    ("s03523", F("notOverruling", 0.85)),
    ("s03172", T("overruled", "partialUnknown", "Casey overruled the holdings in two cases", "(overruling Thornburgh",
                 "Thornburgh", "Casey", 0.9)),
    ("s02993", F("otherDecision", 0.9)),
    ("s03156", F("negation", 0.95)),
    ("s03520", F("argument", 0.9)),
    ("s03679", T("overruled", "all", "Hurst v. Florida, 577 U. S. 92, 101", "(overruling Hildwin", "Hildwin",
                 "Hurst v. Florida", 0.95)),
    ("s03550", F("otherDecision", 0.9)),
    ("s03015", F("otherDecision", 0.95)),
    ("s03292", F("otherDecision", 0.9)),
    ("s03060", F("notOverruling", 0.95)),
    ("s03503", F("otherDecision", 0.95)),
    ("s03540", F("otherDecision", 0.95)),
    ("s03124", F("would", 0.9)),
    ("s03383", F("ownAct", 0.9)),
    ("s03490", F("would", 0.9)),
    ("s03459", F("negation", 0.95)),
    ("s03450", F("otherDecision", 0.95)),
    ("s03463", T("overruled", "all", "overruled our earlier decision in Walton v. Arizona", "death penalty. Ring",
                 "Walton v. Arizona", "Ring", 0.7)),
    ("s03251", F("otherDecision", 0.9)),
    ("s03627", F("argument", 0.9)),
    ("s03621", F("argument", 0.9)),
    ("s03240", F("negation", 0.95)),
    ("s03620", F("notOverruling", 0.95)),
    ("s03579", F("otherDecision", 0.95)),
    ("s03580", T("overruled", "all", "Pearson v. Callahan, 555 U. S. 223, 233 (2009) (overruling Saucier v. Katz",
                 None, "Saucier v. Katz", "Pearson v. Callahan", 0.95)),
    ("s03486", F("otherDecision", 0.95)),
    ("s03505", F("otherDecision", 0.95)),
    ("s03650", F("otherDecision", 0.9)),
    ("s03599", F("otherDecision", 0.95)),
    ("s03683", F("cannotTell", 0.6)),
]


def parse_pack(name):
    with io.open(os.path.join(BASE, "packs", name + ".md"), encoding="utf-8", newline="") as f:
        text = f.read().replace("\r\n", "\n")
    items = []
    for chunk in re.split(r"(?m)^### ITEM ", text)[1:]:
        iid = chunk.split("\n", 1)[0].strip()
        a = chunk.index("\nWINDOW:\n") + len("\nWINDOW:\n")
        b = chunk.index("\nNOTE AT:\n", a)
        items.append((iid, chunk[a:b]))
    return items


ok = True
for pack, answers in ANS.items():
    items = parse_pack(pack)
    ids = [i for i, _ in items]
    aids = [i for i, _ in answers]
    if ids != aids:
        ok = False
        print(pack, "ID MISMATCH", [x for x in ids if x not in aids], [x for x in aids if x not in ids],
              len(ids), len(aids))
        continue
    win = dict(items)
    rows = []
    ntrue = 0
    for iid, a in answers:
        if not a["states"]:
            rows.append({"id": iid, "states": False, "reason": a["reason"], "kind": "", "scope": "",
                         "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]})
            continue
        w = win[iid]
        i = w.find(a["start"])
        if i < 0:
            ok = False
            print(pack, iid, "START NOT FOUND")
            continue
        if a["end"] is None:
            q = a["start"]
        else:
            j = w.find(a["end"], i)
            if j < 0:
                ok = False
                print(pack, iid, "END NOT FOUND")
                continue
            q = w[i:j + len(a["end"])]
        problems = []
        if q not in w:
            problems.append("not substring")
        if len(q) > 400:
            problems.append("too long %d" % len(q))
        if not re.search(r"overrul|abrogat|disapprov|reced", q):
            problems.append("no overruling word")
        if a["xtok"] not in q:
            problems.append("no X")
        if a["ytok"] not in q:
            problems.append("no Y")
        if a["field_limit"] and a["field_limit"] not in w:
            problems.append("field_limit not in window")
        banned = [b for b in BANNED if b in q]
        if problems:
            ok = False
            print(pack, iid, "PROBLEM", problems)
        if banned:
            print(pack, iid, "banned strings in quote (kept, cannot be cut):", banned)
        ntrue += 1
        rows.append({"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"],
                     "field_limit": a["field_limit"], "doctrine": a["doctrine"], "quote": q,
                     "confidence": a["conf"]})
    out = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # re-read and verify
    with io.open(out, encoding="utf-8", newline="") as f:
        raw = f.read()
    assert "\r" not in raw
    back = [json.loads(l) for l in raw.split("\n") if l]
    assert [r["id"] for r in back] == ids, "order"
    for r in back:
        if r["states"]:
            assert r["quote"] in win[r["id"]] and len(r["quote"]) <= 400
    print(pack, "items", len(back), "true", sum(1 for r in back if r["states"]), "len(q) max",
          max([len(r["quote"]) for r in back] or [0]))
print("OK" if ok else "FAILED")
