"""Sénat questions SQL dump (data.senat.fr questions.zip -> questions.sql) -> one text file per question about tax.
Usage: python3 -I harness/auth_senat_extract.py questions.sql OUTDIR"""
import html, os, re, sys
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
TAX = re.compile(r"impôt sur le revenu|code général des impôts|prélèvement à la source|hauts revenus", re.I)
def unesc(s):
    if s == r"\N": return ""
    s = s.replace(r"\r", "").replace(r"\n", "\n").replace(r"\t", "\t").replace("\\\\", "\\")
    return html.unescape(re.sub(r"<[^>]+>", " ", s))
qs, reps, mode, cols = {}, {}, None, None
for line in open(src, encoding="utf-8", errors="replace"):
    if line.startswith("COPY "):
        name = line.split()[1]; cols = re.search(r"\((.*)\)", line).group(1).split(", ")
        mode = name if name in ("tam_questions", "tam_reponses") else None; continue
    if mode is None: continue
    if line.startswith(chr(92) + "."): mode = None; continue
    r = dict(zip(cols, line.rstrip("\n").split("\t")))
    if mode == "tam_questions": qs[r["id"]] = r
    else: reps.setdefault(r["idque"], []).append(r)
k = 0
for i, q in qs.items():
    body = unesc(q.get("txtque", "")) + "\n=== RÉPONSE ===\n" + "\n".join(unesc(x.get("txtrep", "")) for x in reps.get(i, []))
    if not TAX.search(body) and not TAX.search(unesc(q.get("titre", ""))): continue
    k += 1
    ref = re.sub(r"[^A-Za-z0-9_-]", "_", q.get("reference") or i)
    with open(os.path.join(out, f"SEN_{ref}.txt"), "w", encoding="utf-8") as f:
        for a in ("reference", "numero", "legislature", "titre", "rubrique", "datejodepot", "pagejodepot", "mindepotlib", "datejorep1"):
            f.write(f"{a}: {unesc(q.get(a, ''))}\n")
        for x in reps.get(i, []): f.write(f"reponse_jo: {x.get('datejorep')} page {x.get('pagejorep')} ({unesc(x.get('minreplib',''))})\n")
        f.write("\n" + body)
print(len(qs), "questions;", k, "kept")
