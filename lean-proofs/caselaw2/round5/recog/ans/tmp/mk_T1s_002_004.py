import json, re, sys, io

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]


def F(reason, conf=0.9):
    return {"states": False, "reason": reason, "conf": conf}


def T(start, end, xtok, ytok, kind="overruled", scope="all", conf=0.9, fl=None, doctrine=""):
    return {"states": True, "start": start, "end": end, "xtok": xtok, "ytok": ytok, "kind": kind, "scope": scope,
            "conf": conf, "fl": fl, "doctrine": doctrine}


PACKS = {
    "pack_T1s_002": [
        ("s02119", T("Wales", "Hensley v. Municipal Court", "Wales", "Hensley", kind="disapproved",
                     scope="partialUnknown", conf=0.65)),
        ("s00795", F("negation")),
        ("s01121", F("ownAct")),
        ("s02626", T("United States v. One Assortment of 89 Firearms", "116 U. S. 436", "Coffey", "89 Firearms")),
        ("s01487", F("ownAct")),
        ("s01706", F("otherDecision")),
        ("s02635", T("Pennhurst State School and Hospital v. Halderman", "120 U. S. 390", "Rolston", "Pennhurst",
                     scope="partialUnknown")),
        ("s02718", T("United States v. Miller", "121 U. S. 1", "Bain", "Miller", scope="partialUnknown")),
        ("s00396", F("negation")),
        ("s00533", F("otherDecision")),
        ("s00944", T("Gleason, a railroad", "overruling Friedlander", "Friedlander", "Gleason", conf=0.85)),
        ("s00514", F("otherDecision")),
        ("s00624", T("Reid v. United States was to overrule", "the Ogden", "Ogden", "Reid", conf=0.85)),
        ("s00813", F("otherDecision")),
        ("s01868", T("Brimson", "Bloom v. Illinois", "Brimson", "Bloom", scope="partialUnknown")),
        ("s00518", F("negation")),
        ("s00519", F("negation")),
        ("s00609", F("otherDecision")),
        ("s01683", F("otherDecision")),
        ("s02888", T("South Carolina v. Baker", "157 U. S. 429", "Pollock", "Baker")),
        ("s00949", F("otherDecision")),
        ("s00607", F("otherDecision")),
        ("s01789", F("otherDecision")),
        ("s02196", F("otherDecision")),
        ("s02062", F("refusal")),
        ("s03358", F("negation")),
        ("s01368", F("argument")),
        ("s00652", F("negation")),
        ("s00653", F("negation")),
        ("s00979", F("would")),
        ("s00678", F("negation")),
        ("s00757", F("negation")),
        ("s01839", F("cannotTell")),
        ("s00981", F("otherDecision")),
        ("s01106", F("otherDecision")),
        ("s00689", T("Barney case", "Home Telephone & Telegraph Co. v. Los Angeles", "Barney", "Home Telephone",
                     kind="disapproved", scope="partialUnknown", conf=0.75)),
        ("s02043", T("Dunn v. Blumstein", "193 U. S. 621", "Pope v. Williams", "Dunn")),
        ("s00765", F("negation")),
        ("s00610", F("otherDecision")),
        ("s01065", F("otherDecision")),
        ("s00611", T("Ex parte Wisner", "In re Moore", "Wisner", "Moore", scope="partialUnknown",
                     fl=("in so far as it was said", "citizenship existed"))),
        ("s00613", T("Ex parte Wisner", "In re Moore", "Wisner", "Moore", kind="disapproved",
                     scope="partialUnknown", conf=0.85)),
        ("s00615", F("notOverruling")),
        ("s00632", F("notOverruling")),
        ("s00635", F("notOverruling")),
        ("s01369", F("argument")),
    ],
    "pack_T1s_003": [
        ("s00677", F("otherDecision")),
        ("s01412", T("Scully, supra", "Larson v. Domestic & Foreign Commerce Corp.", "Scully", "Larson", conf=0.7)),
        ("s00700", F("notOverruling")),
        ("s01420", F("otherDecision")),
        ("s01694", T("Malloy decision", "Twining v. New Jersey", "Twining", "Malloy", scope="partialUnknown")),
        ("s01695", T("Malloy case", "Twining v. New Jersey", "Twining", "Malloy")),
        ("s01730", F("otherDecision")),
        ("s02759", F("otherDecision")),
        ("s01633", T("Continental Ore overruled", "American Banana Co. v. United Fruit Co.", "American Banana",
                     "Continental Ore", scope="partialUnknown")),
        ("s01026", T("Hendrix v. United States", "Funk v. United States", "Hendrix", "Funk")),
        ("s00693", F("notOverruling")),
        ("s00753", F("notOverruling")),
        ("s00800", F("negation")),
        ("s01162", T("Rochester case which", "Procter & Gamble", "Procter & Gamble", "Rochester")),
        ("s00692", F("argument")),
        ("s00788", F("argument")),
        ("s00919", F("otherDecision")),
        ("s00853", F("otherDecision")),
        ("s02375", F("negation")),
        ("s00854", T("Frank v. Mangum", "Moore v. Dempsey", "Frank v. Mangum", "Moore v. Dempsey", conf=0.85)),
        ("s00980", F("would")),
        ("s01359", F("refusal")),
        ("s01078", F("otherDecision")),
        ("s00952", T("Fidelity & Columbia Trust Co. v. Louisville", "Farmers Loan & Trust Co. v. Minnesota",
                     "Fidelity & Columbia", "Farmers Loan", kind="disapproved")),
        ("s00893", F("otherDecision")),
        ("s00840", F("otherDecision")),
        ("s01079", F("otherDecision")),
        ("s01055", F("otherDecision")),
        ("s02529", F("negation")),
        ("s01192", F("argument")),
        ("s01278", F("argument")),
        ("s01164", F("negation")),
        ("s01027", T("Jin Fuey Moy v. United States", "Funk v. United States", "Jin Fuey Moy", "Funk")),
        ("s01558", F("otherDecision")),
        ("s01482", F("refusal")),
        ("s01483", F("negation")),
        ("s01484", F("refusal")),
        ("s01505", F("negation")),
        ("s01586", F("otherDecision")),
        ("s02551", T("Commonwealth Edison Co. v. Montana", "260 U. S. 245", "Heisler", "Commonwealth Edison")),
        ("s00916", F("otherDecision")),
        ("s01457", F("otherDecision")),
        ("s02093", F("otherDecision")),
        ("s01239", F("otherDecision", 0.6)),
        ("s01123", F("otherDecision")),
        ("s01165", T("O.Malley v. Woodrough", "Miles v. Graham", "Miles v. Graham", "Malley", scope="partialUnknown",
                     fl=("as to the constitutionality of taxation", "federal judges"))),
    ],
    "pack_T1s_004": [
        ("s01166", T("O.Malley v. Woodrough", "Miles v. Graham", "Miles v. Graham", "Malley")),
        ("s01956", F("otherDecision")),
        ("s01112", T("Childers v. Beaver", "Mountain Producers", "Childers", "Mountain Producers")),
        ("s01326", F("argument")),
        ("s01142", F("notMajority", 0.85)),
        ("s01092", F("otherDecision")),
        ("s01244", T("Panhandle Oil Co. v. Knox", "Alabama v. King & Boozer", "Panhandle", "King & Boozer")),
        ("s01245", T("Alabama v. King & Boozer", "Panhandle Oil Co. v. Knox", "Panhandle", "King & Boozer")),
        ("s01246", T("Alabama v. King & Boozer", "Panhandle Oil Co. v. Mississippi ex rel. Knox", "Panhandle",
                     "King & Boozer")),
        ("s02100", T("Lehnhausen v. Lake Shore Auto Parts Co.", "277 U. S. 389", "Quaker City Cab", "Lehnhausen")),
        ("s01827", T("Olmstead, then", "overruled by Katz", "Olmstead", "Katz")),
        ("s01828", T("Katz v. United States", "Olmstead v. United States", "Olmstead", "Katz")),
        ("s01031", F("otherDecision")),
        ("s01340", F("otherDecision")),
        ("s03213", F("negation")),
        ("s01184", F("otherDecision")),
        ("s01022", F("negation")),
        ("s03017", F("wrongDirection")),
        ("s01424", F("otherDecision")),
        ("s01000", F("notOverruling")),
        ("s02494", F("notOverruling")),
        ("s01104", F("otherDecision")),
        ("s01559", F("otherDecision")),
        ("s01118", F("otherDecision")),
        ("s01264", F("quotation", 0.85)),
        ("s01561", F("refusal")),
        ("s01328", F("quotation")),
        ("s02225", F("otherDecision")),
        ("s01023", F("negation")),
        ("s01840", F("cannotTell")),
        ("s01629", F("otherDecision")),
        ("s01638", F("otherDecision", 0.8)),
        ("s01873", F("otherDecision", 0.8)),
        ("s01402", F("ownAct")),
        ("s01234", F("notMajority", 0.85)),
        ("s01478", F("otherDecision")),
        ("s01335", F("wrongDirection")),
        ("s01054", F("otherDecision")),
        ("s01186", T("Helvering v. Hallock", "Helvering v. St. Louis Union Trust Co.", "St. Louis Union Trust",
                     "Hallock")),
        ("s02016", T("Triplett case", "Blonder-Tongue", "Triplett", "Blonder-Tongue", scope="partialUnknown")),
        ("s02017", T("Blonder-Tongue Laboratories", "Triplett v. Lowell", "Triplett", "Blonder-Tongue")),
        ("s01090", F("otherDecision")),
        ("s01139", T("overruled the doctrine of Rogers v. Graves", "Graves v. O.Keefe", "Rogers v. Graves", "Keefe",
                     scope="partialUnknown", conf=0.85)),
        ("s01153", T("New York ex rel. Rogers v. Graves", "Graves v. N. Y. ex rel. O.Keefe", "Rogers v. Graves",
                     "Keefe")),
        ("s01154", T("Graves v. New York ex rel. O.Keefe", "New York ex rel. Rogers v. Graves", "Rogers v. Graves",
                     "Keefe")),
        ("s01191", F("question")),
    ],
}


def rx(a):
    # anchors are literal except '.', which matches any one character
    return re.compile("".join("." if c == "." else re.escape(c) for c in a), re.S)


def parse(pack):
    txt = io.open(BASE + "\\packs\\" + pack + ".md", encoding="utf-8", newline="").read().replace("\r\n", "\n")
    items = []
    for blk in txt.split("### ITEM ")[1:]:
        iid = blk.split("\n", 1)[0].strip()
        w = blk.split("\nWINDOW:\n", 1)[1].split("\nNOTE AT:\n", 1)[0]
        items.append((iid, w))
    return items


def span(window, start, end):
    best = None
    for ms in rx(start).finditer(window):
        me = rx(end).search(window, ms.start())
        if not me:
            continue
        q = window[ms.start():me.end()]
        if OVR.search(q) and (best is None or len(q) < len(best)):
            best = q
    return best


ok = True
out = sys.stdout
for pack, answers in PACKS.items():
    items = parse(pack)
    ids = [i for i, _ in items]
    if ids != [a for a, _ in answers]:
        ok = False
        out.write("ORDER MISMATCH %s\n pack=%s\n ans =%s\n" % (pack, ids, [a for a, _ in answers]))
        continue
    lines = []
    ntrue = 0
    for (iid, w), (_, a) in zip(items, answers):
        if not a["states"]:
            row = {"id": iid, "states": False, "reason": a["reason"], "kind": "", "scope": "", "field_limit": "",
                   "doctrine": "", "quote": "", "confidence": a["conf"]}
        else:
            q = span(w, a["start"], a["end"])
            probs = []
            if q is None:
                probs.append("no span")
                q = ""
            if q not in w or not q:
                probs.append("not substring")
            if len(q) > 400:
                probs.append("too long %d" % len(q))
            if not OVR.search(q):
                probs.append("no overruling word")
            if a["xtok"] not in q:
                probs.append("no X")
            if a["ytok"] not in q:
                probs.append("no Y")
            fl = ""
            if a["fl"]:
                fl = span_fl = None
                ms = rx(a["fl"][0]).search(w)
                me = rx(a["fl"][1]).search(w, ms.start()) if ms else None
                fl = w[ms.start():me.end()] if ms and me else ""
                if not fl:
                    probs.append("no field_limit")
            bad = [f for f in FORBID if f in q]
            if probs:
                ok = False
            out.write("%s %s len=%d %s %s\n   %s\n" % (pack, iid, len(q), "PROBLEM " + ";".join(probs) if probs else "ok",
                                                     ("FORBIDDEN " + ",".join(bad)) if bad else "", q))
            if fl:
                out.write("   FL: %s\n" % fl)
            row = {"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"], "field_limit": fl,
                   "doctrine": a["doctrine"], "quote": q, "confidence": a["conf"]}
            ntrue += 1
        lines.append(json.dumps(row, ensure_ascii=False))
    with io.open(BASE + "\\ans\\ans_" + pack + ".jsonl", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    out.write("== %s items=%d true=%d\n" % (pack, len(lines), ntrue))

# independent re-check of the written files
for pack in PACKS:
    items = dict(parse(pack))
    rows = [json.loads(l) for l in io.open(BASE + "\\ans\\ans_" + pack + ".jsonl", encoding="utf-8").read().splitlines()]
    assert [r["id"] for r in rows] == [i for i, _ in parse(pack)], pack
    for r in rows:
        if r["states"]:
            q = r["quote"]
            assert q and q in items[r["id"]] and len(q) <= 400 and OVR.search(q), r["id"]
out.write("ALL OK\n" if ok else "PROBLEMS FOUND\n")
