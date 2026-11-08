"""analysis11.json -> legal-year-data.json: each jurisdiction with 30+ dated acts, its acts by month and by day of the year.

Usage: python -I ly_prep.py ../analysis11.json legal-year-data.json
"""
import json, sys

a = json.load(open(sys.argv[1], encoding="utf-8"))
a = a.get("a11", a)
SUB = {"australia-western-australia": "Western Australia", "canada-northwest-territories": "Northwest Territories",
       "australia-northern-territory": "Northern Territory"}


def tw(s):
    return " ".join(w if w in ("and", "of", "the") else w[0].upper() + w[1:] for w in s.split("-"))


def title(s):
    if s in SUB:
        return SUB[s]
    for p in ("australia-", "canada-", "united-states-"):
        if s.startswith(p) and len(s) > len(p):
            return tw(s[len(p):])
    return tw(s)


rows = [{"name": title(k), "acts": v["acts"], "month": v["month"], "doy": v.get("doy", {})}
        for k, v in a.items()
        if isinstance(v, dict) and v.get("month") and sum(v["month"]) >= 30 and v.get("acts", 0) >= 3]
rows.sort(key=lambda r: -r["acts"])
json.dump(rows, open(sys.argv[2], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, separators=(",", ":"))
print(len(rows), "jurisdictions")
