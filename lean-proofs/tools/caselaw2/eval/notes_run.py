"""Run notes_extract.py over every US case-law repo, at most 8 at a time, detached and without a window.

    python tools/caselaw2/eval/notes_run.py start   # launches the driver detached and returns
    python tools/caselaw2/eval/notes_run.py drive   # the driver itself (resumes: skips repos already done)

Output: caselaw-lean-2/gold/work/notes/<repo>.notes.tsv; log: caselaw-lean-2/gold/work/notes_run.log.
"""
import os, subprocess, sys, time

FLAGS = 0x08000000 | 0x00000200 | 0x01000000 | 0x00004000  # no window, new group, breakaway, below normal
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/gold/work")
OUT = os.path.join(WORK, "notes")
HERE = os.path.dirname(os.path.abspath(__file__))
MAXP = 8


def repos():
    out = []
    for n in os.listdir(REPOS):
        d = os.path.join(REPOS, n)
        if os.path.isdir(d) and (os.path.isfile(os.path.join(d, "HEAD")) or os.path.isdir(os.path.join(d, ".git"))):
            size = 0
            pk = os.path.join(d, "objects", "pack")
            if os.path.isdir(pk):
                size = sum(os.path.getsize(os.path.join(pk, f)) for f in os.listdir(pk))
            out.append((size, n))
    return [n for _, n in sorted(out, reverse=True)]


def drive():
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(WORK, "notes_run.log"), "a", encoding="utf-8", newline="\n")
    todo = [n for n in repos() if not os.path.exists(os.path.join(OUT, n + ".notes.tsv"))]
    log.write(f"{time.strftime('%H:%M:%S')} start pid={os.getpid()} todo={len(todo)}\n"); log.flush()
    running = {}
    while todo or running:
        while todo and len(running) < MAXP:
            n = todo.pop(0)
            err = open(os.path.join(OUT, n + ".err"), "w")
            running[n] = subprocess.Popen([sys.executable, "-X", "utf8", os.path.join(HERE, "notes_extract.py"),
                                           os.path.join(REPOS, n), OUT], stdout=log, stderr=err, creationflags=FLAGS)
        time.sleep(2)
        for n, p in list(running.items()):
            if p.poll() is not None:
                log.write(f"{time.strftime('%H:%M:%S')} done {n} rc={p.returncode}\n"); log.flush()
                del running[n]
    log.write(f"{time.strftime('%H:%M:%S')} ALLDONE\n"); log.close()


if __name__ == "__main__":
    if sys.argv[1] == "start":
        p = subprocess.Popen([sys.executable, "-X", "utf8", os.path.abspath(__file__), "drive"], creationflags=FLAGS,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("driver pid", p.pid)
    else:
        drive()
