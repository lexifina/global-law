"""Run scan.py over every repo, up to N in parallel; resumable (a repo whose out/<repo>.tsv exists is skipped).

    python run_scan.py <work-dir> [procs=10]            (foreground: the pool itself)
    python run_scan.py --detach <work-dir> [procs=10]   (start the pool detached, no console window, and return)

<work-dir>/in/<repo>.tsv come from prep_inputs.py; outputs go to <work-dir>/out/<repo>.tsv, the log to
<work-dir>/logs/scan.log (one line per repo with its throughput, plus totals).
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
FLAGS = 0x08000000 | 0x00000200 | 0x01000000 | 0x00004000  # no window | new group | breakaway | below normal


def detach(wd, procs):
    log = open(os.path.join(wd, "logs", "launcher.out"), "ab")
    p = subprocess.Popen([sys.executable, os.path.abspath(__file__), wd, str(procs)], stdout=log, stderr=log,
                         stdin=subprocess.DEVNULL, creationflags=FLAGS if os.name == "nt" else 0, close_fds=True)
    print("detached pid", p.pid)


def main(wd, procs):
    os.makedirs(os.path.join(wd, "out"), exist_ok=True)
    os.makedirs(os.path.join(wd, "logs"), exist_ok=True)
    log = open(os.path.join(wd, "logs", "scan.log"), "a", encoding="utf-8", newline="\n")
    with open(os.path.join(wd, "logs", "pool.pid"), "w") as f:
        f.write(str(os.getpid()))
    todo = []
    for fn in os.listdir(os.path.join(wd, "in")):
        repo = fn[:-4]
        if os.path.exists(os.path.join(wd, "out", repo + ".tsv")):
            continue
        todo.append((os.path.getsize(os.path.join(wd, "in", fn)), repo))
    todo.sort(reverse=True)
    t0 = time.time()
    log.write("%s start: %d repos to do, %d procs\n" % (time.strftime("%H:%M:%S"), len(todo), procs))
    log.flush()
    running = {}
    done = 0
    while todo or running:
        while todo and len(running) < procs:
            _, repo = todo.pop(0)
            errf = open(os.path.join(wd, "logs", repo + ".err"), "wb")
            p = subprocess.Popen([sys.executable, os.path.join(HERE, "scan.py"), repo, os.path.join(wd, "in", repo + ".tsv"),
                                  os.path.join(wd, "out", repo + ".tsv")], stdout=subprocess.PIPE, stderr=errf,
                                 stdin=subprocess.DEVNULL, creationflags=0x08000000 | 0x00004000 if os.name == "nt" else 0)
            running[repo] = (p, errf)
        time.sleep(2)
        for repo in list(running):
            p, errf = running[repo]
            if p.poll() is not None:
                line = p.stdout.read().decode("utf-8", "replace").strip()
                errf.close()
                done += 1
                log.write("%s %s rc=%d %s\n" % (time.strftime("%H:%M:%S"), repo, p.returncode, line))
                log.flush()
                del running[repo]
    log.write("%s all done: %d repos in %.0f s\n" % (time.strftime("%H:%M:%S"), done, time.time() - t0))
    log.close()


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--detach":
        detach(a[1], int(a[2]) if len(a) > 2 else 10)
    else:
        main(a[0], int(a[1]) if len(a) > 1 else 10)
