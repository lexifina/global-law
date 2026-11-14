"""Lead: update the live page for round 12 (agent infra12; = round11/lead/live11.py for round 12).

    python -X utf8 round12/lead/live12.py --state Running --note "..." [--progress FILE.html] [--section FILE.html]
    python -X utf8 round12/lead/live12.py --add --state Running --note "..."    (once: append the Round 12 entry)

--progress FILE  replaces the block between <!--r12progress--> and <!--/r12progress--> (inserted before the closing
                 "Running." paragraph the first time) in round5/report/sections/99b_round12.html
--section FILE   replaces the whole section file
Then edits the Round 12 entry of round5/report/processes.json atomically (temp file + os.replace; json indent 2,
ensure_ascii, trailing LF = the file's own format, so every other entry stays byte for byte) and rebuilds
round5/report/make_overturned.py.
"""
import argparse
import json
import os
import subprocess
import sys

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEC = os.path.join(C2, "round5", "report", "sections", "99b_round12.html")
PJ = os.path.join(C2, "round5", "report", "processes.json")
WORK = ("Round 12: Shadow Docket order nodes, en banc vacatur of the court's own panel, Federal Circuit district / "
        "other-target reviews, Brace & Hall third tie")


def atomic_write(path, text):
    tmp = path + ".tmp_r12"
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
    ap.add_argument("--add", action="store_true", help="append the Round 12 entry (refused if one exists)")
    ap.add_argument("--no-build", action="store_true", help="do not rebuild the page")
    a = ap.parse_args()
    if a.section:
        atomic_write(SEC, open(a.section, encoding="utf-8").read())
    elif a.progress:
        s = open(SEC, encoding="utf-8").read()
        block = "<!--r12progress-->\n" + open(a.progress, encoding="utf-8").read().strip() + "\n<!--/r12progress-->"
        if "<!--r12progress-->" in s:
            i = s.index("<!--r12progress-->")
            j = s.index("<!--/r12progress-->") + len("<!--/r12progress-->")
            s = s[:i] + block + s[j:]
        else:
            k = s.rfind("<p>Running.")
            s = (s[:k] + block + "\n" + s[k:]) if k >= 0 else (s.rstrip("\n") + "\n" + block + "\n")
        atomic_write(SEC, s)
    raw = open(PJ, "rb").read().decode("utf-8")
    d = json.loads(raw)
    if dump(d) != raw:
        sys.exit("processes.json is not in the json.dumps(indent=2, ensure_ascii) form: not rewritten")
    hits = [x for x in d if x.get("work", "").startswith("Round 12")]
    if a.add:
        if hits:
            sys.exit("a Round 12 entry exists already")
        d.append({"work": WORK, "state": a.state, "note": a.note})
    else:
        if len(hits) != 1:
            sys.exit("expected one Round 12 entry, found %d (use --add once)" % len(hits))
        hits[0]["state"] = a.state
        hits[0]["note"] = a.note
    new = dump(d)
    if a.add:
        assert new.startswith(raw[:raw.rstrip().rstrip("]").rstrip().rfind("}") + 1]), "earlier entries changed"
    atomic_write(PJ, new)
    print("processes.json: Round 12 entry %s (%s)" % ("added" if a.add else "updated", a.state))
    if a.no_build:
        return
    r = subprocess.run([sys.executable, "-X", "utf8", os.path.join(C2, "round5", "report", "make_overturned.py")],
                       cwd=C2, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout[-400:], r.stderr[-400:], "rc", r.returncode)


if __name__ == "__main__":
    main()
