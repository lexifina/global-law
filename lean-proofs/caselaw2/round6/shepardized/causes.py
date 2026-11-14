#!/usr/bin/env python3
"""Mechanical bucket for EVERY case where Shepardized shows NEG or PART and the model shows no same-case negative.

This is a rule-based sorting of all such cases (not a reading); the 40 + 26 cases read by hand validate it
(SHEPARDIZED.md). Usage: python -I causes.py [--tag asof20101119]

Buckets
  Supreme Court sub-classes (sc_reversed, sc_vacated, sc_part):
    sc_cites_target        a later Supreme Court decision in the corpus cites the target's reporter citation, shares a
                           party name with it, and its text has a reversing/vacating word
    sc_cites_target_no_edge  as sc_in_corpus_no_cite below, but the text does cite the target in a form the citation
                           graph did not link (e.g. "70 F. (2d) 956")
    sc_in_corpus_no_cite   no such decision, but a Supreme Court decision within 4 years with a matching name (token
                           overlap >= 0.5), a reversing/vacating word, and no conflicting "C. A. <n> Cir." label does
                           not cite the target (typically a memorandum order)
    coa_mentions_only      neither; a later decision of the same circuit cites the target with a shared party name
                           (e.g. the order on remand)
    nothing_found          no later same-case decision found in the corpus
  Court of appeals sub-classes (panel_withdrawn, enbanc_different):
    coa_cites_target       a later decision of the same circuit (within 4 years) cites the target, shares a party name
    coa_in_corpus_no_cite  a later decision of the same circuit within 3 years with a matching name does not cite it
    nothing_found
Output: results/<tag>/causes.tsv (one line per case) and causes_summary.tsv.
"""
import argparse
import collections
import csv
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH = os.path.join(HERE, "..", "..", "..", "graph")
REPOS = os.path.join(os.path.expanduser("~"), "Documents", "us-caselaw-repos")
STOP = set("""v vs the of and in re ex parte rel et al inc co corp corporation company ltd united states america state
people commonwealth city county board commissioner commission national association assn dept department for
matter estate administrator secretary director general attorney labor relations internal revenue insurance bank
railroad railway""".split())
ORD = {"1": "1st", "2": "2d", "3": "3d", "4": "4th", "5": "5th", "6": "6th", "7": "7th", "8": "8th", "9": "9th",
       "10": "10th", "11": "11th", "0": "D. C."}
NEGW = re.compile(r"revers|vacat|set aside", re.I)
CAW = re.compile(r"C\. ?A\. ?(D\. ?C\.|\d+(?:st|d|nd|rd|th))\s*Cir", re.I)


def toks(name):
    return {t for t in re.findall(r"[a-z]{3,}", name.lower()) if t not in STOP}


class Texts:
    def __init__(self):
        self.p = {}

    def get(self, repo, path):
        pr = self.p.get(repo)
        if pr is None:
            pr = subprocess.Popen(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            self.p[repo] = pr
        pr.stdin.write(("HEAD:" + path + "\n").encode("utf-8"))
        pr.stdin.flush()
        head = pr.stdout.readline().split()
        if len(head) < 3 or head[1] != b"blob":
            return ""
        n = int(head[2])
        b = pr.stdout.read(n)
        pr.stdout.read(1)
        t = b.decode("utf-8", "replace").replace("\r\n", "\n")
        i = t.find("\n---", 3)
        return t[i + 4:] if t.startswith("---") and i > 0 else t

    def close(self):
        for pr in self.p.values():
            pr.stdin.close()
            pr.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="asof20101119")
    a = ap.parse_args()
    res = os.path.join(HERE, "results", a.tag)
    cases = [c for c in csv.DictReader(open(os.path.join(res, "cases.tsv"), encoding="utf-8", newline=""),
                                       delimiter="\t", quoting=csv.QUOTE_NONE)
             if c["node"] and c["sclass"] in ("NEG", "PART") and c["mclass"] != "NEG_HIST"]
    citers = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(res, "citers.tsv"), encoding="utf-8", newline=""), delimiter="\t",
                            quoting=csv.QUOTE_NONE):
        citers[r["casenum"]].append(r)
    need = {c["node"] for c in cases}
    for c in cases:
        need.update(r["citing"] for r in citers[c["casenum"]])
    meta = {}
    byname = collections.defaultdict(list)  # (repo, year) -> nodes
    with open(os.path.join(GRAPH, "nodes.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            if p[0] in need:
                meta[p[0]] = p
            if p[1] == "supreme-court" or (p[1].startswith("ca") and "-" not in p[1]):
                byname[(p[1], p[4][:4])].append(p)
    tx = Texts()
    rows = []
    for c in cases:
        tm = meta[c["node"]]
        tt = toks(tm[6])
        y0 = int(tm[4][:4])
        vol, ser, pg = re.match(r"(\d+) f(2d|3d) (\d+)", c["cite"]).groups()
        citre = re.compile(r"%s\s*F\.\s*(?:\(%s\)|%s)\s*%s\b" % (vol, ser, ser, pg))
        sc_sub = "sc_" in c["ssub"]
        later = [r for r in citers[c["casenum"]] if r["same_case_guess"] == "1" and int(r["date"][:4]) - y0 <= 8]
        bucket, ev = "nothing_found", ""
        if sc_sub:
            hit = None
            for r in later:
                if r["repo"] == "supreme-court":
                    m = meta[r["citing"]]
                    x = tx.get(m[1], m[2])
                    if citre.search(x) and NEGW.search(x):
                        hit = m
                        break
            if hit:
                bucket, ev = "sc_cites_target", "%s (%s)" % (hit[5].split("|")[0], hit[0])
            else:
                found = None
                for y in range(y0, y0 + 5):
                    for p in byname.get(("supreme-court", str(y)), []):
                        if p[4] < tm[4]:
                            continue
                        pt = toks(p[6])
                        sh = tt & pt
                        if not sh or len(sh) / len(tt | pt) < 0.5:
                            continue
                        x = tx.get(p[1], p[2])
                        if not NEGW.search(x):
                            continue
                        ca = CAW.search(x)
                        if ca:
                            lab = re.sub(r"\s+", " ", ca.group(1)).replace("D.C.", "D. C.").lower()
                            want = ORD[c["circuit"]].lower()
                            if lab.replace("nd", "d").replace("rd", "d") != want:
                                continue
                        found = p
                        break
                    if found:
                        break
                if found:
                    # the text may cite the target in a form the citation graph did not link (e.g. "70 F. (2d) 956")
                    b = "sc_cites_target_no_edge" if citre.search(tx.get(found[1], found[2])) else "sc_in_corpus_no_cite"
                    bucket, ev = b, "%s (%s)" % (found[5].split("|")[0], found[0])
                elif any(r["repo"] != "supreme-court" for r in later):
                    r = next(r for r in later if r["repo"] != "supreme-court")
                    bucket, ev = "coa_mentions_only", "%s (%s)" % (r["cite"], r["citing"])
        else:
            same = [r for r in later if r["repo"] != "supreme-court" and int(r["date"][:4]) - y0 <= 4]
            if same:
                bucket, ev = "coa_cites_target", "%s (%s)" % (same[0]["cite"], same[0]["citing"])
            else:
                found = None
                for y in range(y0, y0 + 4):
                    for p in byname.get((tm[1], str(y)), []):
                        if p[4] < tm[4] or p[0] == c["node"]:
                            continue
                        pt = toks(p[6])
                        sh = tt & pt
                        if sh and len(sh) / len(tt | pt) >= 0.5:
                            found = p
                            break
                    if found:
                        break
                if found:
                    bucket, ev = "coa_in_corpus_no_cite", "%s (%s)" % (found[5].split("|")[0], found[0])
        rows.append((c["casenum"], c["cite"], c["node"], c["sclass"], c["ssub"], bucket, ev))
    tx.close()
    with open(os.path.join(res, "causes.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("casenum\tcite\tnode\tsclass\tssub\tbucket\tevidence\n")
        for r in rows:
            o.write("\t".join(r) + "\n")
    cnt = collections.Counter((r[3], "supreme_court" if "sc_" in r[4] else "court_of_appeals", r[5]) for r in rows)
    with open(os.path.join(res, "causes_summary.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("sclass\tlevel\tbucket\tcases\n")
        for k, v in sorted(cnt.items()):
            o.write("%s\t%s\t%s\t%d\n" % (k + (v,)))
            print("%s\t%s\t%s\t%d" % (k + (v,)))
    print("total", len(rows))


if __name__ == "__main__":
    main()
