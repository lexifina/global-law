# -*- coding: utf-8 -*-
"""Writes ans_pack_T0_001.jsonl and ans_pack_T0_002.jsonl and verifies every quote.

Markers: literal text; a space matches any run of whitespace, the sign "\u00a4" matches any one character.
"""
import io
import json
import os
import re
import sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
W = "\u00a4"

OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
BANNED = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]


def rx(marker):
    p = re.escape(marker)
    p = p.replace("\\ ", r"\s+").replace(" ", r"\s+")
    p = p.replace(re.escape(W), ".").replace(W, ".")
    return re.compile(p)


def T(kind, scope, cands, xchk, ychk, conf, field_limit="", doctrine=""):
    return dict(states=True, kind=kind, scope=scope, cands=cands, xchk=xchk, ychk=ychk, conf=conf,
                field_limit=field_limit, doctrine=doctrine)


def F(reason, conf):
    return dict(states=False, reason=reason, conf=conf)


OG = "otherGrounds"
PU = "partialUnknown"
ALL = "all"

A1 = {
    "w001": T("overruled", PU, [("Hermann Hosp. v. MEBA", "698 F.3d 229")], ["959 F.2d 569"], ["698 F.3d 229"], 0.93),
    "w002": T("abrogated", ALL, [("Hollis v. Lynch", "116 F.4th 458")], ["827 F.3d 436"], ["116 F.4th 458"], 0.95),
    "w003": T("abrogated", OG, [("Jones v. City of Monroe", "681 F.3d 312")], ["341 F.3d 474"], ["681 F.3d 312"], 0.95),
    "w004": T("overruled", ALL, [("overruled its Lauer decision", "346 F. 2d 230")], ["Lauer"], ["346 F. 2d 230"], 0.9),
    "w005": T("overruled", ALL, [("John Morrell, the judicial", "531 F. 2d 366")], ["John Morrell"], ["531 F. 2d 366"], 0.95),
    "w006": T("abrogated", PU, [("Buise v. Hudkins, we held", "860 F.2d 280"), ("584 F.2d 223", "860 F.2d 280")],
              ["584 F.2d 223"], ["860 F.2d 280"], 0.93),
    "w007": T("overruled", PU, [("Newlin v. Helman", "Lee v. Clinton, 209 F.3d 1025"),
                                ("123 F.3d 429", "Lee v. Clinton, 209 F.3d 1025"),
                                ("123 F.3d 429", "Lee v. Clinton")],
              ["123 F.3d 429"], ["Lee v. Clinton"], 0.9),
    "w008": T("overruled", PU, [("Newlin v. Helman", "216 F.3d 626")], ["123 F.3d 429"], ["216 F.3d 626"], 0.9),
    "w009": T("abrogated", ALL, [("United States v. Newbern", "544 F.3d 781"), ("Newbern, 479", "544 F.3d 781"),
                                 ("479 F.3d 506", "544 F.3d 781"), ("479 F.3d 506", "United States v. Smith")],
              ["479 F.3d 506"], ["Smith"], 0.9),
    "w010": T("abrogated", OG, [("United States v. Blum", "668 F.3d 516"), ("534 F.3d 608", "668 F.3d 516")],
              ["534 F.3d 608"], ["668 F.3d 516"], 0.93),
    "w011": T("abrogated", OG, [("United States v. Sprouse", "598 F.3d 960")], ["394 F.3d 578"], ["598 F.3d 960"], 0.95),
    "w012": T("overruled", OG, [("United States v. Federico", "730 F.2d 1255"), ("658 F.2d 1337", "De Bright")],
              ["658 F.2d 1337"], ["De Bright"], 0.95),
    "w013": T("overruled", OG, [("O" + W + "Brien v. Sky Chefs", "810 F. 2d 1477")], ["670 F. 2d 864"], ["810 F. 2d 1477"], 0.95),
    "w014": F("otherDecision", 0.6),
    "w015": T("abrogated", OG, [("Kuntz v. Reese", "51 F.3d 1449")], ["785 F.2d 1410"], ["51 F.3d 1449"], 0.9),
    "w016": T("overruled", PU, [("United States v. Stewart, 779", "80 F. 3d 1253"),
                                ("779 F. 2d 538", "United States v. Hernandez")],
              ["779 F. 2d 538"], ["Hernandez"], 0.92),
    "w017": T("overruled", OG, [("Reynolds v. Cnty. of San Diego", "114 F.3d 999")], ["84 F.3d 1162"], ["114 F.3d 999"], 0.95),
    "w018": T("overruled", OG, [("United States v. Lillie", "179 F.3d 1143")], ["989 F.2d 1054"], ["179 F.3d 1143"], 0.95),
    "w019": T("overruled", OG, [("Gonzales v. Peo ria", "199 F. 3d 1037"), ("722 F. 2d 468", "199 F. 3d 1037")],
              ["722 F. 2d 468"], ["199 F. 3d 1037"], 0.95),
    "w020": T("overruled", OG, [("Adam v. Hawaii", "Green, 255 F.3d at 1093")], ["235 F.3d 1160"], ["Green"], 0.92),
    "w021": T("overruled", ALL, [("Pope v. Zenon", "overruled by Orso")], ["Pope v. Zenon"], ["Orso"], 0.93),
    "w022": T("overruled", OG, [("225 F.3d 1084", "409 F.3d 1177")], ["225 F.3d 1084"], ["409 F.3d 1177"], 0.93),
    "w023": T("overruled", OG, [("Atwood v. Newmont Gold", "458 F.3d 955")], ["45 F.3d 1317"], ["458 F.3d 955"], 0.95),
    "w024": T("overruled", OG, [("United States v. Jeronimo", "496 F.3d 947")], ["398 F.3d 1149"], ["496 F.3d 947"], 0.95),
    "w025": T("abrogated", OG, [("United States v. Nguyen", "642 F.3d 1257")], ["235 F.3d 1179"], ["642 F.3d 1257"], 0.95),
    "w026": T("overruled", OG, [("Estrada-Espinoza v. Mukasey, 546 F.3d 1147", "655 F.3d 915")],
              ["546 F.3d 1147"], ["655 F.3d 915"], 0.7),
    "w027": T("overruled", OG, [("King v. Atiyeh", "693 F.3d 896")], ["814 F.2d 565"], ["693 F.3d 896"], 0.95),
    "w028": T("abrogated", OG, [("Santos-Lemus v. Mukasey", "707 F.3d 1081")], ["Santos-Lemus"], ["707 F.3d 1081"], 0.95),
    "w029": T("overruled", OG, [("Towery v. Ryan", "813 F.3d 798")], ["673 F.3d 933"], ["813 F.3d 798"], 0.95),
    "w030": T("overruled", PU, [("Gibson v. County of Washoe", "833 F.3d 1060")], ["290 F.3d 1175"], ["833 F.3d 1060"], 0.92),
    "w031": T("overruled", OG, [("Metcalf v. Bochco", "by Skidmore, 952 F.3d 1051")], ["294 F.3d 1069"], ["Skidmore"], 0.93),
    "w032": T("overruled", ALL, [("Shelton v. United States", "260 F. 2d 723")], ["169 F. 2d 665"], ["260 F. 2d 723"], 0.95),
    "w033": T("abrogated", OG, [("Read Corp. v. Portec", "52 F.3d 967")], ["970 F.2d 816"], ["52 F.3d 967"], 0.95),
    "w034": F("notOverruling", 0.8),
    "w035": T("overruled", OG, [("Microsoft Corp. v. Proxyconn", "872 F.3d 1290")], ["789 F.3d 1292"], ["872 F.3d 1290"], 0.95),
    "w036": T("overruled", ALL, [("Muller v. Railway Company", "99 Cal. 538")], ["83 Cal. 240"], ["99 Cal. 538"], 0.85),
    "w037": T("overruled", ALL, [("People v. Kidd", "23 Ill. 2d 313")], ["357 Ill. 133"], ["23 Ill. 2d 313"], 0.88),
    "w038": T("overruled", ALL, [("Ellis v. Wild was", "3 Allen, 258")], ["Ellis v. Wild"], ["Merriam v. Wolcott"], 0.95),
    "w039": T("overruled", PU, [("United States v. Radetsky", "921 F.2d 994")], ["535 F.2d 556"], ["921 F.2d 994"], 0.93),
    "w040": T("overruled", OG, [("United States v. Castillo-Garcia", "Encarnacion, 291 F.3d 1219")],
              ["117 F.3d 1179"], ["291 F.3d 1219"], 0.95),
    "w041": F("notOverruling", 0.8),
    "w042": T("overruled", ALL, [("State v. Nanoff", "229 P. 727")], ["State v. English"], ["State v. Nanoff"], 0.93),
    "w043": T("abrogated", OG, [("MacKenzie v. City & Cty. of Denver", "900 F.3d 1166")], ["414 F.3d 1266"], ["900 F.3d 1166"], 0.95),
    "w044": T("overruled", ALL, [("Bank v. Pitt", "314 F.3d 541")], ["928 F.2d 1108"], ["314 F.3d 541"], 0.95),
    "w045": T("overruled", PU, [("Hecht, Levis & Kahn", "240 F.2d 460")], ["121 F.2d 442"], ["240 F.2d 460"], 0.8),
}

A2 = {
    "w046": T("overruled", ALL, [("State ex rel. Warner v. Baer", "overruling Williams v. State")],
              ["Williams v. State"], ["103 Ohio St. 585"], 0.93),
    "w047": T("overruled", ALL, [("State v. Klindt", "61 P.2d 1139")], ["Nowabbi"], ["782 P.2d 401"], 0.95),
    "w048": T("overruled", ALL, [("Wolverine case was specifically", "81 Okla. 134")], ["Wolverine"], ["81 Okla. 134"], 0.93),
    "w049": T("overruled", OG, [("Aqua Stoli Shipping", "585 F.3d 58")], ["460 F.3d 434"], ["585 F.3d 58"], 0.93),
    "w050": T("overruled", ALL, [("overruled in Louisville", "Deveaux")], ["Deveaux"], ["Letson"], 0.8),
    "w051": T("overruled", PU, [("Fleming v. Page, (practically", "Harrison")], ["Fleming v. Page"], ["Harrison"], 0.7),
    "w052": T("overruled", ALL, [("McGuire v. Card", "The Belfast, 7 Wall. 624")], ["21 How. 248"], ["7 Wall. 624"], 0.88),
    "w053": F("question", 0.55),
    "w054": T("overruled", ALL, [("Town of Concord v. Portsmouth", "that decision was overruled")],
              ["92 U. S. 625"], ["100 U. S. 47"], 0.95),
    "w055": F("notOverruling", 0.85),
    "w056": T("overruled", PU, [("it must be regarded as overruled by Pollock", "Conceding Collector v. Hubbard")],
              ["Collector v. Hubbard"], ["158 U. S. 601"], 0.8),
    "w057": T("disapproved", ALL, [("Minnesota v. Barber", "180 U. S. 499")], ["136 U. S. 313"], ["180 U. S. 499"], 0.93),
    "w058": F("notOverruling", 0.85),
    "w059": T("overruled", PU, [("Coulter v. Louisville & Nashville", "207 U. S. 20")], ["196 U. S. 599"], ["207 U. S. 20"], 0.6),
    "w060": T("overruled", PU, [("Ex parte Wisner, which is now overruled", "In re Moore")], ["Wisner"], ["In re Moore"], 0.88),
    "w061": T("overruled", PU, [("Troxell v. Delaware", "234 U. S. 86")], ["227 U. S. 434"], ["234 U. S. 86"], 0.8),
    "w062": T("overruled", ALL, [("Ex parte Wisner, 203 U. S. 449", "260 U. S. 653")], ["203 U. S. 449"], ["260 U. S. 653"], 0.95),
    "w063": F("notOverruling", 0.85),
    "w064": T("overruled", ALL, [("Hendrix v. United States", "overruled in Funk v. United States")],
              ["219 U. S. 79"], ["Funk v. United States"], 0.95),
    "w065": T("overruled", ALL, [("Jin Fuey Moy v. United States", "overruled in Funk v. United States")],
              ["254 U. S. 189"], ["Funk v. United States"], 0.95),
    "w066": T("overruled", PU, [("Wisconsin v. Pelican", "296 U. S. 268")], ["127 U. S. 265"], ["296 U. S. 268"], 0.93),
    "w067": T("overruled", PU, [("West Coast Hotel Co. v. Parrish", "298 U. S. 587")], ["298 U. S. 587"], ["300 U. S. 379"], 0.93,
              field_limit="as to power to enact minimum wage laws"),
    "w068": T("overruled", ALL, [("Helvering v. Mountain Pro ducers Corp.", "overruled by the Mountain Producers")],
              ["Childers v. Beaver"], ["303 U. S. 376"], 0.9),
    "w069": T("overruled", ALL, [("Ashton v. Cameron County District", "304 U. S. 27")], ["298 U. S. 513"], ["304 U. S. 27"], 0.65),
    "w070": T("overruled", ALL, [("Graves v. New York ex rel. O" + W + "Keefe", "16 Pet. 435")], ["16 Pet. 435"], ["306 U. S. 466"], 0.95),
    "w071": T("overruled", ALL, [("Collector v. Day", "overruled in Graves v. N. Y. ex rel. O" + W + "Keefe")],
              ["11 Wall. 113"], ["Graves v. N. Y. ex rel."], 0.93),
    "w072": F("notOverruling", 0.85),
    "w073": T("overruled", ALL, [("These cases were expressly overruled by Helvering v. Hallock", "considered in the St. Louis Trust")],
              ["St. Louis Trust"], ["Helvering v. Hallock"], 0.85),
    "w074": T("overruled", ALL, [("overruling of Fleet Corporation v. Lustgarten", "317 U. S. 575")],
              ["280 U. S. 320"], ["317 U. S. 575"], 0.7),
    "w075": T("overruled", ALL, [("Gillespie v. Oklahoma", "336 U. S. 342")], ["257 U. S. 501"], ["336 U. S. 342"], 0.92),
    "w076": T("overruled", ALL, [("Scully, supra, at 483", "337 U. S. 682")], ["Scully"], ["337 U. S. 682"], 0.7),
    "w077": F("notOverruling", 0.85),
    "w078": T("overruled", PU, [("United States v. Allegheny County", "355 U. S. 466")], ["Allegheny"], ["355 U. S. 466"], 0.93),
    "w079": F("notOverruling", 0.85),
    "w080": F("notOverruling", 0.85),
    "w081": F("notOverruling", 0.85),
    "w082": T("overruled", PU, [("overruled Wolf in that respect", "Mapp v. Ohio, 367 U. S. 643")], ["Wolf"], ["367 U. S. 643"], 0.93),
    "w083": T("overruled", PU, [("American Banana was squarely", "370 U. S. 690")], ["American Banana"], ["370 U. S. 690"], 0.88),
    "w084": F("notOverruling", 0.85),
    "w085": T("overruled", ALL, [("Noia did not appeal", "Brown v. Allen")], ["Brown v. Allen"], ["Noia"], 0.75),
    "w086": T("overruled", PU, [("Malloy decision overruled", "Twining v. New Jersey, 211 U. S. 78")],
              ["211 U. S. 78"], ["Malloy"], 0.9, doctrine="long-settled doctrine"),
    "w087": T("overruled", PU, [("Malloy decision overruled", "Adamson v. California, 332 U. S. 46")],
              ["332 U. S. 46"], ["Malloy"], 0.9, doctrine="long-settled doctrine"),
    "w088": F("notOverruling", 0.85),
    "w089": F("notOverruling", 0.85),
    "w090": T("overruled", ALL, [("Feldman v. United States", "overruled by Murphy")], ["322 U. S. 487"], ["Murphy"], 0.93),
}


def parse_pack(path):
    with io.open(path, "r", encoding="utf-8") as f:
        text = f.read()
    items = []
    for m in re.finditer(r"^### ITEM (\S+)\n(.*?)(?=^### ITEM |\Z)", text, re.S | re.M):
        body = m.group(2)
        w = re.search(r"^WINDOW:\n(.*?)\nNOTE AT:", body, re.S | re.M)
        items.append((m.group(1), w.group(1) if w else ""))
    return items


def make_quote(window, cands):
    for start, end in cands:
        ms = rx(start).search(window)
        if not ms:
            continue
        me = rx(end).search(window, ms.start())
        if not me:
            continue
        q = window[ms.start():me.end()]
        if len(q) <= 400:
            return q
    return None


def run(pack, answers):
    items = parse_pack(os.path.join(BASE, "packs", pack + ".md"))
    ids = [i for i, _ in items]
    problems = []
    if sorted(ids) != sorted(answers):
        problems.append("id mismatch: pack-only %s, answer-only %s" % (
            sorted(set(ids) - set(answers)), sorted(set(answers) - set(ids))))
    rows = []
    n_true = 0
    for iid, window in items:
        a = answers[iid]
        if not a["states"]:
            rows.append({"id": iid, "states": False, "reason": a["reason"], "kind": "", "scope": "",
                         "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]})
            continue
        q = make_quote(window, a["cands"])
        ok = q is not None
        if ok:
            if q not in window or len(q) > 400:
                problems.append("%s: not a span or too long" % iid); ok = False
            if not OVR.search(q):
                problems.append("%s: no overruling word" % iid); ok = False
            if not any(x in q for x in a["xchk"]):
                problems.append("%s: X not in quote: %r" % (iid, q)); ok = False
            if not any(y in q for y in a["ychk"]):
                problems.append("%s: Y not in quote: %r" % (iid, q)); ok = False
            if a["field_limit"] and a["field_limit"] not in window:
                problems.append("%s: field_limit not in window" % iid)
            hits = [b for b in BANNED if b in q.lower()]
            if hits:
                print("NOTE %s: quote holds refused strings %s (len %d)" % (iid, hits, len(q)))
        else:
            problems.append("%s: no candidate span of <= 400 characters" % iid)
        if not ok:
            rows.append({"id": iid, "states": False, "reason": "notInOneSpan", "kind": "", "scope": "",
                         "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]})
            continue
        n_true += 1
        rows.append({"id": iid, "states": True, "kind": a["kind"], "scope": a["scope"],
                     "field_limit": a["field_limit"], "doctrine": a["doctrine"], "quote": q,
                     "confidence": a["conf"]})
    out = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # re-read and re-verify what was written
    with io.open(out, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    assert "\r" not in raw
    back = [json.loads(line) for line in raw.split("\n") if line]
    assert [r["id"] for r in back] == ids, "order/coverage"
    wmap = dict(items)
    for r in back:
        if r["states"]:
            assert r["quote"] in wmap[r["id"]] and len(r["quote"]) <= 400 and OVR.search(r["quote"]), r["id"]
    print("%s: items %d, states true %d" % (pack, len(rows), n_true))
    for p in problems:
        print("PROBLEM", p)
    if "--show" in sys.argv:
        for r in back:
            if r["states"]:
                print(r["id"], len(r["quote"]), "|", r["quote"])


run("pack_T0_001", A1)
run("pack_T0_002", A2)
