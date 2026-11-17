"""Courts as test cases, stage B. From the stage-A decisions (data/court/features.jsonl + text/), keep those that
(1) are an income-tax assessment dispute decided on the merits (not a désistement / non-lieu / irrecevabilité order,
    not a different tax that merely cites income tax), and
(2) state at least one computation figure of a kind the programs produce: number of parts, a tax amount, net taxable
    income / RFR, an allowance, a deductible amount, a reduction or credit, a CEHR amount.
Writes data/court/candidates.jsonl (one line per decision: topics, figure kinds, income years, score) and
data/court/snippets/<id>.txt (the paragraphs that carry the figures + the operative part), for reading.

usage: python3 -I harness/court_candidates.py
"""
import json, os, re, collections

D = os.path.expanduser("~/fr/data/court")
E = r"(\d{1,3}(?:[  .]\d{3})+|\d+)(?:,(\d{1,2}))?\s*(?:euros?|€|EUR)"
FIG = {
    "parts": re.compile(r"(?:quotient\s+familial|nombre\s+de\s+parts?|parts?\s+de\s+quotient)[^.;]{0,100}?(?<![\w,])(\d(?:,\d{1,2})?)\s+parts?\b|(?<![\w,])(\d(?:,\d{1,2})?)\s+parts?\b[^.;]{0,60}(?:quotient|familial)|(?<![dl]['’])\b(?:une|deux|trois|quatre|cinq)\s+parts?(?:\s+et\s+(?:demie|un\s+quart|trois\s+quarts))?\s+(?:de\s+quotient|fiscales?)", re.I),
    "half": re.compile(r"demi[- ]parts?\s+(?:suppl[ée]mentaire|de\s+quotient|au\s+titre)|majoration\s+d.une\s+demi[- ]part|quart\s+de\s+part", re.I),
    "tax": re.compile(r"(?:imp[ôo]t\s+(?:sur\s+le\s+revenu\s+)?(?:brut|net|d[ûu]|dont)|droits\s+(?:simples|rappel[ée]s|en\s+principal)|cotisations?\s+(?:primitive|suppl[ée]mentaires?)\s+d.imp[ôo]t\s+sur\s+le\s+revenu|montant\s+de\s+l.imp[ôo]t)[^.;]{0,120}?" + E, re.I),
    "income": re.compile(r"(?:revenu\s+(?:net\s+)?(?:global\s+)?imposable|revenu\s+fiscal\s+de\s+r[ée]f[ée]rence|revenu\s+brut\s+global|revenu\s+net\s+global)[^.;]{0,100}?" + E, re.I),
    "allow10": re.compile(r"(?:d[ée]duction|abattement)\s+forfaitaire\s+de\s+10[^.;]{0,150}?" + E + r"|frais\s+r[ée]els[^.;]{0,120}?" + E, re.I),
    "pension": re.compile(r"pensions?\s+alimentaires?[^.;]{0,150}?" + E, re.I),
    "a157bis": re.compile(r"(?:157\s*bis|abattement[^.;]{0,40}(?:personnes?\s+[âa]g[ée]es|invalides))[^.;]{0,150}?" + E, re.I),
    "decote": re.compile(r"d[ée]cote[^.;]{0,120}?" + E + r"|(?:61|seuil)[^.;]{0,30}recouvrement", re.I),
    "cehr": re.compile(r"contribution\s+exceptionnelle\s+sur\s+les\s+hauts\s+revenus[^.;]{0,150}?" + E, re.I),
    "pfu": re.compile(r"(?:pr[ée]l[èe]vement\s+forfaitaire\s+unique|taux\s+(?:forfaitaire\s+)?de\s+12[,.]8|option\s+(?:globale\s+)?pour\s+(?:l.imposition\s+(?:selon|au)\s+)?(?:le\s+)?bar[èe]me)", re.I),
    "micro": re.compile(r"(?:micro[- ](?:BIC|BNC|entreprise|foncier)|r[ée]gime\s+d[ée]claratif\s+sp[ée]cial|abattement\s+(?:forfaitaire\s+)?de\s+(?:34|50|71|30)\s*%)[^.;]{0,150}?" + E, re.I),
    "pv": re.compile(r"(?:plus-value|abattement\s+pour\s+dur[ée]e\s+de\s+d[ée]tention)[^.;]{0,150}?" + E, re.I),
    "redcred": re.compile(r"(?:r[ée]duction|cr[ée]dit)\s+d.imp[ôo]t[^.;]{0,150}?" + E, re.I),
    "plafond": re.compile(r"(?:200-0\s*A|plafonnement\s+(?:global\s+)?des\s+(?:avantages|niches))", re.I),
    "quotient": re.compile(r"(?:163-0\s*A|syst[èe]me\s+du\s+quotient|selon\s+le\s+quotient)", re.I),
}
NOMERIT = re.compile(r"donn[ée]\s+acte\s+du\s+d[ée]sistement|il\s+n.y\s+a\s+(?:plus\s+)?lieu\s+(?:de\s+)?statuer\s+sur\s+(?:les\s+conclusions\s+de\s+)?la\s+requ[êe]te|\bO\s*R\s*D\s*O\s*N\s*N\s*E\b", re.I)
OTHER_TAX = re.compile(r"taxe\s+d.habitation|taxe\s+fonci[èe]re|taxe\s+sur\s+la\s+valeur\s+ajout[ée]e|imp[ôo]t\s+sur\s+les\s+soci[ée]t[ée]s|droits\s+de\s+mutation|aide\s+personnalis[ée]e\s+au\s+logement|revenu\s+de\s+solidarit[ée]\s+active|allocation", re.I)
IRDISP = re.compile(r"(?:cotisations?|imposition|suppl[ée]ment|r[ée]duction|d[ée]charge|d[ée]gr[èe]vement|restitution)[^.]{0,120}imp[ôo]t\s+sur\s+le\s+revenu|imp[ôo]t\s+sur\s+le\s+revenu[^.]{0,80}(?:assujetti|mis\s+[àa]\s+(?:sa|leur)\s+charge|au\s+titre\s+de)", re.I)
YEARS = re.compile(r"(?:au\s+titre\s+de[s]?\s+(?:l.ann[ée]e\s+|ann[ée]es\s+|revenus\s+(?:de\s+l.ann[ée]e\s+)?)?|revenus\s+(?:de\s+l.ann[ée]e\s+|perçus\s+en\s+)?|imposition\s+(?:des\s+revenus\s+)?(?:de\s+l.ann[ée]e\s+)?)((?:19|20)\d\d)(?:\s*(?:,|et|à)\s*((?:19|20)\d\d))*", re.I)
PARA = re.compile(r"\n\s*(\d{1,2})\.\s")


def years(t):
    ys = set()
    for m in YEARS.finditer(t):
        for y in re.findall(r"(?:19|20)\d\d", m.group(0)):
            ys.add(int(y))
    return sorted(y for y in ys if 2005 <= y <= 2025)


def snippets(t, kinds):
    paras = re.split(r"\n", t)
    keep = []
    rx = [FIG[k] for k in kinds]
    for i, p in enumerate(paras):
        if any(r.search(p) for r in rx) or re.match(r"\s*Article\s+(1er|2|3)\s*:", p):
            keep.append(p.strip())
    s = "\n".join(keep)
    return s[:6000]


def main():
    os.makedirs(D + "/snippets", exist_ok=True)
    feats = [json.loads(l) for l in open(D + "/features.jsonl")]
    out = []
    funnel = collections.Counter()
    seen = {}
    for f in feats:
        funnel["stage_a"] += 1
        t = open(f"{D}/text/{f['id']}.txt", encoding="utf-8").read()
        body = t.split("\n\n", 1)[-1]
        if len(body) < 2500 and NOMERIT.search(body):
            funnel["drop_order_no_merits"] += 1
            continue
        if not IRDISP.search(body):
            funnel["drop_not_ir_dispute"] += 1
            continue
        kinds = {k: len(r.findall(body)) for k, r in FIG.items()}
        kinds = {k: v for k, v in kinds.items() if v}
        if not kinds:
            funnel["drop_no_figure"] += 1
            continue
        ys = years(body)
        # duplicate: same court number + date (JADE and JA open data overlap)
        key = (re.sub(r"\W", "", (f.get("number") or "")).upper(), (f.get("date") or "")[:10])
        if key[0] and key in seen:
            funnel["drop_duplicate"] += 1
            continue
        seen[key] = f["id"]
        funnel["ir_computation"] += 1
        score = (3 * ("parts" in kinds or "half" in kinds) + 3 * ("tax" in kinds) + 2 * ("income" in kinds)
                 + sum(1 for k in kinds if k not in ("parts", "half", "tax", "income"))
                 + 3 * any(2020 <= y <= 2025 for y in ys) + 1 * any(2015 <= y <= 2019 for y in ys))
        c = {"id": f["id"], "court": f["court"], "date": f["date"], "number": f["number"], "ecli": f.get("ecli"),
             "years": ys, "kinds": kinds, "topics": f["topics"], "score": score, "len": len(body)}
        out.append(c)
        open(f"{D}/snippets/{f['id']}.txt", "w", encoding="utf-8").write(
            f"{f['court']} | {f['date']} | {f['number']} | years {ys} | {kinds}\n\n" + snippets(body, list(kinds)))
    out.sort(key=lambda c: -c["score"])
    with open(D + "/candidates.jsonl", "w") as fo:
        for c in out:
            fo.write(json.dumps(c, ensure_ascii=False) + "\n")
    json.dump(funnel, open(D + "/funnel_stage_b.json", "w"), indent=1)
    print(dict(funnel))
    kc = collections.Counter(k for c in out for k in c["kinds"])
    print(kc.most_common())
    yc = collections.Counter(max(c["years"]) if c["years"] else 0 for c in out)
    print(sorted(yc.items()))


if __name__ == "__main__":
    main()
