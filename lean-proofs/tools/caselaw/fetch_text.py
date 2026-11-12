"""Write the text of decisions (by node id) to files, for the audits.

    python tools/caselaw/fetch_text.py <graph-dir> <repos-dir> <out-dir> <id> [<id> ...]

Each decision is written as <out-dir>/<id>.md (the decision file as held in global-law: front matter and opinions).
"""
import os, subprocess, sys


def main(g, repos, out, ids):
    os.makedirs(out, exist_ok=True)
    want = {int(i) for i in ids}
    for line in open(os.path.join(g, "nodes.tsv"), encoding="utf-8"):
        f = line.split("\t", 3)
        n = int(f[0])
        if n in want:
            r = subprocess.run(["git", "-C", os.path.join(repos, f[1]), "show", "HEAD:" + f[2]], capture_output=True)
            open(os.path.join(out, f"{n}.md"), "wb").write(r.stdout)
            want.discard(n)
            if not want:
                break


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
