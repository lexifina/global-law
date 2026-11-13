"""Frozen-reader main run (detached via launch.py): wait for the scan, resolve every repo, classify with
gpt-5.4-mini, re-read the hard subset with gpt-6.1-sol, certify into caselaw-lean-2/data/.

    python launch.py run_main.py
Each step is resumable; rerunning skips finished work.
"""
import glob, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PY = [sys.executable, "-X", "utf8", "-u"]


def step(args):
    print(time.strftime("%H:%M:%S"), "RUN", " ".join(args), flush=True)
    r = subprocess.run(PY + [os.path.join(HERE, args[0])] + args[1:], cwd=HERE, creationflags=0x08000000)
    print(time.strftime("%H:%M:%S"), "EXIT", r.returncode, args[0], flush=True)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def main():
    log = os.path.join(WORK, "logs", "run_scan.log")
    while "ALLDONE" not in open(log, encoding="utf-8").read():
        time.sleep(30)
    n_nodes = len(glob.glob(os.path.join(WORK, "nodes", "*.tsv")))
    n_cand = len(glob.glob(os.path.join(WORK, "cand", "*.jsonl.gz")))
    print(time.strftime("%H:%M:%S"), "scan done", n_cand, "of", n_nodes, "repos", flush=True)
    step(["resolve.py"])
    step(["classify.py", "--stage", "main", "--tpm", "550000", "--conc", "48"])
    step(["hard.py", "llm/main.gpt-5.4-mini.jsonl", os.path.join(WORK, "hard_ids.tsv"), "20000"])
    step(["classify.py", "--stage", "hard", "--model", "gpt-6.1-sol", "--ids", os.path.join(WORK, "hard_ids.tsv"),
          "--tpm", "300000", "--conc", "24", "--batch", "4"])
    step(["certify.py", "--results", "llm/main.gpt-5.4-mini.jsonl", "--override", "llm/hard.gpt-6.1-sol.jsonl"])
    print(time.strftime("%H:%M:%S"), "MAIN ALLDONE", flush=True)


if __name__ == "__main__":
    main()
