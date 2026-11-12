"""Every version of every section in the US Code record (united-states-law, all titles), from its git history.

    python tools/caselaw/usc_versions.py <united-states-law git dir> <out.tsv>

One row per (section file, commit that touched it), oldest first:
  path, commit, kind (law | edition), law ("Pub. L. 104-317" or the edition's name), in force (yyyymmdd), blob ('' if
  the commit removed the file), short title of the law
A commit is a law's when its author is a public law ("Pub. L. ..."); every other commit (an edition's text no law
accounts for, the start of a title's record, a corrections commit) is an edition's. The day is the In-force trailer,
else the author date (the record's convention: author date = the day in force).
"""
import re, subprocess, sys

SEC = re.compile(r"^title-\d+[A-Za-z]?/[^/]+\.md$")


def main(git, out):
    fmt = "@@%H%x09%an%x09%ad%x09%(trailers:key=In-force,valueonly,separator=;)"
    p = subprocess.Popen(["git", "--git-dir", git, "log", "--reverse", "--date=short", "--no-abbrev", "--raw", "--no-renames",
                          f"--format={fmt}", "main"], stdout=subprocess.PIPE)
    n = 0
    cur = None
    with open(out, "w", encoding="utf-8", newline="\n") as fo:
        for raw in p.stdout:
            line = raw.decode("utf-8", "replace").rstrip("\n")
            if line.startswith("@@"):
                h, author, ad, inforce = (line[2:].split("\t") + ["", "", ""])[:4]
                day = (inforce.split(";")[0].strip() or ad)[:10].replace("-", "")
                law = author.split(" (")[0] if author.startswith("Pub. L.") else author
                short = author[len(law):].strip(" ()") if author.startswith("Pub. L.") else ""
                cur = (h, "law" if author.startswith("Pub. L.") else "edition", law, day, short)
                continue
            if not line.startswith(":") or cur is None:
                continue
            meta, path = line.split("\t", 1)
            if not SEC.match(path):
                continue
            parts = meta.split()
            blob, status = parts[3], parts[4]
            if status == "D":
                blob = ""
            h, kind, law, day, short = cur
            fo.write(f"{path}\t{h}\t{kind}\t{law}\t{day}\t{blob}\t{short}\n")
            n += 1
    p.wait()
    print("section versions", n)


if __name__ == "__main__":
    main(*sys.argv[1:])
