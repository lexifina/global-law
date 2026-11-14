"""Summarise a Dataverse dataset.json: title, licence, terms, description, files. Run with python -I."""
import json
import sys

for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    data = d.get("data", {})
    v = data.get("latestVersion", {})
    print("=====", path)
    print("status", d.get("status"), "| version", v.get("versionNumber"), v.get("versionMinorNumber"),
          "| release", v.get("releaseTime"))
    print("license:", json.dumps(v.get("license")))
    for k in ("termsOfUse", "termsOfAccess", "restrictions", "conditions", "disclaimer"):
        if v.get(k):
            print(k + ":", str(v.get(k))[:600])
    for block in v.get("metadataBlocks", {}).values():
        for fld in block.get("fields", []):
            name = fld.get("typeName")
            val = fld.get("value")
            if name in ("title", "dsDescription", "notesText", "timePeriodCovered", "keyword", "author"):
                s = json.dumps(val)
                print(name + ":", s[:1500])
    for fi in v.get("files", []):
        df = fi.get("dataFile", {})
        print("FILE", df.get("id"), df.get("filename"), df.get("filesize"), "restricted=%s" % fi.get("restricted"),
              (df.get("description") or "")[:200])
