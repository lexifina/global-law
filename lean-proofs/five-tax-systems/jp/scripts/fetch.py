"""Polite fetcher for official pages (NTA, MOF, kyoukaikenpo, nenkin, cfa, soumu).
usage: python3 -I fetch.py <url> <outfile>            save raw bytes
       python3 -I fetch.py --text <file.htm>          print visible text of a saved HTML page
       python3 -I fetch.py --links <file.htm> [regex] list links (absolute) whose href or text matches
Each network fetch sleeps 1.5 s afterwards (sequential, >= 1 s apart)."""
import sys, time, re, urllib.request, urllib.parse
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; tax-formalisation-research/1.0)"


class TextP(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []
        self.skip = 0
        self.links = []
        self.cur = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "br", "tr", "li", "h1", "h2", "h3", "h4", "div", "table", "dt", "dd"):
            self.out.append("\n")
        if tag in ("td", "th"):
            self.out.append(" | ")
        if tag == "a":
            self.cur = [dict(attrs).get("href", ""), ""]

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        if tag == "a" and self.cur is not None:
            self.links.append(tuple(self.cur))
            self.cur = None

    def handle_data(self, data):
        if self.skip:
            return
        self.out.append(data)
        if self.cur is not None:
            self.cur[1] += data.strip()


def decode(b):
    for enc in ("utf-8", "cp932", "euc-jp"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass
    return b.decode("utf-8", "replace")


if sys.argv[1] == "--text":
    p = TextP()
    p.feed(decode(open(sys.argv[2], "rb").read()))
    t = "".join(p.out)
    t = re.sub(r"[ \t\r　]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    print(t)
elif sys.argv[1] == "--links":
    base = sys.argv[3] if len(sys.argv) > 4 else None
    rx = re.compile(sys.argv[3]) if len(sys.argv) > 3 else None
    p = TextP()
    p.feed(decode(open(sys.argv[2], "rb").read()))
    for href, txt in p.links:
        if rx is None or rx.search(href) or rx.search(txt):
            print(href, "\t", txt[:80])
else:
    url, out = sys.argv[1], sys.argv[2]
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    open(out, "wb").write(data)
    print(r.status, len(data), url)
    time.sleep(1.5)
