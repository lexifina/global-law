"""Full run of the vulnerability pipeline on a shared machine, as one detached process: mirrors, index, every detector.
Each stage runs under the environment caps below; a disk guard suspends the running stage while C: is under the floor.

python run_deep.py RUN [--from STAGE]      -> findings/RUN/run.log, findings/RUN/stages.json
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
ENV = {**os.environ, "LE_PRIORITY": "idle", "LE_WORKERS": "6", "LE_GREP_THREADS": "2", "LE_DUCKDB_THREADS": "2",
       "PYTHONUTF8": "1", "GLOBAL_LAW": str(Path.home() / "Documents" / "global-law"),
       "GLOBAL_LAW_ORIGIN": "https://github.com/lexifina/global-law"}
ENV.pop("LE_CPU_AFFINITY", None)
FLOOR_GB, RESUME_GB = 50, 52


def stages(run):
    d = lambda name, *a: (name, [PY, f"detectors/{name}.py", run, *a])
    return [
        ("sync", [PY, "ingest/sync.py"]),
        ("extract", [PY, "ingest/extract.py"]), ("trailers", [PY, "ingest/trailers.py"]),
        ("textscan", [PY, "ingest/textscan.py"]), ("refscan", [PY, "ingest/refscan.py"]),
        ("refscan_czechia", [PY, "ingest/refscan.py", "--fileact", "czechia-law"]), ("headings", [PY, "ingest/headings.py"]),
        d("trailer_only"), d("rank"), d("text_detectors"), d("ref_detectors"), d("placeholder_ref"), d("late_extension"),
        d("owi_de"), d("dead_fine"), d("subref_de"), d("notes_scan"), d("currency_scan"), d("dup_labels"), d("es_crossref"),
    ]


def free_gb():
    return shutil.disk_usage("C:\\").free / 1e9


def main():
    run = sys.argv[1]
    start = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else None
    out = ROOT / "findings" / run; out.mkdir(parents=True, exist_ok=True)
    log = (out / "run.log").open("a", encoding="utf-8")
    state_f = out / "stages.json"
    state = json.loads(state_f.read_text(encoding="utf-8")) if state_f.exists() else {}

    def say(msg):
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n"); log.flush()
    import psutil
    started = start is None
    for name, cmd in stages(run):
        if not started:
            started = name == start
            if not started:
                continue
        if state.get(name, {}).get("rc") == 0 and start is None:
            continue
        while free_gb() < FLOOR_GB:
            say(f"waiting: C: has {free_gb():.0f} GB free, floor {FLOOR_GB}"); time.sleep(120)
        say(f"start {name}: {' '.join(cmd[1:])}  (C: {free_gb():.0f} GB free)")
        t0 = time.time()
        p = subprocess.Popen(cmd, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT,
                             creationflags=(0x00000040 | 0x08000000) if os.name == "nt" else 0)
        proc = psutil.Process(p.pid); paused = False
        while p.poll() is None:
            time.sleep(60)
            g = free_gb()
            try:
                kids = [proc] + proc.children(recursive=True)
                if g < FLOOR_GB and not paused:
                    for k in kids: k.suspend()
                    paused = True; say(f"paused {name}: C: {g:.0f} GB free")
                elif paused and g >= RESUME_GB:
                    for k in kids: k.resume()
                    paused = False; say(f"resumed {name}: C: {g:.0f} GB free")
            except psutil.Error:
                pass
        state[name] = {"rc": p.returncode, "minutes": round((time.time() - t0) / 60, 1), "free_gb": round(free_gb())}
        state_f.write_text(json.dumps(state, indent=1), encoding="utf-8")
        say(f"end {name}: rc {p.returncode}, {state[name]['minutes']} min")
        if p.returncode != 0 and name in ("sync", "extract"):
            say("stopping: later stages need this one"); break
    say("run finished")


if __name__ == "__main__":
    main()
