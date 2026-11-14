"""Lead: update the live page for round 10 (agent infra10; = round9/lead/live9.py for round 10).

    python -X utf8 round10/lead/live10.py --state Running --note "..." [--progress FILE.html] [--section FILE.html]
    python -X utf8 round10/lead/live10.py --add --state Running --note "..."    (once: append the Round 10 entry)

--progress FILE  replaces the block between <!--r10progress--> and <!--/r10progress--> (inserted before the closing
                 "Running." paragraph the first time) in round5/report/sections/98_round10.html
--section FILE   replaces the whole section file
Then edits the Round 10 entry of round5/report/processes.json atomically (temp file + os.replace; json indent 2,
ensure_ascii, trailing LF = the file's own format, so every other entry stays byte for byte) and rebuilds
round5/report/make_overturned.py.
"""
import argparse
import json
import os
import subprocess
import sys

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEC = os.path.join(C2, "round5", "report", "sections", "98_round10.html")
PJ = os.path.join(C2, "round5", "report", "processes.json")
WORK = ("Round 10: syllabus re-cuts, a state-court review linker, FJC named-other-case, SCDB bare citations, "
        "Shadow Docket remand bridge in Lean, one new held-out key")


def atomic_write(path, text):
    tmp = path + ".tmp_r10"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def dump(d):
    return json.dumps(d, indent=2, ensure_ascii=True) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--note", required=True)
    ap.add_argument("--progress")
    ap.add_argument("--section")
    ap.add_argument("--add", action="store_true", help="append the Round 10 entry (refused if one exists)")
    ap.add_argument("--no-build", action="store_true", help="do not rebuild the page")
    a = ap.parse_args()
    if a.section:
        atomic_write(SEC, open(a.section, encoding="utf-8").read())
    elif a.progress:
        s = open(SEC, encoding="utf-8").read()
        block = "<!--r10progress-->\n" + open(a.progress, encoding="utf-8").read().strip() + "\n<!--/r10progress-->"
        if "<!--r10progress-->" in s:
            i = s.index("<!--r10progress-->")
            j = s.index("<!--/r10progress-->") + len("<!--/r10progress-->")
            s = s[:i] + block + s[j:]
        else:
            k = s.rfind("<p>Running.")
            s = (s[:k] + block + "\n" + s[k:]) if k >= 0 else (s.rstrip("\n") + "\n" + block + "\n")
        atomic_write(SEC, s)
    raw = open(PJ, "rb").read().decode("utf-8")
    d = json.loads(raw)
    if dump(d) != raw:
        sys.exit("processes.json is not in the json.dumps(indent=2, ensure_ascii) form: not rewritten")
    hits = [x for x in d if x.get("work", "").startswith("Round 10")]
    if a.add:
        if hits:
            sys.exit("a Round 10 entry exists already")
        d.append({"work": WORK, "state": a.state, "note": a.note})
    else:
        if len(hits) != 1:
            sys.exit("expected one Round 10 entry, found %d (use --add once)" % len(hits))
        hits[0]["state"] = a.state
        hits[0]["note"] = a.note
    new = dump(d)
    if a.add:
        assert new.startswith(raw[:raw.rstrip().rstrip("]").rstrip().rfind("}") + 1]), "earlier entries changed"
    atomic_write(PJ, new)
    print("processes.json: Round 10 entry %s (%s)" % ("added" if a.add else "updated", a.state))
    if a.no_build:
        return
    r = subprocess.run([sys.executable, "-X", "utf8", os.path.join(C2, "round5", "report", "make_overturned.py")],
                       cwd=C2, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout[-400:], r.stderr[-400:], "rc", r.returncode)


if __name__ == "__main__":
    main()
