"""Exercise score_fresh7.py's --split test code path WITHOUT the sealed key.

GOLD is redirected to a fake folder (check/fake_gold) whose sealed/test.tsv is a copy of the DEV key and whose
work/scotus_meta.tsv is a copy of the real one. Nothing under round5/gold_fresh/sealed/ is read or written.
Checks: one TEST_RUNS.log line per run, results in <fake>/sealed/results/<label>.fresh7.*, no moves file,
--out refused for test, and the outcome tables equal the dev run's (same key rows).

    python check/fake_test_path.py <status.tsv> <treatments.tsv> <dev results dir of the same status>
"""
import importlib.util
import io
import json
import os
import shutil
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
status, treatments, devdir = sys.argv[1:4]
fake = os.path.join(HERE, "fake_gold")
shutil.rmtree(fake, ignore_errors=True)
os.makedirs(os.path.join(fake, "sealed"))
os.makedirs(os.path.join(fake, "work"))
shutil.copy(os.path.join(C2, "round5", "gold_fresh", "dev", "dev.tsv"), os.path.join(fake, "sealed", "test.tsv"))
shutil.copy(os.path.join(C2, "round5", "gold_fresh", "work", "scotus_meta.tsv"), os.path.join(fake, "work"))

spec = importlib.util.spec_from_file_location("sf7", os.path.join(C2, "round7", "score_fresh7.py"))
sf7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sf7)
assert sf7.GOLD.endswith(os.path.join("round5", "gold_fresh"))
sf7.GOLD = fake

for i in range(2):
    buf = io.StringIO()
    with redirect_stdout(buf):
        sf7.main(["--split", "test", "--status", status, "--treatments", treatments, "--label", "fake%d" % i])
log = open(os.path.join(fake, "sealed", "TEST_RUNS.log"), encoding="utf-8").read().splitlines()
print("TEST_RUNS.log lines:", len(log))
for line in log:
    print("  ", line[:60], "...", line.split("\t")[-1], "| fields:", len(line.split("\t")))
print("sealed/results:", sorted(os.listdir(os.path.join(fake, "sealed", "results"))))
try:
    sf7.main(["--split", "test", "--status", status, "--label", "x", "--out", HERE])
    print("--out with test: NOT refused")
except SystemExit as e:
    print("--out with test refused:", e)
t = json.load(open(os.path.join(fake, "sealed", "results", "fake0.fresh7.json"), encoding="utf-8"))
d = json.load(open(os.path.join(devdir, "fresh7_dev.json"), encoding="utf-8"))
for v in ("model", "attributed"):
    print(v, "recall equal to the dev run:", t["views"][v]["recall"] == d["views"][v]["recall"])
print("moves recorded:", t["moves"], "| stdout has no pair ids:", "F" not in "".join(
    l.split()[0] for l in buf.getvalue().splitlines() if l[:1] == "F"))
shutil.rmtree(fake)
