"""The statute layer: every decision's US Code citations (the judgment overlay of each case-law repo), with the
version of each section in force on the day decided, and every later change to that section.

    python tools/caselaw/statutes.py <repos-dir> <usc-law-git> <out-dir>

Writes overlay.tsv (repo, decision path, decided, section path, law_commit or '', law_record_from) and
section_versions.tsv (section path, commit, in-force date) for every section cited, from the US Code record.
"""
import glob, json, os, re, subprocess, sys


def main(repos, usc, out):
    os.makedirs(out, exist_ok=True)
    secs = set()
    with open(os.path.join(out, "overlay.tsv"), "w", encoding="utf-8", newline="\n") as fo:
        for d in sorted(glob.glob(os.path.join(repos, "*", ".git"))):
            repo = os.path.dirname(d)
            name = os.path.basename(repo)
            tree = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "HEAD", "--", "judgments"], capture_output=True).stdout.decode()
            for line in tree.splitlines():
                meta, path = line.split("\t", 1)
                sha = meta.split()[2]
                sec = re.sub(r"^judgments/united-states/federal/usc/", "", path)[:-len(".jsonl")] + ".md"
                data = subprocess.run(["git", "-C", repo, "cat-file", "-p", sha], capture_output=True).stdout.decode("utf-8", "replace")
                for row in data.splitlines():
                    try:
                        r = json.loads(row)
                    except Exception:
                        continue
                    fo.write(f"{name}\t{r.get('decision','')}\t{r.get('decided','')}\t{sec}\t{r.get('law_commit','')}\t{r.get('law_record_from','')}\n")
                    secs.add(sec)
            print(name, flush=True)
    with open(os.path.join(out, "section_versions.tsv"), "w", encoding="utf-8", newline="\n") as fv:
        for sec in sorted(secs):
            log = subprocess.run(["git", "-C", usc, "log", "--format=%H%x09%(trailers:key=In-force,valueonly,separator=)", "HEAD", "--", sec],
                                 capture_output=True).stdout.decode("utf-8", "replace")
            for l in log.splitlines():
                h, _, d = l.partition("\t")
                fv.write(f"{sec}\t{h}\t{d.strip()}\n")
    print("sections", len(secs))


if __name__ == "__main__":
    main(*sys.argv[1:])
