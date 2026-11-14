#!/usr/bin/env python3
"""Nodes that a builder of rounds 5-7 has seen: every 6-7 digit number in the names or contents of the working
files people and sub-agents read (briefs, notes, logs, audit packs and texts, diagnosis texts and lists, reading
packs and answers, decoy pools, the fresh-key dev half).

    python -I seen_nodes.py > work/seen_nodes.txt      (one node id per line; stats to stderr)

Scanned: under round5/, round6/, round7/ (not round7/heldout/) and the reader/cue folders of the Lean tools,
  * every .md / .txt file of at most 5 MB, and
  * every file of at most 5 MB whose path has a part named like audit*, diag*, *pack*, ans*, *brief*, dev,
    texts, store, *decoy*,
  except linker row files (rows*.jsonl), certificate deltas (*_delta.tsv) and bulk files naming more than BULK
  distinct numbers, which are model output or feed lists nobody read row by row. Sealed key folders
  (round5/gold_fresh/sealed, round6/history/split) are never walked. A key entry whose order node or lower node
  is in this set is dropped from the time-split key; the set is generous (any 6-7 digit number counts).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOTS = [os.path.join(C2, "round5"), os.path.join(C2, "round6"), os.path.join(C2, "round7"),
         os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/reader"),
         os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues")]
SKIP_DIRS = {"stage", "out", "cache", "__pycache__", ".git"}
SEEN_DIR = re.compile(r"(?:^|/)(?:audit[^/]*|diag[^/]*|[^/]*pack[^/]*|ans[^/]*|[^/]*brief[^/]*|dev|texts|store|"
                      r"[^/]*decoy[^/]*)(?:/|$)", re.I)
NUM = re.compile(r"(?<![0-9.])\d{6,7}(?![0-9])")
LIMIT = 5 * 1024 * 1024
# a file naming more than BULK distinct numbers is a bulk table (feed lists, snapshots of model tables), not
# something a person or sub-agent read row by row; it is left out and listed on stderr
BULK = 5000
# answer keys this agent must never open (DESIGN7 0.3): not walked at all
NEVER = re.compile(r"(?:^|/)(?:gold_fresh/sealed|history/split)(?:/|$)")


def main():
    seen = set()
    bulk = []
    nfiles = 0
    me = os.path.normcase(HERE)
    for root in ROOTS:
        for dp, dns, fns in os.walk(root):
            if os.path.normcase(dp).startswith(me):
                dns[:] = []
                continue
            rel = os.path.relpath(dp, C2).replace("\\", "/")
            if NEVER.search(rel):
                dns[:] = []
                continue
            dns[:] = [d for d in dns if d not in SKIP_DIRS and not NEVER.search(rel + "/" + d)]
            for fn in fns:
                if re.match(r"rows.*\.jsonl$", fn) or fn.endswith("_delta.tsv"):
                    continue
                p = os.path.join(dp, fn)
                ext = os.path.splitext(fn)[1].lower()
                if not (ext in (".md", ".txt") or SEEN_DIR.search(rel + "/" + fn)):
                    continue
                try:
                    if os.path.getsize(p) > LIMIT:
                        continue
                    with open(p, encoding="utf-8", errors="replace") as f:
                        s = f.read()
                except OSError:
                    continue
                nfiles += 1
                found = set(NUM.findall(fn)) | set(NUM.findall(s))
                if len(found) > BULK:
                    bulk.append((len(found), os.path.relpath(p, C2).replace("\\", "/")))
                    continue
                seen.update(found)
    for n in sorted(seen, key=int):
        print(n)
    sys.stderr.write("files scanned %d, distinct 6-7 digit numbers %d; bulk files left out %d\n" %
                     (nfiles, len(seen), len(bulk)))
    for c, p in sorted(bulk, reverse=True)[:40]:
        sys.stderr.write("  bulk %d %s\n" % (c, p))


if __name__ == "__main__":
    main()
