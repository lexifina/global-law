"""Lead: update the live page for round 9.

    python -X utf8 round9/lead/live9.py --state Running --note "..." [--progress FILE.html] [--section FILE.html]

--progress FILE  replaces the block between <!--r9progress--> and <!--/r9progress--> (appended before the closing
                 "Running." paragraph the first time) in round5/report/sections/97_round9.html
--section FILE   replaces the whole section file
Then edits the Round 9 entry of round5/report/processes.json atomically (temp file + os.replace) and rebuilds
round5/report/make_overturned.py.
"""
import argparse
import json
import os
import subprocess
import sys

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEC = os.path.join(C2, "round5", "report", "sections", "97_round9.html")
PJ = os.path.join(C2, "round5", "report", "processes.json")


def atomic_write(path, text):
    tmp = path + ".tmp_r9"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--note", required=True)
    ap.add_argument("--progress")
    ap.add_argument("--section")
    a = ap.parse_args()
    if a.section:
        atomic_write(SEC, open(a.section, encoding="utf-8").read())
    elif a.progress:
        s = open(SEC, encoding="utf-8").read()
        block = "<!--r9progress-->\n" + open(a.progress, encoding="utf-8").read().strip() + "\n<!--/r9progress-->"
        if "<!--r9progress-->" in s:
            i = s.index("<!--r9progress-->")
            j = s.index("<!--/r9progress-->") + len("<!--/r9progress-->")
            s = s[:i] + block + s[j:]
        else:
            k = s.rfind("<p>Running.")
            s = (s[:k] + block + "\n" + s[k:]) if k >= 0 else (s.rstrip("\n") + "\n" + block + "\n")
        atomic_write(SEC, s)
    d = json.load(open(PJ, encoding="utf-8"))
    n = 0
    for x in d:
        if x.get("work", "").startswith("Round 9"):
            x["state"] = a.state
            x["note"] = a.note
            n += 1
    if n != 1:
        sys.exit("expected one Round 9 entry, found %d" % n)
    atomic_write(PJ, json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    r = subprocess.run([sys.executable, "-X", "utf8", os.path.join(C2, "round5", "report", "make_overturned.py")],
                       cwd=C2, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout[-400:], r.stderr[-400:], "rc", r.returncode)


if __name__ == "__main__":
    main()
