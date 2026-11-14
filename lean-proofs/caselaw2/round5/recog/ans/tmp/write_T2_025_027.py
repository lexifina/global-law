# -*- coding: utf-8 -*-
import json, re, sys, os

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACKS = ["pack_T2_025", "pack_T2_026", "pack_T2_027"]

# T(start, end, kind, scope, conf, field_limit="", doctrine="")
def T(s, e, kind="overruled", scope="partialUnknown", conf=0.9, fl="", doc=""):
    return {"t": True, "s": s, "e": e, "kind": kind, "scope": scope, "conf": conf, "fl": fl, "doc": doc}

def F(reason, conf=0.9):
    return {"t": False, "reason": reason, "conf": conf}

A = {}
# ---------------- pack 025
A["r192744"] = T("Harkness v. Palmyra-Eagle School District", "DNR v. City of Waukesha, 184 Wis. 2d 178")
A["r150376"] = T("State v. Shriner, 751 N.W.2d 538, 545", "133 S.Ct. 1552", "abrogated", "all")
A["r150402"] = T("State v. Shriner, 751 N.W.2d 538, 548-50", "133 S.Ct. 1552", "abrogated", "all")
A["r150405"] = T("State v. Shriner, 751 N.W.2d 538, 545", "133 S.Ct. 1552", "abrogated", "all")
A["r156429"] = T("Gilmore v. Bradgate Assocs.", "Averill v. Cox , 145 N.H. 328", "overruled", "all")
A["r109632"] = T("Fireman\u2019s Fund Ins. Co. v. Chasson", "65 Cal.2d 263", "overruled", "partialUnknown", 0.9)
A["r132672"] = T("Robison v. Frasier, 89 Idaho 326", "92 Idaho 306", "abrogated", "all")
A["r121847"] = F("quotation", 0.8)
A["r150982"] = T("Planters\u2019 Lumber Co. v. Tompkins", "Gidden et al. (Miss.), 131 So. 426", "overruled", "all", 0.85)
A["r154154"] = T("State v. Stubbs (1995), 270 Mont. 364", "State v. Loh (1996), 275 Mont. 460", "overruled", "all")
A["r166671"] = F("argument", 0.95)
A["r80860"] = T("McKinnie v. Barnhart", "abrogated by Biestek", "abrogated", "all")
A["r8062"] = T("Casa Blanca Project Lenders, L.P. v. City Commerce Bank", "Future Media Prods., Inc., 547 F.3d 956", "abrogated", "all", 0.85)
A["r145941"] = F("negation", 0.9)
A["r172248"] = T("Coxe\u2019s Estate, 193 Pa. 100", "330 Pa. 39", "overruled", "partialUnknown", 0.9)
A["r186443"] = F("notOverruling", 0.97)
A["r153461"] = F("notOverruling", 0.9)
A["r4261"] = T("Hickox v. Stover, 551 So.2d 259", "Foremost Ins. Co. v. Parham, 693 So.2d 409", "overruled", "all")
A["r185821"] = F("negation", 0.95)
A["r153470"] = F("argument", 0.95)
A["r7700"] = F("notOverruling", 0.85)
A["r153554"] = T("Manny v. Frasier", "Salmon Falls Bank v. Leyser, 116 Mo. 51", "overruled", "all")
A["r111526"] = F("notOverruling", 0.9)
A["r114369"] = T("Crosby v. Dowd, 61 Cal. 557", "De Sepulveda v. Baugh, 74 Cal. 468", "overruled", "all")
A["r167165"] = T("Stevens v. Allmen, 19 Ohio St. 485", "McLain v. Simington, 37 Ohio St. 484", "disapproved", "partialUnknown", 0.85)
A["r122039"] = F("argument", 0.95)
A["r110969"] = T("People v. Reber (1986) 177 Cal.App.3d 523", "People v. Hammon (1997) 15 Cal.4th 1117", "overruled", "partialUnknown")
A["r111632"] = T("People v. Reber (1986) 177 Cal.App.3d 523", "People v. Hammon, supra, 15 Cal.4th 1117", "disapproved", "all")
A["r124808"] = F("question", 0.95)
A["r186345"] = F("notOverruling", 0.97)
A["r114249"] = T("Peabody v. Barham, 52 Cal.App.2d 581", "MacLeod v. Tribune Publishing Co., 52 Cal.2d 536", "disapproved", "partialUnknown", 0.85, "", "rule of Peabody v. Barham (innuendo)")
A["r91045"] = T("Mondakota Gas Co. v. Montana-Dakota Utilities Co., 194 F.2d 705", "Parissi v. Telechron, Inc., 349 U.S. 46", "disapproved", "all")
A["r3781"] = F("question", 0.55)
A["r158937"] = F("otherDecision", 0.9)
A["r122176"] = T("Levy v. United States, 118 Ct.Cl. 106", "169 Ct.Cl. 1020", "overruled", "all", 0.8)
A["r4494"] = T("Garrett v. Raytheon Co., 368 So.2d 516", "Griffin v. Unocal Corp., 990 So.2d 291", "overruled", "all")
A["r134594"] = T("People v. Munetsi, 283 Ill. App. 3d 326", "People v. Fitzgibbon, 184 Ill. 2d 320", "overruled", "all")

# ---------------- pack 026
A["r151099"] = T("Harris v. Griffith, 210 So.2d 629", "Thornhill v. Systems Fuel, Inc., 523 So.2d 983")
A["r79870"] = T("Montenegro v. United States, 248 F.3d 585", "Ashley v. United States, 266 F.3d 671")
A["r112453"] = T("Murillo v. Good Samaritan Hospital (1979) 99 Cal.App.3d 50", "Flowers v. Torrance Memorial Hospital Medical Center (1994) 8 Cal.4th 992", "disapproved")
A["r80198"] = T("Gauger v. Hendle, 349 F.3d 354", "Wallace v. City of Chicago, 440 F.3d 421")
A["r115059"] = T("People v. Najera (1972) 8 Cal.3d 504", "People v. Wiley (1995) 9 Cal.4th 580", "disapproved")
A["r115099"] = T("People v. Najera (1972) 8 Cal.3d 504", "People v. Wiley (1995) 9 Cal.4th 580", "disapproved")
A["r7705"] = F("otherDecision", 0.65)
A["r5832"] = T("State v. Coleman, 122 Ariz. 130", "122 Ariz. 99", "disapproved", "otherGrounds", 0.7)
A["r5444"] = T("Samaniego v. City of Kodiak, 2 P.3d 78, 80", "Sheldon v. City of Ambler, 178 P.3d 459")
A["r5450"] = T("Samaniego v. City of Kodiak, 2 P.3d 78, 86", "Sheldon v. City of Ambler, 178 P.3d 459")
A["r5480"] = T("Samaniego v. City of Kodiak, 2 P.3d 78, 80", "Sheldon, 178 P.3d 459")
A["r190401"] = T("State v. Fitch, 164 W.Va. 337", "State v. Petry, 166 W.Va. 153")
A["r185723"] = T("115 Tex. 551, 285 S.W. 1084", "Dubai Petroleum Co. v. Kazi, 12 S.W.3d 71")
A["r136878"] = T("Thompson v. State, 875 N.E.2d 403", "Williams v. State, 895 N.E.2d 377", "abrogated")
A["r150084"] = T("White v. Johnson, 272 Minn. 363", "255 N.W.2d 362")
A["r169497"] = T("Orr v. East Valley Water District, 203 Or App 430", "Kellas v. Dept. of Corrections, 341 Or 471", "abrogated")
A["r190720"] = T("Robinson v. Continental Casualty Co., 185 W.Va. 244", "Madden, 192 W.Va. 155")
A["r191068"] = T("Robinson v. Continental Casualty Co., 185 W.Va. 244", "Madden, 192 W.Va. 155")
A["r192665"] = T("DNR v. City of Waukesha, 184 Wis. 2d 178", "Auchinleck v. Town of LaGrange, 200 Wis. 2d 585")
A["r125391"] = T("Suarez v. Commissioner, 58 T.C. 792", "Guzzetta v. Commissioner, 78 T.C. 173")
A["r125411"] = T("Suarez v. Commissioner, 58 T.C. 792", "Guzzetta v. Commissioner, 78 T.C. 173")
A["r125417"] = T("Suarez v. Commissioner, 58 T.C. 792", "Guzzetta v. Commissioner, 78 T.C. 173")
A["r139102"] = T("State v. Vandervort, 276 Kan. 164", "State v. Dickey, 301 Kan. 1018")
A["r144479"] = T("Dackman v. Dackman, 252 Md. 331", "Eastgate Associates v. Apper, 276 Md. 698", "disapproved", "otherGrounds")
A["r79063"] = T("Syvock v. Milwaukee Boiler Manufacturing Co., 665 F.2d 149", "Coston v. Plitt Theatres, Inc., 860 F.2d 834")
A["r152944"] = T("Reed v. Reed, 48 S.W.3d 634", "McElroy v. Eagle Star Group, Inc., 156 S.W.3d 392")
A["r156797"] = T("Little Falls Tp. v. Passaic Cty. Bd. of Tax., 115 N. J. Super. 115", "62 N. J. 203")
A["r160105"] = T("Watson v. Blakely, 106 N.M. 687", "Kapnison, 113 N.M. 231")
A["r160909"] = T("State v. Ortega, 2008-NMCA-001", "State v. Mendez, 2010-NMSC-044, 148 N.M. 761")
A["r132784"] = T("Ralph Naylor Farms, LLC v. Latah Cnty., 144 Idaho 806", "Randel, 152 Idaho 906", "overruled", "partialUnknown", 0.9, "as to the standard of review only")
A["r168864"] = T("Dortch v. A. H. Robins Co., Inc., 59 Or App 310", "Border v. Indian Head Industries, Inc., 101 Or App 556", "overruled", "partialUnknown", 0.8)
A["r154273"] = T("State v. Williams (1993), 262 Mont. 530", "309 Mont. 113")
A["r154420"] = T("State v. Williams (1993), 262 Mont. 530", "309 Mont. 113")
A["r56754"] = T("Goodwin v. Metis, 885 F.2d 157", "Albright v. Oliver, 510 U.S. 266")
A["r111633"] = T("Ng. v. Superior Court (1997) 52 Cal.App.4th 1010", "Curle v. Superior Court (2001) 24 Cal.4th 1057", "disapproved")
A["r154427"] = T("State v. Finley (1996), 276 Mont. 126", "304 Mont. 215")
A["r154437"] = T("State v. Finley (1996), 276 Mont. 126", "304 Mont. 215")
A["r154680"] = T("State v. Finley, 276 Mont. 126", "304 Mont. 215")
A["r131206"] = T("Pope v. State, 256 Ga. 195", "Nash v. State, 271 Ga. 281")
A["r150342"] = T("Alanis v. State, 583 N.W.2d 573", "Padilla v. Kentucky, 130 S.Ct. 1473", "abrogated")
A["r150417"] = T("583 N.W.2d 573, 578", "Padilla v. Kentucky, 559 U.S. 356", "abrogated")
A["r156147"] = T("Atherton v. Concord, 109 N.H. 164", "Totty v. Grantham Planning Board, 120 N.H. 388")
A["r156164"] = T("Atherton v. Concord, 109 N.H. 164", "Totty v. Grantham Planning Board, 120 N.H. 388")
A["r7385"] = T("Rothweiler v. Superior Court (City of Tucson), 100 Ariz. 37", "Derendal v. Griffith, 209 Ariz. 416", "abrogated")
A["r172758"] = T("Pew\u2019s Trust Estate, 411 Pa. 96", "Estate of Tyler, 474 Pa. 148")
A["r139988"] = T("Fletcher v. Howard, 226 Ky. 258", "Cissell v. Grimes Investments, Inc., 383 S.W.2d 128")
A["r168231"] = T("Rogers v. Bass & Harbour Co., 1917 OK 482", "79 Okla. 106")
A["r137375"] = T("In re Marriage of Griffin, 570 N.W.2d 258", "In re Marriage of Williams, 595 N.W.2d 126")
A["r192871"] = F("notOverruling", 0.97)
A["r7769"] = T("Townsend v. State, 76 Ark. App. 371", "Townsend v. State, 350 Ark. 129", "overruled", "partialUnknown", 0.8)

# ---------------- pack 027
A["r154634"] = T("State v. Harris, 2001 MT 231", "356 Mont. 282")
A["r176404"] = T("Knoxville Power & Light Co. v. Barnes, 156 Tenn. 184", "Standard Glass Co. v. Wallace, 189 Tenn. 213")
A["r132087"] = T("State v. Cummings", "Schwartz v. State")
A["r127910"] = F("notOverruling", 0.6)
A["r127919"] = F("notOverruling", 0.6)
A["r151675"] = T("Cole, 932 So.2d 9", "Boone, 60 So.3d 172")
A["r173767"] = T("State v. Reed, 293 S.C. 515", "State v. Torrence, 305 S.C. 45")
A["r192504"] = T("State v. Wyss, 124 Wis. 2d 681", "State v. Poellinger, 153 Wis. 2d 493", "overruled", "otherGrounds")
A["r137183"] = T("State v. Streit, 205 N.W.2d 742", "Connell, 275 N.W.2d 197", "overruled", "partialUnknown", 0.85)
A["r115374"] = F("ownAct", 0.97)
A["r153676"] = T("Reals v. Courson, 349 Mo. 1193", "Walters v. City of St. Louis, 364 Mo. 56")
A["r117480"] = T("City & Cnty. of Denver v. Gallegos, 916 P.2d 509", "Corsentino v. Cordova, 4 P.3d 1082", "overruled", "otherGrounds")
A["r117486"] = T("916 P.2d 509, 511", "Corsentino v. Cordova, 4 P.3d 1082", "overruled", "otherGrounds")
A["r127816"] = T("Lomax v. State, 345 So.2d 719", "State v. Abreau, 363 So.2d 1063", "overruled", "partialUnknown", 0.85)
A["r117307"] = T("Snyder v. City of Lakewood, 189 Colo. 421", "Margolis v. District Court, 638 P.2d 297")
A["r117376"] = T("Snyder v. City of Lakewood, 189 Colo. 421", "Margolis v. Dist. Court, 638 P.2d 297")
A["r150206"] = T("Beaudry v. State Farm Mut. Auto. Ins. Co., 518 N.W.2d 11", "Oanes v. Allstate Ins. Co., 617 N.W.2d 401")
A["r150284"] = T("Beaudry v. State Farm Mut. Auto. Ins. Co., 518 N.W.2d 11", "Oanes v. Allstate Ins. Co., 617 N.W.2d 401")
A["r131404"] = T("Cambron v. Canal Ins. Co.", "297 Ga. 683", "disapproved")
A["r131415"] = T("Cambron v. Canal Ins. Co.", "297 Ga. 683", "disapproved")
A["r154340"] = T("Downing v. Grover (1989), 237 Mont. 172", "280 Mont. 196", "overruled", "partialUnknown", 0.85)
A["r121333"] = T("United States v. Rowe, 11 M.J. 11", "United States v. Kunkle, 23 M.J. 213")
A["r191120"] = T("State v. Parsons, 108 W.Va. 705", "State v. Farley, 192 W.Va. 247", "overruled", "partialUnknown", 0.85)
A["r8273"] = T("Trawick, 497 B.R. 572", "134 S.Ct. 2242", "abrogated")
A["r161807"] = T("Farmers\u2019 Dev. Co. v. Rayado Land & Irrigation Co., 18 N.M. 1", "Kelley v. Carlsbad Irrigation Dist., 71 N.M. 464")
A["r136561"] = T("Richardson v. The State, ex rel., 55 Ind. 381", "69 Ind. 166")
A["r112469"] = T("County of Ventura v. Tillett (1982) 133 Cal.App.3d 105", "County of Los Angeles v. Soto (1984) 35 Cal.3d 483", "disapproved")
A["r5238"] = T("375 P.2d 201 (Alaska 1962)", "Scheele v. City of Anchorage, 385 P.2d 582")
A["r155580"] = T("Nika v. State, 113 Nev. 1424", "Leslie v. Warden, 118 Nev. 773")
A["r167913"] = T("Murphy v. State, 2002 OK CR 32", "127 P.3d 1135")
A["r150159"] = T("307 Minn. 72, 78-80", "Prahm v. Rupp Constr. Co., 277 N.W.2d 389")
A["r116837"] = T("Messier v. Phillips, 867 P.2d 128", "Resolution Trust Corp. v. Heiserman, 898 P.2d 1049", "disapproved")
A["r190321"] = T("State v. Ramey, 158 W.Va. 541", "State v. McAboy, 160 W.Va. 497")
A["r190244"] = T("State v. Kirkpatrick, 160 Wash.2d 873", "Jasper, 174 Wash.2d 96")
A["r154185"] = T("State v. Laubach (1982), 201 Mont. 226", "State v. Johnson (1993), 257 Mont. 157")
A["r132156"] = T("State v. Martinez, 109 Idaho 61", "111 Idaho 281", "overruled", "partialUnknown", 0.75)
A["r128058"] = T("Hyden v. State, 715 So.2d 960", "760 So.2d 89", "disapproved", "partialUnknown", 0.8)
A["r186440"] = T("688 S.W.2d 524 (Tex.Crim.App.1985)", "Williams v. State, 780 S.W.2d 802")
A["r156210"] = T("Reid v. Spadone Mach. Co., 119 N.H. 457", "Daigle v. City of Portsmouth, 129 N.H. 561")
A["r156217"] = T("Reid v. Spadone Mach. Co., 119 N.H. 457", "Daigle v. City of Portsmouth, 129 N.H. 561")
A["r79586"] = T("Lostutter v. Peters, 50 F.3d 392", "Hogan v. McBride, 74 F.3d 144", "overruled", "otherGrounds")
A["r186283"] = T("Ex Parte McAtee, 599 S.W.2d 335", "Ex Parte Tovar, 901 S.W.2d 484")
A["r167383"] = T("Travelers\u2019 Ins. Co. v. Myers (1900), 62 Ohio St. 529", "Roehm (1919), 99 Ohio St. 343")
A["r148002"] = T("Michigan Mut Liability Co v Ohio Casualty Ins Co, 123 Mich App 688", "Century Mut Ins Co v League General Ins Co, 213 Mich App 114")
A["r151676"] = T("Thompson, 972 So.2d 582", "Boone, 60 So.3d 172")
A["r151900"] = T("Thompson, 972 So.2d 582", "Boone, 60 So.3d 172")
A["r151508"] = T("Smith v. State, 656 So.2d 95", "Brown v. State, 890 So.2d 901", "overruled", "partialUnknown", 0.85)
A["r173951"] = T("Timms v. Greene, 310 S.C. 469", "405 S.C. 115", "overruled", "partialUnknown", 0.85)
A["r3707"] = F("notOverruling", 0.85)
A["r131886"] = T("Montalvo v. Chang, 64 Haw. 345", "Chun v. Bd. of Trs.")

FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)

def parse(path):
    txt = open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    items = []
    for blk in re.split(r"(?m)^### ITEM ", txt)[1:]:
        iid = blk.split("\n", 1)[0].strip()
        m = re.search(r"\nWINDOW:\n(.*?)\nNOTE AT:\n", blk, re.S)
        x = re.search(r"\nX \(the earlier decision\): (.*)", blk).group(1)
        y = re.search(r"\nY \(the decision said to have done it\): (.*)", blk).group(1)
        items.append((iid, m.group(1), x, y))
    return items

def norm(s):
    return re.sub(r"[\s.,]", "", s).lower()

def named(caption, quote):
    # citation match (normalised) or a distinctive capitalised word of the caption
    nq = norm(quote)
    parts = [p.strip() for p in caption.split(";")]
    first = parts[0]
    cites = []
    mm = re.search(r",\s*(\d+ [A-Z][^;()]*? \d+)\s*(\(\d{4}\))?$", first)
    if mm:
        cites.append(mm.group(1))
    for p in parts[1:]:
        cites.append(re.sub(r"\(\d{4}\)", "", p).strip())
    for c in cites:
        if c and norm(c) in nq:
            return "cite"
    name = first.split(",")[0]
    for w in re.findall(r"[A-Z][A-Za-z'\u2019]{3,}", name):
        if w in ("State", "United", "States", "People", "Commission", "Court", "City", "County", "Company", "Corp", "Insurance", "Superior"):
            continue
        if w.lower() in quote.lower():
            return "name:" + w
    return None

ok = True
for pack in PACKS:
    items = parse(os.path.join(BASE, "packs", pack + ".md"))
    out = []
    ntrue = 0
    for iid, win, x, y in items:
        a = A.get(iid)
        if a is None:
            print("MISSING", pack, iid); ok = False; continue
        if not a["t"]:
            out.append({"id": iid, "states": False, "reason": a["reason"], "kind": "", "scope": "", "field_limit": "",
                        "doctrine": "", "quote": "", "confidence": a["conf"]})
            continue
        i = win.find(a["s"])
        if i < 0:
            print("START NOT FOUND", pack, iid, repr(a["s"])); ok = False; continue
        j = win.find(a["e"], i + 1)
        if j < 0:
            print("END NOT FOUND", pack, iid, repr(a["e"])); ok = False; continue
        q = win[i:j + len(a["e"])]
        probs = []
        if q not in win: probs.append("not substring")
        if len(q) > 400: probs.append("len %d" % len(q))
        if not OVR.search(q): probs.append("no overruling word")
        nx, ny = named(x, q), named(y, q)
        if not nx: probs.append("X not named? " + x)
        if not ny: probs.append("Y not named? " + y)
        bad = [f for f in FORBID if f in q.lower()]
        if bad: probs.append("forbidden: %s" % bad)
        if a["fl"] and a["fl"] not in win: probs.append("field_limit not in window")
        if probs:
            print("CHECK", pack, iid, probs, "\n   ", q)
        ntrue += 1
        out.append({"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"], "field_limit": a["fl"],
                    "doctrine": a["doc"], "quote": q, "confidence": a["conf"]})
    dest = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    # re-read and verify
    rows = [json.loads(l) for l in open(dest, encoding="utf-8").read().split("\n") if l]
    wins = {iid: win for iid, win, _, _ in items}
    assert [r["id"] for r in rows] == [iid for iid, *_ in items], "order/coverage mismatch " + pack
    for r in rows:
        if r["states"]:
            assert r["quote"] in wins[r["id"]] and len(r["quote"]) <= 400 and OVR.search(r["quote"]), r["id"]
    print(pack, "items", len(items), "written", len(rows), "true", ntrue)
print("OK" if ok else "PROBLEMS")
