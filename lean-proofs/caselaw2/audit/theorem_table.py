"""Print the registered theorems as a Markdown table (name, module, one-line statement) from statements.lock."""
import json, os, re
d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "statements.lock"), encoding="utf-8"))
def short(s):
    s = re.sub(r"CaseLaw2\.(Spec\.Horty\.|Spec\.|Exec\.|Cert\.)?", "", s)
    s = " ".join(s.split())
    return s
print("| Theorem | Module | Statement (doc, or the locked statement abbreviated) |\n|---|---|---|")
for t in d:
    doc = t["doc"].strip()
    first = re.split(r"(?<=[.:])\s", doc)[0] if doc else ""
    stmt = short(t["statement"])
    stmt = stmt.split(" : ", 1)[1] if " : " in stmt else stmt
    text = (first.replace("**", "") + " — " if first else "") + "`" + (stmt[:170] + ("…" if len(stmt) > 170 else "")) + "`"
    name = re.sub(r"^CaseLaw2\.", "", t["name"])
    print(f"| `{name}` | {t['module'].replace('LegalProofs.CaseLaw2.', '')} | {text.replace('|', '∣')} |")
