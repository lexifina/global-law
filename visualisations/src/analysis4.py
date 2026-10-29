"""Obligation words per 1,000 words, in force today, constitution against ordinary law, every repo -> analysis4.json
RegData-style counting of binding language, with a word list per language.
"""
import json, re
from pathlib import Path

D = Path.home() / "Documents"
OBL = {
    "en": r"\bshall\b(?!\s+not)|\bmust\b|\bis required to\b|\bare required to\b",
    "pro_en": r"\bshall not\b|\bmust not\b|\bmay not\b|\bis prohibited\b|\bare prohibited\b",
    "de": r"\b(muss|müssen|hat\s+\w+\s+zu|ist verpflichtet|sind verpflichtet|haben\s+\w+\s+zu)\b",
    "pro_de": r"\b(darf nicht|dürfen nicht|ist verboten|ist unzulässig|sind unzulässig|darf\s+\w+\s+nicht)\b",
    "fr": r"\b(doit|doivent|est tenu|sont tenus|est tenue)\b",
    "pro_fr": r"\b(ne peut|ne peuvent|est interdit|sont interdits|il est interdit)\b",
    "sk": r"\b(musí|musia|je povinný|je povinná|sú povinní|je povinné)\b",
    "pro_sk": r"\b(nesmie|nesmú|je zakázané|nemôže|nemôžu)\b",
    "sl": r"\b(mora|morajo|je dolžan|so dolžni|je dolžna)\b",
    "pro_sl": r"\b(ne sme|ne smejo|je prepovedan|je prepovedano)\b",
    "et": r"\b(peab|peavad|on kohustatud|on kohustus)\b",
    "pro_et": r"\b(ei tohi|on keelatud)\b",
    "fi": r"\b(on velvollinen|ovat velvollisia|täytyy|on huolehdittava)\b",
    "pro_fi": r"\b(ei saa|on kielletty|ei voida)\b",
    "hr": r"\b(mora|moraju|dužan je|dužni su|obvezan je|obvezni su)\b",
    "pro_hr": r"\b(ne smije|ne smiju|zabranjen|zabranjeno)\b",
    "da": r"\b(skal)\b",
    "it": r"\b(deve|devono|è tenuto|sono tenuti|è obbligato)\b",
    "pro_it": r"\b(non può|non possono|è vietato|sono vietati)\b",
    "pt": r"\b(deve|devem|é obrigado|são obrigados)\b",
    "pro_pt": r"\b(não pode|não podem|é proibido|são proibidos)\b",
    "pro_da": r"\b(må ikke|ikke må|er forbudt|kan ikke)\b",
}
SETS = [  # code, repo, language, constitution glob, ordinary-law globs
    ("de", "law-in-motion/corpora/grundgesetz", "de", "artikel/*.md", []),
    ("ch", "swiss-law", "de", "101/art-*.md", ["235.1/art-*.md", "281.1/art-*.md"]),
    ("li", "liechtenstein-law", "de", "lv/art-*.md", ["vrg/*.md", "stghg/*.md"]),
    ("lu", "luxembourg-law", "fr", "constitution/**/art_*.md", ["loi/**/*.md"]),
    ("mc", "monaco-law", "fr", "constitution/article-*.md", ["loi-1362/article-*.md"]),
    ("sk", "slovakia-law", "sk", "ustava/cl-*.md", ["volebny-zakon/par-*.md"]),
    ("si", "slovenia-law", "sl", "urs/clen-*.md", ["zvdz/clen-*.md"]),
    ("ee", "estonia-law", "et", "ps/para-*.md", ["rkvs/*.md", "iks/*.md"]),
    ("fi", "finland-law", "fi", "perustuslaki/pykala-*.md", []),
    ("hr", "croatia-law", "hr", "ustav/clanak-*.md", []),
    ("gi", "gibraltar-law", "en", "constitution/**/s-*.md", ["stamp-duties/*.md"]),
    ("dk", "denmark-law", "da", "grundloven/par-*.md", ["skatteforvaltningsloven/*.md"]),
    ("hk", "hong-kong-law", "en", None, ["cap-*/*.md"]),
    ("it", "italy-law", "it", "costituzione/*.md", ["decreto-legislativo/**/*.md"]),
    ("pt", "portugal-law", "pt", "constituicao/artigo-*.md", ["codigo-civil/*.md", "codigo-do-trabalho/*.md"]),
    ("mg", "madagascar-law", "fr", "constitution/article-*.md", []),
    ("rw", "rwanda-law", "en", "constitution/art-*.md", ["law-2020-017/*.md"]),
    ("us", "us-code-history", "en", None, ["title-*/*.md"]),
    ("gb", "uk-law-history", "en", None, ["ukpga/**/*.md", "uksi/**/*.md"]),
    ("mt", "law-in-motion/corpora/malta-law", "en", None, ["cap/**/*.md"]),
]


def body(t):
    t = re.sub(r"^---.*?---\s*", "", t, flags=re.S)
    return re.sub(r"^#.*$", "", t, flags=re.M)


def count(files, lang):
    w = o = p = 0
    for f in files:
        if f.name.lower() == "readme.md": continue
        t = body(f.read_text(encoding="utf-8", errors="ignore"))
        w += len(re.findall(r"\w+", t))
        o += len(re.findall(OBL[lang], t, re.I)); p += len(re.findall(OBL["pro_" + lang], t, re.I))
    return {"words": w, "obl": o, "pro": p, "files": len(files)}


out = {}
for code, repo, lang, cg, og in SETS:
    root = D / repo
    if not root.exists(): continue
    r = {"lang": lang}
    if cg: r["const"] = count(sorted(root.glob(cg)), lang)
    if og: r["ordinary"] = count(sorted({f for g in og for f in root.glob(g)}), lang)
    out[code] = r
    for k in ("const", "ordinary"):
        if k in r and r[k]["words"]:
            v = r[k]; print(code, k, v["files"], v["words"], "obl/1k", round(1000 * v["obl"] / v["words"], 2), "pro/1k", round(1000 * v["pro"] / v["words"], 2))
Path("analysis4.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
