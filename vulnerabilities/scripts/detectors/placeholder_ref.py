"""placeholder_ref: a current provision refers to a provision of the same act whose current text is only a repeal
placeholder ('§ 12 (weggefallen)', 'Art. 376 (Revogado)', 'Derogado', 'Repealed'...). Run 1's dangling_ref only saw
provisions whose files were deleted; this catches acts that keep repealed numbers as placeholders.
python detectors/placeholder_ref.py RUN -> findings/RUN/placeholder_ref.jsonl"""
from __future__ import annotations
import json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from common import FINDINGS, CORPUS, FLAGS, WORKERS, pins, lower_priority
from refscan import refs, path_key, act_of, is_external, before_ref

GONE = re.compile(r"(?i)\b(weggefallen|aufgehoben|revogad[oa]|derogad[oa]|abrogé|abrogée|abrogato|abrogata|repealed|deleted|omitted|"
                  r"mülga|upphävd|upphävs|kumottu|kumottiin|ophævet|opphevet|утратил|утратила|zrušen|zrušeno|uchylony|uchylona|"
                  r"razveljavljen|brisan|çıxarılmışdır|sin contenido|suprimid[oa]|vervallen|vervalt|ingetrokken|annullato|soppresso|"
                  r"ուժը կորցրել|ძალადაკარგ|ამოღებულია|καταργ\w*|not in the \w[\w .']* (?:code|database)|not printed in|"
                  r"\[omitted\]|spent|lapsed|expired|vacat|prestao (?:da )?važi\w*|nevalid\w*|abrogat\w*|hatályon kívül|kehtetu\w*|"
                  r"zaudējis spēku|netekęs galios|исключ[её]н\w*|утратил[аио]? силу|виключено|втратил\w* чинність|հանված|"
                  r"sin efecto|sans objet|void|[(\[]\s*(?:reserved|réservé)\s*[)\]]|διαγρ\w*|ยกเลิก|has had its effect)")
LABEL = re.compile(r"(?i)^\W{0,3}(?:art\.?|article|articolo|artículo|artigo|artikel|άρθρο|madde|section|sec\.|§|มาตรา|член|članak|"
                   r"статья|regulation|rule)?\s*[\dIVXLC๐-๙]{1,6}[a-z]?\s*[.\-–—:)]?\s*$")
NOTE_LINE = re.compile(r"(?i)^\s*(?:source|history|formerly|as amended|as added|amended by|added by|repealed and re-?enacted|"
                       r"historical and statutory|credits|editor|note|fn\b|\[(?!\s*(?:repealed|omitted|deleted|spent|reserved|has had))|\((?![\da-z]{1,3}\))|-|>|\*|\d{1,2}[./]\d{1,2}[./]\d{2,4}|"
                       r"საქართველოს|bgbl|stb\.|boe|jorf|s\.i\.|l\.n\.|p\.l\.|pub\. ?l\.|stats?\.|acts? \d{4})")


def is_placeholder(text: str) -> bool:
    """the provision's only content is a repeal or omission marker (headings and source notes aside)."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    head = " ".join(l.lstrip("# ") for l in lines if l.startswith("#"))
    body = [l for l in lines if not l.startswith("#")]
    labels = [l for l in body if LABEL.match(l)]
    head = (head + " " + " ".join(labels)).strip()
    sub = [l for l in body if not NOTE_LINE.match(l) and not LABEL.match(l)]
    substantive = " ".join(sub)
    if re.search(r"(?i)re-?enacted|\brepeal of\b|repeals? (?:the|all|any)|sont abrog|quedan derogad|ficam revogad|werden aufgehoben",
                 substantive):
        return False
    if not substantive:
        return bool(GONE.search(head) or any(GONE.search(l) for l in body))
    if substantive.strip(" .[]()").lower() in ("reserved", "réservé", "omitted", "repealed", "spent"):
        return True
    return len(substantive) <= 400 and bool(GONE.search(substantive[:70]))
EXTERNAL = re.compile(r"(?i)^\W{0,3}(?:(?:absatz|abs\.|satz|nummer|nr\.|buchstabe|par[áa]grafo|§|inciso|al[íi]nea|apartado|n[º°o]\.?|letra|lit\.|"
                      r"paragraph|subsection|para\.?|\(\w{1,4}\))\s*[\w.]{0,6}\s*,?\s*)*(?:des|der|dem|da|do|dos|das|de la|del|de los|de l'|du|"
                      r"della|dello|of the|of|a la|al|à la|au|ao|à)\s+(?!dieses|dieser|desta|deste|esta|este|la présente|présente|this|questa|presente|"
                      r"chapter|part|title|division|article|subchapter|subdivision|subtitle|subpart|schedule|kapitel|abschnitt|teil|cap[íi]tulo|t[íi]tulo|secci[oó]n|chapitre|titre|section)")
PENAL = re.compile(r"(?i)bestraft|bu(ss|ß)e|geldbu|ordnungswidrig|freiheitsstrafe|geldstrafe|amende|puni|emprisonnement|multa|\bpena\b|penas|"
                   r"sanci|infracci|infraç|reclus|detenç|\bfine\b|penalty|imprisonment|offence|liable on conviction|ceza|cərimə|штраф|boete|straf")


def one(c):
    lower_priority()
    repo = CORPUS / f"{c['repo']}.git"
    if not repo.exists():
        return []
    ls = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "-z", "--format=%(objectname) %(path)", c["sha"]],
                        capture_output=True, creationflags=FLAGS).stdout.decode("utf-8", "replace").split("\0")
    files = {}
    for x in ls:
        if x and x.endswith(".md"):
            sha, path = x.split(" ", 1)
            if path_key(path) or True:
                files[path] = sha
    if not files:
        return []
    p = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"], input=("\n".join(files.values()) + "\n").encode(),
                       capture_output=True, creationflags=FLAGS).stdout
    text, pos = {}, 0
    for path in files:
        nl = p.index(b"\n", pos); size = int(p[pos:nl].split()[2]); text[path] = p[nl + 1: nl + 1 + size].decode("utf-8", "replace"); pos = nl + 2 + size
    holders = {}
    for path, t in text.items():
        k = path_key(path)
        if not k:
            continue
        if is_placeholder(t):
            holders[(act_of(path), k)] = (path, re.sub(r"\s+", " ", t)[:200])
    if not holders:
        return []
    acts = {a for a, _ in holders}
    out = []
    for path, t in text.items():
        a = act_of(path)
        if a not in acts or (a, path_key(path)) in holders:
            continue
        for k, ctx, tail in refs(t):
            h = holders.get((a, k))
            if not h or h[0] == path or EXTERNAL.match(tail) or is_external(before_ref(ctx, tail), tail):
                continue
            out.append({"corpus": c["path"], "repo": c["repo"], "path": path, "ref": k, "target": h[0], "target_text": h[1],
                        "context": ctx, "penal": bool(PENAL.search(ctx) or PENAL.search(t[:400]))})
    return out


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    cs = [c for c in pins()["corpora"] if not c["repo"].startswith(("united-kingdom", "romania", "czechia"))]
    n = 0
    def safe(c):
        try:
            return one(c)
        except Exception as e:  # one corpus must not sink the run
            print(f"error in {c['repo']}: {type(e).__name__}: {e}", flush=True)
            return []
    with ThreadPoolExecutor(min(WORKERS, 6)) as ex, (FINDINGS / run / "placeholder_ref.jsonl").open("w", encoding="utf-8") as fh:
        for rows in ex.map(safe, cs):
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
    print("placeholder_ref", n)


if __name__ == "__main__":
    main()
