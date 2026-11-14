"""scdb9: post-filter of sc9.py rows -> the rows round 9 may add over the v8e base (copy of round 8's select8.py,
base v8e, round-9 classes).

    python -X utf8 select9.py   -> rows9.jsonl, remove9.txt, work/select9_stats.json

Inputs: work/rows_all.jsonl (every rule), work/rows_all_r8.jsonl (round-8 rules + the WEAK fix), leave-one-out runs
work/rows_all_noJ / _noA9 / _noR4w.jsonl, round 8's own run round8/agents/scdb8/work/diag8.jsonl.gz (only to name the
decisions the round-8 NameError skipped), round8/stage/v8e/history.tsv. No key file.

Classes (rule id below:sc9_<cls>_<anchor type>):
  dfix   round 8's D1/D3/D5 judgment readings (not installed in round 8), with the D-fix filters
  j      round-9 judgment readings j1-j4 (with the D-fix filters)
  a9     round-9 anchor (court-pronoun subject / own-name citation sentence), R3 restated
  r4w    rows re-targeted by the widened rehearing-denial phrase
  wfix   rows of the decisions round 8's sc8sel NameError skipped (round 6/7/8 rules, unchanged)
D-fix filters (dfix, j): the target's anchoring citation is not a rehearing-denial citation (_reh9); the restated R3
test (_sole9, _latest9, caption) holds; kind is reversed | vacated | affirmed (no modified); the judgment sentence has no
limiting clause ("according to which", "to the extent", "insofar", "as to"). Generic guards as select8.
"""
import collections, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORK = os.path.join(HERE, "work")
NL = chr(10)
WEAK = {"A1w", "HM_A1", "A2", "A3"}
REVIEW = {"reversed", "vacated", "affirmed", "modified", "reviewDismissed"}
LIMIT = re.compile(r"\baccording\s+to\s+which\b|\bto\s+the\s+extent\b|\binsofar\b|\bin\s+so\s+far\b|\bas\s+to\b|\bin\s+part\b|"
                   r"\bexcept\b|\bso\s+far\s+as\b|\bonly\s+(?:on|as\s+to|with\s+respect\s+to|insofar|in\s+so\s+far)\b|"
                   r"\bon\s+(?:that|this|the\s+\w+)\s+(?:issue|question|claim)\s+only\b", re.I)
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def keys(p):
    return {(r["by"], r["target"], r["kind"]) for r in load(p)} if os.path.exists(p) else None


def main():
    F = L.Facts()
    full = load(os.path.join(WORK, "rows_all.jsonl"))
    r8k = keys(os.path.join(WORK, "rows_all_r8.jsonl"))
    loo = {c: keys(os.path.join(WORK, "rows_all_%s.jsonl" % t)) for t, c in (("noJ", "j"), ("noA9", "a9"), ("noR4w", "r4w"))}
    err8 = set()
    with gzip.open(os.path.join(C2, "round8", "agents", "scdb8", "work", "diag8.jsonl.gz"), "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if (d.get("reason") or "").startswith("error"):
                err8.add(d["n"])
    base = collections.defaultdict(list)
    with open(os.path.join(C2, "round8", "stage", "v8e", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[4] in REVIEW:
                base[int(p[2])].append((p[0], int(p[1]), p[4], p[12]))
    texts_needed = set()
    st = collections.Counter()
    cand = []
    for r in full:
        st["in"] += 1
        k = (r["by"], r["target"], r["kind"])
        vr = base.get(r["by"], [])
        if any(t == r["target"] for _i, t, _k, _s in vr):
            st["skip:in_base"] += 1
            continue
        need = [c for c, ks in loo.items() if ks is not None and k not in ks]
        if not any(ks is not None for ks in loo.values()):
            # attribution by row flags (leave-one-out runs not made): judgment reading j1-j4, anchor a9, else a row
            # the round-8 rule set (with the WEAK fix) does not make = the widened rehearing-denial phrase (r4w)
            need = (["j"] if r.get("_j9") else []) + (["a9"] if r.get("_a9") else [])
            if not need and k not in r8k:
                need = ["r4w"]
        if need:
            cls = need[0] if len(need) == 1 else "multi9"
        elif r.get("_d1"):
            cls = "dfix"
        elif r["by"] in err8 and k in r8k:
            cls = "wfix"
        else:
            st["skip:old_class_not_installed"] += 1
            continue
        st["new:" + cls] += 1
        rem = []
        if vr:
            others = {t for _i, t, _k, _s in vr}
            ok = all(int(F.court[t]) == int(F.court[r["target"]]) and int(F.date[t]) > int(F.date[r["target"]])
                     for t in others)
            linker = all(s.startswith(("r6:below:sc_", "r7:below:sc7_", "r7:below:sc8_")) for _i, _t, _k, s in vr)
            if cls == "r4w" and ok and linker:
                rem = [i for i, _t, _k, _s in vr]
                cls = "r4wrep"
            else:
                st["drop:other_base_row:" + cls] += 1
                continue
        if not r.get("_share"):
            st["drop:no_shared_party_token:" + cls] += 1
            continue
        if r.get("_dock") == "drop":
            st["drop:docket_unresolved:" + cls] += 1
            continue
        if isinstance(r.get("_dock"), list):
            r["kind"], r["scope"] = r["_dock"]
        typ = r["_typ"]
        judg = cls in ("dfix", "j") or (cls == "multi9" and (r.get("_j9") or r.get("_d1")))
        if judg or cls == "a9":
            if r.get("_reh9"):
                st["drop:reh9:" + cls] += 1
                continue
            if not (r.get("_sole9") and r.get("_latest9") and r.get("_cap")):
                st["drop:r3_restated:" + cls] += 1
                continue
        elif r["_path"] == "strict" and typ in WEAK and not (r["_sole"] and r["_latest"] and r.get("_share") and r["_cap"]):
            st["drop:weak_not_r3:" + cls] += 1
            continue
        if judg:
            if r["kind"] not in ("reversed", "vacated", "affirmed"):
                st["drop:kind_" + r["kind"] + ":" + cls] += 1
                continue
            texts_needed.add(r["by"])
        if r["_path"] == "loose" and r.get("_sub") in ("nozone", "fn"):
            st["drop:loose_nozone_fn:" + cls] += 1
            continue
        if r.get("_dcond"):
            st["drop:conditional:" + cls] += 1
            continue
        if r.get("_side"):
            st["drop:side_proceeding:" + cls] += 1
            continue
        if not r["_before_disp"] and r.get("_sub") != "fn":
            st["drop:footnote:" + cls] += 1
            continue
        if r["_rp"] and (r.get("_name_fail") or not r["ev"].startswith("name:")):
            st["drop:rp_name_fail:" + cls] += 1
            continue
        cand.append((r, cls, rem, judg))
    texts = L.fetch_texts(sorted(texts_needed)) if texts_needed else {}
    out, remove = [], []
    for r, cls, rem, judg in cand:
        claim = "-"
        if judg:
            q0, q1 = r["disp"]
            raw = texts[r["by"]][1]
            q = raw[q0:q1]
            if LIMIT.search(q) or LIMIT.search(raw[q1:q1 + 300].split(chr(10) + chr(10))[0]):
                st["drop:limiting_clause:" + cls] += 1
                continue
            # C1 (round-9 cut after r9b01): one judgment sentence that affirms one judgment and reverses / vacates another
            if re.search(r"\baffirm(?:s|ed)?\b", q, re.I) and re.search(r"\b(?:revers|vacat|set\s+aside)", q, re.I):
                st["drop:mixed_sentence:" + cls] += 1
                continue
            # C3: a "judgment sentence" that is a string of citations (two or more reporter citations)
            if len(re.findall(r"\b\d{1,4}\s+(?:U\.\s?S\.|F\.\s?(?:\d[a-z]{1,2}|Supp\.)|S\.\s?Ct\.|[A-Z][A-Za-z.]{1,12}\s?(?:\d[a-z]{1,2})?)\s+\d{1,5}\b", q)) >= 2:
                st["drop:citation_string:" + cls] += 1
                continue
            if r["kind"] == "vacated" and not re.search(r"vacat", q, re.I):
                if re.search(r"set\s+aside", q, re.I):
                    claim = "setAside"
                else:
                    st["drop:no_vacat_cue:" + cls] += 1
                    continue
        sub = (r["_typ"].lower() if r["_path"] == "strict" else "l_" + r["_sub"])
        x = {k: v for k, v in r.items() if not k.startswith("_")}
        x["rule"] = "below:sc9_%s_%s" % (cls, sub)
        x["table"] = "history"
        x["claim"] = claim
        x["note"] = (x.get("note") or "") + "; scdb9 " + cls + ((" " + r["_j9"]) if r.get("_j9") else "") + \
            ((" a9:" + r["_a9"]) if r.get("_a9") else "")
        st["kept:" + cls] += 1
        st["kept:%s/%s" % (x["kind"], x["scope"])] += 1
        out.append(x)
        remove.extend(rem)
    with open(os.path.join(HERE, "rows9.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "remove9.txt"), "w", encoding="utf-8", newline=NL) as f:
        for i in sorted(set(remove)):
            f.write(i + NL)
    st["rows"] = len(out)
    st["remove_ids"] = len(set(remove))
    json.dump(st, open(os.path.join(WORK, "select9_stats.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
