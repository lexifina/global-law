"""Split the BOFiP open-data export (bofip-vigueur.json) into one text file per document.
Usage: python3 -I harness/auth_bofip_extract.py data/authority/raw/bofip/bofip-vigueur.json data/authority/text/bofip
Each file: header lines (ID, TITLE, VALID, URL, TYPE) then the 'contenu' text (paragraph numbers on their own lines)."""
import json, os, re, sys
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
docs = json.load(open(src, encoding="utf-8"))
idx = open(os.path.join(out, "_index.tsv"), "w", encoding="utf-8")
for d in docs:
    ident = d.get("identifiant_juridique") or "noid"
    perm = d.get("permalien") or ""
    m = re.search(r"identifiant=([A-Z0-9-]+)", perm)
    full = m.group(1) if m else ident
    fn = re.sub(r"[^A-Za-z0-9_.-]", "_", full) + ".txt"
    with open(os.path.join(out, fn), "w", encoding="utf-8") as f:
        f.write(f"ID: {full}\nTITLE: {d.get('titre')}\nVALID: {d.get('debut_de_validite')}\nURL: {perm}\nTYPE: {d.get('type')}\n\n")
        f.write((d.get("contenu") or "").replace(" ", " "))
    idx.write(f"{full}\t{d.get('debut_de_validite')}\t{d.get('type')}\t{d.get('titre')}\n")
print(len(docs), "docs")
