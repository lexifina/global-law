"""Run scan.py over every repo, at most N at a time, largest first; finished repos are skipped (resumable).

    python launch.py run_scan.py [N=12]
"""
import glob, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK  # noqa: E402


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    here = os.path.dirname(os.path.abspath(__file__))
    repos = []
    for f in glob.glob(os.path.join(WORK, "nodes", "*.tsv")):
        r = os.path.basename(f)[:-4]
        if not os.path.exists(os.path.join(WORK, "cand", r + ".jsonl.gz")):
            repos.append((os.path.getsize(f), r))
    repos.sort(reverse=True)
    todo = [r for _, r in repos]
    running = {}
    t0 = time.time()
    print(time.strftime("%H:%M:%S"), "repos to scan:", len(todo), flush=True)
    while todo or running:
        while todo and len(running) < n:
            r = todo.pop(0)
            log = open(os.path.join(WORK, "logs", "scan-" + r + ".log"), "wb")
            running[r] = (subprocess.Popen([sys.executable, "-X", "utf8", "-u", os.path.join(here, "scan.py"), r],
                                           stdout=log, stderr=subprocess.STDOUT, cwd=here, creationflags=0x08000000),
                          log)
        time.sleep(3)
        for r in list(running):
            p, log = running[r]
            if p.poll() is not None:
                log.close()
                print(time.strftime("%H:%M:%S"), r, "exit", p.returncode, f"{time.time() - t0:.0f}s", flush=True)
                del running[r]
    print(time.strftime("%H:%M:%S"), "ALLDONE", flush=True)


if __name__ == "__main__":
    main()
