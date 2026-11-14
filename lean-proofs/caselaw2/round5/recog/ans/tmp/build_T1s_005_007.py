# -*- coding: utf-8 -*-
"""Builds ans_pack_T1s_005/006/007.jsonl from reader judgments; quotes are cut from the WINDOW by anchors."""
import io, json, os, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
BANNED = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)


def F(reason, conf=0.9):
    return {"states": False, "reason": reason, "conf": conf}


def T(start, end, x, y, kind="overruled", scope="all", conf=0.9, field_limit="", doctrine=""):
    return {"states": True, "start": start, "end": end, "x": x, "y": y, "kind": kind, "scope": scope,
            "conf": conf, "field_limit": field_limit, "doctrine": doctrine}


P005 = {
    "s01356": F("argument"),
    "s02377": T("Department of Revenue of Washington v. Association", "302 U. S. 90", ["Puget Sound"], ["435 U. S. 734"]),
    "s02167": F("quotation"),
    "s01958": T("Palko was overruled in Benton", "395 U. S. 784", ["Palko"], ["Benton"]),
    "s01221": F("wrongDirection"),
    "s03010": F("otherDecision"),
    "s01302": F("wrongDirection"),
    "s02390": F("otherDecision"),
    "s02242": T("Virginia State Bd. of Pharmacy", "316 U. S. 52", ["Valentine"], ["425 U. S. 748"]),
    "s01277": F("notOverruling"),
    "s01831": F("would", 0.85),
    "s03193": F("otherDecision"),
    "s01403": F("ownAct"),
    "s01341": F("wrongDirection"),
    "s01342": F("negation"),
    "s03606": F("wrongDirection"),
    "s01360": F("quotation", 0.7),
    "s01613": F("wrongDirection"),
    "s01560": T("United States v. Allegheny County, supra, holds", "355 U. S. 466", ["Allegheny"], ["City of Detroit"],
                scope="partialUnknown"),
    "s01593": F("otherDecision"),
    "s01468": F("negation"),
    "s01466": F("argument"),
    "s02967": F("refusal"),
    "s01624": T("Baker v. Carr, 369 U. S. 186", "overruling in part Colegrove, 328 U. S. 549", ["Colegrove"],
                ["Baker v. Carr"], scope="partialUnknown"),
    "s01675": T("Wesberry v. Sanders, 376 U. S. 1", "Colegrove v. Green, 328 U. S. 549", ["Colegrove"], ["Wesberry"]),
    "s02314": T("Complete Auto Transit, Inc. v. Brady, 430 U. S. 274 (1977), overruled", "Spector and Freeman",
                ["Freeman"], ["Complete Auto"]),
    "s01435": F("otherDecision"),
    "s01946": T("Chimel, where the Court overruled", "Rabinowitz and Harris", ["Harris"], ["Chimel"],
                scope="partialUnknown",
                field_limit="as to the area of permissible search incident to a lawful arrest"),
    "s01948": T("Chimel overruled Rabinowitz", "what remained of Harris", ["Harris"], ["Chimel"], conf=0.85),
    "s03302": F("quotation"),
    "s03493": F("negation"),
    "s01698": T("Malloy, supra (overruling", "332 U. S. 46", ["Adamson"], ["Malloy"]),
    "s01438": T("Rabinowitz, supra (overruling", "Trupiano", ["Trupiano"], ["Rabinowitz"]),
    "s01439": T("Trupiano was overruled in", "339 U. S. 56", ["Trupiano"], ["Rabinowitz"], scope="partialUnknown"),
    "s01949": F("otherDecision"),
    "s01531": F("negation"),
    "s02158": F("notOverruling"),
    "s02105": T("Braden v. 30th Judicial Circuit Court of Kentucky, 410 U. S. 484 (1973), overruling", "335 U. S. 188",
                ["Ahrens"], ["Braden"]),
    "s02106": T("Braden ..., which overruled", "Ahrens", ["Ahrens"], ["Braden"], scope="partialUnknown", conf=0.6),
    "s02294": T("Craig v. Boren, 429 U. S. 190 (1976) (overruling", "335 U. S. 464", ["Goesaert"], ["Craig v. Boren"]),
    "s02295": T("Craig v. Boren, 429 U. S. 190 (1976) (gender", "335 U. S. 464", ["Goesaert"], ["Craig v. Boren"]),
    "s02264": T("Machinists v. Wisconsin", "336 U. S. 245", ["Auto Workers"], ["Machinists"]),
    "s01445": F("negation"),
    "s01729": F("argument"),
    "s01471": F("otherDecision"),
    "s01614": T("Mapp v. Ohio, 367 U. S. 643, overruling", "338 U. S. 25", ["Wolf"], ["Mapp"]),
}

P006 = {
    "s01615": T("Mapp v. Ohio, 367 U. S. 643, overruling", "338 U. S. 25", ["Wolf"], ["Mapp"]),
    "s01917": F("otherDecision"),
    "s01950": T("Rabinowitz, however, were disapproved by", "Chimel", ["Rabinowitz"], ["Chimel"], kind="disapproved"),
    "s01951": T("Chimel, where the Court overruled", "Rabinowitz", ["Rabinowitz"], ["Chimel"], scope="partialUnknown",
                field_limit="as to the area of permissible search incident to a lawful arrest"),
    "s01652": T("Darr v. Burford, 339 U. S. 200, 204 (1950) (overruled", "Fay v. Noia", ["Darr"], ["Fay v. Noia"],
                scope="otherGrounds"),
    "s01620": F("would"),
    "s01723": F("would"),
    "s02204": F("otherDecision"),
    "s01832": F("quotation"),
    "s01972": F("argument"),
    "s02214": F("argument"),
    "s01749": F("question"),
    "s01750": F("question"),
    "s01751": F("question"),
    "s01850": T("Grosso must be given", "overruling Kahriger", ["Kahriger"], ["Grosso"], conf=0.55),
    "s01518": F("argument"),
    "s01536": T("Rayonier obviously overrules", "judgment in Dalehite", ["Dalehite"], ["Rayonier"],
                scope="partialUnknown"),
    "s01630": F("ownAct"),
    "s01851": T("Grosso must be given", "Kahriger and Lewis", ["Lewis"], ["Grosso"], conf=0.55),
    "s02968": F("ownAct"),
    "s02063": F("refusal"),
    "s02246": F("argument"),
    "s01892": F("otherDecision"),
    "s02003": F("otherDecision"),
    "s01918": F("negation"),
    "s01788": F("otherDecision"),
    "s02459": F("cannotTell"),
    "s01992": F("otherDecision"),
    "s02510": F("cannotTell", 0.8),
    "s01813": T("Frank v. Maryland was overruled", "Camara v. Municipal Court", ["Frank v. Maryland"], ["Camara"],
                scope="partialUnknown"),
    "s01760": F("negation"),
    "s03303": F("quotation"),
    "s03494": F("negation"),
    "s02327": F("notOverruling"),
    "s01902": F("negation", 0.85),
    "s02511": T("United States v. Salvucci, 448 U. S. 83 (1980) (overruling", "362 U. S. 257", ["362 U. S. 257"],
                ["Salvucci"]),
    "s02391": T("Monell v. New York City Dept. of Social Services, 436 U. S. 658, we have overruled", "365 U. S. 167",
                ["Monroe"], ["Monell"], scope="partialUnknown"),
    "s02392": T("Monell overruled", "Monroe", ["Monroe"], ["Monell"], scope="partialUnknown", conf=0.75),
    "s02393": T("Monell v. New York City Dept. of Social Services, 436 U. S. 658 (1978), overruled", "365 U. S. 167",
                ["Monroe"], ["Monell"], scope="partialUnknown"),
    "s02948": F("otherDecision"),
    "s01637": F("notOverruling"),
    "s01655": F("notOverruling"),
    "s01667": F("notOverruling"),
    "s01736": F("notOverruling"),
    "s01909": F("notOverruling"),
    "s02184": T("Taylor v. Louisiana, 419 U. S. 522 (1975) (overruling in effect", "368 U. S. 57", ["Hoyt"],
                ["Taylor v. Louisiana"]),
}

P007 = {
    "s02185": T("Taylor \u201cin effect\u201d overruled", "Hoyt", ["Hoyt"], ["Taylor"]),
    "s02186": T("Taylor v. Louisiana, 419 U. S. 522 (1975) (jury", "368 U. S. 57", ["Hoyt"], ["Taylor v. Louisiana"]),
    "s01980": F("otherDecision"),
    "s02018": T("Perez v. Campbell, 402 U. S. 637 (1971) (overruling", "369 U. S. 153", ["Kesler"], ["Perez v. Campbell"]),
    "s01649": F("wrongDirection"),
    "s03665": F("cannotTell", 0.85),
    "s01786": F("ownAct"),
    "s01848": F("ownAct"),
    "s02405": F("argument"),
    "s02182": F("refusal"),
    "s03149": T("Keeney v. Tamayo-Reyes, 504 U. S. 1 (1992), partially overruled", "Townsend", ["Townsend"],
                ["Keeney"], scope="partialUnknown"),
    "s01677": F("wrongDirection"),
    "s01704": F("wrongDirection"),
    "s02031": F("otherDecision"),
    "s02367": T("Fay v. Noia, 372 U. S. 391, 430 (1963), overruled", "Sykes", ["Fay v. Noia"], ["Sykes"],
                scope="partialUnknown"),
    "s02394": F("refusal"),
    "s01928": F("otherDecision"),
    "s02868": T("Welch v. Texas Dept. of Highways and Public Transportation, 483 U. S. 468 (1987) (overruling",
                "377 U. S. 184", ["Parden"], ["Welch"], scope="partialUnknown"),
    "s02869": T("Parden we held that FELA", "overruled in Welch", ["Parden"], ["Welch"], scope="partialUnknown"),
    "s02870": T("Welch, overruled", "Parden", ["Parden"], ["Welch"], scope="partialUnknown"),
    "s02979": F("otherDecision"),
    "s02992": F("argument"),
    "s03262": F("ownAct"),
    "s03379": F("otherDecision"),
    "s01903": F("otherDecision"),
    "s02604": T("Illinois v. Gates, 462 U. S. 213 (1983) (overruling", "378 U. S. 108", ["Aguilar"], ["Illinois v. Gates"]),
    "s02796": T("Batson overruled that portion of", "Swain", ["Swain"], ["Batson"], scope="partialUnknown"),
    "s02797": T("Batson \u201cis an explicit", "portion of Swain", ["Swain"], ["Batson"], scope="partialUnknown", conf=0.8),
    "s02798": T("Batson v. Kentucky, 476 U. S. 79 (1986), which overruled", "Swain", ["Swain"], ["Batson"],
                scope="partialUnknown"),
    "s01939": F("otherDecision"),
    "s02829": T("overruled Linkletter in Griffith", "479 U. S. 314", ["Linkletter"], ["Griffith"]),
    "s02133": T("Miller v. California, 413 U. S. 15 (1973) (overruling", "383 U. S. 413", ["Memoirs"],
                ["Miller v. California"]),
    "s01945": F("otherDecision"),
    "s02783": F("negation"),
    "s02987": T("Healy v. Beer Institute, 491 U. S. 324 (1989) (overruling", "384 U. S. 35", ["Seagram"], ["Healy"]),
    "s02660": F("refusal"),
    "s03397": F("negation"),
    "s01952": F("would"),
    "s03130": F("refusal"),
    "s02036": F("otherDecision"),
    "s02354": T("Continental T. V., Inc. v. GTE Sylvania Inc., 433 U. S. 36 (1977), overruling", "388 U. S. 365",
                ["Schwinn"], ["GTE Sylvania"]),
    "s02355": T("Continental T. V., Inc. v. GTE Sylvania Inc., 433 U. S. 36 (1977), we overruled", "388 U. S. 365",
                ["Schwinn"], ["GTE Sylvania"]),
    "s02356": T("GTE Sylvania, 433 U. S., at 57-59 (overruling", "388 U. S. 365", ["Schwinn"], ["GTE Sylvania"]),
    "s01835": F("otherDecision"),
    "s01937": F("wrongDirection"),
    "s01893": F("wrongDirection"),
}


def parse_pack(path):
    text = io.open(path, encoding="utf-8").read().replace("\r\n", "\n")
    items = []
    for block in text.split("### ITEM ")[1:]:
        iid = block.split("\n", 1)[0].strip()
        m = re.search(r"\nWINDOW:\n(.*?)\nNOTE AT:\n", block, re.S)
        if not m:
            raise SystemExit("no window for " + iid)
        items.append((iid, m.group(1)))
    return items


def build(pack, spec):
    items = parse_pack(os.path.join(BASE, "packs", pack + ".md"))
    ids = [i for i, _ in items]
    problems = []
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids in pack")
    missing = [i for i in ids if i not in spec]
    extra = [i for i in spec if i not in ids]
    if missing or extra:
        problems.append("missing %s extra %s" % (missing, extra))
    rows = []
    for iid, window in items:
        a = spec.get(iid)
        if a is None:
            continue
        if not a["states"]:
            rows.append({"id": iid, "states": False, "reason": a["reason"], "kind": "", "scope": "",
                         "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]})
            continue
        i = window.find(a["start"])
        j = window.find(a["end"], i + 1) if i >= 0 else -1
        if i < 0 or j < 0:
            problems.append("%s: anchor not found (start %s, end %s)" % (iid, i, j))
            continue
        quote = window[i:j + len(a["end"])]
        if quote not in window:
            problems.append(iid + ": quote not a substring")
        if len(quote) > 400:
            problems.append("%s: quote too long (%d)" % (iid, len(quote)))
        if not OVR.search(quote):
            problems.append(iid + ": no overruling word")
        if not any(n in quote for n in a["x"]):
            problems.append(iid + ": X not named in quote")
        if not any(n in quote for n in a["y"]):
            problems.append(iid + ": Y not named in quote")
        hit = [b for b in BANNED if b in quote.lower()]
        if hit:
            problems.append("%s: banned strings %s" % (iid, hit))
        if a["field_limit"] and a["field_limit"] not in window:
            problems.append(iid + ": field_limit not in window")
        rows.append({"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"],
                     "field_limit": a["field_limit"], "doctrine": a["doctrine"], "quote": quote,
                     "confidence": a["conf"]})
    out = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # re-read and re-verify from disk
    back = [json.loads(l) for l in io.open(out, encoding="utf-8").read().split("\n") if l]
    wmap = dict(items)
    if [r["id"] for r in back] != ids:
        problems.append("order/coverage mismatch on disk")
    for r in back:
        if r["states"]:
            q = r["quote"]
            if q not in wmap[r["id"]] or len(q) > 400 or not OVR.search(q):
                problems.append(r["id"] + ": disk re-check failed")
    sys.stdout.write("%s: items %d, states true %d\n" % (pack, len(back), sum(1 for r in back if r["states"])))
    for r in back:
        if r["states"]:
            sys.stdout.buffer.write(("  %s [%d] %s\n" % (r["id"], len(r["quote"]), r["quote"])).encode("utf-8"))
    for p in problems:
        sys.stdout.write("  PROBLEM " + p + "\n")
    return problems


if __name__ == "__main__":
    allp = []
    for pack, spec in (("pack_T1s_005", P005), ("pack_T1s_006", P006), ("pack_T1s_007", P007)):
        allp += build(pack, spec)
    sys.stdout.write("problems: %d\n" % len(allp))
