"""Freeze the five calculators for one complete run: copy each exe once (waiting while a build relinks it),
record its hash, and print the folder. `final_run.sh` exports it as CMP_FROZEN so every analysis of the run uses the
same five binaries.

    python3 freeze.py  -> prints runs/frozen/<stamp>
"""
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.pop("CMP_FROZEN", None)
from common import COUNTRIES, EXES, ROOT, sha256  # noqa: E402


def stable_copy(src, dst, tries=40, wait=15):
    """Copy `src` once it exists and its size and mtime have not changed for `wait` seconds."""
    for _ in range(tries):
        if os.path.exists(src):
            s1 = os.stat(src)
            time.sleep(wait)
            if os.path.exists(src):
                s2 = os.stat(src)
                if (s1.st_size, s1.st_mtime) == (s2.st_size, s2.st_mtime) and s2.st_size > 0:
                    shutil.copy2(src, dst)
                    return True
        else:
            time.sleep(wait)
    return False


def main():
    stamp = time.strftime("%Y%m%dT%H%M%S")
    d = os.path.join(ROOT, "runs", "frozen", stamp)
    os.makedirs(d, exist_ok=True)
    info = {}
    for c in COUNTRIES:
        cmd, cwd = EXES[c]
        dst = os.path.join(d, f"{c.lower()}_" + os.path.basename(cmd[0]))
        ok = stable_copy(cmd[0], dst)
        info[c] = {"source": cmd[0], "cmd": [dst] + cmd[1:], "cwd": cwd, "ok": ok,
                   "sha256": sha256(dst) if ok else None,
                   "source_mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.stat(cmd[0]).st_mtime)) if os.path.exists(cmd[0]) else None}
    json.dump(info, open(os.path.join(d, "frozen.json"), "w"), indent=1)
    print(d)


if __name__ == "__main__":
    main()
