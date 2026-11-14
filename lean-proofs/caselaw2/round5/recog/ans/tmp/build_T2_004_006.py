# Builds ans_pack_T2_004/005/006.jsonl from start/end markers copied out of each item's WINDOW,
# then verifies every states:true quote (substring of WINDOW, <= 400 chars, overruling word, both names).
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "argu", "contend", "urge",
          "dissent", "question", "doubt"]


def T(id_, kind, scope, s, e, x, y, conf=0.9, fl="", doc=""):
    return (id_, True, kind, scope, s, e, x, y, conf, fl, doc)


def F(id_, reason, conf=0.9):
    return (id_, False, reason, conf)


P004 = [
    F("r135305", "otherDecision"),
    T("r139196", "overruled", "all", "State v. Lackey , 42 Kan. App. 2d 89", "295 Kan. 816", "42 Kan. App. 2d 89", "295 Kan. 816"),
    T("r167807", "overruled", "partialUnknown", "Byrd has been specifically", "Griffith v. State", "Byrd", "Griffith", 0.85, fl="with respect to this requirement"),
    T("r162514", "overruled", "all", "Mendel v Pittsburgh", "overruled in Victorson v Bock Laundry Mach. Co.", "Mendel", "Victorson", 0.85),
    T("r80674", "abrogated", "all", "Turkhan v. INS, 123 F.3d 487", "LaGuerre v. Reno", "Turkhan v. INS", "LaGuerre"),
    T("r80691", "abrogated", "all", "Turkhan v. INS, 123 F.3d 487", "LaGuerre v. Reno", "Turkhan v. INS", "LaGuerre"),
    T("r117426", "overruled", "all", "Kuiper v. Well Owners", "overruled by Alamosa-La Jara", "Kuiper", "Alamosa-La Jara"),
    F("r112006", "question", 0.8),
    T("r173911", "abrogated", "all", "State v. Edwards, 298 S.C. 272", "State v. Cherry", "Edwards", "Cherry"),
    T("r110719", "disapproved", "all", "People v. Hammon (1987)", "People v. Harrison", "Hammon", "Harrison"),
    F("r145932", "question", 0.8),
    T("r154977", "overruled", "all", "Irwin v. Nuckolls", "Cahill v. Cantwell", "Irwin", "Cahill"),
    T("r81056", "abrogated", "all", "Kanter v. Barr", "abrogated by Bruen", "Kanter", "Bruen"),
    T("r142202", "overruled", "all", "McConnell v. Lemley", "overruled in Cristadoro", "McConnell", "Cristadoro"),
    T("r173995", "overruled", "all", "State v. Jones , 133 S.C. 167", "State v. Foust", "133 S.C. 167", "Foust"),
    T("r111018", "disapproved", "all", "People v. Superior Court (1970) 3 Cal.App.3d 476", "People v. Turner", "3 Cal.App.3d 476", "Turner"),
    T("r187634", "overruled", "all", "State v. Rojas-Martinez", "overruled by Padilla", "Rojas-Martinez", "Padilla"),
    T("r187637", "abrogated", "all", "State v. Rojas-Martinez", "abrogated by Padilla", "Rojas-Martinez", "Padilla"),
    T("r193067", "overruled", "partialUnknown", "Starr v. State, 888 P.2d 1262", "Jones v. State", "Starr", "Jones v. State",
      fl="as to holding the seizure of evidence requires exigent circumstances"),
    T("r81270", "overruled", "all", "United States v. Colon", "United States v. Page", "Colon", "Page", 0.8),
    F("r122025", "negation", 0.6),
    F("r142147", "negation", 0.95),
    T("r154195", "overruled", "all", "State v. Purdie (1984)", "overruled by Hulse", "Purdie", "Hulse"),
    T("r130912", "overruled", "all", "Anglin v. State", "Welch v. State", "Anglin", "Welch"),
    T("r169669", "overruled", "all", "State v. Miller, 43 Or 325", "State v. Weston", "Miller", "Weston", 0.6),
    T("r153574", "overruled", "all", "Menard v. Goltra, 328 Mo. 368, 40 S.W.2d 1053, were", "See Redick", "Menard", "Redick", 0.7),
    T("r112432", "disapproved", "all", "Horton v. City of Oakland", "Connell v. City of Stockton", "Horton", "Connell v. City of Stockton"),
    F("r190358", "otherDecision"),
    F("r124877", "otherDecision"),
    T("r154029", "overruled", "all", "Wiseman v. Holt", "Whitney v. Bails", "Wiseman", "Whitney"),
    T("r193243", "overruled", "all", "Board of Trustees of the University of Wyoming v. Bell", "overruled by Brown v. City of Casper", "Bell", "Brown v. City of Casper"),
    T("r193299", "overruled", "all", "662 P.2d 410 (Wyo.1983)", "overruled by Brown", "662 P.2d 410", "Brown"),
    T("r156364", "overruled", "all", "Carson v. Maurer", "Cmty. Res. for Justice v. City of Manchester", "Carson", "Cmty. Res. for Justice"),
    F("r169654", "otherDecision"),
    T("r113961", "disapproved", "all", "Quintero v. City of Santa Ana (2003)", "disapproved in Morongo", "Quintero", "Morongo"),
    T("r79993", "overruled", "partialUnknown", "Sweeney v. Parke", "White v. Ind. Parole Bd.", "Sweeney", "White v. Ind. Parole Bd."),
    T("r123060", "overruled", "all", "Rice Services, Ltd. v. United States, 59 Fed.Cl. 619", "405 F.3d 1017", "59 Fed.Cl. 619", "405 F.3d 1017", 0.8),
    F("r155594", "otherDecision"),
    T("r136194", "abrogated", "all", "Greer v. State, 690 N.E.2d 1214", "Hopper v. State", "Greer", "Hopper"),
    T("r136231", "abrogated", "all", "Greer v. State, 690 N.E.2d 1214", "Hopper v. State", "Greer", "Hopper", 0.75),
    T("r168019", "overruled", "all", "Wilson v. Greer", "Blundell v. Wallace", "Wilson v. Greer", "Blundell"),
    T("r151786", "overruled", "all", "Odom v. Roberts", "Dedeaux v. Pellerin Laundry, Inc.", "Odom", "Dedeaux"),
    T("r153600", "overruled", "otherGrounds", "State v. Lee, 228 Mo. 480", "State v. Wade", "State v. Lee", "State v. Wade"),
    F("r152140", "otherDecision"),
    T("r80869", "overruled", "all", "United States v. Hurlburt", "Beckles v. United States", "Hurlburt", "Beckles"),
    T("r190409", "overruled", "all", "State v. Wayne, 162 W.Va. 41", "State v. Kopa", "Wayne", "Kopa"),
    T("r190458", "overruled", "all", "State v. Wayne, 162 W.Va. 41", "State v. Kopa", "Wayne", "Kopa"),
    T("r15217", "abrogated", "all", "In re Pascucci", "Nelson v. Scala", "Pascucci", "Nelson v. Scala", 0.8),
    T("r128414", "recededFrom", "all", "Blanco v. State", "Puglisi v. State", "Blanco", "Puglisi"),
]

P005 = [
    F("r139623", "otherDecision"),
    F("r150076", "otherDecision"),
    F("r162007", "quotation"),
    T("r145950", "overruled", "partialUnknown", "Parker v. Barnard", "Wynn v. Sullivan", "Parker v. Barnard", "Wynn", 0.75,
      fl="in so far as it relates to this point"),
    T("r132857", "overruled", "otherGrounds", "6 Ill. App. 172", "Co. v. Dunbar", "Hickey", "Dunbar", 0.8, doc="general doctrine upon other matters"),
    T("r192790", "abrogated", "all", "State v. Bohling, 173 Wis. 2d 529", "Missouri v. McNeely", "Bohling", "McNeely", 0.85),
    T("r125467", "abrogated", "all", "Meyer v. Commissioner", "Johnson v. Commissioner", "Meyer", "Johnson"),
    F("r175586", "argument"),
    T("r142174", "overruled", "all", "State v. Youchunas", "State v. Hilaire", "Youchunas", "Hilaire"),
    F("r114403", "otherDecision", 0.85),
    T("r116449", "overruled", "all", "People v. Herrera", "Close v. People", "Herrera", "Close"),
    F("r185126", "quotation", 0.85),
    T("r125318", "overruled", "otherGrounds", "Estate of Charles Curie", "Estate of Debe W. Hubbard", "Curie", "Hubbard"),
    T("r176639", "abrogated", "all", "R & J of Tennessee, Inc. v. Blankenship-Melton", "Auto Credit of Nashville v. Wimmer", "R & J of Tennessee", "Wimmer"),
    T("r7207", "overruled", "all", "139 Ariz. 428", "State v. LeBlanc", "139 Ariz. 428", "LeBlanc"),
    T("r77943", "disapproved", "all", "Schwimmer v. United States, 27 F.2d 742", "279 U.S. 644", "27 F.2d 742", "279 U.S. 644", 0.5),
    F("r185603", "negation"),
    F("r153421", "otherDecision", 0.8),
    T("r159496", "overruled", "all", "Martin has since been overruled", "Lincoln-Mercury", "Martin", "Performance Leasing"),
    F("r142132", "negation"),
    F("r109357", "argument"),
    T("r109688", "overruled", "all", "Babcock v. Omansky (1973)", "Canal-Randolph Anaheim, Inc. v. Wilkoski", "Babcock", "Canal-Randolph", 0.85),
    T("r148938", "overruled", "all", "Hamilton v. Frothingham", "Mooney v. York Iron Co.", "Hamilton", "Mooney", 0.8),
    T("r165327", "disapproved", "otherGrounds", "Watson v. Clutts", "McPherson v. Ellis", "Watson", "McPherson"),
    T("r151507", "abrogated", "all", "McNeal v. Administrator", "518 So.2d 1205", "McNeal", "518 So.2d 1205"),
    T("r128245", "disapproved", "all", "Vargas v. State, 902 So.2d 166", "disapproved by, Jones v. State", "902 So.2d 166", "Jones v. State", 0.85),
    F("r189468", "negation", 0.7),
    T("r117514", "overruled", "all", "People in the Interest of E.G., 2015 COA 18", "2016 CO 19", "2015 COA 18", "2016 CO 19", 0.85),
    F("r153456", "otherDecision"),
    T("r128205", "recededFrom", "partialUnknown", "Fabre v. Marin", "receded from by Wells", "Fabre", "Wells"),
    T("r190238", "abrogated", "all", "44 Wash. App. 154", "Restraint of Carrier", "44 Wash. App. 154", "Carrier"),
    T("r144400", "overruled", "partialUnknown", "Penn. R. v. Simmons", "Martin v. Sweeney", "Simmons", "Martin v. Sweeney",
      fl="on the point of last clear chance"),
    T("r153259", "overruled", "partialUnknown", "State v. Beck", "State v. Banks", "Beck", "Banks"),
    T("r114865", "overruled", "all", "People v. Garcia (1984)", "People v. Lee", "Garcia", "People v. Lee"),
    T("r95032", "abrogated", "all", "Castro-Cortez v. INS", "Fernandez-Vargas v. Gonzales", "Castro-Cortez", "Fernandez-Vargas", 0.85),
    T("r150269", "abrogated", "all", "297 N.W.2d 241, 249", "Cummings v. Koehnen", "297 N.W.2d 241", "Cummings"),
    T("r155020", "disapproved", "all", "Russell v. Glens Falls Indemnity Co.", "Long v. Railway Mail Assn.", "Russell", "Long v. Railway Mail"),
    T("r121850", "overruled", "all", "United States v. Ranney", "United States v. Phillips", "Ranney", "Phillips"),
    F("r193401", "otherDecision"),
    T("r155827", "overruled", "all", "Clem v. State, 104 Nev. 351", "overruled by Zgombic", "Clem", "Zgombic"),
    T("r153992", "overruled", "all", "Hauswirth v. Sullivan", "Burke v. Interstate S. & L. Assn.", "Hauswirth", "Burke"),
    T("r138855", "overruled", "all", "State v. Groves", "State v. Schoonover", "Groves", "Schoonover"),
    T("r139012", "overruled", "all", "State v. Johnson-Howell, 255 Kan. 928", "State v. Jefferson", "Johnson-Howell", "Jefferson", 0.85),
    F("r113344", "notOverruling", 0.95),
    T("r160702", "overruled", "all", "State v. Frawley", "State v. Lopez", "Frawley", "Lopez"),
    F("r192722", "quotation", 0.7),
    T("r109062", "overruled", "all", "Gustin v. Williams", "Green v. Superior Court", "Gustin", "Green v. Superior Court", 0.7),
    T("r188086", "overruled", "all", "State v. Morrissette, 170 Vt. 569", "In re Manosh", "Morrissette", "Manosh", 0.85),
    T("r169635", "overruled", "partialUnknown", "Wright v. Conservative Invest. Co.", "Lockhart v. Ferrey", "Wright", "Lockhart",
      fl="relative to attorney fees", doc="rule relative to attorney fees"),
]

P006 = [
    T("r193331", "overruled", "all", "Gueke v. Board", "Dunnegan v. Laramie County Commissioners", "Gueke", "Dunnegan"),
    T("r138787", "overruled", "partialUnknown", "Sandy, 225 Kan. 102, was effectively", "Delaware v. Prouse", "Sandy", "Prouse", 0.85,
      doc="authorization of random stops"),
    F("r151111", "otherDecision"),
    T("r110874", "disapproved", "all", "Knight v. McMahon", "American Federation of Labor v. Unemployment Ins. Appeals Bd.", "Knight", "American Federation of Labor"),
    T("r176648", "overruled", "otherGrounds", "Threadgill v. Bd.", "overruled by Lockett", "Threadgill", "Lockett"),
    T("r5778", "disapproved", "all", "Mengel v. Industrial Commission", "Arellano v. Industrial Commission", "Mengel", "Arellano"),
    F("r168715", "argument"),
    F("r139617", "negation", 0.85),
    T("r153541", "disapproved", "partialUnknown", "Gannon v. Pauk, 183 Mo. 265", "Gannon v. Pauk, 200 Mo. 75", "183 Mo. 265", "200 Mo. 75", 0.7,
      fl="as to the construction of the will there involved"),
    T("r172237", "overruled", "all", "Greene County v. Southern Surety Co.", "Commonwealth v. Great American Indemnity Co.", "Greene County", "Great American Indemnity"),
    T("r114210", "disapproved", "all", "Saks & Co. v. City of Beverly Hills", "Fascination, Inc. v. Hoover", "Saks", "Fascination"),
    F("r192377", "negation"),
    F("r138604", "otherDecision"),
    T("r4458", "overruled", "partialUnknown", "Ex parte Taylor, 10 So.3d 1075", "holding in Williams", "Williams", "Taylor", 0.85),
    T("r176583", "overruled", "all", "Pulaski Hous. Auth. v. Smith", "Johnson v. Oman Const. Co.", "Pulaski", "Johnson v. Oman"),
    T("r114376", "overruled", "all", "Gloster v. Wade, 78 Cal. 407, has been", "Huffman v. Hall", "Gloster", "Huffman"),
    T("r169680", "overruled", "all", "McGinnis et al v. Keen", "Nordling v. Johnston", "McGinnis", "Nordling", 0.75),
    F("r145920", "negation"),
    T("r114491", "disapproved", "partialUnknown", "Hillen v. Soule", "Brown v. Jensen", "Hillen", "Brown v. Jensen", 0.85),
    T("r150131", "overruled", "all", "Roderick v. Snyder Brothers Drug", "Kaiser v. Memorial Blood Center of Minneapolis, Inc.", "Roderick", "Kaiser"),
    T("r150203", "overruled", "all", "Koderick v. Snyder Brothers Drug", "Kaiser v. Memorial Blood Center of Minneapolis, Inc.", "413 N.W.2d 856", "Kaiser"),
    T("r115004", "overruled", "partialUnknown", "People v. Alfaro (1986)", "to that extent in Guerrero", "Alfaro", "Guerrero", fl="to that extent"),
    F("r144457", "negation"),
    F("r3796", "question", 0.7),
    T("r3732", "overruled", "all", "Garrison v. Glass", "s Case, 163 Ala. 125", "Garrison", "163 Ala. 125"),
    T("r42397", "abrogated", "all", "United States v. Castillo", "abrogated by Kimbrough", "Castillo", "Kimbrough"),
    T("r136589", "overruled", "all", "Terrell v. State", "Love v. Hall", "Terrell", "Love v. Hall"),
    T("r138899", "overruled", "partialUnknown", "Kau Kau Take Home No. 1", "Estate of Kirkpatrick v. City of Olathe", "Kau Kau", "Kirkpatrick"),
    T("r154203", "overruled", "all", "Casarotto v. Lombardi (1994)", "Assoc. v. Casarotto", "Casarotto v. Lombardi", "Assoc. v. Casarotto", 0.85),
    F("r136549", "otherDecision"),
    T("r150416", "abrogated", "all", "State v. Koperski", "Pollard v. Roy", "Koperski", "Pollard"),
    T("r79844", "overruled", "all", "Meredith v. Allsteel", "Ahng v. Allsteel, Inc.", "Meredith", "Ahng"),
    F("r167260", "negation", 0.85),
    F("r149327", "otherDecision"),
    T("r138291", "overruled", "all", "State v. McBride", "State v. Dickey", "McBride", "Dickey"),
    F("r138611", "notOverruling", 0.8),
    T("r144323", "disapproved", "all", "13 A.3d 68, 77 (2011)", "disapproved of by Stringfellow", "13 A.3d 68", "Stringfellow", 0.85),
    T("r144334", "disapproved", "all", "13 A.3d 68, 77 (2011)", "disapproved of by Stringfellow", "13 A.3d 68", "Stringfellow", 0.85),
    T("r153511", "overruled", "all", "State v. Samuels", "State v. Sakowski", "Samuels", "Sakowski", 0.8),
    T("r159573", "overruled", "all", "State v. Williams, 266 N.J.Super. 154", "overruled by Harvey", "Williams", "Harvey"),
    T("r125762", "overruled", "partialUnknown", "Mieure v. Moore", "Shor v. Paoli", "Mieure", "Shor",
      fl="insofar as the holdings were inconsistent"),
    T("r173783", "overruled", "all", "State v. Shafer, 340 S.C. 291", "Shafer v. South Carolina", "340 S.C. 291", "Shafer v. South Carolina", 0.8),
    T("r154153", "overruled", "all", "Colwell v. City of Great Falls", "Prezeau v. City of Whitefish", "Colwell", "Prezeau"),
    T("r114221", "disapproved", "all", "People v. Lagiss", "People v. Chevalier", "Lagiss", "Chevalier"),
    T("r167981", "overruled", "all", "In re Impunnubbee", "Armstrong v. Letty", "Impunnubbee", "Armstrong"),
    T("r167985", "overruled", "all", "In re Impummbbee", "Armstrong v. Letty", "49 Okla. 161", "Armstrong"),
    T("r114436", "disapproved", "partialUnknown", "People v. McIlvain", "People v. Brown", "McIlvain", "People v. Brown", 0.85),
    T("r161823", "overruled", "all", "State v. Magby", "2000-NMSC-017", "Magby", "2000-NMSC-017"),
    T("r117544", "overruled", "all", "21 Colo. 69", "overruled by Bertrand", "21 Colo. 69", "Bertrand"),
]

PACKS = {"pack_T2_004": P004, "pack_T2_005": P005, "pack_T2_006": P006}


def rx(marker):
    return re.compile(r"\s".join(re.escape(p) for p in marker.split(" ")))


def parse_pack(name):
    with io.open(os.path.join(BASE, "packs", name + ".md"), encoding="utf-8", newline="") as f:
        txt = f.read().replace("\r\n", "\n")
    out = []
    for block in txt.split("### ITEM ")[1:]:
        id_ = block.split("\n", 1)[0].strip()
        m = re.search(r"\nWINDOW:\n(.*?)\nNOTE AT:\n", block, re.S)
        out.append((id_, m.group(1)))
    return out


def pick(window, s, e):
    best = None
    for ms in rx(s).finditer(window):
        me = rx(e).search(window, ms.start())
        while me and me.end() < ms.end():
            me = rx(e).search(window, me.start() + 1)
        if not me:
            continue
        q = window[ms.start():me.end()]
        if OVR.search(q) and (best is None or len(q) < len(best)):
            best = q
    return best


def main():
    problems = 0
    for name, answers in PACKS.items():
        items = parse_pack(name)
        ids = [i for i, _ in items]
        amap = {}
        for a in answers:
            assert a[0] not in amap, ("duplicate answer", a[0])
            amap[a[0]] = a
        assert len(ids) == len(set(ids)), "duplicate ids in pack"
        missing = [i for i in ids if i not in amap]
        extra = [i for i in amap if i not in ids]
        assert not missing and not extra, (name, "missing", missing, "extra", extra)
        lines = []
        n_true = 0
        for id_, window in items:
            a = amap[id_]
            if not a[1]:
                lines.append({"id": id_, "states": False, "reason": a[2], "kind": "", "scope": "",
                              "field_limit": "", "doctrine": "", "quote": "", "confidence": a[3]})
                continue
            _, _, kind, scope, s, e, x, y, conf, fl, doc = a
            q = pick(window, s, e)
            errs = []
            if q is None:
                errs.append("marker not found")
            else:
                if q not in window:
                    errs.append("not a substring")
                if len(q) > 400:
                    errs.append("too long %d" % len(q))
                if not OVR.search(q):
                    errs.append("no overruling word")
                if x not in q:
                    errs.append("X token missing: " + x)
                if y not in q:
                    errs.append("Y token missing: " + y)
                if fl and fl not in window:
                    errs.append("field_limit not in window")
                bad = [w for w in FORBID if w in q]
                if bad:
                    print("  NOTE %s %s forbidden strings in quote: %s" % (name, id_, bad))
            if errs:
                problems += 1
                print("  ERROR %s %s: %s" % (name, id_, errs))
                continue
            n_true += 1
            print("%s [%d] %s" % (id_, len(q), q))
            lines.append({"id": id_, "states": True, "kind": kind, "scope": scope, "field_limit": fl,
                          "doctrine": doc, "quote": q, "confidence": conf})
        if problems:
            continue
        path = os.path.join(BASE, "ans", "ans_" + name + ".jsonl")
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            for obj in lines:
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        # re-read and verify independently
        with io.open(path, encoding="utf-8", newline="") as f:
            raw = f.read()
        assert "\r" not in raw
        rows = [json.loads(l) for l in raw.split("\n") if l]
        assert [r["id"] for r in rows] == ids
        wmap = dict(items)
        for r in rows:
            if r["states"]:
                assert r["quote"] in wmap[r["id"]] and len(r["quote"]) <= 400 and OVR.search(r["quote"])
        print("== %s: items %d, states true %d" % (name, len(rows), sum(1 for r in rows if r["states"])))
    print("problems:", problems)


main()
