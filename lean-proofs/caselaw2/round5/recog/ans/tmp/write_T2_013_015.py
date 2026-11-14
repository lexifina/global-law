import json, re, sys, io, os

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]
OVR = re.compile(r"overrul|abrogat|disapprov|reced")


def T(i, start, end, x, y, kind="overruled", scope="all", conf=0.9, fl=None, doctrine=""):
    return dict(id=i, states=True, start=start, end=end, x=x, y=y, kind=kind, scope=scope, conf=conf, fl=fl,
                doctrine=doctrine)


def F(i, reason, conf=0.9):
    return dict(id=i, states=False, reason=reason, conf=conf)


P13 = [
    F("r110934", "argument", 0.95),
    T("r152473", "State v. Douthit, 846 S.W.2d 761", "State v. Carson, 941 S.W.2d 518", "Douthit", "Carson", scope="otherGrounds", conf=0.85),
    F("r153499", "otherDecision", 0.9),
    T("r173647", "State v. Patrick, 289 S.C. 301", "Casey v. State, 305 S.C. 445", "Patrick", "Casey", conf=0.95),
    T("r167334", "Dairyland Ins. Co. v. Finch", "State Farm Auto. Ins. Co. v. Alexander", "Finch", "Alexander", conf=0.85),
    T("r167341", "Dairyland Ins. Co. v. Finch", "State Farm Auto. Ins. Co. v. Alexander", "Finch", "Alexander", scope="partialUnknown", conf=0.9),
    T("r114228", "People v. Branch, 77 Cal.App. 384", "People v. Burton, 55 Cal.2d 328", "Branch", "Burton", scope="partialUnknown", conf=0.85,
      fl=("as to the proposition that", "inadmissible hearsay")),
    T("r7689", "Paulsen v. Paulsen, 269 Ark. 523", "Gentry v. Gentry", "Paulsen", "Gentry", scope="partialUnknown", conf=0.6),
    F("r132389", "negation", 0.95),
    T("r6949", "Ross v. School Dist. No. 16 of Pima County, 60 Ariz. 9, 130 P.2d 914, which", "Boyd v. Bell, 68 Ariz. 166", "Ross v. School Dist", "Boyd v. Bell", conf=0.95),
    T("r136571", "Pell v. Farquar, 3 Blackf. 331", "Moncrief v. Moncrief", "Pell v. Farquar", "Moncrief", conf=0.95),
    T("r193124", "Matter of Parental Rights of PP, 648 P.2d 512", "Clark v. Alexander", "648 P.2d 512", "Clark v. Alexander", conf=0.85),
    F("r111813", "otherDecision", 0.9),
    T("r120345", "Cabrera v. State, 747 A.2d 543", "Brooks v. State, 40 A.3d 346", "Cabrera", "Brooks", conf=0.95),
    T("r120350", "Cabrera v. State, 747 A.2d 543", "Brooks, 40 A.3d 346", "Cabrera", "Brooks", conf=0.95),
    T("r159518", "Coniglario v. Hanover Ins. Co.", "Hesser v. Harleysville-Garden State Ins. Co.", "Coniglario", "Hesser", conf=0.9),
    F("r121314", "otherDecision", 0.9),
    T("r138746", "Boster and these other cases", "State v. Fortune, 236 Kan. 248", "Boster", "Fortune", conf=0.9),
    T("r169696", "Pace v. Edgemont Inv. Co.", "Furtado v. Gemmell", "Pace v. Edgemont", "Furtado", conf=0.55),
    T("r186696", "In re G.J.C. , 2016 UT App 147", "436 P.3d 206", "379 P.3d 58", "B.T.B.", kind="abrogated", conf=0.85),
    T("r161799", "State v. Guilez, 2000-NMSC-020", "State v. Santillanes", "Guilez", "Santillanes", kind="abrogated", conf=0.9),
    F("r145255", "otherDecision", 0.9),
    T("r139987", "Mash v. Commonwealth, 769 S.W.2d 42", "Commonwealth v. Mobley", "Mash", "Mobley", conf=0.95),
    T("r151977", "Haines v. State , 428 So.2d 590 (Miss. 1983), overruled", "Gollott v. State", "Haines", "Gollott", conf=0.95),
    T("r122027", "Shaw v. Gober, 10 Vet.App. 498", "Carpenter v. Principi", "Shaw v. Gober", "Carpenter", conf=0.9),
    T("r7703", "Order of Ry. Conductors of America v. Bandy", "Anheuser-Busch, Inc. v. Manion", "Bandy", "Manion", conf=0.9),
    F("r5802", "argument", 0.95),
    F("r169667", "wrongDirection", 0.9),
    T("r114495", "Chamberlain was disapproved", "In re Dennis (1959) supra, 51 Cal.2d 666", "Chamberlain", "Dennis", kind="disapproved", scope="partialUnknown", conf=0.9,
      fl=("insofar as it implied", "evidence to the contrary")),
    T("r149958", "Bauer v. Gannett Co.", "Weinberger v. Maplewood Review", "Bauer", "Weinberger", conf=0.95),
    T("r110008", "In re Stanley B. (1971) 17 Cal.App.3d 530", "In re Robert G. (1982) 31 Cal.3d 437", "Stanley B.", "Robert G.", kind="disapproved", conf=0.9),
    T("r155046", "Romberg v. Hughes, 18 Neb. 579", "Schrandt v. Young", "Romberg", "Schrandt", scope="partialUnknown", conf=0.5),
    F("r136604", "otherDecision", 0.9),
    T("r156313", "Estabrook v. American Hoist & Derrick, Inc.", "Young v. Prevue Products", "Estabrook", "Young v. Prevue", conf=0.8),
    F("r131612", "notOverruling", 0.97),
    F("r166250", "negation", 0.95),
    T("r111640", "Grahn v. Tosco Corp.", "disapproved by Hooker", "Grahn", "Hooker", kind="disapproved", conf=0.95),
    T("r139641", "Keenon v. Adams", "Trimble County v. Moore", "Keenon", "Trimble County v. Moore", conf=0.9),
    T("r165120", "Reeves v. Reeves, 82 N.C. 348", "Medlin v. Medlin", "Reeves", "Medlin", kind="abrogated", conf=0.95),
    T("r160910", "State v. Carreon, 2006-NMCA-145", "State v. Savedra", "Carreon", "Savedra", kind="abrogated", conf=0.85),
    T("r188966", "State v. Williams , 93 Wash. App. 340", "abrogated by Kurtz , 178 Wash.2d 466", "Williams", "Kurtz", kind="abrogated", conf=0.9),
    F("r155612", "otherDecision", 0.9),
    F("r168038", "argument", 0.95),
    T("r132824", "Nampa & Meridian Irrigation District v. Washington Federal Savings", "v. Maslen", "Nampa", "Maslen", kind="abrogated", conf=0.9),
    T("r153472", "Gray v. Worst, 129 Mo. 122", "Fischer v. Johnson, 139 Mo. 433", "Gray v. Worst", "Fischer", conf=0.95),
    T("r167397", "Haas v. Hayslip", "Haverlack v. Portage Homes, Inc.", "Haas", "Haverlack", conf=0.95),
    F("r142596", "negation", 0.9),
    T("r186085", "Montgomery v. State, 571 S.W.2d 18", "Ex parte Blume", "Montgomery", "Blume", conf=0.95),
    T("r191228", "Williams v. South Penn Oil Co., 52 W.Va. 181", "Ramage v. South Penn Oil Co.", "Williams v. South Penn", "Ramage", conf=0.8),
]

P14 = [
    T("r188967", "State v. Butler , 126 Wash. App. 741", "abrogated by Kurtz , 178 Wash.2d 466", "Butler", "Kurtz", kind="abrogated", conf=0.9),
    T("r109728", "Gehman v. Superior Court", "26 Cal.3d 744", "Gehman", "26 Cal.3d 744", kind="disapproved", conf=0.85),
    T("r153467", "Fink\u2019s case, 10 Mo. App. 61", "82 Mo. 276", "10 Mo. App. 61", "82 Mo. 276", conf=0.5),
    F("r136142", "quotation", 0.5),
    F("r153528", "argument", 0.85),
    F("r162500", "negation", 0.9),
    T("r136635", "Neeley v. State, (1978) 269 Ind. 588", "German v. State", "Neeley", "German", conf=0.9),
    F("r156093", "wrongDirection", 0.9),
    T("r109826", "In re Marriage of McNeill", "41 Cal. 3d 440", "McNeill", "Fabian", kind="disapproved", scope="partialUnknown", conf=0.9,
      fl=("to the extent it approved", "4800.2")),
    T("r136255", "Hastings Mut. Ins. Co. v. Webb", "DePrizio", "Webb", "DePrizio", kind="disapproved", conf=0.85),
    T("r5005", "McCurry v. State, 538 P.2d 100", "Howe v. State", "McCurry", "Howe", conf=0.9),
    F("r151020", "cannotTell", 0.7),
    F("r125065", "otherDecision", 0.85),
    T("r152013", "Rhodes v. Nevada, 47 Mo. App. 499", "Cobb v. Railroad, 149 Mo. 609", "Rhodes", "Cobb", conf=0.9),
    T("r79328", "United States v. Shackleford", "Huddleston v. United States", "Shackleford", "Huddleston", scope="partialUnknown", conf=0.85,
      doctrine="clear and convincing standard"),
    T("r160722", "State v. Wilson, 2001-NMCA-032", "State v. Montoya", "Wilson", "Montoya", kind="abrogated", conf=0.9),
    T("r107459", "Anderson I, 136 Ct.Cl. 365, was", "Hansen, 450 U.S. 785", "136 Ct.Cl. 365", "Hansen", scope="partialUnknown", conf=0.85,
      fl=("to the extent that it held that", "the result was inequitable")),
    T("r173070", "Scott v. Mid Carolina Homes, Inc.", "Ward v. Dick Dyer", "Scott v. Mid Carolina", "Ward v. Dick Dyer", conf=0.6),
    F("r173775", "quotation", 0.5),
    F("r172227", "wrongDirection", 0.9),
    T("r110079", "Garcia v. Lucido (1961)", "Nichols v. Hast", "Garcia v. Lucido", "Nichols", kind="disapproved", conf=0.9),
    F("r3728", "otherDecision", 0.9),
    T("r58219", "Langley, 62 F.3d 602", "abrogated by Rehaif", "Langley", "Rehaif", kind="abrogated", conf=0.95),
    T("r80037", "Evans v. City of Chicago (\u201cEvans I\u201d)", "873 F.2d 1007", "689 F.2d 1286", "873 F.2d 1007", conf=0.9),
    F("r151243", "negation", 0.9),
    T("r154975", "Yates v. Kinney", "Romberg v. Fokken", "Yates", "Romberg", conf=0.95),
    T("r190286", "De Camp v. Carnahan", "Poling v. Poling", "Carnahan", "Poling", conf=0.85),
    T("r193045", "State v. Selig", "Keffer v. State, 860 P.2d 1118", "Selig", "Keffer", kind="abrogated", conf=0.9),
    T("r166914", "Holaday v. Bethesda Hosp.", "Layman v. Woo", "Holaday", "Layman", kind="disapproved", conf=0.9),
    F("r172225", "negation", 0.95),
    T("r6987", "State v. Hays, 109 Ariz. 123", "State v. Lewis", "Hays", "Lewis", conf=0.95),
    T("r132080", "Leyson, 5 Haw.App. 504", "903 P.2d 667", "Leyson", "Bernard", conf=0.9),
    T("r4251", "Brown v. Whitaker Contracting Corp.", "Tinney", "Whitaker", "Tinney", conf=0.95),
    T("r168004", "Oklahoma Ry. Co. v. Milam", "Ponca City Ice Co. v. Robertson", "Milam", "Ponca City", conf=0.95),
    T("r173491", "Canteen v. McLeod Reg", "Charlotte-Mecklenburg Hosp. Auth.", "384 S.C. 617", "Charlotte-Mecklenburg", conf=0.9),
    T("r115619", "People v. Green (1980) 27 Cal.3d 1", "Martinez, supra, 20 Cal.4th 225", "Green", "Martinez", conf=0.95),
    T("r139184", "Doe v. Thompson , 304 Kan. 291", "overruled by Petersen-Beard", "Thompson", "Petersen-Beard", conf=0.9),
    T("r153844", "State v. Lingar", "State v. Taylor", "Lingar", "Taylor", kind="abrogated", conf=0.9),
    T("r142739", "Wilson v. Bath Iron Works", "Jensen v. S.D. Warren Co.", "Bath Iron Works", "Jensen", kind="abrogated", conf=0.9),
    F("r6670", "otherDecision", 0.9),
    T("r193244", "Amrein v. Wyoming Livestock Bd.", "Brown v. City of Casper", "Amrein", "Brown v. City of Casper", conf=0.95),
    T("r107950", "Jaquay v. Principi", "589 F.3d 1201", "Jaquay", "589 F.3d 1201", conf=0.9),
    F("r168020", "otherDecision", 0.9),
    F("r169084", "cannotTell", 0.9),
    T("r115618", "People v. Caudillo (1978) 21 Cal.3d 562", "People v. Martinez", "Caudillo", "Martinez", conf=0.95),
    T("r167855", "French v. State, 377 P.2d 501", "Peters v. State", "French", "Peters", scope="partialUnknown", conf=0.9,
      fl=("as to prior holdings", "while handcuffed")),
    T("r186107", "Cumbie v. State, 578 S.W.2d 732", "Almanza v. State", "Cumbie", "Almanza", scope="partialUnknown", conf=0.9,
      fl=("to the extent that Cumbie holds", "reversal")),
    T("r140149", "Wilson v. Commonwealth, 836 S.W.2d 872", "St. Clair v. Roark", "836 S.W.2d 872", "Roark", scope="partialUnknown", conf=0.85),
    T("r161972", "Trujillo v. City of Albuquerque, 1990-NMSC-083", "Trujillo v. City of Albuquerque, 1998-NMSC-031, 125 N.M. 721", "110 N.M. 621", "125 N.M. 721", conf=0.9),
]

P15 = [
    T("r139717", "McGinnis v. Commonwealth", "Elliott v. Commonwealth", "McGinnis", "Elliott", conf=0.9),
    T("r186359", "Powell v. State, 897 S.W.2d 307", "Prystash v. State", "Powell", "Prystash", conf=0.9),
    F("r150987", "argument", 0.9),
    F("r4307", "quotation", 0.55),
    T("r4473", "Cooks v. Jim Walter Homes, Inc.", "Ex parte Moore, 793 So.2d 762", "Cooks", "793 So.2d 762", conf=0.85),
    F("r116680", "cannotTell", 0.5),
    F("r192345", "negation", 0.95),
    T("r153486", "Woolfolk v. January, 131 Mo. 620", "Van Cleve v. Berkey, 143 Mo. 109", "Woolfolk", "Van Cleve", scope="partialUnknown", conf=0.9,
      fl=("so much of that opinion as announced", "allege fraud")),
    T("r155734", "Kazalyn v. State, 108 Nev. 67", "Byford v. State", "Kazalyn", "Byford", kind="recededFrom", conf=0.95),
    T("r145241", "O\u2019Connor v. Moten", "Bienkowski v. Brooks", "Moten", "Bienkowski", kind="abrogated", scope="otherGrounds", conf=0.9),
    T("r132673", "State v. Knapp", "State v. Kimball", "Knapp", "Kimball", conf=0.95),
    F("r132352", "quotation", 0.55),
    T("r173408", "Gray v. South Carolina Department of Highways and Public Transportation, which", "371 S.C. 598", "311 S.C. 144", "Hardin", conf=0.9),
    T("r108853", "Lombardy v. Peter Kiewit Sons", "Southern Cal. Edison Co.", "Lombardy", "Southern Cal. Edison Co.", kind="disapproved", conf=0.85),
    T("r114656", "Lombardy was disapproved", "Southern Cal. Edison Co.", "Lombardy", "Southern Cal. Edison Co.", kind="disapproved", scope="partialUnknown", conf=0.9,
      fl=("to the extent inconsistent", "that opinion")),
    F("r155598", "otherDecision", 0.9),
    T("r128027", "Brown v. State, 565 So.2d 304", "Jackson v. State", "Brown", "Jackson", kind="abrogated", conf=0.9),
    T("r128381", "Brown v. State, 565 So.2d 304", "Jackson v. State", "Brown", "Jackson", kind="abrogated", conf=0.75),
    T("r3735", "Ragsdale v. Bowles", "Southern Car Company v. Adams", "Ragsdale", "Southern Car", conf=0.95),
    T("r79806", "Indianapolis Airport Auth. v. American Airlines, Inc.", "Northwest Airlines, 510 U.S. 355", "Indianapolis Airport", "Northwest Airlines", kind="abrogated", conf=0.9),
    T("r150427", "Chambers v. State, 831 N.W.2d 311", "Montgomery v. Louisiana", "Chambers", "Montgomery", conf=0.9),
    F("r109609", "argument", 0.95),
    F("r174274", "otherDecision", 0.8),
    T("r108981", "Neuber v. Royal Realty Co.", "Porter v. Montgomery Ward & Co.", "Neuber", "Porter", scope="otherGrounds", conf=0.9),
    F("r80307", "argument", 0.9),
    T("r136752", "Seymour Nat", "Quakenbush v. Lackey", "Seymour", "Quakenbush", conf=0.9),
    T("r121924", "Laruan v. West", "209 F.3d 1322", "Laruan", "209 F.3d 1322", conf=0.9),
    F("r127984", "wrongDirection", 0.8),
    F("r128210", "wrongDirection", 0.7),
    F("r151391", "wrongDirection", 0.85),
    F("r156089", "otherDecision", 0.5),
    F("r112946", "otherDecision", 0.9),
    F("r121272", "notOverruling", 0.6),
    F("r91030", "negation", 0.85),
    F("r186441", "notOverruling", 0.97),
    T("r137287", "Hillrichs v. Avco Corp.", "494 N.W.2d 224", "Hillrichs", "Reed", kind="abrogated", conf=0.9),
    T("r173689", "State v. McLeod, 303 S.C. 420", "State v. Evans", "McLeod", "Evans", scope="otherGrounds", conf=0.9),
    F("r108608", "otherDecision", 0.9),
    T("r127747", "Heriot v. City of Pensacola", "Asbell v. Green", "Heriot", "Asbell", scope="partialUnknown", conf=0.85),
    F("r130857", "question", 0.95),
    T("r192668", "Ernst v. State, 43 Wis. 2d 661", "State v. Bangert", "Ernst", "Bangert", kind="abrogated", conf=0.9),
    T("r158927", "Winfield v. Erie Railroad Co., 88 N. J. L. 619", "Erie Railroad Co. v. Winfield, 244 U. S. 170", "88 N. J. L. 619", "244 U. S. 170", conf=0.6),
    T("r139995", "Edmonds v. Commonwealth", "Wellman v. Commonwealth", "Edmonds", "Wellman", conf=0.85),
    T("r153755", "Rodden v. Rodden", "Lay v. Lay", "Rodden", "Lay v. Lay", conf=0.95),
    F("r152438", "quotation", 0.55),
    T("r80143", "United States v. Miller, 450 F.3d 270", "Kimbrough v. United States", "Miller", "Kimbrough", kind="abrogated", conf=0.95),
    T("r80231", "United States v. Miller, 450 F.3d 270", "Kimbrough v. United States", "Miller", "Kimbrough", kind="abrogated", conf=0.95),
    T("r80253", "United States v. Miller, 450 F.3d 270", "Kimbrough v. United States", "Miller", "Kimbrough", kind="abrogated", conf=0.95),
    F("r3835", "negation", 0.95),
]


def parse(path):
    txt = io.open(path, encoding="utf-8").read().replace("\r\n", "\n")
    items = []
    for blk in txt.split("### ITEM ")[1:]:
        iid = blk.split("\n", 1)[0].strip()
        w = blk.split("\nWINDOW:\n", 1)[1].split("\nNOTE AT:", 1)[0]
        items.append((iid, w))
    return items


def span(w, start, end):
    best = None
    i = w.find(start)
    while i != -1:
        j = w.find(end, i + len(start))
        if j != -1:
            s = w[i:j + len(end)]
            if best is None or len(s) < len(best):
                best = s
        i = w.find(start, i + 1)
    return best


def run(pack, answers):
    items = parse(os.path.join(BASE, "packs", pack + ".md"))
    amap = {a["id"]: a for a in answers}
    ids = [i for i, _ in items]
    problems = []
    if len(amap) != len(answers):
        problems.append("duplicate ids in answers")
    if set(ids) != set(amap):
        problems.append("id mismatch: missing %s extra %s" % (set(ids) - set(amap), set(amap) - set(ids)))
    out = []
    ntrue = 0
    for iid, w in items:
        a = amap[iid]
        if a["states"]:
            q = span(w, a["start"], a["end"])
            if q is None:
                problems.append("%s: span not found" % iid)
                continue
            if q not in w:
                problems.append("%s: not substring" % iid)
            if len(q) > 400:
                problems.append("%s: too long %d" % (iid, len(q)))
            if not OVR.search(q):
                problems.append("%s: no overruling word" % iid)
            if a["x"] not in q:
                problems.append("%s: x token missing" % iid)
            if a["y"] not in q:
                problems.append("%s: y token missing" % iid)
            if a["x"] != a["y"] and q.find(a["x"]) == q.find(a["y"]):
                problems.append("%s: x/y same position" % iid)
            if "## " in q:
                problems.append("%s: crosses part header" % iid)
            for f in FORBID:
                if f in q:
                    problems.append("%s: FORBIDDEN '%s' in quote" % (iid, f))
            fl = ""
            if a["fl"]:
                fl = span(w, a["fl"][0], a["fl"][1])
                if fl is None:
                    problems.append("%s: field_limit not found" % iid)
                    fl = ""
            ntrue += 1
            out.append({"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"], "field_limit": fl,
                        "doctrine": a["doctrine"], "quote": q, "confidence": a["conf"]})
        else:
            out.append({"id": iid, "states": False, "reason": a["reason"], "kind": "", "scope": "", "field_limit": "",
                        "doctrine": "", "quote": "", "confidence": a["conf"]})
    dst = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    # re-read and verify independently
    back = [json.loads(l) for l in io.open(dst, encoding="utf-8").read().split("\n") if l]
    wmap = dict(items)
    if [b["id"] for b in back] != ids:
        problems.append("order mismatch after re-read")
    for b in back:
        if b["states"]:
            q = b["quote"]
            if not (q and q in wmap[b["id"]] and len(q) <= 400 and OVR.search(q)):
                problems.append("%s: re-read verification failed" % b["id"])
    print(pack, "items", len(items), "written", len(back), "true", ntrue)
    for p in problems:
        print("  PROBLEM", p)
    if "-v" in sys.argv:
        for o in out:
            if o["states"]:
                print("   ", o["id"], len(o["quote"]), "|", o["quote"], "|| FL:", o["field_limit"])


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
run("pack_T2_013", P13)
run("pack_T2_014", P14)
run("pack_T2_015", P15)
