# -*- coding: utf-8 -*-
import json, os, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
PACKS = os.path.join(BASE, "packs")
ANS = os.path.join(BASE, "ans")

OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)


def F(i, reason, conf=0.9):
    return {"id": i, "states": False, "reason": reason, "conf": conf}


def T(i, kind, scope, start, end, xs, ys, conf=0.9, field_limit="", doctrine=""):
    return {"id": i, "states": True, "kind": kind, "scope": scope, "start": start, "end": end,
            "xs": xs, "ys": ys, "conf": conf, "field_limit": field_limit, "doctrine": doctrine}


A = {}

A["pack_T1_001"] = [
    F("r174387", "question", 0.6),
    F("r174392", "negation", 0.95),
    F("r174430", "negation", 0.95),
    T("r174514", "overruled", "partialUnknown", "Wisconsin v. Pelican Insurance Co., 127 U. S. 265", "296 U. S. 268",
      ["Pelican", "127 U. S. 265"], ["Milwaukee County", "296 U. S. 268"], 0.9),
    T("r174620", "disapproved", "all", "Minnesota v. Barber, 136 U. S. 313", "180 U. S. 499",
      ["Barber", "136 U. S. 313"], ["Brundage", "180 U. S. 499"], 0.9),
    T("r174714", "overruled", "partialUnknown", "Plessy v. Ferguson, 163 U. S. 537", "347 U. S. 483",
      ["Plessy", "163 U. S. 537"], ["Brown v. Board", "347 U. S. 483"], 0.9, doctrine="separate but equal"),
    T("r174420", "overruled", "partialUnknown", "Coulter v. Louisville & Nashville R. R. Co., 196 U. S. 599", "207 U. S. 20",
      ["Coulter", "196 U. S. 599"], ["Raymond", "207 U. S. 20"], 0.6),
    F("r174415", "otherDecision", 0.7),
    T("r174464", "overruled", "all", "Ex parte Wisner, 203 U. S. 449", "260 U. S. 653",
      ["Wisner", "203 U. S. 449"], ["Lee v. Chesapeake", "260 U. S. 653"], 0.92),
    T("r174475", "overruled", "partialUnknown", "Troxell v. Delaware", "234 U. S. 86",
      ["Troxell", "227 U. S. 434"], ["Wabash", "234 U. S. 86"], 0.8),
    T("r174751", "overruled", "all", "Gillespie v. Oklahoma, 257 U. S. 501", "336 U. S. 342",
      ["Gillespie", "257 U. S. 501"], ["Texas Co.", "336 U. S. 342"], 0.88),
    T("r175382", "overruled", "partialUnknown", "Panhandle Oil Co. v. Mississippi", "314 U. S. 1",
      ["Panhandle", "277 U. S. 218"], ["King & Boozer", "314 U. S. 1"], 0.85),
    T("r175424", "overruled", "all", "Olmstead v. United States, 277 U.S. 438", "389 U.S. 347",
      ["Olmstead", "277 U.S. 438"], ["Katz", "389 U.S. 347"], 0.95),
    F("r174532", "notOverruling", 0.9),
    T("r174505", "overruled", "all", "Ashton v. Cameron County District", "304 U. S. 27",
      ["Ashton", "298 U. S. 513"], ["Bekins", "304 U. S. 27"], 0.65),
    T("r174943", "overruled", "all", "Palko v. Connecticut", "395 U. S. 784",
      ["Palko", "302 U. S. 319"], ["Benton", "395 U. S. 784"], 0.95),
    F("r174977", "otherDecision", 0.85),
    T("r174788", "overruled", "all", "United States v. Rabinowitz, 339 U. S. 56", "395 U. S. 752",
      ["Rabinowitz", "339 U. S. 56"], ["Chimel", "395 U. S. 752"], 0.93),
    T("r175326", "overruled", "all", "Knapp v. Schweitzer", "378 U. S. 52",
      ["Knapp", "357 U. S. 371"], ["Murphy", "378 U. S. 52"], 0.95),
    T("r175144", "overruled", "otherGrounds", "Monroe v. Pape, 365 U. S. 167", "436 U. S. 658",
      ["Monroe", "365 U. S. 167"], ["Monell", "436 U. S. 658"], 0.92),
    T("r175174", "overruled", "partialUnknown", "Monroe v. Pape, 365 U. S. 167", "436 U. S. 658",
      ["Monroe", "365 U. S. 167"], ["Monell", "436 U. S. 658"], 0.92),
    T("r175184", "overruled", "otherGrounds", "Monroe v. Pape, 365 U. S. 167", "436 U. S. 658",
      ["Monroe", "365 U. S. 167"], ["Monell", "436 U. S. 658"], 0.88),
    T("r175086", "overruled", "otherGrounds", "Atkinson v. Sinclair Refining Co., 370 U. S. 238", "398 U. S. 235",
      ["Atkinson", "370 U. S. 238"], ["Boys Markets", "398 U. S. 235"], 0.92),
    T("r175410", "overruled", "partialUnknown", "Townsend v. Sain", "504 U. S. 1",
      ["Townsend", "372 U. S. 293"], ["Keeney", "504 U. S. 1"], 0.93),
    T("r175362", "abrogated", "otherGrounds", "Aguilar v. Texas, 378 U. S. 108", "462 U. S. 213",
      ["Aguilar", "378 U. S. 108"], ["Gates", "462 U. S. 213"], 0.85),
    T("r175457", "abrogated", "otherGrounds", "United States v. Chadwick, 433 U. S. 1", "500 U. S. 565",
      ["Chadwick", "433 U. S. 1"], ["Acevedo", "500 U. S. 565"], 0.92),
]

A["pack_T1_002"] = [
    T("r175387", "abrogated", "all", "Parker v. Randolph", "481 U. S. 186",
      ["Parker", "442 U. S. 62"], ["Cruz", "481 U. S. 186"], 0.93),
    T("r175538", "abrogated", "otherGrounds", "Agins v. City of Tiburon", "544 U. S. 528",
      ["Agins", "447 U. S. 255"], ["Lingle", "544 U. S. 528"], 0.95),
    F("r175519", "notMajority", 0.7),
    T("r175143", "overruled", "otherGrounds", "Parratt v. Taylor", "474 U. S. 327",
      ["Parratt", "451 U. S. 527"], ["Daniels", "474 U. S. 327"], 0.92),
    T("r175173", "overruled", "partialUnknown", "Parratt v. Taylor", "474 U. S. 327",
      ["Parratt", "451 U. S. 527"], ["Daniels", "474 U. S. 327"], 0.9),
    T("r175308", "overruled", "otherGrounds", "Parratt v. Taylor", "474 U. S. 327",
      ["Parratt", "451 U. S. 527"], ["Daniels", "474 U. S. 327"], 0.92),
    T("r175532", "overruled", "all", "School Dist. of Grand Rapids v. Ball", "521 U.S. 203",
      ["Grand Rapids", "473 U.S. 373"], ["Agostini", "521 U.S. 203"], 0.6),
    F("r175249", "argument", 0.9),
    F("r175518", "notMajority", 0.7),
    T("r175431", "overruled", "all", "Saucier v. Katz", "555 U. S. 223",
      ["Saucier", "533 U. S. 194"], ["Pearson", "555 U. S. 223"], 0.93),
    T("r175471", "overruled", "partialUnknown", "McConnell v. Federal Election Comm", "558 U.S. 310",
      ["McConnell", "540 U.S. 93"], ["Citizens United", "558 U.S. 310"], 0.88),
    T("r175551", "abrogated", "otherGrounds", "Begay v. United States", "576 U. S. 591",
      ["Begay", "553 U. S. 137"], ["Johnson", "576 U. S. 591"], 0.95),
    T("r174452", "overruled", "all", "Blackstone v. Miller, 188 U. S. 189", "280 U. S. 204",
      ["Blackstone", "188 U. S. 189"], ["Farmers", "280 U. S. 204"], 0.8),
    T("r174529", "overruled", "all", "Blackstone v. Miller, 188 U. S. 189", "280 U. S. 204",
      ["Blackstone", "188 U. S. 189"], ["Farmers", "280 U. S. 204"], 0.95),
    T("r174504", "overruled", "all", "Hammer v. Dagenhart, 247 U. S. 251", "312 U. S. 100",
      ["Hammer", "247 U. S. 251"], ["Darby", "312 U. S. 100"], 0.93),
    T("r174517", "overruled", "all", "Hammer v. Dagenhart, 247 U. S. 251", "312 U. S. 100",
      ["Hammer", "247 U. S. 251"], ["Darby", "312 U. S. 100"], 0.95),
    T("r174496", "overruled", "all", "Long v. Rockwood", "286 U. S. 123",
      ["Rockwood", "277 U. S. 142"], ["Fox Film", "286 U. S. 123"], 0.95),
    T("r174530", "overruled", "all", "First National Bank v. Maine", "316 U. S. 174",
      ["First National Bank v. Maine", "284 U. S. 312"], ["Aldrich", "316 U. S. 174"], 0.95),
    F("r174495", "notOverruling", 0.9),
    T("r175320", "overruled", "all", "Delli Paoli, 229 F. 2d 319", "391 U. S. 123",
      ["Paoli", "352 U. S. 232"], ["Bruton", "391 U. S. 123"], 0.85),
    T("r175015", "overruled", "all", "Sinclair Refining Co. v. Atkinson", "398 U. S. 235",
      ["Sinclair", "370 U. S. 195"], ["Boys Markets", "398 U. S. 235"], 0.95),
    F("r175455", "notMajority", 0.75),
    T("r174933", "overruled", "all", "Food Employees v. Logan Valley Plaza", "424 U. S. 507",
      ["Logan Valley", "391 U. S. 308"], ["Hudgens", "424 U. S. 507"], 0.93),
    T("r175279", "overruled", "all", "National League of Cities v. Usery", "469 U. S. 528",
      ["National League of Cities", "426 U. S. 833"], ["Garcia", "469 U. S. 528"], 0.93),
    T("r175316", "overruled", "otherGrounds", "National League of Cities v. Usery", "469 U. S. 528",
      ["National League of Cities", "426 U. S. 833"], ["Garcia", "469 U. S. 528"], 0.95),
    T("r175315", "overruled", "all", "National League of Cities v. Usery", "469 U. S. 528",
      ["National League of Cities", "426 U. S. 833"], ["Garcia", "469 U. S. 528"], 0.95),
]

A["pack_T1s_001"] = [
    F("s01407", "otherDecision", 0.95),
    T("s00020", "overruled", "all", "Bank of United States v. Deveaux", "2 How. 497",
      ["Deveaux", "5 Cranch 61"], ["Letson", "2 How. 497"], 0.95),
    T("s00031", "overruled", "all", "The Genesee Chief, 12 How. 443", "10 Wheat. 428",
      ["Thomas Jefferson", "10 Wheat. 428"], ["Genesee Chief", "12 How. 443"], 0.93),
    F("s00910", "otherDecision", 0.9),
    F("s03154", "negation", 0.95),
    T("s00098", "overruled", "partialUnknown", "11 Pet. 175", "Insurance Co. v. Dunham",
      ["11 Pet. 175"], ["Dunham"], 0.5),
    F("s00990", "otherDecision", 0.95),
    F("s01669", "otherDecision", 0.95),
    F("s00034", "notOverruling", 0.95),
    T("s01144", "overruled", "all", "Graves v. New York ex rel. O", "16 Pet. 435",
      ["Dobbins", "16 Pet. 435"], ["Graves", "306 U. S. 466"], 0.95),
    T("s01145", "overruled", "all", "Graves v. New York ex rel. O", "Day-Dobbins",
      ["Dobbins"], ["Graves", "306 U. S. 466"], 0.8),
    F("s00041", "notOverruling", 0.85),
    T("s00099", "overruled", "partialUnknown", "New Jersey Steam Navigation Co. v. Merchants", "Insurance Co. v. Dunham",
      ["New Jersey Steam Navigation", "6 How. 344"], ["Dunham"], 0.5),
    T("s00039", "overruled", "partialUnknown", "Fleming v. Page, (practically", "v. Harrison",
      ["Fleming v. Page"], ["Harrison"], 0.85),
    F("s00911", "notOverruling", 0.9),
    F("s02847", "notOverruling", 0.95),
    F("s02947", "notOverruling", 0.95),
    F("s03055", "ownAct", 0.95),
    T("s00089", "overruled", "all", "McGuire v. Card", "7 Wall. 624",
      ["McGuire v. Card", "21 How. 248"], ["Belfast", "7 Wall. 624"], 0.85),
    F("s00176", "notOverruling", 0.9),
    F("s00108", "cannotTell", 0.9),
    F("s00141", "cannotTell", 0.9),
    F("s00515", "negation", 0.9),
    T("s02854", "overruled", "all", "Puerto Rico v. Branstad", "24 How. 66",
      ["Dennison", "24 How. 66"], ["Branstad"], 0.93),
    F("s00153", "negation", 0.95),
    F("s00177", "notOverruling", 0.9),
    T("s01148", "overruled", "all", "Graves v. New York ex rel. O", "11 Wall. 113",
      ["Collector v. Day", "11 Wall. 113"], ["Graves", "306 U. S. 466"], 0.93),
    T("s01149", "overruled", "all", "Collector v. Day, 11 Wall. 113", "Keefe",
      ["Collector v. Day", "11 Wall. 113"], ["Keefe"], 0.93),
    F("s00215", "notOverruling", 0.95),
    F("s00142", "notOverruling", 0.95),
    F("s01619", "otherDecision", 0.95),
    T("s02220", "overruled", "all", "Low v. Austin, 13 Wall. 29", "Michelin Tire Corp. v. Wages",
      ["Low v. Austin", "13 Wall. 29"], ["Michelin"], 0.95),
    F("s02221", "quotation", 0.6),
    T("s02222", "overruled", "all", "Michelin Tire Corp. v. Wages, 423 U. S. 276", "13 Wall. 29",
      ["Low v. Austin", "13 Wall. 29"], ["Michelin", "423 U. S. 276"], 0.93),
    F("s00131", "would", 0.95),
    T("s00705", "disapproved", "partialUnknown", "Barnes explicitly disapproved", "observing that Trist",
      ["Trist"], ["Barnes"], 0.65, doctrine="identification of the fund when the contract is made"),
    F("s00437", "argument", 0.95),
    F("s00148", "negation", 0.9),
    F("s00355", "notOverruling", 0.95),
    F("s00281", "argument", 0.85),
    F("s01449", "otherDecision", 0.95),
    T("s02341", "overruled", "all", "Shaffer v. Heitner", "95 U. S. 714",
      ["Pennoyer", "95 U. S. 714"], ["Shaffer", "433 U. S. 186"], 0.93),
    F("s01766", "otherDecision", 0.95),
    F("s01390", "cannotTell", 0.95),
    F("s00417", "question", 0.9),
    F("s02104", "otherDecision", 0.9),
]


def parse_pack(path):
    with open(path, encoding="utf-8", newline="") as f:
        txt = f.read().replace("\r\n", "\n")
    items = []
    for chunk in txt.split("### ITEM ")[1:]:
        iid = chunk.split("\n", 1)[0].strip()
        w0 = chunk.index("\nWINDOW:\n") + len("\nWINDOW:\n")
        w1 = chunk.index("\nNOTE AT:", w0)
        items.append((iid, chunk[w0:w1]))
    return items


def main():
    ok = True
    for pack, answers in A.items():
        items = parse_pack(os.path.join(PACKS, pack + ".md"))
        ids = [i for i, _ in items]
        aids = [a["id"] for a in answers]
        if ids != aids:
            ok = False
            print(pack, "ID MISMATCH", [x for x in ids if x not in aids], [x for x in aids if x not in ids])
            for k, (p, q) in enumerate(zip(ids, aids)):
                if p != q:
                    print("  first diff at", k, p, q)
                    break
            continue
        win = dict(items)
        rows = []
        ntrue = 0
        for a in answers:
            if not a["states"]:
                rows.append({"id": a["id"], "states": False, "reason": a["reason"], "kind": "", "scope": "",
                             "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]})
                continue
            w = win[a["id"]]
            s = w.find(a["start"])
            e = w.find(a["end"], s + 1) if s >= 0 else -1
            problem = None
            quote = ""
            if s < 0 or e < 0:
                problem = "anchor not found"
            else:
                quote = w[s:e + len(a["end"])]
                if len(quote) > 400:
                    problem = "too long %d" % len(quote)
                elif quote not in w:
                    problem = "not substring"
                elif not OVR.search(quote):
                    problem = "no overruling word"
                elif not any(x in quote for x in a["xs"]):
                    problem = "no X"
                elif not any(y in quote for y in a["ys"]):
                    problem = "no Y"
            if problem:
                print(pack, a["id"], "PROBLEM:", problem, "->", "notInOneSpan" if problem.startswith("too long") else "FIX")
                if problem.startswith("too long"):
                    rows.append({"id": a["id"], "states": False, "reason": "notInOneSpan", "kind": "", "scope": "",
                                 "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]})
                else:
                    ok = False
                continue
            ntrue += 1
            rows.append({"id": a["id"], "states": True, "kind": a["kind"], "scope": a["scope"],
                         "field_limit": a["field_limit"], "doctrine": a["doctrine"], "quote": quote,
                         "confidence": a["conf"]})
        out = os.path.join(ANS, "ans_" + pack + ".jsonl")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        # re-verify from disk
        with open(out, encoding="utf-8") as f:
            back = [json.loads(line) for line in f if line.strip()]
        assert [r["id"] for r in back] == ids, pack
        for r in back:
            if r["states"]:
                q = r["quote"]
                assert q in win[r["id"]] and len(q) <= 400 and OVR.search(q), r["id"]
        print(pack, "items", len(back), "true", sum(1 for r in back if r["states"]))
        if "-v" in sys.argv:
            for r in back:
                if r["states"]:
                    print("  ", r["id"], len(r["quote"]), "|", r["quote"])
    print("OK" if ok else "NOT OK")


main()
