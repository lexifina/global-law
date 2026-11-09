"""dead_fine: a penalty provision (a fine, an offence, an administrative infraction) whose trigger points at a provision of
the same act that is repealed (only a placeholder is left) or deleted. A penalty needs an existing statutory basis, so the
dead part of the provision cannot be enforced. Every corpus, any language; generalises owi_de.py (Germany only).

python detectors/dead_fine.py RUN [--repos germany-law,malta-law] [--acts germany-law:awaffv,eigv]
  -> findings/RUN/dead_fine.jsonl

The core, scan_act(files, deleted), takes {path: text} for one act and the keys of its deleted provisions, so tests can
drive it without a corpus.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FINDINGS, CORPUS, FLAGS, INDEX, WORKERS, pins, lower_priority
from refscan import refs, path_key, act_of, is_external, before_ref
from placeholder_ref import is_placeholder, EXTERNAL

# A provision is a penalty provision if it creates an offence or a fine. Cues are whole phrases, not single words such as
# 'penalty' or 'Strafe', which also appear in procedure, sentencing and tax-surcharge rules.
PENAL_CUE = re.compile(r"(?i)("
    # German / Austrian / Swiss
    r"ordnungswidrig\s+(?:im\s+sinne\s+\S+(?:\s+\S+){0,8}?\s+)?handelt|ordnungswidrigkeiten|bußgeldvorschrift|bussgeldvorschrift|"
    r"wird\s+mit\s+(?:freiheitsstrafe|geldstrafe|geldbuße|geldbusse|busse|buße)|mit\s+(?:busse|buße)\s+(?:bis\s+zu\s+[\d.' ]+\s+franken\s+)?wird\s+bestraft|"
    r"verwaltungsübertretung|strafbestimmung|strafvorschrift|"
    # English
    r"commits?\s+an\s+offen[cs]e|(?:is|shall\s+be)\s+guilty\s+of\s+(?:an?\s+|the\s+)?(?:offen[cs]e|misdemeanou?r|felony|crime)|"
    r"liable\s+on\s+(?:summary\s+)?conviction|(?:shall\s+be|is|are)\s+liable\s+(?:on\s+\w+\s+conviction\s+)?to\s+(?:a\s+fine|"
    r"imprisonment|a\s+term\s+of|a\s+penalty\s+(?:of|not)|punishment|both)|shall\s+be\s+(?:punished|punishable)|is\s+punishable\s+by|"
    r"commits?\s+(?:the\s+(?:crime|offen[cs]e)\s+of|a\s+crime\b)|power\s+to\s+punish|"
    r"ska\s+(?:\S+\s+){0,3}?dömas|den\s+dömas|uloží\s+pokutu|za\s+priestupok|přestup(?:ek|ku)\s+se\s+dopustí|"
    r"civil\s+penalty\s+(?:of|provision)|administrative\s+(?:fine|penalty)\s+of|offen[cs]e\s+and\s+punishment|in\s+contempt\s+of\s+court|"
    # Spanish
    r"constituyen?\s+infracci|son\s+infracciones|se\s+(?:sancionar[áa]n?|castigar[áa]n?)|ser[áa]n?\s+sancionad|infracci[oó]n\s+(?:muy\s+)?(?:grave|leve)|"
    r"multa\s+de\s+[\d.]+|ser[áa]n?\s+castigad|incurrir[áa]n?\s+en\s+(?:la\s+)?(?:multa|sanci)|ser[áa]n?\s+reprimid|"
    r"se\s+(?:le\s+)?impondr[áa]n?\s+(?:\w+\s+){0,6}?(?:prisi[oó]n|multa|pena|sanci)|se\s+prohíbe\s+y\s+sanciona|"
    # Portuguese
    r"incorrer[ãa]o?\s+(?:na|em)\s+multa|(?:é|será|serão)\s+punid|constitui\s+(?:infração|contraordenação)|sujeit[oa]s?\s+(?:a|à)\s+multa|"
    r"\bpena\s*[-–—:]\s*(?:reclus[ãa]o|deten[çc][ãa]o|multa|pris[ãa]o|pagamento)|"
    # French / Italian
    r"(?:est|sera)\s+puni|(?:sont|seront)\s+punis|(?:est|sont)\s+passibles?\s+d'une\s+amende|constitue\s+une\s+(?:infraction|contravention)|"
    r"interdit\s+et\s+puni|sanctions?\s+administratives?|sous\s+peine\s+de|"
    r"(?:è|sono)\s+punit|sanzione\s+amministrativa\s+pecuniaria|"
    # Dutch / Nordic / Baltic
    r"wordt\s+gestraft|straffes\s+med|bøde\s+idømmes|straffes\s+(?:den|med)|döms\s+(?:\S+\s+){0,8}?till\s+(?:böter|fängelse)|"
    r"dömes\s+till\s+(?:böter|fängelse)|tuomitaan\s+(?:\S+\s+){0,6}?sakkoon|karistatakse\s+(?:rahatrahvi|aresti|vangistus|rahalise)|"
    r"baudžiam|sodu\s+līdz|"
    # Turkish / Slavic / Greek / Azerbaijani / Russian / Bulgarian / Ukrainian
    r"cezalandırılır|para\s+cezası|kažnjava\s+se|kaznuje\s+se|se\s+trestá|pokutou\s+do|τιμωρείται|ένοχος\s+(?:\S+\s+)?αδικήματος|"
    r"διοικητικ\w+\s+κυρώσ\w+|επιβάλλεται\s+πρόστιμο|cərimə|cəzalandırılır|наказывается|штраф\w*\s+в\s+размере|се\s+наказва|"
    r"наказва\w*\s+с|карається|"
    # Arabic / Thai / Japanese / Chinese
    r"يعاقب|يُعاقب|بغرامة|ต้องระวางโทษ|"
    r"(?:罰金|拘禁刑|懲役|禁錮|科料|過料)に処する|罰金刑を科する|處[^。；]{0,40}?(?:罰金|罰鍰|徒刑|拘役)|处[^。；]{0,40}?(?:罚款|罚金|徒刑|拘役))")
# A reference is a trigger when it says what was breached: 'contrary to § 12', 'contravenes section 47', 'el artículo 15'.
TRIGGER = re.compile(r"(?i)(entgegen|zuwiderhandelt|verstößt|verletzt|contrary\s+to|contravenes?|in\s+contravention\s+of|"
                     r"fails?\s+to\s+comply\s+with|in\s+breach\s+of|under|en\s+violaci[oó]n|incumpl\w*|vulnera\w*|"
                     r"contrairement|en\s+violation|méconna\w*|em\s+viola[çc][ãa]o|infringi\w*|descumpri\w*|in\s+violazione|"
                     r"in\s+strijd\s+met|i\s+strid\s+med|aykırı|suprotno|v\s+rozporu|nach|gemäß|des\s+artikels|du\s+présent|"
                     r"previst[oa]s?\s+(?:no|na|en|in)|dispuesto\s+en|disposto\s+n)")


FAMILY = [  # numbering units; a reference in one family cannot mean a provision numbered in another
    ("para", re.compile(r"(?i)§§?\s*$")),
    ("art", re.compile(r"(?i)(?<![A-Za-zÀ-ÿ])(?:art\.?|arts\.|artikel\w*|article\w*|artículo\w*|articulo\w*|artigo\w*|articol\w*|άρθρ\w*|"
                       r"madde\w*|član\w*|člen\w*|članak|статья\w*|стаття\w*|maddə\w*)\s*$")),
    ("sec", re.compile(r"(?i)(?<![A-Za-zÀ-ÿ])(?:section\w*|sec\.|ss?\.|regulation\w*|reg\.|rule\w*|r\.)\s*$")),
]
# a reference to the act's earlier version is deliberate (transitional rules)
OLD_VERSION = re.compile(r"(?i)geltenden\s+fassung|in\s+der\s+fassung|in\s+the\s+version|as\s+in\s+force\s+(?:before|on)|"
                         r"redacci[oó]n\s+(?:anterior|vigente|dada)|na\s+reda[çc][ãa]o|dans\s+sa\s+r[ée]daction|nella\s+formulazione")
# 'section 57 under the Tax Administration Act 2009', 'article 12 of the Companies Act'
OTHER_ACT_TAIL = re.compile(r"^[\s\w(),.\-]{0,20}?\b(?:of|under|in)\s+(?:the\s+)?(?:[A-Z][\w\-’']+\s+){1,7}"
                            r"(?:Act|Code|Ordinance|Decree|Regulations?|Law|Rules)\b")


def _before(ctx: str, tail: str) -> str:
    """the text just before the reference's number. refs() gives ctx = 120 chars either side and tail = the 70 chars after
    the match, so the match ends where the tail starts; ctx.split(key) would cut at the key's first occurrence ('1831/2003')."""
    t = re.sub(r"\s+", " ", tail)[:40]
    end = ctx.rfind(t) if t.strip() else len(ctx)
    if end < 0:
        end = len(ctx)
    return re.sub(r"\d[\d.]*[\s\-]?(?:[A-Za-z]{1,2}|bis|ter|quater)?\s*$", "", ctx[:end])


def _family(before: str) -> str | None:
    tail = before[-30:]
    for name, rx in FAMILY:
        if rx.search(tail):
            return name
    return None


def _act_family(files: dict[str, str]) -> str | None:
    counts: dict[str, int] = {}
    for t in files.values():
        head = t.lstrip("# \n").split("\n", 1)[0][:20]
        for name, rx in FAMILY:
            m = re.match(r"(?i)\s*(§|(?:art|artikel|article|artículo|artigo|articolo|άρθρο|madde|section|sec|regulation|rule)\b|s\.)", head)
            if m:
                w = m.group(1).lower()
                fam = "para" if w == "§" else "sec" if w in ("section", "sec", "s.", "regulation", "rule") else "art"
                counts[fam] = counts.get(fam, 0) + 1
                break
    return max(counts, key=counts.get) if counts else None


def is_penal(text: str) -> bool:
    return bool(PENAL_CUE.search(text))


def scan_act(files: dict[str, str], deleted: set[str] | frozenset = frozenset()) -> list[dict]:
    """files: {path: text} of one act; deleted: keys of provisions that existed and were removed.
    Returns one flag per (penalty provision, dead reference)."""
    act_fam = _act_family(files)
    status = {}
    for p, t in files.items():
        k = path_key(p)
        if k:
            status[k] = ("placeholder", p) if is_placeholder(t) else ("live", p)
    out, seen = [], set()
    for path, t in files.items():
        own = path_key(path)
        if not own or status.get(own, ("",))[0] == "placeholder" or not is_penal(t):
            continue
        # refs() skips the first line as a heading; corpora without heading lines (Brazil: 'Art. 347 - ...') keep the
        # provision's opening sentence there, so give them an empty heading.
        for k, ctx, tail in refs(t):
            if k == own:
                continue
            before = before_ref(ctx, tail)
            if EXTERNAL.match(tail) or is_external(before, tail) or OTHER_ACT_TAIL.match(tail) or OLD_VERSION.search(ctx):
                continue
            fam = _family(before)
            if fam and act_fam and fam != act_fam:
                continue
            st = status.get(k)
            if st and st[0] == "placeholder":
                kind, target = "repealed (placeholder)", st[1]
            elif not st and k in deleted:
                kind, target = "deleted", None
            else:
                continue
            if (path, k) in seen:
                continue
            seen.add((path, k))
            num = re.escape(re.match(r"\d+", k).group(0))
            line = next((l for l in t.splitlines() if not l.startswith("#") and re.search(rf"(?<![\d.]){num}(?![\d])", l)), "")
            trig = bool(TRIGGER.search(before[-80:]))
            out.append({"path": path, "ref": k, "target": target, "target_status": kind, "trigger": trig,
                        "score": round(0.6 + (0.25 if trig else 0) + (0.15 if kind.startswith("repealed") else 0.05), 2),
                        "context": ctx, "line": line.strip()[:500]})
    return out


def _corpus_texts(c, only_acts: set[str] | None):
    repo = CORPUS / f"{c['repo']}.git"
    ls = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "-z", "--format=%(objectname) %(path)", c["sha"]],
                        capture_output=True, creationflags=FLAGS).stdout.decode("utf-8", "replace").split("\0")
    files = {}
    for x in ls:
        if x and x.endswith(".md"):
            sha, path = x.split(" ", 1)
            if only_acts and act_of(path) not in only_acts:
                continue
            files[path] = sha
    if not files:
        return {}
    p = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"], input=("\n".join(files.values()) + "\n").encode(),
                       capture_output=True, creationflags=FLAGS).stdout
    text, pos = {}, 0
    for path in files:
        nl = p.index(b"\n", pos); hdr = p[pos:nl].split()
        if len(hdr) < 3 or hdr[1] != b"blob":
            pos = nl + 1; continue
        size = int(hdr[2]); text[path] = p[nl + 1: nl + 1 + size].decode("utf-8", "replace"); pos = nl + 2 + size
    return text


def _deleted_keys(c) -> dict[str, set[str]]:
    """act -> keys whose last change in the history is a deletion (needs the index; empty without it)."""
    f = INDEX / "changes" / f"{c['repo']}.parquet"
    if not f.exists():
        return {}
    import duckdb
    rows = duckdb.sql(f"""select path from (select path, arg_max(left(status,1), rowid) last from (
                            select *, row_number() over () rowid from '{f.as_posix()}') group by path) where last = 'D'""").fetchall()
    out: dict[str, set[str]] = {}
    for (p,) in rows:
        k = path_key(p)
        if k:
            out.setdefault(act_of(p), set()).add(k)
    return out


def scan_corpus(c, only_acts: set[str] | None = None) -> list[dict]:
    lower_priority()
    text = _corpus_texts(c, only_acts)
    deleted = _deleted_keys(c)
    acts: dict[str, dict[str, str]] = {}
    for p, t in text.items():
        acts.setdefault(act_of(p), {})[p] = t
    out = []
    for a, files in acts.items():
        live = {path_key(p) for p in files if path_key(p)}
        for r in scan_act(files, frozenset(deleted.get(a, set()) - live)):
            out.append({"corpus": c["path"], "repo": c["repo"], **r})
    return out


def main() -> None:
    lower_priority()
    ap = argparse.ArgumentParser(); ap.add_argument("run")
    ap.add_argument("--repos", default=""); ap.add_argument("--acts", default="", help="repo:act1,act2;repo2:act3")
    a = ap.parse_args()
    only: dict[str, set[str]] = {}
    for part in filter(None, a.acts.split(";")):
        repo, acts = part.split(":", 1); only[repo] = set(acts.split(","))
    want = set(filter(None, a.repos.split(","))) | set(only)
    cs = [c for c in pins()["corpora"] if not c["repo"].startswith(("united-kingdom", "romania"))
          and (not want or c["repo"] in want) and (CORPUS / f"{c['repo']}.git").exists()]
    (FINDINGS / a.run).mkdir(parents=True, exist_ok=True)

    def safe(c):
        try:
            return scan_corpus(c, only.get(c["repo"]))
        except Exception as e:
            print(f"error in {c['repo']}: {type(e).__name__}: {e}", flush=True); return []
    n = 0
    with ThreadPoolExecutor(min(WORKERS, 6)) as ex, (FINDINGS / a.run / "dead_fine.jsonl").open("w", encoding="utf-8") as fh:
        for rows in ex.map(safe, cs):
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
    print("dead_fine", n)


if __name__ == "__main__":
    main()
