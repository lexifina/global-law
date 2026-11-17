"""Run the per-issue searches over every extracted corpus and record which documents hit.
Usage: python3 -I harness/auth_issue_search.py data/authority   -> data/authority/hits/<issue>.tsv and a summary on stdout.
A document hits an issue when it matches ALL regexes of one of the issue's patterns (case-insensitive)."""
import os, re, sys
root = sys.argv[1]
CORPORA = {"bofip": "text/bofip", "courts": "text/courts", "an": "text/an", "senat": "text/senat"}
ISSUES = {
 "F1_union_dues_overtime": [[r"199\s*quater\s*C|cotisations?\s+syndicales?", r"heures\s+suppl|81\s*quater"]],
 "F1_union_dues_base": [[r"199\s*quater\s*C", r"revenu\s+brut"]],
 "F2_cehr_flat_levy": [[r"223\s*sexies|hauts\s+revenus", r"151-0|versements?\s+libératoires?|micro"],
                       [r"223\s*sexies|hauts\s+revenus", r"taux\s+effectif|197\s*C\b"]],
 "F5_rounding": [[r"article\s+193\b|1657", r"euro\s+le\s+plus\s+proche|fraction\s+d.euro"]],
 "W1_61_in_rate": [[r"204\s*H|taux\s+d[eu]\s+prélèvement|taux\s+individualis", r"\b61\s*(€|euros)|1\s+bis\s+de\s+l.article\s+1657|seuils?\s+de\s+mise\s+en\s+recouvrement"]],
 "W2_rate_rounding": [[r"204\s*H|taux\s+d[eu]\s+prélèvement", r"décimale|arrondi"]],
 "W3_zero_rate_threshold": [[r"204\s*H|taux\s+nul", r"par\s+part\s+de\s+quotient\s+familial"]],
 "W4_W5_individual_rate": [[r"204\s*M|taux\s+individualis", r"décote|plafonnement|quotient\s+familial"]],
 "W6_default_grid": [[r"taux\s+par\s+défaut|III\s+de\s+l.article\s+204\s*H", r"8\s?7[38]9"]],
 "R_61_cehr_common": [[r"1\s+bis\s+de\s+l.article\s+1657", r"hauts\s+revenus"]],
 "R_credit_under_61": [[r"\b61\s*(€|euros)|1\s+bis\s+de\s+l.article\s+1657", r"restitu|rembours"]],
 "R_effective_rate_decote": [[r"taux\s+effectif", r"décote"]],
 "R_frais_reels_option": [[r"frais\s+réels", r"déduction\s+forfaitaire", r"renonc|option"]],
}
os.makedirs(os.path.join(root, "hits"), exist_ok=True)
texts = {}
for c, d in CORPORA.items():
    p = os.path.join(root, d)
    texts[c] = [(f, open(os.path.join(p, f), encoding="utf-8", errors="replace").read()) for f in sorted(os.listdir(p)) if f.endswith(".txt")]
print("corpus sizes:", {c: len(v) for c, v in texts.items()})
for issue, pats in ISSUES.items():
    rx = [[re.compile(r, re.I) for r in pat] for pat in pats]
    out = open(os.path.join(root, "hits", issue + ".tsv"), "w", encoding="utf-8")
    counts = {}
    for c, docs in texts.items():
        n = 0
        for f, t in docs:
            if any(all(r.search(t) for r in pat) for pat in rx):
                n += 1; out.write(f"{c}\t{f}\n")
        counts[c] = n
    print(issue, counts)
