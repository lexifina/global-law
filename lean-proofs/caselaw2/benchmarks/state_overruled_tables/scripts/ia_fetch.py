"""Polite Internet Archive fetcher (stdlib only).

    python -I ia_fetch.py meta <outdir> <id> [<id> ...]     -> <outdir>/<id>.json (metadata API), summary on stdout
    python -I ia_fetch.py djvu <rawdir> <id> [<id> ...]     -> <rawdir>/<id>/<id>_djvu.txt (new empty folder each)

Pacing: 3 s between requests; no login, no cookies; stops on any non-200 answer for that item.
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

UA = "caselaw-benchmark-research/1.0 (public-domain text layer fetch)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, r.read()


def meta(outdir, ids):
    os.makedirs(outdir, exist_ok=True)
    for i in ids:
        try:
            st, b = get("https://archive.org/metadata/%s" % i)
        except Exception as e:  # noqa
            print(i, "ERR", e)
            time.sleep(3)
            continue
        with open(os.path.join(outdir, i + ".json"), "wb") as f:
            f.write(b)
        d = json.loads(b.decode("utf-8"))
        m = d.get("metadata", {})
        files = d.get("files", [])
        dj = [f for f in files if f.get("name", "").endswith("_djvu.txt")]
        print("\t".join([i, str(m.get("title", ""))[:90], str(m.get("date", "")), str(m.get("imagecount", "")),
                         ";".join("%s:%s" % (f["name"], f.get("size")) for f in dj) or "NO_DJVU",
                         str(m.get("possible-copyright-status", "")), str(d.get("is_dark", ""))]))
        time.sleep(3)


def djvu(rawdir, ids):
    for i in ids:
        d = os.path.join(rawdir, i)
        if os.path.exists(d) and os.listdir(d):
            print(i, "exists, skipped")
            continue
        os.makedirs(d, exist_ok=True)
        url = "https://archive.org/download/%s/%s_djvu.txt" % (i, i)
        try:
            st, b = get(url)
        except Exception as e:  # noqa
            print(i, "ERR", e)
            time.sleep(3)
            continue
        p = os.path.join(d, i + "_djvu.txt")
        with open(p, "wb") as f:
            f.write(b)
        print("\t".join([i, url, str(len(b)), hashlib.sha256(b).hexdigest(),
                         time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())]))
        time.sleep(3)


def djvuxml(rawdir, ids):
    """<rawdir>/<id>_xml/<id>_djvu.xml (its own new empty folder)."""
    for i in ids:
        d = os.path.join(rawdir, i + "_xml")
        if os.path.exists(d) and os.listdir(d):
            print(i, "exists, skipped")
            continue
        os.makedirs(d, exist_ok=True)
        url = "https://archive.org/download/%s/%s_djvu.xml" % (i, i)
        try:
            st, b = get(url)
        except Exception as e:  # noqa
            print(i, "ERR", e)
            time.sleep(3)
            continue
        p = os.path.join(d, i + "_djvu.xml")
        with open(p, "wb") as f:
            f.write(b)
        print("\t".join([i, url, str(len(b)), hashlib.sha256(b).hexdigest(),
                         time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())]))
        time.sleep(3)


if __name__ == "__main__":
    cmd, out, ids = sys.argv[1], sys.argv[2], sys.argv[3:]
    {"meta": meta, "djvu": djvu, "xml": djvuxml}[cmd](out, ids)
