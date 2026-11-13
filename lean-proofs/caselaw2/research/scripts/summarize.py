"""Tables from recs.jsonl. python summarize.py <recs.jsonl>"""
import json, sys, collections
POP = {"fed_app": 895162, "fed_trial_special": 697214, "scotus": 384140, "state_app": 2238282, "state_last": 2196591,
       "state_trial_special": 479780, "unmapped": 1285}
R = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
ST = ["scotus", "fed_app", "fed_trial_special", "state_last", "state_app", "state_trial_special"]
by = collections.defaultdict(list)
for r in R:
    by[r["s"]].append(r)


def row(name, f):
    vals = []
    est = 0.0
    for s in ST:
        L = by[s]
        k = sum(1 for r in L if f(r))
        vals.append("%.1f%%" % (100 * k / len(L)))
        est += POP[s] * k / len(L)
    print("| %s | %s | %.1f%% (~%s) |" % (name, " | ".join(vals), 100 * est / sum(POP[s] for s in ST), "{:,}".format(int(round(est, -3)))))


def hdr(t):
    print("\n### " + t + "\n")
    print("| measure | " + " | ".join(ST) + " | corpus (weighted) |")
    print("|---|" + "---|" * (len(ST) + 1))


hdr("Source and text")
row("CourtListener source", lambda r: r["src"] == "CL")
row("opinion text >= 1,000 chars", lambda r: r["oplen"] >= 1000)
row("opinion text < 300 chars (order/stub)", lambda r: r["oplen"] < 300)
row("has Head matter section", lambda r: "head matter" in r["kinds"])
row("head matter >= 300 chars", lambda r: r["head_len"] >= 300)
row("has Majority section", lambda r: "majority" in r["kinds"])
row("has Concurrence section", lambda r: "concurrence" in r["kinds"])
row("has Dissent section", lambda r: "dissent" in r["kinds"])
row("only Combined section(s)", lambda r: "combined" in r["kinds"] and "majority" not in r["kinds"])
row("any other section type", lambda r: any(k.startswith("other") or k in ("plurality", "rehearing", "lead", "addendum", "remittitur", "concurring in part") for k in r["kinds"]))
row("'dissent' word but no Dissent section", lambda r: r["p_dissent_word"] > 0 and "dissent" not in r["kinds"]) if "p_dissent_word" in R[0] else None
row("front matter judges", lambda r: r["judges"])
row("front matter docket", lambda r: r["docket"])
row("precedential_status present", lambda r: r["pstat"] is not None)
row("precedential_status != published", lambda r: r["pstat"] not in (None, "published"))
row("decision_type present", lambda r: r["dtype"] is not None)

hdr("Status markers: header zone (fm + head matter + first 1,500 chars) / body only / either")
for k in ("en_banc", "per_curiam", "plurality", "unpublished", "vacated", "vacated_opinion", "withdrawn", "rehearing",
          "rehearing_granted_or_on", "rehearing_denied"):
    row(k + " in header", lambda r, k=k: r["p_" + k] & 1)
    row(k + " body only", lambda r, k=k: r["p_" + k] == 2)
row("per curiam in section title", lambda r: r["sec_percuriam"])
row("judges field says en banc", lambda r: r["judges_enbanc"])

hdr("Head matter content")
row("syllabus word in head matter", lambda r: r["syll_head"])
row("'Held:' in head matter", lambda r: r["held_head"])
row(">=1 numbered headnote line in head matter", lambda r: r["hn_head"] >= 1)
row(">=3 numbered headnote lines", lambda r: r["hn_head"] >= 3)
row("attorney line in head matter", lambda r: r["att_head"])
row("'Syllabus' in first 4k chars of opinion text", lambda r: r["syll_body"])
row("'Held,'/'Held:' in first 6k chars of opinion text", lambda r: r["held_body"])
row("head matter prose (non-attorney lines >150 chars) >= 500 chars", lambda r: r["head_prose"] >= 500)
row("usable summary: head prose>=500 or Held or Syllabus", lambda r: r["head_prose"] >= 500 or r["held_head"] or r["syll_head"] or r["syll_body"])
print("\nSCOTUS full opinions only (opinion text >= 1,000 chars):")
L = [r for r in by["scotus"] if r["oplen"] >= 1000]
print("n=%d; head prose>=500: %.1f%%; Held in head: %.1f%%; Syllabus in text: %.1f%%; CL: %.1f%%" % (len(L),
      100 * sum(r["head_prose"] >= 500 for r in L) / len(L), 100 * sum(r["held_head"] for r in L) / len(L),
      100 * sum(r["syll_body"] for r in L) / len(L), 100 * sum(r["src"] == "CL" for r in L) / len(L)))
dd = collections.Counter((int(r["year"]) // 20 * 20, r["head_prose"] >= 500) for r in L if r["year"].isdigit())
print("by 20-yr period (head prose>=500 / n):", ", ".join("%d: %d/%d" % (d, dd[(d, True)], dd[(d, True)] + dd[(d, False)]) for d in sorted({k[0] for k in dd})))

hdr("Treatment phrases: share of decisions with >=1 hit")
TK = list(R[0]["t"].keys())
for k in TK:
    row(k, lambda r, k=k: r["t"][k] > 0)
print("\n### Treatment phrases: occurrences per 1,000 decisions and estimated corpus total\n")
print("| phrase | " + " | ".join(ST) + " | est. total occurrences |")
print("|---|" + "---|" * (len(ST) + 1))
for k in TK:
    vals = []
    est = 0
    for s in ST:
        n = sum(r["t"][k] for r in by[s])
        vals.append("%.1f" % (1000 * n / len(by[s])))
        est += POP[s] * n / len(by[s])
    print("| %s | %s | %s |" % (k, " | ".join(vals), "{:,}".format(int(round(est, -2)))))

print("\n### Decade breakdown (all strata pooled, unweighted)\n")
dec = collections.defaultdict(list)
for r in R:
    try:
        d = int(r["year"]) // 10 * 10
    except Exception:
        d = 0
    dec[min(max(d, 1780), 2020)].append(r)
print("| decade | n | head matter>=300 | Dissent section | Combined only | en banc header | unpublished any | CL |")
print("|---|---|---|---|---|---|---|---|")
for d in sorted(dec):
    L = dec[d]
    f = lambda c: "%.1f%%" % (100 * sum(1 for r in L if c(r)) / len(L))
    print("| %d | %d | %s | %s | %s | %s | %s | %s |" % (d, len(L), f(lambda r: r["head_len"] >= 300), f(lambda r: "dissent" in r["kinds"]),
          f(lambda r: "combined" in r["kinds"] and "majority" not in r["kinds"]), f(lambda r: r["p_en_banc"] & 1),
          f(lambda r: r["p_unpublished"] > 0), f(lambda r: r["src"] == "CL")))

print("\n### Other section titles (top)\n")
c = collections.Counter(k for r in R for k in r["kinds"])
print(", ".join("%s %d" % kv for kv in c.most_common(30)))

print("\n### State intermediate districts recovered (sample, all strata)\n")
g = collections.defaultdict(collections.Counter)
for r in R:
    if "dist" in r:
        g[r["dist"][0]][(r["dist"][1] or "NONE").split(":")[0]] += 1
print("| group | n | recovered | by route |")
print("|---|---|---|---|")
for k in sorted(g):
    n = sum(g[k].values())
    print("| %s | %d | %.1f%% | %s |" % (k, n, 100 * (n - g[k]["NONE"]) / n, ", ".join("%s %d" % kv for kv in g[k].most_common())))
print("\n### dtype/pstat\n")
print(collections.Counter((r["s"], r["dtype"]) for r in R if r["dtype"]).most_common(12))
print(collections.Counter((r["s"], r["pstat"]) for r in R).most_common(20))
