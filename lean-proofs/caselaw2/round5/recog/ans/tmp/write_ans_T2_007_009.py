# Writes ans_pack_T2_007/008/009.jsonl from reader decisions; quotes are cut from each item's WINDOW by anchors.
import io, json, os, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]


def T(kind, scope, s, e, conf, fl="", doc=""):
    return dict(states=True, kind=kind, scope=scope, s=s, e=e, conf=conf, fl=fl, doc=doc)


def F(reason, conf):
    return dict(states=False, reason=reason, conf=conf)


O, A, D, R = "overruled", "abrogated", "disapproved", "recededFrom"
ALL, PU, OG = "all", "partialUnknown", "otherGrounds"

SPEC = {
    "pack_T2_007": {
        "r193405": T(O, ALL, "In re Estate of Nielsen", "overruled by Essex , 2018 WY 111, 427 P.3d 708", 0.95),
        "r130832": T(O, PU, "Boughton v. Georgia R. Co., 109 Ga. 604", "City of Columbus v. Anglin, 120 Ga. 785", 0.65),
        "r111935": F("otherDecision", 0.9),
        "r136539": T(O, ALL, "Harney v. Owen", "Dallas v. Hollingsworth, 3 Ind. 537", 0.95),
        "r134275": T(O, PU, "People v. Brogan (1979)", "People v. Bier (1991), 210 Ill. App. 3d 1", 0.9),
        "r137990": T(A, ALL, "State v. Tonn, 195 Iowa 94", "State v. Cline, 617 N.W.2d 277", 0.95),
        "r138114": T(A, ALL, "195 Iowa 94, 106", "State v. Cline , 617 N.W.2d 277", 0.9),
        "r156108": T(O, ALL, "Sandwell v. Elliott Hospital", "Dowd v. Portsmouth Hospital, 105 N.H. 53", 0.95),
        "r139686": F("negation", 0.95),
        "r154962": T(D, PU, "Gerard-Ley v. Ley, 5 Neb. App. 229", "Schuman v. Schuman, 265 Neb. 459", 0.9,
                     doc="rule from Gerard-Ley"),
        "r140287": T(O, ALL, "Wagner v. Commonwealth, 581 S.W.2d 352", "Estep v. Commonwealth, 663 S.W.2d 213", 0.9),
        "r166965": F("notOverruling", 0.95),
        "r114377": F("negation", 0.95),
        "r191184": T(O, PU, "State v. Kennedy, 205 W.Va. 224", "State v. Mechling, 219 W.Va. 366", 0.9,
                     fl="as to our holding on the Confrontation Clause issue"),
        "r116503": F("cannotTell", 0.6),
        "r110806": T(O, ALL, "People v. Scott (1982) 129 Cal.App.3d 301", "People v. Hedgecock (1990) 51 Cal.3d 395", 0.9),
        "r172355": F("notOverruling", 0.5),
        "r121452": T(O, ALL, "Robert E. McNeill, 16 B. T. A. 479", "James M. Butler, 19 B. T. A. 718", 0.9),
        "r128211": T(R, ALL, "Farina v. State, 679 So.2d 1151", "699 So.2d 1312", 0.95),
        "r153485": F("notOverruling", 0.9),
        "r139185": T(O, ALL, "State v. Redmond , 304 Kan. 283", "overruled by Petersen-Beard , 304 Kan. 192", 0.85),
        "r172213": T(O, ALL, "Ilgenfritz", "McConkey v. McConkey, 9 Watts 352", 0.85),
        "r132922": F("otherDecision", 0.65),
        "r117125": T(O, PU, "Folks v. Patterson, 159 Colo. 403",
                     "In re Question Concerning State Judicial Review, 199 Colo. 463", 0.9),
        "r108728": T(D, ALL, "People ex rel. Dept. Pub. Wks. v. Elsmore", "v. Ramos (1969) 1 Cal.3d 261", 0.9),
        "r148965": T(O, PU, "Robertson v. New York Life Ins. Co., 312 Mich 92",
                     "Poledna v. Bendix Aviation Corp., 360 Mich 129", 0.9, doc="rule of Robertson"),
        "r159206": T(O, PU, "Brookdale Homes that an ordinance", "Lionshead Lake, Inc. v. Tp. of Wayne, 10 N.J. 165", 0.9),
        "r153505": F("otherDecision", 0.9),
        "r112751": T(D, PU, "Downer v. Zolin (1995)", "Lake, supra, 16 Cal.4th 448", 0.9,
                     fl="to the extent it would require lab reports to be sworn"),
        "r154995": T(O, PU, "Bergeron v. State, 53 Neb. 752, overlooking", "Schultz v. State, 88 Neb. 613", 0.9),
        "r7836": T(O, ALL, "Fore v. Circuit Court of Izard County", "Wise Co. v. Clay Circuit, 315 Ark. 333", 0.85),
        "r169586": T(A, ALL, "State v. Patnesky, 265 Or App 356", "State v. McNally, 361 Or 314", 0.95),
        "r168318": T(A, ALL, "State v. Patnesky , 265 Or. App. 356", "McNally , 361 Or. 314", 0.95),
        "r117380": T(A, ALL, "Stevens v. People, 29 P.3d 305", "124 S.Ct. 1354", 0.95),
        "r128104": T(D, ALL, "Williamson v. State, 510 So.2d 335", "Clark v. State, 783 So.2d 967", 0.95),
        "r80663": T(A, ALL, "Doe by Doe v. City of Belleville", "523 U.S. 75", 0.95),
        "r158301": F("otherDecision", 0.55),
        "r113868": T(D, ALL, "Brill Media Co., LLC v. TCW Group, Inc. (2005)", "v. Gore (2010) 49 Cal.4th 12", 0.95),
        "r139683": T(O, ALL, "Dept, of Revenue v. D &W Auto Supply", "678 S.W.2d 378", 0.95),
        "r176645": T(O, ALL, "Johnson v. Johnson , 37 S.W.3d 892", "137 S.Ct. 1400", 0.9),
        "r138207": T(O, ALL, "Kiesau v. Bantz", "880 N.W.2d 699", 0.85),
        "r80263": T(O, ALL, "United States v. Welton, 583 F.3d 494", "United States v. Corner. 598 F.3d 411", 0.95),
        "r38931": T(O, ALL, "Skillin v. Magnus", "Kelley v. Gill, 245 U. S. 116", 0.95),
        "r153454": T(O, ALL, "Crittenden v. Lietsendorfer, 35 Mo. 239", "Wilhite v. Wilhite, 53 Mo. 71", 0.9),
        "r187792": T(O, ALL, "State v. Manning, 136 Vt. 436", "State v. Gardner, 139 Vt. 456", 0.95),
        "r187757": T(A, ALL, "Whitney v. Faulkner , 2004 UT 52", "USA Power, LLC v. PacifiCorp , 2016 UT 20, 372 P.3d 629", 0.9),
        "r168144": T(O, OG, "Gaines v. Sun Refinery and Marketing, 1990 OK 33", "826 P.2d 587", 0.95),
        "r174092": T(A, ALL, "Owen v. Owen, 444 N.W.2d 710", "488 N.W.2d 63", 0.95),
        "r149990": F("otherDecision", 0.9),
    },
    "pack_T2_008": {
        "r185966": T(O, ALL, "Mooney v. State, 73 Tex.Cr.R. 121", "283 S.W. 506", 0.95),
        "r137268": T(O, ALL, "State v. Small, 184 Iowa 882", "Young v. City of Des Moines, 262 N.W.2d 612", 0.95),
        "r168101": T(D, ALL, "Drummond v. Drummond, 49 Okla. 649",
                     "McAdams v. District Court of Oklahoma County, 197 Okla. 237", 0.85),
        "r161757": T(A, ALL, "State v. Desnoyers, 2002-NMSC-031", "State v. Forbes, 2005-NMSC-027, 138 N.M. 264, 119 P.3d 144", 0.95),
        "r187233": T(O, ALL, "In re A.T. (A.T. I), 2013 UT App 184, 307 P.3d 672", "2015 UT 41, 353 P.3d 131", 0.9),
        "r3706": T(O, ALL, "Flowers v. Bitting, 45 Ala. 448", "Dallas v. Wimberly, 52 Ala. 196", 0.95),
        "r3773": T(O, ALL, "Flowers v. Bitting, 45 Ala. 448", "Wimberly v. Dallas, 52 Ala. 196", 0.7),
        "r154216": T(O, ALL, "State v. Fertterer (1992), 255 Mont. 73", "State v. Gatts (1996), 279 Mont. 42", 0.95),
        "r79536": T(O, ALL, "Mason v. Gramley, 9 F.3d 1345", "Hogan v. McBride, 74 F.3d 144", 0.97),
        "r130886": F("negation", 0.7),
        "r157271": T(O, PU, "Ghegan appear", "State v. Hammond, 118 N.J. 306", 0.6),
        "r154974": T(O, ALL, "Pcarson v. Kansas Mfg. Co., 14 Neb. 211", "Barry v. Wachosky, 57 Neb. 534", 0.95),
        "r132594": T(O, ALL, "Corgatelli v. Globe Life", "Casey v. Highlands Ins. Co., 100 Idaho 505", 0.95),
        "r161521": T(O, ALL, "State ex rel. State Highway Commission v. Trujillo, 82 N.M. 694", "103 N.M. 407", 0.9),
        "r173611": F("cannotTell", 0.65),
        "r109520": T(D, ALL, "Holt v. Superior Court (1950)", "Superior Court (1984) 36 Cal.3d 188", 0.95),
        "r157830": T(O, ALL, "Dlugosz v. Fred S. James", "Brook v. April, 294 N.J.Super. 90", 0.95),
        "r190328": T(O, ALL, "Coletrane v. Ott, 86 W. Va. 179", "118 W. Va. 190", 0.95),
        "r114577": T(D, ALL, "People v. Silverstein (1953)", "Richard M. v. Superior Court, supra, 4 Cal.3d 370", 0.95),
        "r109358": T(D, ALL, "People v. Hernandez, supra, 100 Cal.App.3d 637", "People v. Williams, supra, 140 Cal.App.3d 445", 0.9),
        "r167195": F("notOverruling", 0.9),
        "r117052": T(O, OG, "People v. Stead, 66 P.3d 117", "303 P.3d 1202", 0.95),
        "r141694": T(O, ALL, "State v. Desdunes, 579 So.2d 452", "665 So.2d 1164", 0.9),
        "r169658": F("notOverruling", 0.97),
        "r169660": F("notOverruling", 0.97),
        "r186447": F("notOverruling", 0.97),
        "r117248": T(O, ALL, "Ellis v. Ellis, 191 Colo. 317", "In re Marriage of Gallo, 752 P.2d 47", 0.97),
        "r66806": T(A, ALL, "United States v. Gonzalez-Longoria, 831 F.3d 670", "Sessions v. Dimaya, 138 S. Ct. 1204", 0.97),
        "r66808": T(A, ALL, "United States v. Gonzalez-Longoria, 831 F.3d 670", "Sessions v. Dimaya, 138 S. Ct. 1204", 0.97),
        "r133895": T(O, ALL, "People v. Hutchison (1977)", "People v. Graven (1984), 124 Ill. App. 3d 990", 0.85),
        "r142126": T(O, ALL, "Bordelon Case, 11 La. Ann. 676", "16 La. Ann. 219", 0.7),
        "r3705": T(O, ALL, "Davis v. Clark, 65 Ala. 617", "92 Ala. 145", 0.7),
        "r167678": F("otherDecision", 0.85),
        "r151474": T(O, OG, "Blue v. State, 674 So.2d 1184", "King v. State, 784 So.2d 884", 0.9),
        "r169559": T(A, ALL, "State v. Phillips, 217 Or App 93", "State v. Brumbach, 273 Or App 552", 0.95),
        "r122386": F("quotation", 0.85),
        "r146501": T(O, ALL, "Boston v. Massachusetts Comm", "65 Mass. App. Ct. 329", 0.95),
        "r169455": T(O, ALL, "State v. Collins, 100 Or App 311", "State v. Torres, 249 Or App 571", 0.95),
        "r152577": F("otherDecision", 0.95),
        "r130823": F("wrongDirection", 0.9),
        "r186016": F("notOverruling", 0.9),
        "r111223": T(D, PU, "People v. Smith, supra, 187 Cal.App.3d 666, relied", "People v. Bacigalupo, supra, 1 Cal.4th 103", 0.9),
        "r115874": T(D, ALL, "Lucas v. Superior Court (1988)", "Garcia v. Superior Court (1997) 14 Cal.4th 953", 0.95),
        "r114364": T(O, ALL, "Bacon v. Scannell, 9 Cal. 271", "Stevens v. Irwin, 15 Cal. 503", 0.9),
        "r114346": T(D, ALL, "People v. McGee (2002)", "People v. Avila (2006) 38 Cal.4th 491", 0.95),
        "r3780": T(D, PU, "Marengo County v. Lyles, 101 Ala. 423", "Scarbrough v. Watson, 140 Ala. 349", 0.9),
        "r142181": F("notOverruling", 0.9),
        "r166253": T(O, ALL, "Stanford v. McGill", "Hart-Parr Co. v. Finley, 31 N. D. 130", 0.9),
        "r136837": T(O, ALL, "Gentile v. State, 29 Ind. 409", "Heckler v. Conter, 206 Ind. 376", 0.95),
    },
    "pack_T2_009": {
        "r136601": T(D, PU, "Littell v. State, 133 Ind. 577", "Green v. State, 154 Ind. 655", 0.9),
        "r4266": T(O, ALL, "Hicks v. Globe Life & Acc. Ins. Co., 584 So.2d 458", "693 So.2d 409", 0.95),
        "r185962": T(O, ALL, "Bessett v. State, 78 Tex. Cr.R. 110", "Champion v. State, 113 Tex.Cr.R. 172", 0.9),
        "r116054": T(A, ALL, "People v. Taylor , 2012 COA 91", "134 S.Ct. 2473", 0.95),
        "r154973": T(O, PU, "Richardson v. Campbell, 34 Neb. 181, which", "Havemeyer v. Paul, 45 Neb. 373", 0.85,
                     doc="doctrine of Richardson v. Campbell (first point of the syllabus)"),
        "r127732": F("notOverruling", 0.95),
        "r114172": T(O, ALL, "People v. Banks, 39 Cal.App.2d 164", "People v. Woods, 35 Cal.2d 504", 0.97),
        "r160788": T(O, ALL, "State v. Smith, 102 N.M. 350", "Gillespie v. State, 107 N.M. 455", 0.95),
        "r187452": T(O, PU, "State v. Dunkley, 85 Utah 546", "State v. Crank, 105 Utah 332", 0.95,
                     fl="to the extent it allowed jury to determine voluntariness of a confession"),
        "r5380": F("otherDecision", 0.9),
        "r135240": T(O, ALL, "Colligan v. Cousar (1963)", "Wimmer v. Koenigseder (1985), 108 Ill. 2d 435", 0.95),
        "r186600": T(O, ALL, "Ex parte Duffy, 607 S.W.2d 507", "Hernandez v. State, 988 S.W.2d 770", 0.95),
        "r3712": T(O, ALL, "Hogan v. Branch Bank, 10 Ala. 485", "Griffin v. Bank, 17 Ala. 258", 0.9),
        "r166822": F("notOverruling", 0.95),
        "r109670": T(O, PU, "Pas v. Hill (1978) 87 Cal.App.3d 521", "supra, 111 Cal.App.3d 309", 0.9,
                     doc="central holding in Pas v. Hill"),
        "r110396": T(O, ALL, "Pas v. Hill (1978) 87 Cal.App.3d 521", "(1980) 111 Cal.App.3d 309", 0.95),
        "r139658": T(O, ALL, "Thomason v. Commonwealth", "429 S.W.2d 364", 0.97),
        "r187507": T(O, ALL, "State v. Robertson, 932 P.2d 1219", "State v. Reyes, 2005 UT 33, 116 P.3d 305", 0.95),
        "r167680": F("cannotTell", 0.55),
        "r147268": T(O, ALL, "Bristow v Woodhaven, 35 Mich App 205", "391 Mich 139", 0.95),
        "r109509": T(D, ALL, "Briney v. Santa Ana High School Dist. (1933)", "Gassman v. Governing Board, supra, 18 Cal.3d 137", 0.95),
        "r117437": T(O, ALL, "Mark v. Mark, 697 P.2d 799", "185 P.3d 794", 0.8),
        "r172664": T(O, ALL, "Commonwealth v. Hubbard, 472 Pa. 259", "Commonwealth v. Grant, 572 Pa. 48", 0.97),
        "r172720": T(A, ALL, "Commonwealth v. Hubbard, 472 Pa. 259", "Commonwealth v. Grant, 572 Pa. 48", 0.97),
        "r172748": T(O, ALL, "Commonwealth v. Hubbard, 472 Pa. 259", "Commonwealth v. Grant, 572 Pa. 48", 0.97),
        "r172220": T(O, ALL, "Borrell", "Kline v. Jacobs, 68 Pa. 57", 0.9),
        "r155320": T(O, ALL, "State v. Clark, 36 Nev. 472", "State v. Clark, 38 Nev. 304", 0.6),
        "r79888": F("notOverruling", 0.85),
        "r139029": T(D, ALL, "Allen v. Kansas Dept. of Revenue, 292 Kan. 653", "Sloop v. Kansas Dept. of Revenue, 296 Kan. 13", 0.85),
        "r172224": F("otherDecision", 0.8),
        "r168041": T(O, ALL, "Methvin v. American Savings", "North v. Haning, 204 Okl. 321", 0.7),
        "r174054": T(O, ALL, "State v. Neville, 346 N.W.2d 425", "State v. Hoenscheid, 374 N.W.2d 128", 0.97),
        "r185749": T(O, ALL, "Medallion Homes, Inc. v. Thermar Inv., Inc., 698 S.W.2d 400", "Ojeda de Toca v. Wise, 748 S.W.2d 449", 0.95),
        "r174036": T(O, PU, "Bearry v. Brensing, 85 S.D. 370", "Hunt v. Briggs, S.D., 267 N.W.2d 566", 0.55),
        "r172537": T(O, ALL, "Holly v. Unemployment Compensation Board of Review, 151 Pa.Cmwlth. 450",
                     "Navickas v. Unemployment Compensation Review Board, 567 Pa. 298", 0.95),
        "r159530": T(O, ALL, "Hanover Ins. Co. v. Lewis, 260 N.J.Super. 380", "270 N.J.Super. at 626-27, 637 A.2d 941", 0.95),
        "r192384": F("argument", 0.75),
        "r168008": T(O, ALL, "Tibbs-Dorsey Mfg. Co. v. State Industrial Commission, 147 Okla. 232", "Purcell, 153 Okla. 21", 0.95),
        "r128382": T(A, ALL, "Alvord v. State, 322 So.2d 533", "Way v. State, 760 So.2d 903", 0.85),
        "r160777": T(A, ALL, "State v. Bonham, 1998-NMCA-178", "State v. Traeger, 2001-NMSC-022", 0.95),
        "r132757": T(O, ALL, "State v. Hagerman Water Right Owners", "155 Idaho 55", 0.95),
        "r108860": T(O, ALL, "People v. Stroud (1969) 273 Cal.App.2d 670", "Lego v. Twomey (1972) 404 U.S. 477", 0.9),
        "r5583": T(A, ALL, "Glover v. Ranney , 314 P.3d 535", "137 S.Ct. 1400", 0.95),
        "r135033": T(O, PU, "Cincinnati, Indianapolis and Western Railway Co. v. People, 207 Ill. 566", "212 Ill. 518", 0.75),
        "r108784": T(D, PU, "Martin v. Martin, 215 Cal.App.2d 338", "Tijerina at 1 Cal.3d 41", 0.95),
        "r186541": T(A, ALL, "Helms v. State, 484 S.W.2d 925", "Young v. State, 8 S.W.3d 656", 0.95),
        "r186188": T(O, ALL, "Kemper v. State, 63 Tex.Crim. 1", "Robertson v. State, 63 Tex.Crim. 216", 0.9),
        "r152936": T(O, ALL, "State v. Civella, 364 S.W.2d 624", "Longhibler v. State, 832 S.W.2d 908", 0.95),
        "r131194": F("otherDecision", 0.9),
    },
}


def parse(path):
    txt = io.open(path, encoding="utf-8").read().replace("\r\n", "\n")
    items = []
    for block in re.split(r"(?m)^### ITEM ", txt)[1:]:
        iid = block.split("\n", 1)[0].strip()
        m = re.search(r"\nWINDOW:\n(.*?)\nNOTE AT:\n", block, re.S)
        if not m:
            raise SystemExit("no window for " + iid)
        items.append((iid, m.group(1)))
    return items


def main():
    ok = True
    for pack, spec in SPEC.items():
        items = parse(os.path.join(BASE, "packs", pack + ".md"))
        ids = [i for i, _ in items]
        if len(set(ids)) != len(ids):
            print(pack, "DUPLICATE ids in pack"); ok = False
        missing = [i for i in ids if i not in spec]
        extra = [i for i in spec if i not in ids]
        if missing or extra:
            print(pack, "MISSING", missing, "EXTRA", extra); ok = False
            continue
        rows, ntrue = [], 0
        for iid, win in items:
            sp = spec[iid]
            if sp["states"]:
                a = win.find(sp["s"])
                b = win.find(sp["e"], a + len(sp["s"])) if a >= 0 else -1
                if a < 0 or b < 0:
                    print(pack, iid, "ANCHOR NOT FOUND", a, b); ok = False
                    continue
                q = win[a:b + len(sp["e"])]
                probs = []
                if q not in win: probs.append("not substring")
                if len(q) > 400: probs.append("len %d" % len(q))
                if not OVR.search(q): probs.append("no overruling word")
                if sp["s"] not in q or sp["e"] not in q: probs.append("name missing")
                if probs:
                    print(pack, iid, "PROBLEM", probs); ok = False
                bad = [f for f in FORBID if f in q.lower()]
                if bad:
                    print(pack, iid, "note: checker-refused string in quote:", bad, "| len", len(q))
                ntrue += 1
                rows.append({"id": iid, "states": True, "kind": sp["kind"], "scope": sp["scope"],
                             "field_limit": sp["fl"], "doctrine": sp["doc"], "quote": q, "confidence": sp["conf"]})
            else:
                rows.append({"id": iid, "states": False, "reason": sp["reason"], "kind": "", "scope": "",
                             "field_limit": "", "doctrine": "", "quote": "", "confidence": sp["conf"]})
        out = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
        with io.open(out, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        # re-read and verify independently
        back = [json.loads(l) for l in io.open(out, encoding="utf-8").read().split("\n") if l]
        wins = dict(items)
        assert [r["id"] for r in back] == ids, "order mismatch"
        for r in back:
            if r["states"]:
                assert r["quote"] in wins[r["id"]] and len(r["quote"]) <= 400 and OVR.search(r["quote"]), r["id"]
        print(pack, "items", len(ids), "true", ntrue, "rows written", len(back))
        if "-v" in sys.argv:
            for r in back:
                if r["states"]:
                    print("  ", r["id"], len(r["quote"]), "|", r["quote"])
    print("OK" if ok else "FAILED")


if __name__ == "__main__":
    main()
