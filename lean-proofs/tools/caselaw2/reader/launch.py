"""Start a reader job detached, with no console window.

    python launch.py <script.py> [args...]

The job's stdout/stderr go to data/reader_work/logs/<script>.log; its PID is written next to it.
"""
import os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK  # noqa: E402

FLAGS = 0x08000000 | 0x00000200 | 0x01000000 | 0x00004000  # no window | new group | breakaway | below normal


def main():
    script = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    logs = os.path.join(WORK, "logs")
    os.makedirs(logs, exist_ok=True)
    tag = os.path.splitext(os.path.basename(script))[0]
    log = open(os.path.join(logs, tag + ".log"), "ab")
    p = subprocess.Popen([sys.executable, "-X", "utf8", "-u", os.path.join(here, script)] + sys.argv[2:],
                         stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=here,
                         creationflags=FLAGS, close_fds=True)
    with open(os.path.join(logs, tag + ".pid"), "w", encoding="utf-8", newline="\n") as f:
        f.write(str(p.pid) + "\n")
    print(tag, "pid", p.pid)


if __name__ == "__main__":
    main()
