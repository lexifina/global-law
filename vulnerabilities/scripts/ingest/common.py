"""Shared paths and a low-priority, windowless git runner. Read-only over law repos."""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
CORPUS = SOURCES / "corpus"
GLOBAL = SOURCES / "global-law.git"
INDEX = ROOT / "index"
FINDINGS = ROOT / "findings"
PINS = ROOT / "pins.json"
GLOBAL_LIVE = Path(os.environ.get("GLOBAL_LAW", Path.home() / "Documents" / "global-law"))  # a global-law clone (optional)
CACHE_LIVE = GLOBAL_LIVE / ".git" / "corpus-cache"
WORKERS = int(os.environ.get("LE_WORKERS", str(max(1, (os.cpu_count() or 4) // 2))))

IDLE = os.environ.get("LE_PRIORITY", "").lower() == "idle"   # use only spare cycles on a shared machine
GIT_GREP_THREADS = os.environ.get("LE_GREP_THREADS", "4")
DUCKDB_THREADS = int(os.environ.get("LE_DUCKDB_THREADS", "0"))   # cap DuckDB on a shared machine (0 = DuckDB default)
if DUCKDB_THREADS:
    import duckdb as _duckdb
    _connect = _duckdb.connect

    def _capped_connect(*a, **k):
        con = _connect(*a, **k)
        con.execute(f"set threads to {DUCKDB_THREADS}")
        return con
    _duckdb.connect = _capped_connect
    _duckdb.execute(f"set threads to {DUCKDB_THREADS}")   # the default connection behind duckdb.sql()
FLAGS = 0
if sys.platform == "win32":
    FLAGS = (0x00000040 if IDLE else 0x00004000) | 0x08000000  # IDLE or BELOW_NORMAL_PRIORITY_CLASS | CREATE_NO_WINDOW


def lower_priority() -> None:
    try:
        import psutil
        me = psutil.Process()
        if sys.platform == "win32":
            me.nice(psutil.IDLE_PRIORITY_CLASS if IDLE else psutil.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            me.nice(19 if IDLE else 10)
        aff = os.environ.get("LE_CPU_AFFINITY")  # e.g. "12-23" to share a machine
        if aff:
            a, b = (int(x) for x in aff.split("-"))
            me.cpu_affinity(list(range(a, b + 1)))
    except Exception:
        pass


def git(*args: str, cwd: Path | None = None, binary: bool = False, check: bool = True):
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, creationflags=FLAGS)
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(args[:3])} failed in {cwd}: {p.stderr.decode(errors='replace')[:400]}")
    return p.stdout if binary else p.stdout.decode("utf-8", errors="replace")


def pins() -> dict:
    return json.loads(PINS.read_text(encoding="utf-8"))
