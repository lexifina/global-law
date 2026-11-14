# -*- coding: utf-8 -*-
"""Build and verify answers for pack_T2_028, pack_T2_029, pack_T2_030."""
import io
import json
import os
import re
import sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACKS = os.path.join(BASE, "packs")
ANS = os.path.join(BASE, "ans")

FORBIDDEN = [
    "not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
    "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
    "without overruling", "rather than overrul", "declin", "refus", "would overrule",
    "should be overruled", "should overrule", "to overrule", "argu", "contend", "urge",
    "dissent", "question", "doubt",
]
OVR = re.compile(r"overrul|abrogat|disapprov|reced")

AP = "\u2019"


def T(id_, start, end, kind="overruled", scope="partialUnknown", conf=0.9, fl="", doc=""):
    return dict(id=id_, states=True, start=start, end=end, kind=kind, scope=scope,
                conf=conf, fl=fl, doc=doc)


def F(id_, reason, conf=0.9):
    return dict(id=id_, states=False, reason=reason, conf=conf)


SPEC = {}

SPEC["pack_T2_028"] = [
    T("r119340", "Beard" + AP + "s Appeal, 64 Conn. 526", "Morelli v. Manpower, Inc., 226 Conn. 831", conf=0.7),
    T("r186389", "Johnson, 803 S.W.2d 272", "Heitman v. State, 815 S.W.2d 681", kind="disapproved"),
    T("r127891", "Hite v. State, 364 So.2d 771", "State v. Lowery, 419 So.2d 621"),
    T("r138898", "Kau Kau Take Home No. 1 v. City of Wichita, 281 Kan. 1185", "Estate of Kirkpatrick v. City of Olathe, 289 Kan. 554"),
    T("r169908", "State v. Holmes, 311 Or 400", "State v. Ashbaugh, 349 Or 297"),
    T("r151433", "Killingsworth v. State, 490 So.2d 849", "Turner v. State, 818 So.2d 1186"),
    T("r135615", "Cheeseman v. Jay School Corp.", "Albro, 585 N.E.2d 666"),
    F("r168033", "ownAct"),
    T("r128411", "Times Pub. Co. v. Williams, 222 So.2d 470", "Neu v. Miami Herald Pub. Co., 462 So.2d 821"),
    T("r109306", "Fitch v. Carpenter (1945) 70 Cal.App.2d 827", "46 Cal.2d 318", kind="disapproved"),
    T("r109019", "J. A. Thompson & Sons, Inc. v. Superior Court (1963) 215 Cal.App.2d 719", "Cross v. Pacific Gas & Elec. Co. (1964) 60 Cal.2d 690", kind="disapproved"),
    T("r150169", "Eberle v. Miller, 170 Minn. 207", "Johnson v. Iverson, 175 Minn. 319"),
    T("r119691", "Middletown v. Hartford Electric Light Co., 192 Conn. 591", "Waterbury v. Washington, 260 Conn. 506"),
    T("r151916", "Bush v. State , 895 So.2d 836", "233 So.3d 288", kind="abrogated"),
    T("r159544", "Brogan v. Passaic Daily News, 22 N.J. 139", "Maressa v. New Jersey Monthly, 89 N.J. 176", fl="in Shield Law context"),
    T("r135953", "Redman v. State, 679 N.E.2d 927", "Carter v. State, 750 N.E.2d 778", kind="abrogated"),
    T("r136135", "Redman v. State, 679 N.E.2d 927", "Carter v. State, 750 N.E.2d 778", kind="abrogated"),
    T("r138749", "Samsel v. Wheeler Transport Services, Inc., 246 Kan. 336", "248 Kan. 824", conf=0.8),
    T("r173890", "State v. Vazquez, 364 S.C. 293", "State v. Evans, 371 S.C. 27", kind="abrogated"),
    T("r6855", "State v. Garcia, 200 Ariz. 471", "Ferrero, 229 Ariz. 239", kind="disapproved"),
    T("r149181", "Federal Kemper Ins Co, Inc v Health Ins Administration, Inc, 424 Mich 537", "Frederick & Herrud, Inc, 443 Mich 358"),
    T("r6650", "State v. Winter, 146 Ariz. 461", "State v. Kamai, 184 Ariz. 620", kind="abrogated"),
    T("r5151", "In re J.L.F., 828 P.2d 166", "In re S.A., 912 P.2d 1235", conf=0.85),
    T("r5045", "Chase v. State, 369 P.2d 997", "Fields v. State, 487 P.2d 831"),
    T("r139749", "Jewell v. Commonwealth, Ky., 549 S.W.2d 807", "Payne v. Commonwealth, Ky., 623 S.W.2d 867"),
    T("r168242", "Marshall v. OK Rental & Leasing, Inc., 1997 OK 34", "2008 OK 105", scope="otherGrounds"),
    T("r80777", "Hemsworth v. Quotesmith.com, Inc., 476 F.3d 487", "Ortiz v. Werner Enterprises, Inc., 834 F.3d 760", conf=0.75),
    T("r155294", "State v. Ruisi , 9 Neb. App. 435", "State v. Decker , 261 Neb. 382", kind="disapproved"),
    T("r110987", "Rojes v. Riverside General Hospital (1988) 203 Cal.App.3d 1151", "Passavanti v. Williams (1990) 225 Cal.App.3d 1602", scope="otherGrounds", conf=0.85),
    T("r172513", "Taylor v. King, 284 Pa. 235", "Kelley, 433 Pa. 406"),
    T("r172517", "Taylor v. King, 284 Pa. 235", "Kelley, 433 Pa. 406"),
    T("r127926", "Reddish v. Smith, 468 So.2d 929", "Yamuni, 529 So.2d 258", kind="recededFrom"),
    T("r192568", "Pollack v. State, 215 Wis. 200", "Goodchild v. Burke, 27 Wis. 2d 244"),
    T("r192708", "Pollack v. State, 215 Wis. 200", "Goodchild v. Burke, 27 Wis. 2d 244", conf=0.85),
    T("r192637", "State v. Brown, 50 Wis. 2d 565", "State v. Walker, 154 Wis. 2d 158"),
    T("r190652", "State ex rel. Vance v. Arthur, 142 W.Va. 737", "Stalnaker v. Roberts, 168 W.Va. 593"),
    T("r136452", "Jones v. State , 766 N.E.2d 1258", "Fajardo v. State , 859 N.E.2d 1201", kind="abrogated"),
    T("r108637", "In re Van Brunt (1966) 242 Cal.App.2d 96", "In re Smiley (1967) 66 Cal.2d 606", kind="disapproved"),
    T("r144604", "Blocher v. Harlow, 268 Md. 571", "Eastgate Assocs. v. Apper, 276 Md. 698", kind="disapproved", fl="as to the use of Rule 885"),
    T("r149031", "Maslen v Anderson, 163 Mich 477", "Newton v Security National Bank of Battle Creek, 324 Mich 344", conf=0.75),
    T("r119351", "State v. Eason, 192 Conn. 37", "Paulsen v. Manson, 203 Conn. 484"),
    T("r119382", "State v. Eason, 192 Conn. 37", "Paulsen v. Manson, 203 Conn. 484"),
    T("r119419", "State v. Eason, 192 Conn. 37", "Paulsen v. Manson, 203 Conn. 484", conf=0.65),
    T("r119095", "State v. Colonese, 108 Conn. 454", "State v. Hayes, 127 Conn. 543"),
    T("r166395", "Schmidt v. Anderson, 29 N.D. 262", "Loan & Trust Co., 43 N.D. 260"),
    T("r131870", "Wong v. Panis, 7 Haw.App. 414", "Hac v. Univ. of Hawaii", kind="abrogated"),
    T("r191452", "Walker v. Doe , 210 W.Va. 490", "State v. McKinley , 234 W.Va. 143"),
    T("r186489", "Ward v. State, 829 S.W.2d 787", "Riney v. State, 28 S.W.3d 561"),
    T("r151672", "In re Garner, 466 So.2d 884", "Boone, 60 So.3d 172"),
    T("r119808", "State v. Day, 233 Conn. 813", "State v. Connor, 292 Conn. 483"),
]

SPEC["pack_T2_029"] = [
    T("r138366", "State v. Patterson, 12 Kan. App. 2d 731", "State v. Gibson, 246 Kan. 298", kind="disapproved"),
    T("r186527", "574 S.W.2d 73 (Tex.Cr.App. 1978)", "Ex parte Tarver, 725 S.W.2d 195", conf=0.85),
    F("r3778", "negation", 0.95),
    T("r150435", "Jostens, Inc. v. CNA", "523 N.W.2d 657", conf=0.85),
    T("r155065", "Aetna Cas. & Surety Co. v. Nielsen, 217 Neb. 297", "First Nat. Bank v. Bolzer, 221 Neb. 415"),
    T("r188820", "Flannagan v. Mutual Ins. Co., 152 Va. 38", "Gilley v. Union Life Ins. Co., 194 Va. 966"),
    T("r154763", "State v. Matt, 2008 MT 444", "357 Mont. 355"),
    T("r155547", "Bennett v. State, 106 Nev. 135", "Leslie v. Warden, 118 Nev. 773"),
    T("r155569", "Bennett v. State, 106 Nev. 135", "Leslie II, 118 Nev. 773"),
    T("r155617", "Bennett v. State (Bennett I), 106 Nev. 135", "Leslie v. Warden, 118 Nev. 773"),
    T("r155549", "Glover v. Concerned Citizens for Fuji Park, 118 Nev. 488", "Garvin v. Dist. Ct., 118 Nev. 749"),
    T("r145547", "Commonwealth v. Kirkpatrick, 44 Mass. App. Ct. 355", "Commonwealth v. Montalvo, 50 Mass. App. Ct. 85"),
    T("r140296", "Flinn v. Blakeman, 254 Ky. 416", "Warfield Natural Gas Co. v. Ward, 286 Ky. 73"),
    T("r152249", "Cozean was specifically overruled", "Murphy, 518 S.W.2d 655"),
    T("r140017", "Harris v. Commonwealth, 846 S.W.2d 678", "Mitchell v. Commonwealth, 908 S.W.2d 100"),
    T("r149436", "Karaczewski v Farbman Stein & Co, 478 Mich 28", "Inc, 487 Mich 455"),
    T("r186542", "Ex parte Jarrett, 891 S.W.2d 935", "Ex parte Wilson, 956 S.W.2d 25"),
    T("r154578", "Onstad v. Payless Shoesource, 2000 MT 230", "Johnson v. Costco Wholesale, 2007 MT 43"),
    T("r7217", "White v. Arizona Eastern R. Co., 26 Ariz. 590", "Holtz, 101 Ariz. 247"),
    T("r128341", "State v. Florida, 894 So.2d 941", "Valdes v. State, 3 So.3d 1067"),
    T("r155147", "Plock v. Crossroads Joint Venture, 239 Neb. 211", "Hynes v. Hogan, 251 Neb. 404"),
    T("r151565", "Johnson v. State, 512 So.2d 1246", "Smith v. State, 986 So.2d 290"),
    T("r150168", "Church of the Nativity of Our Lord v. WatPro, Inc., 491 N.W.2d 1", "Ly v. Nystrom, 615 N.W.2d 302", conf=0.85),
    F("r189435", "argument", 0.95),
    T("r128356", "Wilding v. State, 674 So.2d 114", "Devoney v. State, 717 So.2d 501", kind="recededFrom", conf=0.8),
    T("r114216", "People v. Candiotto, 128 Cal.App. 2d 347", "People v. Gould, 54 Cal.2d 621", scope="otherGrounds"),
    T("r165491", "State v. Pinch, 306 N.C. 1", "323 N.C. 318"),
    T("r150207", "O" + AP + "Neill v. Illinois Farmers Ins. Co., 381 N.W.2d 439", "Oanes v. Allstate Ins. Co., 617 N.W.2d 401"),
    T("r150285", "O" + AP + "Neill v. Illinois Farmers Insurance Co., 381 N.W.2d 439", "Oanes v. Allstate Ins. Co., 617 N.W.2d 401"),
    T("r150375", "State v. Netland, 762 N.W.2d 202", "133 S.Ct. 1552", kind="abrogated", conf=0.85),
    T("r150404", "State v. Netland, 762 N.W.2d 202", "133 S.Ct. 1552", kind="abrogated"),
    T("r161632", "101 N.M. 687, 687 P.2d 1038 (1984)", "Chavez v. Manville Prods. Corp., 108 N.M. 643", conf=0.5),
    T("r185921", "St. Elizabeth Hosp. v. Garrard , 730 S.W.2d 649", "Boyles v. Kerr , 855 S.W.2d 593"),
    T("r160816", "State v. Nemeth, 2001-NMCA-029", "137 N.M. 174"),
    T("r155340", "State v. Lung, 21 Nev. 209", "Darnell v. State, 92 Nev. 680", fl="as to impossibility of means utilized"),
    T("r112738", "Estate of Shinkle, supra, 97 Cal.App.4th 990", "39 Cal.4th 794", kind="disapproved", conf=0.85),
    T("r121699", "United States v. King, 58 M.J. 110", "United States v. Rendon, 58 M.J. 221"),
    T("r151179", "Mississippi State Highway Commission v. Stout, 242 Miss. 208", "390 So.2d 284"),
    T("r167410", "Minton v. Honda of Am. Mfg., Inc. (1997), 80 Ohio St.3d 62", "529 U.S. 861", kind="abrogated"),
    T("r151567", "Manning v. State, 726 So.2d 1152", "Weatherspoon v. State, 732 So.2d 158"),
    T("r186292", "Rogers v. State, 168 Tex.Cr.R. 306", "Scott v. State, 553 S.W.2d 361", conf=0.85),
    T("r132533", "State v. Hall, 86 Idaho 63", "Sivak v. State, 112 Idaho 197", conf=0.85),
    T("r159836", "Yanhko v. Fane, 70 N.J. 528", "Inc., 87 N.J. 146"),
    T("r150318", "State v. Brown, 348 N.W.2d 743", "State v. Ramey, 721 N.W.2d 294", kind="abrogated"),
    F("r114628", "ownAct", 0.95),
    T("r153058", "Crum v. Sachs Elec., 769 S.W.2d 131", "Hampton v. Big Boy Steel Erection, 121 S.W.3d 220"),
    T("r94202", "Draper v. Astoria Sch. Dist. No. 1C, 995 F.Supp. 1122", "350 F.3d 967"),
    T("r148283", "People v Burton, 44 Mich App 732", "People v Wright, 431 Mich 282"),
    F("r151012", "notOverruling", 0.85),
    F("r151014", "notOverruling", 0.85),
]

SPEC["pack_T2_030"] = [
    T("r161409", "Fryar v. Johnsen, 93 N.M. 485", "Woodson v. Phillips Petroleum Co., 102 N.M. 333", conf=0.85),
    T("r193362", "Shull v. State, 2017 WY 14", "Schmuck v. State, 2017 WY 140"),
    T("r176567", "Hilliard v. Park, 212 Tenn. 588", "Southall v. Billings, 213 Tenn. 280"),
    T("r153523", "Davis v. Luster, 64 Mo. 43", "Dyer, 147 Mo. 219"),
    T("r141361", "State v. Desdunes, 579 So.2d 452", "665 So.2d 1164", conf=0.85),
    T("r154750", "Story v. Bozeman, 242 Mont. 436", "Klyap, 2003 MT 294"),
    T("r193171", "State v. Chastain, 594 P.2d 458", "Olson v. State, 698 P.2d 107"),
    T("r139706", "Hall v. Commonwealth, Ky., 817 S.W.2d 228", "Commonwealth v. Ramsey, Ky., 920 S.W.2d 526"),
    T("r192693", "State v. Petrone, 161 Wis. 2d 530", "272 Wis. 2d 444"),
    T("r108876", "People v. Hayden (1973) 30 Cal.App.3d 446", "People v. Rist, supra, 16 Cal.3d 211", kind="disapproved"),
    F("r191119", "otherDecision", 0.9),
    T("r121978", "Holliday v. Principi, 14 Vet.App. 280", "Kuzma v. Principi, 341 F.3d 1327"),
    T("r115248", "People v. Wein (1958) 50 Cal.2d 383", "Daniels, supra, 71 Cal.2d 1119"),
    T("r127858", "Palm Beach Junior College Board of Trustees v. United Faculty of Palm Beach Junior College, 425 So.2d 133", "475 So.2d 1221", kind="disapproved", conf=0.55),
    T("r80694", "United States v. Thomas, 930 F.2d 526", "United States v. Canoy, 38 F.3d 893", scope="otherGrounds"),
    T("r154751", "Kitchen Krafters v. Eastside Bank, 242 Mont. 155", "Busta v. Columbus Hosp., 276 Mont. 342"),
    T("r154798", "Kitchen Krafters v. Eastside Bank, 242 Mont. 155", "Busta v. Columbus Hosp., 276 Mont. 342"),
    T("r154260", "State v. Oleson, 1998 MT 130", "291 Mont. 474"),
    T("r154552", "State v. Oleson, 1998 MT 130", "291 Mont. 474"),
    T("r155799", "Hampe v. Foote, 118 Nev. 405", "124 Nev. 224", kind="abrogated"),
    T("r134465", "Davis v. Human Rights Comm", "274 Ill. App. 3d 72", scope="otherGrounds", conf=0.85),
    T("r116604", "Midboe v. Indus. Claim Appeals Office, 88 P.3d 643", "Ray, 145 P.3d 661"),
    T("r128437", "Blanton v. State, 880 So.2d 798", "978 So.2d 149", kind="disapproved", conf=0.55),
    T("r80566", "Keri v. Bd. of Trs. of Purdue Univ., 458 F.3d 620", "Hill v. Tangherlini, 724 F.3d 965", scope="otherGrounds"),
    T("r159917", "State v. Tanton (hereinafter Tanton I), 88 N.M. 5", "88 N.M. 333", conf=0.85),
    T("r161327", "State v. Tanton, 88 N.M. 5", "State v. Tanton, 88 N.M. 333", conf=0.7),
    T("r5901", "Kosidlo v. Kosidlo, 125 Ariz. 32", "125 Ariz. 18", kind="disapproved", scope="otherGrounds", conf=0.6),
    T("r7111", "Kosidlo v. Kosidlo, 125 Ariz. 32", "125 Ariz. 18", kind="disapproved", conf=0.6),
    T("r128041", "Maddox v. State, 708 So.2d 617", "760 So.2d 89", kind="disapproved", conf=0.55),
    T("r128044", "Maddox v. State, 708 So.2d 617", "760 So.2d 89", kind="disapproved", conf=0.55),
    T("r128045", "Maddox v. State, 708 So.2d 617", "760 So.2d 89", kind="disapproved", conf=0.55),
    T("r135889", "Risner v. Indiana Parole Bd., 779 N.E.2d 49", "Robinson v. State, 805 N.E.2d 783", conf=0.8),
    T("r108699", "Kelly v. McDonald (1929) 98 Cal.App. 121", "McCarthy v. Tally (1956) 46 Cal.2d 577", kind="disapproved"),
    T("r142485", "Koslowski v. Sanchez, 576 So.2d 470", "648 So.2d 879"),
    T("r167306", "Viers v. Dunlap (1982), 1 Ohio St. 3d 173", "Wilfong v. Batdorf (1983), 6 Ohio St. 3d 100"),
    T("r155548", "Clem v. State, 104 Nev. 351", "Zgombic v. State, 106 Nev. 571"),
    T("r155568", "Clem v. State, 104 Nev. 351", "Zgombic v. State, 106 Nev. 571"),
    T("r155651", "Clem v. State, 104 Nev. 351", "Zgombic v. State, 106 Nev. 571"),
    F("r139694", "otherDecision", 0.9),
    T("r155158", "Muller v. Nebraska Methodist Hospital, 160 Neb. 279", "Myers v. Drozda, 180 Neb. 183"),
    T("r155183", "Muller v. Nebraska Methodist Hospital, 160 Neb. 279", "Myers v. Drozda, 180 Neb. 183", conf=0.85),
    T("r121802", "United States v. Foster, 40 M.J. 140", "United States v. Miller, 67 M.J. 385", conf=0.85),
    T("r121806", "United States v. Foster, 40 M.J. 140", "United States v. Miller, 67 M.J. 385"),
    T("r154304", "State v. D.B.S. (1985), 216 Mont. 234", "State v. Olson (1997), 286 Mont. 364", conf=0.85),
    T("r154770", "State v. Moore, 268 Mont. 20", "State v. Gollehon, 274 Mont. 116"),
    F("r29329", "argument", 0.85),
    T("r7822", "Arkansas Bar Ass", "Creekmore v. Izard, 236 Ark. 558"),
    T("r159506", "Cepeda v. Cumberland Engineering Co., 76 N.J. 152", "Suter, supra, 81 N.J. 150"),
    T("r155764", "122 Nev. 385, 398", "124 Nev. 224", conf=0.85),
    F("r167194", "notOverruling", 0.9),
]

# Items where a checker-refused string sits between the three things and cannot be cut out.
KNOWN_FORBIDDEN = {"r150318"}


def parse_pack(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read().replace("\r\n", "\n")
    items = []
    for chunk in text.split("### ITEM ")[1:]:
        id_ = chunk.split("\n", 1)[0].strip()
        a = chunk.index("\nWINDOW:\n") + len("\nWINDOW:\n")
        b = chunk.index("\nNOTE AT:")
        items.append((id_, chunk[a:b]))
    return items


def main():
    problems = 0
    for pack, spec in SPEC.items():
        items = parse_pack(os.path.join(PACKS, pack + ".md"))
        ids = [i for i, _ in items]
        sids = [s["id"] for s in spec]
        if ids != sids:
            print(pack, "ID ORDER MISMATCH")
            print(" missing:", [i for i in ids if i not in sids])
            print(" extra:", [i for i in sids if i not in ids])
            problems += 1
            continue
        win = dict(items)
        lines = []
        for s in spec:
            w = win[s["id"]]
            if not s["states"]:
                row = {"id": s["id"], "states": False, "reason": s["reason"], "kind": "", "scope": "",
                       "field_limit": "", "doctrine": "", "quote": "", "confidence": s["conf"]}
            else:
                i = w.find(s["start"])
                j = w.find(s["end"], i + 1) if i >= 0 else -1
                if i < 0 or j < 0:
                    print(pack, s["id"], "MARKER NOT FOUND", i, j)
                    problems += 1
                    continue
                q = w[i:j + len(s["end"])]
                if s["fl"] and s["fl"] not in w:
                    print(pack, s["id"], "FIELD LIMIT NOT IN WINDOW")
                    problems += 1
                row = {"id": s["id"], "states": True, "kind": s["kind"], "scope": s["scope"],
                       "field_limit": s["fl"], "doctrine": s["doc"], "quote": q, "confidence": s["conf"]}
            lines.append(json.dumps(row, ensure_ascii=False))
        out = os.path.join(ANS, "ans_" + pack + ".jsonl")
        with io.open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

        # Verify from the written file.
        with io.open(out, "r", encoding="utf-8", newline="") as f:
            raw = f.read()
        assert "\r" not in raw
        rows = [json.loads(l) for l in raw.split("\n") if l]
        assert [r["id"] for r in rows] == ids, "written ids differ"
        n_true = 0
        for r, s in zip(rows, spec):
            if not r["states"]:
                assert r["reason"] and r["quote"] == ""
                continue
            n_true += 1
            q = r["quote"]
            w = win[r["id"]]
            errs = []
            if q not in w:
                errs.append("not substring")
            if len(q) > 400:
                errs.append("len %d" % len(q))
            if not OVR.search(q):
                errs.append("no overruling word")
            if s["start"] not in q or s["end"] not in q:
                errs.append("names missing")
            if not (q.startswith(s["start"]) and q.endswith(s["end"])):
                errs.append("span edges")
            low = q.lower()
            bad = [x for x in FORBIDDEN if x in low]
            if bad and r["id"] not in KNOWN_FORBIDDEN:
                errs.append("forbidden %s" % bad)
            if bad and r["id"] in KNOWN_FORBIDDEN:
                print(pack, r["id"], "known unavoidable refused string:", bad)
            if "## " in q:
                errs.append("crosses part header")
            if errs:
                problems += 1
                print(pack, r["id"], errs, "|", q)
        print("%s: items=%d states_true=%d" % (pack, len(rows), n_true))
    print("PROBLEMS:", problems)
    if "--show" in sys.argv:
        for pack in SPEC:
            with io.open(os.path.join(ANS, "ans_" + pack + ".jsonl"), "r", encoding="utf-8") as f:
                for l in f:
                    r = json.loads(l)
                    if r["states"]:
                        print(r["id"], len(r["quote"]), "|", r["quote"])


if __name__ == "__main__":
    main()
