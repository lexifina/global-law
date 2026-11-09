"""Scan text once per corpus (current files at the pin + every amended version's before/after).

index/dates/<repo>.parquet           "until <date>" style limits in current text
index/amounts/<repo>.parquet         money / percentage amounts in current text
index/amount_changes/<repo>.parquet  amounts removed/added by each law amendment (M changes)
"""
from __future__ import annotations
import re, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import duckdb, pyarrow as pa, pyarrow.parquet as pq
from common import CORPUS, FLAGS, INDEX, WORKERS, git, lower_priority, pins

MONTHS = ("january february march april may june july august september october november december "
          "janvier février mars avril mai juin juillet août septembre octobre novembre décembre "
          "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre "
          "januar februar märz april mai juni juli august september oktober november dezember "
          "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro "
          "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre "
          "januari februari mars april maj juni juli augusti september oktober november december "
          "januari februari maart april mei juni juli augustus september oktober november december "
          "januar februar marts april maj juni juli august september oktober november december "
          "januar februar mars april mai juni juli august september oktober november desember "
          "stycznia lutego marca kwietnia maja czerwca lipca sierpnia września października listopada grudnia "
          "ledna února března dubna května června července srpna září října listopadu prosince "
          "januára februára marca apríla mája júna júla augusta septembra októbra novembra decembra "
          "ianuarie februarie martie aprilie mai iunie iulie august septembrie octombrie noiembrie decembrie "
          "janar shkurt mars prill maj qershor korrik gusht shtator tetor nëntor dhjetor "
          "ocak şubat mart nisan mayıs haziran temmuz ağustos eylül ekim kasım aralık "
          "januarja februarja marca aprila maja junija julija avgusta septembra oktobra novembra decembra "
          "siječnja veljače ožujka travnja svibnja lipnja srpnja kolovoza rujna listopada studenoga prosinca "
          "jaanuar veebruar märts aprill mai juuni juuli august september oktoober november detsember "
          "tammikuuta helmikuuta maaliskuuta huhtikuuta toukokuuta kesäkuuta heinäkuuta elokuuta syyskuuta lokakuuta marraskuuta joulukuuta "
          "ιανουαρίου φεβρουαρίου μαρτίου απριλίου μαΐου ιουνίου ιουλίου αυγούστου σεπτεμβρίου οκτωβρίου νοεμβρίου δεκεμβρίου "
          "января февраля марта апреля мая июня июля августа сентября октября ноября декабря").split()
MI: dict[str, int] = {}
for _i in range(0, len(MONTHS), 12):
    for _n, _m in enumerate(MONTHS[_i:_i + 12], 1):
        MI.setdefault(_m, _n)
MI["setiembre"] = 9
MON = "|".join(sorted(map(re.escape, MI), key=len, reverse=True))
DATE = (rf"(?P<d1>\d{{1,2}})\.?\s*(?:de\s+)?(?P<mon>{MON})\s*(?:de\s+)?(?P<y1>\d{{4}})"
        rf"|(?P<mon2>{MON})\s+(?P<d2>\d{{1,2}}),?\s+(?P<y2>\d{{4}})"
        r"|(?P<d3>\d{1,2})[./](?P<m3>\d{1,2})[./](?P<y3>\d{4})"
        r"|(?P<y4>\d{4})-(?P<m4>\d{2})-(?P<d4>\d{2})"
        r"|(?P<m5>\d{1,2})-(?P<d5>\d{1,2})-(?P<y5>\d{4})")
DEADLINE = r"not later than|no later than|spätestens|au plus tard|a más tardar|uiterlijk|senest|senast|najpóźniej|nejpozději"
UNTIL = (r"until the end of|until|till|up to and including|not later than|no later than|expires? on|expired|in force until|valid until|"
         r"cease[sd]? to (?:be effective|be operative|have effect|apply)(?: after| on)?|(?:becomes?|shall become) inoperative on|"
         r"(?:is|are) repealed (?:as of|on)|upphör att gälla u:|upphör att gälla den|mbaron më|përfundon në datën|përfundon më|"
         r"deri më|deri në|până la|până pe|fino a|sino al|tot|til og med|t\.o\.m\.|kuni|iki|līdz|έως|μέχρι|do|ending on|"
         r"ceases? to have effect on|bis zum|befristet bis|außer kraft am|bis|jusqu'au|jusqu’au|jusqu'à|jusqu’à|"
         r"hasta el|hasta|até|fino al|tot en met|t/m|till och med|t\.o\.m\.?|indtil|frem til|до|по|do dnia|"
         r"mpaka|sampai dengan|hingga")
LIMIT = re.compile(rf"(?i)\b(?:{UNTIL})\s*(?:the\s+|le\s+|el\s+|o\s+|il\s+|den\s+|dem\s+)?(?:{DATE})")
CUR = (r"€|eur(?:o|os)?|\$|usd|dollars?|£|gbp|pounds?|chf|francs?|kr\.?|kronor|kroner|sek|nok|dkk|"
       r"lei|ron|zł|zloty|czk|kč|korun|huf|forint|rub|руб(?:лей|ля|\.)?|lari|gel|azn|manat|dram|amd|"
       r"tl|lira|lire|liras|pesos?|reais|r\$|soles|bolívares|rand|zar|naira|shillings?|kwacha|"
       r"cedis?|rupees?|rs\.?|rupiah|rp\.?|yen|円|元|yuan|won|baht|ringgit|dinars?|dirhams?|riyals?")
PCT = r"%|per ?cent|pour cent|por ciento|por cento|prozent|procent|процент\w*"
NUM = r"\d{1,3}(?:[ ., ']\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?"
AMT = re.compile(rf"(?i)(?:(?P<c1>{CUR})\s?(?P<n1>{NUM})|(?P<n2>{NUM})\s?(?P<c2>{CUR}|{PCT}))(?!\w)")


def norm_num(s: str) -> str:
    s = s.strip(" ., '")
    m = re.match(r"^(.*?)[.,](\d{1,2})$", s)  # keep decimals as .dd
    if m and not re.search(r"[.,]\d{3}$", s):
        return (re.sub(r"\D", "", m.group(1)).lstrip("0") or "0") + "." + m.group(2)
    return re.sub(r"\D", "", s).lstrip("0") or "0"


def amounts(text: str) -> set[tuple[str, str]]:
    out = set()
    for m in AMT.finditer(text):
        n = m.group("n1") or m.group("n2")
        c = (m.group("c1") or m.group("c2") or "").lower()
        v = norm_num(n)
        pct = bool(re.fullmatch(PCT, c, re.I))
        if v in ("0",) or (not pct and len(v.split(".")[0]) < 2):
            continue
        if not pct and len(v) == 4 and v.startswith(("19", "20")):
            continue
        out.add((v, "%" if pct else c.rstrip(".")))
    return out


DEADLINE_RX = re.compile(rf"(?i)\b(?:{DEADLINE})\s*$")


def limits(text: str, deadlines: bool = True):
    """(iso date, context) for every 'until <date>' in the text; deadlines=False drops 'not later than <date>' deadlines."""
    for m in LIMIT.finditer(text):
        g = m.groupdict()
        if not deadlines and re.match(rf"(?i)(?:{DEADLINE})\b", m.group(0)):
            continue
        try:
            if g.get("y5"):
                y, mo, d = int(g["y5"]), int(g["m5"]), int(g["d5"])
            elif g["y1"]:
                y, mo, d = int(g["y1"]), MI[g["mon"].lower()], int(g["d1"])
            elif g["y2"]:
                y, mo, d = int(g["y2"]), MI[g["mon2"].lower()], int(g["d2"])
            elif g["y3"]:
                y, mo, d = int(g["y3"]), int(g["m3"]), int(g["d3"])
            else:
                y, mo, d = int(g["y4"]), int(g["m4"]), int(g["d4"])
        except (KeyError, TypeError, ValueError):
            continue
        if 1800 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 31:
            s, e = max(0, m.start() - 200), min(len(text), m.end() + 100)
            yield f"{y:04d}-{mo:02d}-{d:02d}", text[s:e].replace("\n", " ")


class Cat:
    def __init__(self, repo: Path):
        self.p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=repo, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, creationflags=FLAGS)

    def __call__(self, sha: str) -> str:
        self.p.stdin.write(sha.encode() + b"\n")
        self.p.stdin.flush()
        head = self.p.stdout.readline().split()
        if len(head) < 3 or head[1] != b"blob":
            return ""
        data = self.p.stdout.read(int(head[2]))
        self.p.stdout.read(1)
        return data.decode("utf-8", errors="replace")

    def close(self):
        self.p.stdin.close()
        self.p.wait()


def stream(repo: Path, shas: list[str]):
    """Yield (sha, text) for many blobs through one buffered cat-file process (a writer thread feeds it)."""
    import threading
    p = subprocess.Popen(["git", "cat-file", "--batch", "--buffer"], cwd=repo, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=FLAGS, bufsize=1 << 20)

    def feed():
        try:
            for sh in shas:
                p.stdin.write(sh.encode() + b"\n")
        finally:
            p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    for sh in shas:
        head = p.stdout.readline().split()
        if len(head) < 3 or head[1] != b"blob":
            yield sh, ""
            continue
        data = p.stdout.read(int(head[2]))
        p.stdout.read(1)
        yield sh, data.decode("utf-8", errors="replace")
    p.wait()


SKIP = {"readme.md", "reproduce.md", "changelog.md", "license.md", "sources.md", "contributing.md"}


def is_law_file(path: str) -> bool:
    p = path.lower()
    return p.endswith((".md", ".txt")) and p.rsplit("/", 1)[-1] not in SKIP and not p.startswith(("docs/", "tools/", "tests/", ".github/"))


def one(c: dict, shard: int = 0, nshards: int = 1):
    lower_priority()
    t0 = time.time()
    repo = CORPUS / f"{c['repo']}.git"
    D = {k: [] for k in ("path", "until", "context")}
    A = {k: [] for k in ("path", "value", "unit")}
    cur = []
    for line in git("ls-tree", "-r", c["sha"], cwd=repo).splitlines():
        meta, path = line.split("\t", 1)
        if meta.split()[1] == "blob" and is_law_file(path):
            cur.append((meta.split()[2], path))
    cur = cur[shard::nshards]
    for (_, text), (_, path) in zip(stream(repo, [x[0] for x in cur]), cur):
        if len(text) > 2_000_000:
            continue
        for u, ctx in limits(text):
            D["path"].append(path); D["until"].append(u); D["context"].append(ctx)
        for v, u in amounts(text):
            A["path"].append(path); A["value"].append(v); A["unit"].append(u)
    con = duckdb.connect()
    rows = con.sql(f"""select ch.commit, ch.path, ch.old_blob, ch.new_blob, r.in_force, r.law
        from '{(INDEX / 'changes' / (c['repo'] + '.parquet')).as_posix()}' ch
        join '{(INDEX / 'root.parquet').as_posix()}' r on r.corpus_commit = ch.commit
        where left(ch.status,1)='M' and r.kind='law'""").fetchall()
    X = {k: [] for k in ("commit", "path", "in_force", "law", "removed", "added")}
    rows = [r for r in rows if is_law_file(r[1])][shard::nshards]
    flat = [sh for r in rows for sh in (r[2], r[3])]
    texts = stream(repo, flat)
    for commit, path, ob, nb, inf, law in rows:
        a, b = next(texts)[1], next(texts)[1]
        if len(a) > 1_000_000 or len(b) > 1_000_000:
            continue
        la, lb = set(a.splitlines()), set(b.splitlines())  # only lines that changed can change an amount
        old, new = amounts(chr(10).join(la - lb)), amounts(chr(10).join(lb - la))
        rem, add = old - new, new - old
        if rem or add:
            X["commit"].append(commit); X["path"].append(path); X["in_force"].append(inf); X["law"].append(law)
            X["removed"].append([f"{v}|{u}" for v, u in sorted(rem)])
            X["added"].append([f"{v}|{u}" for v, u in sorted(add)])
    for name, cols in (("dates", D), ("amounts", A), ("amount_changes", X)):
        (INDEX / name).mkdir(parents=True, exist_ok=True)
        schema = pa.schema([(k, pa.list_(pa.string()) if k in ("removed", "added") else pa.string()) for k in cols])
        t = pa.table(cols, schema=schema)
        t = t.append_column("corpus", pa.array([c["path"]] * t.num_rows, pa.string()))
        stem = c["repo"] if nshards == 1 else f"{c['repo']}.s{shard}of{nshards}"
        pq.write_table(t, INDEX / name / f"{stem}.parquet", compression="zstd")
    return f"{c['repo']}[{shard}/{nshards}]", len(D["path"]), len(A["path"]), len(X["path"]), len(rows), time.time() - t0


def _one(args):
    return one(*args)


if __name__ == "__main__":
    t0 = time.time()
    if sys.argv[1:2] == ["--shards"]:  # e.g. --shards france-law:6 spain-law:2
        plan = dict(a.split(":") for a in sys.argv[2:])
        jobs = [(c, i, int(plan[c["repo"]])) for c in pins()["corpora"] if c["repo"] in plan for i in range(int(plan[c["repo"]]))]
        with ProcessPoolExecutor(WORKERS) as ex:
            for r in ex.map(_one, jobs):
                print("%-42s limits=%-7d amounts=%-8d amount_changes=%-7d of_M=%-8d %.0fs" % r, flush=True)
        print(f"done in {time.time()-t0:.0f}s", flush=True)
        sys.exit(0)
    only = set(sys.argv[1:])
    corp = [c for c in pins()["corpora"] if (not only or c["repo"] in only)
            and not (INDEX / "amount_changes" / f"{c['repo']}.parquet").exists()]
    corp.sort(key=lambda c: -(INDEX / "changes" / f"{c['repo']}.parquet").stat().st_size)
    with ProcessPoolExecutor(WORKERS) as ex:
        for r in ex.map(one, corp):
            print("%-42s limits=%-7d amounts=%-8d amount_changes=%-7d of_M=%-8d %.0fs" % r, flush=True)
    print(f"done in {time.time()-t0:.0f}s", flush=True)
