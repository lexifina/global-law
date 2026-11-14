# -*- coding: utf-8 -*-
import json, os, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "argu", "contend", "urge",
          "dissent", "question", "doubt"]


def T(kind, scope, start, end=None, conf=0.9, fl="", doc=""):
    return {"states": True, "kind": kind, "scope": scope, "start": start, "end": end,
            "conf": conf, "fl": fl, "doc": doc}


def F(reason, conf=0.9):
    return {"states": False, "reason": reason, "conf": conf}


O, A, D = "overruled", "abrogated", "disapproved"
ALL, OG, PU = "all", "otherGrounds", "partialUnknown"

ANS = {}
ANS["pack_T2_010"] = {
    "r173998": T(A, ALL, "State v. Koon , 278 S.C. 528", "abrogated by Skipper v. South Carolina"),
    "r186446": F("notOverruling", 0.95),
    "r138103": T(O, ALL, "State v. Kuster , 353 N.W.2d 428", "overruled by State v. Huisman"),
    "r7652": T(D, ALL, "Polk v. State, 45 Ark. 165", "disapproved in Hardin v. State"),
    "r148396": T(O, ALL, "Williams v Payne, 131 Mich App 403", "overruled by DiFranco v Pickard"),
    "r189639": T(O, ALL, "Safeway Stores v. Retail Clerks", "was overruled by Yakima v. Gorham"),
    "r139980": T(O, ALL, "Herald v. Gross, 343 S.W.2d 831", "overruled by Rogers v. Sullivan"),
    "r174335": T(O, ALL, "Kirschenman v. Hutchinson County Board of Commissioners", "overruled by Bechen"),
    "r161810": T(A, ALL, "State v. Ruiz, 120 N.M. 534", "abrogated by State v. Martinez"),
    "r156792": T(O, ALL, "Hackensack Water Co. opinion", "15 N. J. 82", 0.8),
    "r185932": T(D, ALL, "831 S.W.2d 444", "N. Austin Mun. Util. Dist. No. 1 , 950 S.W.2d 371", 0.85),
    "r7872": T(O, ALL, "2009 Ark. 481, 14, 346 S.W.3d 273", "2015 Ark. 289, 467 S.W.3d 129", 0.85),
    "r139048": T(D, ALL, "State v. Bornholdt, 261 Kan. 644", "disapproved by State v. Marsh"),
    "r128107": F("quotation", 0.85),
    "r108642": T(D, OG, "People v. Harrison (1959) 176 Cal.App.2d 330", "disapproved in another respect by People v. Whitehorn"),
    "r136276": T(A, ALL, "Memorial Hospital v. Hahaj, 430 N.E.2d 412", "abrogated by Bartrom, 618 N.E.2d 1"),
    "r155507": T(D, PU, "118 Nev. 574, 53 P.3d 387 (2002), disapproved in pan by Garvin, 118 Nev. 749", None, 0.85),
    "r149122": T(O, PU, "Parker v Highland Park, 404 Mich 183", "impliedly overruled by Ross v Consumers Power Co", 0.85,
                 fl=("to the extent Parker", "does not constitute a governmental function")),
    "r169944": T(A, ALL, "Elliott v. Wallowa County, 57 Or 236", "abrogated by State ex rel. Douglas Cty. v. Sanders", 0.85),
    "r192609": T(A, ALL, "Waube v. Warrington, 216 Wis. 603", "abrogated by Klassa v. Milwaukee Gas Light Co."),
    "r135054": F("otherDecision", 0.9),
    "r154658": F("argument", 0.95),
    "r153346": T(O, ALL, "Loyd v. Ozark Elec. Co-op., Inc., 4 S.W.3d 579", "overruled by Hampton v. Big Boy Steel Erection"),
    "r139624": T(O, ALL, "Ratcliffe v. Marr, 87 Ky. 26", "184 Ky. 493"),
    "r155163": T(O, ALL, "State v. Blackson, 245 Neb. 833", "overruled by State v. White", 0.85),
    "r120297": T(O, ALL, "Chao v. State, 604 A.2d 1351", "overruled by Williams v. State"),
    "r151004": F("negation", 0.95),
    "r117064": F("negation", 0.95),
    "r130846": T(O, ALL, "Morris v. Yates, 226 Ga. 43", "overruled by this court in Chewning v. Brand", 0.95),
    "r186069": T(O, PU, "Gamez v. State, 403 S.W.2d 418", "See Bell v. State", 0.8),
    "r146564": F("otherDecision", 0.9),
    "r43937": T(A, ALL, "Picerni v. Bilingual Seit & Preschool Inc.", "Cheeks, 796 F.3d 199"),
    "r144986": T(O, ALL, "Young v. State, 15 Md.App. 707", "overruled by State v. Hicks", 0.85),
    "r190645": T(O, ALL, "State v. Adkins, 162 W.Va. 815", "overruled by State v. Lassiter", 0.65),
    "r153818": T(A, ALL, "Bridge Data Co. v. Dir. of Revenue, 794 S.W.2d 204", "958 S.W.2d 554", 0.85),
    "r135371": F("argument", 0.9),
    "r114435": T(O, ALL, "People v. Manzo, 9 Cal.2d 594", "overruled by People v. Valentine"),
    "r7865": T(O, ALL, "Bunch v. State , 346 Ark. 33", "overruled by Grillot v. State"),
    "r4199": T(O, ALL, "Baker v. Ball, 473 So.2d 1031", "overruled in Ford Motor Co. v. Neese"),
    "r139166": F("otherDecision", 0.9),
    "r114771": T(D, ALL, "People v. Thomas (1978) 20 Cal.3d 457", "disapproved in People v. Tassell"),
    "r109859": T(O, ALL, "Burke v. Superior Court (1982) 129 Cal.App.3d 570", "overruled by Strang v. Cabrol", 0.95),
    "r136606": T(O, ALL, "Jenckes v. Jenckes (1896), 145 Ind. 624", "Sulzer-Vogt Machine Co. v. Rushville Water Co."),
    "r172865": F("cannotTell", 0.6),
    "r168304": F("argument", 0.95),
    "r121450": F("wrongDirection", 0.85),
    "r142128": F("otherDecision", 0.95),
    "r113660": T(D, ALL, "Fenton v. Groveland Community Services Dist. (1982) 135 Cal.App.3d 797", "disapproved in Katzberg v. Regents of University of California", 0.85),
    "r165135": F("argument", 0.9),
}

ANS["pack_T2_011"] = {
    "r187655": T(O, ALL, "State v. Anderson, 612 P.2d 778", "overruled by State v. Clark"),
    "r125369": T(O, ALL, "Sherman v. Commissioner, 18 T.C. 746", "overruled by Rushing v. Commissioner"),
    "r108150": T(D, ALL, "Madera Oversight Coalition, Inc. v. County of Madera (2011) 199 Cal.App.4th 48", "disapproved in Neighbors for Smart Rail"),
    "r165737": T(O, ALL, "State v. Allen, 339 N.C. 545", "overruled by State v. Gaines"),
    "r166207": T(A, ALL, "State v. Allen , 339 N.C. 545", "abrogated by State v. Gaines"),
    "r176449": T(A, ALL, "Bowers v. Colonial Stages Interstate Transit, Inc., 163 Tenn. 502", "abrogated by Camper v. Minor"),
    "r192476": T(O, ALL, "Hayes v. City of Oshkosh, 33 Wis. 314", "overruled by Holytz, 17 Wis. 2d 26"),
    "r131787": T(O, ALL, "State v. Kupau, 76 Hawai", "overruled by State v. Haanio"),
    "r130991": T(O, ALL, "Maxwell v. State, 262 Ga. 73", "overruled by Wall v. State"),
    "r193044": T(O, ALL, "Richter v. State, 642 P.2d 1269", "overruled by Westmark v. State", 0.85),
    "r136538": F("otherDecision", 0.8),
    "r79468": T(O, ALL, "Zeigler Coal Co. v. Office of Workers", "overruled by Director, OWCP v. Greenwich Collieries", 0.85),
    "r167394": T(O, ALL, "State v. Thomas (1980), 61 Ohio St.2d 254", "overruled by State v. Crago"),
    "r168010": F("otherDecision", 0.9),
    "r167694": T(O, ALL, "Bailey v. City of Tulsa, Okl.Cr., 491 P.2d 316", "effectively overruled in State v. Thomason", 0.8),
    "r151963": T(O, ALL, "Harrison Cty. v. Guice , 244 Miss. 95", "v. Gilich"),
    "r132785": T(O, ALL, "State v. Diaz, 144 Idaho 300, 303", "overruled by Wulff, 157 Idaho 416"),
    "r132788": T(O, ALL, "State v. Diaz, 144 Idaho 300, 303", "overruled by State v. Wulff"),
    "r136590": F("otherDecision", 0.9),
    "r6968": T(O, OG, "Spitalny v. Tanner Const. Co., 75 Ariz. 192", "overruled in another respect in Schwartz v. Schwerin"),
    "r148961": F("negation", 0.95),
    "r160239": T(O, ALL, "Zengerle v. City of Socorro, 105 N.M. 797", "overruled by Whittenberg v. Graves Oil & Butane Co.", 0.95),
    "r135351": T(O, ALL, "People v. Morgan, 203 Ill. 2d 470", "overruled by People v. Sharpe"),
    "r151972": F("negation", 0.95),
    "r144297": T(A, ALL, "Egloff, supra, 130 Md.App. 113", "abrogated by Gosain"),
    "r152358": T(O, ALL, "Hamil v. State, 778 S.W.2d 247", "was overruled by Onken v. State", 0.95),
    "r152073": T(O, PU, "Hampton simply overruled Gordon", None, 0.85),
    "r167704": T(O, PU, "Gilmore v. State, 365 P.2d 573", "See, Jones v. State", 0.7),
    "r115794": T(O, ALL, "People v. Frazer (1999) 21 Cal.4th 737", "overruled in Stogner v. California", 0.85),
    "r193130": F("otherDecision", 0.7),
    "r155592": T(O, ALL, "Lane v. State, 110 Nev. 1156", "overruled by Leslie v. Warden"),
    "r168154": T(O, ALL, "Muskogee County v. City of Muskogee, 1991 OK 115", "overruled by Clay v. Independent School Dist."),
    "r162497": T(D, ALL, "Farmer v. Nat. Life Assn. of Hartford, 138 N. Y. 265", "disapproved in Goldey v. Morning News", 0.75),
    "r176629": T(O, ALL, "Walker v. Walker, 656 S.W.2d 11", "overruled by Seessel v. Seessel"),
    "r158964": F("negation", 0.95),
    "r114131": F("argument", 0.95),
    "r146110": T(O, ALL, "Rand v. Boston, 164 Mass. 354", "overruled by Hyde v. Fall River"),
    "r109135": T(D, PU, "People v. Babb, supra, 103 Cal.App.2d 326", "disapproved in Pryor v. Municipal Court", 0.9,
                 fl=("insofar as Babb interpreted", "unconstitutionally vague")),
    "r129782": T(O, ALL, "Ga. Power Co. v. Maddox, 113 Ga. App. 642", "Christiansen v. Robertson"),
    "r185954": F("wrongDirection", 0.9),
    "r135727": T(O, ALL, "State v. McLaughlin, 471 N.E.2d 1125", "overruled by State v. Garcia", 0.85),
    "r168515": F("negation", 0.95),
    "r156338": T(O, ALL, "Morrill v. Morrill, 5 N.H. 329", "overruled by Doughty v. Little"),
    "r169932": T(A, ALL, "Brewer v. Erwin, 287 Or 435", "abrogated by McGanty v. Staudenraus"),
    "r193257": T(O, ALL, "Bircher v. Foster, 378 P.2d 901", "overruled by Estate of Johnson, 2010 WY 63"),
    "r7289": T(O, PU, "Jones v. City of Phoenix, 29 Ariz. 181", "overruled in pari by Stone v. Arizona Highway Commission"),
    "r186385": F("negation", 0.95),
    "r108726": T(O, PU, "Pruitt v. Fontana, 143 Cal.App.2d 675", "overruled by Mattei v. Hopper", 0.9,
                 fl=("to the extent it suggested", "cases")),
    "r138778": F("otherDecision", 0.9),
}

ANS["pack_T2_012"] = {
    "r155638": T(O, ALL, "Moore v. State, 105 Nev. 378", "overruled by Peck v. State"),
    "r128271": T(D, ALL, "Nicoletti v. Nicoletti 902 So.2d 215", "disapproved by Montello v. Montello", 0.95),
    "r192356": F("argument", 0.9),
    "r151871": T(A, ALL, "West v. State, 725 So.2d 872", "abrogated by Jackson v. State", 0.8),
    "r167491": T(O, ALL, "Ratner v. Stark Cty. Bd. of Revision, 23 Ohio St.3d 59", "overruled in Berea, 106 Ohio St.3d 269"),
    "r144498": T(O, ALL, "State v. Sutton, 4 Gill. 494", "overruled by Hechter v. State"),
    "r153491": T(O, ALL, "Fields v. Maloney, 78 Mo. 172", "overruled in Stearns v. Railroad, 94 Mo. 317", 0.8),
    "r167676": T(O, ALL, "Wilson v. State, 65 Okl.Cr. 10", "overruled in the case of Ex parte Lewis, supra, 85 Okl.Cr. 322"),
    "r116576": T(O, ALL, "People v. Allen, 78 P.3d 751", "overruled by Lopez v. People"),
    "r7849": T(O, PU, "Philyaw v. State, 292 Ark. 24", "overruled, by Thomas v. State", 0.9,
               fl=("to the extent that Philyaw held", "under Rule 37")),
    "r136676": T(O, ALL, "Worley v. State (1986), Ind., 501 N.E.2d 406", "overruled by Spradlin v. State"),
    "r110408": T(D, OG, "People v. Ellhamer (1962) 199 Cal.App.2d 777", "disapproved by People v. Beeman"),
    "r3797": F("negation", 0.95),
    "r131975": T(O, PU, "Ai v. Frank Huff Agency, Ltd., 61 Haw. 607", "Sch. Bus, Inc. v. Laupahoehoe Transp. Co.", 0.9,
                 fl=("to the extent that they held", "private right")),
    "r119274": T(O, ALL, "TLC Development, Inc. v. Planning & Zoning Commission, 215 Conn. 527", "overruled by Friedman v. Planning & Zoning Commission", 0.75),
    "r156084": T(O, PU, "Judge of Probate v. Robins, 5 N. H. 246", "by Towle v. Towle", 0.9,
                 fl=("In so far as Gookin", "different rule")),
    "r136610": F("otherDecision", 0.9),
    "r155859": T(A, ALL, "Ortega v. Reyna, 114 Nev. 55", "abrogated by Martinez v. Maruszczak"),
    "r142600": T(O, ALL, "Coffin v. Rich (1858) 45 Me. 507", "Hawthorne v. Calef", 0.65),
    "r174246": T(O, ALL, "Leisinger v. Jacobson, 2002 SD 108", "overruled by State v. Martin", 0.95),
    "r139727": T(O, ALL, "Feathers v. State Farm Fire and Casualty Co.", "overruled by Federal Kemper, Ky., 711 S.W.2d 844"),
    "r162002": F("negation", 0.9),
    "r152160": T(O, OG, "Murphy v. Burlington Overall Co., 225 Mo.App. 866", "otherwise overruled in Wentz v. Price Candy Co.", 0.85),
    "r176398": T(O, ALL, "State v. Trusty, 919 S.W.2d 305", "overruled by State v. Dominy"),
    "r3804": T(O, ALL, "Yellow-Stone Kit v. State, 88 Ala. 196", "by Grimes v. State", 0.65),
    "r4267": T(O, ALL, "Yellow-Stone Kit v. State, 88 Ala. 196", "overruled by Grimes v. State"),
    "r114506": T(D, ALL, "People v. Bean (1948) 88 Cal.App.2d 34", "disapproved in People v. Kehoe"),
    "r6223": T(O, ALL, "Herzberg v. David, 27 Ariz.App; 418", "overruled by Southwestern Paint & Varnish Co."),
    "r115432": T(O, OG, "People v. Price, supra, 210 Cal.App.3d 1183", "38 Cal.App.4th 1741", 0.85),
    "r117163": T(O, PU, "Jefferson County School Dist. v. Industrial Comm", "Moffat County School Dist.", 0.9,
                 fl=("To the extent that the decisions in Umberfield", "mandate a different result")),
    "r186131": F("otherDecision", 0.55),
    "r136578": F("negation", 0.95),
    "r142594": T(O, ALL, "Furbish v. Robertson, 67 Me. 35", "overruled in Stowell v. Hooper", 0.75),
    "r119233": T(O, PU, "Blakeslee & Sons v. Carroll, 64 Conn. 223", "overruled by Petyan v. Ellis", 0.9,
                 fl=("To the extent that this court", "finally be determined")),
    "r166834": F("notOverruling", 0.95),
    "r172231": T(O, ALL, "Mintzer v. Greenough, 192 Pa. 137", "overruled in Lindstrom v. Pennsylvania Co."),
    "r146548": T(A, PU, "Jansen, petitioner, 444 Mass. 112", "abrogated by Commonwealth v. Dwyer", 0.9,
                 fl="with respect to procedure required to obtain pretrial access to records of third party"),
    "r119230": T(O, PU, "Meader v. Trout Brook Ice & Feed Co., 96 Conn. 454", "169 Conn. 593", 0.9,
                 fl=("To the extent that Meader", "action for fraud")),
    "r145220": T(O, ALL, "Key-El v. State, 349 Md. 811", "overruled by Weitzel v. State", 0.85),
    "r155415": T(O, ALL, "Theriault v. State, 92 Nev. 185", "overruled by Alford v. State"),
    "r161857": T(A, ALL, "Lozoya v. Sanchez, 2003-NMSC-009", "abrogated by Heath v. La Mariana Apartments"),
    "r172917": T(O, PU, "Previte v. Wanskuck Co., 80 R.I. 1", "Haddad v. First National Stores", 0.9,
                 fl="as it related to an infant trespasser"),
    "r138796": T(D, PU, "State v. Ochoa, 20 Kan. App. 2d 1014", "largely disapproved in State v. Valentine"),
    "r168012": F("negation", 0.95),
    "r121873": T(O, PU, "Patterson v. Brown, 5 Vet.App. 362", "partially overruled in Mayer v. Brown"),
    "r157215": T(O, PU, "State v. Lightfoot, 208 N.J.Super. 475", "State v. Hawks", 0.9,
                 fl="in its application to primarily deterrent statutes"),
    "r153640": T(O, ALL, "State ex rel. River Corp. v. State Tax Comm", "overruled in International Travel Advisors"),
    "r186445": F("notOverruling", 0.95),
    "r108636": T(D, ALL, "Wetsel v. Garibaldi, 159 Cal.App.2d 4", "disapproved in Posner v. Grunwald-Marx"),
}


def parse_pack(path):
    txt = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    items = []
    for blk in re.split(r"(?m)^### ITEM ", txt)[1:]:
        iid = blk.split("\n", 1)[0].strip()
        m = re.search(r"\nWINDOW:\n(.*?)\nNOTE AT:\n", blk, re.S)
        if not m:
            raise SystemExit("no window for " + iid)
        items.append((iid, m.group(1)))
    return items


def span(window, start, end, need_ovr=True):
    """shortest span from an occurrence of start to the first end after it"""
    if end is None:
        return start if start in window else None
    best = None
    i = window.find(start)
    while i != -1:
        j = window.find(end, i + len(start))
        if j != -1:
            s = window[i:j + len(end)]
            if (not need_ovr or OVR.search(s)) and (best is None or len(s) < len(best)):
                best = s
        i = window.find(start, i + 1)
    return best


problems = []
summary = []
for pack, answers in ANS.items():
    items = parse_pack(os.path.join(BASE, "packs", pack + ".md"))
    ids = [i for i, _ in items]
    if len(ids) != len(set(ids)):
        problems.append((pack, "duplicate ids in pack"))
    missing = [i for i in ids if i not in answers]
    extra = [i for i in answers if i not in ids]
    if missing or extra:
        problems.append((pack, "missing", missing, "extra", extra))
    lines = []
    ntrue = 0
    for iid, window in items:
        a = answers.get(iid)
        if a is None:
            continue
        if not a["states"]:
            row = {"id": iid, "states": False, "reason": a["reason"], "kind": "", "scope": "",
                   "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]}
        else:
            q = span(window, a["start"], a["end"])
            fl = a["fl"]
            if isinstance(fl, tuple):
                fl2 = span(window, fl[0], fl[1], need_ovr=False)
                if fl2 is None:
                    problems.append((pack, iid, "field_limit markers not found"))
                    fl2 = ""
                fl = fl2
            elif fl and fl not in window:
                problems.append((pack, iid, "field_limit not in window"))
            bad = None
            if q is None:
                bad = "quote markers not found"
            elif q not in window:
                bad = "quote not substring"
            elif len(q) > 400:
                bad = "quote too long %d" % len(q)
            elif not OVR.search(q):
                bad = "no overruling word"
            else:
                low = q.lower()
                hit = [f for f in FORBID if f in low]
                if hit:
                    bad = "forbidden %r" % hit
            if bad:
                problems.append((pack, iid, bad))
                q = q or ""
            ntrue += 1
            row = {"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"],
                   "field_limit": fl, "doctrine": a["doc"], "quote": q, "confidence": a["conf"]}
            print("%s %s [%d] %s" % (pack, iid, len(q), q))
            if fl:
                print("      FL: " + fl)
        lines.append(json.dumps(row, ensure_ascii=False))
    out = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    # re-read and verify
    rows = [json.loads(l) for l in open(out, encoding="utf-8").read().split("\n") if l]
    assert [r["id"] for r in rows] == ids, "order mismatch " + pack
    wmap = dict(items)
    for r in rows:
        if r["states"]:
            assert r["quote"] in wmap[r["id"]] and len(r["quote"]) <= 400 and OVR.search(r["quote"]), r["id"]
    summary.append((pack, len(rows), sum(1 for r in rows if r["states"])))

print("PROBLEMS:", problems)
print("SUMMARY:", summary)
