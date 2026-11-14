#!/usr/bin/env python3
"""Fetch the Supreme Court's own docket record (JSON) for every docket number carried by a corpus Supreme Court
node dated on or after the cutoff.

    python -I fetch_dockets.py [--from 20210101] [--sleep 1.0]

Docket numbers come from the round-6 cache metadata (round6/history/cache/supreme-court*.meta.tsv.gz, docket
column); nothing else of the corpus and no model output is read. Each record is saved as
src_scdocket/json/<docket>.json (bytes as served) and one line per request is appended to
src_scdocket/manifest.tsv: docket, url, UTC time, HTTP status, bytes, sha1. Already fetched dockets are skipped
(resumable). Generic client name, no personal details.
"""
import argparse
import datetime
import glob
import gzip
import hashlib
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(C2, "round6", "history", "cache")
OUT = os.path.join(HERE, "src_scdocket")
URL = "https://www.supremecourt.gov/RSS/Cases/JSON/%s.json"
UA = "research-client/1.0"
DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")


def dockets(cut):
    out = set()
    for p in sorted(glob.glob(os.path.join(CACHE, "supreme-court*.meta.tsv.gz"))):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                q = line.rstrip("\n").split("\t")
                if q[4] != "2906" or q[3] < cut:
                    continue
                for m in re.finditer(r"(?<!\d)(\d{2})\s*-\s*(\d{1,5})(?!\d)", q[5].translate(DASHES)):
                    out.add("%s-%d" % (m.group(1), int(m.group(2))))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="cut", default="20210101")
    ap.add_argument("--sleep", type=float, default=1.0)
    a = ap.parse_args()
    os.makedirs(os.path.join(OUT, "json"), exist_ok=True)
    man = os.path.join(OUT, "manifest.tsv")
    done = set()
    if os.path.exists(man):
        with open(man, encoding="utf-8") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 4 and p[3] in ("200", "404"):
                    done.add(p[0])
    ds = [d for d in dockets(a.cut) if d not in done]
    sys.stderr.write("%d dockets to fetch\n" % len(ds))
    for i, d in enumerate(ds):
        url = URL % d
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        status, body = 0, b""
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                status, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:  # network error: logged, retried on the next run
            status = -1
            sys.stderr.write("%s: %s\n" % (d, e))
        if status == 200:
            with open(os.path.join(OUT, "json", d + ".json"), "wb") as o:
                o.write(body)
        with open(man, "a", encoding="utf-8", newline="\n") as o:
            o.write("%s\t%s\t%s\t%d\t%d\t%s\n" % (d, url, datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"), status, len(body), hashlib.sha1(body).hexdigest() if body else "-"))
        if (i + 1) % 50 == 0:
            sys.stderr.write("%d/%d\n" % (i + 1, len(ds)))
        time.sleep(a.sleep)


if __name__ == "__main__":
    main()
