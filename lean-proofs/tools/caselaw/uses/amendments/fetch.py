"""Cached, paced fetches from GovInfo / congress.gov.

Cache: uses/amendments/cache/<sha256(url)[:24]>.{bin,json}. The US Code history build keeps a cache with the same key
scheme (lexifina/src/backend/.us_code_history/cache); a hit there is copied (read-only) into ours, so nothing is fetched
twice and the other session's files are never written.
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
CACHE = HERE / "cache"
SHARED = Path.home() / "Documents/lexifina/src/backend/.us_code_history/cache"
UA = "Mozilla/5.0 (compatible; research crawler; amendment-instruction check)"
_last = [0.0]


def _key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]


def _bad(url: str, data: bytes) -> bool:
    head = data[:8000].lower()
    return (b"<title>error" in head or b"page not found" in head
            or (url.endswith(".xml") and (not data.lstrip().startswith(b"<") or b"<html" in head)))


def fetch(url: str, *, pause: float = 1.2, offline: bool = False):
    """Bytes of the file, or None if the publisher has none. Misses are cached too (as a .json with missing=true)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    k = _key(url)
    body, meta = CACHE / f"{k}.bin", CACHE / f"{k}.json"
    if meta.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        if m.get("missing"):
            return None
        return body.read_bytes()
    sb, sm = SHARED / f"{k}.bin", SHARED / f"{k}.json"
    if sb.exists() and sm.exists():
        data = sb.read_bytes()
        if not _bad(url, data):
            body.write_bytes(data)
            m = json.loads(sm.read_text(encoding="utf-8"))
            m["copied_from"] = "us_code_history cache"
            meta.write_text(json.dumps(m), encoding="utf-8", newline="\n")
            return data
    if offline:
        return None
    for attempt in range(3):
        wait = pause - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                data = b""
                break
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(10 + 20 * attempt)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 + 10 * attempt)
    else:
        return None
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not data or _bad(url, data):
        meta.write_text(json.dumps({"url": url, "missing": True, "fetched_at": now}), encoding="utf-8", newline="\n")
        return None
    body.write_bytes(data)
    meta.write_text(json.dumps({"url": url, "sha256": hashlib.sha256(data).hexdigest(), "fetched_at": now}),
                    encoding="utf-8", newline="\n")
    return data


def plaw_uslm(c: int, n: int) -> str:
    return f"https://www.govinfo.gov/content/pkg/PLAW-{c}publ{n}/uslm/PLAW-{c}publ{n}.xml"


def plaw_mods(c: int, n: int) -> str:
    return f"https://www.govinfo.gov/metadata/pkg/PLAW-{c}publ{n}/mods.xml"


def bill_xml(c: int, kind: str, num: str, version: str) -> str:
    p = f"BILLS-{c}{kind.lower()}{num}{version}"
    return f"https://www.govinfo.gov/content/pkg/{p}/xml/{p}.xml"
