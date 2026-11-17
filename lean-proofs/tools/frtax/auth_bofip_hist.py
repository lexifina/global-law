"""Text of archived BOFiP versions fetched from bofip.impots.gouv.fr (raw HTML) -> grep-able text.
Usage: python3 -I harness/auth_bofip_hist.py data/authority/raw/bofip_hist data/authority/text/bofip_hist"""
import html, os, re, sys
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.endswith(".html"): continue
    t = open(os.path.join(src, f), encoding="utf-8", errors="replace").read()
    m = re.search(r'<div[^>]*class="[^"]*field--name-body[^"]*"[^>]*>(.*)', t, re.S)
    body = m.group(1) if m else t
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S)
    body = re.sub(r"</p>|<br\s*/?>|</li>|</h\d>", "\n", body)
    body = html.unescape(re.sub(r"<[^>]+>", " ", body)); body = re.sub(r"[ \t ]+", " ", body); body = re.sub(r"\n\s*\n+", "\n", body)
    open(os.path.join(out, f.replace(".html", ".txt")), "w", encoding="utf-8").write(f"ID: {f[:-5]}\nURL: https://bofip.impots.gouv.fr/bofip/identifiant={f[:-5]}\n\n" + body)
print("done")
