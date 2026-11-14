# -*- coding: utf-8 -*-
import json, re, sys, io, os

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]

# id: (start, end, xtokens, ytokens, scope, field_limit, confidence)  or  id: ("FALSE", reason, confidence)
T = "T"
A = {
 "pack_T1s_011": {
  "s01128": ("Erie R. Co. v. Tompkins, 304 U. S. 64, overruling", "Swift v. Tyson, 16 Pet. 1", ["Swift v. Tyson"], ["Tompkins"], "all", "", 0.95),
  "s01129": ("In overruling Swift v. Tyson", "Erie R. Co. v. Tompkins", ["Swift v. Tyson"], ["Tompkins"], "all", "", 0.93),
  "s01130": ("Erie R. Co. v. Tompkins, 304 U. S. 64, overruling", "Swift v. Tyson, 16 Pet. 1", ["Swift v. Tyson"], ["Tompkins"], "all", "", 0.95),
  "s03035": ("Collins v. Youngblood, 497 U. S. 37", "107 U. S. 221", ["Kring"], ["Collins v. Youngblood"], "all", "", 0.93),
  "s03037": ("Collins v. Youngblood, 497 U.S. 37", "(overruling Kring", ["Kring"], ["Collins v. Youngblood"], "all", "", 0.8),
  "s01987": ("The Harrisburg initially", "Moragne v. States Marine Lines, Inc., 398 U. S. 375", ["The Harrisburg"], ["Moragne"], "partialUnknown", "", 0.85),
  "s01988": ("Moragne v. States Marine Lines, 398 U. S. 375", "The Harrisburg, 119 U. S. 199", ["The Harrisburg"], ["Moragne"], "all", "", 0.95),
  "s02444": ("Hughes v. Oklahoma, 441 U. S. 322", "Geer v. Connecticut, 161 U. S. 519", ["Geer"], ["Hughes v. Oklahoma"], "all", "", 0.94),
  "s01198": ("Connolly v. Union Sewer", "Tigner v. Texas, 310 U. S. 141", ["Connolly"], ["Tigner"], "all", "", 0.9),
  "s01270": ("Williams v. North Carolina, 317 U. S. 287", "Haddock v. Haddock, 201 U. S. 562", ["Haddock"], ["Williams v. North Carolina"], "all", "", 0.95),
  "s00759": ("Dick Company. This Court held", "243 U. S. 502", ["Dick"], ["Motion Picture Patents"], "all", "", 0.75),
  "s00760": ("Henry v. Dick, 224 U. S. 1", "243 U. S. 502", ["Henry v. Dick"], ["Motion Picture Patents"], "partialUnknown", "", 0.92),
  "s01214": ("United States v. Darby, 312 U. S. 100, overruled", "Hammer v. Dagenhart, 247 U. S. 251", ["Hammer v. Dagenhart"], ["Darby"], "partialUnknown", "as to Congressional power over labor in manufacture", 0.92),
  "s01215": ("United States v. Darby, 312 U. S. 100, overruling", "Hammer v. Dagenhart, 247 U. S. 251", ["Hammer v. Dagenhart"], ["Darby"], "all", "", 0.95),
  "s01237": ("Nye v. United States, 313 U. S. 33", "Toledo Newspaper Co. v. United States, 247 U. S. 402", ["Toledo Newspaper"], ["Nye v. United States"], "all", "", 0.95),
  "s01109": ("Helvering v. Mountain Producers Corp., 303 U. S. 376", "Gillespie v. Oklahoma, 257 U. S. 501", ["Gillespie"], ["Mountain Producers"], "all", "", 0.95),
  "s01111": ("Helvering v. Mountain Producers Corp., 303 U. S. 376", "squarely overruled Gillespie", ["Gillespie"], ["Mountain Producers"], "all", "", 0.95),
  "s01080": ("West Coast Hotel Co. v. Parrish, 300 U. S. 379, overruled", "261 U. S. 525", ["Adkins"], ["West Coast Hotel"], "partialUnknown", "as to power to enact minimum wage laws", 0.92),
  "s01081": ("West Coast Hotel Co. v. Parrish, 300 U. S. 379, overruling", "261 U. S. 525", ["Adkins"], ["West Coast Hotel"], "all", "", 0.95),
  "s01082": ("West Coast Hotel Co. v. Parrish, supra, overruling", "Hospital", ["Adkins"], ["West Coast Hotel"], "all", "", 0.93),
  "s01230": ("California v. Thompson, 313 U. S. 109", "DiSanto v. Pennsylvania, 273 U. S. 34", ["DiSanto"], ["California v. Thompson"], "all", "", 0.95),
  "s01932": ("Whitney v. California, supra, since", "Brandenburg v. Ohio, 395 U. S. 444", ["Whitney"], ["Brandenburg"], "all", "", 0.93),
  "s01933": ("Brandenburg v. Ohio, 395 U. S. 444 (1969). We expressly", "Whitney v. California, 274 U. S. 357", ["Whitney"], ["Brandenburg"], "partialUnknown", "", 0.9),
  "s01934": ("Brandenburg v. Ohio, 395 U. S. 444", "274 U. S. 357", ["274 U. S. 357"], ["Brandenburg"], "all", "", 0.93),
  "s01232": ("Ribnik, supra, has long", "Olsen v. Nebraska, 313 U. S. 236", ["Ribnik"], ["Olsen v. Nebraska"], "all", "", 0.7),
  "s02138": ("North Dakota Pharmacy Bd.", "Baldridge, 278 U. S. 105", ["Liggett"], ["Snyder"], "all", "", 0.94),
  "s01261": ("State Tax Commission v. Aldrich, 316 U. S. 174", "First National Bank v. Maine, 284 U. S. 312", ["First National Bank v. Maine"], ["Aldrich"], "all", "", 0.95),
  "s01115": ("Helvering v. Mountain Producers Corp., 303 U. S. 6", "Burnet v. Coronado Oil & Gas Co., 285 U. S. 393", ["Coronado"], ["Mountain Producers"], "all", "", 0.93),
  "s01117": ("Helvering v. Mountain Producers Corp., 303 U. S. 376", "Burnet v. Coronado Oil & Gas Co., 285 U. S. 393", ["Coronado"], ["Mountain Producers"], "all", "", 0.94),
  "s01886": ("Peyton v. Rowe intervened", "McNally v. Hill, 293 U. S. 131", ["McNally"], ["Peyton v. Rowe"], "all", "", 0.94),
  "s01887": ("Peyton v. Rowe, 391 U. S. 54", "McNally v. Hill, 293 U. S. 131", ["McNally"], ["Peyton v. Rowe"], "all", "", 0.95),
  "s01888": ("Peyton v. Rowe, 391 U. S. 54", "we overruled McNally", ["McNally"], ["Peyton v. Rowe"], "all", "", 0.95),
  "s01300": ("Allwright, supra, at 663-666", "Grovey v. Townsend, 295 U. S. 45", ["Grovey"], ["Allwright"], "all", "", 0.93),
  "s01301": ("Smith v. Allwright, 321 U. S. 649", "Grovey v. Townsend, 295 U. S. 45", ["Grovey"], ["Allwright"], "all", "", 0.94),
  "s01194": ("Madden v. Kentucky, 309 U. S. 83", "Colgate v. Harvey, 296 U. S. 404", ["Colgate"], ["Madden"], "all", "", 0.95),
  "s01289": ("Board of Education v. Barnette, 319 U. S. 624", "Gobitis, 310 U. S. 586", ["Gobitis"], ["Barnette"], "all", "", 0.95),
  "s01290": ("Barnette, supra, was faced", "Gobitis, 310 U. S. 586", ["Gobitis"], ["Barnette"], "all", "", 0.9),
  "s01291": ("Barnette, supra, was faced", "Gobitis, 310 U. S. 586", ["Gobitis"], ["Barnette"], "all", "", 0.55),
 },
 "pack_T1s_012": {
  "s02051": ("Andrews v. Louisville & Nashville R. Co., 406 U. S. 320", "Moore v. Illinois Central R. Co., 312 U. S. 630", ["Moore v. Illinois Central"], ["Andrews"], "all", "", 0.95),
  "s02052": ("Andrews v. Louisville & Nashville R. Co., 406 U. S. 320", "Moore v. Illinois Central R. Co., 312 U. S. 630", ["Moore v. Illinois Central"], ["Andrews"], "all", "", 0.95),
  "s01644": ("Gideon v. Wainwright, supra (overruling", "Betts v. Brady, 316 U. S. 455", ["Betts"], ["Gideon"], "all", "", 0.94),
  "s01645": ("Betts was in turn overruled", "Gideon v. Wainwright, 372 U. S. 335", ["Betts"], ["Gideon"], "all", "", 0.95),
  "s01714": ("Feldman v. United States, 322 U. S. 487", "overruled by Murphy", ["Feldman"], ["Murphy"], "all", "", 0.93),
  "s01604": ("James v. United States, 366 U. S. 213 (1961). In the latter", "Wilcox, 327 U. S. 404", ["Wilcox"], ["James v. United States"], "all", "", 0.93),
  "s01605": ("James v. United States, 366 U. S. 213", "(overruling Wilcox", ["Wilcox"], ["James v. United States"], "all", "", 0.95),
  "s01923": ("Moore v. Ogilvie, 394 U. S. 814", "MacDougall v. Green, 335 U. S. 281", ["MacDougall"], ["Moore v. Ogilvie"], "all", "", 0.95),
  "s02318": ("Spector, which had", "by Complete Auto", ["Spector"], ["Complete Auto"], "all", "", 0.6),
  "s02319": ("Complete Auto Transit, Inc. v. Brady, 430 U. S. 274", "which overruled Spector", ["Spector"], ["Complete Auto"], "all", "", 0.95),
  "s02320": ("Complete Auto Transit, Inc. v. Brady, we overruled", "340 U. S. 602", ["Spector"], ["Complete Auto"], "all", "", 0.95),
  "s01894": ("Lee v. Florida, 392 U. S. 378", "we overruled Schwartz v. Texas", ["Schwartz"], ["Lee v. Florida"], "all", "", 0.95),
  "s01895": ("Lee v. Florida, supra, this Court", "Schwartz v. Texas, 344 U. S. 199", ["Schwartz"], ["Lee v. Florida"], "all", "", 0.95),
  "s02933": ("Wilko decided", "490 U. S. 477", ["Wilko"], ["Quijas"], "partialUnknown", "", 0.88),
  "s01859": ("Bruton v. United States, 391 U. S. 123", "Delli Paoli v. United States, 352 U. S. 232", ["Paoli"], ["Bruton"], "all", "", 0.95),
  "s01860": ("Delli Paoli was expressly", "Bruton v. United States", ["Paoli"], ["Bruton"], "all", "", 0.95),
  "s02272": ("New Orleans v. Dukes, 427 U. S. 297", "Morey v. Doud, 354 U. S. 457", ["Morey"], ["Dukes"], "all", "", 0.94),
  "s01811": ("FALSE", "quotation", 0.65),
  "s01745": ("Swift & Co. v. Wickham, 382 U. S. 111", "we overruled Kesler", ["Kesler"], ["Wickham"], "all", "", 0.94),
  "s01746": ("Swift & Co. v. Wickham, 382 U. S. 111", "369 U. S. 153", ["Kesler"], ["Wickham"], "all", "", 0.94),
  "s01981": ("Boys Markets v. Retail Clerks Union, 398 U. S. 235", "overruling Sinclair", ["Sinclair"], ["Boys Markets"], "all", "", 0.95),
  "s01982": ("Boys Markets, Inc. v. Retail Clerks, 398 U. S. 235", "Atkinson, 370 U. S. 195", ["Sinclair"], ["Boys Markets"], "all", "", 0.95),
  "s03332": ("Khan, 522 U. S., at 22", "Albrecht v. Herald Co., 390 U. S. 145", ["Albrecht"], ["Khan"], "all", "", 0.94),
  "s03333": ("State Oil Co. v. Khan, 522 U. S. 3", "Albrecht v. Herald Co., 390 U. S. 145", ["Albrecht"], ["Khan"], "all", "", 0.95),
  "s02234": ("Hudgens v. NLRB, 424 U. S. 507", "overruling of Logan Valley", ["Logan Valley"], ["Hudgens"], "all", "", 0.94),
  "s02864": ("Solorio v. United States, 483 U. S. 435", "Parker, 395 U. S. 258", ["Callahan"], ["Solorio"], "all", "", 0.94),
  "s02865": ("Solorio v. United States, 483 U. S. 435", "Parker, 395 U. S. 258", ["Callahan"], ["Solorio"], "all", "", 0.95),
  "s02866": ("Solorio v. United States, 483 U. S. 435", "Callahan", ["Callahan"], ["Solorio"], "all", "", 0.94),
  "s02705": ("Garcia v. San Antonio Metropolitan Transit Authority, 469 U. S. 528", "National League of Cities v. Usery", ["National League of Cities"], ["Garcia"], "all", "", 0.93),
  "s03690": ("Janus v. State, County, and Municipal Employees", "Abood v. Detroit Bd. of Ed.", ["Abood"], ["Janus"], "all", "", 0.8),
  "s03591": ("Montejo v. Louisiana, 556 U. S. 778", "Michigan v. Jackson, 475 U. S. 625", ["Michigan v. Jackson"], ["Montejo"], "all", "", 0.94),
  "s03593": ("Montejo v. Louisiana, 556 U. S. 778", "475 U. S. 625", ["475 U. S. 625"], ["Montejo"], "all", "", 0.94),
  "s03483": ("Lawrence v. Texas, 539 U. S. 558", "Bowers v. Hardwick, 478 U. S. 186", ["Bowers"], ["Lawrence v. Texas"], "all", "", 0.95),
  "s03111": ("Payne v. Tennessee, 501 U. S. 808", "Booth v. Maryland, 482 U. S. 496", ["Booth"], ["Payne"], "all", "", 0.94),
  "s03112": ("FALSE", "quotation", 0.8),
  "s03608": ("Citizens United, supra, at 362", "Austin, 494 U. S. 652", ["Austin"], ["Citizens United"], "all", "", 0.94),
  "s03609": ("Citizens United v. Federal Election Comm", "Austin v. Michigan Chamber of Commerce, 494 U. S. 652", ["Austin"], ["Citizens United"], "all", "", 0.95),
  "s03649": ("Alleyne, 570 U. S., at 107", "Harris v. United States, 536 U. S. 545", ["Harris"], ["Alleyne"], "all", "", 0.94),
 },
}


def parse(pack):
    with io.open(os.path.join(BASE, "packs", pack + ".md"), encoding="utf-8", newline="") as f:
        text = f.read()
    items = []
    for chunk in text.split("### ITEM ")[1:]:
        lines = chunk.replace("\r\n", "\n").split("\n")
        iid = lines[0].strip()
        wi = lines.index("WINDOW:")
        ni = lines.index("NOTE AT:")
        window = "\n".join(lines[wi + 1:ni])
        if window.endswith("\n"):
            window = window[:-1]
        items.append((iid, window))
    return items


ok = True
for pack, ans in A.items():
    items = parse(pack)
    ids = [i for i, _ in items]
    if ids != list(ans.keys()):
        print("ORDER/ID MISMATCH", pack, [i for i in ids if i not in ans], [i for i in ans if i not in ids])
        ok = False
    out = []
    ntrue = 0
    for iid, window in items:
        a = ans[iid]
        if a[0] == "FALSE":
            out.append({"id": iid, "states": False, "reason": a[1], "kind": "", "scope": "", "field_limit": "",
                        "doctrine": "", "quote": "", "confidence": a[2]})
            continue
        start, end, xt, yt, scope, fl, conf = a
        s = window.find(start)
        e = window.find(end, s) if s >= 0 else -1
        if s < 0 or e < 0:
            print("ANCHOR MISSING", pack, iid, s, e)
            ok = False
            continue
        q = window[s:e + len(end)]
        probs = []
        if q not in window:
            probs.append("not substring")
        if len(q) > 400:
            probs.append("len %d" % len(q))
        if not re.search(r"overrul|abrogat|disapprov|reced", q, re.I):
            probs.append("no word")
        if not any(t in q for t in xt):
            probs.append("no X")
        if not any(t in q for t in yt):
            probs.append("no Y")
        bad = [b for b in FORBID if b in q.lower()]
        if bad:
            probs.append("forbidden %s" % bad)
        if fl and fl not in window:
            probs.append("field_limit not in window")
        if probs:
            print("PROBLEM", pack, iid, probs, "|", q)
            if any(not p.startswith("forbidden") for p in probs):
                ok = False
        ntrue += 1
        out.append({"id": iid, "states": True, "kind": "overruled", "scope": scope, "field_limit": fl,
                    "doctrine": "", "quote": q, "confidence": conf})
    path = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    # re-read and verify
    with io.open(path, encoding="utf-8", newline="") as f:
        raw = f.read()
    assert "\r" not in raw
    rows = [json.loads(l) for l in raw.split("\n") if l]
    wmap = dict(items)
    assert [r["id"] for r in rows] == ids, "ids differ"
    for r in rows:
        if r["states"]:
            assert r["quote"] in wmap[r["id"]] and len(r["quote"]) <= 400, r["id"]
    print(pack, "items", len(rows), "true", sum(1 for r in rows if r["states"]))
    for r in rows:
        if r["states"]:
            print("  ", r["id"], len(r["quote"]), "|", r["quote"])
print("OK" if ok else "NOT OK")
