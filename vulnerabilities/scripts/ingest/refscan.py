"""Dangling internal references, every corpus, any language.

For each act folder: the provision keys that ever existed (from the heading of every version) and those that exist now;
for each current provision: references to provisions of the same kind ("§ 12", "Art. 7", "article 7", "artículo 7",
"Madde 7", "Section 7", "7 §", "Статья 7", "Հոդված 7", "მუხლი 7", ...). A reference to a key that existed in that act
and no longer exists is a candidate dangling reference.

python ingest/refscan.py [repo ...]          -> index/refs/<repo>.parquet
python ingest/refscan.py --shards repo:N ...
"""
from __future__ import annotations
import re, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import duckdb, pyarrow as pa, pyarrow.parquet as pq
from common import CORPUS, INDEX, WORKERS, git, lower_priority, pins
from textscan import is_law_file, stream

UNIT = (r"§§?|art\.|arts\.|article|articles|artikel|artikels|artículo|artículos|articulo|artigo|artigos|articolo|articoli|"
        r"artykuł|článek|članak|člen|clanak|madde|maddesi|section|sections|sec\.|s\.|статья|статьи|статті|стаття|հոդված|"
        r"հոդվածի|მუხლი|მუხლის|maddə|maddəsi|pykälä|paragrahv|straipsnis|pants|άρθρο|pasal|bab|seksyen|regulation|rule|"
        r"regla|règle|norma|numeral|inciso|άρθρου|άρθρα|άρθρων|άρθρ\w*|член\w*|чл\.|члан\w*|članka|članku|članak|članaka|"
        r"articol\w*|artikull\w*|artikelen|član\w*|čl\.|regulations|rules|neni|nenit|cikk|straipsni\w*|pantu|pantā|artiklan|artikla|maddesinin|maddenin|มาตรา")
LATIN = r"bis|ter|quater|quinquies|sexies|septies|octies|nonies|novies|decies"
# a suffix is either a Latin ordinal (may follow a space or hyphen) or one or two letters glued to the number
# ("12a", "12-A"); a separate word ("12 of", "458 y", "24 se") is never a suffix (the bug that halved recall).
NUM = rf"(\d{{1,2}}\.\d{{3}}(?!\d|\.\d)|\d{{1,4}})(?:[\s\-‑]?({LATIN})(?![a-z])|[\-‑]?([A-Za-z]{{1,2}})(?![A-Za-zÀ-ÿ\d]))?"
REF = re.compile(rf"(?i)(?<![\w])(?:{UNIT})\s*{NUM}")
NORDIC = re.compile(rf"(?i)(?<![\w\d.])(\d{{1,4}})\s?([a-z])?\s?§")  # Swedish/Danish/Norwegian/Finnish "7 §", "7 a §"
# number before the unit word: Slovene/Croatian/Serbian "65. člena", Czech/Slovak "5. článku", Hungarian "5. §", Baltic
PRE = re.compile(r"(?i)(?<![\w\d.])(\d{1,4})(?:\.\s*(?:člen\w*|član\w*|článk\w*|cikk\w*|straipsn\w*|pant\w*|§)|"
                 r"(?:-\d{1,3})?[-\s]?(?:ci|cı|cu|cü|nci|ncı|ncu|ncü|inci|ıncı|uncu|üncü|ünci|uncı)\s+madd\w*|"
                 r"\s+straipsn\w*|\s+pant\w*)")
CJK = re.compile(r"第\s*([\d一二三四五六七八九十百千〇零]{1,8})\s*[條条](?:\s*之\s*(\d{1,3}))?")
KANJI = {c: i for i, c in enumerate("〇一二三四五六七八九")}; KANJI["零"] = 0
THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")


def kanji_int(s: str) -> int:
    if s.isdigit():
        return int(s)
    total, cur = 0, 0
    for ch in s:
        if ch in KANJI:
            cur = cur * 10 + KANJI[ch] if cur else KANJI[ch]
        else:
            mult = {"十": 10, "百": 100, "千": 1000}[ch]
            total += (cur or 1) * mult; cur = 0
    return total + cur
ARMENIAN = re.compile(r"(?<![\d])(\d{1,4})\s*-?\s*(?:րդ|ին)\s+հոդված\w*")
EXT_BEFORE = re.compile(r"(?i)(?:\w+(?:lovens?|lagens?|loven|lagen|lov|laki|lain|gesetzes|gesetzbuchs?|ordnung|verordnung|"
                        r"kodeksi|koodeksi|kanunu|kanununun|zakona|zákona|törvény|"
                        r"code's|act's)|\bAct(?:\s+\d{4})?|\bU\.S\.C\.|\bC\.F\.R\.|\bCode|\bStat\.)\s*(?:\(\w+\)\s*)?$")
EXT_AFTER = re.compile(r"^\s*(?:(?:Abs\.|Absatz|Satz|para\.?|al\.|lit\.|Nr\.|Ziff\.)\s*\w+\s*,?\s*)*(?:[A-ZÄÖÜ]{2,}[A-Za-zÄÖÜ]*|EU|EG|EWG)\b(?![.:])")


def is_external(before: str, tail: str) -> bool:
    """another act named just before ('ekteskapsloven § 8', 'Customs Act 2018 Sections 306') or by acronym after ('Art. 34 DSGVO')."""
    return bool(EXT_BEFORE.search(before[-60:]) or EXT_AFTER.match(tail))


THAI = re.compile(r"มาตรา\s*(\d{1,4})")
MONGOL = re.compile(r"(?:хуулийн|журмын|дүрмийн)\s+(\d{1,4})(?:\.\d{1,3})*(?:\s*-?\s*(?:т|д|ыг|ийн|д заасан|т заасан))")
ARABIC = re.compile(r"(?:المادة|المادتين|مادة|للمادة|بالمادة|والمادة)\s*\(?\s*([0-9٠-٩]{1,4})")
LISTNUM = re.compile(rf"\s*(?:,|;|\band\b|\bor\b|\by\b|\be\b|\bet\b|\bou\b|\bund\b|\boder\b|\bo\b|\bve\b|\bi\b|\bin\b|\bта\b|\bи\b|\bа\b|"
                     rf"\ben\b|\bog\b|\boch\b|\bsamt\b)\s*(?:(?:art\.|arts\.|§§?|section|sections|artikel|artículo|artigo|articolo)\s*)?{NUM}")
RANGENUM = re.compile(rf"\s*(?:to|through|thru|bis|à|a|al|até|fino a|tot en met|tot|t/m|till|–|-|—|до|do)\s*(?:(?:art\.|§§?|section)\s*)?{NUM}", re.I)
NOTE = re.compile(r"(?i)(as added by|as amended by|amended by|added by|inserted by|substituted by|repealed by|P\.L\.\s*\d|"
                  r"Stats?\.\s*\d|\bSource:|^\s*\(?(added|amended|inserted|substituted)\b|\bLN\s*\d|\bS\.I\.\s*\d|"
                  r"aufgehoben durch|eingefügt durch|geändert durch|derogado por|modificado por|redacción dada por|"
                  r"abrogé par|modifié par|revogado pel|alterado pel|incluído pel|redação dada pel|D\.C\. Law|\bDCR\b|Pub\. ?L\.|"
                  r"\((?:Added|Amended|Replaced|Repealed|Inserted|Substituted)\s+\d)")
HEAD = re.compile(rf"(?i)^\s*#*\s*(?:{UNIT})\s*{NUM}")
HEAD_NORDIC = re.compile(r"(?i)^\s*#*\s*(\d{1,4})\s?([a-z])?\s?§")
EXTERNAL = re.compile(r"(?i)^[\s,.;:()\-–]*(?:abs\.|absatz|satz|nr\.|para|paragraph|al\.|alinéa|apartado|párrafo|"
                      r"inciso|lit\.|bst\.|of|des|der|del|de la|de|da|do|du|della|dello|van|av|i|z|zákona|ve|of the)\s*\S*")


def key(num: str, suf: str | None, suf2: str | None = None) -> str:
    num = num.replace(".", "").translate(THAI_DIGITS)
    s = (suf or suf2 or "").lower()
    if s in ("o", "º"):          # ordinal marker ("4o.", "1º"), not a suffix
        s = ""
    return f"{int(num)}{s}"


def _mkey(m) -> str:
    return key(m.group(1), m.group(2), m.group(3) if m.re.groups >= 3 else None)


def heading_key(text: str) -> str | None:
    first = next((l for l in text.splitlines() if l.strip()), "")
    m = HEAD.match(first) or HEAD_NORDIC.match(first)
    if not m:
        return None
    return _mkey(m) if m.re is HEAD else key(m.group(1), m.group(2))


SERIES = re.compile(r"(?i)(ek|geçici|gecici|adicional|transitoria|final|derogatoria|transitional|übergangs\w*|"
                    r"schluss\w*|annex|anhang|anlage|schedule|annexe|anexo|supplementary|additional)\s*$")
SERIES_PATH = re.compile(r"(?i)(^|[/_\-~])(ek|gecici|geçici|da|dt|df|dd|ad|annex|anlage|anhang|schedule|annexe|anexo|"
                         r"tablo|liste|yururluk|uebergang|transitional|supplement)([\-_~0-9]|$)")


REPEAL_NOTE = re.compile(r"(?i)in der fassung|außer kraft|ausser kraft|aufgehoben|entfällt|entfallen|weggefallen|"
                         r"derogad|derogó|suprimid|sin contenido|abrogé|abrogée|abrogés|mülga|"
                         r"repealed|omitted|spent|upphävd|upphör|kumotaan|ophævet|opphevet|утратил|утратила|"
                         r"ուժը կորցրած|ძალადაკარგ|revogad|καταργ")
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def _expand(body: str, m, first: str):
    """the reference itself plus any list or range that continues it: 'arts. 3, 5 and 7', 'sections 9 to 11'."""
    keys, pos, prev = [first], m.end(), int(re.match(r"\d+", first).group(0))
    while True:
        r = RANGENUM.match(body, pos)
        if r and r.group(1) and re.match(r"[-‑]\d+[-‑]\d", body[pos:pos + 12]):
            break  # "7-17-3" is a section number, not a range
        if r and r.group(1):
            hi = int(r.group(1).replace(".", ""))   # '1.048' (Brazilian thousands) is article 1048
            if prev < hi <= prev + 30:
                keys += [str(x) for x in range(prev + 1, hi)] + [key(r.group(1), r.group(2), r.group(3))]
                prev, pos = hi, r.end(); continue
        l = LISTNUM.match(body, pos)
        if l and l.group(1):
            keys.append(key(l.group(1), l.group(2), l.group(3))); prev, pos = int(l.group(1).replace(".", "")), l.end(); continue
        break
    return keys, pos


def before_ref(ctx: str, tail: str) -> str:
    """the text just before a reference's number. refs() returns ctx = 120 characters either side and tail = the 70 after
    the match, so the match ends where the tail starts. ctx.split(key) would cut at the key's first occurrence instead
    ('1831/2003' for 'Artikel 3')."""
    t = re.sub(r"\s+", " ", tail)[:40]
    end = ctx.rfind(t) if t.strip() else len(ctx)
    if end < 0:
        end = len(ctx)
    return re.sub(r"\d[\d.]*[\s\-]?(?:[A-Za-z]{1,2}|bis|ter|quater)?\s*$", "", ctx[:end])


def refs(text: str):
    """(key, context, tail) for every reference to a numbered provision in the body of a provision file."""
    # the first line is skipped only when it is a heading: some corpora (Brazil: 'Art. 347 - ...') have no heading line
    # and keep the provision's opening sentence there. The provision's own label is filtered by the caller (key == own).
    if text.lstrip().startswith("#"):
        body = text.split("\n", 1)[1] if "\n" in text else ""
    else:
        first, _, rest = text.partition("\n")
        first = re.sub(rf"(?i)^\s*(?:{UNIT})\s*{NUM}\s*[.\-–—:)]*", " ", first, count=1)   # drop the leading 'Art. 347 -'
        body = first + "\n" + rest
    body = "\n".join(l for l in body.splitlines() if "|" not in l)  # tables list other laws' articles
    seen_spans = []
    for rx in (REF, NORDIC, PRE, ARMENIAN, CJK, ARABIC, THAI, MONGOL):
        for m in rx.finditer(body):
            if any(a <= m.start() < b for a, b in seen_spans):
                continue
            ls = body.rfind("\n", 0, m.start()) + 1
            le = body.find("\n", m.end()); le = len(body) if le < 0 else le
            line, before = body[ls:le], body[ls:m.start()]
            tail = body[m.end():m.end() + 70]
            if not before.strip(" -*#>\t") and (re.match(r"\s*(?:\[\d+\])?\s*(?:\.?[-–—:]|\.\s|\.$|\)\s|[º°ª]\.?\s|$)", tail) or rx in (NORDIC, THAI)):
                continue  # the provision's own heading at the start of a line ("Artículo 7.-", "7 § Text", "Sec. 3. (a)")
            if re.match(r"\s*(?:\[\d+\])?\s*[–—\-:]\s", tail):
                continue  # an article heading inside the text ("Madde 7 –"), not a reference
            if rx is REF and re.match(r"\s*-?\s*(?:րդ|ին|ci|cı|cu|cü|nci|ncı|inci|üncü|ncü)\b", tail):
                continue  # the number belongs to the next unit ("հոդվածի 3-րդ մաս", "maddenin 2 nci fıkrası")
            if rx is REF and m.group(0).lstrip().startswith("§") and re.search(r"\d\s?[a-z]?\s?$", before):
                continue  # Nordic "6 § 2 mom.": the § belongs to the number before it
            if is_external(before, tail):
                continue
            if NOTE.search(line) or (REPEAL_NOTE.search(line) and (line.lstrip().startswith(("[", "(", "-", ">")) or len(line) < 200)):
                continue  # amendment / repeal notes legitimately name repealed provisions
            if SERIES.search(body[max(0, m.start() - 25):m.start()]):
                continue  # separately numbered series (Ek Madde, disposición adicional, transitional ...)
            if rx is ARABIC:
                first = str(int(m.group(1).translate(AR_DIGITS)))
                ks, end = [first], m.end()
            elif rx is CJK:
                first = str(kanji_int(m.group(1)))
                ks, end = [first], m.end()
            elif rx in (THAI, MONGOL, ARMENIAN):
                first = key(m.group(1), None)
                ks, end = [first], m.end()
            elif rx in (NORDIC, PRE):
                first = key(m.group(1), m.group(2) if rx is NORDIC else None)
                ks, end = [first], m.end()
            else:
                first = _mkey(m)
                ks, end = _expand(body, m, first)
            seen_spans.append((m.start(), end))
            ctx = body[max(0, m.start() - 120):end + 120].replace("\n", " ")
            for k in ks:
                yield k, ctx, body[end:end + 70]


def path_key(path: str) -> str | None:
    base = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    if SERIES_PATH.search("/" + base):
        return None
    m = re.match(r"(?i)^(?:art|madde|section|sec|s|para|paragraf|article|a|par|clanek|neni)?[-_]?0*(\d{1,4})[-_]?([a-z]{0,6})$", base)
    return key(m.group(1), m.group(2)) if m else None


def act_of(path: str) -> str:
    return path.rsplit("/", 1)[0] if "/" in path else ""


def one(c: dict, shard: int = 0, nshards: int = 1):
    lower_priority()
    t0 = time.time()
    repo = CORPUS / f"{c['repo']}.git"
    con = duckdb.connect()
    ch = (INDEX / "changes" / f"{c['repo']}.parquet").as_posix()
    hist = con.sql(f"""select ch.path, ch.new_blob, r.in_force, r.law from '{ch}' ch
        join '{(INDEX/'root.parquet').as_posix()}' r on r.corpus_commit = ch.commit
        where left(ch.status,1) <> 'D' and r.kind in ('law','baseline')""").fetchall()
    hist = [h for h in hist if is_law_file(h[0])]
    acts_shard = {a for a in {act_of(h[0]) for h in hist} if hash(a) % nshards == shard} if nshards > 1 else None
    if acts_shard is not None:
        hist = [h for h in hist if act_of(h[0]) in acts_shard]
    # every key that ever existed in each act, with the last date a file carried it
    blobs = list(dict.fromkeys(h[1] for h in hist))
    hk = {}
    for sha, text in stream(repo, blobs):
        hk[sha] = heading_key(text)
    ever: dict[tuple[str, str], tuple[str, str, str]] = {}
    for path, blob, inf, law in hist:
        if SERIES_PATH.search("/" + path.rsplit("/", 1)[-1]):
            continue
        for k in {hk.get(blob), path_key(path)} - {None}:
            a = act_of(path)
            if (a, k) not in ever or inf > ever[(a, k)][0]:
                ever[(a, k)] = (inf, path, law)
    cur = []
    for line in git("ls-tree", "-r", c["sha"], cwd=repo).splitlines():
        meta, path = line.split("\t", 1)
        if meta.split()[1] == "blob" and is_law_file(path) and (acts_shard is None or act_of(path) in acts_shard):
            cur.append((meta.split()[2], path))
    now: set[tuple[str, str]] = set()
    texts = {}
    for (sha, text), (_, path) in zip(stream(repo, [x[0] for x in cur]), cur):
        texts[path] = text
        if SERIES_PATH.search("/" + path.rsplit("/", 1)[-1]):
            continue
        for k in {heading_key(text), path_key(path)} - {None}:
            now.add((act_of(path), k))
    R = {k: [] for k in ("path", "ref", "context", "tail", "target_last_seen", "target_path", "target_last_law")}
    for path, text in texts.items():
        a = act_of(path)
        seen = {heading_key(text), path_key(path)}
        for k, ctx, tail in refs(text):
            if (a, k) in now or (a, k) not in ever or k in seen:
                continue
            seen.add(k)
            inf, tp, law = ever[(a, k)]
            R["path"].append(path); R["ref"].append(k); R["context"].append(ctx); R["tail"].append(tail)
            R["target_last_seen"].append(inf); R["target_path"].append(tp); R["target_last_law"].append(law)
    t = pa.table(R, schema=pa.schema([(k, pa.string()) for k in R]))
    t = t.append_column("corpus", pa.array([c["path"]] * t.num_rows, pa.string()))
    (INDEX / "refs").mkdir(parents=True, exist_ok=True)
    stem = c["repo"] if nshards == 1 else f"{c['repo']}.s{shard}of{nshards}"
    pq.write_table(t, INDEX / "refs" / f"{stem}.parquet", compression="zstd")
    return f"{c['repo']}[{shard}/{nshards}]", len(blobs), len(now), len(R["path"]), time.time() - t0


INLINE = re.compile(r"(?mi)^\s*(?:#+\s*|\*\*)?(?:§|art\.?|článek|čl\.|artikel|article|artículo|artigo|madde|section)\s*(\d{1,4})\s*([a-z]?)\s*(?:\*\*)?\.?\s*$")


def inline_keys(text: str) -> set[str]:
    return {key(m.group(1), m.group(2)) for m in INLINE.finditer(text)}


def one_fileact(c: dict):
    """Acts stored as one file with inline section headings (e.g. Czechia): the file is the act."""
    lower_priority()
    t0 = time.time()
    repo = CORPUS / f"{c['repo']}.git"
    con = duckdb.connect()
    ch = (INDEX / "changes" / f"{c['repo']}.parquet").as_posix()
    hist = con.sql(f"""select ch.path, ch.new_blob, r.in_force, r.law from '{ch}' ch
        join '{(INDEX/'root.parquet').as_posix()}' r on r.corpus_commit = ch.commit
        where left(ch.status,1) <> 'D' and r.kind in ('law','baseline') order by r.in_force""").fetchall()
    hist = [h for h in hist if is_law_file(h[0])]
    blobs = list(dict.fromkeys(h[1] for h in hist))
    ik = {sha: inline_keys(text) for sha, text in stream(repo, blobs)}
    ever: dict[tuple[str, str], tuple[str, str]] = {}
    prev: dict[str, set[str]] = {}
    for path, blob, inf, law in hist:  # a key 'removed' = present in one version of the file, gone in the next
        keys = ik.get(blob, set())
        if len(keys) < 3:
            continue
        for k in prev.get(path, set()) - keys:
            ever[(path, k)] = (inf, law)
        prev[path] = keys
    cur = []
    for line in git("ls-tree", "-r", c["sha"], cwd=repo).splitlines():
        meta, path = line.split("\t", 1)
        if meta.split()[1] == "blob" and is_law_file(path) and any(p == path for p, _ in ever):
            cur.append((meta.split()[2], path))
    R = {k: [] for k in ("path", "ref", "context", "tail", "target_last_seen", "target_path", "target_last_law")}
    for (sha, text), (_, path) in zip(stream(repo, [x[0] for x in cur]), cur):
        now = inline_keys(text)
        seen = set()
        for k, ctx, tail in refs(text):
            if k in now or (path, k) not in ever or k in seen:
                continue
            seen.add(k)
            inf, law = ever[(path, k)]
            R["path"].append(path); R["ref"].append(k); R["context"].append(ctx); R["tail"].append(tail)
            R["target_last_seen"].append(inf); R["target_path"].append(f"{path}#{k}"); R["target_last_law"].append(law)
    t = pa.table(R, schema=pa.schema([(k, pa.string()) for k in R]))
    t = t.append_column("corpus", pa.array([c["path"]] * t.num_rows, pa.string()))
    (INDEX / "refs_fileact").mkdir(parents=True, exist_ok=True)
    pq.write_table(t, INDEX / "refs_fileact" / f"{c['repo']}.parquet", compression="zstd")
    return c["repo"] + " (file=act)", len(blobs), len(ever), len(R["path"]), time.time() - t0


def _one(a):
    """one corpus; a failure is reported and that corpus skipped, so one odd line cannot sink a run of hundreds."""
    try:
        return one(*a)
    except Exception as e:
        print(f"error in {a[0]['repo'] if a and isinstance(a[0], dict) else a}: {type(e).__name__}: {e}", flush=True)
        return (f"FAILED {a[0]['repo'] if a and isinstance(a[0], dict) else a}"[:36], 0, 0, 0, 0)


if __name__ == "__main__":
    t0 = time.time()
    args = sys.argv[1:]
    plan = {}
    if args[:1] == ["--fileact"]:
        corp = [c for c in pins()["corpora"] if not args[1:] or c["repo"] in args[1:]]
        corp.sort(key=lambda c: -(INDEX / "changes" / f"{c['repo']}.parquet").stat().st_size)
        with ProcessPoolExecutor(WORKERS) as ex:
            for r in ex.map(one_fileact, corp):
                print("%-36s blobs=%-8d removed_keys=%-8d dangling=%-7d %.0fs" % r, flush=True)
        print(f"done in {time.time()-t0:.0f}s", flush=True)
        sys.exit(0)
    if args[:1] == ["--shards"]:
        plan = dict(x.split(":") for x in args[1:]); args = []
    only = set(args)
    jobs = []
    for c in pins()["corpora"]:
        if c["repo"] in plan:
            jobs += [(c, i, int(plan[c["repo"]])) for i in range(int(plan[c["repo"]]))]
        elif not plan and (not only or c["repo"] in only) and not (INDEX / "refs" / f"{c['repo']}.parquet").exists():
            jobs.append((c, 0, 1))
    jobs.sort(key=lambda j: -(INDEX / "changes" / f"{j[0]['repo']}.parquet").stat().st_size / j[2])
    with ProcessPoolExecutor(WORKERS) as ex:
        for r in ex.map(_one, jobs):
            print("%-36s blobs=%-8d keys_now=%-8d dangling=%-7d %.0fs" % r, flush=True)
    print(f"done in {time.time()-t0:.0f}s", flush=True)
