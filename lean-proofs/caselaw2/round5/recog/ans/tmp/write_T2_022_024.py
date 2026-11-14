import json, re, sys, os

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]


def F(reason, conf):
    return {"states": False, "reason": reason, "conf": conf}


def T(kind, scope, start, pivot, end, conf, field_limit="", doctrine=""):
    return {"states": True, "kind": kind, "scope": scope, "start": start, "pivot": pivot, "end": end,
            "conf": conf, "field_limit": field_limit, "doctrine": doctrine}


A = {}

A["pack_T2_022"] = {
    "r172828": F("notOverruling", 0.85),
    "r149431": T("overruled", "all", "Zwiers v Growney", "was overruled by this Court in", "Driver v Naini, 490 Mich 239", 0.75),
    "r138610": F("notOverruling", 0.9),
    "r108743": F("argument", 0.9),
    "r136262": T("disapproved", "all", "Methodist Hosp. of Ind., Inc. v. Rioux", "disapproved of by", "Lomax, 465 N.E.2d 731", 0.9),
    "r153525": F("otherDecision", 0.7),
    "r189453": T("overruled", "all", "Brice v. Starr, 90 Wash. 369", "the above case was overruled", "93 Wash. 501", 0.9),
    "r120204": T("overruled", "partialUnknown", "M & M, Inc. v. Wade", "it was overruled in", "Mosley v. Bank of Delaware", 0.9),
    "r108869": T("disapproved", "all", "People v. Delgado", "later disapproved in", "People v. Rist, 16 Cal.3d 211", 0.9),
    "r6654": T("abrogated", "all", "Munroe v. Galati", "abrogated by", "Geier v. Am. Honda Motor Co.", 0.9),
    "r155741": T("recededFrom", "all", "Witter v. State, 112 Nev. 908", "893 (1996), receded from by", "Byford, 116 Nev. 215", 0.9),
    "r165295": F("negation", 0.95),
    "r80327": T("overruled", "partialUnknown", "Montenegro v. United States", "overruled in unrelated part by", "Ashley v. United States, 266 F.3d 671", 0.9),
    "r153465": F("question", 0.65),
    "r187729": T("abrogated", "all", "Reiser v. Lohner", "(citations omitted), abrogated by", "Johnson v. Rogers", 0.9),
    "r142119": F("argument", 0.9),
    "r7629": T("overruled", "partialUnknown", "Wells v. Cole, 27 Ark. 603", "which has been overruled by subsequent decisions", "English v. Oliver, 28 Ark. 317", 0.85),
    "r188054": T("abrogated", "all", "In re Estate of Leno", "abrogated by Jakab", "Jakab v. Jakab, 163 Vt. 575", 0.9),
    "r155957": T("disapproved", "all", "Alvis v. State", "disapproved of by", "AA Primo Builders v. Washington, 126 Nev. 578", 0.9),
    "r153438": T("overruled", "all", "Ruby v. Strother, 11 Mo. 417", "was overruled by the case of", "Creath v. Smith, 20 Mo. 113", 0.95),
    "r156095": T("overruled", "partialUnknown", "Johnson v. Railroad", "which was overruled in", "Vassillion v. Sullivan, 94 N. H. 97", 0.6, doctrine="liability without fault"),
    "r156104": T("overruled", "partialUnknown", "Johnson v. Railroad", "which was overruled in", "Vassillion v. Sullivan, 94 N.H. 97", 0.6, doctrine="liability without fault"),
    "r156156": F("otherDecision", 0.9),
    "r139100": T("abrogated", "all", "State v. Hannebohn", "abrogated by State v. Hall", "State v. Hall, 298 Kan. 978", 0.9),
    "r158300": T("disapproved", "all", "Goodman v. Goodman", "were disapproved in", "Hughes v. Hughes, 125 N. J. Eq. 47", 0.9),
    "r4499": F("negation", 0.95),
    "r153478": T("overruled", "all", "Francis v. Blair, 89 Mo. 291", "reviewed and overruled in the same case", "Francis v. Blair, 96 Mo. 515", 0.9),
    "r109586": T("disapproved", "otherGrounds", "People v. Plies", "(disapproved in People v. Crowson", "33 Cal.3d 623", 0.9),
    "r109814": F("quotation", 0.65),
    "r109483": T("disapproved", "partialUnknown", "Estate of Riviere, supra, 8 Cal.App. 773", "disapproved in effect in", "Estate of Higgins (1910) 158 Cal. 355", 0.8),
    "r135122": T("overruled", "all", "Gibson v. Leonard", "overruled in Dini", "20 Ill. 2d 406", 0.9),
    "r137910": T("overruled", "all", "312 N.W.2d 534", "overruled by State v. Gaskins", "State v. Gaskins, 866 N.W.2d 1", 0.9),
    "r130822": F("otherDecision", 0.9),
    "r174006": T("overruled", "all", "Quinn v. City of Columbia", "overruled by St. Andrews", "349 S.C. 602", 0.9),
    "r155316": T("overruled", "partialUnknown", "Vansickle v. Haines", "finally unequivocally overruled", "Stevenson, 20 Nev. 269", 0.9, doctrine="riparian rights"),
    "r7674": F("argument", 0.9),
    "r152335": T("overruled", "partialUnknown", "Brown v. Beuc", "was overruled by Matthew", "Matthew v. Smith, 707 S.W.2d 411", 0.85),
    "r115455": T("overruled", "all", "West v. City of San Diego", "which were in turn overruled by", "Rodriguez v. Bethlehem Steel Corp.", 0.85),
    "r150963": F("notOverruling", 0.85),
    "r114802": T("overruled", "all", "Loudermilk", "was overruled by In re Marriage of Carney", "24 Cal.3d 725", 0.9),
    "r193245": T("overruled", "all", "Beaulieu v. Florquist", "868-69 (Wyo.2004), overruled by", "Brown v. City of Casper", 0.9),
    "r151626": T("overruled", "all", "Walker v. Whitfield Nursing Center", "overruled by Wimley", "Wimley v. Reid, 991 So.2d 135", 0.9),
    "r151344": T("overruled", "all", "Robinson v. State, 434 So.2d 206", "overruled by Flowers", "Flowers v. State, 473 So.2d 164", 0.9),
    "r151365": T("overruled", "all", "Robinson v. State, 434 So.2d 206", "overruled by Flowers", "Flowers v. State, 473 So.2d 164", 0.9),
    "r139996": T("overruled", "all", "Ratliff v. Commonwealth", "warranted an instruction on EED), overruled by", "Wellman v. Commonwealth, 694 S.W.2d 696", 0.9),
    "r131043": T("overruled", "all", "Sprayberry v. Dougherty County", "overruled in Ferguson", "275 Ga. 255", 0.9),
    "r146791": F("notOverruling", 0.9),
    "r190662": T("overruled", "all", "Haney v. Pittsburgh", "overruled by Jackson", "43 W.Va. 380", 0.9),
    "r5693": T("overruled", "all", "Associates Finance Corporation v. Scott", "have recently been overruled by", "Hanen v. Willis, 102 Ariz. 6", 0.9),
}

A["pack_T2_023"] = {
    "r136675": T("overruled", "all", "Santana v. State", "486 N.E.2d 1010, overruled by", "Spradlin v. State (1991), Ind., 569 N.E.2d 948", 0.95),
    "r152486": T("overruled", "all", "State v. Reyes", "subsequently overruled by the Missouri Supreme Court", "State v. Withrow, 8 S.W.3d 75", 0.95),
    "r192845": T("overruled", "all", "Harnischfeger Corp. v. LIRC", "overruled by Tetra Tech", "2018 WI 75", 0.9),
    "r192849": T("overruled", "all", "Harnischfeger Corp. v. LIRC", "overruled by Tetra Tech", "2018 WI 75", 0.9),
    "r114902": F("otherDecision", 0.55),
    "r155559": T("overruled", "all", "Meyer v. State, 95 Nev. 885", "overruled by Little", "Little v. Warden, 117 Nev. 845", 0.9),
    "r192511": T("overruled", "all", "City of La Crosse v. Schubert", "was overruled by Daanen", "Daanen & Janssen, Inc. v. Cedarapids, Inc.", 0.9),
    "r172646": T("abrogated", "all", "Commonwealth v. Deans", "(abrogated by Snyder", "963 A.2d 396", 0.9),
    "r148920": F("question", 0.9),
    "r139186": T("overruled", "all", "State v. Buser", "Ex Post Facto Clause.), overruled by", "304 Kan. 192", 0.85),
    "r153535": T("overruled", "partialUnknown", "Fusz v. Spaunhorst", "this construction was overruled in", "Cummings v. Winn, 89 Mo. 51", 0.9),
    "r185635": T("overruled", "all", "115 Tex. 551", "(1926), overruled by Dubai", "Dubai Petroleum Co. v. Kazi, 12 S.W.3d 71", 0.9),
    "r157812": T("overruled", "all", "State v. Whalen", "(App.Div.1989), overruled by", "State v. Anderson", 0.9),
    "r151978": T("overruled", "all", "Berryhill v. State", "overruled by Gollott", "Gollott v. State", 0.9),
    "r137076": T("overruled", "all", "State v. Moran, 7 Iowa 236", "has been virtually overruled in", "State v. Weese, 53 Iowa 92", 0.9),
    "r111407": T("disapproved", "all", "Newman (1927) 88 Cal.App. 186", "disapproved by Adoption of Barnett", "54 Cal.2d 370", 0.85),
    "r146290": T("overruled", "all", "Commonwealth v. West", "overruled in Commonwealth v. Maguire", "392 Mass. 466", 0.95),
    "r5083": T("overruled", "partialUnknown", "Crisp v. Kenai Peninsula School District", "partially overruled by", "Rosen v. State Bd. of Pub. Accountancy", 0.9),
    "r139718": T("overruled", "all", "Knox v. Commonwealth", "overruled by Lane", "Lane v. Commonwealth, Ky., 956 S.W.2d 874", 0.95),
    "r167453": T("overruled", "all", "Wren Paper Co. v. Glander", "overruled by Fifth Third", "Fifth Third Union Trust Co. v. Peck (1954), 161 Ohio St. 169", 0.9),
    "r190269": T("overruled", "partialUnknown", "State v. Zigler", "but it was overruled in", "State v. Staley, 45 W. Va. 792", 0.8),
    "r190272": T("overruled", "partialUnknown", "State v. Zeigler", "which has been overruled in", "State v. Staley, 45 W. Va. 792", 0.85),
    "r155194": T("overruled", "all", "State v. Myers", "was overruled in State v. Burlison", "State v. Burlison, 255 Neb. 190", 0.9),
    "r130897": F("cannotTell", 0.55),
    "r168031": T("overruled", "partialUnknown", "Harrell v. Suter", "which was expressly overruled in", "Cole v. Kinch, 134 Okla. 262", 0.8),
    "r193404": T("overruled", "all", "Waldron v. Waldron", "977 (Wyo. 2015), overruled by", "427 P.3d 708", 0.9),
    "r137453": T("overruled", "partialUnknown", "State v. Lott", "overruled by State v. Allen", "State v. Allen, 633 N.W.2d 752", 0.9),
    "r152065": T("abrogated", "all", "State v. Rose", "abrogated by Hoeber", "Hoeber v. State", 0.9),
    "r108615": T("overruled", "all", "People v Washington", "is impliedly overruled by", "People v. Merriam, 66 Cal.2d 390", 0.9),
    "r136089": T("abrogated", "all", "State v. Gullion", "(all abrogated by", "Fajardo v. State, 859 N.E.2d 1201", 0.9),
    "r80791": T("overruled", "all", "Newsom v. Friedman", "overruled by Suesz", "757 F.3d 636", 0.9),
    "r142521": T("disapproved", "all", "State v. Langley, 2004-0269", "disapproved of by", "958 So.2d 1160", 0.85),
    "r155525": F("notOverruling", 0.8),
    "r124791": F("notOverruling", 0.9),
    "r131989": T("overruled", "all", "72 Haw. 469", "overruled by, State v. Moore", "State v. Moore", 0.9),
    "r139650": F("notOverruling", 0.9),
    "r169632": T("overruled", "all", "Cross v. Chichester, 4 Or. 114", "were subsequently overruled", "Elwert v. Norton, 34 Or. 567", 0.85),
    "r113489": T("disapproved", "all", "In re Ronje", "(Ronje), disapproved in", "Reilly v. Superior Court (2013) 57 Cal.4th 641", 0.9),
    "r153571": F("question", 0.85),
    "r193270": T("abrogated", "all", "Reilly v. State", "abrogated by Granzer", "Granzer v. State, 2008 WY 118", 0.9),
    "r160557": T("overruled", "all", "Estate of Gutierrez v. Albuquerque", "overruled by Bracken", "Bracken v. Yates Petroleum Corp., 107 N.M. 463", 0.8),
    "r185959": T("overruled", "all", "Hardeman v. State", "which was expressly overruled in", "Wooten v. State, 109 Tex. Cr. R. 325", 0.9),
    "r156350": T("abrogated", "all", "Governor", "abrogated by Simplex", "Simplex Technologies v. Town of Newington, 145 N.H. 727", 0.9),
    "r192376": F("negation", 0.95),
    "r137799": T("overruled", "all", "State v. Mudra", "(per curiam), overruled by", "State v. Thompson, 856 N.W.2d 915", 0.85),
    "r3733": T("overruled", "all", "Moore v. Skill, 80 Ala. 129", "which said case was overruled in", "Bancroft v. Otis, 91 Ala. 279", 0.9),
    "r153534": T("overruled", "partialUnknown", "St. Louis v. Dorr, 145 Mo. 466", "were overruled in State ex rel. McCaffery", "Mason, 155 Mo. 486", 0.9),
    "r114407": F("notOverruling", 0.55),
    "r153501": F("notOverruling", 0.95),
}

A["pack_T2_024"] = {
    "r80840": T("abrogated", "all", "Newsome v. McCabe", "abrogated by Manuel", "Manuel v. City of Joliet", 0.95),
    "r136002": T("abrogated", "all", "Tripp v. State", "abrogated by Fajardo", "Fajardo v. State, 859 N.E.2d 1201", 0.95),
    "r125061": T("overruled", "all", "Estate of Mary H. Hughes, 44 B. T. A. 1196", "was overruled in Estate of Edward E. Bradley", "1 T. C. 518", 0.95),
    "r168001": T("overruled", "all", "Carter State Bank v. Ross", "which was overruled in Egan", "Egan v. First National Bank of Tulsa, 67 Okla. 168", 0.95),
    "r168072": F("argument", 0.65),
    "r135064": T("overruled", "all", "Bates v. Gillett", "which was expressly overruled in", "Dustin v. Brown, 297 Ill. 499", 0.95),
    "r3748": F("negation", 0.95),
    "r193403": T("overruled", "all", "Lokey v. Irwin", "315 (Wyo. 2016), overruled by", "427 P.3d 708", 0.9),
    "r175960": T("abrogated", "all", "Butler v. Commissioner, 114 T.C. 276", "abrogated by Porter", "Porter v. Commissioner, 132 T.C. 203", 0.9),
    "r109976": F("argument", 0.9),
    "r192756": T("abrogated", "partialUnknown", "Pattermann v. Pattermann", "was abrogated in", "Smaxwell v. Bayard, 2004 WI 101", 0.9),
    "r186442": F("notOverruling", 0.97),
    "r142297": T("overruled", "all", "State v. Williams, 354 So.2d 152", "apparently overruled in", "State v. Peoples, 383 So.2d 1006", 0.6),
    "r130939": T("overruled", "partialUnknown", "Wasden v. Rusco Indus.", "which was overruled on this issue in", "Murphy v. Murphy, 263 Ga. 280", 0.9),
    "r187654": T("overruled", "all", "Webb v. Univ. of Utah", "overruled by Cope", "Cope, 2014 UT 53", 0.9),
    "r110359": T("disapproved", "all", "People v. Van Hoek", "disapproved by People v. Jones", "51 Cal.3d 294", 0.9),
    "r111438": T("disapproved", "all", "People v. Van Hoek", "disapproved in People v. Jones", "51 Cal.3d 294", 0.9),
    "r111453": T("disapproved", "all", "People v. Van Hoek", "disapproved in People v. Jones", "51 Cal.3d 294", 0.9),
    "r111812": T("disapproved", "all", "People v. Johnson (1989)", "disapproved by People v. Simon", "9 Cal.4th 493", 0.9),
    "r153326": T("abrogated", "all", "State v. Payne, 414 S.W.3d 52", "abrogated by Hoeber", "Hoeber v. State, 488 S.W.3d 648", 0.9),
    "r169643": F("otherDecision", 0.85),
    "r137072": T("disapproved", "all", "Bennett v. City of Emmetsburg", "were disapproved in", "Clifton Land Company v. City of Des Moines, 144 Iowa 625", 0.9),
    "r140241": F("otherDecision", 0.9),
    "r153598": T("overruled", "all", "Kansas City Terminal Ry. Co. v. Kansas City Transit (1961)", "overruled by this court en banc", "359 S.W.2d 698", 0.75),
    "r165396": T("overruled", "all", "Hinnant v. Power Co.", "was itself overruled by", "Nicholson v. Hospital, 300 N.C. 295", 0.85),
    "r138720": F("otherDecision", 0.85),
    "r186325": T("abrogated", "all", "Armstead v. State", "abrogated by Green", "Green v. State, 906 S.W.2d 937", 0.9),
    "r128000": T("disapproved", "all", "Department of Transportation v. Wallis", "which has since been disapproved", "Department of Educ. v. Roe, 679 So.2d 756", 0.85),
    "r160032": F("negation", 0.85),
    "r175450": T("overruled", "partialUnknown", "Calderon v. United States Dist. Court", "overruled in unrelated part", "Woodford v. Garceau, 538 U. S. 202", 0.9),
    "r109018": T("disapproved", "otherGrounds", "Tuck v. Thuesen", "disapproved in another respect in", "Gelfand (1971) 6 Cal.3d 176", 0.9),
    "r119598": F("quotation", 0.85),
    "r132063": T("overruled", "all", "State v. Soares", "overruled, by State v. Janto", "State v. Janto", 0.8),
    "r131038": F("argument", 0.55),
    "r3689": F("negation", 0.95),
    "r6171": T("overruled", "all", "Cluff v. Farmers Ins. Exch.", "overruled by Godbehere", "Godbehere v. Phoenix Newspapers, Inc., 162 Ariz. 335", 0.95),
    "r149445": T("overruled", "all", "People v Herron", "which this Court overruled in", "People v Lockridge, 498 Mich 358", 0.95),
    "r151157": T("overruled", "all", "Canning v. State", "(Miss.1969), overruled by", "White v. State, 571 So.2d 956", 0.95),
    "r115792": F("otherDecision", 0.9),
    "r172901": F("argument", 0.9),
    "r156041": T("overruled", "all", "State v. Eighth Judicial Dist. Court (Romano)", "overruled by Abbott", "Abbott v. State", 0.9),
    "r169633": F("otherDecision", 0.8),
    "r173683": T("overruled", "otherGrounds", "Dockside Assoc., Inc. v. Detyens", "overruled in pt. on other grounds", "286 S.C. 555", 0.9),
    "r187280": F("ownAct", 0.65),
    "r124109": T("abrogated", "otherGrounds", "Standard Mfg. Co. v. United States", "abrogated in other", "Uniloc USA, Inc. v. Microsoft Corp., 632 F.3d 1292", 0.9),
    "r189427": T("overruled", "all", "Philadelphia, Mortgage", "has been virtually overruled", "Potter v. Whatcom, 25 Wash. 207", 0.85),
    "r153569": T("overruled", "partialUnknown", "State v. Alexander, 56 Mo. 131", "the case has been expressly overruled", "State v. Young, 345 Mo. 407", 0.6),
    "r167216": T("overruled", "all", "Wyler v. Tripi", "overruled in Oliver", "Oliver v. Kaiser Community Health Found. (1983), 5 Ohio St. 3d 111", 0.9),
    "r148923": T("overruled", "partialUnknown", "Gregory v. Railway", "but this was overruled in", "Woodworth v. Railway, 153 Mich. 108", 0.9),
}


def parse_pack(path):
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read().replace("\r\n", "\n")
    items = []
    for block in re.split(r"(?m)^### ITEM ", text)[1:]:
        lines = block.split("\n")
        iid = lines[0].strip()
        wi = lines.index("WINDOW:")
        ni = lines.index("NOTE AT:")
        window = "\n".join(lines[wi + 1:ni])
        items.append((iid, window))
    return items


def main():
    ok = True
    for pack, ans in A.items():
        items = parse_pack(os.path.join(BASE, "packs", pack + ".md"))
        ids = [i for i, _ in items]
        if len(ids) != len(set(ids)):
            print("DUP ids in pack", pack); ok = False
        missing = [i for i in ids if i not in ans]
        extra = [i for i in ans if i not in ids]
        if missing or extra:
            print(pack, "MISSING", missing, "EXTRA", extra); ok = False
        out = []
        ntrue = 0
        for iid, window in items:
            a = ans.get(iid)
            if a is None:
                continue
            if not a["states"]:
                out.append({"id": iid, "states": False, "reason": a["reason"], "kind": "", "scope": "",
                            "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]})
                continue
            p = window.find(a["pivot"])
            if p < 0:
                print(pack, iid, "PIVOT NOT FOUND"); ok = False; continue
            if window.count(a["pivot"]) != 1:
                print(pack, iid, "PIVOT NOT UNIQUE", window.count(a["pivot"])); ok = False
            s = window.rfind(a["start"], 0, p + 1)
            e = window.find(a["end"], p)
            if s < 0 or e < 0:
                print(pack, iid, "ANCHOR NOT FOUND", s, e); ok = False; continue
            q = window[s:e + len(a["end"])]
            problems = []
            if q not in window: problems.append("notSubstring")
            if len(q) > 400: problems.append("tooLong %d" % len(q))
            if not OVR.search(q): problems.append("noOverrulingWord")
            if not q.startswith(a["start"]) or not q.endswith(a["end"]) or a["pivot"] not in q:
                problems.append("anchors")
            if "\n" in q: problems.append("newline")
            fb = [w for w in FORBID if w in q.lower()]
            if problems:
                ok = False
            print("%s %s len=%d %s %s\n    %s" % (pack, iid, len(q), "PROBLEMS " + str(problems) if problems else "ok",
                                               "FORBID " + str(fb) if fb else "", q))
            ntrue += 1
            out.append({"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"],
                        "field_limit": a["field_limit"], "doctrine": a["doctrine"], "quote": q,
                        "confidence": a["conf"]})
        dest = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            for row in out:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        # re-read and verify independently
        with open(dest, encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        wmap = dict(items)
        assert [r["id"] for r in rows] == ids, "order/coverage mismatch " + pack
        for r in rows:
            if r["states"]:
                assert r["quote"] in wmap[r["id"]] and len(r["quote"]) <= 400 and OVR.search(r["quote"]), r["id"]
        print("SUMMARY", pack, "items", len(rows), "true", sum(1 for r in rows if r["states"]))
    print("ALL OK" if ok else "SOME PROBLEMS")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
