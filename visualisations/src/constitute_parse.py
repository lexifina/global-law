"""Constitute topic tags per article for the German and Swiss constitutions -> constitute/tags.json"""
import json, re
from pathlib import Path
out = {}
for cid, key, art_re in [("German_Federal_Republic_2014", "de", r"Article\s+(\d+[a-z]?)"), ("Switzerland_2014", "ch", r"Art\.?\s+(\d+[a-z]?)")]:
    h = json.loads(Path(f"constitute/{cid}.html").read_text(encoding="utf-8"))["html"]
    tags, cur = {}, None
    for m in re.finditer(r'data-topics="([^"]+)"|<h3>(.*?)</h3>|<p>((?:Art|Article)\b[^<]*)</p>', h, re.S):
        if m.group(1) is None:
            a = re.match(art_re, re.sub("<[^>]+>", "", m.group(2) or m.group(3)).strip())
            if a: cur = a.group(1)
            continue
        topics = [t.rsplit("/", 1)[1] for t in m.group(1).split(",")]
        rest = h[m.end(): m.end() + 400]
        hm = re.search(r"<h3>(.*?)</h3>|<p>((?:Art|Article)[^<]*)</p>|<p class", rest, re.S)
        target = cur
        if hm and not hm.group(0).startswith("<p class"):
            a = re.match(art_re, re.sub("<[^>]+>", "", hm.group(1) or hm.group(2)).strip())
            target = a.group(1) if a else cur
        if target: tags.setdefault(target, set()).update(topics)
    out[key] = {k: sorted(v) for k, v in tags.items()}
    print(key, len(out[key]), "articles tagged;", sum(map(len, out[key].values())), "tags; e.g.", list(out[key].items())[:3])
def walk(ns, acc):
    for n in ns:
        acc[n["key"]] = n["label"]; walk(n.get("topics", []), acc)
    return acc
labels = walk(json.loads(Path("constitute/topics.json").read_text(encoding="utf-8")), {})
Path("constitute/tags.json").write_text(json.dumps({"tags": out, "labels": labels}, ensure_ascii=False), encoding="utf-8")
shared = set(t for v in out["de"].values() for t in v) & set(t for v in out["ch"].values() for t in v)
print(len(labels), "topic labels;", len(shared), "topics used by both")
