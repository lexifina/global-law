"""OLRC's own verdicts on amendments: Amendment notes in the 2024 and 2023 editions of the Code (GovInfo HTML, cached by
the US Code history build) that say an amendment "could not be executed" or was "executed ... to reflect the probable
intent of Congress". Output: data/olrc_notes.tsv (title, section, law, kind, note text)."""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fetch  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
rows = {}
for year in (2024, 2023):
    for t in range(1, 55):
        url = f"https://www.govinfo.gov/content/pkg/USCODE-{year}-title{t}/html/USCODE-{year}-title{t}.htm"
        data = fetch.fetch(url, offline=True)
        if not data:
            continue
        s = data.decode("utf-8", errors="replace")
        heads = [(m.start(), html.unescape(m.group(1))) for m in re.finditer(r'<h3 class="section-head">(.*?)</h3>', s)]
        for i, (pos, head) in enumerate(heads):
            m = re.match(r"\[?§\s*([0-9]+[A-Za-z]*(?:[-–][0-9]+[A-Za-z]*)?)\.", head)
            if not m:
                continue
            sec = m.group(1).replace("–", "-")
            end = heads[i + 1][0] if i + 1 < len(heads) else len(s)
            body = s[pos:end]
            for p in re.findall(r'<p class="note-body">(.*?)</p>', body, re.S):
                txt = html.unescape(re.sub(r"<[^>]+>", "", p))
                kind = ("not_executed" if "could not be executed" in txt else
                        "probable_intent" if "probable intent" in txt else None)
                if not kind:
                    continue
                for law in re.findall(r"Pub\. L\. (\d+)[–-](\d+)", txt)[:1]:   # the law the note is about
                    key = (t, sec, f"Pub. L. {law[0]}-{law[1]}", kind)
                    rows.setdefault(key, re.sub(r"\s+", " ", txt)[:600])
with open(HERE / "data/olrc_notes.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("title\tsection\tlaw\tkind\tnote\n")
    for (t, sec, law, kind), txt in sorted(rows.items()):
        f.write(f"{t}\t{sec}\t{law}\t{kind}\t{txt}\n")
print(len(rows), "notes;", sum(1 for k in rows if k[3] == "not_executed"), "not executed")
