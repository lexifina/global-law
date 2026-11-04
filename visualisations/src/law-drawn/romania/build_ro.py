"""ro_data.json + ro_data2.json -> romanian-law-drawn.html (template_ro.html with compact data inlined); prints caption totals."""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
A = json.loads((HERE / "ro_data.json").read_text(encoding="utf-8"))
B = json.loads((HERE / "ro_data2.json").read_text(encoding="utf-8"))
acts = json.loads((HERE / "tip" / "data" / "acts.json").read_text(encoding="utf-8"))["acts"]
iss = B["issued"]
years = list(range(1990, 2027))
d = {
    "issued": {k: [iss[k].get(str(y), {}).get("issued", 0) for y in years] for k in ("Legea", "OUG", "OG", "HG")}, "years": years,
    "pm": B["pm"],
    "approvals": [[a["oug"], a["oug_pub"], a["lag"], a["verdict"][0], a["law"]] for a in A["approvals"]],
    "start": A["start"],
    "hubs": B["hubs"],
    "ccr": [[c["decision"], c["date"], c["target"], c["units"][:80]] for c in A["ccr"] if c["date"]],
    "fiscal": [[f["code"], f["date"], f["kind"], f["law"], f["units"]] for f in B["fiscal"] if not f["first"] and f["kind"] != "Correction"],
    "rect": [[r["rect"], r["target"], r["kind"], r["lag"]] for r in B["rect"]],
    "stats": {"acts": len(acts), "in_force": sum(1 for a in acts if a["status"] == "in force"), "commits": 37819},
    "cmp": json.loads((HERE.parent / "cmp.json").read_text(encoding="utf-8")),
    "spain": json.loads((HERE.parent / "spain_numbers.json").read_text(encoding="utf-8")),
}
for k in ("Legea", "OUG", "OG", "HG"):
    print(k, "1997-2026 total", sum(v for y, v in zip(years, d["issued"][k]) if y >= 1997), "| 2025", d["issued"][k][years.index(2025)], "| 2020", d["issued"][k][years.index(2020)])
gov = sum(sum(v for y, v in zip(years, d["issued"][k]) if y >= 1997) for k in ("OUG", "OG", "HG")); law = sum(v for y, v in zip(years, d["issued"]["Legea"]) if y >= 1997)
print(f"government acts per law 1997-2026: {gov/law:.1f} ({gov} vs {law})")
t = (HERE / "template_ro.html").read_text(encoding="utf-8")
# Part two (Romania among its neighbours): its sections go before the footer, its charts at the end of the script
t = t.replace("<footer>", (HERE / "part2.html").read_text(encoding="utf-8") + "\n<footer>", 1)
i = t.rindex("</script>"); t = t[:i] + (HERE / "part2.js").read_text(encoding="utf-8") + t[i:]
# Part three: same placement, with its own data file
d.update(json.loads((HERE / "part3_data.json").read_text(encoding="utf-8")))
t = t.replace("<footer>", (HERE / "part3.html").read_text(encoding="utf-8") + "\n<footer>", 1)
i = t.rindex("</script>"); t = t[:i] + (HERE / "part3.js").read_text(encoding="utf-8") + t[i:]
# Part four: same placement again
d.update(json.loads((HERE / "part4_data.json").read_text(encoding="utf-8")))
t = t.replace("<footer>", (HERE / "part4.html").read_text(encoding="utf-8") + "\n<footer>", 1)
i = t.rindex("</script>"); t = t[:i] + (HERE / "part4.js").read_text(encoding="utf-8") + t[i:]
# Part five: Romania against all of global law
d.update(json.loads((HERE / "part5_data.json").read_text(encoding="utf-8")))
t = t.replace("<footer>", (HERE / "part5.html").read_text(encoding="utf-8") + "\n<footer>", 1)
i = t.rindex("</script>"); t = t[:i] + (HERE / "part5.js").read_text(encoding="utf-8") + t[i:]
out = HERE / "romanian-law-drawn.html"
out.write_text(t.replace("__DATA__", json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")), encoding="utf-8", newline="\n")
print(out, out.stat().st_size, "bytes")
